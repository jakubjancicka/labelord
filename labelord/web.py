"""
This module contains classes and functions for Web application.
"""
import click
import configparser
import flask
import hashlib
import hmac
import os
import sys
import time

from .helpers import create_config, extract_labels, extract_repos
from .github import GitHub, GitHubError

NO_WEBHOOK_SECRET_RETURN = 8
NO_GH_TOKEN_RETURN = 3
NO_REPOS_SPEC_RETURN = 7

###############################################################################
# Flask task
###############################################################################


class LabelordChange:
    CHANGE_TIMEOUT = 10

    def __init__(self, action, name, color, new_name=None):
        self.action = action
        self.name = name
        self.color = None if action == 'deleted' else color
        self.old_name = new_name
        self.timestamp = int(time.time())

    @property
    def tuple(self):
        return self.action, self.name, self.color, self.old_name

    def __eq__(self, other):
        return self.tuple == other.tuple

    def is_valid(self):
        return self.timestamp > (int(time.time()) - self.CHANGE_TIMEOUT)


class LabelordWeb(flask.Flask):
    """
    Class **LabelordWeb** represents Flask web application
    """
    def __init__(self, labelord_config, github, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labelord_config = labelord_config
        self.github = github
        self.ignores = {}

    def inject_session(self, session):
        """
        Inject session.
        
        :param: ``session``: session
        """
        self.github.set_session(session)

    def reload_config(self):
        """
        Reload config file.
        """
        config_filename = os.environ.get('LABELORD_CONFIG', None)
        self.labelord_config = create_config(
            token=os.getenv('GITHUB_TOKEN', None),
            config_filename=config_filename
        )
        self._check_config()
        self.github.token = self.labelord_config.get('github', 'token')

    @property
    def repos(self):
        """
        Extract repositories.
        
        :return: List of repositories.
        """
        return extract_repos(flask.current_app.labelord_config)

    def _check_config(self):
        if not self.labelord_config.has_option('github', 'token'):
            click.echo('No GitHub token has been provided', err=True)
            sys.exit(NO_GH_TOKEN_RETURN)
        if not self.labelord_config.has_section('repos'):
            click.echo('No repositories specification has been found',
                       err=True)
            sys.exit(NO_REPOS_SPEC_RETURN)
        if not self.labelord_config.has_option('github', 'webhook_secret'):
            click.echo('No webhook secret has been provided', err=True)
            sys.exit(NO_WEBHOOK_SECRET_RETURN)

    def _init_error_handlers(self):
        from werkzeug.exceptions import default_exceptions
        for code in default_exceptions:
            self.errorhandler(code)(LabelordWeb._error_page)

    def finish_setup(self):
        """
        Check config and init error handlers.
        """
        self._check_config()
        self._init_error_handlers()

    @staticmethod
    def create_app(config=None, github=None):
        """
        Create application.

        :param: ``config``: congiuration file
        :param: ``github``: GitHub object
        """
        cfg = config or create_config(
            token=os.getenv('GITHUB_TOKEN', None),
            config_filename=os.getenv('LABELORD_CONFIG', None)
        )
        gh = github or GitHub('')  # dummy, but will be checked later
        gh.token = cfg.get('github', 'token', fallback='')
        return LabelordWeb(cfg, gh, import_name=__name__)

    @staticmethod
    def _error_page(error):
        return flask.render_template('error.html', error=error), error.code

    def cleanup_ignores(self):
        """
        Clenaup ingore repositories.
        """
        for repo in self.ignores:
            self.ignores[repo] = [c for c in self.ignores[repo]
                                  if c.is_valid()]

    def process_label_webhook_create(self, label, repo):
        """
        Create label on Github.

        :param: ``label``: Created label.
        :param: ``repo``: Given repository.
        """
        self.github.create_label(repo, label['name'], label['color'])

    def process_label_webhook_delete(self, label, repo):
        """
        Delete label on Github.

        :param: ``label``: Created label.
        :param: ``repo``: Given repository.
        """
        self.github.delete_label(repo, label['name'])

    def process_label_webhook_edit(self, label, repo, changes):
        """
        Update label on Github.

        :param: ``label``: Created label.
        :param: ``repo``: Given repository.
        :param: ``changes``: Desired changes.
        """
        name = old_name = label['name']
        color = label['color']
        if 'name' in changes:
            old_name = changes['name']['from']
        self.github.update_label(repo, name, color, old_name)

    def process_label_webhook(self, data):
        """
        Process response from Github.

        :param: ``data``: Response from GitHub.
        """
        self.cleanup_ignores()
        action = data['action']
        label = data['label']
        repo = data['repository']['full_name']
        flask.current_app.logger.info(
            'Processing LABEL webhook event with action {} from {} '
            'with label {}'.format(action, repo, label)
        )
        if repo not in self.repos:
            return  # This repo is not being allowed in this app

        change = LabelordChange(action, label['name'], label['color'])
        if action == 'edited' and 'name' in data['changes']:
            change.new_name = label['name']
            change.name = data['changes']['name']['from']

        if repo in self.ignores and change in self.ignores[repo]:
            self.ignores[repo].remove(change)
            return  # This change was initiated by this service
        for r in self.repos:
            if r == repo:
                continue
            if r not in self.ignores:
                self.ignores[r] = []
            self.ignores[r].append(change)
            try:
                if action == 'created':
                    self.process_label_webhook_create(label, r)
                elif action == 'deleted':
                    self.process_label_webhook_delete(label, r)
                elif action == 'edited':
                    self.process_label_webhook_edit(label, r, data['changes'])
            except GitHubError:
                pass  # Ignore GitHub errors

app = LabelordWeb.create_app()


@app.before_first_request
def finalize_setup():
    """
    Setup finalization.
    """
    flask.current_app.finish_setup()


@app.route('/', methods=['GET'])
def index():
    """
    Index action.
    """
    repos = flask.current_app.repos
    return flask.render_template('index.html', repos=repos)


@app.route('/', methods=['POST'])
def hook_accept():
    """
    Accept hook.
    """
    headers = flask.request.headers
    signature = headers.get('X-Hub-Signature', '')
    event = headers.get('X-GitHub-Event', '')
    data = flask.request.get_json()

    if not flask.current_app.github.webhook_verify_signature(
            flask.request.data, signature,
            flask.current_app.labelord_config.get('github', 'webhook_secret')
    ):
        flask.abort(401)

    if event == 'label':
        if data['repository']['full_name'] not in flask.current_app.repos:
            flask.abort(400, 'Repository is not allowed in application')
        flask.current_app.process_label_webhook(data)
        return ''
    if event == 'ping':
        flask.current_app.logger.info('Accepting PING webhook event')
        return ''
    flask.abort(400, 'Event not supported')

"""
This module contains classes and functions for command-line application.
"""

import click
import configparser
import hashlib
import hmac
import requests
import os
import sys
import time

from .github import GitHub, GitHubError
from .web import app
from .helpers import create_config, extract_repos, extract_labels

DEFAULT_SUCCESS_RETURN = 0
DEFAULT_ERROR_RETURN = 10
NO_GH_TOKEN_RETURN = 3
GH_ERROR_RETURN = {
    401: 4,
    404: 5
}


###############################################################################
# Printing and logging
###############################################################################


class BasePrinter:
    """
    Class **BasePrinter** serves as general class for printing information about events to terminal.
    
    A few events may happen:

    **ADD** - Add new Github tag.

    **DEL** - Delete Github tag. 

    **UPD** - Update color or name of Github tag.

    **LBL** - Read Github tag.

    **SUC** - Operation has been successful.

    **ERR** - Operation has ended with error.

    **DRY** - Operation has run in dry mode. 
    """

    SUCCESS_SUMMARY = '{} repo(s) updated successfully'
    ERROR_SUMMARY = '{} error(s) in total, please check log above'

    EVENT_CREATE = 'ADD'
    EVENT_DELETE = 'DEL'
    EVENT_UPDATE = 'UPD'
    EVENT_LABELS = 'LBL'

    RESULT_SUCCESS = 'SUC'
    RESULT_ERROR = 'ERR'
    RESULT_DRY = 'DRY'

    def __init__(self):
        self.repos = set()
        self.errors = 0

    def add_repo(self, slug):
        """
        Add Github repository with which has been manipulated.
        """
        self.repos.add(slug)

    def event(self, event, result, repo, *args):
        """
        Log event.
        
        :param: ``event``: Operation
        :param: ``result``: Result of operation
        :param: ``repo``: Repository
        :param: ``*args``: Additional arguments 
        """
        if result == self.RESULT_ERROR:
            self.errors += 1

    def summary(self):
        """
        Print logs about events to terminal window.
        """
        pass

    def _create_summary(self):
        if self.errors > 0:
            return self.ERROR_SUMMARY.format(self.errors)
        return self.SUCCESS_SUMMARY.format(len(self.repos))


class Printer(BasePrinter):
    """
    Class **Printer** prints only events which end with error. At the end summary is printed.
    """
    def event(self, event, result, repo, *args):
        """Refer to :func:`~labelord.cli.BasePrinter.event`"""
        super().event(event, result, repo, *args)
        if result == self.RESULT_ERROR:
            line_parts = ['ERROR: ' + event, repo, *args]
            click.echo('; '.join(line_parts))

    def summary(self):
        """Refer to :func:`~labelord.cli.BasePrinter.summary`"""
        click.echo('SUMMARY: ' + self._create_summary())


class QuietPrinter(BasePrinter):
    """
    Class **QuietPrinter** does not produce any output.
    """
    pass


class VerbosePrinter(BasePrinter):
    """
    Class **VerbosePrinter** prints all events which happened.
    """
    LINE_START = '[{}][{}] {}'

    def event(self, event, result, repo, *args):
        """Refer to :func:`~labelord.cli.BasePrinter.event`"""
        super().event(event, result, repo, *args)
        line_parts = [self.LINE_START.format(event, result, repo), *args]
        click.echo('; '.join(line_parts))

    def summary(self):
        """Refer to :func:`~labelord.cli.BasePrinter.summary`"""
        click.echo('[SUMMARY] ' + self._create_summary())

###############################################################################
# Processing changes (RUN and MODES)
###############################################################################


class RunModes:
    """
    Class **RunModes** is general class which realizes operations over tags in Github repositories.
    """
    @staticmethod
    def _make_labels_dict(labels_spec):
        return {k.lower(): (k, v) for k, v in labels_spec.items()}

    @classmethod
    def update_mode(cls, labels, labels_specs):
        """
        This mode executes update mode - changes names and colors.

        :param: ``labels``: Dictionary of labels, which are in repository
        :param: ``labels_specs``: Dictionary of labels specifications
        
        :return: ``create``: dictionary of tags which should be created
        :return: ``update``: dictionary of tags which should be updated
        """    
        create = dict()
        update = dict()
        xlabels = cls._make_labels_dict(labels)
        for name, color in labels_specs.items():
            if name.lower() not in xlabels:
                create[name] = (name, color)
            elif name not in labels:  # changed case of name
                old_name = xlabels[name.lower()][0]
                update[old_name] = (name, color)
            elif labels[name] != color:
                update[name] = (name, color)
        return create, update, dict()

    @classmethod
    def replace_mode(cls, labels, labels_specs):
        """
        This mode executes replace mode - changes names and colors and if existing label does not in specification it will be deleted.

        :param: ``labels``: Dictionary of labels, which are in repository
        :param: ``labels_specs``: Dictionary of labels specifications
        :return: ``create``: dictionary of tags which should be created
        :return: ``update``: dictionary of tags which should be updated
        :return: ``delete``: dictionary of tags which should be deleted
        """    
        create, update, delete = cls.update_mode(labels, labels_specs)
        delete = {n: (n, c) for n, c in labels.items()
                  if n not in labels_specs}
        return create, update, delete


class RunProcessor:
    """
    Class **RunProcessor** realizes actual operations over Github.
    """

    MODES = {
        'update': RunModes.update_mode,
        'replace': RunModes.replace_mode
    }

    def __init__(self, github, printer=None):
        self.github = github
        self.printer = printer or QuietPrinter()

    def _process_generic(self, slug, key, data, event, method):
        old_name, name, color = key, data[0], data[1]
        try:
            method(slug, name=name, color=color, old_name=old_name)
        except GitHubError as error:
            self.printer.event(event, Printer.RESULT_ERROR,
                               slug, name, color, error.code_message)
        else:
            self.printer.event(event, Printer.RESULT_SUCCESS,
                               slug, name, color)

    def _process_create(self, slug, key, data):
        self._process_generic(slug, key, data, Printer.EVENT_CREATE,
                              self.github.create_label)

    def _process_update(self, slug, key, data):
        self._process_generic(slug, key, data, Printer.EVENT_UPDATE,
                              self.github.update_label)

    def _process_delete(self, slug, key, data):
        self._process_generic(slug, key, data, Printer.EVENT_DELETE,
                              self.github.delete_label)

    @staticmethod
    def _process(slug, changes, processor):
        for key, data in changes.items():
            processor(slug, key, data)

    def _run_one(self, slug, labels_specs, mode):
        self.printer.add_repo(slug)
        try:
            labels = self.github.list_labels(slug)
        except GitHubError as error:
            self.printer.event(Printer.EVENT_LABELS, Printer.RESULT_ERROR,
                               slug, error.code_message)
        else:
            create, update, delete = mode(labels, labels_specs)
            self._process(slug, create, self._process_create)
            self._process(slug, update, self._process_update)
            self._process(slug, delete, self._process_delete)

    def run(self, slugs, labels_specs, mode):
        """
        Run processor for each repository.
        
        :return: Return code
        """
        for slug in slugs:
            self._run_one(slug, labels_specs, mode)
        self.printer.summary()
        return (DEFAULT_ERROR_RETURN if self.printer.errors > 0
                else DEFAULT_SUCCESS_RETURN)


class DryRunProcessor(RunProcessor):
    """
    Class **DryRunProcessor** runs operations in dry mode.
    """

    def __init__(self, github, printer=None):
        super().__init__(github, printer)

    def _process_create(self, slug, key, data):
        self.printer.event(Printer.EVENT_CREATE, Printer.RESULT_DRY,
                           slug, data[0], data[1])

    def _process_update(self, slug, key, data):
        self.printer.event(Printer.EVENT_UPDATE, Printer.RESULT_DRY,
                           slug, data[0], data[1])

    def _process_delete(self, slug, key, data):
        self.printer.event(Printer.EVENT_DELETE, Printer.RESULT_DRY,
                           slug, data[0], data[1])

###############################################################################
# Simple helpers
###############################################################################


def pick_printer(verbose, quiet):
    """
    Pick right printer according to parameters.
    
    :param: ``verbose``: *True* if verbose mode is wanted
    :param: ``quiet``: *True* if quiet mode is wanted
    
    :return: Printer

    If both parameters is set to True :class:`~labelord.cli.Printer` is chosen.
    """
    if verbose and not quiet:
        return VerbosePrinter
    if quiet and not verbose:
        return QuietPrinter
    return Printer


def pick_runner(dry_run):
    """
    Pick right runner.

    :param: ``dry_run``: *True* if dry mode is wanted. Otherwise all commands are executed on Github.
    :return: Chosen processor
    """
    return DryRunProcessor if dry_run else RunProcessor


def gh_error_return(github_error):
    """
    Return right error code according to parameter ``github_error``.

    :param: ``github_error``: Error from Github response.
    """
    return GH_ERROR_RETURN.get(github_error.status_code, DEFAULT_ERROR_RETURN)


def retrieve_github_client(ctx):
    """
    Extract Github client object from context.

    :param: ``ctx``: Click context
    :return: GitHub object
    """
    if 'GitHub' not in ctx.obj:
        click.echo('No GitHub token has been provided', err=True)
        sys.exit(NO_GH_TOKEN_RETURN)
    return ctx.obj['GitHub']


###############################################################################
# Click commands
###############################################################################


@click.group(name='labelord')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path of the auth config file.')
@click.option('--token', '-t', envvar='GITHUB_TOKEN',
              help='GitHub API token.')
@click.version_option(version='0.2',
                      prog_name='labelord')
@click.pass_context
def cli(ctx, config, token):
    """
    Click group function.
    
    :param: ``ctx``: Click context.
    :param: ``config``: Path of the auth config file.
    :param: ``token``: Github API token.
    """
    ctx.obj['config'] = create_config(config, token)
    ctx.obj['config'].optionxform = str
    if token is not None:
        ctx.obj['config'].read_dict({'github': {'token': token}})
    if ctx.obj['config'].has_option('github', 'token'):
        session = ctx.obj.get('session', requests.Session())
        ctx.obj['GitHub'] = GitHub(
            ctx.obj['config'].get('github', 'token'),
            session
        )


@cli.command(help='Listing accessible repositories.')
@click.pass_context
def list_repos(ctx):
    """
    List all user repositories.

    :param: ``ctx``: Click context.
    """
    github = retrieve_github_client(ctx)
    try:
        repos = github.list_repositories()
        click.echo('\n'.join(repos))
    except GitHubError as error:
        click.echo(error, err=True)
        sys.exit(gh_error_return(error))


@cli.command(help='Listing labels of desired repository.')
@click.argument('repository')
@click.pass_context
def list_labels(ctx, repository):
    """
    List labels for specified repository.

    :param: ``ctx``: Click context.
    :param: ``repository``: Repository whose labels are printed.
    """
    github = retrieve_github_client(ctx)
    try:
        labels = github.list_labels(repository)
        for name, color in labels.items():
            click.echo('#{} {}'.format(color, name))
    except GitHubError as error:
        click.echo(error, err=True)
        sys.exit(gh_error_return(error))


@cli.command(help='Run labels processing.')
@click.argument('mode', default='update', metavar='<update|replace>',
                type=click.Choice(['update', 'replace']))
@click.option('--template-repo', '-r', type=click.STRING,
              help='Repository which serves as labels template.')
@click.option('--dry-run', '-d', is_flag=True,
              help='Proceed with just dry run.')
@click.option('--verbose', '-v', is_flag=True,
              help='Really exhaustive output.')
@click.option('--quiet', '-q', is_flag=True,
              help='No output at all.')
@click.option('--all-repos', '-a', is_flag=True,
              help='Run for all repositories available.')
@click.pass_context
def run(ctx, mode, template_repo, dry_run, verbose, quiet, all_repos):
    """
    Update or replace labels.

    :param: ``ctx``: Click context.
    :param: ``mode``: Update/Replace mode.
    :param: ``template_repo``: Repository which is used as specification.
    :param: ``dry_run``:  Turn on dry run mode.
    :param: ``verbose``: Turn on verbose mode.
    :param: ``quiet``: Turn on quiet mode.
    :param: `all_repos``:  If *True* update tags for all repositories.
    """
    github = retrieve_github_client(ctx)
    labels = extract_labels(
        github, template_repo,
        ctx.obj['config']
    )
    if all_repos:
        repos = github.list_repositories()
    else:
        repos = extract_repos(ctx.obj['config'])
    printer = pick_printer(verbose, quiet)()
    processor = pick_runner(dry_run)(github, printer)
    try:
        return_code = processor.run(repos, labels, processor.MODES[mode])
        sys.exit(return_code)
    except GitHubError as error:
        click.echo(error, err=True)
        sys.exit(gh_error_return(error))


@cli.command(help='Run master-to-master replication server.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--debug', '-d', is_flag=True,
              help='Turns on DEBUG mode.')
@click.pass_context
def run_server(ctx, host, port, debug):
    """
    Run Flask server.

    :param: ``host``: The interface to bind to.
    :param: ``port``: The port to bind to.
    :param: ``debug``: Turn on DEBUG mode.
    """
    app.labelord_config = ctx.obj['config']
    app.github = retrieve_github_client(ctx)
    app.run(host=host, port=port, debug=debug)


def main():
    """
    Main entry point for console application.
    """    
    cli(obj={})

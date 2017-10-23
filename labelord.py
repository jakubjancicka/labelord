# MI-PYT, task 1 (requests+click)
# File: labelord.py
import click
import requests
import configparser
import sys

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('labelord, version 0.1')
    ctx.exit()

class BadCredentialException(Exception):
    pass

class NotFoundException(Exception):
    pass

class GithubErrorException(Exception):
    pass

# Create proper header for Github
def github_session(session, token):
    session.headers = {'User-Agent': 'Python'}
    
    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth

# Check status code of https request
def check_status_code(r, data={}):
    if r.status_code == 401:
        raise BadCredentialException({'error': 'GitHub: ERROR 401 - Bad credentials', 'status': r.status_code, 'message': r.json()['message'], 'data': data, 'code': 4})
    
    if r.status_code == 404:
        raise NotFoundException({'error': 'GitHub: ERROR 404 - Not Found', 'status': r.status_code, 'message': r.json()['message'], 'data': data, 'code': 5})
    
    if r.status_code < 200 or r.status_code > 299:
        raise GithubErrorException({'error': 'GitHub: ERROR {} - {}'.format(r.status_code, r.json()['message']), 'status': r.status_code, 'data': data, 'message': r.json()['message'], 'code': 10})

# GET request
def get_request(session, url, data={}):
    content = []
    r = session.get(url)
    check_status_code(r, data) 
    content.extend(r.json())
    
    while 'next' in r.links:
        r = session.get(r.links['next']['url'])
        check_status_code(r, data) 
        content.extend(r.json())
    
    return content

# Get all repos accessible to the authenticated user
def get_repos(session):
    return get_request(session, 'https://api.github.com/user/repos?per_page=100&page=1')

# Get repo labels
def get_labels(session, repo):
    return get_request(session, 'https://api.github.com/repos/{}/labels?per_page=100&page=1'.format(repo), {'repo': repo})

def add_label(session, repo, label_name, label_color):
    r = session.post('https://api.github.com/repos/{}/labels'.format(repo), json = {'name': label_name, 'color': label_color})
    check_status_code(r, {'repo': repo, 'label_name': label_name, 'label_color': label_color})

def update_label(session, repo, old_label_name, new_label_name, label_color):
    r = session.patch('https://api.github.com/repos/{}/labels/{}'.format(repo, old_label_name), json = {'name': new_label_name, 'color': label_color})
    check_status_code(r, {'repo': repo, 'label_name': new_label_name, 'label_color': label_color})

def delete_label(session, repo, label_name):
    r = session.delete('https://api.github.com/repos/{}/labels/{}'.format(repo, label_name))
    check_status_code(r, {'repo': repo, 'label_name': label_name})

def output(msg, mode, verbose, quiet, dry, error):
    second_tag = 'DRY' if dry else 'ERR' if error else 'SUC'
    if verbose and not quiet:
        print("[{}][{}] {}".format(mode, second_tag, msg))
    elif error and ((verbose and quiet) or (not verbose and not quiet)):
        print("ERROR: {}; {}".format(mode, msg), file=sys.stderr)

def summary(repo_count, error_count, verbose, quiet):
    sum_string = '[SUMMARY]' if verbose and not quiet else 'SUMMARY:'
    if error_count == 0:
        if not quiet or (quiet and verbose):
            print("{} {} repo(s) updated successfully".format(sum_string, repo_count))
        return 0
    else:
        if not quiet or (quiet and verbose):
            print("{} {} error(s) in total, please check log above".format(sum_string, error_count))
        return 10

@click.group('labelord')
@click.option('-c', '--config', default='config.cfg', help='Path to config file')
@click.option('-t', '--token', envvar='GITHUB_TOKEN', help='Secret token for Github account')
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.pass_context
def cli(ctx, config, token):
    # Read config from config file
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(config)
    ctx.obj['config'] = cfg
    
    # Read token if option or argument are not used
    if token is None and 'github' in ctx.obj['config'] and 'token' in ctx.obj['config']['github']:        
        token = ctx.obj['config']['github']['token']
    
    # Exit if token has not been provided    
    if not token:    
        print("No GitHub token has been provided", file=sys.stderr)
        sys.exit(3)               

    # Use session for communication with GitHub
    session = ctx.obj.get('session', requests.Session())
    github_session(session, token)
    if 'session' not in ctx.obj:
        ctx.obj['session'] = session

@cli.command(help='Show available repositories.')
@click.pass_context
def list_repos(ctx):
    try:
        repos = get_repos(ctx.obj['session'])
    except (BadCredentialException, GithubErrorException) as e:
        print(e.args[0]['error'], file=sys.stderr)
        sys.exit(e.args[0]['code'])               
    
    for repo in repos:
        print(repo['full_name'])
    
@cli.command(help='Listing labels of desired repository.')
@click.argument('repo')
@click.pass_context
def list_labels(ctx, repo):
    try:
        labels = get_labels(ctx.obj['session'], repo)
    except (BadCredentialException, NotFoundException, GithubErrorException) as e:
        print(e.args[0]['error'], file=sys.stderr)
        sys.exit(e.args[0]['code'])               
    
    for label in labels:
        print("#{} {}".format(label['color'], label['name']))

@cli.command(help='Update or replace labels according to template.')
@click.option('-r', '--template-repo', help='Name of the repo which serves as template')
@click.option('-a', '--all-repos', is_flag=True, default=False, help='Use all available repositories')
@click.option('-d', '--dry-run', is_flag=True, default=False, help='Run program without actual changes')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Print all messages')
@click.option('-q', '--quiet', is_flag=True, default=False, help='No output')
@click.argument('mode', type=click.Choice(['update', 'replace']))
@click.pass_context
def run(ctx, template_repo, all_repos, dry_run, verbose, quiet, mode):
    # Get labels according to user settings
    labels = {}
    if template_repo is not None:
        try:
            for label in get_labels(ctx.obj['session'], template_repo):
                labels[label['name'].lower()] = (label['name'], label['color'])
        except (BadCredentialException, NotFoundException, GithubErrorException) as e:
            print(e.args[0]['error'], file=sys.stderr)
            sys.exit(e.args[0]['code'])               
    elif 'others' in ctx.obj['config'] and 'template-repo' in ctx.obj['config']['others']:
        try:
            for label in get_labels(ctx.obj['session'], ctx.obj['config']['others']['template-repo']):
                labels[label['name'].lower()] = (label['name'], label['color'])
        except (BadCredentialException, NotFoundException, GithubErrorException) as e:
            print(e.args[0]['error'], file=sys.stderr)
            sys.exit(e.args[0]['code'])               
    elif 'labels' in ctx.obj['config']:
        for label_name in ctx.obj['config']['labels']:
            labels[label_name.lower()] = (label_name, ctx.obj['config']['labels'][label_name])
    else:
        print("No labels specification has been found", file=sys.stderr)
        sys.exit(6)
    
    # Get repositories according to user settings
    repositories = []
    if all_repos:
        try:        
            for repo in get_repos(ctx.obj['session']):
                repositories.append(repo['full_name'])
        except (BadCredentialException, NotFoundException, GithubErrorException) as e:
            print(e.args[0]['error'], file=sys.stderr)
            sys.exit(e.args[0]['code'])               
    elif 'repos' in ctx.obj['config']:
        for repo_name in ctx.obj['config']['repos']:
            if ctx.obj['config'].getboolean('repos', repo_name):
                repositories.append(repo_name) 
    else:
        print("No repositories specification has been found", file=sys.stderr)
        sys.exit(7)
    
    error_count = 0;
    
    for repository in repositories:
        # Load actual repo labels
        repo_labels = {}
        try:
            for repo_label in get_labels(ctx.obj['session'], repository):
                repo_labels[repo_label['name'].lower()] = (repo_label['name'], repo_label['color'])  
        except (BadCredentialException, NotFoundException, GithubErrorException) as e:
            details = e.args[0]
            output('{}; {} - {}'.format(details['data']['repo'], details['status'], details['message']), 'LBL', verbose, quiet, False, True)
            error_count += 1
            continue

        # if replace mode -> delete unwanted labels
        if mode == 'replace':
            for repo_label_key, repo_label in repo_labels.items():
                repo_label_name, repo_label_color = repo_label
                if repo_label_key not in labels:
                    try:
                        if not dry_run:
                            delete_label(ctx.obj['session'], repository, repo_label[0])
                        output('{}; {}; {}'.format(repository, repo_label_name, repo_label_color), 'DEL', verbose, quiet, True if dry_run else False, False)
                    except (BadCredentialException, NotFoundException, GithubErrorException) as e:
                        details = e.args[0]
                        output('{}; {}; {}; {} - {}'.format(details['data']['repo'], details['data']['label_name'], details['data']['label_color'],
                                details['status'], details['message']), 'DEL', verbose, quiet, False, True)
                        error_count += 1
        
        # update labels
        for label_key, label in labels.items():
            label_name, label_color = label
            if label_key not in repo_labels:
                try:                
                    if not dry_run:
                        add_label(ctx.obj['session'], repository, label_name, label_color)  
                    output('{}; {}; {}'.format(repository, label_name, label_color), 'ADD', verbose, quiet, True if dry_run else False, False)
                except (BadCredentialException, NotFoundException, GithubErrorException) as e:
                    details = e.args[0]
                    output('{}; {}; {}; {} - {}'.format(details['data']['repo'], details['data']['label_name'], details['data']['label_color'],
                                details['status'], details['message']), 'ADD', verbose, quiet, False, True)
                    error_count += 1
                
            elif label_color != repo_labels[label_key][1] or label_name != repo_labels[label_key][0]:
                try:
                    if not dry_run:
                        update_label(ctx.obj['session'], repository, repo_labels[label_key][0], label_name, label_color)  
                    output('{}; {}; {}'.format(repository, label_name, label_color), 'UPD', verbose, quiet, True if dry_run else False, False)
                except (BadCredentialException, NotFoundException, GithubErrorException) as e:
                    details = e.args[0]
                    output('{}; {}; {}; {} - {}'.format(details['data']['repo'], details['data']['label_name'], details['data']['label_color'],
                                details['status'], details['message']), 'UPD', verbose, quiet, False, True)
                    error_count += 1
                
    # Print summary
    return_code = summary(len(repositories), error_count, verbose, quiet)

    sys.exit(return_code)

if __name__ == '__main__':
    cli(obj={})

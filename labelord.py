# MI-PYT, task 1 (requests+click)
# File: labelord.py
import click
import requests
import configparser
import sys

class BadCredentialException(Exception):
    pass

class NotFoundException(Exception):
    pass

class GithubErrorException(Exception):
    pass

def github_session(token):
    session = requests.Session()
    session.headers = {'User-Agent': 'Python'}
    
    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    return session

# Check status code of https request
def check_status_code(status_code):
    if status_code == 401:
        raise BadCredentialException({'message': 'GitHub: ERROR 401 - Bad credentials', 'code': 4})
    
    if status_code == 404:
        raise NotFoundException({'message': 'GitHub: ERROR 404 - Not Found', 'code': 5})
    
    if status_code != 200:
        raise GithubErrorException({'message': 'GitHub: ERROR {}'.format(status_code), 'code': 10})

# Get request
def get_request(session, url):
    data = []
    r = session.get(url)
    check_status_code(r.status_code) 
    data.extend(r.json())
    
    while 'next' in r.links:
        r = session.get(r.links['next']['url'])
        check_status_code(r.status_code) 
        data.extend(r.json())

    return data

# Get all repos accessible to the authenticated user
def get_repos(session):
    return get_request(session, 'https://api.github.com/user/repos?per_page=100&page=1')

# Get repo labels
def get_labels(session, repo):
    return get_request(session, 'https://api.github.com/repos/{}/labels?per_page=100&page=1'.format(repo))

@click.group('labelord')
@click.option('-c', '--config', default='config.cfg', help='Path to config file')
@click.option('-t', '--token', envvar='GITHUB_TOKEN', help='Secret token for Github account')
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
    session = ctx.obj.get('session', github_session(token))
    if 'session' not in ctx.obj:
        ctx.obj['session'] = session

@cli.command()
@click.pass_context
def list_repos(ctx):
    try:
        repos = get_repos(ctx.obj['session'])
    except BadCredentialException as e:
        print(e.args[0]['message'], file=sys.stderr)
        sys.exit(e.args[0]['code'])               
    except GithubErrorException as e:
        sys.exit(e.args[0]['code'])               
    
    for repo in repos:
        print(repo['full_name'])
    
@cli.command()
@click.argument('repo')
@click.pass_context
def list_labels(ctx, repo):
    try:
        labels = get_labels(ctx.obj['session'], repo)
    except (BadCredentialException, NotFoundException) as e:
        print(e.args[0]['message'], file=sys.stderr)
        sys.exit(e.args[0]['code'])               
    except GithubErrorException as e:
        sys.exit(e.args[0]['code'])               
    
    for label in labels:
        print("#{} {}".format(label['color'], label['name']))

@cli.command()
@click.option('-r', '--template-repo', help='Name of the repo which serves as template')
@click.option('-a', '--all-repos', is_flag=True, default=False, help='Use all available repositories')
@click.argument('mode', type=click.Choice(['update', 'replace']))
@click.pass_context
def run(ctx, template_repo, all_repos, mode):
    # Get labels according to user settings
    labels = []
    if template_repo is not None:
        labels = get_labels(ctx.obj['session'], template_repo)     
    elif 'others' in ctx.obj['config'] and 'template-repo' in ctx.obj['config']['others']:
        labels = get_labels(ctx.obj['session'], ctx.obj['config']['others']['template-repo'])           
    elif 'labels' in ctx.obj['config']:
        for label_name in ctx.obj['config']['labels']:
            labels.append({'name': label_name, 'color': ctx.obj['config']['labels'][label_name]}) 
    else:
        print("No labels specification has been found", file=sys.stderr)
        sys.exit(6)
    
    # Get repositories according to user settings
    repositories = []
    if all_repos:
        repositories = get_repos(ctx.obj['session'])
    elif 'repos' in ctx.obj['config']:
        for repo_name in ctx.obj['config']['repos']:
            if ctx.obj['config'].getboolean('repos', repo_name):
                repositories.append({'full_name': repo_name}) 
    else:
        print("No repositories specification has been found", file=sys.stderr)
        sys.exit(7)

    

if __name__ == '__main__':
    cli(obj={})

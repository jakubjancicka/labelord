# MI-PYT, task 1 (requests+click)
# File: labelord.py
import click
import requests
import configparser
import sys

def github_session(token):
    session = requests.Session()
    session.headers = {'User-Agent': 'Python'}
    
    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    return session

# Get all repos accessible to the authenticated user
def get_repos(session):
    r = session.get('https://api.github.com/user/repos?per_page=100&page=1')
    
    if r.status_code != 200:
        sys.exit(10)
    
    return r.json()

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

    # Verify connection
    try:
        r = session.get('https://api.github.com/user/repos')
    except requests.exceptions.ConnectionError:
        print("Connection with Github can't be established", file=sys.stderr)
        sys.exit(2)               
    
    if r.status_code == 401:
        print("GitHub: ERROR 401 - Bad credentials", file=sys.stderr)
        sys.exit(4)               

@cli.command()
@click.pass_context
def list_repos(ctx):
    repos = get_repos(ctx.obj['session'])
    
    for repo in repos:
        print(repo['full_name'])
    
@cli.command()
@click.argument('repo')
@click.pass_context
def list_labels(ctx, repo):
    # TODO: Add required options/arguments
    # TODO: Implement the 'list_labels' command
    pass

@cli.command()
@click.pass_context
def run(ctx):
    # TODO: Add required options/arguments
    # TODO: Implement the 'run' command
    pass

if __name__ == '__main__':
    cli(obj={})

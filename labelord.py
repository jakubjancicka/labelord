# MI-PYT, task 1 (requests+click)
# File: labelord.py
import click
import requests
import configparser
import sys

def parse_config_file(config_file):
    conf = configparser.ConfigParser()
    conf.read(config_file)
    config = {}
    
    for section in conf.sections():
        config[section] = {}
    
        for option in conf.options(section):
            config[section][option] = conf.get(section, option)
    return config
    

@click.group('labelord')
@click.option('-c', '--config', default='config.cfg', help='Path to config file')
@click.option('-t', '--token', envvar='GITHUB_TOKEN', help='Secret token for Github account')
@click.pass_context
def cli(ctx, config, token):
    # TODO: Add and process required app-wide options
    # You can/should use context 'ctx' for passing
    # data and objects to commands
    
    # Read config from config file
    ctx.obj['config'] = parse_config_file(config)

    # Read token if option or argument are not used
    if token is None and 'github' in ctx.obj['config']:        
        token = ctx.obj['config']['github'].get('token')
    
    # Exit if token has not been provided    
    if not token:    
        print("No GitHub token has been provided", file=sys.stderr)
        sys.exit(3)               
    

    # Use this session for communication with GitHub
    #session = ctx.obj.get('session', requests.Session())

@cli.command()
@click.pass_context
def list_repos(ctx):
    # TODO: Add required options/arguments
    # TODO: Implement the 'list_repos' command
    pass

@cli.command()
@click.pass_context
def list_labels(ctx):
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

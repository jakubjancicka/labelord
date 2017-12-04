"""
This module contains helper functions.
"""
import click
import configparser
import os
import sys


###############################################################################
# HELPERS
###############################################################################


DEFAULT_CONFIG_FILE = './config.cfg'
NO_LABELS_SPEC_RETURN = 6
NO_REPOS_SPEC_RETURN = 7



def create_config(config_filename=None, token=None):
    """
    Parse configuration file.

    :param: ``config_filename``: Path to configuration file.
    :token: ``token``: Github token.
    :return: Dictionary with configuration.
    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg_filename = config_filename or DEFAULT_CONFIG_FILE

    if os.access(cfg_filename, os.R_OK):
        with open(cfg_filename) as f:
            cfg.read_file(f)
    if token is not None:
        cfg.read_dict({'github': {'token': token}})
    return cfg

def extract_labels(gh, template_opt, cfg):
    """
    Extract labels from configuration.
    
    :param: ``gh``: GitHub object
    :param: ``template_opt``: Template repository
    :param: ``cfg``: Dictionary with configuration
    """
    if template_opt is not None:
        return gh.list_labels(template_opt)
    if cfg.has_section('others') and 'template-repo' in cfg['others']:
        return gh.list_labels(cfg['others']['template-repo'])
    if cfg.has_section('labels'):
        return {name: str(color) for name, color in cfg['labels'].items()}
    click.echo('No labels specification has been found', err=True)
    sys.exit(NO_LABELS_SPEC_RETURN)


def extract_repos(cfg):
    """
    Extract repositories from configuration.
    
    :param: ``cfg``: Dictionary with configuration
    :return: List of repositories.
    """
    if cfg.has_section('repos'):
        repos = cfg['repos'].keys()
        return [r for r in repos if cfg['repos'].getboolean(r, False)]
    click.echo('No repositories specification has been found', err=True)
    sys.exit(NO_REPOS_SPEC_RETURN)


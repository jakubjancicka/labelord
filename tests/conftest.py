import sys, os
import betamax
import json
import pytest
import requests
from labelord import github

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CASSETTES_PATH = ABS_PATH + '/fixtures/cassettes'
CONFIGS_PATH = ABS_PATH + '/fixtures/configs'

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = CASSETTES_PATH
    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')
    if 'GITHUB_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'once'
    else:
        config.default_cassette_options['record_mode'] = 'none'
    config.define_cassette_placeholder('<TOKEN>', token)


class Utils:

    @staticmethod
    def config(name):
        return CONFIGS_PATH + '/' + name + '.cfg'

@pytest.fixture
def utils():
    return Utils() 

@pytest.fixture
def gh(betamax_session):
    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')
    gh = github.GitHub(token, betamax_session)
    return gh 

import pytest
import flexmock
from labelord.cli import pick_printer, QuietPrinter, VerbosePrinter, Printer, pick_runner, DryRunProcessor, RunProcessor, gh_error_return, retrieve_github_client
from labelord import helpers

def test_create_config(utils):
    cfg = helpers.create_config(utils.config('basic_config'))
    assert len(cfg.sections()) == 4
    assert 'github' in cfg
    assert 'labels' in cfg
    assert 'repos' in cfg
    assert 'others' in cfg
    assert cfg['github']['token'] == 'MY_SECRET_TOKEN'
    assert cfg['github']['webhook_secret'] == 'WEBHOOK_SECRET_TOKEN'
    assert cfg['labels']['Test'] == 'FF0000'
    assert cfg.getboolean('repos','user/repo') is True
    assert cfg.getboolean('repos','user/repo2') is False
    assert cfg['others']['template-repo'] == 'user/repo'

def test_create_config_nonexisting_cfg(utils):
    cfg = helpers.create_config(utils.config('nonexisting_config'))
    assert len(cfg.sections()) == 0

def test_create_config_add_token(utils):
    cfg = helpers.create_config(utils.config('basic_config'), 'MY_TOKEN')
    assert cfg['github']['token'] == 'MY_TOKEN'
    
    cfg = helpers.create_config(utils.config('config_without_token'), 'MY_TOKEN')
    assert cfg['github']['token'] == 'MY_TOKEN'

def test_extract_repos_no_repo(utils, capsys):
    cfg = helpers.create_config(utils.config('no_repo'))
    with pytest.raises(SystemExit) as e:
        helpers.extract_repos(cfg)
    assert e.value.code == 7
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'No repositories specification has been found\n'

def test_extract_repos(utils):
    cfg = helpers.create_config(utils.config('repos'))
    repos = helpers.extract_repos(cfg)
    assert len(repos) == 3
    assert 'user/repo' in repos
    assert 'user/repo3' in repos
    assert 'user2/repo' in repos    
 
def test_pick_printer_quiet():
    assert pick_printer(False, True) == QuietPrinter

def test_pick_printer_verbose():
    assert pick_printer(True, False) == VerbosePrinter

def test_pick_printer_printer():
    assert pick_printer(True, True) == Printer
    assert pick_printer(False, False) == Printer

def test_pick_runner_run():
    assert pick_runner(False) == RunProcessor

def test_pick_runner_dry():
    assert pick_runner(True) == DryRunProcessor

@pytest.mark.parametrize(
    ['error', 'code'],
    [(401, 4),(404,5)],)
def test_gh_error_return(error, code):
    e = flexmock(status_code=error)
    assert gh_error_return(e) == code


def test_retrieve_github_client_no_token(capsys):
    ctx = flexmock(obj={})
    with pytest.raises(SystemExit) as e:
        retrieve_github_client(ctx)
    assert e.value.code == 3
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'No GitHub token has been provided\n'

def test_retrieve_github_client():
    ctx = flexmock(obj={'GitHub': 'githubclient'})
    assert retrieve_github_client(ctx) == 'githubclient'

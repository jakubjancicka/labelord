import pytest
import flexmock
from labelord import cli
from click.testing import CliRunner

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'list_labels' in result.output
    assert 'list_repos' in result.output
    assert 'run' in result.output

import pytest
import flexmock
from labelord import github, helpers


def test_list_repositories(gh):
    res = gh.list_repositories()
    repos = ['jakubjancicka/wator', 'jakubjancicka/labelord', 'jakubjancicka/Pandas_tutorial', 'jakubjancicka/lunch_guy']
    assert len(res) == 5
    for repo in repos:
        assert repo in res

def test_list_labels(gh):
    res = gh.list_labels('jakubjancicka/labelord')
    labels = {'Test': 'FF4F10', 'bug': 'ee0701', 'duplicate': 'cccccc', 'enhancement': '84b6eb', 'wontfix': 'ffffff'}
    assert len(res) == 5
    for label in labels:
        assert label in res
        assert res[label] == labels[label]

def test_list_labels_no_label(gh):
    res = gh.list_labels('jakubjancicka/wator')
    assert len(res) == 0

    
def test_create_label_repository_doesnt_exist(gh):
    with pytest.raises(github.GitHubError):
        gh.create_label('jakubjancicka/nonexisting', 'test', '123456')

def test_update_label_without_permission(gh):
    with pytest.raises(github.GitHubError):
        gh.update_label('cvut/MI-PYT', 'bug', '123456')

def test_delete_nonexisting_label(gh):
    with pytest.raises(github.GitHubError):
        gh.delete_label('jakubjancicka/wator', 'test')

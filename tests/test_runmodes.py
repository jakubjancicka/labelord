import pytest
import flexmock
from labelord.cli import RunModes

@pytest.mark.parametrize(
    ['labels', 'spec', 'create', 'update', 'delete'],
    [({'l1': 'FF0011'}, {'L1': '000000'}, {}, {'l1': ('L1','000000')}, {}),
    ({'l1': 'FF0011', 'l2': 'FFFFFF'}, {'L1': 'FF0011', 'l3': '123456'}, {'l3': ('l3','123456')}, {'l1': ('L1','FF0011')}, {}),
    ({}, {'L1': 'FF0011', 'l3': '123456'}, {'l3': ('l3','123456'), 'L1': ('L1','FF0011')}, {}, {}),
    ({'L1': 'FF0011', 'l3': '123456'}, {}, {}, {}, {})
    ],
)
def test_update_mode(labels, spec, create, update, delete):
    c, u, d = RunModes.update_mode(labels, spec)
    
    assert len(c) == len(create)
    assert len(u) == len(update)
    assert len(d) == len(delete)
    for i in c:
        assert i in create
        assert c[i] == create[i]
    for i in u:
        assert i in update
        assert u[i] == update[i]
    for i in d:
        assert i in delete
        assert d[i] == delete[i]

@pytest.mark.parametrize(
    ['labels', 'spec', 'create', 'update', 'delete'],
    [({'l1': 'FF0011'}, {'L1': '000000'}, {}, {'l1': ('L1','000000')}, {'l1': ('l1','FF0011')}),
    ({'l1': 'FF0011', 'l2': 'FFFFFF'}, {'L1': 'FF0011', 'l3': '123456'}, {'l3': ('l3','123456')}, {'l1': ('L1','FF0011')}, {'l1': ('l1','FF0011'), 'l2': ('l2','FFFFFF')}),
    ({}, {'L1': 'FF0011', 'l3': '123456'}, {'l3': ('l3','123456'), 'L1': ('L1','FF0011')}, {}, {}),
    ({'L1': 'FF0011', 'l3': '123456'}, {}, {}, {}, {'L1': ('L1','FF0011'), 'l3': ('l3','123456')})
    ],
)
def test_replace_mode(labels, spec, create, update, delete):
    c, u, d = RunModes.replace_mode(labels, spec)
    
    assert len(c) == len(create)
    assert len(u) == len(update)
    assert len(d) == len(delete)
    for i in c:
        assert i in create
        assert c[i] == create[i]
    for i in u:
        assert i in update
        assert u[i] == update[i]
    for i in d:
        assert i in delete
        assert d[i] == delete[i]

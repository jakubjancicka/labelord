import pytest
import flexmock
from labelord.cli import BasePrinter, Printer, QuietPrinter, VerbosePrinter


def test_printer(capsys):
    printer = Printer()
    printer.add_repo('repo1')
    printer.add_repo('repo2')
    printer.add_repo('repo3')
    printer.event('ADD', 'ERR', 'repo1', 'label1')
    printer.event('ADD', 'SUC', 'repo1', 'label2')
    printer.event('DEL', 'SUC', 'repo2', 'label2')
    printer.event('DEL', 'ERR', 'repo2', 'label1')
    printer.event('UPD', 'SUC', 'repo3', 'label3')
    printer.event('UPD', 'ERR', 'repo3', 'label4')
    printer.event('ADD', 'DRY', 'repo3', 'label4')
    printer.event('DEL', 'DRY', 'repo3', 'label4')
    printer.summary() 

    out, err = capsys.readouterr()
    out = out.split('\n')
    assert len(out) == 5
    assert out[0] == 'ERROR: ADD; repo1; label1'
    assert out[1] == 'ERROR: DEL; repo2; label1'
    assert out[2] == 'ERROR: UPD; repo3; label4'
    assert out[3] == 'SUMMARY: 3 error(s) in total, please check log above'
    assert out[4] == ''
    assert err == ''

def test_printer_no_error(capsys):
    printer = Printer()
    printer.add_repo('repo1')
    printer.add_repo('repo2')
    printer.add_repo('repo3')
    printer.event('ADD', 'SUC', 'repo1', 'label2')
    printer.event('DEL', 'SUC', 'repo2', 'label2')
    printer.event('UPD', 'SUC', 'repo3', 'label3')
    printer.event('ADD', 'DRY', 'repo3', 'label4')
    printer.event('DEL', 'DRY', 'repo3', 'label4')
    printer.summary() 

    out, err = capsys.readouterr()
    assert out == 'SUMMARY: 3 repo(s) updated successfully\n'
    assert err == ''

def test_quiet_printer(capsys):
    printer = QuietPrinter()
    printer.add_repo('repo1')
    printer.add_repo('repo2')
    printer.add_repo('repo3')
    printer.event('ADD', 'ERR', 'repo1', 'label1')
    printer.event('ADD', 'SUC', 'repo1', 'label2')
    printer.event('DEL', 'SUC', 'repo2', 'label2')
    printer.event('DEL', 'ERR', 'repo2', 'label1')
    printer.event('UPD', 'SUC', 'repo3', 'label3')
    printer.event('UPD', 'ERR', 'repo3', 'label4')
    printer.event('ADD', 'DRY', 'repo3', 'label4')
    printer.event('DEL', 'DRY', 'repo3', 'label4')
    printer.summary() 

    out, err = capsys.readouterr()
    assert err == ''
    assert out == ''

def test_verbose_printer(capsys):
    printer = VerbosePrinter()
    printer.add_repo('repo1')
    printer.add_repo('repo2')
    printer.add_repo('repo3')
    printer.event('ADD', 'ERR', 'repo1', 'label1')
    printer.event('ADD', 'SUC', 'repo1', 'label2')
    printer.event('DEL', 'SUC', 'repo2', 'label2')
    printer.event('DEL', 'ERR', 'repo2', 'label1')
    printer.event('UPD', 'SUC', 'repo3', 'label3')
    printer.event('UPD', 'ERR', 'repo3', 'label4')
    printer.event('ADD', 'DRY', 'repo3', 'label4')
    printer.event('DEL', 'DRY', 'repo3', 'label4')
    printer.summary() 
    
    out, err = capsys.readouterr()
    out = out.split('\n')
    assert len(out) == 10
    assert out[0] == '[ADD][ERR] repo1; label1'
    assert out[1] == '[ADD][SUC] repo1; label2'
    assert out[2] == '[DEL][SUC] repo2; label2'
    assert out[3] == '[DEL][ERR] repo2; label1'
    assert out[4] == '[UPD][SUC] repo3; label3'
    assert out[5] == '[UPD][ERR] repo3; label4'
    assert out[6] == '[ADD][DRY] repo3; label4'
    assert out[7] == '[DEL][DRY] repo3; label4'
    assert out[8] == '[SUMMARY] 3 error(s) in total, please check log above'
    assert out[9] == ''
    assert err == ''

def test_verbose_printer_no_error(capsys):
    printer = VerbosePrinter()
    printer.add_repo('repo1')
    printer.add_repo('repo2')
    printer.add_repo('repo3')
    printer.event('ADD', 'SUC', 'repo1', 'label2')
    printer.event('DEL', 'SUC', 'repo2', 'label2')
    printer.event('UPD', 'SUC', 'repo3', 'label3')
    printer.event('ADD', 'DRY', 'repo3', 'label4')
    printer.event('DEL', 'DRY', 'repo3', 'label4')
    printer.summary() 
    
    out, err = capsys.readouterr()
    out = out.split('\n')
    assert len(out) == 7
    assert out[0] == '[ADD][SUC] repo1; label2'
    assert out[1] == '[DEL][SUC] repo2; label2'
    assert out[2] == '[UPD][SUC] repo3; label3'
    assert out[3] == '[ADD][DRY] repo3; label4'
    assert out[4] == '[DEL][DRY] repo3; label4'
    assert out[5] == '[SUMMARY] 3 repo(s) updated successfully'
    assert out[6] == ''
    assert err == ''

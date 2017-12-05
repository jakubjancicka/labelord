Examples of output
==================
In this section you can find a few examples of outputs which are produced when you run a labelord application. It shows differences between normal mode, verbose mode and quiet mode.

.. testsetup::
 
    import os
    import click
    import sys
    import time
    from labelord.cli import BasePrinter, Printer, QuietPrinter, VerbosePrinter

- Normal mode

    In normal mode only errors are printed. 
    
    .. testcode::

        printer = Printer()
        printer.add_repo('repo/test')
        printer.add_repo('repo/test2')
        printer.event(Printer.EVENT_CREATE, Printer.RESULT_SUCCESS, 'repo/test', 'Label', 'FF0000')
        printer.event(Printer.EVENT_DELETE, Printer.RESULT_ERROR, 'repo/test', 'Label2', '000000')
        printer.event(Printer.EVENT_UPDATE, Printer.RESULT_ERROR, 'repo/test2', 'Label1', 'FF0000')
        printer.summary()

       

    .. testoutput::
        
        ERROR: DEL; repo/test; Label2; 000000
        ERROR: UPD; repo/test2; Label1; FF0000
        SUMMARY: 2 error(s) in total, please check log above

- Verbose mode
    
    In verbose mode all events are printed.
    
    .. testcode::

        printer = VerbosePrinter()
        printer.add_repo('repo/test')
        printer.add_repo('repo/test2')
        printer.event(Printer.EVENT_CREATE, Printer.RESULT_SUCCESS, 'repo/test', 'Label', 'FF0000')
        printer.event(Printer.EVENT_DELETE, Printer.RESULT_ERROR, 'repo/test', 'Label2', '000000')
        printer.event(Printer.EVENT_UPDATE, Printer.RESULT_ERROR, 'repo/test2', 'Label1', 'FF0000')
        printer.summary()

       

    .. testoutput::
        
        [ADD][SUC] repo/test; Label; FF0000
        [DEL][ERR] repo/test; Label2; 000000
        [UPD][ERR] repo/test2; Label1; FF0000
        [SUMMARY] 2 error(s) in total, please check log above

- Quiet mode

    In quiet mode nothing is printed.
    
    .. testcode::

        printer = QuietPrinter()
        printer.add_repo('repo/test')
        printer.add_repo('repo/test2')
        printer.event(Printer.EVENT_CREATE, Printer.RESULT_SUCCESS, 'repo/test', 'Label', 'FF0000')
        printer.event(Printer.EVENT_DELETE, Printer.RESULT_ERROR, 'repo/test', 'Label2', '000000')
        printer.event(Printer.EVENT_UPDATE, Printer.RESULT_ERROR, 'repo/test2', 'Label1', 'FF0000')
        printer.summary()

       

    .. testoutput::
        
        

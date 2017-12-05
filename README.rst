Labelord
========

Labelord is multi-project management of GitHub labels. This Python application allows user to list repositories, list labels for given repository and update or replace labels for multiple projects according to configuration. Application has command-line and web interface. User can run master-to-master replication web server which works with GitHub webhooks and manage labels for multiple repositories in even simpler way.

Installation
------------
There are two ways of installation you can choose from. 

The first one is from *Test Pypi*.

    python -m pip install --extra-index-url https://test.pypi.org/pypi labelord_jancijak

The second one is from GitHub repository.
    - Download Python labelord module from https://github.com/jakubjancicka/labelord
    - Install module: ``python setup.py install``

Documentation
-------------
Documentation contains information about installation, license and describes configuration file, CLI and Web interface. It also contains code examples and API reference.

If you want to build documentation, run following commands from top level direcory of this repository:

    cd ./docs

    python -m install -r requirements.txt

    make doctest

    make html
    
Documentation is also published online on http://labelord-jancijak.readthedocs.io/en/latest/.

Configuration
-------------
Example configuration (*config.cfg.sample*) can be found in *labelord* directory. All sections are described in documentation. 

License
-------
Module *labelord* is published under GNU GPL license. See LICENSE for further details.

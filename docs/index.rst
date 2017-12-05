.. labelord documentation master file, created by
   sphinx-quickstart on Mon Dec  4 17:59:25 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to labelord's documentation!
====================================

Labelord is multi-project management of GitHub labels. This Python application allows user to list repositories, list labels for given repository and update or replace labels for multiple projects according to configuration. Application has command-line and web interface. User can run master-to-master replication web server which works with GitHub webhooks and manage labels for multiple repositories in even simpler way. 

User's Guide
============
This part of the documentation contains information about installation, license and describes configuration file, CLI and Web interface. This part also contains code examples.

.. toctree::
    :maxdepth: 1
    
    installation
    license
    config_file
    cli_application
    web_application

API Reference
=============
Information about modules, classes and functions of labelord can be find in this section. 

.. toctree::
   :maxdepth: 4

   labelord


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

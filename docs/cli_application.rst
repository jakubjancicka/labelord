Command-line application
========================

If you want to use command-line application run:

.. code:: Python
    
    labelord [options] [subcommand] 

Options can be found :ref:`here<options>`.

There are 3 subcommand:

List repositories
-----------------
You can print all repositories which are accessible by user.

.. code:: Python

    labelord [options] list_repos 
    
List labels
-----------
This subcommand print labels in given repository.

.. code:: Python

    labelord [options] list_labels [repository]

Run modes
---------
This subcommand changes labels. It operates in two modes:

- update
    This mode adds missing labels and updates color of existing tags.

    .. code:: Python

        labelord [options] run update [options]
    
- replace
    This mode adds missing labels and updates color of existing tags. This mode also deletes tags which are not defined.

    .. code:: Python

        labelord [options] run replace [options]

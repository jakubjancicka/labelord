Configuration
=============

There are three ways to set configuration. You can use :ref:`config-file`, :ref:`envars` and :ref:`options` (ordered by priority from lowest to the highest). For proper function of labelord module you have to obtain :ref:`githubtoken` and :ref:`secret`.

.. _githubtoken:

Github token
------------
Github token serves for authentification of user when labelord application communicates with GitHub via API.  

For obtaining your Github token you must follow these steps:

1. Log into your account on www.github.com
2. Click on **Profile** > **Settings** > **Developer settings** > **Personal access tokens**
3. Then clik on **Generate new token** button.
4. Fill a *token description* and from *Select scopes* select *repo* in *public* section.
5. Don't forget to copy your token because you will never see it again.

.. warning:: This token should remain in secret. Be careful to work with it and never place it on public place!

.. _secret:

Github webhoook secret
----------------------
You can use desired repository as a template repository - every label change is propagated to other repositories. For this function webhooks are used. Webhook secret is used for GitHub webhook verification.

For obtaining your Github webhook secret you must follow these steps:

1. Log into your account on www.github.com
2. Open your repository.
3. Click on **Settings** > **Webhooks** > **Add webhook**
4.  **Generate new token** button.
5. Fill a form.
6. Click on **Add webhook** button.

.. _config-file:

Configuration file
------------------
Configuration file is written in INI format. Default path to configuration file is in ``./config.cfg``, file path can be modified by command option ``-c/--config``.

Configuration file has several sections.

- In *Github* section there are stored :ref:`githubtoken` and :ref:`secret`. 

.. code::

    [github]
    token = MY_SECRET_TOKEN
    webhook_secret = WEBHOOK_SECRET_TOKEN

- In *labels* section there are definitions of labels. It consists of *name of label* and *color of label*.

.. code::

    [labels]
    Test = FF0000

- In *repos* section there are repositories whose labels can be modified. You can manualy turn on / off synchronization for each repository with on/off flag. 

.. code::

    [repos]
    user/repo = on
    user/repo2 = off

- In *others* section is defined a template repository. Labels definition in this repository will be propagated to other repositories.

.. code::

    [others]
    template-repo = user/repo

.. _envars:

Enviroment variables
--------------------
You can use enviroment variables to modify configuration of labelord application. 

- ``GITHUB_TOKEN`` Set :ref:`githubtoken`.

- ``LABELORD_CONFIG`` Set path to :ref:`config-file`.

.. _options:

Command options
---------------
The last way for configurating application is command options.

- ``-c/config [FILE]`` Set path to :ref:`config-file`.

- ``-t/--token [STRING]`` Set :ref:`githubtoken`.

- ``-r/--template-repo [STRING]`` Set template repository.

- ``-a/--all-repos`` Labels from all repositories will be changed if set.

- ``-d/--dry-run`` Set dry run mode.

- ``-v/--verbose`` Set verbose mode.

- ``-q/--quiet`` Set no output on terminal.

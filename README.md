# labelord

Global multi-project management of GitHub labels (MI-PYT@FIT CTU project)

----

This Python app allows user to do via CLI:

* List repositories
* List labels for given repository
* Run update/replace labels for multiple projects (labels are specified in configuration file or by template repo)

App allows you run master-to-master replication web server which works with GitHub webhooks and manage labels for multiple repositories in even simpler way (try `run_server` command and see landing page for more information)!

TESTS
Tests can be found in 'tests' directory.
 
Run this command for start testing:
`python setup.py test`

If you want to re-record cassettes, you have to delete them from 'tests/fixture    s/cassettes' directory and you have to export variable 'GITHUB_TOKEN' with your     GitHub token.
~                  

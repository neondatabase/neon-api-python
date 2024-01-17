# neon_client: an api wrapper for neon.tech v2 api



## Future Installation

```bash
$ pip install neon-client
```

**Please Note**: this repository is a work in progress.  The package is not yet available on PyPi.  The above command will not work.

## Usage

```pycon
>>> from neon_client import NeonClient

>>> neon = NeonClient(api_key='your_api_key')

>>> # List all the API keys.
>>> api_keys = neon.api_keys()

>>> # Get a specific API key.
>>> api_key = neon.api_key(api_key_id='your_api_key_id')

>>> # Get all the projects
>>> projects = neon.projects()


>>> # Get a specific project
>>> project = neon.project(project_id='your_project_id')

>>> # Get all the databases
>>> databases = neon.databases()

>>> # Get a specific database
>>> database = neon.database(database_id='your_database_id')

>>> # Get all the branches for a given database.
>>> branches = neon.branches(database_id='your_database_id')

>>> # Get a specific branch
>>> branch = neon.branch(database_id='your_database_id', branch_id='your_branch_id')


```

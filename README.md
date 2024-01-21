# `neon_client`: an api wrapper for [neon.tech v2 api](https://api-docs.neon.tech/reference/getting-started-with-neon-api)

This Python wrapper would allow developers to interact with the Neon API with ease. Instead of directly making HTTP requests and handling responses, developers can use this wrapper to call simple functions that return Python objects. 

```python
from neon_client import NeonAPI

# Initialize the client.
client = NeonApi(api_key='your_api_key')
```

Methods of `NeonClient`:

- `me()`: Returns the current user.
- `api_keys()`: Returns a list of API keys.
- `api_key_create(key_name)`: Creates an API key.
- `api_key_delete(key_id)`: Deletes a given API key.
- `projects()`: Returns a list of projects.
- `project(project_id)`: Returns a specific project.
- `project_create(project_id, json)`: Creates a new project. 
- `project_update(project_id, json)`: Updates a given project.
- `project_delete(project_id)`: Deletes a given project.
- `branches(project_id)`
- `branch(project_id, branch_id)`
- `branch_create(project_id, **json)`
- `branch_update(project_id, branch_id, **json)`
- `branch_delete(project_id, branch_id)`
- `branch_set_as_primary(project_id, branch_id)`
- `databases(project_id, branch_id)`
- `database(project_id, branch_id, database_id)`
- `database_create(project_id, branch_id, **json)`
- `database_update(project_id, branch_id, **json)`
- `database_delete(project_id, branch_id, database_id)`
- `endpoints()`
- `endpoint_create()`
- `endpoint_update()`
- `endpoint_delete()`
- `endpoint_start()`
- `endpoint_suspend()`
- `role()`
- `roles()`
- `role_create()`
- `role_delete()`
- `role_password_reveal()`
- `role_password_reset()`
- `operations()`
- `operation()`
- `...`

Remember that you should never expose your api_key and handle it carefully since it gives access to sensitive data. It's better to set it as an environment variable (e.g. `NEON_API_KEY` + accompanying `neon_client.from_environ()`).

## Installation

```bash
$ pip install neon-client
```

**Please Note**: this repository is a work in progress.  The package is not yet available on PyPi.  The above command will not work.

## Usage

```python
>>> from neon_client import NeonClient

>>> neon = NeonClient(api_key='your_api_key')

# List all the API keys.
>>> api_keys = neon.api_keys()

# Get a specific API key.
>>> api_key = neon.api_key(api_key_id='your_api_key_id')

# Get all the projects
>>> projects = neon.projects()

# Get a specific project
>>> project = neon.project(project_id='your_project_id')

# Get all the databases
>>> databases = neon.databases()

# Get a specific database
>>> database = neon.database(database_id='your_database_id')

# Get all the branches for a given database.
>>> branches = neon.branches(database_id='your_database_id')

# Get a specific branch
>>> branch = neon.branch(database_id='your_database_id', branch_id='your_branch_id')
```

## Development

[to be written]

## License & Copyright

[MIT licensed](./LICENSE).

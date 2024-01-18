# `neon_client`: an api wrapper for [neon.tech v2 api](https://api-docs.neon.tech/reference/getting-started-with-neon-api)

This Python wrapper would allow developers to interact with the Neon API with ease. Instead of directly making HTTP requests and handling responses, developers can use this wrapper to call simple functions that return Python objects. 

```python
from neon_client import NeonAPI

# Initialize the client.
client = NeonApi(api_key='your_api_key')
```

Methods of `NeonClient`:

- `me()`: Returns the current user.
- `project(project_id)`: Returns a specific project.
- 

Remember that you should never expose your api_key and handle it carefully since it gives access to sensitive data. It's better to set it as an environment variable (e.g. `NEON_API_KEY` + accompanying `neon_client.from_environ()`).

Please note that this is a hypothetical example and might not work without proper implementation considering neon.tech's actual API documentation. 

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

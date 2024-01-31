.. neon-client documentation master file, created by
   sphinx-quickstart on Fri Jan 26 14:52:57 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

``neon-client`` — Python client for the Neon API.
=================================================

This is the documentation for the ``neon_client`` package. It is a Python client for the Neon API. ``neon_client`` empowers 
developers by providing a comprehensive Python wrapper around the Neon API. This enables seamless integration of Neon's 
cloud database capabilities into Python applications, facilitating a wide range of operations such as managing API keys, 
projects, branches, databases, endpoints, roles, and operations directly from your codebase.

With ``neon_client``, developers can:

- Automate the provisioning and management of Neon cloud databases.
- Programmatically control and manipulate database endpoints and roles.
- Streamline workflows by integrating database operations into CI/CD pipelines.
- Enhance application security by managing API keys and permissions through code.
- Leverage the power of Neon's cloud database without the need for manual intervention or the Neon console.

This project simplifies the complexity of interacting with the Neon API, making it more accessible for developers to 
build scalable, data-driven applications with ease. Pydantic dataclasses are used to represent the data structures returned
by the API, and the client provides a relatively transparent interface to the Neon API.

.. note::

    This documentation is a work in progress. It is not yet complete.

Installation
------------

To install the package, run the following command:

.. code-block:: bash

    $ pip install neon-client

Usage
-----

To use the package, you need to have a valid API key. You can obtain an API key from the Neon console. 
Once you have an API key, you can use the ``neon_client`` package to interact with the Neon API.

There are two ways to initialize the client:

1. By passing the API key directly to the client.
2. By setting the API key as an environment variable and using the `from_environ` method.

We recommend using the second method to avoid exposing your API key in your codebase:

.. code-block:: bash

    $ export NEON_API_KEY=your_api_key

Then, from Python…

.. code-block:: python

    from neon_client import NeonAPI

    neon = NeonAPI.from_environ()


Quickstart
----------

Below is an example of how to use the package to interact with the Neon API:

.. code-block:: python

    from neon_client import NeonAPI

    # Initialize the client.
    neon = NeonAPI.from_environ() or NeonAPI(api_key='your_api_key')

    # Get the current user
    user = neon.me()
    print(user)

    # Get a list of API keys
    keys = neon.api_keys()
    print(keys)

    # Create a new API key
    new_key = neon.api_key_create(name="new_key")
    print(new_key)

    # Revoke an API key
    revoked_key = neon.api_key_revoke(api_key_id="api_key_id_to_revoke")
    print(revoked_key)

    # Get a list of projects
    projects = neon.projects()
    print(projects)

    # Get a specific project
    project = neon.project(project_id="project_id_to_get")
    print(project)

    # Create a new project
    new_project = neon.project_create(name="new_project")
    print(new_project)

    # Update a project
    updated_project = neon.project_update(project_id="project_id_to_update", name="updated_name")
    print(updated_project)

    # Delete a project
    deleted_project = neon.project_delete(project_id="project_id_to_delete")
    print(deleted_project)

    # Get a project permissions
    permissions = neon.project_permissions(project_id="project_id_to_get_permissions")
    print(permissions)

    # Grant permissions to a project
    granted_permissions = neon.project_permissions_grant(project_id="project_id_to_grant_permissions", user_id="user_id_to_grant", permissions=["read", "write"])
    print(granted_permissions)

    # Revoke permissions from a project
    revoked_permissions = neon.project_permissions_revoke(project_id="project_id_to_revoke_permissions", user_id="user_id_to_revoke")
    print(revoked_permissions)

    # Get a list of branches for a given project
    branches = neon.branches(project_id="project_id_to_get_branches")
    print(branches)

    # Get a specific branch
    branch = neon.branch(project_id="project_id_to_get_branch", branch_id="branch_id_to_get")
    print(branch)

    # Create a new branch
    new_branch = neon.branch_create(project_id="project_id_to_create_branch", name="new_branch")
    print(new_branch)

    # Update a branch
    updated_branch = neon.branch_update(project_id="project_id_to_update_branch", branch_id="branch_id_to_update", name="updated_name")
    print(updated_branch)

    # Delete a branch
    deleted_branch = neon.branch_delete(project_id="project_id_to_delete_branch", branch_id="branch_id_to_delete")
    print(deleted_branch)

    # Get a list of roles for a given branch
    roles = neon.roles(project_id="project_id_to_get_roles", branch_id="branch_id_to_get_roles")
    print(roles)

    # Get a role for a given branch
    role = neon.role(project_id="project_id_to_get_role", branch_id="branch_id_to_get_role", role_name="role_name_to_get")
    print(role)

    # Create a new role
    new_role = neon.role_create(project_id="project_id_to_create_role", branch_id="branch_id_to_create_role", role_name="new_role")
    print(new_role)

    # Delete a role
    deleted_role = neon.role_delete(project_id="project_id_to_delete_role", branch_id="branch_id_to_delete_role", role_name="role_name_to_delete")
    print(deleted_role)

    # Get a role password
    password = neon.role_password_reveal(project_id="project_id_to_get_password", branch_id="branch_id_to_get_password", role_name="role_name_to_get_password")
    print(password)

    # Reset a role password
    reset_password = neon.role_password_reset(project_id="project_id_to_reset_password", branch_id="branch_id_to_reset_password", role_name="role_name_to_reset_password")
    print(reset_password)

    # Get a list of operations
    operations = neon.operations(project_id="project_id_to_get_operations")
    print(operations)

    # Get an operation
    operation = neon.operation(project_id="project_id_to_get_operation", operation_id="operation_id_to_get")
    print(operation)

    # Get a list of consumption metrics for all projects
    consumption = neon.consumption()
    print(consumption)


API Reference
-------------

The following sections provide detailed information about the classes and methods available in the ``neon_client`` package

.. automodule:: neon_client
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

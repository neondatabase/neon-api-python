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

.. note::

    This documentation is a work in progress. It is not yet complete.

This project simplifies the complexity of interacting with the Neon API, making it more accessible for developers to 
build scalable, data-driven applications with ease. Pydantic dataclasses are used to represent the data structures returned
by the API, and the client provides a relatively transparent interface to the Neon API.

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

Please reference the API Reference section for a comprehensive list of available methods and classes.

API Reference
-------------

The following sections provide detailed information about the classes and methods available in the ``neon_client`` package

Module–level functions
//////////////////////

.. automodule:: neon_client
    :members:
    :undoc-members:
    :show-inheritance:

Classes
///////

.. autoclass:: neon_client.NeonAPI
    :members:
    :undoc-members:
    :show-inheritance:

--------------------

.. automodule:: neon_client.schema
    :members:
    :undoc-members:
    :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

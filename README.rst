Absio Python Library
====================

Protect your application's sensitive data with Absio's Secured Containers.

Obtaining an API Key
~~~~~~~~~~~~~~~~~~~~

The ``absio`` library requires a valid API Key that must be passed into the
``absio.initialize(...)`` function.  Obtain an API Key by contacting us
`here <https://www.absio.com/contact>`_ or sending an email to sales@absio.com. An API key should
be considered private and protected as such.

Quick Start
~~~~~~~~~~~

Installation:

.. code:: python

    pip install absio

Import and initialize the module:

.. code:: python

    import absio
    absio.initialize(api_key='your api key')

Create accounts:

.. code:: python

    alice = absio.user.create('password', 'reminder', 'passphrase')
    bob = absio.user.create('password', 'reminder', 'passphrase')

Log in with an account:

.. code:: python

    absio.login(alice.id, 'password', 'passphrase')

Create and share an Absio Secured Container:

.. code:: python

    container = absio.container.create(
        header={'some sensitive metadata': None},
        content=open('/some/sensitive/data.bin/', 'rb').read(),
        access=[bob.id, alice.id],
    )

Securely access this container from another system:


.. code:: python

    absio.login(bob.id, 'password', 'passphrase')

    # Access the container with the container ID returned during creation, or a Container Event.
    container = absio.container.get('container_id')


Getting Started
===============

You can be up and running with the ``absio`` Python library in minutes.  Follow the guide below to
rapidly create and share encrypted content between users.

.. _get_api_key:

Obtaining an API Key
~~~~~~~~~~~~~~~~~~~~

The ``absio`` library requires a valid API Key that must be passed into the :func:`initialize()
<absio.initialize>` function.  Obtain an API Key by contacting us here_ or sending an email to
sales@absio.com. An API key should be considered private and protected as such.

.. _quickstart:

Quick Start
~~~~~~~~~~~

#. Installation::

    pip install absio

#. Import and initialize the module::

    import absio
    absio.initialize(api_key='your api key')

#. Create accounts::

    alice = absio.user.create('password', 'reminder', 'passphrase')
    bob = absio.user.create('password', 'reminder', 'passphrase')

#. Log in with an account::

    absio.login(alice.id, 'password', 'passphrase')

#. Create and share an Absio Secured Container::

    container = absio.container.create(
        header={'some sensitive metadata': None},
        content=open('/some/sensitive/data.bin/', 'rb').read(),
        access=[bob.id, alice.id],
    )

#. Securely access this container from another system::

    absio.login(bob.id, 'password', 'passphrase')

    # Access the container with the container ID returned during creation, or a Container Event.
    container = absio.container.get('container_id')

.. _here: https://www.absio.com/contact

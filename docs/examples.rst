Examples
========

Sometimes the easiest way to learn is by seeing the library in action.  Here are a collection of
fully working examples that demonstrate the flexibility and ease of use of the ``absio`` library.


.. note::

    These examples require the installation of the `Click <http://click.pocoo.org>`_ library.

User Manipulation
~~~~~~~~~~~~~~~~~

This tool allows you to create users and modify their credentials.  Users can also be imported
into new systems.:

.. literalinclude:: ../examples/cli/user_util.py


Content Sharing
~~~~~~~~~~~~~~~

Being able to securely and easily share content with other users is the main use case for using
the ``absio`` library.  This tool allows you select local files and recipients with whom they
should be shared:

.. literalinclude:: ../examples/cli/container_util.py

.. _custom_provider_example:

Custom Provider
~~~~~~~~~~~~~~~

Curious how to create your own provider?  Here's an example that illustrates using the Absio API
Server Application for everything except the encrypted secured container content - the management
of the actual encrypted content is now the responsibility of the library user.

Imagine that you have requirements where you cannot store your content in a cloud provider, or
perhaps only within a specific cloud provider, or on a SAN, etc.  This provider shows how you can
quickly override the default behavior and you become responsible for managing content, while still
fully leveraging the Absio API Server Application for its user and key management system:

.. literalinclude:: ../examples/providers/self_managed_content.py

So how would you go about using this provider?  Like this::

    with absio.providers.provider(self_managed):
        user = absio.login(user_id, password)
        # This container is created on the server and in the OFS, but the content is not stored
        # in either location.
        container = absio.container.create(content)
        # Now you, the app developer, decide where to store the data.  Here's an example:
        open('/tmp/{}'.format(container.id), 'wb').write(container.data)

        # Now to fetch the container back and merge it with your encrypted data:
        data = open('/tmp/{}'.format(container.id), 'rb').read()
        container = absio.container.get(container.id, data=data)

Note that the storage and retrieval of your self-managed data could just as easily have been
accomplished within the implementation of the :meth:`get` and :meth:`update_or_create` methods.
This would reduce the sample usage to just the :meth:`create` and :meth:`get`.
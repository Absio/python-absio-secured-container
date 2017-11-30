Providers
=========

A `provider` is a core feature of the ``absio`` library.  It handles (provides) the main Absio
data types:

* Secured Containers
* Users
* Keys
* Key Files
* Events

Providers manage creating, updating, reading, and deleting those data types from their dedicated
locations.

This library ships with three providers: one for the :ref:`server_provider`, another for the
:ref:`ofs_provider`, and a final one that combines the two: :ref:`server_cache_ofs_provider`.  By
default, all operations will utilize the :ref:`server_cache_ofs_provider` provider.

.. _server_provider:

Server
~~~~~~

All data is synchronized with the Absio API Server Application.  Harness the power of a central
server to ensure that your data is available from anywhere, anytime.

.. _ofs_provider:

Obfuscating File System (OFS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All data is stored in the OFS.  This is an entirely local (file-system) based provider that does
not require the usage of the Absio API Server Application.

For a greater understanding of the OFS, consider reading up on the :ref:`technology <ofs_tech>`
powering it.

.. _server_cache_ofs_provider:

Server Cache OFS
~~~~~~~~~~~~~~~~

This provider joins together the Server and OFS providers.  When data (containers, keys, etc.) is
requested, the OFS is first queried.  If it is found (cache hit), it is returned immediately,
otherwise (cache miss) the server is then queried.  If the data is found on the server, the
provider will attempt to store it in the OFS cache before returning it to the caller potentially
resulting in a cache hit on subsequent requests.

Custom
~~~~~~

The power of a provider really shines when it comes time to modify where your secured containers
reside.  If you wanted to instead store your data on a local SAN, or in a different cloud service,
you could create your own provider that does :ref:`exactly this <custom_provider_example>`.
This is not limited to secured containers but can apply to any type of data managed by a provider:
containers, keys, users, events, etc.

To develop your own provider, it must match the existing provider interfaces.  (See the
:ref:`providers <api_provider_section>` API section for specific details.)  The full interface only
needs to be implemented if you plan to execute the "top level" module functions and make your custom
provider the default one.  Otherwise, you only need to implement the specific interface that will
be called.

For instance, the :ref:`example <custom_provider_example>` is complete to the point it can be made the
default provider and used without a context manager.  But if just part of your program required that you
retrieved public keys from another source, you could just implement the :func:`keys.get` interface and
use it with a context manager.


Utilization
~~~~~~~~~~~

There is a provider context manager that can be used to allow for easily modifying which bits of
data go where.  So while the default settings have the data being stored on both the Absio API
Server Application and in your local OFS, you can selectively mark specific content as being
stored in just one location only::

    import absio
    from absio.providers import provider, server, ofs, server_cache_ofs

    # This content is only stored in the Absio API Server Application
    with provider(server):
        container = absio.container.create(...)

    # While this content is only stored locally in the OFS.
    with provider(ofs):
        container = absio.container.create(...)

    # And this content is stored in both locations.  If no context manager is used, the default
    # provider (server_cache_ofs) will be selected.  Thus the following two statements are
    # equivalent.
    container = absio.container.create(...)

    with provider(server_cache_ofs):
        container = absio.container.create(...)

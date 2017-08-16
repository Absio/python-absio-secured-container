Providers
=========

Where and how your data is stored is handled by the concept of a Provider.  A Provider handles
synchronizing your data with a destination source.  This library ships with two providers: one for
the :ref:`server_provider` and another for the :ref:`ofs_provider`.  By
default, all operations that involve the creation or fetching of content will utilize both
providers.

.. _server_provider:

Server
~~~~~~

All data is synchronized with the public Absio API Server Application.

.. _ofs_provider:

Obfuscating File System (OFS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All data is stored in the OFS.  In the default case of both providers being enabled, this OFS
provider acts as a cache, reducing the amount of network traffic required.  If something exists
locally in the OFS and is up to date, it is used first before the Server Application is accessed.

For a greater understanding of the OFS, consider reading up on the :ref:`technology <ofs_tech>`
powering it.


Custom
~~~~~~

The power of a Provider really shines when it comes time to modify where your secured containers
reside.  If you wanted to instead store your data on a local SAN, or in a different cloud service,
you could create your own provider that does exactly this.


Utilization
~~~~~~~~~~~

Providers used with standard Python context managers allow for easily modifying which bits of data
go where.  So while the default settings have the data being stored on both the Absio API Server
Application and in your local OFS, you can selectively mark specific content as being stored in
just one location only::

    from absio import providers, Container

    # This content is only stored in the Absio API Server Application
    with providers.server:
        container = Container(...)

    # While this content is only stored locally in the OFS.
    with providers.ofs:
        container = Container(...)

    # And this content is stored in both locations.
    container = Container(...)

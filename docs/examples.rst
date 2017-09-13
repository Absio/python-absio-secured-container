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

.. literalinclude:: ../examples/user_util.py


Content Sharing
~~~~~~~~~~~~~~~

Being able to securely and easily share content with other users is the main use case for using
the ``absio`` library.  This tool allows you select local files and recipients with whom they
should be shared:

.. literalinclude:: ../examples/container_util.py

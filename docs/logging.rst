Logging
~~~~~~~

The ``absio`` library uses the `logging` module from the Python standard library.  It can be
controlled via normal methods::

    import logging
    log = logging.getLogger('absio')
    log.setLevel(logging.DEBUG)

When debug is enabled, it is possible that sensitive information may leak into your logging
sub-system.

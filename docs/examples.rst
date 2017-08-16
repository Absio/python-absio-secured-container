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
should be shared::

    import absio
    import argparse
    import os

    def parse_ars():
        parser = argparse.ArgumentParser()
        parser.add_argument('api_key')
        parser.add_argument('--recipient')
        parser.add_argument('--file')
        args = parser.parse_args()
        return args

    def main():
        args = parse_args()
        absio.initialize(api_key=parser.api_key)

        if not os.path.exists(parser.file):
            raise OSError('Specified file does not exist.')

        # Let's include the file info in what we send to the recipient.
        header = {'stat': os.stat(parser.file)}
        content = open(parser.file, 'rb').read()
        access = [parser.recipient]

        absio.container.create(
            header=header,
            content=content,
            access=access
        )

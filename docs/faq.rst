FAQ
~~~

#. How do I install this on Windows?

   You will need to install the Microsoft Visual C++ Build Tools before the
   ``pip install absio`` will compile the dependencies correctly.

   .. _force_refresh_example:

#. What are events?  Why should I care?  How do I use them?

   Events allow you to receive notification of new content, either from other users
   or from account activity on another system.  They're an easy way for your account
   to remain in sync.  This snippet is an example of how you could stay up to date::

        start = 0  # The value of your last synchronization
        with absio.providers.provider(server_cache_ofs, force_refresh=True):
            for event in absio.container.get_events(starting_event_id=start):
                if event.action == 'deleted':
                    absio.container.delete(event.container_id)
                elif event.action in ['added', 'updated']:
                    # By setting the 'force_refresh' option, this forces the new data into the cache.
                    absio.container.get(event.container_id)
            start = event.id  # Save this so we can pick up where we left off next time.

#. I cannot import the library!  There's an error about 'Bad Magic Number'!  What gives?

   We only ship the pre-compiled Python byte-code.  Unfortunately this means that it can only be
   used by the exact same version of Python that we compiled with.  This normally applies to the
   major and minor numbers (e.g. Python 3.5) and there has been an unwritten rule that Python will
   not change the byte-code when performing a micro number release.  Unfortunately a bug in Python
   (https://bugs.python.org/issue29514) broke this rule.  Therefore this library will only work in
   Python 3.5.4+.

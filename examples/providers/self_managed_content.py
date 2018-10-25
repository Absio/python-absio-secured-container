"""An example provider demonstrating managing yourself the storage of encrypted content.

The Absio Broker™ application and OFS are utilized to store users, keys, events, etc, but
the actual encrypted content is not stored in other of those locations.  Instead, this provider
allows you to handle the data storage yourself.
"""
from types import SimpleNamespace
from absio.providers import server_cache_ofs


class ContainerProvider(object):

    def get(self, container_id, data, *args, **kwargs):
        # This will return a container that's as populated as it can be.
        container = server_cache_ofs.container.get(container_id)
        assert container.encrypted

        container.data = data

        if container.data and container.container_keys:
            container.decrypt()

        return container

    def update_or_create(self, container, **kwargs):
        assert container.encrypted
        # Save the container data so that it is not stored on the server / ofs
        data = container.data
        container.data = None

        # Now that we've stored the data, we can store it in the provider.
        container = server_cache_ofs.container.update_or_create(container, **kwargs)

        # Finally, restore the data so it's transparent to the caller.
        container.data = data
        return container

    def delete(self, container_id):
        # This will delete the container keys & access info from the server and ofs.
        server_cache_ofs.container.delete(container_id)


class SelfManagedContentProvider(object):
    def __init__(self):
        self.session = SimpleNamespace(user=None)
        # We use the default behavior of the default provider...
        self.keys = server_cache_ofs.keys
        self.key_file = server_cache_ofs.key_file
        self.events = server_cache_ofs.events
        self.users = server_cache_ofs.users
        # ...for everything except for containers, at which point our custom behavior takes over.
        self.containers = ContainerProvider()

    def initialize(self, *args, **kwargs):
        server_cache_ofs.initialize(*args, **kwargs)

    def login(self, *args, **kwargs):
        user = server_cache_ofs.login(*args, **kwargs)
        self.session.user = user
        return user

    def logout(self, *args, **kwargs):
        server_cache_ofs.logout(*args, **kwargs)
        self.session.user = None


self_managed = SelfManagedContentProvider()

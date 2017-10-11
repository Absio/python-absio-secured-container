#!/usr/bin/env python
"""A sample application involving containers.

You may create, update, and delete containers.
"""
import arrow
import absio
import click
import json
import pprint
import sys
import uuid
from copy import deepcopy
from functools import partial, reduce

APP_NAME = 'python-absio-container-cli'

error = partial(click.secho, fg='red')
warn = partial(click.secho, fg='yellow')
info = partial(click.secho, fg='white')
success = partial(click.secho, fg='green')

container_attrs = [
    'access',
    'content',
    'created_at',
    'created_by',
    'encrypted',
    'header.data',
    'id',
    'modified_at',
    'modified_by',
    'type',
]


access_perms = [
    'access.view',
    'access.modify',
    'container.download',
    'container.decrypt',
    'container.upload',
    'container.type.view',
    'container.type.modify',
]


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


sentinel = object()


def rgetattr(obj, attr, default=sentinel):
    if default is sentinel:
        _getattr = getattr
    else:
        def _getattr(obj, name):
            return getattr(obj, name, default)
    return reduce(_getattr, [obj] + attr.split('.'))


def getchar():
    """A wrapper for click's getchar function.

    This is due to: https://github.com/pallets/click/issues/822
    """
    c = click.getchar().lower()
    if isinstance(c, bytes):
        enc = getattr(sys.stdin, 'encoding', 'cp1252')
        c = c.decode(enc, 'replace')
    return c


def _set_value(name, current):
    click.clear()
    warn('Set Container {}\n'.format(name.capitalize()))
    info('Current: {}\n'.format(current))
    value = click.prompt('New {}'.format(name.lower()))
    return value


def _pprint_access(access, title='Access', menunum=None):
    if menunum:
        click.echo(click.style('  {}.  '.format(menunum), fg='blue', bold=True) + click.style(title, fg='green'), nl=False)
    else:
        click.echo(click.style(title, fg='green'), nl=False)

    if access is None:
        info(' (None)')

    elif isinstance(access, dict):
        info('')
        for user_id, val in access.items():
            click.echo(click.style('       User ID', fg='green') + ': {}'.format(user_id))
            click.echo(click.style('          Expiration', fg='green') + ': {}'.format(val.expiration))
            click.echo(click.style('          Permissions', fg='green') + ': {}'.format(val.permissions))

    elif isinstance(access, list):
        info('')
        for user_id in access:
            click.echo(click.style('       User ID', fg='green') + ': {}'.format(user_id))


def menu(num, opt):
    click.echo(click.style('  {}'.format(num), fg='blue', bold=True) + '.  {}'.format(opt))


def _container_attr_menu(attrs):
    info('\nItem:\n')
    click.echo(click.style('  1.  ', fg='blue', bold=True) + click.style('Header', fg='green') + ' ({})'.format(attrs['header']))
    content = attrs['content']
    if content is not None:
        content = (content[:30] + b'...') if len(content) > 33 else content
    click.echo(click.style('  2.  ', fg='blue', bold=True) + click.style('Content', fg='green') + ' ({})'.format(content))
    click.echo(click.style('  3.  ', fg='blue', bold=True) + click.style('Type', fg='green') + ' ({})'.format(attrs['type']))
    _pprint_access(attrs['access'], title='Access', menunum=4)


def _set_container_content(existing):
    while True:
        click.clear()
        warn('Set container content:\n')
        if existing is not None:
            data = (existing[:30] + b'...') if len(existing) > 33 else existing
        else:
            data = None
        click.echo(click.style('Current Content', fg='green') + ': ({})\n'.format(data))
        menu(1, 'Raw Input.')
        menu(2, 'From File.')
        menu('D', 'Done.\n')
        c = getchar()
        if c == 'd':
            return existing
        if c == '1':
            value = click.prompt('Enter container data')
            return value.encode('utf-8')
        if c == '2':
            fp = click.prompt('Enter file to load', type=click.File('rb'))
            return fp.read()


def _set_container_access(existing):
    while True:
        click.clear()
        warn('Set container access:\n')
        _pprint_access(existing, title='Current Access')
        menu('\n  1', 'Default access.')
        menu(2, 'By user ID(s).')
        menu(3, 'Advanced setting.')
        menu('\n  D', 'Done.')
        c = getchar()
        if c == '1':
            return
        elif c == '2':
            while True:
                value = click.prompt('Enter comma seperated User IDs')
                # Verify that we have a list of UUIDs
                try:
                    return [str(uuid.UUID(val.strip())) for val in value.split(',')]
                except:
                    error('Value must be comma seperated UUID strings.')
        elif c == '3':
            return _set_advanced_container_access(existing)
        elif c == 'd':
            return


def _set_individual_access(user_id, existing=None):
    if existing is None:
        existing = dict(expiration=None, permissions=None)
    else:
        existing = dict(expiration=existing.expiration, permissions=existing.permissions)

    while True:
        click.clear()
        warn('Setting individual user access for {}:\n'.format(user_id))
        info('  1. Expiration ({})'.format(existing['expiration']))
        info('  2. Permissions ({})'.format(existing['permissions']))
        info('  D. Done')
        c = getchar()
        if c == '1':
            while True:
                value = click.prompt('Expiration', default='')
                if value == '':
                    existing['expiration'] = None
                    break
                try:
                    existing['expiration'] = arrow.get(value).datetime
                except:
                    error('Unable to convert to time, try again.')
                else:
                    break
        elif c == '2':
            existing['permissions'] = _set_permissions(user_id)
        elif c == 'd':
            break
    # Now that the user is finished fine tuning the params, we can construct an access obj.
    access = absio.access.Access(user_id=user_id, expiration=existing['expiration'], permissions=existing['permissions'])
    return access


def _set_advanced_container_access(existing):
    if isinstance(existing, dict):
        access = existing
    else:
        # If existing access isn't a dict, that means it's either None (default) or a list.  Neither
        # of which matter when configuring advanced access.
        access = dict()

    while True:
        click.clear()
        warn('Setting advanced access:\n')
        _pprint_access(existing, title='Current Access')
        info('\n  1. Add User')
        info('  2. Edit User')
        info('  3. Remove User')
        info('  D. Done\n')
        c = getchar()
        if c == '1':
            user_id = str(click.prompt('Enter User ID', type=uuid.UUID))
            access[user_id] = _set_individual_access(user_id)
        elif c == '2':
            user_id = None
            while user_id not in access:
                user_id = click.prompt('Enter User ID', type=uuid.UUID)
            access[user_id] = _set_individual_access(user_id, access[user_id])
        elif c == '3':
            user_id = None
            while user_id not in access:
                user_id = click.prompt('Enter User ID', type=uuid.UUID)
            access.pop(user_id)
        elif c == 'd':
            break
    return access


def _set_permissions(user_id):
    click.clear()
    warn('Setting permissions for {}\n'.format(user_id))
    p = absio.permissions.Permissions()
    for perm in access_perms:
        if not click.confirm('  ' + perm, default=True):
            rsetattr(p, perm, False)
    return p


def create():
    # Where we'll store the currently selected info prior to creation.
    attrs = {
        'header': None,
        'content': None,
        'type': None,
        'access': None,
    }

    while True:
        click.clear()
        warn('Create a container.')
        _container_attr_menu(attrs)
        menu('\n  C', 'Create it')
        menu('M', 'Main menu\n')
        c = getchar()
        if c == 'm':
            break
        elif c == '1':
            attrs['header'] = _set_value('header', attrs['header'])
        elif c == '2':
            attrs['content'] = _set_container_content(attrs['content'])
        elif c == '3':
            attrs['type'] = _set_value('Type', attrs['type'])
        elif c == '4':
            attrs['access'] = _set_container_access(attrs['access'])

        elif c == 'c':
            # Allow string input of the JSON header ...
            try:
                header = json.loads(attrs['header'])
            except:
                header = attrs['header']

            kwargs = {
                'header': header,
                'content': attrs['content'],
                'type': attrs['type'],
                'access': attrs['access'],
            }
            container = absio.container.create(**kwargs)
            success('\nCreated ' + str(container) + '\n')
            click.pause()
            break


def read():
    click.clear()
    warn('Read a container.\n')
    container_id = click.prompt('Container ID', type=uuid.UUID)
    try:
        container = absio.container.get(container_id)
    except Exception as e:
        error('Unable to get container: {}'.format(e))
        if click.confirm('Would you like to try again?'):
            read()
        main_menu()
    success('\n' + str(container) + '\n')
    for attr in container_attrs:
        if attr == 'access':
            click.echo(click.style('{:>12}'.format(attr), fg='green') + ':')
            click.echo('{:>16}'.format(pprint.pformat(getattr(container, attr))))
        elif attr == 'content':
            content = container.content.data
            if content is not None and len(content) > 33:
                content = content[:30] + b'...'
            click.echo(click.style('{:>12}'.format(attr), fg='green') + ': ' + str(content))
        else:
            click.echo(click.style('{:>12}'.format(attr), fg='green') + ': ' + str(rgetattr(container, attr)))
    info('')
    click.pause()


def update():
    click.clear()
    warn('Update a container.\n')
    container_id = click.prompt('Container ID', type=uuid.UUID)
    try:
        container = absio.container.get(container_id)
    except Exception as e:
        error('Unable to get container: {}'.format(e))
        if click.confirm('Would you like to try again?'):
            update()
        main_menu()

    attrs = {
        'header': container.header.data,
        'content': container.content.data,
        'type': container.type,
        'access': deepcopy(container.access),
    }
    while True:
        click.clear()
        warn('Updating container {}'.format(container.id))
        _container_attr_menu(attrs)
        info('\n  U. Update it')
        info('  M. Main menu\n')
        c = getchar()
        if c == 'm':
            break
        if c == '1':
            attrs['header'] = _set_value('header', attrs['header'])
        elif c == '2':
            attrs['content'] = _set_container_content(attrs['content'])
        elif c == '3':
            attrs['type'] = _set_value('type', attrs['type'])
        elif c == '4':
            attrs['access'] = _set_container_access(attrs['access'])

        elif c == 'u':
            try:
                header = json.loads(attrs['header'])
            except:
                header = attrs['header']

            kwargs = dict()
            if header != container.header.data:
                kwargs['header'] = header
            if attrs['content'] != container.content.data:
                kwargs['content'] = attrs['content']
            if attrs['type'] != container.type:
                kwargs['type'] = attrs['type']
            if attrs['access'] != container.access:
                kwargs['access'] = attrs['access']
            absio.container.update(container.id, **kwargs)
            success('Container {} has been updated.'.format(container.id))
            click.pause()
            break


def delete():
    click.clear()
    warn('Delete a container.\n')
    container_id = click.prompt('Container ID', type=uuid.UUID)
    if click.confirm('\nAre you sure you would like to delete container {}?'.format(container_id)):
        try:
            absio.container.delete(container_id)
        except Exception as e:
            error('Unable to delete container: {}'.format(e))
            if click.confirm('\nWould you like to try again?'):
                delete()
            main_menu()
    else:
        main_menu()
    success('\nContainer {} has been deleted.\n'.format(container_id))
    click.pause()


def events():
    click.clear()
    warn('All container events.\n')
    events = absio.container.get_events()
    click.echo_via_pager('\n'.join((str(e) for e in events)))


def exit():
    click.clear()
    sys.exit()


def main_menu():
    click.clear()
    warn('Welcome to the Absio Container CRUD Sample App.\n')
    info('Choose your option:\n')
    menu('C', 'Create')
    menu('R', 'Read')
    menu('U', 'Update')
    menu('D', 'Delete\n')
    menu('L', 'List Events')
    menu('Q', 'Quit')
    cmd = getchar()
    dispatch = {
        'c': create,
        'r': read,
        'u': update,
        'd': delete,
        'l': events,
        'q': exit,
    }
    dispatch.get(cmd, main_menu)()


@click.command()
@click.option('--api-key', required=True)
@click.option('--url', default='https://sandbox.absio.com')
@click.option('--user-id', required=True)
@click.option('--password', required=True)
@click.option('--backup-phrase', required=True)
def main(api_key, url, user_id, password, backup_phrase):

    absio.initialize(api_key=api_key, server_url=url, app_name=APP_NAME)
    # Try logging in to the OFS before falling back to the server.
    try:
        absio.login(user_id, password)
    except:
        absio.login(user_id, password, backup_phrase)

    while True:
        try:
            main_menu()
        except Exception as e:
            error('Unexpected error: {}\n'.format(e))
            click.pause()


if __name__ == '__main__':
    main()

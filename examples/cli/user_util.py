#!/usr/bin/env python
"""A sample application involving users.

You may create and delete users.  Additionally you may manage user's authentication and backup
credentials.
"""
import click
import absio
import logging
import sys
from functools import partial

APP_NAME = 'python-absio-user-cli'

error = partial(click.secho, fg='red')
warn = partial(click.secho, fg='yellow')
info = partial(click.secho, fg='white')
success = partial(click.secho, fg='green')


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    # If debug is enabled, redirect the absio logging to the console.
    if debug:
        logger = logging.getLogger('absio')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)


# A common set of options used for server specification.
server_options = (
    click.option('--api-key', required=True),
    click.option('--url', default='https://sandbox.absio.com'),
)

# Options used to log a specific account into the server.
login_options = (
    click.option('--user-id', required=True),
    click.option('--password', required=True),
    click.option('--backup-phrase', required=True),
)


def apply_options(*options):
    def g(f):
        for option in reversed(options):
            f = option(f)

        return f

    return g


@cli.command()
@apply_options(*server_options)
@click.option('--password', required=True)
@click.option('--reminder', required=True)
@click.option('--backup-phrase', required=True)
def create(api_key, url, password, reminder, backup_phrase):
    """Registers a new user."""
    info('Creating user.')
    absio.initialize(api_key, app_name=APP_NAME, server_url=url)
    try:
        user = absio.user.create(password=password, reminder=reminder, passphrase=backup_phrase)
    except Exception as e:
        error('Failed to create user: {e}'.format(e=e))
        sys.exit(1)
    success('User created: {user}'.format(user=user))


@cli.command()
@apply_options(*(server_options + login_options))
def delete(api_key, url, user_id, password, backup_phrase):
    """Permanently removes a user."""
    info('Deleting user.')
    absio.initialize(api_key, app_name=APP_NAME, server_url=url)
    try:
        absio.login(user_id, password=password, passphrase=backup_phrase)
        absio.user.delete()
    except Exception as e:
        error('Failed to delete user: {e}'.format(e=e))
        sys.exit(1)
    success('Deleted user: {id}'.format(id=user_id))


def _login(api_key, url, user_id, password, backup_phrase):
    info('Logging in.')
    absio.initialize(api_key, app_name=APP_NAME, server_url=url)
    try:
        user = absio.login(user_id, password=password, passphrase=backup_phrase)
    except Exception as e:
        error('Failed to login user: {e}'.format(e=e))
        sys.exit(1)
    success('Successfully logged in user: {user}'.format(user=user))


@cli.command()
@apply_options(*(server_options + login_options))
def login(api_key, url, user_id, password, backup_phrase):
    """Verifies credentials by logging in."""
    _login(api_key, url, user_id, password, backup_phrase)


@cli.command()
@apply_options(*server_options)
@click.option('--user-id', required=True)
def getreminder(api_key, url, user_id):
    """Returns the publicly accessible reminder for the user's backup passphrase."""
    info('Fetching reminder information.')
    absio.initialize(api_key, app_name=APP_NAME, server_url=url)
    try:
        reminder = absio.user.get_backup_reminder(user_id)
    except Exception as e:
        error('Failed to fetch reminder information: {e}'.format(e=e))
        sys.exit(1)
    success('Reminder information: {reminder}'.format(reminder=reminder))


@cli.command()
@apply_options(*(server_options + login_options))
@click.option('--new-password', required=True)
@click.option('--new-backup-phrase', required=True)
@click.option('--new-reminder', required=False)
def change_credentials(api_key, url, user_id, password, backup_phrase, new_password, new_backup_phrase, new_reminder):
    """Changes a user's backup phrase and reminder."""
    info('Changing backup passphrase and reminder.')
    _login(api_key, url, user_id, password, backup_phrase)
    try:
        absio.user.change_credentials(
            password=new_password,
            passphrase=new_backup_phrase,
            reminder=new_reminder,
        )
    except Exception as e:
        error('Failed to change backup credentials: {e}'.format(e=e))
        sys.exit(1)
    success('Successfully changed backup passphrase to {p}'.format(p=new_backup_phrase))
    success('Successfully changed backup reminder to {r}'.format(r=new_reminder))


if __name__ == '__main__':
    cli()

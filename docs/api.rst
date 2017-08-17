API
***


General
=======

Python Absio Library <http://absio.readthedocs.io/>

absio.initialize(api_key, app_name=None, server_url='https://sandbox.absio.com')

   This method must be called first to initialize the module.

   See the section about Obtaining an API Key for more information
   about the api_key argument.

   Parameters:
      * **api_key** (*A UUID** or **string.*) – The API key that you
        have received from Absio.

      * **app_name** – Name used by the Absio API Server Application
        to identify different applications.

      * **server_url** (*string*) – The URL of the Absio API Server
        Application that you intend to use.  The "api_key" that you
        have been issued must have come from that server instance.

absio.login(user_id, password, passphrase=None)

   Logs in a User.

   Parameters:
      * **user_id** (*A UUID** or **a string.*) – The identifier of
        the user to login with.

      * **password** (*string*) – The user’s password, used to
        decrypt their key file.

      * **passphrase** (*string*) – If the user’s key file is not
        local but is stored on the Absio API Server Application, the
        passphrase must be provided so that it may be retrieved.

   Returns:
      The logged in "User".

   Return type:
      "User"

absio.logout()

   Clears any user data cached in memory.

   The user will no longer be authenticated with the Absio API Server
   Application.

absio.is_password_valid(password)

   Validates that a password meets the complexity requirements.

   By default, the password must be at least 8 characters long and
   include at least 1 character from 3 of the following types of
   characters:

      * Lower case

      * Upper case

      * Number

      * Special

   You may override this validator globally by replacing this function
   with your own, or you may pass your validator function as an
   argument to the functions that allow for credential updates.

   Parameters:
      **password** (*string*) – The password to be validated.

   Returns:
      If the password is valid.

   Return type:
      bool

absio.is_passphrase_valid(passphrase)

   Validates that a passphrase meets the complexity requirements.

   By default, the passphrase must be at least 8 characters long and
   include at least 1 character from 3 of the following types of
   characters:

      * Lower case

      * Upper case

      * Number

      * Special

   You may override this validator globally by replacing this function
   with your own, or you may pass your validator function as an
   argument to the functions that allow for credential updates.

   Parameters:
      **passphrase** (*string*) – The passphrase to be validated.

   Returns:
      If the passphrase is valid.

   Return type:
      bool

absio.is_reminder_valid(reminder)

   Validates that the reminder meets the complexity requirements.

   Absio does not enforce any complexity upon the reminder, therefore
   this implementation just returns True.  It can however be
   overridden to enforce your requirements.

   You may override this validator globally by replacing this function
   with your own, or you may pass your validator function as an
   argument to the functions that allow for credential updates.

   Returns:
      If the reminder is valid.

   Return type:
      bool


Container
=========

Containers are the method by which data is passed between users
securely.

Crucial to utilizing a container is understanding ‘access’.  This
specifies details such as with whom the container should be shared,
what access and permissions are enabled, if the access should be
revoked at a particular time, etc.

Containers have headers and content.  Headers are intended to include
metadata information.  They could contain client-enforceable controls
such as “is this recipient allowed to print” or identifiers that help
tie the content back to something your system understands.  The only
restriction is that the header must be JSON serializable, otherwise
the sky is the limit as to what can be placed into the header.

The content is assumed to be a file body.  However, it too could be
more JSON, or XML, or any other type of data.  The content is intended
to be just that - the data.

Other metadata exists for containers that is not wrapped up and
protected by encryption.  This information includes the date the
container was created, when it was modified, the ‘type’, and the
length of the container.

absio.container.create(content, access=None, header=None, type_=None)

   Creates a "Container".

   The container will be uploaded to the Absio API Server Application
   and access will be granted to the specified users.  If local
   storage is being utilized, the container and associated access will
   also be stored in the OFS.

   The container will never expire for the creator.  The creator is
   automatically granted full permissions to the container, unless a
   limited permission is defined in the "access" kwarg.

   Parameters:
      * **content** (*bytes*) – The data to be stored in a
        container.

      * **access** (*dict**, **list*) – Details about with whom the
        container is shared and what permissions they have. If not
        provided, the container will only be accessible to the
        creator.  If "access" is a dict, the keys need to be user IDs
        and the values are "Access" instances for that user. Finally,
        "access" can be provided as a list of user IDs.  Default
        access will be granted for each user ID.  If "access" is
        specified, then the creator must explicitly be included if
        they should have access.

      * **header** (*JSON serializable data*) – Optionally,
        containers may also contain headers.

      * **type** (*string*) – An optional clear bit of metadata that
        might help explain what type of data has been wrapped up into
        the container.  This can be used to organize containers on the
        Absio API Server Application.

   Returns:
      The created "Container".

   Usage:

      # Create a container only accessible by yourself
      >>> container = create(content='asdf')
      <Container(d21ba58c-9e50-472a-9ce2-5a2595704e7a) Encrypted: True>

      # Share with default permissions and access settings to multiple users
      >>> users = ['1d4c568b-e762-4284-b14e-167cc4776026', '0e28abdc-1a8f-43db-b565-088161af2b53']
      >>> container = create(content='asdf', access=users)
      <Container(d21ba58c-9e50-472a-9ce2-5a2595704e7a) Encrypted: True>

      # Selectively fine-tune the access information
      >>> expiring_access = Access(user_id='1d4c568b-e762-4284-b14e-167cc4776026', expiration=utcnow())
      >>> permission = Permission()
      >>> permission.container.download = False
      >>> limited_access = Access(user_id='0e28abdc-1a8f-43db-b565-088161af2b53', permission=permission)
      >>> accesses = [expiring_access, limited_access]
      >>> container = create(content='asdf', access={access.id: access for access in accesses})
      <Container(d21ba58c-9e50-472a-9ce2-5a2595704e7a) Encrypted: True>

absio.container.delete(container_id)

   This revokes the authenticated user’s access to the container.

   If local storage is being utilized, the container and the
   associated access will be removed from the OFS.  If the
   authenticated user is the only user with access, then the content
   will be deleted from the Absio API Server Application.

   Parameters:
      **container_id** (*UUID*) – The ID of the container to delete.

   Note: If you want the container itself to be deleted, you must
     first remove all other user’s access to it and then call this
     function. This will result in no other users having access and
     the content then being removed locally and on the Absio API
     Server Application.

absio.container.get(container_id, include_content=True)

   Retrieves a container and decrypts it for use.

   If local storage is being utilized, the library will first check
   the OFS.  If not using local storage or the container is not found,
   the latest version will be downloaded from the Absio API Server
   Application.  By default, the content is included (downloaded and
   decrypted).

   Parameters:
      * **container_id** (*UUID*) – The ID of the container to
        fetch.

      * **include_content** (*bool*) – Set to "False" to prevent
        downloading and decrypting content.  This is helpful when the
        content is very large.

absio.container.get_events(container_type=None, container_id=None, action=None, starting_event_id=None)

   Gets all new container events since the last call to this method.

   If any of the arguments are provided, then they change the criteria
   used to query and filter results.  These events are retrieved from
   the Absio API Server Application.

   Parameters:
      * **container_type** (*string*) – Only events of the specified
        container type will be returned.  Type is a string used to
        categorize containers on the Absio API Server Application.

      * **container_id** (*UUID*) – Filter the results to only
        include events related to the specified container ID.

      * **action** ("EventAction") – Filters the results to only
        include events that have the specified action.

      * **starting_event_id** (*int*) – 0 will start from the
        beginning and download all events for the current user with
        the specified criteria.  Use the event_id field from a
        container event to start from a known event.  If omitted, the
        newest events since the last call will be downloaded.

   Returns:
      All of the events that match the filter criteria.

   Return type:
      "list" of "Events"

absio.container.update(container_id, **kwargs)

   Updates a container with the specified ID.

   At least one of the optional kwargs must be provided for an update
   to occur.  This will update the container and access information on
   the Absio API Server Application as well as in the OFS.

   Parameters:
      * **container_id** (*UUID*) – The ID of the container to
        update.

      * **access** (*dict*) – The access granted to the container.
        If not specified, the currently defined access will be left
        unchanged.

      * **content** (*bytes*) – New content to be encrypted.

      * **header** (*JSON serializable data*) – A new header to be
        applied.

      * **type** (*string*) – A new string to categorize the
        container on the Absio API Server Application.

class absio.crypto.container.Access(user_id, permissions=None, expiration=None, key=None)

   Used to define a user’s access to a container.

   The "Access" object is used by the container "create()",
   "update()", and "get()" methods to define a user’s access to a
   container.  The access information includes specific permissions
   and an optional expiration.

   key_blob

      The unique keys required to decrypt the container, for this
      particular access.

class absio.crypto.container.Container(data=None, content_cls=<class 'absio.crypto.container.RawPayload'>, **kwargs)

   Creates an Intelligent Data Object (Container).

   Parameters:
      * **data** (*bytes*) – If "data" is provided, this represents
        a container in its entirety and is therefore considered to be
        an encrypted container.

      * **content_cls** ("RawPayload") – This allows for determing
        what type of content payload is constructed. Some types of
        containers use a JSON payload, while others use bytes. By
        changing the constructor type, the data can automatically be
        translated into the format you desire.

      * **container_id** (*UUID*) – This is an optional kwarg used
        to construct an unencrypted Container.

      * **header** (*JSON serializable unencrypted data*) – An
        unencrypted payload for the header portion of a container.

      * **content** (*Unencrypted data*) – The unencrypted payload
        for the content portion of a container.

      * **type"** (*string*) – Allows for organization of containers
        on the Absio API Server Application.

   container_keys = None

      The "ContainerKeys" that were used to encrypt the container, if
      encrypted.

   content = None

      The container content

   data

      The data of a container.

   decrypt(container_keys=None)

      Decrypts a Container.

      Parameters:
         **container_keys** ("ContainerKeys") – An optional parameter,
         the container_keys that came from decrypting the recipient
         key bob (RKB).  If not provided, and the Container keys were
         stored as part of the encryption process, those stored keys
         will be used.

   encrypt(container_keys=None)

      Encrypts a Container.

      Parameters:
         **container_keys** ("ContainerKeys") – If keys are provided,
         they will be used to do the encryption, otherwise a new set
         will be created.

      Returns:
         "ContainerKeys"

   encrypted

      A property that returns a boolean indicating whether or not the
      container is encrypted.

   header = None

      The container header.

   id = None

      The UUID of the container.

   type = None

      The container’s type.

class absio.crypto.container.ContainerKeys(cipher_index=0, mac_index=0, cipher_key=None, mac_key=None)

   cipher_index

   cipher_key

   mac_index

   mac_key

   to_bytes()

class absio.crypto.container.JSONPayload(enc_data=None, ptxt_data=None)

   Assumes that the payload type is JSON.

   Converts the data to/from JSON as it is accessed.

   data

   encrypt(container_keys)

class absio.crypto.container.Permissions(value=127)

class absio.crypto.container.RawPayload(enc_data=None, ptxt_data=None)

   One of the two portions of an Container.

   Makes no assumptions about the type of data being stored.

   data

   decrypt(container_keys)

   encrypt(container_keys)

   encrypted

   set_encrypted_data(ciphertext)


Event
=====

class absio.event.Event(action, id, changes, client_app_name, container_expired_at, container_id, container_modified_at, container_type, date, related_user_id, type)

   Notification that something has happened.

   The Absio API Server Application tracks all container and key file
   actions (accessed, added, updated, and deleted).  This information
   may help you become aware of new containers, or receive updates
   from other users.

   action

      Always one of "accessed", "added", "deleted", or "updated".

   id

      An integer value for this event.  Event IDs are constantly
      increasing.

   changes

      Information about what has changed.  For example: "{'field that
      changed': 'updated value'}"

   client_app_name

      The name of the application responsible for the action.  This
      may or may not exist, depending on the settings configured in
      the responsible application.

   container_expired_at

      A "datetime" object if the container has expired, "None"
      otherwise.

   container_id

      The container ID ("UUID") that this event relates to, if type is
      "container".

   container_modified_at

      A "datetime" object corresponding to when the container content
      was last modified.  It does not change when updating the access,
      header, or type of a container and will be "None" in those
      cases.

   container_type

      The container type as specified upon creation or last update.

   date

      A "datetime" object corresponding to when the event occurred.

   related_user_id

      If this event relates or was triggered by another user, this
      field will be set to that user’s ID ("UUID").

   type

      The event type, always one of "container" or "key_file".


User
====

Handles Absio User Accounts.

class absio.user.User(id, key_file)

   An Absio User.

   id = None

      The user’s ID value (UUID)

   keys = None

      The user’s key ring.  Contains both signing and derivation keys.
      If this user is one that has been logged in, this key ring will
      contain the private keys.  Otherwise it will only have the
      public keys.

absio.user.change_backup_credentials(user_id, current_passphrase, new_reminder, new_passphrase, current_password=None, reminder_validator=<function is_reminder_valid>, passphrase_validator=<function is_passphrase_valid>)

   Changes the backup credentials (reminder and passphrase) for the
   account.

   Use a secure value for the passphrase as it can be used to reset
   the user’s password.  This operation causes the key file to be re-
   encrypted.  The new copy of the key file will be pushed to the
   Absio API Server Application.  If local storage is being utilized,
   it will also be saved in the OFS.

   Parameters:
      * **user_id** (*UUID*) – The identifier of the user.

      * **current_passphrase** (*string*) – The current passphrase
        set up during creation of the account.

      * **current_password** (*string*) – If provided, the password
        will be validated to make sure the caller is in possession of
        both sets of credentials (passphrase and password), not just
        the passphrase.

      * **new_reminder** (*string*) – The new backup reminder for
        the user’s passphrase.  The reminder is publicly available in
        plain text.  Do not include sensitive information or wording
        that allows the passphrase to be easily compromised.

      * **new_passphrase** (*string*) – The new backup passphrase
        for the user.  Use a secure value for this. This can be used
        to reset the password for the user’s account.

      * **reminder_validator** (*callable*) – An optional validator
        to enforce passphrase complexity requirements. If provided, it
        should take a single argument (the passphrase) and return a
        boolean indicating whether or not the passphrase passes
        validation.

      * **passphrase_validator** (*callable*) – An optional
        validator to enforce passphrase complexity requirements.  If
        provided, it should take a single argument (the passphrase)
        and return a boolean indicating whether or not the passphrase
        passes validation.

absio.user.change_password(user_id, passphrase, new_password, current_password=None, pass_validator=<function is_password_valid>)

   Changes a user’s password to the new value.

   If a user doesn’t remember their password but can recall their
   recovery passphrase, their password can be updated via this
   function.  You may call "get_backup_reminder()" to get the reminder
   for the passphrase.  This operation causes the Key File to be re-
   encrypted and stored on the Absio API server Application.  If local
   storage is being utilized, it will also be saved in the OFS.

   Parameters:
      * **user_id** (*UUID*) – The identifier of the user.

      * **passphrase** (*string*) – The passphrase that was setup
        during account creation.

      * **new_password** (*string*) – The new password for the user.
        It cannot be the same as the existing password.

      * **current_password** (*string*) – If provided, the password
        will be validated to make sure the caller is in possession of
        both sets of credentials (passphrase and password), not just
        the passphrase.

      * **pass_validator** (*callable*) – An optional validator to
        enforce password complexity requirements.  If provided, it
        should take a single argument (the password) and return a
        boolean indicating whether or not the password passes
        validation.

absio.user.create(password, reminder, passphrase, pass_validator=<function is_passphrase_valid>, reminder_validator=<function is_reminder_valid>)

   Creates a new user, registering them on the Absio API Server
   Application

   Generates private keys and registers a new user on the Absio API
   Server Application. The user’s private keys are encrypted with the
   password to product a Key File.  The passphrase is used to reset
   the password and download the Key File from the Absio API Server
   Application.  If local storage is utilized, the Key File is also
   saved in the Obfuscating File System.

   Parameters:
      * **password** (*string*) – Used to encrypt the key file.

      * **reminder** (*string*) – Used to prompt the user to
        remember their passphrase if trying to retrieve their key file
        from the Absio API Server Application.

      * **passphrase** (*string*) – Allows the user to reset the
        password and download their key file.

      * **reminder_validator** (*callable*) – An optional validator
        to enforce passphrase complexity requirements. If provided, it
        should take a single argument (the passphrase) and return a
        boolean indicating whether or not the passphrase passes
        validation.

      * **pass_validator** (*callable*) – An optional validator to
        enforce password complexity requirements.  If provided, it
        should take a single argument (the password) and return a
        boolean indicating whether or not the password passes
        validation.

   Returns:
      The newly created user.

   Return type:
      "User"

absio.user.delete(user)

   Removes a user permanently.

   Parameters:
      **user** ("User") – The user to be removed.

   Danger: This function cannot be undone.  All data associated with
     the user will be permanently deleted and cannot be recovered.
     Use with caution.

absio.user.get_backup_reminder(user_id=None)

   Gets the publicly accessible reminder for the user’s backup
   passphrase.

   Parameters:
      **user_id** (*UUID*) – The identifier of the user for whom the
      reminder should be retrieved.  If no value is provided, the ID
      of the currently authenticated user will be used.

   Returns:
      The publicaly accessible reminder for the user’s backup
      passphrase.

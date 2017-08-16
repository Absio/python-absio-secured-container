.. _tech: 

Absio Technology
================

Absio offers a set of tools that developers can use to protect application data
throughout its lifecycle—from creation to deletion, everywhere it
exists—without having to manage keys, add hardware, increase latency or rely on
a third-party service for access to data. Absio’s cross-platform, Serverless
Encryption technology automatically encrypts any type of unstructured data
object (file or stream) generated or processed by an application prior to being
stored or transmitted, each with its own unique key. Data content keys are
uniquely encrypted for each user given access to the data, allowing
user-specific access and permissions to be added or revoked at any time without
needing to re-encrypt the data object. All key generation and management is
performed automatically on the device running the application and not by a
central key server. Encrypted data objects and content keys can be stored
locally in an obfuscated file system to reduce network latency impacts and
enable local content to be decrypted and encrypted while offline. Absio
technology automatically obfuscates file names and types and randomizes the
folder structure, enabling keys and content to be stored locally without
putting data at risk.

In addition, developers can use Absio tools to associate classification, audit
history, policy and other metadata from any source, enabling software
applications to consume this information and 1) process and update metadata
without providing access to, or decrypting content, and/or 2) restrict who,
how, where, and for how long decrypted content can be used. For data sharing,
Absio technology provides an automated public key infrastructure, and a
portable (installable anywhere), extensible, zero-knowledge server application
for authentication, content/key exchange, sync, and backup.

Components
~~~~~~~~~~

The Absio developer toolset consists of cross platform-capable software
development kits (SDKs), each with a simple application programming interface
(API), and a portable server application (Absio API Server Application). The
Absio SDK is currently available in JavaScript (Browser and Node.js) and C#.
SDKs for Swift, Java and Python will be available late summer 2017. The Absio
Server Application is written in Python and can be deployed by the organization
via a Python package, RPM, VM or Docker container. All communication with the
Absio Server Application is handled by the SDK methods, so no separate API
calls are required.

Goals
~~~~~

Several goals were identified and met in the creation of Absio's developer
toolset:

- Simple API
- Flexible architecture
- Serverless Encryption
- Key generation and encryption at the application
- Automatic key generation and management
- Bound metadata - encrypted with content (See the header portion of an Absio
  Secured Container for more details)
- Associated metadata - stored in database and related to content (See the type field under the
  containers section for more details)
- Offline access (See Obfuscating File System)
- Strong, safe and verifiable encryption

Absio API Server Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Absio API Server Application is used for identity management in the Absio
ecosystem through usage and distribution of public keys.  Users are registered
through the SDK and their public keys are stored on the Absio API Server
Application, accessible to all other registered users.  Container access is
stored on the Absio API Server Application.

The Absio API Server Application tracks and distributes container-related
events when containers are:

- Accessed
- Created
- Deleted (access or content removed)
- Updated

Users
~~~~~

A User is an entity with a set of private keys and an identifier.  There are two main key types:
those used for signature verification, and those used for derivation.  The user's public keys are
registered with the Absio API Server Application and are made available to other Absio users.
These public keys allow for granting access to containers and validating user actions.

Users are able to create Absio Secured Containers that are each uniquely encrypted.  Optionally,
a user can share containers with other users and add unique permissions or lifespan controls.

Absio Secured Containers
~~~~~~~~~~~~~~~~~~~~~~~~

An Absio Secured Container (ASC) is the fundamental encrypted data structure in the Absio
ecosystem.

A container's header and content are part of the encrypted data.

- Header

  * The header is any information about the content that is private or sensitive (i.e. should be
    encrypted) or that needs to remain with the data, wherever it goes.
  * The header must be JSON serializable.
  * The header can be independently decrypted without downloading and/or decrypting the content.

- Content

  * The content is the data payload of a container.
  * While there are no limitations on the maximum size of a container, application performance and
    user experience may vary depending on platform limitations.


Key File
~~~~~~~~

An AES256 encrypted key file is created for each user, which contains the users private keys (both
signing and derivation) and password reset information.  The user's password is used to encrypt
the private keys.

A passphrase may also be provided and will allow a key file to be synchronized between devices as
well as enables a secure password reset method.  By default, the user key files are backed up on
the Absio API Server Application, but may optionally be stored locally in the Obfuscating File
System.


.. _ofs_tech:

Obfuscating File System
~~~~~~~~~~~~~~~~~~~~~~~

If the application using the ``absio`` library supports file storage, then the library can be used
for local storage.  The local storage acts as a cache allowing for offline access of data, as well
improved performance (no need to request the keys and content from the Absio API Server
Application).

Local storage is performed in the Obfuscating File System (OFS). The OFS creates random,
nonsensical paths within the root directory for all files. This serves to remove any identifiable
attributes (file name and associated content), ruining the economics of an attempt to target
specific files for brute-force decryption. Optionally, the content within the OFS can be
segregated by user ID.

Encryption
~~~~~~~~~~

A user's private keys are stored in an encrypted key file.  This key file is encrypted with AES256
using a key derived via PBKDF2 from the user's password.

Each Absio Secured Container has a unique set of secret keys.

- HMAC-SHA256 digests are used for content validation to mitigate content tampering.
- AES256 keys are used to individually encrypt the header and content.

These secret keys are uniquely encrypted for each user that can access the container.  This
encryption process uses Static-Ephemeral Diffie-Hellman Key Exchange (DHKE) based upon a user's
public derivation key.  This process ensures that the decryption of the container's secret keys
can only be accomplished using the user's corresponding private key.  Furthermore the container
keys are signed with the creator's private signing keys to help mitigate Main-in-the-Middle
attacks.

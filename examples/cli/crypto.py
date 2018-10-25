import absio
import click
from uuid import uuid4
from absio.crypto.keys import Key, KeyType, KeyRing


@click.group()
def cli():
    pass


@cli.group()
def aes():
    """Symmetric Cryptography."""


@aes.command()
@click.argument('output', type=click.File('wb'))
def create_key(output):
    output.write(absio.crypto.aes.create_key())


@aes.command()
@click.argument('output', type=click.File('wb'))
def create_iv(output):
    output.write(absio.crypto.aes.create_iv())


@aes.command()
@click.argument('key', type=click.File('rb'))
@click.argument('iv', type=click.File('rb'))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def encrypt(key, iv, input, output):
    key = key.read()
    iv = iv.read()
    plaintxt = input.read()
    ciphertxt = absio.crypto.aes.encrypt(plaintxt, key, iv)
    output.write(ciphertxt)


@aes.command()
@click.argument('key', type=click.File('rb'))
@click.argument('iv', type=click.File('rb'))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def decrypt(key, iv, input, output):
    key = key.read()
    iv = iv.read()
    ciphertxt = input.read()
    plaintxt = absio.crypto.aes.decrypt(ciphertxt, key, iv)
    output.write(plaintxt)


@cli.command()
@click.argument('data', type=click.File('rb'))
def hash(data):
    """Performs a SHA384 hash."""
    click.echo(absio.crypto.hash.get_hash(data.read()))


@cli.command()
@click.argument('private', type=click.File('wb'))
@click.argument('public', type=click.File('wb'))
def p384(private, public):
    """Creates an elliptic curve (P384) key pair."""
    private_key = absio.crypto.p384.generate_private_key()
    private_pem = absio.crypto.to_pem_private(private_key)
    public_pem = absio.crypto.to_pem_public(private_key.public_key())

    private.write(private_pem)
    public.write(public_pem)


@cli.group()
def ecdsa():
    """Elliptic Curve Signature Algorithm"""


@ecdsa.command()
@click.argument('key', type=click.File('rb'))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def sign(key, input, output):
    key = absio.crypto.p384.load_pem_private_key(key.read())
    data = input.read()
    output.write(absio.crypto.ecdsa.sign(key, data))


@ecdsa.command()
@click.argument('key', type=click.File('rb'))
@click.argument('data', type=click.File('rb'))
@click.argument('signature', type=click.File('rb'))
def verify(key, data, signature):
    key = absio.crypto.p384.load_pem_private_key(key.read())
    data = data.read()
    sig = signature.read()
    try:
        absio.crypto.ecdsa.verify(key.public_key(), data, sig)
    except absio.crypto.InvalidSignature:
        click.echo('Invalid')
        return 1


@cli.group()
def ies():
    """Absio Integrated Encryption Scheme"""

@ies.command()
@click.argument('ptxt', type=click.File('rb'))
@click.argument('sender_private_key', type=click.File('rb'))
@click.argument('recip_public_key', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def encrypt(ptxt, sender_private_key, recip_public_key, output):
    """Encrypts some data."""
    data = ptxt.read()

    sender_user_id = uuid4()
    sender_key_ring = KeyRing(user_id=sender_user_id, pub_keys=[])
    sender_key_ring[KeyType.AUTH][0] = Key(KeyType.AUTH, private=sender_private_key.read())
    sender_key_ring[KeyType.AUTH][0].index = 0
    sender_key_ring[KeyType.AUTH][0].user_id = sender_user_id

    recip_user_id = uuid4()
    recip_key_ring = KeyRing(user_id=recip_user_id, pub_keys=[])
    recip_key_ring[KeyType.DERIVATION][0] = Key(KeyType.DERIVATION, public=recip_public_key.read())
    recip_key_ring[KeyType.DERIVATION][0].index = 0
    recip_key_ring[KeyType.DERIVATION][0].user_id = recip_user_id

    container = absio.crypto.ies.encrypt(data, sender_key_ring, recip_key_ring)

    output.write(container)


@ies.command()
@click.argument('ciphertxt', type=click.File('rb'))
@click.argument('recip_private_key', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def decrypt(ciphertxt, recip_private_key, output):
    """Decrypts some data."""
    data = ciphertxt.read()

    recip_user_id = uuid4()
    recip_key_ring = KeyRing(user_id=recip_user_id, pub_keys=[])
    recip_key_ring[KeyType.DERIVATION][0] = Key(KeyType.DERIVATION, private=recip_private_key.read())
    recip_key_ring[KeyType.DERIVATION][0].index = 0
    recip_key_ring[KeyType.DERIVATION][0].user_id = recip_user_id

    ptxt = absio.crypto.ies.decrypt(data, recip_key_ring)

    output.write(ptxt)


@cli.command()
@click.argument('private', type=click.File('rb'))
@click.argument('public', type=click.File('rb'))
@click.argument('secret', type=click.File('wb'))
def ecdhe(private, public, secret):
    """Elliptic curve key exchange."""
    private = absio.crypto.p384.load_pem_private_key(private.read())
    public = absio.crypto.p384.load_pem_public_key(public.read())

    secret.write(absio.crypto.ecdhe.exchange(private, public))


@cli.command()
@click.argument('secret', type=click.File('rb'))
@click.option('--length', type=int, default=32)
@click.argument('output', type=click.File('wb'))
def kdf2(secret, length, output):
    """Key Derivation Function."""
    secret = secret.read()
    key = absio.crypto.KDF2(secret, length=length)
    output.write(key)


@cli.command()
@click.argument('password', type=click.File('rb'))
@click.option('--salt', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def pbkdf2(password, salt, output):
    """Password based key derivation function."""
    password = password.read()
    salt = salt.read() if salt else None
    key = absio.crypto.pbkdf2.create_key(password, salt=salt)
    output.write(key)


@cli.group()
def hmac():
    """HMAC"""


@hmac.command()
@click.argument('output', type=click.File('wb'))
def create_key(output):
    output.write(absio.crypto.hmac.generate_key())


@hmac.command()
@click.argument('key', type=click.File('rb'))
@click.argument('data', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def digest(key, data, output):
    key = key.read()
    data = data.read()

    output.write(absio.crypto.hmac.digest(key, data))


@hmac.command()
@click.argument('key', type=click.File('rb'))
@click.argument('data', type=click.File('rb'))
@click.argument('digest', type=click.File('rb'))
def verify(key, data, digest):
    key = key.read()
    data = data.read()
    digest = digest.read()

    absio.crypto.hmac.verify(key, data, digest)


if __name__ == '__main__':
    cli()

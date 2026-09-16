# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS2, AS4, EnvVariable
from zato.common.const import SECRETS
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.typing_ import any_, anydict, strnone, strtuple

from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

# A value starting with either of these is already encrypted and is stored as it is.
Secret_Prefixes = (SECRETS.PREFIX, SECRETS.Encrypted_Indicator)

# What a secret is replaced with in log lines.
Redacted = '***'

# What a security definition created without a password receives, followed by a random hex string.
Auto_Password_Prefix = 'Zato-Auto-Password-'

# The two names every runtime treats as secrets no matter the connection type.
Common_Secret_Keys = ('password', 'secret')

# Every name any enmasse object type keeps a secret under - for log lines that do not know the type of what they log.
Known_Secret_Keys = Common_Secret_Keys + (
    'api_token', 'token', 'api_key', 'client_secret', 'secret_value', 'consumer_key', 'consumer_secret', 'static_token',
) + AS2.Secret_Fields + AS4.Secret_Fields

# The keys the session carries the importer's crypto context under.
Session_Key_Crypto_Manager = 'crypto_manager'
Session_Key_Server_Dir = 'server_dir'

# ################################################################################################################################
# ################################################################################################################################

def get_crypto_manager(session:'SASession') -> 'ServerCryptoManager':
    """ Returns the crypto manager the session was opened with.
    """
    out = session.info[Session_Key_Crypto_Manager]
    return out

# ################################################################################################################################

def get_server_dir(session:'SASession') -> 'str':
    """ Returns the server directory the session was opened for.
    """
    out = session.info[Session_Key_Server_Dir]
    return out

# ################################################################################################################################

def is_encrypted(value:'str') -> 'bool':
    """ Returns True if the value carries one of the encryption prefixes.
    """
    out = value.startswith(Secret_Prefixes)
    return out

# ################################################################################################################################

def is_usable_secret(value:'any_') -> 'bool':
    """ Returns True for a non-empty string that is not a placeholder standing in for an environment variable
    that was not set - only such a value is a secret the YAML actually gives.
    """
    if not isinstance(value, str):
        return False

    if not value:
        return False

    if value.startswith(EnvVariable.Missing_Value_Prefix):
        return False

    return True

# ################################################################################################################################

def encrypt_secret(session:'SASession', value:'str') -> 'str':
    """ Returns the value encrypted in the form the server produces - the well-known prefix followed by the token.
    A value that is encrypted already is returned as it is.
    """
    if is_encrypted(value):
        return value

    crypto_manager = get_crypto_manager(session)

    # With needs_str the manager always returns a string
    encrypted = cast_('str', crypto_manager.encrypt(value, needs_str=True))

    out = SECRETS.PREFIX + encrypted
    return out

# ################################################################################################################################

def decrypt_secret(session:'SASession', value:'strnone') -> 'strnone':
    """ Returns the value in clear text, whether it is stored encrypted or not.
    """
    # A row with no secret at all is a nullable column, the same way the server hands it back as is
    if value is None:
        return value

    crypto_manager = get_crypto_manager(session)
    out = crypto_manager.decrypt(value)

    # The crypto manager hands plain text input back as bytes
    if isinstance(out, bytes):
        out = out.decode('utf8')

    return out

# ################################################################################################################################

def ensure_encrypted(session:'SASession', value:'str') -> 'str':
    """ Returns a stored value in its encrypted form, encrypting it if it is stored in clear text.
    """
    if is_encrypted(value):
        out = value
    else:
        out = encrypt_secret(session, value)

    return out

# ################################################################################################################################

def redact_secrets(definition:'anydict', keys:'strtuple'=()) -> 'anydict':
    """ Returns a copy of the definition with the value of every secret key replaced by a fixed marker.
    The common secret keys are always redacted, the keys given are the ones specific to the caller's type.
    """
    out = dict(definition)

    for key in keys:
        if key in out:
            out[key] = Redacted

    for key in Common_Secret_Keys:
        if key in out:
            out[key] = Redacted

    return out

# ################################################################################################################################

def is_secret_to_write(value:'any_', is_create:'bool') -> 'bool':
    """ Returns True if the value is a secret the YAML actually gives. A placeholder standing in for an environment
    variable that was not set counts only when an object is created - an existing one keeps its stored secret instead.
    """
    if is_create:
        out = isinstance(value, str) and bool(value)
    else:
        out = is_usable_secret(value)

    return out

# ################################################################################################################################

def secret_needs_update(session:'SASession', yaml_value:'any_', db_value:'any_') -> 'bool':
    """ Returns True if the secret the YAML gives differs from the stored one, once the stored one is decrypted.
    A YAML value that is not usable is never compared, so it never triggers an update.
    """
    if not is_usable_secret(yaml_value):
        return False

    # A row may hold no value at all under this key
    if not isinstance(db_value, str):
        return True

    stored = decrypt_secret(session, db_value)

    out = stored != yaml_value
    return out

# ################################################################################################################################

def encrypt_opaque_secrets(
    definition:'anydict',
    stored:'anydict',
    keys:'strtuple',
    session:'SASession',
    is_create:'bool',
) -> 'None':
    """ Prepares the secret keys of a definition about to land in opaque attributes. A value the YAML gives
    is encrypted in place, a key the YAML does not give in a usable form is dropped so the stored value stays,
    and a stored value that is still in clear text is written back encrypted.
    """
    for name in keys:

        value = definition.get(name)

        if is_secret_to_write(value, is_create):
            definition[name] = encrypt_secret(session, cast_('str', value))
            continue

        # The definition gives no usable value, so a stored one is the one to keep,
        # written back encrypted if it is still in clear text ..
        stored_value = stored.get(name)
        if is_usable_secret(stored_value):
            definition[name] = ensure_encrypted(session, cast_('str', stored_value))
            continue

        # .. an empty default is not a secret and stays, so a wrapper finds the key it expects ..
        if name in definition:
            if not value:
                continue

        # .. and a placeholder must not land anywhere.
        _ = definition.pop(name, None)

# ################################################################################################################################

def encrypt_kept_opaque_secrets(session:'SASession', row:'any_', keys:'strtuple') -> 'bool':
    """ Encrypts in place the secrets a row keeps in its opaque attributes that are still in clear text.
    Returns True if the row was changed. For rows an import found nothing to update in.
    """
    opaque = load_opaque(row.opaque1)
    changed = False

    for name in keys:
        value = opaque.get(name)

        if not is_usable_secret(value):
            continue

        value = cast_('str', value)

        if is_encrypted(value):
            continue

        opaque[name] = encrypt_secret(session, value)
        changed = True

    if changed:
        row.opaque1 = dumps(opaque)
        session.add(row)

    return changed

# ################################################################################################################################

def load_opaque(opaque1:'any_') -> 'anydict':
    """ Returns the opaque attributes a row holds, an empty dict for a row that has none yet.
    """
    if not opaque1:
        return {}

    out = loads(opaque1)
    return out

# ################################################################################################################################
# ################################################################################################################################

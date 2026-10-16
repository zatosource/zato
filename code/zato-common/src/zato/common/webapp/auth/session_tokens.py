# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# cryptography
from cryptography.fernet import Fernet, InvalidToken

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The session key under which the encrypted credentials are stored
Session_Credentials_Key = 'zato_openapi_credentials'

# The key is generated once per process tree - the application is imported in the gunicorn master
# before workers fork, so all workers share it. Restarting the application invalidates all sessions, which is desired.
_credentials_key = Fernet.generate_key()
_credentials_fernet = Fernet(_credentials_key)

# ################################################################################################################################
# ################################################################################################################################

def encrypt_credentials(credentials:'stranydict') -> 'str':
    """ Encrypts the credentials into an opaque token that can be stored in the session cookie.
    """
    data = json.dumps(credentials)
    token = _credentials_fernet.encrypt(data.encode('utf8'))

    out = token.decode('utf8')

    return out

# ################################################################################################################################

def decrypt_credentials(token:'str') -> 'strdictnone':
    """ Decrypts the credentials from a session token. Returns None if the token is not valid,
    e.g. it was issued before the console was last restarted.
    """
    try:
        data = _credentials_fernet.decrypt(token.encode('utf8'))
    except InvalidToken:
        logger.info('Could not decrypt session credentials - the application may have been restarted')
        return None

    out = json.loads(data)

    return out

# ################################################################################################################################
# ################################################################################################################################

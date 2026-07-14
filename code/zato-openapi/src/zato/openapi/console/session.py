# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import json
import logging

# cryptography
from cryptography.fernet import Fernet, InvalidToken

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import optional, strtuple

    strtuplenone = optional[strtuple]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The session key under which the encrypted credentials are stored
Session_Credentials_Key = 'zato_openapi_credentials'

# The key is generated once per process tree - the console application is imported in the gunicorn master
# before workers fork, so all workers share it. Restarting the console invalidates all sessions, which is desired.
_credentials_key = Fernet.generate_key()
_credentials_fernet = Fernet(_credentials_key)

# ################################################################################################################################
# ################################################################################################################################

def encrypt_credentials(username:'str', password:'str') -> 'str':
    """ Encrypts the credentials into an opaque token that can be stored in the session cookie.
    """
    data = json.dumps({'username': username, 'password': password})
    token = _credentials_fernet.encrypt(data.encode('utf8'))

    out = token.decode('utf8')

    return out

# ################################################################################################################################

def decrypt_credentials(token:'str') -> 'strtuplenone':
    """ Decrypts the credentials from a session token. Returns None if the token is not valid,
    e.g. it was issued before the console was last restarted.
    """
    try:
        data = _credentials_fernet.decrypt(token.encode('utf8'))
    except InvalidToken:
        logger.info('Could not decrypt session credentials - the console may have been restarted')
        return None

    credentials = json.loads(data)

    out = (credentials['username'], credentials['password'])

    return out

# ################################################################################################################################
# ################################################################################################################################

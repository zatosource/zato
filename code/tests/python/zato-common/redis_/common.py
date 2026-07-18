# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.redis_env import get_redis_conn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import stranydict, strlist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the Redis connection environment variables share
_env_prefix = 'Zato_Redis_'

# Maps connection detail keys to the suffix of the corresponding environment variable
_detail_suffixes = {
    'host':          'Host',
    'port':          'Port',
    'db':            'DB',
    'username':      'Username',
    'password':      'Password',
    'ssl':           'SSL',
    'ssl_ca_file':   'SSL_CA_File',
    'ssl_cert_file': 'SSL_Cert_File',
    'ssl_key_file':  'SSL_Key_File',
    'ssl_verify':    'SSL_Verify',
}

# ################################################################################################################################
# ################################################################################################################################

def get_env_names() -> 'strlist':
    """ Returns the names of all the environment variables the Redis prefix expands to.
    """

    # Our response to produce
    out:'strlist' = []

    for suffix in _detail_suffixes.values():
        out.append(_env_prefix + suffix)

    return out

# ################################################################################################################################

def build_env(details:'stranydict') -> 'stranydict':
    """ Turns a Redis server's connection details into environment variables.
    Everything becomes a string because that is what the environment holds.
    """

    # Our response to produce
    out:'stranydict' = {}

    for key, value in details.items():
        suffix = _detail_suffixes[key]
        out[_env_prefix + suffix] = str(value)

    return out

# ################################################################################################################################

@contextmanager
def redis_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_Redis_* variables at one server for the duration of a block.
    """
    env_names = get_env_names()
    values = build_env(details)

    # Save everything that is set now so it can be restored later ..
    saved:'stranydict' = {}

    for name in env_names:
        saved[name] = os.environ.pop(name, None)

    # .. apply the server under test ..
    os.environ.update(values)

    try:
        yield

    # .. and restore the previous environment afterwards.
    finally:
        for name in env_names:
            _ = os.environ.pop(name, None)

        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value

# ################################################################################################################################

def run_redis_scenario() -> 'None':
    """ The complete scenario run against whichever server the environment points at -
    ping the server, then write, read and delete a key.
    """
    conn = get_redis_conn()

    # The server must be reachable ..
    assert conn.ping() is True

    # .. a key written must come back unchanged ..
    key = 'zato.test.redis.' + CryptoManager.generate_hex_string(32)
    value = 'test-value-' + CryptoManager.generate_hex_string(32)

    _ = conn.set(key, value)
    stored = conn.get(key)

    assert stored == value.encode('utf-8')

    # .. and once deleted, it must be gone.
    _ = conn.delete(key)
    stored = conn.get(key)

    assert stored is None

    conn.close()

# ################################################################################################################################
# ################################################################################################################################

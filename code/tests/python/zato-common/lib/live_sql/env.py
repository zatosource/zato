# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.db_env.database import database_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import stranydict, strlist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# Maps connection detail keys to the suffix of the corresponding environment variable -
# the prefix Zato_Database_ turns the suffix Type into Zato_Database_Type.
_detail_suffixes = {
    'type':          'Type',
    'path':          'Path',
    'host':          'Host',
    'port':          'Port',
    'username':      'Username',
    'password':      'Password',
    'name':          'Name',
    'ssl':           'SSL',
    'ssl_ca_file':   'SSL_CA_File',
    'ssl_cert_file': 'SSL_Cert_File',
    'ssl_key_file':  'SSL_Key_File',
    'ssl_verify':    'SSL_Verify',
}

# ################################################################################################################################
# ################################################################################################################################

def get_env_names() -> 'strlist':
    """ Returns the names of all the environment variables that select the Zato database.
    """

    # Our response to produce
    out:'strlist' = []

    for suffix in _detail_suffixes.values():
        out.append(database_config.env_prefix + suffix)

    return out

# ################################################################################################################################

def build_env(details:'stranydict') -> 'stranydict':
    """ Turns a database server's connection details into the environment variables of the Zato database.
    """

    # Our response to produce
    out:'stranydict' = {}

    for key, value in details.items():
        suffix = _detail_suffixes[key]
        out[database_config.env_prefix + suffix] = value

    return out

# ################################################################################################################################

@contextmanager
def database_env(details:'stranydict') -> 'envgen':
    """ Points the Zato database at one database server or SQLite file for the duration of a block.
    """
    env_names = get_env_names()
    values = build_env(details)

    # Save everything that is set now so it can be restored later ..
    saved:'stranydict' = {}

    for name in env_names:
        saved[name] = os.environ.pop(name, None)

    # .. apply the database under test ..
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
# ################################################################################################################################

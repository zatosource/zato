# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import stranydict, strlist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# Maps connection detail keys to the suffix of the corresponding environment variable -
# a prefix such as Zato_Ext_DB_ turns the suffix Type into Zato_Ext_DB_Type.
_detail_suffixes = {
    'type':          'Type',
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

def get_env_names(prefix:'str') -> 'strlist':
    """ Returns the names of all the environment variables a given prefix expands to.
    """

    # Our response to produce
    out:'strlist' = []

    for suffix in _detail_suffixes.values():
        out.append(prefix + suffix)

    return out

# ################################################################################################################################

def build_env(prefix:'str', details:'stranydict') -> 'stranydict':
    """ Turns a database server's connection details into environment variables under a given prefix.
    """

    # Our response to produce
    out:'stranydict' = {}

    for key, value in details.items():
        suffix = _detail_suffixes[key]
        out[prefix + suffix] = value

    return out

# ################################################################################################################################

@contextmanager
def database_env(prefix:'str', details:'stranydict') -> 'envgen':
    """ Points the environment variables under a given prefix at one database for the duration of a block.
    """
    env_names = get_env_names(prefix)
    values = build_env(prefix, details)

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

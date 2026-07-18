# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.redis_env import get_redis_conn_from_values, Default_DB, Default_Host, Default_Port, Default_SSL, \
    Default_SSL_Verify

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

def build_values(details:'stranydict') -> 'stranydict':
    """ Expands a Redis server's connection details into a complete dict of connection values,
    the same shape a normalized [redis] section of server.conf has.
    """

    # Our response to produce - the defaults first ..
    out:'stranydict' = {
        'host':          Default_Host,
        'port':          Default_Port,
        'db':            Default_DB,
        'username':      '',
        'password':      '',
        'ssl':           Default_SSL,
        'ssl_ca_file':   '',
        'ssl_cert_file': '',
        'ssl_key_file':  '',
        'ssl_verify':    Default_SSL_Verify,
    }

    # .. overlaid with the details of the server under test.
    out.update(details)

    return out

# ################################################################################################################################

def run_redis_scenario(details:'stranydict') -> 'None':
    """ The complete scenario run against the server the details point at -
    ping the server, then write, read and delete a key.
    """
    values = build_values(details)
    conn = get_redis_conn_from_values(values)

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

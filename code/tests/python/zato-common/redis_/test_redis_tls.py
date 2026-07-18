# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Redis
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

# Zato
from common import run_redis_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

def test_redis_tls(redis_tls_server:'stranydict') -> 'None':
    """ The complete scenario against a TLS-only Redis server,
    with the server certificate verified against the test CA.
    """
    run_redis_scenario(redis_tls_server)

# ################################################################################################################################

def test_redis_tls_rejects_plain_connections(redis_tls_server:'stranydict') -> 'None':
    """ The TLS-only server must not accept unencrypted connections,
    which proves the scenario above really ran over TLS.
    """
    conn = Redis(
        host=redis_tls_server['host'],
        port=redis_tls_server['port'],
    )

    with pytest.raises(RedisConnectionError):
        _ = conn.ping()

    conn.close()

# ################################################################################################################################
# ################################################################################################################################

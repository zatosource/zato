# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import redis_env, run_redis_scenario
from zato.common.redis_env import get_redis_values, Default_DB, Default_Host, Default_Port

# ################################################################################################################################
# ################################################################################################################################

def test_redis_plain() -> 'None':
    """ The complete scenario against the plain Redis server on localhost.
    """
    details = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    }

    with redis_env(details):
        run_redis_scenario()

# ################################################################################################################################

def test_redis_defaults() -> 'None':
    """ With no environment variables set at all, the connection values
    default to a plain localhost server.
    """
    values = get_redis_values()

    assert values['host'] == Default_Host
    assert values['port'] == Default_Port
    assert values['db'] == Default_DB
    assert values['ssl'] is False

    # The defaults describe the same localhost server, so the scenario works with them too.
    run_redis_scenario()

# ################################################################################################################################
# ################################################################################################################################

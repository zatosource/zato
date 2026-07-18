# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_redis_scenario
from zato.common.redis_env import get_redis_values_from_section, Default_DB, Default_Host, Default_Port

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

    run_redis_scenario(details)

# ################################################################################################################################

def test_redis_section_defaults() -> 'None':
    """ A [redis] section written by an older release carries none of the newer keys -
    normalizing it must fill in the defaults, which describe a plain localhost server.
    """
    section = {
        'host': 'localhost',
        'port': '6379',
        'db': '0',
    }

    values = get_redis_values_from_section(section)

    assert values['host'] == Default_Host
    assert values['port'] == Default_Port
    assert values['db'] == Default_DB
    assert values['username'] == ''
    assert values['password'] == ''
    assert values['ssl'] is False
    assert values['ssl_verify'] is True
    assert values['ssl_ca_file'] == ''
    assert values['ssl_cert_file'] == ''
    assert values['ssl_key_file'] == ''

    # The normalized values describe the same localhost server, so the scenario works with them too.
    run_redis_scenario(values)

# ################################################################################################################################
# ################################################################################################################################

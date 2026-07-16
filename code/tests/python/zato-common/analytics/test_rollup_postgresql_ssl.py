# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import analytics_test_env, assert_postgresql_connection_encrypted, run_rollup_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_postgresql_ssl(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete rollup scenario against a PostgreSQL server that requires TLS,
    confirming the analytics store's session really is encrypted.
    """
    with analytics_test_env(postgresql_ssl_server.details):
        run_rollup_scenario()
        assert_postgresql_connection_encrypted()

# ################################################################################################################################
# ################################################################################################################################

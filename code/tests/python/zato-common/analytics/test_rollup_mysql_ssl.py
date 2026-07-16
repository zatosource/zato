# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import analytics_test_env, assert_mysql_connection_encrypted, run_rollup_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_mysql_ssl(mysql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete rollup scenario against a MySQL server that requires TLS,
    confirming the analytics store's session really is encrypted.
    """
    with analytics_test_env(mysql_ssl_server.details):
        run_rollup_scenario()
        assert_mysql_connection_encrypted()

# ################################################################################################################################
# ################################################################################################################################

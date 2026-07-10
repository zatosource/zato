# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from common import assert_postgresql_connection_encrypted, ext_db_env, run_ext_db_scenario
from zato.common.ext_db.api import get_ext_db_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_ext_db_postgresql_ssl(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete external AS2/AS4 database scenario against a PostgreSQL server that requires TLS,
    confirming the session really is encrypted.
    """
    with ext_db_env(postgresql_ssl_server.details):
        run_ext_db_scenario()
        assert_postgresql_connection_encrypted()

# ################################################################################################################################

def test_ext_db_postgresql_ssl_is_required(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ Connecting without SSL to a PostgreSQL server that requires TLS must fail.
    """
    details = dict(postgresql_ssl_server.details)
    details['ssl'] = 'off'

    with ext_db_env(details):
        with pytest.raises(DBAPIError):
            _ = get_ext_db_engine()

# ################################################################################################################################
# ################################################################################################################################

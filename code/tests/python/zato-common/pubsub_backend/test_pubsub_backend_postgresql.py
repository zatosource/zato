# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import replace

# pytest
import pytest

# Zato
from cleanup_postgresql import run_cleanup_postgresql_scenario
from scenarios import run_common_scenarios
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.pubsub_database import connect, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_modes = [PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS, PubSubDBMode.PostgreSQL_MTLS]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    """ A PostgreSQL container per mode, removed with its data once the mode's tests complete.
    """
    database = start_pubsub_database('backend', request.param)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_postgresql(pubsub_database:'PubSubDatabase') -> 'None':
    """ The complete pub/sub backend scenario against PostgreSQL, in plain TCP, TLS and mutual TLS.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_pubsub_engine()
        assert engine.dialect.name == 'postgresql'

        run_common_scenarios()
        run_cleanup_postgresql_scenario()

# ################################################################################################################################

def test_pubsub_postgresql_connections_use_tls(pubsub_database:'PubSubDatabase') -> 'None':
    """ The connections of the TLS modes are encrypted, and the server accepts no other TCP connections.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_pubsub_engine()

        with engine.connect() as connection:
            query = 'select ssl from pg_stat_ssl where pid = pg_backend_pid()'
            is_ssl = connection.exec_driver_sql(query).scalar_one()

    expected = pubsub_database.mode != PubSubDBMode.PostgreSQL
    assert is_ssl is expected, (pubsub_database.mode, is_ssl)

    # A connection without TLS is refused in the TLS modes.
    if expected:
        plain = replace(pubsub_database, mode=PubSubDBMode.PostgreSQL)
        with pytest.raises(Exception, match='pg_hba.conf|no encryption'):
            with closing(connect(plain)):
                pass

# ################################################################################################################################
# ################################################################################################################################

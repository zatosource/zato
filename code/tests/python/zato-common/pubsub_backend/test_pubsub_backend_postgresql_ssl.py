# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.exc import OperationalError

# Zato
from common import assert_postgresql_connection_encrypted, pubsub_backend_env
from encryption import run_encryption_scenario
from lifecycle import run_lifecycle_scenario
from queues import run_queues_scenario
from stats import run_stats_scenario
from wakeup import run_wakeup_scenario
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_postgresql_ssl(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete pub/sub backend scenario against a PostgreSQL server that requires TLS,
    confirming the session really is encrypted.
    """
    with pubsub_backend_env(postgresql_ssl_server.details):
        run_lifecycle_scenario()
        run_queues_scenario()
        run_stats_scenario()
        run_wakeup_scenario()
        run_encryption_scenario()
        assert_postgresql_connection_encrypted()

# ################################################################################################################################

def test_pubsub_backend_postgresql_ssl_is_required(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ Connecting without SSL to a PostgreSQL server that requires TLS must fail.
    """
    details = dict(postgresql_ssl_server.details)
    details['ssl'] = 'off'

    with pubsub_backend_env(details):
        with pytest.raises(OperationalError):
            # The engine is resolved per access, not in __init__, so the connection
            # attempt - and the failure - happens on the property read.
            _ = SQLPubSubBackend().engine

# ################################################################################################################################
# ################################################################################################################################

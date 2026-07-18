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
from common import assert_postgresql_connection_encrypted, audit_log_env, run_audit_log_scenario
from config_audit import run_config_audit_scenario
from resubmit_core import run_resubmit_core_scenario
from retention_tiers import run_retention_tiers_scenario
from structured import run_structured_events_scenario
from zato.common.audit_log.api import AuditLog

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_postgresql_ssl(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete audit log scenario against a PostgreSQL server that requires TLS,
    confirming the session really is encrypted.
    """
    with audit_log_env(postgresql_ssl_server.details):
        run_audit_log_scenario()
        run_structured_events_scenario()
        run_retention_tiers_scenario()
        run_resubmit_core_scenario()
        run_config_audit_scenario()
        assert_postgresql_connection_encrypted()

# ################################################################################################################################

def test_audit_log_postgresql_ssl_is_required(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ Connecting without SSL to a PostgreSQL server that requires TLS must fail.
    """
    details = dict(postgresql_ssl_server.details)
    details['ssl'] = 'off'

    with audit_log_env(details):
        with pytest.raises(DBAPIError):
            _ = AuditLog('test-audit-log-server')

# ################################################################################################################################
# ################################################################################################################################

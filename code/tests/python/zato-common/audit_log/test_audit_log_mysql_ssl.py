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
from common import assert_mysql_connection_encrypted, audit_log_env, run_audit_log_scenario
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_mysql_ssl(mysql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete audit log scenario against a MySQL server that requires TLS,
    confirming the session really is encrypted.
    """
    with audit_log_env(mysql_ssl_server.env):
        run_audit_log_scenario()
        assert_mysql_connection_encrypted()

# ################################################################################################################################

def test_audit_log_mysql_ssl_is_required(mysql_ssl_server:'DatabaseServer') -> 'None':
    """ Connecting without SSL to a MySQL server that requires TLS must fail.
    """
    env = dict(mysql_ssl_server.env)
    env[AuditLogCtx.Env_SSL] = 'off'

    with audit_log_env(env):
        with pytest.raises(OperationalError):
            _ = AuditLog('test-audit-log-server')

# ################################################################################################################################
# ################################################################################################################################

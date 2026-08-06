# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a direct SMTP send reaches for when it is exercised offline - a transport that records
# what would have gone on the wire instead of opening a connection, a connection built around
# it and the environment that points the audit log at a throwaway database.

# stdlib
import os
from contextlib import contextmanager

# Zato
from live_sql.env import database_env
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx
from zato.common.ext.bunch import Bunch
from zato.server.connection.email import SMTPConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-smtp-audit-server'

# The name the connection under test goes by
Connection_Name = 'test.smtp.audit'

# What the raising transport raises with
Raised_Error = 'The SMTP server went away'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def smtp_audit_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################
# ################################################################################################################################

class TransportRecorder:
    """ Stands in for the outbox class - it records what a send was given instead of
    opening a connection.
    """

    # Every send that went through any instance, one (email, attachments, from_) triple each
    sends:'anylist' = []

    def __init__(self, *ignored_args:'any_', **ignored_kwargs:'any_') -> 'None':
        pass

    def __enter__(self) -> 'TransportRecorder':
        return self

    def __exit__(self, *ignored:'any_') -> 'None':
        pass

    def send(self, email:'any_', attachments:'any_', from_:'any_') -> 'None':
        TransportRecorder.sends.append((email, attachments, from_))

# ################################################################################################################################

class RaisingTransport(TransportRecorder):
    """ A transport whose every send fails the way a dead server makes it fail.
    """

    def send(self, email:'any_', attachments:'any_', from_:'any_') -> 'None':
        raise Exception(Raised_Error)

# ################################################################################################################################
# ################################################################################################################################

def new_smtp_connection(
    *,
    is_audit_log_active:'bool' = True,
    transport_class:'any_' = TransportRecorder,
    ) -> 'SMTPConnection':
    """ Builds the connection under test - real except for the transport, which never
    touches the network.
    """
    config = Bunch()

    config.name = Connection_Name
    config.host = 'smtp.invalid'
    config.port = 25
    config.mode_outbox = 'plain'
    config.is_debug = False
    config.timeout = 10
    config.needs_tls_verify = True
    config.ca_certs_path = ''
    config.helo_hostname = ''
    config.from_address = ''
    config.username = ''
    config.password = ''
    config.is_audit_log_active = is_audit_log_active

    audit_log = AuditLog(Server_Name)

    out = SMTPConnection(config, config, audit_log)
    out.conn_class = transport_class

    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# SQLAlchemy
from sqlalchemy import create_engine, func, select

# Zato
from common import audit_log_env
from zato.common.audit_log.api import event_table, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-env-switch-server'

# The channel the test events belong to
_channel_name = 'audit.test.env-switch-channel'

# ################################################################################################################################
# ################################################################################################################################

def _count_events_in_file(db_path:'str') -> 'int':
    """ Counts the audit events in an SQLite file directly, with a throwaway engine,
    independently of whatever the environment variables currently point at.
    """
    engine = create_engine(f'sqlite:///{db_path}')

    count_query = select(func.count()).select_from(event_table)

    with engine.connect() as connection:
        count_result = connection.execute(count_query)
        out = count_result.scalar()

    engine.dispose()
    return out

# ################################################################################################################################

def _insert_events(audit_log:'AuditLog', how_many:'int') -> 'None':
    """ Writes a number of events through the given writer.
    """
    for index in range(how_many):
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
            cid=f'cid-switch-{index}', endpoint='/switch/test', size=10, outcome=AuditOutcome.OK,
            data='{"note": "engine switch test"}')

# ################################################################################################################################

def test_audit_log_env_switch(tmp_path:'os.PathLike') -> 'None':
    """ One writer instance keeps working when the Zato_Audit_Log_DB_* variables are repointed
    at another database at runtime - new events go to the new database and the old one
    keeps what it had, which is exactly what the Config DB SQL screen relies on.
    """
    db_path_a = os.path.join(str(tmp_path), 'audit-a.db')
    db_path_b = os.path.join(str(tmp_path), 'audit-b.db')

    details_a = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path_a,
    }

    details_b = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path_b,
    }

    with audit_log_env(details_a):

        # The writer is created while the environment points at file A ..
        audit_log = AuditLog(_server_name)

        # .. and its first events land there ..
        _insert_events(audit_log, 3)

        assert _count_events_in_file(db_path_a) == 3

        # .. now the environment is repointed at file B, the way a save on the SQL screen does it ..
        with audit_log_env(details_b):

            # .. the very same instance writes through its per-access engine ..
            _insert_events(audit_log, 2)

            # .. the new events are all in file B ..
            assert _count_events_in_file(db_path_b) == 2

            # .. and file A kept its count, untouched by the switch ..
            assert _count_events_in_file(db_path_a) == 3

        # .. once the variables point back at file A, the same instance follows again.
        _insert_events(audit_log, 1)

        assert _count_events_in_file(db_path_a) == 4
        assert _count_events_in_file(db_path_b) == 2

# ################################################################################################################################
# ################################################################################################################################

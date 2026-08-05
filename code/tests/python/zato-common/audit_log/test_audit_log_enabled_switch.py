# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import create_engine, func, select

# Zato
from common import audit_log_env
from zato.common.audit_log.api import event_table, is_audit_log_enabled, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import intnone

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-enabled-switch-server'

# The channel the test events belong to
_channel_name = 'audit.test.enabled-switch-channel'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _audit_log_enabled(is_enabled:'bool') -> 'envgen':
    """ Sets the Enabled switch for the duration of a block, the way a save on the SQL screen does,
    and restores whatever the environment had before.
    """
    env_name = AuditLogCtx.Env_Enabled
    previous = os.environ.get(env_name)

    os.environ[env_name] = str(is_enabled)

    try:
        yield
    finally:
        # A variable that was not there before is removed rather than left behind as an empty one
        if previous is None:
            _ = os.environ.pop(env_name, None)
        else:
            os.environ[env_name] = previous

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

    assert out is not None
    return out

# ################################################################################################################################

def _insert_event(audit_log:'AuditLog', index:'int') -> 'intnone':
    """ Writes one event through the given writer and returns whatever it reported.
    """
    out = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
        cid=f'cid-enabled-{index}', endpoint='/enabled/test', size=10, outcome=AuditOutcome.OK,
        data='{"note": "enabled switch test"}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_enabled_default() -> 'None':
    """ Without the variable set at all, the audit log records events - the switch has to be
    turned off explicitly for anything to change.
    """
    env_name = AuditLogCtx.Env_Enabled
    previous = os.environ.get(env_name)

    _ = os.environ.pop(env_name, None)

    try:
        assert is_audit_log_enabled() is True
    finally:
        if previous is not None:
            os.environ[env_name] = previous

# ################################################################################################################################

def test_audit_log_enabled_switch(tmp_path:'os.PathLike') -> 'None':
    """ One writer instance stops and resumes writing as the Enabled switch is flipped at runtime,
    with no restart and with no new writer, which is what the Config DB SQL screen relies on.
    Nothing is written while the switch is off and no error is raised either - the inserts
    are silent no-ops reporting no event id.
    """
    db_path = os.path.join(str(tmp_path), 'audit-enabled.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with audit_log_env(details):

        audit_log = AuditLog(_server_name)

        # With the switch on, an event is written and reports its id ..
        with _audit_log_enabled(True):

            event_id = _insert_event(audit_log, 1)

            assert event_id is not None
            assert _count_events_in_file(db_path) == 1

        # .. with the switch off, the very same instance writes nothing and reports no id ..
        with _audit_log_enabled(False):

            assert is_audit_log_enabled() is False

            assert _insert_event(audit_log, 2) is None
            assert _insert_event(audit_log, 3) is None

            assert _count_events_in_file(db_path) == 1

        # .. and turning it back on makes the very next event land, without any restart.
        with _audit_log_enabled(True):

            event_id = _insert_event(audit_log, 4)

            assert event_id is not None
            assert _count_events_in_file(db_path) == 2

# ################################################################################################################################
# ################################################################################################################################

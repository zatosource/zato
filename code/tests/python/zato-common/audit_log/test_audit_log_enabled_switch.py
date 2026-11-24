# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.api import event_table, is_audit_log_enabled, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.test.zato_database import zato_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import intnone

    Engine = Engine
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

def _count_events(engine:'Engine') -> 'int':
    """ Counts the audit events in the database of the test directly.
    """
    count_query = select(func.count()).select_from(event_table)

    with engine.connect() as connection:
        count_result = connection.execute(count_query)
        out = count_result.scalar()

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

def test_audit_log_enabled_switch() -> 'None':
    """ One writer instance stops and resumes writing as the Enabled switch is flipped at runtime,
    with no restart and with no new writer, which is what the Config DB SQL screen relies on.
    Nothing is written while the switch is off and no error is raised either - the inserts
    are silent no-ops reporting no event id.
    """
    with zato_database_engine() as engine:

        audit_log = AuditLog(_server_name)

        # With the switch on, an event is written and reports its id ..
        with _audit_log_enabled(True):

            event_id = _insert_event(audit_log, 1)

            assert event_id is not None
            assert _count_events(engine) == 1

        # .. with the switch off, the very same instance writes nothing and reports no id ..
        with _audit_log_enabled(False):

            assert is_audit_log_enabled() is False

            assert _insert_event(audit_log, 2) is None
            assert _insert_event(audit_log, 3) is None

            assert _count_events(engine) == 1

        # .. and turning it back on makes the very next event land, without any restart.
        with _audit_log_enabled(True):

            event_id = _insert_event(audit_log, 4)

            assert event_id is not None
            assert _count_events(engine) == 2

# ################################################################################################################################
# ################################################################################################################################

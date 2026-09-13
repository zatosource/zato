# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Make this directory importable so that test modules can import helpers from conftest.
_conftest_dir = os.path.dirname(__file__)
sys.path.insert(0, _conftest_dir)

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_
    any_ = any_
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'os.PathLike') -> 'any_':
    """ Points the audit database at a per-test SQLite file so every test
    runs on its own isolated database.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
Server_Name = 'test-alerting-server'

# The channels the tests seed events for
Channel_Name = 'hl7.test.channel'
Other_Channel_Name = 'hl7.other.channel'

# The outgoing connection the health check tests seed events for
Connection_Name = 'crm.orders.api'

# The window the error-rate measures cover in these tests, in seconds
Window_Seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def backdate(event_id:'int', event_time:'datetime') -> 'None':
    """ Moves one stored event back in time - the collectors compare event times,
    and the tests need events older than their deadlines.
    """
    engine = get_audit_engine()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def seed_outcome(audit_log:'AuditLog', cid:'str', outcome:'str', *, object_name:'str'=Channel_Name) -> 'None':
    """ Stores one inbound acknowledgment event with the given outcome.
    """
    _ = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, object_name, cid=cid, outcome=outcome)

# ################################################################################################################################

def seed_exchange(audit_log:'AuditLog', source:'str', cid:'str', outcome:'str') -> 'None':
    """ Stores the request/response pair an outgoing connection leaves behind, the way its
    wrapper writes it - the request half always goes out fine, the response half carries
    what actually happened.
    """
    _ = audit_log.insert(source, AuditEvent.Request_Sent, Connection_Name, cid=cid, outcome=AuditOutcome.OK)
    _ = audit_log.insert(source, AuditEvent.Response_Received, Connection_Name, cid=cid, outcome=outcome)

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource, ModuleCtx as AuditLogCtx, event_table
from zato.common.util.api import utcnow
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

def _make_reconciler(tmp_path:'os.PathLike') -> 'Reconciler':
    """ Points the audit log at a per-test SQLite file and builds a reconciler on it.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    out = Reconciler('test-server')
    return out

# ################################################################################################################################

def _cleanup_env() -> 'None':
    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################
# ################################################################################################################################

def test_outstanding_and_matching(tmp_path:'os.PathLike') -> 'None':
    """ Sent interchanges are outstanding until their acknowledgment arrives.
    """
    try:
        reconciler = _make_reconciler(tmp_path)

        reconciler.record_interchange_sent('SENDERID', 'RECEIVERID', '000000905', cid='cid-905')
        reconciler.record_interchange_sent('SENDERID', 'RECEIVERID', '000000906', cid='cid-906')

        # Both interchanges await their acknowledgments
        cutoff = utcnow() + timedelta(seconds=1)
        outstanding = reconciler.outstanding(cutoff)

        assert len(outstanding) == 2
        assert outstanding[0].sender == 'SENDERID'
        assert outstanding[0].receiver == 'RECEIVERID'
        assert outstanding[0].control_number == '905'
        assert outstanding[0].cid == 'cid-905'
        assert outstanding[1].control_number == '906'

        # A 997 echoes the control number without the zero padding - it still matches
        reconciler.record_ack_received('SENDERID', 'RECEIVERID', '905')

        outstanding = reconciler.outstanding(cutoff)
        assert len(outstanding) == 1
        assert outstanding[0].control_number == '906'

        # The other acknowledgment arrives with its full padded number
        reconciler.record_ack_received('SENDERID', 'RECEIVERID', '000000906')

        outstanding = reconciler.outstanding(cutoff)
        assert outstanding == []

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_pairs_are_independent(tmp_path:'os.PathLike') -> 'None':
    """ An acknowledgment from one partner never covers another partner's interchange.
    """
    try:
        reconciler = _make_reconciler(tmp_path)

        reconciler.record_interchange_sent('SENDERID', 'PARTNER-A', '17')
        reconciler.record_interchange_sent('SENDERID', 'PARTNER-B', '17')

        reconciler.record_ack_received('SENDERID', 'PARTNER-A', '17')

        cutoff = utcnow() + timedelta(seconds=1)
        outstanding = reconciler.outstanding(cutoff)

        assert len(outstanding) == 1
        assert outstanding[0].receiver == 'PARTNER-B'

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_cutoff_excludes_recent_sends(tmp_path:'os.PathLike') -> 'None':
    """ An interchange sent after the cutoff is not outstanding yet.
    """
    try:
        reconciler = _make_reconciler(tmp_path)

        cutoff = utcnow() - timedelta(minutes=5)

        reconciler.record_interchange_sent('SENDERID', 'RECEIVERID', '905')

        outstanding = reconciler.outstanding(cutoff)
        assert outstanding == []

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_inbound_events_are_recorded(tmp_path:'os.PathLike') -> 'None':
    """ Received interchanges and sent acknowledgments are audit events too,
    without affecting the outstanding list.
    """
    try:
        reconciler = _make_reconciler(tmp_path)

        reconciler.record_interchange_received('PARTNERID', 'SENDERID', '000000301')
        reconciler.record_ack_sent('PARTNERID', 'SENDERID', '000000301')

        cutoff = utcnow() + timedelta(seconds=1)
        outstanding = reconciler.outstanding(cutoff)
        assert outstanding == []

        # Both events landed in the shared audit table under the X12 source
        statement = select(event_table.c.event_type)
        statement = statement.where(event_table.c.source == AuditSource.X12)
        statement = statement.order_by(event_table.c.id)

        with reconciler.engine.connect() as connection:
            result = connection.execute(statement)
            rows = result.fetchall()

        event_types = []
        for row in rows:
            event_types.append(row[0])

        assert event_types == [AuditEvent.Interchange_Received, AuditEvent.Ack_Sent]

    finally:
        _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

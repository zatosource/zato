# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table, get_audit_engine
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.query import outstanding_conditions
from zato.common.typing_ import anylist
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

def _use_tmp_audit_db(tmp_path:'os.PathLike') -> 'None':
    """ Points the audit database at a per-test SQLite file.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

# ################################################################################################################################

def _cleanup_env() -> 'None':
    _ = os.environ.pop(AuditLogCtx.Env_Type, None)
    _ = os.environ.pop(AuditLogCtx.Env_Name, None)

# ################################################################################################################################

def _run_outstanding_query(
    source:'str',
    open_event:'str',
    close_event:'str',
    needs_object_name_match:'bool',
    ) -> 'anylist':
    """ Runs the outstanding filter the way the audit log page does - the source's open events
    without their closing event, oldest first - returning (object_name, msg_id) pairs.
    """
    conditions = outstanding_conditions(source, open_event, close_event, needs_object_name_match)

    stmt = select(
        event_table.c.object_name,
        event_table.c.msg_id,
    ).where(
        event_table.c.source == source,
        *conditions,
    ).order_by(event_table.c.id.asc())

    engine = get_audit_engine()

    with engine.connect() as connection:
        rows = connection.execute(stmt).fetchall()

    out:'anylist' = []

    for object_name, msg_id in rows:
        out.append((object_name, msg_id))

    return out

# ################################################################################################################################

def _run_as2_query() -> 'anylist':
    out = _run_outstanding_query(AuditSource.AS2, AuditEvent.Message_Sent, AuditEvent.MDN_Received, False)
    return out

# ################################################################################################################################

def _run_x12_query() -> 'anylist':
    out = _run_outstanding_query(AuditSource.X12, AuditEvent.Interchange_Sent, AuditEvent.Ack_Received, True)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2Outstanding:

    def test_sent_messages_without_their_mdn_are_outstanding_oldest_first(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            # Three messages leave, in this order ..
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-first@zato>')
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-second@zato>')
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorpEU', '<orders-third@zato>')

            # .. and only the second one is acknowledged.
            reconciler.record_mdn_received('<orders-second@zato>')

            outstanding = _run_as2_query()

            # The other two are outstanding, oldest first.
            assert outstanding == [
                ('ZatoRetail:PartnerCorp', 'orders-first@zato'),
                ('ZatoRetail:PartnerCorpEU', 'orders-third@zato'),
            ]

        finally:
            _cleanup_env()

    def test_nothing_is_outstanding_once_every_mdn_arrived(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-first@zato>')
            reconciler.record_mdn_received('<orders-first@zato>')

            assert _run_as2_query() == []

        finally:
            _cleanup_env()

    def test_other_event_types_are_not_open_items(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            # An MDN arriving on its own, e.g. for an already-reconciled message,
            # is not an open item of any kind.
            reconciler.record_mdn_received('<already-reconciled@zato>')

            assert _run_as2_query() == []

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestX12Outstanding:

    def test_interchanges_without_their_ack_are_outstanding(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = Reconciler('test-server')

            reconciler.record_interchange_sent('ZATORETAIL', 'PARTNERCORP', '000000001')
            reconciler.record_interchange_sent('ZATORETAIL', 'PARTNERCORP', '000000002')

            # The 997 for the first interchange arrives.
            reconciler.record_ack_received('ZATORETAIL', 'PARTNERCORP', '000000001')

            outstanding = _run_x12_query()

            # Control numbers are normalized, so the zero-padded ISA13 compares equal to its echo.
            assert outstanding == [
                ('ZATORETAIL:PARTNERCORP', '2'),
            ]

        finally:
            _cleanup_env()

    def test_an_ack_for_another_pair_does_not_close_the_interchange(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = Reconciler('test-server')

            # Two partners happen to share the same control number ..
            reconciler.record_interchange_sent('ZATORETAIL', 'PARTNERCORP', '000000007')
            reconciler.record_interchange_sent('ZATORETAIL', 'PARTNERCORPEU', '000000007')

            # .. and only one of them acknowledges it.
            reconciler.record_ack_received('ZATORETAIL', 'PARTNERCORPEU', '000000007')

            outstanding = _run_x12_query()

            # The acknowledgment closes its own pair's interchange only.
            assert outstanding == [
                ('ZATORETAIL:PARTNERCORP', '7'),
            ]

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

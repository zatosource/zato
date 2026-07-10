# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.common import AS2Exception
from zato.common.as2.outbound import SendResult
from zato.common.as2.partnership import new_partnership, Partnership
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import find_connection_name, load_event, record_message_received, reprocess, resend, \
    Target_Service, Target_Topic
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource, event_table, get_audit_engine
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.json_internal import loads
from zato.common.typing_ import dictlist, stranydict
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

# The topic reprocessed messages land on when the partner has no routing override.
_Default_Topic = 'zato.as2.inbound'

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

def _get_last_event_id() -> 'int':
    """ Returns the id of the most recently written audit event.
    """
    stmt = select(event_table.c.id).order_by(event_table.c.id.desc()).limit(1)
    engine = get_audit_engine()

    with engine.connect() as connection:
        row = connection.execute(stmt).first()

    out = row[0]
    return out

# ################################################################################################################################

def _get_events(event_type:'str') -> 'dictlist':
    """ Returns all events of one type, oldest first, each as a dict.
    """
    stmt = select(
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.data,
    ).where(event_table.c.event_type == event_type).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        rows = connection.execute(stmt).fetchall()

    out:'dictlist' = []

    for cid, correl_id, object_name, msg_id, data in rows:
        out.append({'cid': cid, 'correl_id': correl_id, 'object_name': object_name, 'msg_id': msg_id, 'data': data})

    return out

# ################################################################################################################################
# ################################################################################################################################

class _SendRecorder:
    """ A stand-in for an outgoing connection's send method, remembering what it was given
    and answering with a fresh delivery result the way the real pipeline would.
    """

    def __init__(self) -> 'None':
        self.payload = None
        self.filename = None

    def __call__(self, payload:'str', filename:'str | None') -> 'SendResult':
        self.payload = payload
        self.filename = filename

        out = SendResult()
        out.is_ok = True
        out.message_id = '<resent-message@zato>'
        out.mic = 'UmVzZW50TUlDVmFsdWU=, sha-256'

        return out

# ################################################################################################################################

class _RouteRecorder:
    """ A stand-in for a routing target, remembering where each message went.
    """

    def __init__(self) -> 'None':
        self.target_name = None
        self.message = None

    def __call__(self, target_name:'str', message:'stranydict') -> 'None':
        self.target_name = target_name
        self.message = message

# ################################################################################################################################
# ################################################################################################################################

class TestLoadEvent:

    def test_load_event_returns_the_stored_details(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<orders-850@zato>',
                mic='T3JkZXJzTUlD, sha-256',
                cid='cid-original',
                payload='ISA*00*Test payload of an 850 order',
                filename='orders-850.edi',
            )

            event_id = _get_last_event_id()
            event = load_event(event_id)

            assert event.id == event_id
            assert event.cid == 'cid-original'
            assert event.source == AuditSource.AS2
            assert event.event_type == AuditEvent.Message_Sent
            assert event.object_name == 'ZatoRetail:PartnerCorp'
            assert event.msg_id == 'orders-850@zato'
            assert event.details['payload'] == 'ISA*00*Test payload of an 850 order'
            assert event.details['filename'] == 'orders-850.edi'
            assert event.details['mic'] == 'T3JkZXJzTUlD, sha-256'

        finally:
            _cleanup_env()

    def test_load_event_rejects_an_unknown_id(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            _ = AuditLog('test-server')

            with pytest.raises(AS2Exception, match='was not found'):
                _ = load_event(12345)

        finally:
            _cleanup_env()

    def test_load_event_rejects_an_event_without_json_data(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            audit_log.insert(
                AuditSource.AS2, AuditEvent.Message_Sent, 'ZatoRetail:PartnerCorp',
                cid='cid-raw', data='Not a JSON document at all')

            event_id = _get_last_event_id()

            with pytest.raises(AS2Exception, match='does not carry JSON data'):
                _ = load_event(event_id)

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestFindConnectionName:

    def test_the_matching_pair_names_its_connection(self):
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
            {'name': 'AS2 to PartnerCorpEU', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorpEU'},
        ]

        out = find_connection_name(configs, 'ZatoRetail', 'PartnerCorpEU')
        assert out == 'AS2 to PartnerCorpEU'

    def test_an_unknown_pair_is_rejected(self):
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
        ]

        with pytest.raises(AS2Exception, match='No outgoing AS2 connection matches'):
            _ = find_connection_name(configs, 'ZatoRetail', 'UnknownPartner')

# ################################################################################################################################
# ################################################################################################################################

class TestResend:

    def test_resend_delivers_the_stored_payload_again(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<orders-850@zato>',
                cid='cid-original',
                payload='ISA*00*Test payload of an 850 order',
                filename='orders-850.edi',
            )

            event_id = _get_last_event_id()
            event = load_event(event_id)

            send = _SendRecorder()
            result = resend(event, send, reconciler, 'cid-resend')

            # The stored payload went back through the connection, with its filename ..
            assert send.payload == 'ISA*00*Test payload of an 850 order'
            assert send.filename == 'orders-850.edi'
            assert result.message_id == '<resent-message@zato>'

            # .. the new attempt is its own event, linked to the original by its CID ..
            events = _get_events(AuditEvent.Message_Sent)
            event_count = len(events)
            assert event_count == 2

            resent = events[1]
            assert resent['cid'] == 'cid-resend'
            assert resent['correl_id'] == 'cid-original'
            assert resent['object_name'] == 'ZatoRetail:PartnerCorp'
            assert resent['msg_id'] == 'resent-message@zato'

            # .. and it carries the payload too, so it can be resent once again.
            details = loads(resent['data'])
            assert details['payload'] == 'ISA*00*Test payload of an 850 order'
            assert details['filename'] == 'orders-850.edi'
            assert details['mic'] == 'UmVzZW50TUlDVmFsdWU=, sha-256'

        finally:
            _cleanup_env()

    def test_resend_is_a_fresh_open_item(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<orders-850@zato>',
                cid='cid-original',
                payload='ISA*00*Test payload of an 850 order',
            )

            # The original message reconciles once its MDN arrives ..
            reconciler.record_mdn_received('<orders-850@zato>')

            event = load_event(1)
            send = _SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # .. while the resent one waits for an MDN of its own.
            cutoff = utcnow() + timedelta(seconds=1)
            outstanding = reconciler.outstanding(cutoff)

            outstanding_count = len(outstanding)
            assert outstanding_count == 1
            assert outstanding[0].message_id == 'resent-message@zato'

        finally:
            _cleanup_env()

    def test_resend_rejects_other_event_types(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', payload='Test payload')

            # The MDN arrival is an event too, only not a resendable one.
            reconciler.record_mdn_received('<orders-850@zato>', data='{"disposition": "processed"}')

            event_id = _get_last_event_id()
            event = load_event(event_id)

            send = _SendRecorder()

            with pytest.raises(AS2Exception, match='can be resent'):
                _ = resend(event, send, reconciler, 'cid-resend')

        finally:
            _cleanup_env()

    def test_resend_rejects_an_event_without_a_payload(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            # A reconciliation-only entry, recorded without the payload.
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>')

            event = load_event(1)
            send = _SendRecorder()

            with pytest.raises(AS2Exception, match='does not carry a payload'):
                _ = resend(event, send, reconciler, 'cid-resend')

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestReprocess:

    def _seed_received_message(self) -> 'AuditLog':
        """ Writes one inbound message into the audit database, the way the channel records it.
        """
        audit_log = AuditLog('test-server')

        record_message_received(
            audit_log,
            'PartnerCorp', 'ZatoRetail', '<invoice-810@partnercorp>',
            payload='ISA*00*Test payload of an 810 invoice',
            filename='invoice-810.edi',
            content_type='application/edi-x12',
            cid='cid-received',
        )

        return audit_log

    def _new_reversed_partnership(self) -> 'Partnership':
        """ Builds the partnership matching messages that arrive from PartnerCorp -
        the fields compare crosswise, the way inbound matching works.
        """
        out = new_partnership()
        out.as2_from = 'ZatoRetail'
        out.as2_to = 'PartnerCorp'

        return out

    def test_reprocess_routes_to_the_partner_service(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            partnership = self._new_reversed_partnership()
            partnership.inbound_service = 'orders.process-invoice'

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            result = reprocess(event, [partnership], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            # The partner's own service received the message directly ..
            assert result.target_kind == Target_Service
            assert result.target_name == 'orders.process-invoice'
            assert invoke_service.target_name == 'orders.process-invoice'
            assert publish.target_name is None

            # .. in the same shape a live delivery would arrive in.
            message = invoke_service.message
            assert message is not None
            assert message['message_id'] == 'invoice-810@partnercorp'
            assert message['as2_from'] == 'PartnerCorp'
            assert message['as2_to'] == 'ZatoRetail'
            assert message['filename'] == 'invoice-810.edi'
            assert message['content_type'] == 'application/edi-x12'
            assert message['data'] == 'ISA*00*Test payload of an 810 invoice'
            assert 'edi' in message

        finally:
            _cleanup_env()

    def test_reprocess_routes_to_the_partner_topic(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            partnership = self._new_reversed_partnership()
            partnership.inbound_topic = 'partnercorp.invoices'

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            result = reprocess(event, [partnership], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            assert result.target_kind == Target_Topic
            assert result.target_name == 'partnercorp.invoices'
            assert publish.target_name == 'partnercorp.invoices'
            assert invoke_service.target_name is None

        finally:
            _cleanup_env()

    def test_reprocess_defaults_to_the_shared_topic(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            # No partnership matches the pair anymore, e.g. the connection was deleted.
            result = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            assert result.target_kind == Target_Topic
            assert result.target_name == _Default_Topic
            assert publish.target_name == _Default_Topic

        finally:
            _cleanup_env()

    def test_reprocess_records_the_new_attempt(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            # The new attempt is its own event, linked to the original by its CID ..
            events = _get_events(AuditEvent.Message_Received)
            event_count = len(events)
            assert event_count == 2

            reprocessed = events[1]
            assert reprocessed['cid'] == 'cid-reprocess'
            assert reprocessed['correl_id'] == 'cid-received'
            assert reprocessed['object_name'] == 'PartnerCorp:ZatoRetail'
            assert reprocessed['msg_id'] == 'invoice-810@partnercorp'

            # .. and it carries the payload too, so it can be reprocessed once again.
            details = loads(reprocessed['data'])
            assert details['payload'] == 'ISA*00*Test payload of an 810 invoice'
            assert details['filename'] == 'invoice-810.edi'
            assert details['content_type'] == 'application/edi-x12'

        finally:
            _cleanup_env()

    def test_reprocess_rejects_other_event_types(self, tmp_path):
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            reconciler = MDNReconciler('test-server')
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', payload='Test payload')

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            with pytest.raises(AS2Exception, match='can be reprocessed'):
                _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.common.as2.audit import decode_payload_documents, decode_raw_mime, encode_payload_document
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
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

# ################################################################################################################################

def _cleanup_env() -> 'None':
    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

def _get_last_event_id() -> 'int':
    """ Returns the id of the most recently written audit event.
    """
    statement = select(event_table.c.id).order_by(event_table.c.id.desc()).limit(1)
    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    out = row[0]
    return out

# ################################################################################################################################

def _get_events(event_type:'str') -> 'dictlist':
    """ Returns all events of one type, oldest first, each as a dict.
    """
    statement = select(
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.data,
    ).where(event_table.c.event_type == event_type).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

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

# ################################################################################################################################

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

        # Every message this target received, which is more than one for a delivery
        # that carried several documents.
        self.messages:'dictlist' = []

# ################################################################################################################################

    def __call__(self, target_name:'str', message:'stranydict') -> 'None':
        self.target_name = target_name
        self.message = message
        self.messages.append(message)

# ################################################################################################################################
# ################################################################################################################################

class TestLoadEvent:

    def test_load_event_returns_the_stored_details(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_load_event_rejects_an_unknown_id(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            _ = AuditLog('test-server')

            with pytest.raises(AS2Exception, match='was not found'):
                _ = load_event(12345)

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_load_event_rejects_an_event_without_json_data(self, tmp_path:'os.PathLike') -> 'None':
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

    def test_the_matching_pair_names_its_connection(self) -> 'None':
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
            {'name': 'AS2 to PartnerCorpEU', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorpEU'},
        ]

        out = find_connection_name(configs, 'ZatoRetail', 'PartnerCorpEU')
        assert out == 'AS2 to PartnerCorpEU'

# ################################################################################################################################

    def test_an_unknown_pair_is_rejected(self) -> 'None':
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
        ]

        with pytest.raises(AS2Exception, match='No outgoing AS2 connection matches'):
            _ = find_connection_name(configs, 'ZatoRetail', 'UnknownPartner')

# ################################################################################################################################
# ################################################################################################################################

class TestResend:

    def test_resend_delivers_the_stored_payload_again(self, tmp_path:'os.PathLike') -> 'None':
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
            assert send.payload == b'ISA*00*Test payload of an 850 order'
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

# ################################################################################################################################

    def test_resend_is_a_fresh_open_item(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_resend_rejects_other_event_types(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_resend_rejects_an_event_without_a_payload(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def _new_reversed_partnership(self) -> 'Partnership':
        """ Builds the partnership matching messages that arrive from PartnerCorp -
        the fields compare crosswise, the way inbound matching works.
        """
        out = new_partnership()
        out.as2_from = 'ZatoRetail'
        out.as2_to = 'PartnerCorp'

        return out

# ################################################################################################################################

    def test_reprocess_routes_to_the_partner_service(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_reprocess_routes_to_the_partner_topic(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_reprocess_defaults_to_the_shared_topic(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_reprocess_records_the_new_attempt(self, tmp_path:'os.PathLike') -> 'None':
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

# ################################################################################################################################

    def test_reprocess_rejects_other_event_types(self, tmp_path:'os.PathLike') -> 'None':
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

# A short run of bytes no text decoding survives - byte 0x80 is not valid UTF-8 and 0x00 does not
# survive a round trip through a text field either. Real payloads that look like this are the PDFs
# and compressed archives that travel as attachments next to an EDI document.
_binary_payload = b'%PDF-1.7\x00\x80\xff\xfe binary content \x01\x02\x03'

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadFidelity:
    """ A resubmit has to deliver what arrived, byte for byte. A payload kept in a text field goes
    through a UTF-8 decode with replacement characters on the way in and an encode on the way out,
    which silently rewrites every byte that is not valid UTF-8 - and the whole point of multiple
    attachments is carrying exactly the kind of content that is not.
    """

    def test_binary_documents_survive_a_reprocess(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            lossy_text = _binary_payload.decode('utf8', 'replace')
            document = encode_payload_document(_binary_payload, 'application/pdf', 'bill-of-lading.pdf')

            record_message_received(
                audit_log,
                'PartnerCorp', 'ZatoRetail', '<bol@partnercorp>',
                payload=lossy_text,
                filename='bill-of-lading.pdf',
                content_type='application/pdf',
                cid='cid-received',
                payloads=[document],
            )

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            # The stored document came back unchanged, which the readable text field
            # could not have managed.
            documents = decode_payload_documents(event.details)
            first_document = documents[0]
            data = first_document[0]

            assert data == _binary_payload

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_binary_documents_survive_a_resend(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            lossy_text = _binary_payload.decode('utf8', 'replace')
            document = encode_payload_document(_binary_payload, 'application/pdf', 'bill-of-lading.pdf')

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<bol@zato>',
                cid='cid-original',
                payload=lossy_text,
                filename='bill-of-lading.pdf',
                payloads=[document],
            )

            event = load_event(1)

            send = _SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # The exact bytes went back out over the wire ..
            assert send.payload == _binary_payload
            assert send.filename == 'bill-of-lading.pdf'

            # .. and the new event carries them too, so the next resend is lossless as well.
            events = _get_events(AuditEvent.Message_Sent)
            new_event = events[1]
            details = loads(new_event['data'])

            stored_documents = details['payloads']
            first_document = stored_documents[0]
            data = decode_raw_mime(first_document['data'])

            assert data == _binary_payload

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_every_attachment_is_reprocessed(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            edi = b'ISA*00*Test payload of an 856 ship notice'
            edi_text = edi.decode('utf8')

            edi_document = encode_payload_document(edi, 'application/edi-x12', 'ship-notice-856.edi')
            pdf_document = encode_payload_document(_binary_payload, 'application/pdf', 'bill-of-lading.pdf')

            record_message_received(
                audit_log,
                'PartnerCorp', 'ZatoRetail', '<ship-notice@partnercorp>',
                payload=edi_text,
                filename='ship-notice-856.edi',
                content_type='application/edi-x12',
                cid='cid-received',
                payloads=[edi_document, pdf_document],
            )

            event = load_event(1)

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            result = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            # Both documents were routed, each with its own content type and filename -
            # a subscriber that received the EDI document and the attached PDF the first time
            # receives both of them again.
            routed_count = len(publish.messages)
            assert routed_count == 2

            first, second = publish.messages

            assert first['filename'] == 'ship-notice-856.edi'
            assert first['content_type'] == 'application/edi-x12'
            assert first['data'] == edi_text

            assert second['filename'] == 'bill-of-lading.pdf'
            assert second['content_type'] == 'application/pdf'

            # The result reports every routed message, with the first one still available
            # on its own for the single-document case.
            message_count = len(result.messages)
            first_message = result.messages[0]

            assert message_count == 2
            assert result.message is first_message

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_every_attachment_is_resent_together(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            edi = b'ISA*00*Test payload of an 856 ship notice'
            edi_text = edi.decode('utf8')

            edi_document = encode_payload_document(edi, 'application/edi-x12', 'ship-notice-856.edi')
            pdf_document = encode_payload_document(_binary_payload, 'application/pdf', 'bill-of-lading.pdf')

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<ship-notice@zato>',
                cid='cid-original',
                payload=edi_text,
                filename='ship-notice-856.edi',
                payloads=[edi_document, pdf_document],
            )

            event = load_event(1)

            send = _SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # The message goes back out as one multi-attachment delivery, each document keeping
            # its own content type and filename, which is what the partner received originally.
            item_count = len(send.payload)
            assert item_count == 2

            first, second = send.payload

            assert first.data == edi
            assert first.content_type == 'application/edi-x12'
            assert first.filename == 'ship-notice-856.edi'

            assert second.data == _binary_payload
            assert second.content_type == 'application/pdf'
            assert second.filename == 'bill-of-lading.pdf'

            # A multi-document payload carries its filenames inside, so none travels separately.
            assert send.filename is None

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_an_event_from_before_the_payload_entries_still_resubmits(self, tmp_path:'os.PathLike') -> 'None':
        try:
            _use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            # The older shape - one text payload with its metadata alongside it, which is what
            # events already in the database look like.
            record_message_received(
                audit_log,
                'PartnerCorp', 'ZatoRetail', '<invoice-810@partnercorp>',
                payload='ISA*00*Test payload of an 810 invoice',
                filename='invoice-810.edi',
                content_type='application/edi-x12',
                cid='cid-received',
            )

            event = load_event(1)

            # The entries are empty, so the text field is what the reprocess falls back to.
            del event.details['payloads']

            invoke_service = _RouteRecorder()
            publish = _RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', _Default_Topic)

            routed_count = len(publish.messages)
            assert routed_count == 1

            message = publish.messages[0]

            assert message['data'] == 'ISA*00*Test payload of an 810 invoice'
            assert message['filename'] == 'invoice-810.edi'
            assert message['content_type'] == 'application/edi-x12'

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

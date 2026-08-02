# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from .resubmit_helpers import Binary_Payload, cleanup_env, Default_Topic, get_events, RouteRecorder, SendRecorder, \
    use_tmp_audit_db
from zato.common.as2.audit import decode_payload_documents, decode_raw_mime, encode_payload_document
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import load_event, record_message_received, reprocess, resend
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.json_internal import loads
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

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
            use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            lossy_text = Binary_Payload.decode('utf8', 'replace')
            document = encode_payload_document(Binary_Payload, 'application/pdf', 'bill-of-lading.pdf')

            options = {
                'payload': lossy_text,
                'filename': 'bill-of-lading.pdf',
                'content_type': 'application/pdf',
                'cid': 'cid-received',
                'payloads': [document],
                }
            record_message_received(audit_log, 'PartnerCorp', 'ZatoRetail', '<bol@partnercorp>', **cast_('any_', options))

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            # The stored document came back unchanged, which the readable text field
            # could not have managed.
            documents = decode_payload_documents(event.details)
            first_document = documents[0]
            data = first_document[0]

            assert data == Binary_Payload

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_binary_documents_survive_a_resend(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            lossy_text = Binary_Payload.decode('utf8', 'replace')
            document = encode_payload_document(Binary_Payload, 'application/pdf', 'bill-of-lading.pdf')

            options = {
                'cid': 'cid-original',
                'payload': lossy_text,
                'filename': 'bill-of-lading.pdf',
                'payloads': [document],
                }
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<bol@zato>', **cast_('any_', options))

            event = load_event(1)

            send = SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # The exact bytes went back out over the wire ..
            assert send.payload == Binary_Payload
            assert send.filename == 'bill-of-lading.pdf'

            # .. and the new event carries them too, so the next resend is lossless as well.
            events = get_events(AuditEvent.Message_Sent)
            new_event = events[1]
            details = loads(new_event['data'])

            stored_documents = details['payloads']
            first_document = stored_documents[0]
            encoded_data = first_document['data']
            data = decode_raw_mime(encoded_data)

            assert data == Binary_Payload

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_every_attachment_is_reprocessed(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            edi = b'ISA*00*Test payload of an 856 ship notice'
            edi_text = edi.decode('utf8')

            edi_document = encode_payload_document(edi, 'application/edi-x12', 'ship-notice-856.edi')
            pdf_document = encode_payload_document(Binary_Payload, 'application/pdf', 'bill-of-lading.pdf')

            options = {
                'payload': edi_text,
                'filename': 'ship-notice-856.edi',
                'content_type': 'application/edi-x12',
                'cid': 'cid-received',
                'payloads': [edi_document, pdf_document],
                }
            record_message_received(audit_log, 'PartnerCorp', 'ZatoRetail', '<ship-notice@partnercorp>', **cast_('any_', options))

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            result = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

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
            cleanup_env()

# ################################################################################################################################

    def test_every_attachment_is_resent_together(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            edi = b'ISA*00*Test payload of an 856 ship notice'
            edi_text = edi.decode('utf8')

            edi_document = encode_payload_document(edi, 'application/edi-x12', 'ship-notice-856.edi')
            pdf_document = encode_payload_document(Binary_Payload, 'application/pdf', 'bill-of-lading.pdf')

            options = {
                'cid': 'cid-original',
                'payload': edi_text,
                'filename': 'ship-notice-856.edi',
                'payloads': [edi_document, pdf_document],
                }
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<ship-notice@zato>', **cast_('any_', options))

            event = load_event(1)

            send = SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # The message goes back out as one multi-attachment delivery, each document keeping
            # its own content type and filename, which is what the partner received originally.
            item_count = len(cast_('any_', send.payload))
            assert item_count == 2

            first, second = send.payload

            assert cast_('any_', first).data == edi
            assert cast_('any_', first).content_type == 'application/edi-x12'
            assert cast_('any_', first).filename == 'ship-notice-856.edi'

            assert cast_('any_', second).data == Binary_Payload
            assert cast_('any_', second).content_type == 'application/pdf'
            assert cast_('any_', second).filename == 'bill-of-lading.pdf'

            # A multi-document payload carries its filenames inside, so none travels separately.
            assert send.filename is None

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_an_event_from_before_the_payload_entries_still_resubmits(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            # The older shape - one text payload with its metadata alongside it, which is what
            # events already in the database look like.
            options = {
                'payload': 'ISA*00*Test payload of an 810 invoice',
                'filename': 'invoice-810.edi',
                'content_type': 'application/edi-x12',
                'cid': 'cid-received',
                }
            record_message_received(audit_log, 'PartnerCorp', 'ZatoRetail', '<invoice-810@partnercorp>', **options)

            event = load_event(1)

            # The entries are empty, so the text field is what the reprocess defaults to.
            del event.details['payloads']

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            routed_count = len(publish.messages)
            assert routed_count == 1

            message = publish.messages[0]

            assert message['data'] == 'ISA*00*Test payload of an 810 invoice'
            assert message['filename'] == 'invoice-810.edi'
            assert message['content_type'] == 'application/edi-x12'

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

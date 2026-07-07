# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import NS, Severity
from zato.common.as4.ebms import build_envelope, build_error, build_pull_request, build_receipt, build_user_message, \
    new_message_id, parse_messaging, qname
from zato.common.as4.outbound import new_part
from zato.common.as4.pmode import new_pmode

# ################################################################################################################################
# ################################################################################################################################

def _make_pmode():
    out = new_pmode()

    out.initiator.party_id = 'party-a'
    out.initiator.role = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator'
    out.responder.party_id = 'party-b'
    out.responder.role = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder'

    out.service = 'urn:test:service'
    out.action = 'SubmitInvoice'

    out.original_sender = 'C1-original-sender'
    out.final_recipient = 'C4-final-recipient'

    return out

# ################################################################################################################################

def _messaging_of(envelope):
    header = envelope.find(qname(NS.SOAP, 'Header'))
    out = header.find(qname(NS.EBMS, 'Messaging'))
    return out

# ################################################################################################################################

def _validate(schema, envelope):
    """ Validates the eb:Messaging block of an envelope against the official OASIS schema.
    """
    messaging = deepcopy(_messaging_of(envelope))
    schema.assertValid(messaging)

# ################################################################################################################################
# ################################################################################################################################

class TestUserMessage:

    def test_user_message_validates_against_official_schema(self, ebms_schema):
        pmode = _make_pmode()
        part = new_part(b'<Invoice/>')
        part.compressed = True
        part.content_type = 'application/gzip'

        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')

        _validate(ebms_schema, envelope)

    def test_user_message_parse_roundtrip(self):
        pmode = _make_pmode()
        part = new_part(b'<Invoice/>')
        part.compressed = True
        part.content_type = 'application/gzip'

        envelope = build_envelope()
        message_id = new_message_id()
        _ = build_user_message(envelope, pmode, [part], message_id, 'conversation-1')

        # Serialize and reparse to prove the wire form carries everything.
        wire = etree.tostring(envelope)
        messaging = parse_messaging(etree.fromstring(wire))

        assert len(messaging.user_messages) == 1
        user_message = messaging.user_messages[0]

        assert user_message.message_id == message_id
        assert user_message.conversation_id == 'conversation-1'
        assert user_message.from_party == 'party-a'
        assert user_message.to_party == 'party-b'
        assert user_message.service == 'urn:test:service'
        assert user_message.action == 'SubmitInvoice'

        # The four-corner properties travel as message properties.
        assert user_message.message_properties['originalSender'] == 'C1-original-sender'
        assert user_message.message_properties['finalRecipient'] == 'C4-final-recipient'

        # The payload part is described with its compression state.
        assert len(user_message.part_infos) == 1
        part_info = user_message.part_infos[0]
        assert part_info.href == f'cid:{part.content_id}'
        assert part_info.properties['MimeType'] == 'application/xml'
        assert part_info.properties['CompressionType'] == 'application/gzip'

# ################################################################################################################################
# ################################################################################################################################

class TestSignals:

    def test_receipt_validates_against_official_schema(self, ebms_schema):
        envelope = build_envelope()
        _ = build_receipt(envelope, 'original-message-id@test', [])

        _validate(ebms_schema, envelope)

    def test_receipt_parse_roundtrip(self):
        envelope = build_envelope()
        _ = build_receipt(envelope, 'original-message-id@test', [])

        wire = etree.tostring(envelope)
        messaging = parse_messaging(etree.fromstring(wire))

        assert len(messaging.signals) == 1
        signal = messaging.signals[0]

        assert signal.is_receipt
        assert signal.ref_to_message_id == 'original-message-id@test'

    def test_error_validates_against_official_schema(self, ebms_schema):
        envelope = build_envelope()
        _ = build_error(envelope, 'bad-message-id@test', 'EBMS:0101', 'FailedAuthentication', 'The check failed')

        _validate(ebms_schema, envelope)

    def test_error_parse_roundtrip(self):
        envelope = build_envelope()
        _ = build_error(envelope, 'bad-message-id@test', 'EBMS:0101', 'FailedAuthentication', 'The check failed')

        wire = etree.tostring(envelope)
        messaging = parse_messaging(etree.fromstring(wire))

        signal = messaging.signals[0]
        assert len(signal.errors) == 1

        error = signal.errors[0]
        assert error.error_code == 'EBMS:0101'
        assert error.severity == Severity.Failure
        assert error.detail == 'The check failed'
        assert error.ref_to_message_id == 'bad-message-id@test'

    def test_pull_request_validates_against_official_schema(self, ebms_schema):
        envelope = build_envelope()
        _ = build_pull_request(envelope, 'urn:test:mpc:eori:pl:1234')

        _validate(ebms_schema, envelope)

    def test_pull_request_parse_roundtrip(self):
        envelope = build_envelope()
        _ = build_pull_request(envelope, 'urn:test:mpc:eori:pl:1234')

        wire = etree.tostring(envelope)
        messaging = parse_messaging(etree.fromstring(wire))

        signal = messaging.signals[0]
        assert signal.pull_mpc == 'urn:test:mpc:eori:pl:1234'

# ################################################################################################################################
# ################################################################################################################################

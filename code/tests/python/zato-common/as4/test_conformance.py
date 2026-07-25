# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone

# httpx
import httpx

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.typing_ import cast_
from zato.common.as4.common import AS4Exception, AS4ProtocolException, EbMSError, Limits, NS
from zato.common.as4.ebms import Body_Element_ID, build_envelope, build_receipt, build_user_message, \
    find_messaging, Messaging_Element_ID, parse_messaging
from zato.common.as4.inbound import handle
from zato.common.as4.mime_ import build_multipart, Cid_Prefix, compress_part, decompress_part, parse_multipart
from zato.common.as4.outbound import build_push_message, new_message_id, new_part, send
from zato.common.as4.profiles import new_edelivery1_pmode, new_peppol_pmode
from zato.common.as4.sbdh import parse_sbdh
from zato.common.as4.security.sign import sign_envelope
from zato.common.as4.security.verify import verify_envelope
from zato.common.util.xml_.core import parse_xml, qname, to_timestamp
from zato.common.util.xml_.keystore import new_keystore
from zato.common.util.xml_.signature import compute_signature_value
from zato.common.util.xml_.xmlsec import encode_base64

from .conftest import set_party_ids

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The contents of the file that the documents below name in an entity declaration.
External_Text = 'as4-external-file-contents'

# One entity referencing the next, each ten times over, so three levels turn ten bytes into ten thousand.
_nested_entity_declarations = (
    b'<!ENTITY level_one "aaaaaaaaaa">'
    b'<!ENTITY level_two "&level_one;&level_one;&level_one;&level_one;&level_one;'
    b'&level_one;&level_one;&level_one;&level_one;&level_one;">'
    b'<!ENTITY level_three "&level_two;&level_two;&level_two;&level_two;&level_two;'
    b'&level_two;&level_two;&level_two;&level_two;&level_two;">'
)

_expanded_marker = b'a' * 1000

Payload = b'<Invoice xmlns="urn:test"><Total>100</Total></Invoice>'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def external_file(tmp_path:'any_') -> 'str':
    """ A file on disk that the documents below name in an entity declaration.
    """
    path = tmp_path / 'as4-external-file.txt'
    _ = path.write_text(External_Text)

    out = str(path)
    return out

# ################################################################################################################################

def _envelope_with_doctype(declarations:'bytes', body:'bytes') -> 'bytes':
    """ Builds a SOAP envelope carrying an inline DTD.
    """
    prologue = b'<?xml version="1.0"?><!DOCTYPE s12:Envelope ['
    root_start = b']><s12:Envelope xmlns:s12="http://www.w3.org/2003/05/soap-envelope"><s12:Header/><s12:Body>'
    epilogue = b'</s12:Body></s12:Envelope>'

    out = prologue + declarations + root_start + body + epilogue
    return out

# ################################################################################################################################

def _standard_business_document(doctype:'str', receiver_id:'str') -> 'bytes':
    """ Builds a StandardBusinessDocument with the doctype and receiver id given.
    """
    out = (
        '<?xml version="1.0"?>'
        f'{doctype}'
        '<sbdh:StandardBusinessDocument'
        ' xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">'
        '<sbdh:StandardBusinessDocumentHeader>'
        '<sbdh:Sender><sbdh:Identifier Authority="iso6523-actorid-upis">0192:111</sbdh:Identifier></sbdh:Sender>'
        f'<sbdh:Receiver><sbdh:Identifier Authority="iso6523-actorid-upis">{receiver_id}</sbdh:Identifier></sbdh:Receiver>'
        '<sbdh:DocumentIdentification><sbdh:InstanceIdentifier>instance-01</sbdh:InstanceIdentifier>'
        '</sbdh:DocumentIdentification>'
        '</sbdh:StandardBusinessDocumentHeader>'
        '<Invoice xmlns="urn:test"/>'
        '</sbdh:StandardBusinessDocument>'
    ).encode('utf8')

    return out

# ################################################################################################################################

def _handle(body:'bytes') -> 'any_':
    """ Runs one envelope through the inbound pipeline with a minimal configuration.
    """
    pmode = new_edelivery1_pmode()

    out = handle(body, 'application/soap+xml', [pmode], new_keystore())
    return out

# ################################################################################################################################

def _make_peppol_pmode(parties:'TestParties') -> 'any_':
    """ A P-Mode that signs without encrypting, so that a message can be taken apart in a test.
    """
    out = new_peppol_pmode()

    set_party_ids(out, parties)

    out.service = 'urn:test:service'
    out.action = 'SubmitInvoice'

    return out

# ################################################################################################################################

def _serialize(envelope:'any_') -> 'bytes':
    out = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def _build_message_signed_over(
    pmode:'any_',
    keystore:'any_',
    parts:'any_',
    keep_body:'bool',
    keep_attachments:'bool',
    ) -> 'any_':
    """ Builds a push message whose signature covers eb:Messaging and, as the flags say, the SOAP
    Body and the attachments. References are removed from ds:SignedInfo after signing and the
    signature value is recomputed over what is left, so the message stays internally consistent -
    every digest in it is correct and the signature over them verifies.
    """
    message_id = new_message_id()

    envelope = build_envelope()
    _ = build_user_message(envelope, pmode, parts, message_id, message_id)

    signature = sign_envelope(envelope, parts, keystore, pmode.security)
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    for reference in signed_info.findall(qname(NS.DS, 'Reference')):
        uri = reference.get('URI')

        if uri.startswith(Cid_Prefix):
            if not keep_attachments:
                signed_info.remove(reference)

        elif uri == f'#{Body_Element_ID}':
            if not keep_body:
                signed_info.remove(reference)

    signature_bytes = compute_signature_value(signed_info, keystore, pmode.security.signature_algorithm)
    signature_value = signature.find(qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    out = build_multipart(_serialize(envelope), parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInboundXMLParsing:
    """ What the inbound pipeline accepts from a document, which is the same set of parse rules
    the whole SOAP family follows.
    """

    def test_nested_entities_are_not_expanded(self) -> 'None':
        body = _envelope_with_doctype(_nested_entity_declarations, b'&level_three;')

        result = _handle(body)

        assert result.is_error
        assert result.error_code == EbMSError.Invalid_Header

        # No expanded text reaches the response.
        assert _expanded_marker not in result.body

# ################################################################################################################################

    def test_external_entities_are_not_resolved(self, external_file:'str') -> 'None':
        declarations = f'<!ENTITY declared SYSTEM "file://{external_file}">'.encode('utf8')
        body = _envelope_with_doctype(declarations, b'&declared;')

        result = _handle(body)

        assert result.is_error
        assert External_Text.encode('utf8') not in result.body

# ################################################################################################################################

    def test_envelope_without_a_messaging_header_is_refused(self) -> 'None':
        result = _handle(b'<not-an-envelope/>')

        assert result.is_error
        assert result.error_code == EbMSError.Invalid_Header

# ################################################################################################################################
# ################################################################################################################################

class TestSBDHParsing:
    """ The same parse rules apply to a Peppol payload as to the envelope that carried it.
    """

    def test_a_document_naming_an_external_entity_is_refused(self, external_file:'str') -> 'None':
        doctype = f'<!DOCTYPE sbdh:StandardBusinessDocument [<!ENTITY declared SYSTEM "file://{external_file}">]>'
        document = _standard_business_document(doctype, '&declared;')

        with pytest.raises(AS4ProtocolException) as raised:
            _ = parse_sbdh(document)

        assert raised.value.error_code == EbMSError.Value_Not_Recognized

# ################################################################################################################################

    def test_the_same_document_without_a_doctype_parses(self) -> 'None':

        # The counterpart to the test above, which would otherwise pass on any document at all.
        document = _standard_business_document('', '0192:222')

        details, _ = parse_sbdh(document)

        assert details.sender_id == '0192:111'
        assert details.receiver_id == '0192:222'

# ################################################################################################################################

    def test_nested_entities_are_not_expanded(self) -> 'None':
        prologue = b'<?xml version="1.0"?><!DOCTYPE sbdh:StandardBusinessDocument ['
        root_start = (
            b']><sbdh:StandardBusinessDocument'
            b' xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">'
            b'<sbdh:StandardBusinessDocumentHeader>&level_three;</sbdh:StandardBusinessDocumentHeader>'
            b'</sbdh:StandardBusinessDocument>'
        )

        document = prologue + _nested_entity_declarations + root_start

        with pytest.raises(AS4ProtocolException) as raised:
            _ = parse_sbdh(document)

        assert raised.value.error_code == EbMSError.Value_Not_Recognized

# ################################################################################################################################
# ################################################################################################################################

class TestSignatureCoverage:
    """ The AS4 profile requires the signature to cover eb:Messaging, the SOAP Body and every
    attachment. Each of the three is asserted separately.
    """

    def test_a_message_signed_over_the_header_alone_is_refused(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)
        parts = [new_part(Payload)]

        body, content_type = _build_message_signed_over(
            pmode, rsa_parties.sender, parts, keep_body=False, keep_attachments=False)

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Policy_Noncompliance
        assert result.payloads == []

# ################################################################################################################################

    def test_a_message_with_an_unsigned_attachment_is_refused(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)
        parts = [new_part(Payload)]

        body, content_type = _build_message_signed_over(
            pmode, rsa_parties.sender, parts, keep_body=True, keep_attachments=False)

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Policy_Noncompliance

# ################################################################################################################################

    def test_the_same_message_signed_over_everything_is_accepted(self, rsa_parties:'TestParties') -> 'None':

        # The counterpart to the two tests above - the same construction with nothing removed goes
        # through, so what they assert on is the coverage and not the way they build a message.
        pmode = _make_peppol_pmode(rsa_parties)
        parts = [new_part(Payload)]

        body, content_type = _build_message_signed_over(
            pmode, rsa_parties.sender, parts, keep_body=True, keep_attachments=True)

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert not result.is_error
        assert result.payloads[0].data == Payload

# ################################################################################################################################

    def test_a_second_messaging_header_is_refused(self, rsa_parties:'TestParties') -> 'None':

        # A copy of the signed header block, carrying its own id so that it is unambiguous, placed
        # ahead of the original where a parse by element name reaches it first.
        pmode = _make_peppol_pmode(rsa_parties)
        parts = [new_part(Payload)]

        body, content_type, _, _ = build_push_message(pmode, rsa_parties.sender, parts)
        envelope_bytes, wire_parts = parse_multipart(body, content_type)

        envelope = etree.fromstring(envelope_bytes)
        header = cast_('any_', envelope.find(qname(NS.SOAP, 'Header')))
        messaging = header.find(qname(NS.EBMS, 'Messaging'))

        inserted = deepcopy(messaging)
        inserted.set(qname(NS.WSU, 'Id'), f'{Messaging_Element_ID}-inserted')
        header.insert(0, inserted)

        wrapped_body, wrapped_content_type = build_multipart(_serialize(envelope), wire_parts)

        result = handle(wrapped_body, wrapped_content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Policy_Noncompliance

# ################################################################################################################################
# ################################################################################################################################

class TestInboundPolicy:
    """ What a P-Mode requires of an incoming message beyond what the message itself states.
    """

    def test_an_unencrypted_message_is_refused_when_the_pmode_encrypts(self, rsa_parties:'TestParties') -> 'None':
        pmode = new_edelivery1_pmode()
        set_party_ids(pmode, rsa_parties)
        pmode.service = 'urn:test:service'
        pmode.action = 'SubmitInvoice'

        # The same exchange, sent without encryption.
        sending_pmode = deepcopy(pmode)
        sending_pmode.security.encrypt = False

        body, content_type, _, _ = build_push_message(sending_pmode, rsa_parties.sender, [new_part(Payload)])

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Policy_Noncompliance
        assert result.payloads == []

# ################################################################################################################################

    def test_a_message_from_a_party_the_certificate_does_not_name_is_refused(
        self,
        rsa_parties:'TestParties',
        ) -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)

        # The sender names itself as a party its certificate does not name.
        sending_pmode = deepcopy(pmode)
        sending_pmode.initiator.party_id = 'as4-somebody-else'

        body, content_type, _, _ = build_push_message(sending_pmode, rsa_parties.sender, [new_part(Payload)])

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Failed_Authentication

# ################################################################################################################################

    def test_a_receipt_that_leaves_out_a_reference_is_refused(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)
        pmode.endpoint_url = 'https://as4.invalid/msh'

        def responder(request:'any_') -> 'any_':

            # A valid receipt in every respect except that it accounts for one reference only.
            envelope_bytes, parts = parse_multipart(request.content, request.headers['content-type'])
            envelope = parse_xml(envelope_bytes)
            messaging = parse_messaging(envelope)

            verify_result = verify_envelope(envelope, parts, rsa_parties.receiver)

            receipt_envelope = build_envelope()
            _ = build_receipt(
                receipt_envelope, messaging.user_messages[0].message_id, verify_result.signed_references[:1])
            _ = sign_envelope(receipt_envelope, [], rsa_parties.receiver, pmode.security)

            body = _serialize(receipt_envelope)

            out = httpx.Response(200, content=body, headers={'Content-Type': 'application/soap+xml; charset=UTF-8'})
            return out

        client = httpx.Client(transport=httpx.MockTransport(responder))

        with pytest.raises(AS4Exception) as raised:
            _ = send(pmode, rsa_parties.sender, [new_part(Payload)], client=client)

        assert 'does not account for' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestResourceLimits:
    """ What one incoming message is allowed to be and to cost.
    """

    def test_a_part_that_decompresses_past_the_limit_is_refused(self) -> 'None':

        # A part that is small on the wire and decompresses to just past the limit.
        part = new_part(b'a' * (Limits.Max_Decompressed_Size_Bytes + 1))
        compress_part(part)

        assert len(part.data) < 1024 * 1024

        with pytest.raises(AS4ProtocolException) as raised:
            decompress_part(part)

        assert raised.value.error_code == EbMSError.Decompression_Failure

# ################################################################################################################################

    def test_a_part_within_the_limit_decompresses(self) -> 'None':
        part = new_part(Payload)
        compress_part(part)

        decompress_part(part)

        assert part.data == Payload
        assert not part.compressed

# ################################################################################################################################

    def test_too_many_parts_are_refused(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)

        parts = []
        for _ in range(Limits.Max_Part_Count + 1):
            parts.append(new_part(Payload))

        body, content_type, _, _ = build_push_message(pmode, rsa_parties.sender, parts)

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Mime_Inconsistency

# ################################################################################################################################

    def test_a_message_from_outside_the_timestamp_window_is_refused(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_peppol_pmode(rsa_parties)
        parts = [new_part(Payload)]

        # An eb:Timestamp far enough in the past to be outside the window, signed as such, so the
        # message is internally consistent and only the timestamp itself is at issue.
        message_id = new_message_id()

        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, parts, message_id, message_id)

        long_ago = datetime.now(timezone.utc) - timedelta(seconds=Limits.Timestamp_Window_Seconds * 2)

        messaging = find_messaging(envelope)
        timestamp = messaging.find(f'.//{qname(NS.EBMS, "Timestamp")}')
        timestamp.text = to_timestamp(long_ago)

        _ = sign_envelope(envelope, parts, rsa_parties.sender, pmode.security)

        body, content_type = build_multipart(_serialize(envelope), parts)

        result = handle(body, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Value_Inconsistent

# ################################################################################################################################
# ################################################################################################################################

class TestExternalFileFixture:

    def test_the_named_file_really_exists(self, external_file:'str') -> 'None':
        """ The counterpart to the two tests that name this file.
        """
        assert os.path.exists(external_file)

        with open(external_file) as file_:
            contents = file_.read()

        assert contents == External_Text

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone

# lxml
from lxml.etree import fromstring, tostring

# pytest
import pytest

# Zato
from zato.common.b2b.ebms2.common import Actor, EbMS2Exception, ErrorCode, MSHService
from zato.common.b2b.ebms2.header import parse_ack_requested, parse_manifest, parse_message_header, parse_message_order, \
    parse_sync_reply
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope
from zato.common.b2b.ebms2.signals import parse_acknowledgment, parse_error_list, parse_status_request, parse_status_response
from zato.common.b2b.ebms2.xml_ import eb_tag
from zato.common.test.b2b_interoperability import FixtureDirectory, read_header

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.header import Manifest, MessageHeader
    from zato.common.b2b.ebms2.message import MessageElements
    from zato.common.typing_ import any_, strlist
    any_ = any_
    Manifest = Manifest
    MessageElements = MessageElements
    MessageHeader = MessageHeader
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The fixtures whose SOAP part does not parse, with the error code each one is rejected with.
_parse_errors = {
    'acknowledgment-redeclared-namespaces.xml':   ErrorCode.Inconsistent,
    'acknowledgment-two-ref-to-empty-party.xml':  ErrorCode.Inconsistent,
    'envelope-mismatched-end-tag.xml':            ErrorCode.Other_XML,
    'error-list-unprefixed-attributes.xml':       ErrorCode.Inconsistent,
    'request-text-timestamp.xml':                 ErrorCode.Inconsistent,
    'request-unknown-eb-body-elements.xml':       ErrorCode.Not_Supported,
}

# The fixtures that are not valid against the ebMS 2.0 and SOAP 1.1 schemas.
_schema_invalid = {
    'acknowledgment-redeclared-namespaces.xml',
    'acknowledgment-two-ref-to-empty-party.xml',
    'envelope-mismatched-end-tag.xml',
    'error-list-unprefixed-attributes.xml',
    'request-mixed-cid-mid-numeric-id.xml',
    'request-text-timestamp.xml',
    'request-unknown-eb-body-elements.xml',
}

# The ebMS elements of an envelope that the message header schema validates one by one.
_schema_elements = (
    'message_header',
    'ack_requested',
    'sync_reply',
    'message_order',
    'acknowledgment',
    'error_list',
    'manifest',
    'status_request',
    'status_response',
)

_description_tag = eb_tag('Description')

# The directory of the fixtures, which the parametrized tests list when they are collected.
_tests_dir = os.path.dirname(__file__)
_messages_dir = os.path.join(_tests_dir, '..', 'fixtures', 'messages')
_fixture_directory = FixtureDirectory(_messages_dir)
_fixture_name_list = _fixture_directory.names()

# ################################################################################################################################
# ################################################################################################################################

def _parse(data:'bytes') -> 'MessageElements':
    """ Parses a SOAP part with the parser of each ebMS element it contains.
    """
    envelope = parse_envelope(data)
    out = collect_elements(envelope)

    _ = parse_message_header(out.message_header)

    if out.ack_requested is not None:
        _ = parse_ack_requested(out.ack_requested)

    if out.sync_reply is not None:
        parse_sync_reply(out.sync_reply)

    if out.message_order is not None:
        _ = parse_message_order(out.message_order)

    if out.acknowledgment is not None:
        _ = parse_acknowledgment(out.acknowledgment)

    if out.error_list is not None:
        _ = parse_error_list(out.error_list)

    if out.manifest is not None:
        _ = parse_manifest(out.manifest)

    if out.status_request is not None:
        _ = parse_status_request(out.status_request)

    if out.status_response is not None:
        _ = parse_status_response(out.status_response)

    return out

# ################################################################################################################################

def _is_schema_valid(data:'bytes', msg_header_schema:'any_', soap11_schema:'any_') -> 'bool':
    """ Validates the envelope against the SOAP 1.1 schema and each ebMS element, standalone, against the message header schema.
    """
    try:
        envelope = parse_envelope(data)
        elements = collect_elements(envelope)
    except EbMS2Exception:
        return False

    tree = envelope.getroottree()

    if not soap11_schema.validate(tree):
        return False

    for name in _schema_elements:
        if (element := getattr(elements, name)) is not None:
            standalone_data = tostring(element)
            standalone = fromstring(standalone_data)
            if not msg_header_schema.validate(standalone):
                return False

    return True

# ################################################################################################################################

def _manifest(messages:'FixtureDirectory', name:'str') -> 'Manifest':
    data = messages.load(name)
    elements = _parse(data)

    out = parse_manifest(elements.manifest)
    return out

# ################################################################################################################################

def _raw_descriptions(data:'bytes') -> 'strlist':
    """ Returns the text of every eb:Description of a SOAP part as the parser of lxml reads it.
    """
    out:'strlist' = []

    root = fromstring(data)

    for element in root.iter(_description_tag):
        out.append(element.text)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEveryFixture:
    """ Every fixture parses as its feature says, and is schema-valid unless its feature is a schema violation.
    """

    @pytest.mark.parametrize('name', _fixture_name_list)
    def test_parse(self, messages:'FixtureDirectory', name:'str') -> 'None':
        data = messages.load(name)

        if error_code := _parse_errors.get(name):
            with pytest.raises(EbMS2Exception) as info:
                _ = _parse(data)
            assert info.value.error_code == error_code

        else:
            elements = _parse(data)
            assert elements.message_header is not None

    @pytest.mark.parametrize('name', _fixture_name_list)
    def test_schema(self, messages:'FixtureDirectory', name:'str', msg_header_schema:'any_', soap11_schema:'any_') -> 'None':
        data = messages.load(name)

        is_valid = _is_schema_valid(data, msg_header_schema, soap11_schema)
        is_expected_valid = name not in _schema_invalid

        assert is_valid == is_expected_valid

# ################################################################################################################################
# ################################################################################################################################

class TestHeaderForms:
    """ The forms of the MessageHeader values that the fixtures carry.
    """

    def test_timestamp_without_zone_is_utc(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('ping-ack-requested-two-soap-prefixes.xml')
        header = read_header(data)

        expected = datetime(2026, 1, 15, 9, 29, 40, tzinfo=timezone.utc)
        assert header.message_data.timestamp == expected

    def test_timestamp_with_offset_and_milliseconds(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('signed-request-sha1-typed-service.xml')
        header = read_header(data)

        expected = datetime(2026, 1, 15, 9, 29, 26, 652000, tzinfo=timezone.utc)
        assert header.message_data.timestamp == expected

    def test_timestamp_with_seven_fractional_digits(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('signed-request-key-value-empty-x509.xml')
        header = read_header(data)

        expected = datetime(2026, 1, 15, 9, 29, 50, 306947, tzinfo=timezone.utc)
        assert header.message_data.timestamp == expected

    def test_textual_timestamp(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('request-text-timestamp.xml')

        with pytest.raises(EbMS2Exception) as info:
            _ = read_header(data)

        assert info.value.error_code == ErrorCode.Inconsistent

    def test_message_id_with_leading_space(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('signed-request-reference-not-in-manifest.xml')
        header = read_header(data)

        assert header.message_data.message_id == '5150c999-acb2-4c89-9fd5-dfe4d5e1e119'
        assert header.duplicate_elimination

    def test_conversation_id_with_trailing_newline(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('request-roles-service-with-spaces.xml')
        header = read_header(data)

        assert header.conversation_id == 'localconid'
        assert header.service == 'Manage Record Exchange'
        assert header.service_type == 'v4.0'
        assert header.from_party.role == 'Supplier'
        assert header.to_party.role == 'Buyer'
        assert header.message_data.time_to_live == datetime(2026, 1, 15, 10, 29, 30, tzinfo=timezone.utc)

    def test_two_party_ids_with_mixed_case_roles(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('acknowledgment-receipt-references.xml')
        header = read_header(data)

        from_ids:'strlist' = []
        for party_id in header.from_party.party_ids:
            from_ids.append(f'{party_id.id_type}:{party_id.value}')

        assert from_ids == ['REG:52817', 'ORG:600418277']
        assert header.from_party.role == 'SUMMARYreceiver'
        assert header.to_party.role == 'SUMMARYsender'
        assert not header.message_data.ref_to_message_id

    def test_ref_to_message_id_equal_to_own_message_id(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('response-ref-to-own-message-id.xml')
        header = read_header(data)

        message_data = header.message_data

        assert message_data.ref_to_message_id == message_data.message_id
        assert header.conversation_id == message_data.message_id
        assert header.duplicate_elimination

    def test_description_with_structured_text(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('signed-request-sha256-roles.xml')
        header = read_header(data)

        description = header.descriptions[0]

        assert description.language == 'DE'
        assert description.text.startswith('{"handler":"Test Handler"')
        assert header.service_type == 'string'

    def test_untyped_url_service(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('request-url-service-time-to-live.xml')
        header = read_header(data)

        message_data = header.message_data

        assert header.service == 'http://b2b.test/ebms/inbound'
        assert not header.service_type
        assert message_data.time_to_live == message_data.timestamp

    def test_sync_reply_requires_the_next_actor(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('request-sync-reply-typed-service.xml')
        envelope = parse_envelope(data)
        elements = collect_elements(envelope)

        parse_sync_reply(elements.sync_reply)
        ack_requested = elements.ack_requested

        assert ack_requested is None

    def test_ack_requested_without_actor(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('signed-request-reference-not-in-manifest.xml')
        envelope = parse_envelope(data)
        elements = collect_elements(envelope)

        ack_requested = parse_ack_requested(elements.ack_requested)

        assert ack_requested.signed
        assert ack_requested.actor == Actor.To_Party_MSH

    def test_ack_requested_for_next_msh(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('request-mid-references.xml')
        envelope = parse_envelope(data)
        elements = collect_elements(envelope)

        ack_requested = parse_ack_requested(elements.ack_requested)

        assert not ack_requested.signed
        assert ack_requested.actor == Actor.Next_MSH

    def test_same_message_in_three_serializations(self, messages:'FixtureDirectory') -> 'None':
        names = (
            'request-sync-reply-duplicate.xml',
            'request-sync-reply-alternative-serialization.xml',
            'request-soapenv-prefix-encoding-namespaces.xml',
        )

        headers:'list[MessageHeader]' = []
        manifests:'list[Manifest]' = []

        for name in names:
            data = messages.load(name)
            header = read_header(data)
            manifest = _manifest(messages, name)
            headers.append(header)
            manifests.append(manifest)

        first, second, third = headers

        assert first == second
        assert first.message_data == third.message_data
        assert first.from_party == third.from_party
        assert first.to_party == third.to_party
        assert first.service == third.service
        assert first.action == third.action
        assert not third.duplicate_elimination

        for manifest in manifests:
            assert manifest == manifests[0]

# ################################################################################################################################
# ################################################################################################################################

class TestManifestForms:
    """ The references, schemas, descriptions and extension elements of the manifests the fixtures carry.
    """

    def test_extension_children_of_the_manifest(self, messages:'FixtureDirectory') -> 'None':
        manifest = _manifest(messages, 'request-default-service-free-type.xml')

        reference = manifest.references[0]

        assert len(manifest.references) == 1
        assert reference.href == 'cid:records/batch/RecordBatch.xml@node0093.b2b.test'

    def test_extension_element_inside_a_reference(self, messages:'FixtureDirectory') -> 'None':
        manifest = _manifest(messages, 'response-ref-to-own-message-id.xml')

        reference = manifest.references[0]
        schema = reference.schemas[0]
        description = reference.descriptions[0]

        assert schema.location == 'urn:zato:b2b:test:schema:RecordReceipt.xsd'
        assert schema.version == '13'
        assert description.text == 'The record payload'
        assert description.language == 'en'

    def test_reference_role(self, messages:'FixtureDirectory') -> 'None':
        manifest = _manifest(messages, 'signed-request-reference-not-in-manifest.xml')

        reference = manifest.references[0]
        description = reference.descriptions[0]

        assert reference.role == 'XLinkRole'
        assert description.language == 'fi'

    def test_identifier_starting_with_a_digit(self, messages:'FixtureDirectory') -> 'None':
        manifest = _manifest(messages, 'request-mixed-cid-mid-numeric-id.xml')

        identifiers:'strlist' = []
        for reference in manifest.references:
            identifiers.append(reference.reference_id)

        assert identifiers == [
            '',
            'A2AD948E-4091-4686-A8A2-991119B5CCD2',
            '1AB54AF9-243C-4267-8673-FC9069E6E499',
            '9D80B68A-37C4-47A6-8320-E187B76F5AA1',
            '92A86673-1B3D-480C-8278-22C7F2C8E193',
        ]

    def test_multiline_description_is_preserved(self, messages:'FixtureDirectory') -> 'None':
        name = 'request-multiline-description.xml'

        data = messages.load(name)
        manifest = _manifest(messages, name)

        raw_descriptions = _raw_descriptions(data)
        raw_text = raw_descriptions[1]
        reference = manifest.references[1]
        description = reference.descriptions[0]

        lines:'strlist' = []
        for line in description.text.splitlines():
            stripped = line.strip()
            lines.append(stripped)

        assert description.text == raw_text.strip()
        assert lines == [
            'Filename="A379BE92A-FE7B-43C2-89A7-77234AC49187_notes.txt"',
            'ContentType=text/plain',
            'Compressed=No',
            'LargeAttachment=No',
            'OriginalBase64=Yes',
        ]

    def test_description_with_unterminated_quote(self, messages:'FixtureDirectory') -> 'None':
        manifest = _manifest(messages, 'request-mid-xml-attachment.xml')

        reference = manifest.references[1]
        description = reference.descriptions[0]
        last_line = description.text.splitlines()[-1]

        assert reference.href == 'mid:D17A1EB7-CDA6-4FE8-A1A0-3F26D79C9998'
        assert not reference.reference_id
        assert last_line.strip() == 'DomainData="X-Record-Skeleton: Yes'

    def test_message_service_handler_manifest(self, messages:'FixtureDirectory') -> 'None':
        data = messages.load('pong-with-manifest.xml')
        header = read_header(data)
        manifest = _manifest(messages, 'pong-with-manifest.xml')

        assert header.service == MSHService.Service
        assert header.action == MSHService.Pong
        assert manifest.references[0].href == 'cid:statusResponse@relay.b2b.test'

# ################################################################################################################################
# ################################################################################################################################

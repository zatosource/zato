# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
import lxml.etree as etree

# pytest
import pytest

# Zato
from zato.common.soap.common import Must_Understand_Value, NS, SOAPException, SOAPVersion
from zato.common.soap.ebxml import build_message, EbXMLInfo, get_manifest_references, parse_message_header
from zato.common.soap.envelope import build_envelope, get_header, parse_envelope, to_bytes
from zato.common.soap.mtom import build_swa, parse_message
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The party type of the tests - a node code plus a service instance.
_party_type = 'urn:zato:b2b:test:party-type:node+instance'

# ################################################################################################################################
# ################################################################################################################################

def _info():
    """ The addressing details of a business message between two test nodes.
    """

    # Our response to produce
    out = EbXMLInfo()

    out.from_party = 'NODE1-0000123'
    out.from_party_type = _party_type
    out.to_party = 'NODE2-0000456'
    out.to_party_type = _party_type
    out.cpa_id = 'C1001A0042'
    out.conversation_id = 'C9E984B5-2F8C-4A6B-B1D3-DDBB1E9DE988'
    out.service = 'urn:zato:b2b:test:services:records:query'
    out.action = 'RecordQuery_v2'

    return out

# ################################################################################################################################

def _reparse(envelope:'any_'):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMessageHeader:
    """ The ebMS 2.0 MessageHeader, which carries the addressing of every business message.
    """

    def test_header_roundtrip(self):
        envelope = build_message(_info(), [])

        parsed = parse_message_header(_reparse(envelope))

        assert parsed.from_party == 'NODE1-0000123'
        assert parsed.from_party_type == _party_type
        assert parsed.to_party == 'NODE2-0000456'
        assert parsed.cpa_id == 'C1001A0042'
        assert parsed.conversation_id == 'C9E984B5-2F8C-4A6B-B1D3-DDBB1E9DE988'
        assert parsed.service == 'urn:zato:b2b:test:services:records:query'
        assert parsed.action == 'RecordQuery_v2'

    def test_message_id_and_timestamp_are_generated(self):
        envelope = build_message(_info(), [])

        parsed = parse_message_header(_reparse(envelope))

        assert parsed.message_id
        assert parsed.message_id.endswith('@zato')

        message_data = envelope.find(f'.//{qname(NS.EBXML2, "MessageData")}')
        timestamp = message_data.find(qname(NS.EBXML2, 'Timestamp'))
        assert timestamp.text.endswith('Z')

    def test_ref_to_message_id_on_replies(self):
        info = _info()
        info.ref_to_message_id = 'ORIGINAL-ID@b2b.test'

        envelope = build_message(info, [])
        parsed = parse_message_header(_reparse(envelope))

        assert parsed.ref_to_message_id == 'ORIGINAL-ID@b2b.test'

    def test_header_is_soap11_and_must_understand(self):
        # ebMS 2.0 is bound to SOAP 1.1.
        envelope = build_message(_info(), [])

        assert envelope.tag == f'{{{NS.SOAP11}}}Envelope'

        header = get_header(envelope)
        message_header = header.find(qname(NS.EBXML2, 'MessageHeader'))

        must_understand = message_header.get(qname(NS.SOAP11, 'mustUnderstand'))
        assert must_understand == Must_Understand_Value[SOAPVersion.V11]
        assert message_header.get(qname(NS.EBXML2, 'version')) == '2.0'

    def test_missing_header_is_rejected(self):
        envelope = build_envelope(SOAPVersion.V11)

        with pytest.raises(SOAPException):
            _ = parse_message_header(envelope)

# ################################################################################################################################
# ################################################################################################################################

class TestManifestAndSwA:
    """ The Manifest plus SwA packaging - the payload travels as a MIME part
    that the Manifest of the body references, as ebMS 2.0 defines it.
    """

    def test_manifest_references_each_part(self):
        part = Part()
        part.content_id = new_content_id('b2b.test')
        part.content_type = 'text/xml'
        part.data = b'<RecordQuery>record query</RecordQuery>'

        envelope = build_message(_info(), [part])

        references = get_manifest_references(envelope)
        assert references == [part.content_id]

    def test_swa_packaging_roundtrip(self):
        part = Part()
        part.content_id = new_content_id('b2b.test')
        part.content_type = 'text/xml'
        part.data = b'<RecordQuery>record query</RecordQuery>'

        envelope = build_message(_info(), [part])
        body, content_type = build_swa(to_bytes(envelope), [part], SOAPVersion.V11)

        # The other side unpacks the multipart and follows the manifest to the payload.
        envelope_bytes, parts = parse_message(body, content_type)
        received = parse_envelope(envelope_bytes)

        parsed = parse_message_header(received)
        assert parsed.action == 'RecordQuery_v2'

        references = get_manifest_references(received)
        assert len(parts) == 1
        assert parts[0].content_id == references[0]
        assert parts[0].data == part.data

    def test_no_manifest_without_parts(self):
        envelope = build_message(_info(), [])

        references = get_manifest_references(envelope)
        assert references == []

# ################################################################################################################################
# ################################################################################################################################

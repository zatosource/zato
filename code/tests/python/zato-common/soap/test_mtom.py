# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.soap.common import Content_Type, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, parse_body, parse_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.mtom import build_mtom, build_swa, parse_message, to_bytes_map
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################
# ################################################################################################################################

# The IHE XDS.b submission namespace - ITI-41 Provide and Register
# "shall use SOAP 1.2 and MTOM with XOP encoding" per the IHE ITI framework.
_ns_xds = 'urn:ihe:iti:xds-b:2007'

# A stand-in clinical document.
_document = b'%PDF-1.7 discharge summary bytes'

# ################################################################################################################################
# ################################################################################################################################

class TestMTOM:
    """ MTOM/XOP packaging as IHE XDS ITI-41 requires - TEFCA, the German ePA
    and the Swiss EPD all submit documents this way.
    """

    def test_document_becomes_a_part(self):
        request = SOAPMessage()
        request.namespace = _ns_xds
        request.SubmitObjectsRequest = 'metadata'
        request.Document = _document

        envelope = build_envelope(SOAPVersion.V12)

        xop_parts = []
        _ = attach_body(envelope, request, 'ProvideAndRegisterDocumentSetRequest', xop_parts=xop_parts)

        # The bytes moved into a MIME part instead of inline base64.
        assert len(xop_parts) == 1
        assert xop_parts[0].data == _document

        wire = to_bytes(envelope)
        assert _document not in wire
        assert b'Include' in wire

    def test_mtom_roundtrip(self):
        request = SOAPMessage()
        request.namespace = _ns_xds
        request.SubmitObjectsRequest = 'metadata'
        request.Document = _document

        envelope = build_envelope(SOAPVersion.V12)

        xop_parts = []
        _ = attach_body(envelope, request, 'ProvideAndRegisterDocumentSetRequest', xop_parts=xop_parts)

        body, content_type = build_mtom(to_bytes(envelope), xop_parts, SOAPVersion.V12)

        assert 'multipart/related' in content_type
        assert 'application/xop+xml' in content_type
        assert 'start-info="application/soap+xml' in content_type

        # The other side unpacks the multipart and resolves the xop:Include back to bytes.
        envelope_bytes, parts = parse_message(body, content_type)
        parsed_envelope = parse_envelope(envelope_bytes)
        parsed_body = parse_body(parsed_envelope, to_bytes_map(parts))

        request_out = parsed_body.ProvideAndRegisterDocumentSetRequest
        assert request_out.SubmitObjectsRequest == 'metadata'
        assert request_out.Document == _document

    def test_bytes_stay_inline_without_a_collector(self):
        request = SOAPMessage()
        request.namespace = _ns_xds
        request.Document = _document

        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, request, 'ProvideAndRegisterDocumentSetRequest')

        # Without MTOM the bytes travel as inline base64.
        wire = to_bytes(envelope)
        assert b'Include' not in wire

# ################################################################################################################################
# ################################################################################################################################

class TestSwA:
    """ SOAP with Attachments packaging - the NHS Spine and Norway Helsenett
    carry their ebXML payloads this way.
    """

    def test_swa_roundtrip(self):
        part = Part()
        part.content_id = new_content_id()
        part.content_type = 'text/xml'
        part.data = b'<ClinicalDocument>referral</ClinicalDocument>'

        envelope = build_envelope(SOAPVersion.V11)
        body, content_type = build_swa(to_bytes(envelope), [part], SOAPVersion.V11)

        assert 'multipart/related' in content_type
        assert 'type="text/xml"' in content_type

        envelope_bytes, parts = parse_message(body, content_type)

        _ = parse_envelope(envelope_bytes)
        assert len(parts) == 1
        assert parts[0].content_id == part.content_id
        assert parts[0].data == part.data

# ################################################################################################################################
# ################################################################################################################################

class TestBareEnvelope:

    def test_bare_envelope_passthrough(self):
        envelope = build_envelope(SOAPVersion.V12)
        wire = to_bytes(envelope)

        envelope_bytes, parts = parse_message(wire, Content_Type[SOAPVersion.V12])

        assert envelope_bytes == wire
        assert parts == []

# ################################################################################################################################
# ################################################################################################################################

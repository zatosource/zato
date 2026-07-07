# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.soap.common import Content_Type, FaultCode, NS, SOAPFault, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, get_body, get_header, get_version, \
    parse_body, parse_envelope, parse_fault, raise_for_fault, to_bytes
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

# The CDC IIS transport namespace.
_ns_cdc = 'urn:cdc:iisb:2011'

# ################################################################################################################################
# ################################################################################################################################

class TestEnvelopes:

    def test_soap12_envelope(self):
        # The CDC IIS spec: "The Sender and Receiver SHALL conform to SOAP 1.2 over HTTPS".
        envelope = build_envelope(SOAPVersion.V12)

        assert envelope.tag == f'{{{NS.SOAP12}}}Envelope'
        assert get_version(envelope) == SOAPVersion.V12
        assert Content_Type[SOAPVersion.V12] == 'application/soap+xml; charset=utf-8'

    def test_soap11_envelope(self):
        # NHS Spine ebXML and Norway Helsenett run on SOAP 1.1.
        envelope = build_envelope(SOAPVersion.V11)

        assert envelope.tag == f'{{{NS.SOAP11}}}Envelope'
        assert get_version(envelope) == SOAPVersion.V11
        assert Content_Type[SOAPVersion.V11] == 'text/xml; charset=utf-8'

    def test_header_and_body_are_present(self):
        envelope = build_envelope(SOAPVersion.V12)

        header = get_header(envelope)
        body = get_body(envelope)

        assert header.tag == f'{{{NS.SOAP12}}}Header'
        assert body.tag == f'{{{NS.SOAP12}}}Body'

    def test_body_roundtrip_over_the_wire(self):
        # A CDC IIS submission in a 1.2 envelope, serialized and parsed back.
        request = SOAPMessage()
        request.namespace = _ns_cdc
        request.username = 'MYUSERNAME'
        request.password = 'MYPASSWORD'
        request.hl7Message = 'MSH|^~\\&|MYEHR|MYCLINIC'

        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, request, 'submitSingleMessage')

        wire = to_bytes(envelope)
        parsed = parse_envelope(wire)
        body = parse_body(parsed)

        assert body.submitSingleMessage.username == 'MYUSERNAME'
        assert body.submitSingleMessage.hl7Message == 'MSH|^~\\&|MYEHR|MYCLINIC'

    def test_non_envelope_is_rejected(self):
        with pytest.raises(Exception):
            _ = parse_envelope(b'<NotAnEnvelope/>')

# ################################################################################################################################
# ################################################################################################################################

class TestFaults:

    def test_soap12_fault(self):
        # The CDC IIS spec defines four SOAP 1.2 faults - a security fault is one of them.
        detail = SOAPMessage()
        detail.namespace = _ns_cdc
        detail.SecurityFault.Code = '4'
        detail.SecurityFault.Reason = 'Security'

        envelope = build_fault(SOAPVersion.V12, FaultCode.Sender, 'Invalid credentials', detail)

        fault = parse_fault(envelope)

        assert fault.code == 'Sender'
        assert fault.reason == 'Invalid credentials'
        assert fault.detail.SecurityFault.Code == '4'

    def test_soap11_fault(self):
        envelope = build_fault(SOAPVersion.V11, FaultCode.Receiver, 'Internal error')

        fault = parse_fault(envelope)

        # The version-independent Receiver maps to Server in the 1.1 dialect.
        assert fault.code == 'Server'
        assert fault.reason == 'Internal error'

    def test_raise_for_fault(self):
        envelope = build_fault(SOAPVersion.V12, FaultCode.Sender, 'Unsupported operation')

        with pytest.raises(SOAPFault) as exc:
            raise_for_fault(envelope)

        assert exc.value.reason == 'Unsupported operation'

    def test_no_fault_means_no_exception(self):
        envelope = build_envelope(SOAPVersion.V12)

        assert parse_fault(envelope) is None
        raise_for_fault(envelope)

    def test_fault_roundtrip_over_the_wire(self):
        envelope = build_fault(SOAPVersion.V12, FaultCode.Sender, 'Message too large')

        wire = to_bytes(envelope)
        parsed = parse_envelope(wire)

        fault = parse_fault(parsed)
        assert fault.code == 'Sender'
        assert fault.reason == 'Message too large'

# ################################################################################################################################
# ################################################################################################################################

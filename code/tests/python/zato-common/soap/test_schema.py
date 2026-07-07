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
from zato.common.soap.addressing import add_addressing, AddressingInfo
from zato.common.soap.common import FaultCode, SOAPVersion
from zato.common.soap.ebxml import build_message, EbXMLInfo
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################
# ################################################################################################################################

# Every namespace and identifier below is typed out literally from the governing
# specification, never imported from the code under test - the expected values
# come from the specs, the actual ones from the wire.

# SOAP 1.1 and 1.2 (W3C)
_soap11 = '{http://schemas.xmlsoap.org/soap/envelope/}'
_soap12 = '{http://www.w3.org/2003/05/soap-envelope}'

# WS-Addressing 1.0 (W3C Recommendation), including its anonymous address.
_wsa = '{http://www.w3.org/2005/08/addressing}'
_wsa_anonymous = 'http://www.w3.org/2005/08/addressing/anonymous'

# XOP - XML-binary Optimized Packaging (W3C Recommendation)
_xop = '{http://www.w3.org/2004/08/xop/include}'

# ebXML Message Service 2.0 (OASIS Standard)
_eb = '{http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd}'

# ################################################################################################################################
# ################################################################################################################################

def _cdc_request():
    """ A CDC IIS submission message.
    """

    # Our response to produce
    out = SOAPMessage()

    out.namespace = 'urn:cdc:iisb:2011'
    out.username = 'MYUSERNAME'
    out.password = 'MYPASSWORD'
    out.hl7Message = 'MSH|^~\\&|MYEHR|MYCLINIC'

    return out

# ################################################################################################################################

def _reparse(envelope):
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSchemaConformance:
    """ Everything the library produces must validate against the official W3C schemas -
    proven here so that no schema machinery is ever needed at runtime.
    """

    def test_soap12_envelope_validates(self, soap12_schema):
        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap11_envelope_validates(self, soap11_schema):
        envelope = build_envelope(SOAPVersion.V11)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap11_schema.assertValid(_reparse(envelope))

    def test_soap12_envelope_with_addressing_validates(self, soap12_schema):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = 'urn:cdc:iisb:2011:submitSingleMessage'
        info.to = 'https://iis.example.gov/soap'

        add_addressing(envelope, info)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap12_fault_validates(self, soap12_schema):
        envelope = build_fault(SOAPVersion.V12, FaultCode.Sender, 'Invalid credentials')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap11_fault_validates(self, soap11_schema):
        envelope = build_fault(SOAPVersion.V11, FaultCode.Receiver, 'Internal error')

        soap11_schema.assertValid(_reparse(envelope))

# ################################################################################################################################
# ################################################################################################################################

class TestAddressingConformance:
    """ WS-Addressing 1.0 - every header block the library produces validates
    against the official W3C schema, element by element.
    """

    def _addressed_wire(self):
        """ An IHE XCA style request carrying the full set of addressing headers.
        """
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = 'urn:ihe:iti:2007:CrossGatewayQuery'
        info.to = 'https://qhin.example.gov/xca/query'
        info.reply_to = _wsa_anonymous
        info.relates_to = 'urn:uuid:11111111-2222-3333-4444-555555555555'

        add_addressing(envelope, info)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        out = _reparse(envelope)
        return out

    def test_each_header_block_validates(self, wsa_schema):
        wire = self._addressed_wire()
        header = wire.find(f'{_soap12}Header')

        header_blocks = [element for element in header if element.tag.startswith(_wsa)]
        local_names = {etree.QName(element).localname for element in header_blocks}

        # All of these are global element declarations in the official schema,
        # so each one validates as a document in its own right.
        assert {'Action', 'To', 'MessageID', 'ReplyTo', 'RelatesTo'} <= local_names

        for element in header_blocks:
            wsa_schema.assertValid(deepcopy(element))

    def test_reply_to_is_an_endpoint_reference(self):
        wire = self._addressed_wire()

        # The core spec models ReplyTo as an EndpointReference whose required
        # Address child here carries the spec's own anonymous URI.
        address = wire.find(f'.//{_wsa}ReplyTo/{_wsa}Address')

        assert address is not None
        assert address.text == _wsa_anonymous

# ################################################################################################################################
# ################################################################################################################################

class TestXOPConformance:
    """ XOP - the optimized-content placeholder validates against the official
    W3C schema and references its MIME part the way the recommendation says.
    """

    def _optimized_wire(self):
        """ An IHE XDS.b style submission with one optimized document,
        returned along with the collected MTOM parts.
        """
        request = SOAPMessage()
        request.namespace = 'urn:ihe:iti:xds-b:2007'
        request.SubmitObjectsRequest = 'metadata'
        request.Document = b'%PDF-1.7 discharge summary bytes'

        envelope = build_envelope(SOAPVersion.V12)

        xop_parts = []
        _ = attach_body(envelope, request, 'ProvideAndRegisterDocumentSetRequest', xop_parts=xop_parts)

        out = _reparse(envelope)
        return out, xop_parts

    def test_include_validates_against_the_official_schema(self, xop_schema):
        wire, _ = self._optimized_wire()

        include = wire.find(f'.//{_xop}Include')
        assert include is not None

        xop_schema.assertValid(deepcopy(include))

    def test_href_is_a_cid_uri_matching_the_part(self):
        wire, xop_parts = self._optimized_wire()

        include = wire.find(f'.//{_xop}Include')
        href = include.get('href')

        # The recommendation requires a cid URL resolving to the part's Content-ID.
        assert href.startswith('cid:')
        assert href[4:] == xop_parts[0].content_id

    def test_optimized_envelope_validates(self, soap12_schema):
        wire, _ = self._optimized_wire()

        soap12_schema.assertValid(wire)

# ################################################################################################################################
# ################################################################################################################################

class TestEbXMLConformance:
    """ ebXML Message Service 2.0 - the MessageHeader and Manifest validate
    against the official OASIS schema and the whole message stays valid SOAP 1.1.
    """

    def _spine_wire(self):
        """ An NHS Spine style message with one SwA payload part.
        """
        info = EbXMLInfo()

        info.from_party = 'A1234-0000123'
        info.from_party_type = 'urn:nhs:names:partyType:ocs+serviceInstance'
        info.to_party = 'B5678-0000456'
        info.to_party_type = 'urn:nhs:names:partyType:ocs+serviceInstance'
        info.cpa_id = 'S1001A1234'
        info.conversation_id = 'C9E984B5-2F8C-4A6B-B1D3-DDBB1E9DE988'
        info.service = 'urn:nhs:names:services:pdsquery'
        info.action = 'QUPA_IN000006UK02'

        part = Part()
        part.content_id = new_content_id('spine')
        part.content_type = 'text/xml'
        part.data = b'<QUPA_IN000006UK02>patient query</QUPA_IN000006UK02>'

        envelope = build_message(info, [part])

        out = _reparse(envelope)
        return out

    def test_message_header_validates(self, ebms2_schema):
        wire = self._spine_wire()

        message_header = wire.find(f'{_soap11}Header/{_eb}MessageHeader')
        assert message_header is not None

        ebms2_schema.assertValid(deepcopy(message_header))

    def test_manifest_validates(self, ebms2_schema):
        wire = self._spine_wire()

        manifest = wire.find(f'{_soap11}Body/{_eb}Manifest')
        assert manifest is not None

        ebms2_schema.assertValid(deepcopy(manifest))

    def test_envelope_validates(self, soap11_schema):
        wire = self._spine_wire()

        soap11_schema.assertValid(wire)

# ################################################################################################################################
# ################################################################################################################################

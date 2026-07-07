# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo
from zato.common.soap.common import FaultCode, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, to_bytes
from zato.common.soap.message import SOAPMessage

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

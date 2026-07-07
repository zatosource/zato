# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo, Anonymous_Address, new_message_id, parse_addressing
from zato.common.soap.common import Must_Understand_Value, NS, SOAPVersion
from zato.common.soap.envelope import build_envelope, get_header, to_bytes
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

# The IHE XCA cross-gateway query action - what TEFCA QHINs dispatch on.
_action_xca_query = 'urn:ihe:iti:2007:CrossGatewayQuery'

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAddressing:

    def test_xca_query_headers(self):
        # An IHE XCA query the way the TEFCA QTF requires - SOAP 1.2 with WS-Addressing.
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query
        info.to = 'https://qhin.example.gov/xca/query'
        info.reply_to = Anonymous_Address

        add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.action == _action_xca_query
        assert parsed.to == 'https://qhin.example.gov/xca/query'
        assert parsed.reply_to == Anonymous_Address

    def test_message_id_is_generated(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.message_id.startswith('urn:uuid:')

        # The generated id is also written back into the input info.
        assert parsed.message_id == info.message_id

    def test_relates_to_on_responses(self):
        request_message_id = new_message_id()

        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = 'urn:ihe:iti:2007:CrossGatewayQueryResponse'
        info.relates_to = request_message_id

        add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.relates_to == request_message_id

    def test_action_is_must_understand(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        add_addressing(envelope, info)

        header = get_header(envelope)
        action = header.find(qname(NS.WSA, 'Action'))

        must_understand = action.get(qname(NS.SOAP12, 'mustUnderstand'))
        assert must_understand == Must_Understand_Value[SOAPVersion.V12]

    def test_absent_headers_stay_none(self):
        envelope = build_envelope(SOAPVersion.V12)

        parsed = parse_addressing(envelope)

        assert parsed.action is None
        assert parsed.to is None
        assert parsed.message_id is None
        assert parsed.reply_to is None
        assert parsed.relates_to is None
        assert parsed.fault_to is None

# ################################################################################################################################
# ################################################################################################################################

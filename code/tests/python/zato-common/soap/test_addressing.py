# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo, Anonymous_Address, new_message_id, parse_addressing
from zato.common.soap.common import Must_Understand_Value, NS, SOAPAddressingException, SOAPVersion
from zato.common.soap.envelope import build_envelope, get_header, to_bytes
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The IHE XCA cross-gateway query action - what TEFCA QHINs dispatch on.
_action_xca_query = 'urn:ihe:iti:2007:CrossGatewayQuery'

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope:'any_'):
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

        _ = add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.action == _action_xca_query
        assert parsed.to == 'https://qhin.example.gov/xca/query'
        assert parsed.reply_to == Anonymous_Address

    def test_message_id_is_generated(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        message_id = add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.message_id.startswith('urn:uuid:')

        # The generated id comes back to the caller ..
        assert parsed.message_id == message_id

        # .. and the caller's own info is left alone, so reusing it for a second message
        # does not send that one under the first message's id.
        assert info.message_id is None

    def test_reused_info_gets_a_fresh_message_id(self):
        info = AddressingInfo()
        info.action = _action_xca_query

        first = add_addressing(build_envelope(SOAPVersion.V12), info)
        second = add_addressing(build_envelope(SOAPVersion.V12), info)

        assert first != second

    def test_action_is_required(self):
        envelope = build_envelope(SOAPVersion.V12)

        with pytest.raises(SOAPAddressingException):
            _ = add_addressing(envelope, AddressingInfo())

    def test_addressing_is_not_added_twice(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        _ = add_addressing(envelope, info)

        with pytest.raises(SOAPAddressingException):
            _ = add_addressing(envelope, info)

    def test_duplicate_header_is_refused(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        _ = add_addressing(envelope, info)

        # A second Action lets a sender show one action to whatever inspects the message
        # and have the receiver dispatch on the other.
        header = get_header(envelope)
        duplicate = etree.SubElement(header, qname(NS.WSA, 'Action'))
        duplicate.text = 'urn:ihe:iti:2007:SomethingElse'

        with pytest.raises(SOAPAddressingException):
            _ = parse_addressing(_reparse(envelope))

    def test_reply_endpoint_without_message_id_is_refused(self):
        envelope = build_envelope(SOAPVersion.V12)
        header = get_header(envelope)

        action = etree.SubElement(header, qname(NS.WSA, 'Action'))
        action.text = _action_xca_query

        reply_to = etree.SubElement(header, qname(NS.WSA, 'ReplyTo'))
        address = etree.SubElement(reply_to, qname(NS.WSA, 'Address'))
        address.text = Anonymous_Address

        with pytest.raises(SOAPAddressingException):
            _ = parse_addressing(_reparse(envelope))

    def test_addressing_without_action_is_refused(self):
        envelope = build_envelope(SOAPVersion.V12)
        header = get_header(envelope)

        message_id = etree.SubElement(header, qname(NS.WSA, 'MessageID'))
        message_id.text = new_message_id()

        with pytest.raises(SOAPAddressingException):
            _ = parse_addressing(_reparse(envelope))

    def test_relates_to_on_responses(self):
        request_message_id = new_message_id()

        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = 'urn:ihe:iti:2007:CrossGatewayQueryResponse'
        info.relates_to = request_message_id

        _ = add_addressing(envelope, info)

        parsed = parse_addressing(_reparse(envelope))

        assert parsed.relates_to == request_message_id

    def test_action_is_must_understand(self):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = _action_xca_query

        _ = add_addressing(envelope, info)

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

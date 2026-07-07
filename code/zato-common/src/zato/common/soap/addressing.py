# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from uuid import uuid4

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS
from zato.common.soap.envelope import get_header, get_version, set_must_understand
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    any_ = any_
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The anonymous address means the reply travels back on the same HTTP connection.
Anonymous_Address = 'http://www.w3.org/2005/08/addressing/anonymous'

_wsa_nsmap = {
    'wsa': NS.WSA,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AddressingInfo:
    """ The WS-Addressing headers of a message, either to be added to an outgoing one
    or as read from an incoming one.
    """
    action:     'strnone' = None
    to:         'strnone' = None
    message_id: 'strnone' = None
    reply_to:   'strnone' = None
    relates_to: 'strnone' = None
    fault_to:   'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def new_message_id() -> 'str':
    """ Returns a fresh wsa:MessageID in the urn:uuid form WS-Addressing recommends.
    """
    out = f'urn:uuid:{uuid4()}'
    return out

# ################################################################################################################################

def _add_text_header(header:'any_', tag:'str', value:'str') -> 'any_':
    """ Adds one text-carrying wsa header block to a Header element.
    """
    element = etree.SubElement(header, qname(NS.WSA, tag), nsmap=_wsa_nsmap)
    element.text = value

    return element

# ################################################################################################################################

def add_addressing(envelope:'any_', info:'AddressingInfo', needs_must_understand:'bool'=True) -> 'None':
    """ Adds the WS-Addressing header blocks an outgoing message needs. The Action header
    is required, everything else is added only when set. A missing MessageID is generated.
    """
    version = get_version(envelope)
    header = get_header(envelope)

    # Action is what routers and receivers dispatch on, so it is always present ..
    action = _add_text_header(header, 'Action', info.action)

    # .. and it is the one block marked mustUnderstand when the caller wants that.
    if needs_must_understand:
        set_must_understand(action, version)

    if info.to:
        _ = _add_text_header(header, 'To', info.to)

    # Request-reply exchanges need a MessageID for the reply to relate to.
    if not info.message_id:
        info.message_id = new_message_id()

    _ = _add_text_header(header, 'MessageID', info.message_id)

    if info.reply_to:
        reply_to = etree.SubElement(header, qname(NS.WSA, 'ReplyTo'), nsmap=_wsa_nsmap)
        address = etree.SubElement(reply_to, qname(NS.WSA, 'Address'))
        address.text = info.reply_to

    if info.fault_to:
        fault_to = etree.SubElement(header, qname(NS.WSA, 'FaultTo'), nsmap=_wsa_nsmap)
        address = etree.SubElement(fault_to, qname(NS.WSA, 'Address'))
        address.text = info.fault_to

    if info.relates_to:
        _ = _add_text_header(header, 'RelatesTo', info.relates_to)

# ################################################################################################################################

def _find_text(header:'any_', tag:'str') -> 'strnone':
    """ Returns the text of one wsa header block, or None when the block is absent.
    """
    element = header.find(qname(NS.WSA, tag))

    if element is None:
        out = None
    else:
        out = element.text

    return out

# ################################################################################################################################

def _find_address(header:'any_', tag:'str') -> 'strnone':
    """ Returns the wsa:Address text of an endpoint-reference block such as ReplyTo, or None.
    """
    element = header.find(qname(NS.WSA, tag))

    if element is None:
        out = None
    else:
        address = element.find(qname(NS.WSA, 'Address'))
        if address is None:
            out = None
        else:
            out = address.text

    return out

# ################################################################################################################################

def parse_addressing(envelope:'any_') -> 'AddressingInfo':
    """ Reads the WS-Addressing headers of an incoming message. Absent headers stay None.
    """
    header = get_header(envelope)

    # Our response to produce
    out = AddressingInfo()

    out.action     = _find_text(header, 'Action')
    out.to         = _find_text(header, 'To')
    out.message_id = _find_text(header, 'MessageID')
    out.relates_to = _find_text(header, 'RelatesTo')
    out.reply_to   = _find_address(header, 'ReplyTo')
    out.fault_to   = _find_address(header, 'FaultTo')

    return out

# ################################################################################################################################
# ################################################################################################################################

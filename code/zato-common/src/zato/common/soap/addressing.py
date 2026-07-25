# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS, SOAPAddressingException
from zato.common.soap.envelope import find_header, get_header, get_version, set_must_understand
from zato.common.util.xml_.core import new_uuid_urn, qname

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

# The header blocks WS-Addressing 1.0 allows at most once in a message. RelatesTo is deliberately
# absent - a message may relate to several others, so it is the one block that repeats legitimately.
_Single_Occurrence_Headers = (
    'Action',
    'To',
    'MessageID',
    'ReplyTo',
    'FaultTo',
    'From',
)

# The blocks whose presence makes a MessageID mandatory. Both name somewhere a reply is to be sent,
# and a reply has nothing to put in its RelatesTo without a MessageID to relate to.
_Reply_Endpoint_Headers = (
    'ReplyTo',
    'FaultTo',
)

# The fault subcodes WS-Addressing 1.0 defines for the two things that can be wrong with an
# addressing header - one is present but malformed, or a required one is missing altogether.
Fault_Invalid_Addressing_Header = 'InvalidAddressingHeader'
Fault_Message_Addressing_Header_Required = 'MessageAddressingHeaderRequired'

# The subcode refining an InvalidAddressingHeader fault when a block appears more times than once.
Fault_Invalid_Cardinality = 'InvalidCardinality'

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
    out = new_uuid_urn()
    return out

# ################################################################################################################################

def _add_text_header(header:'any_', tag:'str', value:'str') -> 'any_':
    """ Adds one text-carrying wsa header block to a Header element.
    """
    element = etree.SubElement(header, qname(NS.WSA, tag), nsmap=_wsa_nsmap)
    element.text = value

    return element

# ################################################################################################################################

def _has_addressing(header:'any_') -> 'bool':
    """ Says whether a header carries any WS-Addressing block at all.
    """
    for child in header:

        # Comments and processing instructions carry a callable tag rather than a string one.
        if not isinstance(child.tag, str):
            continue

        namespace, _, _ = child.tag.rpartition('}')

        if namespace[1:] == NS.WSA:
            return True

    return False

# ################################################################################################################################

def add_addressing(envelope:'any_', info:'AddressingInfo', needs_must_understand:'bool'=True) -> 'str':
    """ Adds the WS-Addressing header blocks an outgoing message needs. The Action header
    is required, everything else is added only when set. A missing MessageID is generated.

    Returns the MessageID the message went out with, so a caller waiting for a correlated reply has
    it without having to read it back out of the envelope.
    """
    version = get_version(envelope)
    header = get_header(envelope)

    # An addressed message with no action is not addressed - a receiver has nothing to dispatch on,
    # and the empty Action element that used to go out instead looks valid while meaning nothing.
    if not info.action:
        raise SOAPAddressingException('WS-Addressing requires an action', [
            qname(NS.WSA, Fault_Message_Addressing_Header_Required),
        ])

    # A second call would otherwise append a second full set of blocks, and a message carrying two
    # of each is one this node would itself refuse on the way in.
    if _has_addressing(header):
        raise SOAPAddressingException('Message already carries WS-Addressing headers', [
            qname(NS.WSA, Fault_Invalid_Addressing_Header),
            qname(NS.WSA, Fault_Invalid_Cardinality),
        ])

    # Action is what routers and receivers dispatch on, so it is always present ..
    action = _add_text_header(header, 'Action', info.action)

    # .. and it is the one block marked mustUnderstand when the caller wants that.
    if needs_must_understand:
        set_must_understand(action, version)

    if info.to:
        _ = _add_text_header(header, 'To', info.to)

    # Request-reply exchanges need a MessageID for the reply to relate to. The generated one is
    # returned rather than written back into the caller's own dataclass - a caller that reuses one
    # AddressingInfo for several messages would otherwise send them all under the first id.
    message_id = info.message_id

    if not message_id:
        message_id = new_message_id()

    _ = _add_text_header(header, 'MessageID', message_id)

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

    out = message_id
    return out

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

def _check_cardinality(header:'any_') -> 'None':
    """ Raises when a header block WS-Addressing allows at most once appears more than once.

    A duplicate is not a harmless oddity: two Action blocks let a sender show one action to whatever
    inspects the message on the way in and have the receiver dispatch on the other, depending on
    which of the two each side happens to read first.
    """
    for tag in _Single_Occurrence_Headers:
        found = header.findall(qname(NS.WSA, tag))

        if len(found) > 1:
            reason = f'WS-Addressing header appears {len(found)} times -> wsa:{tag}'
            raise SOAPAddressingException(reason, [
                qname(NS.WSA, Fault_Invalid_Addressing_Header),
                qname(NS.WSA, Fault_Invalid_Cardinality),
            ])

# ################################################################################################################################

def _check_required(header:'any_', info:'AddressingInfo') -> 'None':
    """ Raises when a header block the message needs is missing.

    Action is required in every message that uses addressing at all - it is what a receiver
    dispatches on, and the specification names it as the one block with no default. A MessageID is
    required once the message names anywhere for a reply to go, since the reply's RelatesTo has
    nothing to carry otherwise.
    """
    if not info.action:
        raise SOAPAddressingException('WS-Addressing message has no wsa:Action', [
            qname(NS.WSA, Fault_Message_Addressing_Header_Required),
        ])

    if info.message_id:
        return

    for tag in _Reply_Endpoint_Headers:
        if header.find(qname(NS.WSA, tag)) is not None:
            reason = f'WS-Addressing wsa:{tag} is present without a wsa:MessageID'
            raise SOAPAddressingException(reason, [
                qname(NS.WSA, Fault_Message_Addressing_Header_Required),
            ])

# ################################################################################################################################

def parse_addressing(envelope:'any_') -> 'AddressingInfo':
    """ Reads the WS-Addressing headers of an incoming message. Absent headers stay None.

    A message carrying no addressing at all is left alone - addressing is optional, and a channel
    that requires it says so through its own configuration rather than through this function. A
    message that does carry addressing is validated, because half-formed addressing is worse than
    none: the sender believes it asked for something the receiver never saw.
    """
    header = find_header(envelope)

    # Our response to produce
    out = AddressingInfo()

    # A message with no header carries no addressing, so there is nothing to read or to check.
    if header is None:
        return out

    out.action     = _find_text(header, 'Action')
    out.to         = _find_text(header, 'To')
    out.message_id = _find_text(header, 'MessageID')
    out.relates_to = _find_text(header, 'RelatesTo')
    out.reply_to   = _find_address(header, 'ReplyTo')
    out.fault_to   = _find_address(header, 'FaultTo')

    # Absent addressing is not the same thing as broken addressing - only a message that used
    # addressing has anything to answer for.
    if _has_addressing(header):
        _check_cardinality(header)
        _check_required(header, out)

    return out

# ################################################################################################################################
# ################################################################################################################################

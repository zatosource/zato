# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.b2b.ebms2.common import Actor, EbMS2Exception, ErrorCode, NS
from zato.common.b2b.ebms2.xml_ import location, Must_Understand_Value, SOAP_Actor, SOAP_Must_Understand
from zato.common.soap.common import SOAPException, SOAPVersion
from zato.common.soap.envelope import build_envelope, find_header, get_body, get_header, get_version, to_bytes
from zato.common.util.xml_.core import parse_xml, qname, XMLException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict, strset
    any_ = any_
    anytuple = anytuple
    stranydict = stranydict
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_ds_signature = qname(NS.DS, 'Signature')

_eb_prefix = f'{{{NS.EB}}}'

_message_header_location = location('MessageHeader')

# The ebMS header blocks and body elements a message may have, each at most once.
_header_block_names:'strset' = {'MessageHeader', 'AckRequested', 'SyncReply', 'MessageOrder', 'Acknowledgment', 'ErrorList'}
_body_element_names:'strset' = {'Manifest', 'StatusRequest', 'StatusResponse'}

# The actors of the header blocks that this node processes - a block with no actor is for this node too.
_own_actors:'strset' = {Actor.Next_MSH, Actor.To_Party_MSH, Actor.SOAP_Next}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessageElements:
    """ The ebMS header blocks and body elements of a received envelope, each one an element or None.
    """
    envelope: 'any_'

    message_header: 'any_' = None
    ack_requested:  'any_' = None
    sync_reply:     'any_' = None
    message_order:  'any_' = None
    acknowledgment: 'any_' = None
    error_list:     'any_' = None
    signature:      'any_' = None

    manifest:        'any_' = None
    status_request:  'any_' = None
    status_response: 'any_' = None

# ################################################################################################################################
# ################################################################################################################################

def new_envelope() -> 'anytuple':
    """ Returns a new SOAP 1.1 envelope with its Header and its Body.
    """
    envelope = build_envelope(SOAPVersion.V11)
    soap_header = get_header(envelope)
    soap_body = get_body(envelope)

    out = (envelope, soap_header, soap_body)
    return out

# ################################################################################################################################

def serialize(envelope:'any_') -> 'bytes':
    out = to_bytes(envelope)
    return out

# ################################################################################################################################

def parse_envelope(data:'bytes') -> 'any_':
    """ Parses the SOAP part of a message, which is to be a SOAP 1.1 envelope.
    """
    try:
        out = parse_xml(data)
        version = get_version(out)
    except (XMLException, SOAPException) as e:
        raise EbMS2Exception(ErrorCode.Other_XML, f'The SOAP part is not a SOAP envelope -> {e}')

    if version != SOAPVersion.V11:
        raise EbMS2Exception(ErrorCode.Not_Supported, f'SOAP {version} is not supported')

    return out

# ################################################################################################################################

def _store(found:'stranydict', element:'any_', allowed:'strset') -> 'bool':
    """ Stores an ebMS element under its name. Returns False when the element is not of the ebMS namespace.
    """

    # Our response to produce
    out = element.tag.startswith(_eb_prefix)

    if out:

        _, _, name = element.tag.rpartition('}')
        where = location(name)

        if name not in allowed:
            raise EbMS2Exception(ErrorCode.Not_Supported, f'Element `{name}` is not supported here', where)

        if name in found:
            raise EbMS2Exception(ErrorCode.Inconsistent, f'Element `{name}` occurs more than once', where)

        found[name] = element

    return out

# ################################################################################################################################

def collect_elements(envelope:'any_') -> 'MessageElements':
    """ Returns the ebMS elements of an envelope, rejecting a mandatory header block that this node does not understand.
    """
    out = MessageElements()
    out.envelope = envelope

    if (soap_header := find_header(envelope)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'The envelope has no SOAP Header', _message_header_location)

    # The ebMS elements by their names.
    found:'stranydict' = {}

    for element in soap_header:

        if not isinstance(element.tag, str):
            continue

        if _store(found, element, _header_block_names):
            continue

        if element.tag == _ds_signature:
            out.signature = element
            continue

        # Any other header block is ignored, unless it is mandatory and meant for this node.
        if element.get(SOAP_Must_Understand) == Must_Understand_Value:

            if (actor := element.get(SOAP_Actor)) is None:
                actor = Actor.SOAP_Next

            if actor in _own_actors:
                raise EbMS2Exception(ErrorCode.Not_Supported, f'Mandatory header block `{element.tag}` is not understood')

    soap_body = get_body(envelope)

    for element in soap_body:

        if not isinstance(element.tag, str):
            continue

        _ = _store(found, element, _body_element_names)

    if (message_header := found.get('MessageHeader')) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `MessageHeader` is missing', _message_header_location)

    out.message_header = message_header
    out.ack_requested = found.get('AckRequested')
    out.sync_reply = found.get('SyncReply')
    out.message_order = found.get('MessageOrder')
    out.acknowledgment = found.get('Acknowledgment')
    out.error_list = found.get('ErrorList')
    out.manifest = found.get('Manifest')
    out.status_request = found.get('StatusRequest')
    out.status_response = found.get('StatusResponse')

    return out

# ################################################################################################################################
# ################################################################################################################################

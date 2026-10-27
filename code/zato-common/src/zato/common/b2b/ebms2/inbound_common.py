# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from hashlib import sha256
from http.client import OK

# Zato
from zato.common.b2b.ebms2.common import EbMS2Exception, ErrorCode, SOAP_Action_Header, SOAP_Action_Value
from zato.common.b2b.ebms2.header import parse_message_header
from zato.common.b2b.ebms2.message import parse_envelope
from zato.common.b2b.ebms2.packaging import unpack
from zato.common.b2b.ebms2.xml_ import eb_tag, location
from zato.common.soap.envelope import find_header
from zato.common.util.xml_.xmlsec import encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.packaging import Package, payload_list
    from zato.common.b2b.ebms2.signals import Acknowledgment, ErrorList, StatusResponse
    from zato.common.typing_ import anytuple, strlist, strstrdict
    Acknowledgment = Acknowledgment
    anytuple = anytuple
    ErrorList = ErrorList
    MessageHeader = MessageHeader
    Package = Package
    payload_list = payload_list
    StatusResponse = StatusResponse
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_message_header_tag = eb_tag('MessageHeader')
_message_header_location = location('MessageHeader')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Delivery:
    """ One received business message whose payloads are handed over to the application.
    """
    message_id:        str
    conversation_id:   str
    ref_to_message_id: str
    service:           str
    service_type:      str
    action:            str
    from_party:        str
    to_party:          str
    payloads:          'payload_list'

delivery_list = list[Delivery]

# ################################################################################################################################

@dataclass(init=False)
class HTTPResponse:
    """ What is returned on the HTTP connection a message arrived on.
    """
    status_code:  int = OK
    content_type: str = ''
    body:         bytes = b''

    @property
    def headers(self) -> 'strstrdict':
        out:'strstrdict' = {}

        # Receivers identify a response that carries a message service handler message as ebMS by its SOAPAction header,
        # in the same way as a request.
        if self.content_type:
            out['Content-Type'] = self.content_type
            out[SOAP_Action_Header] = SOAP_Action_Value

        return out

# ################################################################################################################################

@dataclass(init=False)
class AsyncSignal:
    """ A message service handler message that is sent to the other party on a connection of its own.
    """
    endpoint: str
    package:  'Package'

# ################################################################################################################################

@dataclass(init=False)
class ReceivedSignal:
    """ A message service handler message that answers a message sent earlier. The Content-Type and the body
    are kept so that the signal can be passed on as it arrived.
    """
    kind:              str
    ref_to_message_id: str
    header:            'MessageHeader'
    content_type:      str
    body:              bytes

    acknowledgment:  'Acknowledgment | None' = None
    error_list:      'ErrorList | None' = None
    status_response: 'StatusResponse | None' = None

# ################################################################################################################################
# ################################################################################################################################

def payload_digests(payloads:'payload_list') -> 'strlist':
    """ Returns the base64 SHA-256 digest of each payload, which is how outcomes name payloads.
    """
    out:'strlist' = []

    for payload in payloads:
        digest = sha256(payload.data)
        digest_bytes = digest.digest()
        encoded = encode_base64(digest_bytes)
        out.append(encoded)

    return out

# ################################################################################################################################

def read_message(headers:'strstrdict', body:'bytes') -> 'anytuple':
    """ Splits a message into its envelope and its payloads and reads its MessageHeader. These are the steps whose failure
    leaves no MessageId that an error message could refer to.
    """
    unpacked = unpack(headers, body)
    envelope = parse_envelope(unpacked.envelope)

    if (soap_header := find_header(envelope)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'The envelope has no SOAP Header', _message_header_location)

    if (header_element := soap_header.find(_message_header_tag)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `MessageHeader` is missing', _message_header_location)

    header = parse_message_header(header_element)

    out = (envelope, header, unpacked.payloads)
    return out

# ################################################################################################################################
# ################################################################################################################################

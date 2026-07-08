# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# lxml
from lxml.etree import XMLSyntaxError

# Zato
from zato.common.exception import ClientHTTPError
from zato.common.marshal_.api import ModelValidationError
from zato.common.soap.addressing import add_addressing, AddressingInfo, new_message_id, parse_addressing
from zato.common.soap.common import Content_Type, FaultCode, NS, SOAPException, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, get_body, get_version, parse_envelope, \
    to_bytes
from zato.common.soap.message import parse, SOAPMessage
from zato.common.soap.mtom import build_mtom, parse_message, to_bytes_map
from zato.common.soap.security.saml import get_assertion
from zato.common.soap.security.wss import Mode
from zato.common.util.xml_.core import qname
from zato.server.connection.http_soap import BadRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict, strnone
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anytuple = anytuple
    part_list = part_list
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The suffix of the response element and of the reply's wsa:Action, both derived
# from the request per the WS-Addressing default action pattern.
_response_suffix = 'Response'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SOAPSecurityInfo:
    """ What the channel's security enforcement established about the incoming message -
    available to services as self.request.soap.security.
    """
    # The WS-Security mode the channel's definition is in, if any.
    mode: 'strnone' = None

    # The verified username of a UsernameToken message.
    username: 'strnone' = None

    # The subject and issuer of the message's SAML assertion.
    subject: 'strnone' = None
    issuer:  'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SOAPRequestContext:
    """ The protocol context of one incoming SOAP request - available to services
    as self.request.soap, next to the unwrapped payload in self.request.payload.
    """
    # The SOAP version of the incoming envelope.
    soap_version: 'str' = SOAPVersion.V11

    # The local name of the operation element in soap:Body.
    operation: 'str' = ''

    # The WS-Addressing headers of the request, absent ones staying None.
    addressing: 'AddressingInfo'

    # What the security enforcement established about the message.
    security: 'SOAPSecurityInfo'

    # The MIME parts of a multipart request, empty for bare envelopes.
    attachments: 'part_list'

    # The raw envelope bytes as they arrived, before any decryption.
    envelope: 'bytes' = b''

    # The operation element as a dot-accessed message - what services read as self.request.payload.
    payload: 'SOAPMessage'

    # The parsed envelope element - security enforcement may decrypt it in place,
    # which is what makes the decrypted body visible to the service.
    element: 'any_' = None

    # Whether the channel packages responses carrying bytes as MTOM.
    use_mtom: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

def parse_soap_request(cid:'str', body:'bytes', content_type:'str', channel_item:'stranydict') -> 'SOAPRequestContext':
    """ Parses an incoming HTTP body of any packaging into a request context - the envelope
    element, its version, the WS-Addressing headers and any MIME parts. The operation
    and the payload are resolved separately, after security enforcement.
    """

    # Our response to produce
    out = SOAPRequestContext()

    out.security = SOAPSecurityInfo()
    out.payload = SOAPMessage()

    # Split off any MIME parts first - bare envelopes come back unchanged ..
    try:
        envelope_bytes, parts = parse_message(body, content_type)
        element = parse_envelope(envelope_bytes)
    except (SOAPException, XMLSyntaxError) as e:
        raise BadRequest(cid, f'Invalid SOAP request -> {e}', needs_msg=True)

    # .. the version comes from the envelope's own namespace ..
    out.soap_version = get_version(element)

    # .. the addressing headers are read up front because headers are never encrypted ..
    out.addressing = parse_addressing(element)

    out.attachments = parts
    out.envelope = envelope_bytes
    out.element = element

    # .. and the channel's configuration says how to package responses - the flag
    # is an opaque attribute, so it is absent from channels that never set it.
    out.use_mtom = bool(channel_item.get('use_mtom'))

    return out

# ################################################################################################################################

def resolve_soap_payload(cid:'str', context:'SOAPRequestContext', wsgi_environ:'stranydict') -> 'None':
    """ Resolves the operation element into the context's payload and fills in the security
    information. Runs after security enforcement so an encrypted body is already decrypted
    and the credentials the message carried are already verified.
    """
    body = get_body(context.element)

    # The operation is the first element child of soap:Body ..
    for child in body:
        if isinstance(child.tag, str):
            operation_element = child
            break
    else:
        raise BadRequest(cid, 'SOAP Body has no operation element', needs_msg=True)

    _, _, operation = operation_element.tag.rpartition('}')
    context.operation = operation

    # .. xop:Include references resolve back into bytes through the parts map ..
    if context.attachments:
        parts_map = to_bytes_map(context.attachments)
    else:
        parts_map = None

    context.payload = parse(operation_element, parts_map)

    # .. and whatever security enforcement established is surfaced too.
    _fill_security_info(context, wsgi_environ)

# ################################################################################################################################

def _fill_security_info(context:'SOAPRequestContext', wsgi_environ:'stranydict') -> 'None':
    """ Fills in the security information out of the security definition that
    enforcement ran against and out of the message itself.
    """

    # A channel may have no security definition at all.
    sec_def_info = wsgi_environ.get('zato.sec_def')

    if not sec_def_info:
        return

    sec_def = sec_def_info['impl']
    mode = sec_def.get('mode')

    # Definitions of other types than WS-Security carry no mode.
    if not mode:
        return

    context.security.mode = mode

    # The username was verified against the definition during enforcement ..
    if mode == Mode.UsernameToken:
        context.security.username = sec_def['username']

    # .. and a SAML subject travels in the message's own assertion.
    elif mode == Mode.SAML:
        context.security.issuer = sec_def['issuer']

        assertion = get_assertion(context.element)
        subject = assertion.find(qname(NS.SAML2, 'Subject'))

        if subject is not None:
            name_id = subject.find(qname(NS.SAML2, 'NameID'))
            if name_id is not None:
                context.security.subject = name_id.text

# ################################################################################################################################
# ################################################################################################################################

def build_soap_response(context:'SOAPRequestContext', message:'SOAPMessage') -> 'anytuple':
    """ Wraps a service's response message in an envelope matching the request - the same
    SOAP version, the operation's response element and, when the request carried
    WS-Addressing, the reply headers. Returns the body bytes and their Content-Type.
    """
    envelope = build_envelope(context.soap_version)

    # With MTOM enabled, bytes values leave as parts instead of inline base64 ..
    xop_parts:'part_list | None' = [] if context.use_mtom else None

    _ = attach_body(envelope, message, context.operation + _response_suffix, xop_parts=xop_parts)

    # .. a request that carried WS-Addressing gets the reply headers back ..
    if context.addressing.message_id:
        if context.addressing.action:

            reply = AddressingInfo()
            reply.action = context.addressing.action + _response_suffix
            reply.message_id = new_message_id()
            reply.relates_to = context.addressing.message_id

            add_addressing(envelope, reply)

    envelope_bytes = to_bytes(envelope)

    # .. with parts collected, the reply is an MTOM package, otherwise a bare envelope.
    if xop_parts:
        body, content_type = build_mtom(envelope_bytes, xop_parts, context.soap_version)
    else:
        body = envelope_bytes
        content_type = Content_Type[context.soap_version]

    out = (body, content_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_soap_fault_response(soap_version:'str', exception:'Exception', default_error_message:'str') -> 'anytuple':
    """ Turns a service exception into a well-formed SOAP fault of the request's version.
    Client errors become Sender faults carrying their message, everything else becomes
    a Receiver fault with the default message - a traceback never reaches the caller.
    Returns the body bytes and their Content-Type.
    """
    if isinstance(exception, (ClientHTTPError, ModelValidationError)):
        code = FaultCode.Sender
        reason = exception.msg

        # A client error may have been raised without any message.
        if reason is None:
            reason = default_error_message
    else:
        code = FaultCode.Receiver
        reason = default_error_message

    envelope = build_fault(soap_version, code, reason)

    body = to_bytes(envelope)
    content_type = Content_Type[soap_version]

    out = (body, content_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

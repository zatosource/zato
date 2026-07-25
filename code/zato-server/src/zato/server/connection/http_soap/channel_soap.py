# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# Zato
from zato.common.exception import ClientHTTPError
from zato.common.marshal_.api import ModelValidationError
from zato.common.soap.addressing import add_addressing, AddressingInfo, new_message_id, parse_addressing
from zato.common.soap.common import Action_Parameter, Content_Type, Fault_HTTP_Status, FaultCode, NS, \
    SOAPAddressingException, SOAPException, SOAPMustUnderstandException, SOAPVersion, \
    SOAPVersionMismatchException, Understood_Header_Namespaces, Version_By_Media_Type
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, check_must_understand, get_body, \
    get_version, parse_envelope, to_bytes
from zato.common.soap.message import parse, SOAPMessage
from zato.common.soap.mtom import build_mtom, parse_message, to_bytes_map
from zato.common.soap.security.saml import get_assertion
from zato.common.soap.security.wss import Mode
from zato.common.util.xml_.core import qname, XMLException
from zato.common.util.xml_.mime_ import parse_header_parameters
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

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# The suffix of the response element and of the reply's wsa:Action, both derived
# from the request per the WS-Addressing default action pattern.
_response_suffix = 'Response'

# What a caller is told when its message does not parse - the parser's own text names
# internal entities and offsets, so it goes to the log rather than back over the wire.
_invalid_request_reason = 'Invalid SOAP request'

# What a caller is told when it marked a header block mustUnderstand that this node does not
# implement. The block's own name goes to the log - naming it back over the wire would let an
# unauthenticated caller enumerate which specifications the node speaks.
_not_understood_reason = 'Mandatory header block not understood'

# What a caller is told when its transport and its envelope disagree on the SOAP version.
_version_mismatch_reason = 'SOAP version of the Content-Type does not match the envelope'

# The media type of a multipart package, which declares its SOAP version further in rather than
# in the outer Content-Type.
_multipart_related = 'multipart/related'

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

    # The action the request declared on the transport - the SOAPAction header in 1.1, the
    # Content-Type action parameter in 1.2. None when the caller declared none.
    soap_action: 'strnone' = None

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

    # What the message's signature covered, when the channel's definition involves one. Left as
    # None by definitions that carry no signature, and by channels with no security at all.
    verified_signature: 'any_' = None

    # Whether the channel packages responses carrying bytes as MTOM.
    use_mtom: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

def _transport_version(content_type:'str') -> 'strnone':
    """ Returns the SOAP version a request declares through its media type, or None when the media
    type is one neither version's binding names.
    """
    parameters = parse_header_parameters(content_type)
    media_type = parameters[''].strip().lower()

    # A multipart package declares the version in its type parameter instead, pointing at the media
    # type of the root part - which for MTOM is an XOP package, whose own type parameter says it.
    if media_type == _multipart_related:
        return None

    out = Version_By_Media_Type.get(media_type)
    return out

# ################################################################################################################################

def _transport_action(content_type:'str', soap_action_header:'strnone') -> 'strnone':
    """ Returns the action a request declares on the transport, from whichever place its SOAP
    version puts it - a header in 1.1, a Content-Type parameter in 1.2.

    Both places are read whatever the version, since a caller that puts the action in the other
    version's place still said what it meant, and a value read is better than a value ignored. The
    quotes SOAP 1.1 requires around the header value are stripped, because they are transport
    syntax rather than part of the action.
    """
    parameters = parse_header_parameters(content_type)
    action = parameters.get(Action_Parameter)

    if action is None:
        action = soap_action_header

    if action is None:
        return None

    out = action.strip().strip('"')

    # An empty SOAPAction header means "the action is not stated", which SOAP 1.1 explicitly
    # allows, so it comes back as no action rather than as an action that is the empty string.
    if not out:
        return None

    return out

# ################################################################################################################################

def _check_version(cid:'str', content_type:'str', envelope_version:'str') -> 'None':
    """ Raises when the version a request declares on the transport is not the one its envelope
    declares.

    Reading both matters because they are two independent statements about the same message, and a
    receiver that trusts only the envelope will process as 1.2 a message that every proxy and
    firewall on the way in read as 1.1. The two versions also differ in what a fault looks like and
    what status it leaves with, so answering under the wrong one leaves the sender unable to parse
    the answer.
    """
    transport_version = _transport_version(content_type)

    # A media type neither binding names, or a multipart package that declares the version further
    # in, says nothing to compare against - the envelope is then the only statement there is.
    if transport_version is None:
        return

    if transport_version != envelope_version:
        logger.warning('SOAP version mismatch -> cid:`%s` -> transport:`%s` envelope:`%s`', cid,
            transport_version, envelope_version)
        raise SOAPVersionMismatchException(_version_mismatch_reason)

# ################################################################################################################################

def parse_soap_request(
    cid:'str',
    body:'bytes',
    content_type:'str',
    channel_item:'stranydict',
    soap_action_header:'strnone'=None,
) -> 'SOAPRequestContext':
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
    except (SOAPException, XMLException) as e:
        logger.warning('Could not parse SOAP request -> cid:`%s` -> %s', cid, e)
        raise BadRequest(cid, _invalid_request_reason, needs_msg=True)

    # .. the version comes from the envelope's own namespace ..
    out.soap_version = get_version(element)

    # .. and the transport has to agree with it ..
    _check_version(cid, content_type, out.soap_version)

    # .. the action the caller declared is read from wherever its version puts it ..
    out.soap_action = _transport_action(content_type, soap_action_header)

    # .. a mandatory header block this node does not implement stops the message here, before
    # anything reads the body, since the sender is entitled to assume the block was honoured ..
    check_must_understand(element, Understood_Header_Namespaces)

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

    # Verification recorded which body element the signature covered. This is the other half of
    # that check: the body about to be read has to be the very same element, not merely one that
    # looks like it, because locating the verified element and the processed element independently
    # is what makes XML signature wrapping possible in the first place.
    if context.verified_signature is not None:
        if body is not context.verified_signature.body:
            logger.error('Verified body is not the body being processed -> cid:`%s`', cid)
            raise BadRequest(cid, _invalid_request_reason, needs_msg=True)

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

            _ = add_addressing(envelope, reply)

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
    Returns the body bytes, their Content-Type and the HTTP status the fault leaves with.
    """

    subcodes = None

    # A header this node does not understand is its own fault code, and one the caller can act on -
    # it says which of its header blocks to drop rather than merely that the request was refused.
    if isinstance(exception, SOAPMustUnderstandException):
        code = FaultCode.MustUnderstand
        reason = _not_understood_reason

    # A version disagreement is its own code in both versions, and it is what tells the sender to
    # retry under the other version rather than that the message itself was wrong.
    elif isinstance(exception, SOAPVersionMismatchException):
        code = FaultCode.VersionMismatch
        reason = _version_mismatch_reason

    # Addressing faults name the offending header in a subcode, which is the whole reason
    # WS-Addressing defines subcodes - a bare Sender fault leaves the sender guessing.
    elif isinstance(exception, SOAPAddressingException):
        code = FaultCode.Sender
        reason = exception.reason
        subcodes = exception.subcodes

    elif isinstance(exception, (ClientHTTPError, ModelValidationError)):
        code = FaultCode.Sender
        reason = exception.msg

        # A client error may have been raised without any message.
        if reason is None:
            reason = default_error_message
    else:
        code = FaultCode.Receiver
        reason = default_error_message

    envelope = build_fault(soap_version, code, reason, subcodes=subcodes)

    body = to_bytes(envelope)
    content_type = Content_Type[soap_version]

    # The status belongs to the fault code, not to the exception class the fault came from - the
    # generic classifier would put a 1.1 fault on a 4xx, which a 1.1 client reads as a transport
    # failure and never parses as a fault at all.
    status_code = Fault_HTTP_Status[soap_version][code]

    out = (body, content_type, status_code)
    return out

# ################################################################################################################################
# ################################################################################################################################

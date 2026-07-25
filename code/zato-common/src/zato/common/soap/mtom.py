# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.soap.common import Content_Type, SOAPException, SOAPVersion
from zato.common.util.xml_.mime_ import build_related, parse_header_parameters, part_list, split_related

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import bytes_by_content_id
    from zato.common.typing_ import anytuple, strstrdict
    anytuple = anytuple
    bytes_by_content_id = bytes_by_content_id
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The content type of an MTOM root part - the XOP package that wraps the envelope.
_xop_content_type = 'application/xop+xml'

# What the type parameter of an incoming multipart/related may name as its root part - an XOP
# package for MTOM, or a bare envelope of either SOAP version for SOAP with Attachments. The
# values are the bare media types, since the type parameter carries no charset.
Accepted_Root_Types = {
    _xop_content_type,
    Content_Type[SOAPVersion.V11].split(';')[0],
    Content_Type[SOAPVersion.V12].split(';')[0],
}

# ################################################################################################################################
# ################################################################################################################################

def build_mtom(envelope:'bytes', parts:'part_list', version:'str') -> 'anytuple':
    """ Packages an envelope and its binary parts as an MTOM message - a multipart/related
    body whose root part is an XOP package. Returns the body bytes and the Content-Type header.
    """
    # MTOM declares the SOAP version through the type parameter of the root part.
    soap_content_type = Content_Type[version]
    root_content_type = f'{_xop_content_type}; charset=UTF-8; type="{soap_content_type}"'

    out = build_related(envelope, root_content_type, parts, _xop_content_type, start_info=soap_content_type)
    return out

# ################################################################################################################################

def build_swa(envelope:'bytes', parts:'part_list', version:'str') -> 'anytuple':
    """ Packages an envelope and its attachments as SOAP with Attachments - a multipart/related
    body whose root part is the plain envelope. Returns the body bytes and the Content-Type header.
    """
    soap_content_type = Content_Type[version]

    # In SwA the type parameter is the bare content type without its charset parameter.
    type_parameter = soap_content_type.split(';')[0]

    out = build_related(envelope, soap_content_type, parts, type_parameter)
    return out

# ################################################################################################################################

def parse_message(body:'bytes', content_type:'str') -> 'anytuple':
    """ Parses an incoming HTTP body of any packaging - bare envelope, MTOM or SwA.
    Returns the envelope bytes and the list of attachment parts, empty for bare envelopes.
    """
    parameters = parse_header_parameters(content_type)
    base_type = parameters['']

    # Anything that is not multipart is a bare envelope.
    if base_type != 'multipart/related':
        out = (body, [])
        return out

    if 'boundary' not in parameters:
        raise SOAPException('Content-Type has no boundary parameter')

    # The type parameter says what the root part is. Reading it means an MTOM package and a SwA
    # package are told apart by what they declare rather than by guessing, and a package declaring
    # something else entirely is refused instead of being parsed as SOAP.
    _check_root_type(parameters)

    # The start parameter names which part is the root - see split_related on why it matters.
    envelope, parts = split_related(body, parameters['boundary'], parameters.get('start'))

    if not envelope:
        raise SOAPException('Multipart body has no envelope part')

    out = (envelope, parts)
    return out

# ################################################################################################################################

def _check_root_type(parameters:'strstrdict') -> 'None':
    """ Checks the type parameter of a multipart/related Content-Type against the two packagings
    this implementation reads - an XOP package for MTOM, a bare envelope for SwA.
    """
    root_type = parameters.get('type')

    # RFC 2387 requires the parameter, but a peer that omits it is not thereby sending something
    # else, and the root part's own Content-Type is what actually decides. Refusing the message
    # over a missing parameter would reject working senders for no gain.
    if root_type is None:
        return

    root_type = root_type.strip().lower()

    if root_type not in Accepted_Root_Types:
        raise SOAPException(f'Unsupported multipart root type `{root_type}`')

# ################################################################################################################################

def to_bytes_map(parts:'part_list') -> 'bytes_by_content_id':
    """ Returns the bytes of each part keyed by its Content-ID - the shape
    that message parsing expects for resolving xop:Include references.
    """

    # Our response to produce
    out:'bytes_by_content_id' = {}

    for part in parts:
        out[part.content_id] = part.data

    return out

# ################################################################################################################################
# ################################################################################################################################

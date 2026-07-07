# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.soap.common import Content_Type, SOAPException
from zato.common.util.xml_.mime_ import build_related, parse_header_parameters, part_list, split_related

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import bytes_by_content_id
    from zato.common.typing_ import anytuple
    anytuple = anytuple
    bytes_by_content_id = bytes_by_content_id

# ################################################################################################################################
# ################################################################################################################################

# The content type of an MTOM root part - the XOP package that wraps the envelope.
_xop_content_type = 'application/xop+xml'

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

    envelope, parts = split_related(body, parameters['boundary'])

    if not envelope:
        raise SOAPException('Multipart body has no envelope part')

    out = (envelope, parts)
    return out

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

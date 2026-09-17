# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import IMAPMessage
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.util.xml_.message import XMLMessage
from zato.edifact.envelope import EDIEnvelopeError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The UNB syntax identifier names the character set of the whole interchange
_syntax_encoding = {
    'UNOA': 'ascii',
    'UNOB': 'ascii',
    'UNOC': 'iso-8859-1',
    'UNOD': 'iso-8859-2',
    'UNOE': 'iso-8859-5',
    'UNOF': 'iso-8859-7',
    'UNOY': 'utf-8',
}

# What bytes without a UNB header decode as
_default_encoding = 'iso-8859-1'

# The UNB header, if present, starts within this many bytes
_preamble_length = 32

# The syntax identifier is the four characters after the UNB tag and its element separator
_unb_tag = b'UNB'
_unb_tag_with_separator_length = 4
_syntax_identifier_length = 4

# The reserved key under which an XMLMessage keeps the text of its own element
_xml_text_key = 'text'

# ################################################################################################################################
# ################################################################################################################################

def _encoding_from_bytes(data:'bytes') -> 'str':
    """ Returns the encoding the UNB syntax identifier of the interchange calls for,
    or the default when there is no UNB header.
    """
    preamble = data[:_preamble_length]
    unb_index = preamble.find(_unb_tag)

    # Bare messages have no UNB and get the default ..
    if unb_index == -1:
        out = _default_encoding

    # .. otherwise the identifier follows the tag and its separator.
    else:
        syntax_start = unb_index + _unb_tag_with_separator_length
        syntax_end = syntax_start + _syntax_identifier_length
        syntax_identifier = data[syntax_start:syntax_end]
        syntax_identifier = syntax_identifier.decode('ascii')

        if encoding := _syntax_encoding.get(syntax_identifier):
            out = encoding
        else:
            out = _default_encoding

    return out

# ################################################################################################################################

def _text_from_bytes(data:'bytes') -> 'str':
    encoding = _encoding_from_bytes(data)
    out = data.decode(encoding)

    return out

# ################################################################################################################################

def _text_from_xml(payload:'XMLMessage') -> 'str':
    """ Returns the interchange text a SOAP operation element carries - either as its own text
    or as the text of its single child element.
    """

    # The operation element itself may hold the text ..
    if text := payload[_xml_text_key]:
        out = text

    # .. or one child element does.
    else:
        children = payload.to_dict()
        texts:'strlist' = []

        for value in children.values():
            if isinstance(value, str):
                texts.append(value)

        text_count = len(texts)
        has_single_text = text_count == 1

        if has_single_text:
            out = texts[0]
        else:
            child_names = list(children)
            raise EDIEnvelopeError(f'Expected exactly 1 text child in the SOAP operation, found {text_count} in {child_names}')

    return out

# ################################################################################################################################

def _text_from_imap(message:'IMAPMessage') -> 'str':
    """ Returns the first plain-text part of an e-mail, which is where an interchange travels.
    """
    body = message.data.body
    plain_parts = body['plain']

    if plain_parts:
        out = plain_parts[0]
    else:
        raise EDIEnvelopeError(f'No plain-text part in e-mail `{message.uid}`')

    return out

# ################################################################################################################################

def wire_text_from(raw:'any_', payload:'any_') -> 'str':
    """ Returns the EDIFACT wire text out of what a channel handed to a service - the raw request
    for most channels and the parsed operation element for SOAP ones.
    """

    # A SOAP raw request is the whole envelope, so the parsed operation element is what to read ..
    if isinstance(payload, XMLMessage):
        out = _text_from_xml(payload)

    # .. an e-mail carries the text in its first plain-text part ..
    elif isinstance(raw, IMAPMessage):
        out = _text_from_imap(raw)

    # .. a received file carries it as bytes ..
    elif isinstance(raw, FileTransferItem):
        out = _text_from_bytes(raw.data)

    # .. bytes decode by the interchange's own syntax identifier ..
    elif isinstance(raw, bytes):
        out = _text_from_bytes(raw)

    # .. text is the wire form already ..
    elif isinstance(raw, str):
        out = raw

    # .. and anything else does not carry EDIFACT.
    else:
        type_name = type(raw).__name__
        raise EDIEnvelopeError(f'Cannot read EDIFACT from a request of type `{type_name}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

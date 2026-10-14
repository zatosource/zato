# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Envelope reading - extracting the routing identifiers of an EDI payload without a full parse.
# For EDIFACT that is the UNB sender and recipient and the UNH message type. This is what lets a channel
# route on the partner plus the document type, since the transport an interchange arrives over is payload-agnostic.

from __future__ import annotations

# stdlib
from dataclasses import asdict, dataclass

# Zato
from zato.edifact.syntax import EDISyntaxError
from zato.edifact.syntax import parse_segment as parse_edifact_segment, parse_una, split_segments as split_edifact_segments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strbytes, strlist
    stranydict = stranydict
    strbytes = strbytes
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The recognized envelope formats.
Format_EDIFACT = 'edifact'

# The segment tags envelope reading looks at.
EDIFACT_Advice_Tag      = 'UNA'
EDIFACT_Interchange_Tag = 'UNB'
EDIFACT_Message_Tag     = 'UNH'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EnvelopeInfo:
    """ The envelope identifiers of one EDI payload - everything routing and reporting
    can key on without a full parse. All the fields default to empty strings so a payload
    that is not EDI at all yields a result whose format is empty.
    """

    # Which envelope format the payload carries - Format_EDIFACT or empty.
    format: str = ''

    # The interchange-level sender and receiver - UNB02 for the sender and UNB03 for the recipient,
    # whose qualifiers ride in the second component of each composite.
    sender_qualifier:   str = ''
    sender_id:          str = ''
    receiver_qualifier: str = ''
    receiver_id:        str = ''

    # The document type routing keys on - UNH02.1, e.g. ORDERS or INVOIC.
    document_type: str = ''

    # The control numbers of each envelope level - UNB05 and UNH01.
    interchange_control_number: str = ''
    set_control_number:         str = ''

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':
        """ Returns the envelope identifiers as a plain dictionary - the shape routed messages
        and audit metadata carry them in.
        """
        out = asdict(self)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _element(parts:'strlist', index:'int') -> 'str':
    """ Returns one element of a separator-split segment, or an empty string
    when the segment is shorter than that.
    """
    part_count = len(parts)

    if index >= part_count:
        return ''

    out = parts[index]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _read_edifact(text:'str') -> 'EnvelopeInfo':
    """ Reads the UNB and the first UNH of an EDIFACT interchange.
    The service characters come from the UNA when there is one, otherwise the defaults apply.
    """

    # Our response to produce
    out = EnvelopeInfo()
    out.format = Format_EDIFACT

    # The optional UNA declares the service characters for the rest of the interchange.
    separators, rest = parse_una(text)
    segments = split_edifact_segments(rest, separators)

    for segment_text in segments:
        raw_segment = parse_edifact_segment(segment_text, separators)

        # The UNB carries the interchange-level sender, recipient and control reference ..
        if raw_segment.tag == EDIFACT_Interchange_Tag:
            elements = raw_segment.elements
            element_count = len(elements)

            # UNB02 is the sender composite - the id, then the qualifier ..
            if element_count > 1:
                sender = elements[1]
                out.sender_id = _element(sender, 0)
                out.sender_qualifier = _element(sender, 1)

            # .. UNB03 is the recipient composite of the same shape ..
            if element_count > 2:
                recipient = elements[2]
                out.receiver_id = _element(recipient, 0)
                out.receiver_qualifier = _element(recipient, 1)

            # .. and UNB05 is the interchange control reference.
            if element_count > 4:
                control_reference = elements[4]
                out.interchange_control_number = _element(control_reference, 0)

        # .. and the first UNH names the message type - after that, routing has everything it needs.
        elif raw_segment.tag == EDIFACT_Message_Tag:
            elements = raw_segment.elements
            element_count = len(elements)

            # UNH01 is the message reference number ..
            if element_count > 0:
                reference_composite = elements[0]
                out.set_control_number = _element(reference_composite, 0)

            # .. and UNH02.1 is the message type, e.g. ORDERS.
            if element_count > 1:
                message_type_composite = elements[1]
                out.document_type = _element(message_type_composite, 0)

            break

    return out

# ################################################################################################################################

def read_envelope(data:'strbytes') -> 'EnvelopeInfo':
    """ Extracts the envelope identifiers of an EDI payload without a full parse.
    Never raises - a payload that is not EDI, or whose envelope is malformed,
    comes back with an empty format, because envelope reading exists to inform routing,
    not to validate the document.
    """

    # EDI envelopes are pure ASCII, so any single-byte decoding preserves them.
    if isinstance(data, bytes):
        text = data.decode('latin-1')
    else:
        text = data

    # Leading whitespace is decorative.
    text = text.lstrip()

    # EDIFACT opens with either the UNA service advice or the UNB itself ..
    is_una = text.startswith(EDIFACT_Advice_Tag)
    is_unb = text.startswith(EDIFACT_Interchange_Tag)

    if is_una or is_unb:
        try:
            out = _read_edifact(text)
        except EDISyntaxError:
            out = EnvelopeInfo()
        return out

    # .. and anything else is not an EDI payload.
    out = EnvelopeInfo()
    return out

# ################################################################################################################################
# ################################################################################################################################

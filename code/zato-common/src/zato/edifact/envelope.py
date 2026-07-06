# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

# Zato
from zato.edifact.base import EDIMessage, _wrap_raw_segment
from zato.edifact.service import UNB, UNZ
from zato.edifact.syntax import RawSegment, Separators, default_separators, parse_segments, parse_una

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
any_             = 'Any'
intnone          = 'Optional[int]'
strnone          = 'Optional[str]'
strlist          = list[str]
anylist          = list['Any']
stranydict       = dict[str, 'Any']
raw_segment_list      = list[RawSegment]
raw_segment_list_list = list[raw_segment_list]
message_list          = list[EDIMessage]

# ################################################################################################################################
# ################################################################################################################################

# Service segment tags that belong to the interchange or group envelope, not to any message.
_envelope_tags = {'UNB', 'UNZ', 'UNG', 'UNE'}

# ################################################################################################################################
# ################################################################################################################################

class EDIEnvelopeError(Exception):
    """ Raised when the interchange envelope is structurally invalid, e.g. there is nothing to parse.
    """

# ################################################################################################################################
# ################################################################################################################################

class EDIInterchange:
    """ A parsed EDIFACT interchange - the optional UNA/UNB/UNZ envelope and the messages inside it.
    Bare messages without an envelope (as sent through ZorgMail mailboxes) parse into
    an interchange whose header and trailer are None.
    """

    def __init__(self) -> 'None':

        # The service characters in effect for this interchange
        self.separators:'Separators' = default_separators

        # Whether the wire data carried an explicit UNA service string advice
        self.has_una:'bool' = False

        # The UNB segment, if any
        self.header:'any_' = None

        # The UNZ segment, if any
        self.trailer:'any_' = None

        # Functional group service segments (UNG/UNE), if any, kept in wire order
        self.group_segments:'anylist' = []

        # The typed messages of this interchange
        self.messages:'message_list' = []

# ################################################################################################################################

    @property
    def message(self) -> 'EDIMessage':
        """ The single message of this interchange - for the common case of one message per interchange.
        """
        message_count = len(self.messages)

        if message_count != 1:
            raise EDIEnvelopeError(f'Expected exactly 1 message, found {message_count}')

        out = self.messages[0]
        return out

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serializes the whole interchange to its wire form, one segment per line.
        """
        lines:'strlist' = []

        # The UNA comes first if the original had one ..
        if self.has_una:
            separators = self.separators
            service_characters = separators.component + separators.element + separators.decimal + \
                separators.release + separators.repetition + separators.terminator
            lines.append(f'UNA{service_characters}')

        # .. then the UNB header ..
        if self.header is not None:
            line = self.header.serialize(self.separators)
            lines.append(line)

        # .. then every message ..
        for message in self.messages:
            line = message.serialize(self.separators)
            lines.append(line)

        # .. and the UNZ trailer concludes the interchange.
        if self.trailer is not None:
            line = self.trailer.serialize(self.separators)
            lines.append(line)

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    to_edifact = serialize

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this interchange to a dictionary representation.
        """

        # Our response to produce
        out:'stranydict' = {}

        if self.header is not None:
            out['header'] = self.header.to_dict(include_empty=include_empty)

        messages:'anylist' = []

        for message in self.messages:
            messages.append(message.to_dict(include_empty=include_empty))

        out['messages'] = messages

        if self.trailer is not None:
            out['trailer'] = self.trailer.to_dict(include_empty=include_empty)

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone'=None, include_empty:'bool'=True) -> 'str':
        """ Converts this interchange to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _split_messages(raw_segments:'raw_segment_list') -> 'raw_segment_list_list':
    """ Splits the raw segments of an interchange body into per-message slices.
    A message runs from its UNH up to and including its UNT. Real-world fragments
    without UNH/UNT (e.g. published message excerpts) become a single message slice.
    """

    # Our response to produce
    out:'raw_segment_list_list' = []

    current:'raw_segment_list' = []

    for raw_segment in raw_segments:

        # A UNH starts a new message - flush whatever was collected before it ..
        if raw_segment.tag == 'UNH':
            if current:
                out.append(current)
            current = [raw_segment]
            continue

        current.append(raw_segment)

        # .. and a UNT concludes the current message.
        if raw_segment.tag == 'UNT':
            out.append(current)
            current = []

    if current:
        out.append(current)

    return out

# ################################################################################################################################

def parse_edifact(raw:'str') -> 'EDIInterchange':
    """ Parses wire text into an EDIInterchange. Accepts full interchanges with UNA/UNB/UNZ,
    bare messages starting at UNH and even envelope-less segment fragments.
    """

    # Our response to produce
    out = EDIInterchange()

    # Leading whitespace never carries meaning in an interchange
    raw = raw.lstrip()

    # Read the UNA service string advice if there is one ..
    separators, rest = parse_una(raw)
    out.separators = separators
    out.has_una = raw.startswith('UNA')

    # .. split the text into raw segments ..
    raw_segments = parse_segments(rest, separators)

    if not raw_segments:
        raise EDIEnvelopeError('No segments found in input')

    # .. pull out the envelope service segments ..
    body:'raw_segment_list' = []

    for raw_segment in raw_segments:
        if raw_segment.tag == 'UNB':
            out.header = UNB.from_raw(raw_segment)
        elif raw_segment.tag == 'UNZ':
            out.trailer = UNZ.from_raw(raw_segment)
        elif raw_segment.tag in _envelope_tags:
            group_segment = _wrap_raw_segment(raw_segment)
            out.group_segments.append(group_segment)
        else:
            body.append(raw_segment)

    # .. split the body into messages and wrap each in its typed class.
    message_slices = _split_messages(body)

    for message_segments in message_slices:
        message_class = EDIMessage.resolve_class(message_segments)
        message = message_class.from_raw(message_segments, separators)
        out.messages.append(message)

    return out

# ################################################################################################################################
# ################################################################################################################################

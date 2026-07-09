# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
strlist     = list[str]
strlistlist = list[list[str]]

# ################################################################################################################################
# ################################################################################################################################

# The interchange header tag - every X12 interchange starts with it.
ISA_Tag = 'ISA'

# The ISA is a fixed-width segment - its sixteen elements have these exact lengths.
ISA_Element_Lengths = (2, 10, 2, 10, 2, 15, 2, 15, 6, 4, 1, 5, 9, 1, 1, 1)

# How many elements a well-formed ISA always has.
ISA_Element_Count = len(ISA_Element_Lengths)

# Zero-based indexes of the ISA elements that carry syntax information.
ISA_Repetition_Index     = 10 # ISA11 - repetition separator (or standards identifier in older versions)
ISA_Version_Index        = 11 # ISA12 - interchange control version number
ISA_Control_Number_Index = 12 # ISA13 - the nine-digit interchange control number
ISA_Component_Index      = 15 # ISA16 - component element separator

# ISA11 became the repetition separator in version 00402 - before that it was
# the standards identifier `U` and there was no repetition separator at all.
Repetition_Min_Version = '00402'

# The value the repetition field takes when an interchange version has no repetition separator.
No_Repetition = ''

# Characters that are ignored between segments - real-world interchanges use bare newlines
# and CR/LF pairs as visual separators after each segment terminator.
Inter_Segment_Whitespace = '\r\n\t '

# ################################################################################################################################
# ################################################################################################################################

# Offsets of the element separators inside a well-formed ISA - one right before each of the sixteen elements ..
_offsets:'list[int]' = []
_position = len(ISA_Tag)

for _element_length in ISA_Element_Lengths:
    _offsets.append(_position)
    _position += 1 + _element_length

ISA_Separator_Offsets = tuple(_offsets)

# .. the segment terminator comes right after the last element ..
ISA_Terminator_Offset = _position

# .. which makes the whole segment exactly 106 characters, terminator included.
ISA_Total_Length = ISA_Terminator_Offset + 1

# ################################################################################################################################
# ################################################################################################################################

# Offsets of the individual syntax characters inside a well-formed ISA.
ISA_Repetition_Offset = ISA_Separator_Offsets[ISA_Repetition_Index] + 1
ISA_Version_Offset    = ISA_Separator_Offsets[ISA_Version_Index] + 1
ISA_Version_Length    = ISA_Element_Lengths[ISA_Version_Index]
ISA_Component_Offset  = ISA_Separator_Offsets[ISA_Component_Index] + 1

# ################################################################################################################################
# ################################################################################################################################

class X12SyntaxError(Exception):
    """ Raised when an interchange cannot be split into valid X12 segments,
    e.g. the fixed-width ISA is malformed or data contains an active separator.
    """

# ################################################################################################################################
# ################################################################################################################################

class Separators(NamedTuple):
    """ The X12 syntax characters - always derived from the ISA on the parse side,
    the defaults are only a convenience for building new interchanges.
    """
    element:'str'    = '*'
    component:'str'  = '>'
    repetition:'str' = '^'
    terminator:'str' = '~'
    version:'str'    = '00501'

# ################################################################################################################################
# ################################################################################################################################

# The customary separators most trading partners use with version 00501.
default_separators = Separators()

# ################################################################################################################################
# ################################################################################################################################

class RawSegment:
    """ One parsed segment - its tag and its data elements, each element being a list
    of component strings. The counters list always stays empty - it exists because
    the shared EDI descriptor base expects it on every raw segment, but X12 has no
    tag-attached repeat counters the way EDIFACT Medeur messages do.
    """

    def __init__(self, tag:'str', counters:'strlist', elements:'strlistlist') -> 'None':
        self.tag = tag
        self.counters = counters
        self.elements = elements

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'<RawSegment {self.tag} elements={self.elements}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

raw_segment_list = list[RawSegment]

# ################################################################################################################################
# ################################################################################################################################

def parse_isa(raw:'str') -> 'Separators':
    """ Reads the syntax characters from the fixed-width ISA segment at the beginning of an interchange.
    The element separator is the character right after the ISA tag, the component separator is ISA16,
    the repetition separator is ISA11 (in versions 00402 and later) and the segment terminator
    is whatever single character follows ISA16. Raises X12SyntaxError if the ISA is malformed -
    there is no release character in X12, so a broken fixed-width layout cannot be guessed around.
    """

    # The ISA must be long enough to hold the full fixed-width layout ..
    raw_length = len(raw)
    if raw_length < ISA_Total_Length:
        raise X12SyntaxError(f'ISA segment must be at least {ISA_Total_Length} characters long, not {raw_length}')

    # .. and must actually start with the ISA tag ..
    if not raw.startswith(ISA_Tag):
        prefix = raw[:len(ISA_Tag)]
        raise X12SyntaxError(f'Interchange must start with `{ISA_Tag}`, not `{prefix}`')

    # .. the element separator is the character right after the tag ..
    element = raw[ISA_Separator_Offsets[0]]

    # .. and the fixed element widths dictate where every other separator must appear.
    for offset in ISA_Separator_Offsets[1:]:
        character = raw[offset]
        if character != element:
            raise X12SyntaxError(f'Malformed ISA - expected element separator `{element}` at offset {offset}, not `{character}`')

    component  = raw[ISA_Component_Offset]
    terminator = raw[ISA_Terminator_Offset]
    version    = raw[ISA_Version_Offset:ISA_Version_Offset + ISA_Version_Length]

    # A terminator is never a letter or digit - if it is one, the fixed-width layout was violated.
    if terminator.isalnum():
        raise X12SyntaxError(f'Malformed ISA - terminator must not be a letter or digit, found `{terminator}`')

    # ISA11 is the repetition separator only in versions that define one -
    # older interchanges carry the standards identifier there instead.
    if version < Repetition_Min_Version:
        repetition = No_Repetition
    else:
        repetition = raw[ISA_Repetition_Offset]

    out = Separators(element, component, repetition, terminator, version)
    return out

# ################################################################################################################################

def split_segments(raw:'str', separators:'Separators') -> 'strlist':
    """ Splits wire text into individual segment strings. There is no release character in X12,
    so every occurrence of the terminator ends a segment and a plain split is exact - which also
    keeps large interchanges fast, with memory proportional to the input size. Whitespace between
    segments is ignored, including the CR/LF pairs and bare newlines real senders emit.
    """

    # Our response to produce
    out:'strlist' = []

    terminator = separators.terminator

    # Every terminator ends a segment ..
    parts = raw.split(terminator)

    # .. except that the text after the last one is not a complete segment.
    last_part = parts[-1]
    parts = parts[:-1]

    for part in parts:

        # Whitespace before a segment is decorative and is dropped ..
        part = part.lstrip(Inter_Segment_Whitespace)

        # .. and anything else gets its terminator back.
        if part:
            segment_text = part + terminator
            out.append(segment_text)

    # An interchange may lack the final terminator - keep whatever is left as the last segment.
    remainder = last_part.strip()
    if remainder:
        out.append(remainder)

    return out

# ################################################################################################################################

def parse_segment(segment_text:'str', separators:'Separators') -> 'RawSegment':
    """ Parses one segment string (with or without its trailing terminator) into a RawSegment.
    The ISA is special-cased because its sixteenth element is the component separator itself
    and must stay verbatim. The repetition separator is not split at this level - it is preserved
    inside component values so that round-trips stay byte-exact.
    """

    # Drop the trailing terminator if it is still attached ..
    if segment_text.endswith(separators.terminator):
        segment_text = segment_text[:-1]

    # .. split the segment into its data elements ..
    element_parts = segment_text.split(separators.element)
    tag = element_parts[0]
    data_parts = element_parts[1:]

    # .. ISA elements are kept as-is because ISA16 carries the component separator ..
    if tag == ISA_Tag:

        data_count = len(data_parts)
        if data_count != ISA_Element_Count:
            raise X12SyntaxError(f'ISA must have exactly {ISA_Element_Count} elements, not {data_count}')

        elements:'strlistlist' = []

        for element_text in data_parts:
            elements.append([element_text])

    # .. and any other segment splits each element into its components.
    else:
        elements = []

        for element_text in data_parts:
            components = element_text.split(separators.component)
            elements.append(components)

    out = RawSegment(tag, [], elements)
    return out

# ################################################################################################################################

def _ensure_no_separators(value:'str', separators:'Separators') -> 'None':
    """ Raises X12SyntaxError if a value contains an active separator - X12 has no release character,
    so a separator inside data cannot be escaped on the wire. The repetition separator is not checked
    because parsing keeps repetitions verbatim inside component values and round-trips must stay byte-exact.
    """
    for separator in (separators.element, separators.component, separators.terminator):
        if separator in value:
            raise X12SyntaxError(f'Separator `{separator}` must not appear in data: `{value}`')

# ################################################################################################################################

def _serialize_isa(segment:'RawSegment', separators:'Separators') -> 'str':
    """ Emits an ISA segment in its fixed-width layout - alphanumeric elements are padded
    with trailing spaces and the nine-digit control number with leading zeros.
    """

    # The ISA always carries exactly sixteen elements ..
    element_count = len(segment.elements)
    if element_count != ISA_Element_Count:
        raise X12SyntaxError(f'ISA must have exactly {ISA_Element_Count} elements, not {element_count}')

    element_texts:'strlist' = [ISA_Tag]

    for index, components in enumerate(segment.elements):

        element_number = index + 1

        # .. each element is a single fixed-width value, never a composite ..
        component_count = len(components)
        if component_count != 1:
            raise X12SyntaxError(f'ISA element {element_number} must have exactly one component, not {component_count}')

        value = components[0]
        width = ISA_Element_Lengths[index]

        # .. the control number gets leading zeros, everything else trailing spaces ..
        if index == ISA_Control_Number_Index:
            value = value.rjust(width, '0')
        else:
            value = value.ljust(width)

        # .. a value wider than its fixed width cannot be represented ..
        value_length = len(value)
        if value_length > width:
            raise X12SyntaxError(f'ISA element {element_number} must be at most {width} characters long, not {value_length}')

        # .. and the element separator or terminator inside a value would corrupt the segment.
        # The component separator is not checked because ISA16 is that very character.
        if separators.element in value:
            raise X12SyntaxError(f'Separator `{separators.element}` must not appear in ISA data: `{value}`')
        if separators.terminator in value:
            raise X12SyntaxError(f'Separator `{separators.terminator}` must not appear in ISA data: `{value}`')

        element_texts.append(value)

    body = separators.element.join(element_texts)

    out = body + separators.terminator
    return out

# ################################################################################################################################

def serialize_segment(segment:'RawSegment', separators:'Separators') -> 'str':
    """ Turns a RawSegment back into its wire form. The ISA is emitted in its fixed-width layout,
    any other segment joins its components and elements with the active separators,
    rejecting data that contains one of them.
    """

    # The ISA has its own fixed-width serialization rules ..
    if segment.tag == ISA_Tag:
        out = _serialize_isa(segment, separators)

    # .. everything else is a plain join of components and elements.
    else:
        element_texts = [segment.tag]

        for components in segment.elements:

            for component_value in components:
                _ensure_no_separators(component_value, separators)

            element_text = separators.component.join(components)
            element_texts.append(element_text)

        body = separators.element.join(element_texts)
        out = body + separators.terminator

    return out

# ################################################################################################################################

def parse_segments(raw:'str', separators:'Separators') -> 'raw_segment_list':
    """ Splits wire text into segments and parses each one into a RawSegment.
    """

    # Our response to produce
    out:'raw_segment_list' = []

    segment_texts = split_segments(raw, separators)

    for segment_text in segment_texts:
        segment = parse_segment(segment_text, separators)
        out.append(segment)

    return out

# ################################################################################################################################
# ################################################################################################################################

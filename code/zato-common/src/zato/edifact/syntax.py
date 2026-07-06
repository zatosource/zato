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
una_result  = tuple['Separators', str]

# ################################################################################################################################
# ################################################################################################################################

# The service string advice tag - when present, it is always the very first three characters of an interchange.
UNA_Tag = 'UNA'

# A full UNA carries six service characters after the tag ..
UNA_Full_Length = 6

# .. but some real-world senders omit the reserved repetition position and send only five.
UNA_Short_Length = 5

# Characters that are ignored between segments - real-world interchanges use bare newlines,
# CR/LF pairs and even tabs (e.g. indented CUSCAR cargo reports) as visual separators.
Inter_Segment_Whitespace = '\r\n\t '

# ################################################################################################################################
# ################################################################################################################################

class EDISyntaxError(Exception):
    """ Raised when an interchange or message cannot be split into valid EDIFACT segments.
    """

# ################################################################################################################################
# ################################################################################################################################

class Separators(NamedTuple):
    """ The EDIFACT service characters, either the defaults or the ones a UNA segment declares.
    """
    component:'str'  = ':'
    element:'str'    = '+'
    decimal:'str'    = '.'
    release:'str'    = '?'
    repetition:'str' = ' '
    terminator:'str' = "'"

# ################################################################################################################################
# ################################################################################################################################

# The default service characters per ISO 9735 level A.
default_separators = Separators()

# ################################################################################################################################
# ################################################################################################################################

class RawSegment:
    """ One parsed segment - its tag, the optional Medeur repeat counters that follow the tag
    (e.g. BEP:1:1:2 has tag BEP and counters ['1', '1', '2']) and its data elements.
    Each element is a list of already unescaped component strings.
    """

    def __init__(self, tag:'str', counters:'strlist', elements:'strlistlist') -> 'None':
        self.tag = tag
        self.counters = counters
        self.elements = elements

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'<RawSegment {self.tag} counters={self.counters} elements={self.elements}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

raw_segment_list = list[RawSegment]

# ################################################################################################################################
# ################################################################################################################################

def parse_una(raw:'str') -> 'una_result':
    """ Reads the UNA service string advice from the beginning of an interchange, if there is one.
    Returns the separators to use and the remaining text after the UNA. Handles both the standard
    six-character form (UNA:+.? ') and the real-world five-character form without the repetition position.
    """

    # No UNA means the default service characters apply ..
    if not raw.startswith(UNA_Tag):
        return default_separators, raw

    service_characters = raw[3:3 + UNA_Full_Length]

    component  = service_characters[0]
    element    = service_characters[1]
    decimal    = service_characters[2]
    release    = service_characters[3]
    repetition = service_characters[4]
    terminator = service_characters[5]

    # A terminator is never a letter or digit - if the sixth character is one, the sender
    # omitted the reserved repetition position and the fifth character is already the
    # terminator (e.g. UNA:+.?' directly followed by UNB).
    if terminator.isalnum():
        separators = Separators(component, element, decimal, release, ' ', repetition)
        rest = raw[3 + UNA_Short_Length:]

        return separators, rest

    # Otherwise this is the standard six-character form.
    separators = Separators(component, element, decimal, release, repetition, terminator)
    rest = raw[3 + UNA_Full_Length:]

    return separators, rest

# ################################################################################################################################

def split_segments(raw:'str', separators:'Separators') -> 'strlist':
    """ Splits wire text into individual segment strings, honoring the release character
    so that an escaped terminator (e.g. ?') inside a value does not end the segment.
    Whitespace between segments is ignored, including the tabs and newlines real senders emit.
    """

    # Our response to produce
    out:'strlist' = []

    release = separators.release
    terminator = separators.terminator

    current:'strlist' = []
    is_released = False

    for character in raw:

        # Whitespace between segments is decorative and is skipped ..
        if not current:
            if character in Inter_Segment_Whitespace:
                continue

        current.append(character)

        # .. an unescaped terminator concludes the current segment ..
        if character == terminator:
            if not is_released:
                segment_text = ''.join(current)
                out.append(segment_text)
                current = []

        # .. the release character escapes exactly the one character that follows it.
        if character == release:
            is_released = not is_released
        else:
            is_released = False

    # A message may lack the final terminator - keep whatever is left as the last segment.
    remainder = ''.join(current).strip()
    if remainder:
        out.append(remainder)

    return out

# ################################################################################################################################

def split_with_release(text:'str', delimiter:'str', release:'str') -> 'strlist':
    """ Splits text on a delimiter while honoring the release character.
    The escape sequences themselves are preserved - unescaping is a separate step.
    """

    # Our response to produce
    out:'strlist' = []

    current:'strlist' = []
    is_released = False

    for character in text:

        # An unescaped delimiter ends the current part ..
        if character == delimiter:
            if not is_released:
                part = ''.join(current)
                out.append(part)
                current = []
                is_released = False
                continue

        current.append(character)

        # .. and the release character escapes the one character that follows it.
        if character == release:
            is_released = not is_released
        else:
            is_released = False

    last_part = ''.join(current)
    out.append(last_part)

    return out

# ################################################################################################################################

def unescape(value:'str', separators:'Separators') -> 'str':
    """ Removes release characters from a value, turning e.g. ?' into a literal apostrophe.
    Per ISO 9735 the release character always makes the character that follows it literal,
    even when that character is not a service character - real-world senders do emit
    such stray escapes and receivers are expected to drop the release character.
    """

    # Our response to produce
    out:'strlist' = []

    index = 0
    length = len(value)

    while index < length:
        character = value[index]

        # A release character makes the next character literal ..
        if character == separators.release:
            next_index = index + 1
            if next_index < length:
                next_character = value[next_index]
                out.append(next_character)
                index += 2
                continue

        # .. anything else is copied through as-is.
        out.append(character)
        index += 1

    result = ''.join(out)
    return result

# ################################################################################################################################

def escape(value:'str', separators:'Separators') -> 'str':
    """ Inserts release characters before any service character occurring in a value.
    """

    # Our response to produce
    out:'strlist' = []

    special = {separators.component, separators.element, separators.release, separators.terminator}

    for character in value:

        # Every service character needs the release character in front of it ..
        if character in special:
            out.append(separators.release)

        # .. and then the character itself is copied through.
        out.append(character)

    result = ''.join(out)
    return result

# ################################################################################################################################

def parse_segment(segment_text:'str', separators:'Separators') -> 'RawSegment':
    """ Parses one segment string (with or without its trailing terminator) into a RawSegment.
    The tag element is split on the component separator because Medeur messages attach
    repeat counters to the tag itself (e.g. TXT:3 or BEP:1:1:2).
    """

    # Drop the trailing terminator if it is still attached and genuinely a terminator,
    # i.e. it is preceded by an even number of release characters ..
    if segment_text.endswith(separators.terminator):
        release_count = 0
        position = len(segment_text) - 2

        while position >= 0:
            if segment_text[position] == separators.release:
                release_count += 1
                position -= 1
            else:
                break

        is_escaped = release_count % 2 == 1
        if not is_escaped:
            segment_text = segment_text[:-1]

    # .. split the segment into its data elements ..
    element_parts = split_with_release(segment_text, separators.element, separators.release)

    # .. the first element carries the tag and any Medeur repeat counters ..
    tag_parts = split_with_release(element_parts[0], separators.component, separators.release)
    tag = tag_parts[0]
    counters = tag_parts[1:]

    # .. and each remaining element is split into its unescaped components.
    elements:'strlistlist' = []

    for element_text in element_parts[1:]:
        component_parts = split_with_release(element_text, separators.component, separators.release)
        components:'strlist' = []

        for component_text in component_parts:
            component_value = unescape(component_text, separators)
            components.append(component_value)

        elements.append(components)

    out = RawSegment(tag, counters, elements)
    return out

# ################################################################################################################################

def serialize_segment(segment:'RawSegment', separators:'Separators') -> 'str':
    """ Turns a RawSegment back into its wire form, re-escaping service characters
    and re-attaching any Medeur repeat counters to the tag.
    """

    # Rebuild the tag element with its repeat counters ..
    tag_parts = [segment.tag]

    for counter in segment.counters:
        tag_parts.append(counter)

    element_texts = [separators.component.join(tag_parts)]

    # .. then each data element from its escaped components ..
    for components in segment.elements:
        component_texts:'strlist' = []

        for component_value in components:
            component_text = escape(component_value, separators)
            component_texts.append(component_text)

        element_text = separators.component.join(component_texts)
        element_texts.append(element_text)

    # .. and join everything with the element separator, ending with the terminator.
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

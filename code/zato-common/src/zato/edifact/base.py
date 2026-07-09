# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# Zato
from zato.edi.base import EDIComponent, EDIComposite, EDIElement, EDIGroup, EDIGroupAttr, EDIMessage as _EDIMessageCore, \
     EDIRepeatableList, EDISegment as _EDISegmentCore, EDISegmentAttr, EDIValidationError, Usage
from zato.edifact.syntax import RawSegment, default_separators, serialize_segment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
any_             = 'Any'
strlist          = list[str]
strlistlist      = list[list[str]]
anylist          = list['Any']
stranydict       = dict[str, 'Any']
raw_segment_list = list[RawSegment]

# ################################################################################################################################
# ################################################################################################################################

# The generic descriptor machinery lives in zato.edi and is re-exported here
# so that every existing "from zato.edifact import ..." keeps working.
__all__ = [
    'EDIComponent',
    'EDIComposite',
    'EDIElement',
    'EDIGenericMessage',
    'EDIGenericSegment',
    'EDIGroup',
    'EDIGroupAttr',
    'EDIMessage',
    'EDIRepeatableList',
    'EDISegment',
    'EDISegmentAttr',
    'EDIValidationError',
    'Usage',
]

# ################################################################################################################################
# ################################################################################################################################

class EDISegment(_EDISegmentCore):
    """ Base class for all EDIFACT segment definitions.
    """

    # The EDIFACT raw-segment machinery bound to the dialect hooks of the shared base
    _raw_segment_class = RawSegment
    _serialize_segment = staticmethod(serialize_segment)
    _default_separators = default_separators

# ################################################################################################################################

    @property
    def counters(self) -> 'strlist':
        """ The Medeur repeat counters attached to this segment's tag, e.g. ['1', '1', '2'] for BEP:1:1:2.
        """
        raw_segment = self._raw_segment
        if raw_segment is None:
            return []

        out = raw_segment.counters
        return out

# ################################################################################################################################

    to_edifact = _EDISegmentCore.serialize

# ################################################################################################################################
# ################################################################################################################################

class EDIGenericSegment(EDISegment):
    """ A segment without a Python class definition - its elements are reachable
    through positional attributes like e_1, e_2, etc. and through .elements.
    """

# ################################################################################################################################

    @property
    def tag(self) -> 'str':
        out = self._raw_segment.tag
        return out

# ################################################################################################################################

    @property
    def elements(self) -> 'strlistlist':
        out = self._raw_segment.elements
        return out

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':

        # Positional access like e_1 resolves to the element at that position,
        # collapsing a single-component element to its scalar value.
        if name.startswith('e_'):
            suffix = name[2:]

            if suffix.isdigit():
                position = int(suffix)
                index = position - 1
                element_count = len(self._raw_segment.elements)

                if index < element_count:
                    components = self._raw_segment.elements[index]
                    component_count = len(components)
                    has_single_component = component_count == 1

                    if has_single_component:

                        out = components[0]
                        return out

                    out = components
                    return out

                return None

        raise AttributeError(name)

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this generic segment to a dictionary with positional keys.
        """

        # Our response to produce
        out:'stranydict' = {'_segment_tag': self._raw_segment.tag}

        if self._raw_segment.counters:
            out['_counters'] = self._raw_segment.counters

        for element_index, components in enumerate(self._raw_segment.elements):
            position = element_index + 1
            key = f'e_{position}'
            component_count = len(components)
            has_single_component = component_count == 1

            if has_single_component:
                out[key] = components[0]
            else:
                out[key] = components

        return out

# ################################################################################################################################
# ################################################################################################################################

class EDIMessage(_EDIMessageCore):
    """ Base class for all EDIFACT message definitions. A message covers the segments
    between UNH and UNT inclusive.
    """

    # The EDIFACT raw-segment machinery bound to the dialect hooks of the shared base
    _serialize_segment = staticmethod(serialize_segment)
    _generic_segment_class = EDIGenericSegment

    # Built messages serialize with the default service characters per ISO 9735 level A
    _separators = default_separators

# ################################################################################################################################

    @classmethod
    def resolve_class(cls, raw_segments:'raw_segment_list') -> 'type[EDIMessage]':
        """ Finds the message class for the given raw segments based on the UNH message identifier,
        trying the association code first, then type:version, then the bare type.
        """
        identifier:'strlist' = []

        for raw_segment in raw_segments:
            if raw_segment.tag == 'UNH':
                element_count = len(raw_segment.elements)
                if element_count >= 2:
                    identifier = raw_segment.elements[1]
                break

        message_type = identifier[0] if identifier else ''
        message_version = identifier[1] if len(identifier) >= 2 else ''
        association = identifier[4] if len(identifier) >= 5 else ''

        # The association assigned code is the most specific identity ..
        if association:
            if association in cls._registry:

                out = cls._registry[association]
                return out

        # .. then the type and version pair ..
        if message_type:
            if message_version:
                type_and_version = f'{message_type}:{message_version}'
                if type_and_version in cls._registry:

                    out = cls._registry[type_and_version]
                    return out

            # .. then the bare type ..
            if message_type in cls._registry:

                out = cls._registry[message_type]
                return out

        # .. and anything else is a generic message navigable by raw segments.
        out = EDIGenericMessage
        return out

# ################################################################################################################################

    to_edifact = _EDIMessageCore.serialize

# ################################################################################################################################
# ################################################################################################################################

class EDIGenericMessage(EDIMessage):
    """ A message without a Python class definition - navigable through .segments()
    and serializable byte-exact.
    """

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this generic message to a dictionary of its raw segments.
        """

        # Our response to produce
        out:'stranydict' = {'_message_type': ''}

        raw_segments = self._raw_segments

        # Note the message type from UNH if we have one ..
        for raw_segment in raw_segments:
            if raw_segment.tag == 'UNH':
                element_count = len(raw_segment.elements)
                if element_count >= 2:
                    identifier = raw_segment.elements[1]
                    if identifier:
                        out['_message_type'] = identifier[0]
                break

        # .. and convert every segment positionally.
        segments:'anylist' = []

        for raw_segment in raw_segments:
            segment = _wrap_raw_segment(raw_segment)
            segments.append(segment.to_dict(include_empty=include_empty))

        out['segments'] = segments

        return out

# ################################################################################################################################
# ################################################################################################################################

def _wrap_raw_segment(raw_segment:'RawSegment') -> 'EDISegment':
    """ Wraps a raw segment in a generic segment instance. Typed segment classes are
    reached through the EDISegmentAttr descriptors of the message that declares them -
    a bare tag alone does not identify a segment definition across dialects.
    """
    out = EDIGenericSegment.from_raw(raw_segment)
    return out

# ################################################################################################################################
# ################################################################################################################################

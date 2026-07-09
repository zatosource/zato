# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
from typing import cast as cast_

# Zato
from zato.edi.base import EDIComponent, EDIComposite, EDIElement, EDIGroup, EDIGroupAttr, EDIMessage as _EDIMessageCore, \
     EDIRepeatableList, EDISegment as _EDISegmentCore, EDISegmentAttr, EDIValidationError, Usage
from zato.x12.syntax import RawSegment, default_separators, serialize_segment

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

hierarchical_loop_list = list['X12HierarchicalLoop']
hierarchical_loop_none = 'X12HierarchicalLoop | None'
str_loop_dict          = dict[str, 'X12HierarchicalLoop']

# ################################################################################################################################
# ################################################################################################################################

# The generic descriptor machinery lives in zato.edi and is re-exported here
# so that X12 dictionaries import everything from one place.
__all__ = [
    'EDIComponent',
    'EDIComposite',
    'EDIElement',
    'EDIGroup',
    'EDIGroupAttr',
    'EDIRepeatableList',
    'EDISegmentAttr',
    'EDIValidationError',
    'Usage',
    'X12GenericMessage',
    'X12GenericSegment',
    'X12HierarchicalLoop',
    'X12Message',
    'X12Segment',
]

# ################################################################################################################################
# ################################################################################################################################

# Segment tags that conclude the transaction set body - an HL hierarchy never extends past them.
_hierarchy_stop_tags = {'CTT', 'SE'}

# The positions of the HL elements that build the hierarchy (1-based).
_HL_ID_Position     = 1
_HL_Parent_Position = 2
_HL_Level_Position  = 3
_HL_Child_Position  = 4

# ################################################################################################################################
# ################################################################################################################################

def _element_value(raw_segment:'RawSegment', position:'int') -> 'str':
    """ Returns the first component of the element at the given 1-based position,
    or an empty string when the element is absent from the wire data.
    """
    index = position - 1
    element_count = len(raw_segment.elements)

    if index >= element_count:
        return ''

    components = raw_segment.elements[index]
    if not components:
        return ''

    out = components[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class X12Segment(_EDISegmentCore):
    """ Base class for all X12 segment definitions.
    """

    # The X12 raw-segment machinery bound to the dialect hooks of the shared base
    _raw_segment_class = RawSegment
    _serialize_segment = staticmethod(serialize_segment)
    _default_separators = default_separators

# ################################################################################################################################
# ################################################################################################################################

class X12GenericSegment(X12Segment):
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

class X12HierarchicalLoop:
    """ One HL loop instance of a hierarchical transaction set (856, 837, 270/271) -
    the HL segment's identifiers, the segments belonging to this loop and the child
    loops resolved from the HL parent pointers, which flat leader-tag slicing cannot express.
    """

    def __init__(self) -> 'None':

        # HL01 - the hierarchical id of this loop
        self.hl_id:'str' = ''

        # HL02 - the id of the parent loop, empty for a top-level loop
        self.parent_id:'str' = ''

        # HL03 - the level code, e.g. S (shipment), O (order), P (pack), I (item)
        self.level_code:'str' = ''

        # HL04 - whether this loop announces subordinate loops
        self.child_code:'str' = ''

        # The HL segment itself plus every segment up to the next HL
        self.raw_segments:'raw_segment_list' = []

        # The loops whose HL02 points at this loop
        self.children:'hierarchical_loop_list' = []

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'<X12HierarchicalLoop id={self.hl_id} level={self.level_code} children={len(self.children)}>'
        return out

# ################################################################################################################################

    def segments(self, tag:'str') -> 'anylist':
        """ Returns all segments of this loop with the given tag, in wire order,
        each wrapped in a generic segment for positional access.
        """

        # Our response to produce
        out:'anylist' = []

        for raw_segment in self.raw_segments:
            if raw_segment.tag == tag:
                segment = X12GenericSegment.from_raw(raw_segment)
                out.append(segment)

        return out

# ################################################################################################################################

    @classmethod
    def build(cls, raw_segments:'raw_segment_list') -> 'hierarchical_loop_list':
        """ Builds the loop tree from the raw segments of one transaction set.
        Each HL starts a new loop that collects every following segment until the next HL
        or the end of the set body, and the HL02 parent pointers link the loops into a tree.
        Returns the top-level loops - segments before the first HL belong to no loop.
        """

        # Our response to produce
        out:'hierarchical_loop_list' = []

        nodes:'hierarchical_loop_list' = []
        current:'hierarchical_loop_none' = None

        for raw_segment in raw_segments:

            # The set trailer area concludes every loop ..
            if raw_segment.tag in _hierarchy_stop_tags:
                break

            # .. each HL starts a new loop ..
            if raw_segment.tag == 'HL':
                node = cls()
                node.hl_id = _element_value(raw_segment, _HL_ID_Position)
                node.parent_id = _element_value(raw_segment, _HL_Parent_Position)
                node.level_code = _element_value(raw_segment, _HL_Level_Position)
                node.child_code = _element_value(raw_segment, _HL_Child_Position)
                node.raw_segments.append(raw_segment)

                nodes.append(node)
                current = node
                continue

            # .. and everything after an HL belongs to the most recent loop.
            if current is not None:
                current.raw_segments.append(raw_segment)

        # Resolve the parent pointers into a tree ..
        nodes_by_id:'str_loop_dict' = {}

        for node in nodes:
            nodes_by_id[node.hl_id] = node

        # .. a loop whose parent exists becomes its child, anything else is top-level.
        for node in nodes:
            if parent := nodes_by_id.get(node.parent_id):
                parent.children.append(node)
            else:
                out.append(node)

        return out

# ################################################################################################################################
# ################################################################################################################################

class X12Message(_EDIMessageCore):
    """ Base class for all X12 transaction set definitions. A message covers the segments
    between ST and SE inclusive.
    """

    # The X12 raw-segment machinery bound to the dialect hooks of the shared base
    _serialize_segment = staticmethod(serialize_segment)
    _generic_segment_class = X12GenericSegment

    # Built messages serialize with the customary version 00501 characters
    _separators = default_separators

    # Every concrete transaction set class declares its ST and SE through EDISegmentAttr -
    # the base only reserves the names so that envelope code can address them uniformly.
    st:'any_' = None
    se:'any_' = None

# ################################################################################################################################

    @classmethod
    def resolve_class(cls, raw_segments:'raw_segment_list', version:'str') -> 'type[X12Message]':
        """ Finds the transaction set class for the given raw segments - by ST01 plus
        the GS08 version of the enclosing group (e.g. 850:004010 or 837:005010X222A1),
        then by ST01 plus the ST03 implementation convention reference, then by ST01 alone.
        """
        identifier_code = ''
        implementation_reference = ''

        for raw_segment in raw_segments:
            if raw_segment.tag == 'ST':
                identifier_code = _element_value(raw_segment, 1)
                implementation_reference = _element_value(raw_segment, 3)
                break

        if identifier_code:

            # The group version is the primary identity ..
            if version:
                type_and_version = f'{identifier_code}:{version}'
                if type_and_version in cls._registry:

                    out = cast_('type[X12Message]', cls._registry[type_and_version])
                    return out

            # .. then the implementation convention reference the set itself declares ..
            if implementation_reference:
                type_and_reference = f'{identifier_code}:{implementation_reference}'
                if type_and_reference in cls._registry:

                    out = cast_('type[X12Message]', cls._registry[type_and_reference])
                    return out

            # .. then the bare set identifier ..
            if identifier_code in cls._registry:

                out = cast_('type[X12Message]', cls._registry[identifier_code])
                return out

        # .. and anything else is a generic message navigable by raw segments.
        out = X12GenericMessage
        return out

# ################################################################################################################################

    @property
    def hierarchy(self) -> 'hierarchical_loop_list':
        """ The HL loop tree of this transaction set - empty for sets without HL segments
        and for messages built from scratch.
        """
        raw_segments = self._raw_segments
        if raw_segments is None:
            return []

        out = X12HierarchicalLoop.build(raw_segments)
        return out

# ################################################################################################################################
# ################################################################################################################################

class X12GenericMessage(X12Message):
    """ A transaction set without a Python class definition - navigable through .segments()
    and serializable byte-exact.
    """

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this generic message to a dictionary of its raw segments.
        """

        # Our response to produce
        out:'stranydict' = {'_message_type': ''}

        raw_segments = self._raw_segments

        # Note the set identifier from ST if we have one ..
        for raw_segment in raw_segments:
            if raw_segment.tag == 'ST':
                out['_message_type'] = _element_value(raw_segment, 1)
                break

        # .. and convert every segment positionally.
        segments:'anylist' = []

        for raw_segment in raw_segments:
            segment = X12GenericSegment.from_raw(raw_segment)
            segments.append(segment.to_dict(include_empty=include_empty))

        out['segments'] = segments

        return out

# ################################################################################################################################
# ################################################################################################################################

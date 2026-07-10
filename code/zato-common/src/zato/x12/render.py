# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The human-readable rendering of X12 documents - what the Dashboard shows next to the raw
# wire format: segments in document order, each element named after its dictionary descriptor,
# loops indented. Built on the same descriptors the parser uses, so anything the dictionaries
# know by name is shown by name and everything else stays reachable positionally.

from __future__ import annotations

# Zato
from zato.edi.base import EDIComponent, EDIElement, EDIGroupAttr, EDISegmentAttr, _composite_classes, \
     _declared_attr_descriptors
from zato.x12 import hipaa as hipaa, retail as retail  # noqa: F401 - imported so the dictionaries register their classes
from zato.x12.base import X12GenericMessage, X12HierarchicalLoop
from zato.x12.envelope import X12EnvelopeError, parse_x12
from zato.x12.service import GE, GS, IEA, ISA, SE, ST, TA1
from zato.x12.syntax import ISA_Tag, X12SyntaxError, parse_isa

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.x12.base import X12Message
    from zato.x12.envelope import X12Interchange
    from zato.x12.syntax import RawSegment, Separators
    RawSegment = RawSegment
    Separators = Separators
    X12Interchange = X12Interchange
    X12Message = X12Message

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
strlist          = list[str]
typenone         = 'type | None'
raw_segment_list = list['RawSegment']

element_by_position_dict   = dict[int, EDIElement]
component_by_position_dict = dict[int, EDIComponent]
segment_class_by_tag_dict  = dict[str, type]
group_info_by_leader_dict  = dict[str, '_GroupInfo']
group_info_list            = list['_GroupInfo']
depth_by_segment_dict      = dict[int, int]
hierarchical_loop_list     = list[X12HierarchicalLoop]

# ################################################################################################################################
# ################################################################################################################################

# One indentation level in the rendered output.
_indent = '    '

# The envelope segment classes, addressable by tag - they name the envelope elements
# of every interchange, including ones whose transaction sets have no dictionary.
_envelope_segment_classes:'segment_class_by_tag_dict' = {
    'ISA': ISA,
    'GS':  GS,
    'GE':  GE,
    'IEA': IEA,
    'ST':  ST,
    'SE':  SE,
    'TA1': TA1,
}

# ################################################################################################################################
# ################################################################################################################################

class _GroupInfo:
    """ What one group class declares - collected once per class for loop indentation.
    """

    def __init__(self) -> 'None':

        # The tag whose each occurrence starts a new instance of this loop
        self.leader_tag:'str' = ''

        # The tags of the segments declared directly inside this loop
        self.member_tags:'strlist' = []

        # The loops nested inside this one, by their leader tag
        self.nested:'group_info_by_leader_dict' = {}

# ################################################################################################################################
# ################################################################################################################################

class _RenderSchema:
    """ What one transaction set class declares - collected once per class and cached.
    """

    def __init__(self) -> 'None':

        # The segment class of every tag the set or its loops declare
        self.segment_class_by_tag:'segment_class_by_tag_dict' = {}

        # The loops declared at the message level, by their leader tag
        self.groups:'group_info_by_leader_dict' = {}

# ################################################################################################################################

_render_schema_cache:'dict[type, _RenderSchema]' = {}
_element_descriptor_cache:'dict[type, element_by_position_dict]' = {}
_component_descriptor_cache:'dict[type, component_by_position_dict]' = {}

# ################################################################################################################################
# ################################################################################################################################

def _element_descriptors_by_position(segment_class:'type') -> 'element_by_position_dict':
    """ Returns the element descriptors of a segment class, by their 1-based position.
    """
    if descriptors := _element_descriptor_cache.get(segment_class):
        out = descriptors
        return out

    # Our response to produce
    out:'element_by_position_dict' = {}

    for name in dir(segment_class):
        attribute = getattr(segment_class, name)
        if isinstance(attribute, EDIElement):
            out[attribute.position] = attribute

    _element_descriptor_cache[segment_class] = out

    return out

# ################################################################################################################################

def _component_descriptors_by_position(composite_class:'type') -> 'component_by_position_dict':
    """ Returns the component descriptors of a composite class, by their 1-based position.
    """
    if descriptors := _component_descriptor_cache.get(composite_class):
        out = descriptors
        return out

    # Our response to produce
    out:'component_by_position_dict' = {}

    for name in dir(composite_class):
        attribute = getattr(composite_class, name)
        if isinstance(attribute, EDIComponent):
            out[attribute.position] = attribute

    _component_descriptor_cache[composite_class] = out

    return out

# ################################################################################################################################

def _collect_group_info(group_class:'type') -> '_GroupInfo':
    """ Walks the declared attributes of a group class, recording its member tags
    and the loops nested inside it.
    """

    # Our response to produce
    out = _GroupInfo()
    out.leader_tag = group_class._leader_tag

    for descriptor in _declared_attr_descriptors(group_class):

        # A segment reference is a direct member of this loop ..
        if isinstance(descriptor, EDISegmentAttr):
            out.member_tags.append(descriptor.tag)

        # .. and a group reference is a loop nested inside it.
        elif isinstance(descriptor, EDIGroupAttr):
            nested = _collect_group_info(descriptor.group_class)
            out.nested[nested.leader_tag] = nested

    return out

# ################################################################################################################################

def _collect_segment_classes(source_class:'type', segment_class_by_tag:'segment_class_by_tag_dict') -> 'None':
    """ Walks the declared attributes of a message or group class, recording the segment
    class of every tag, including the tags of nested loops.
    """
    for descriptor in _declared_attr_descriptors(source_class):

        if isinstance(descriptor, EDISegmentAttr):
            if descriptor.tag not in segment_class_by_tag:
                segment_class_by_tag[descriptor.tag] = descriptor.segment_class

        elif isinstance(descriptor, EDIGroupAttr):
            _collect_segment_classes(descriptor.group_class, segment_class_by_tag)

# ################################################################################################################################

def _get_render_schema(message_class:'type') -> '_RenderSchema':
    """ Returns the cached render schema of a transaction set class, building it on first use.
    """
    if schema := _render_schema_cache.get(message_class):
        out = schema
        return out

    # Our response to produce
    out = _RenderSchema()

    # Every declared tag maps to its segment class ..
    _collect_segment_classes(message_class, out.segment_class_by_tag)

    # .. and every message-level group contributes its loop structure.
    for descriptor in _declared_attr_descriptors(message_class):
        if isinstance(descriptor, EDIGroupAttr):
            group_info = _collect_group_info(descriptor.group_class)
            out.groups[group_info.leader_tag] = group_info

    _render_schema_cache[message_class] = out

    return out

# ################################################################################################################################
# ################################################################################################################################

def _assign_hierarchy_depths(out:'depth_by_segment_dict', loops:'hierarchical_loop_list', depth:'int') -> 'None':
    """ Assigns each segment of each HL loop the depth of its loop in the tree.
    """
    for loop in loops:

        for raw_segment in loop.raw_segments:
            out[id(raw_segment)] = depth

        _assign_hierarchy_depths(out, loop.children, depth + 1)

# ################################################################################################################################

def _hierarchy_depths(raw_segments:'raw_segment_list') -> 'depth_by_segment_dict':
    """ Returns the HL-tree depth of every segment of a hierarchical transaction set -
    segments outside any HL loop, e.g. the header and trailer areas, stay at depth zero.
    """

    # Our response to produce
    out:'depth_by_segment_dict' = {}

    # Everything starts outside any loop ..
    for raw_segment in raw_segments:
        out[id(raw_segment)] = 0

    # .. and the segments of each HL loop take the depth of their loop.
    loops = X12HierarchicalLoop.build(raw_segments)
    _assign_hierarchy_depths(out, loops, 1)

    return out

# ################################################################################################################################

def _group_depths(groups:'group_info_by_leader_dict', raw_segments:'raw_segment_list') -> 'depth_by_segment_dict':
    """ Returns the loop depth of every segment of a transaction set, mirroring how
    group slicing works - a leader tag opens its loop, the following segments stay
    inside it as long as they are its members, and anything else concludes it.
    """

    # Our response to produce
    out:'depth_by_segment_dict' = {}

    stack:'group_info_list' = []

    for raw_segment in raw_segments:
        tag = raw_segment.tag

        # Unwind every loop this segment does not belong to ..
        while stack:
            current = stack[-1]

            # .. a repeated leader starts a sibling instance at the same depth ..
            if tag == current.leader_tag:
                break

            # .. a nested leader will open its loop below ..
            if tag in current.nested:
                break

            # .. a member stays inside the current loop ..
            if tag in current.member_tags:
                break

            # .. and anything else concludes the current loop.
            _ = stack.pop()

        # A leader tag opens its loop - a nested one or a message-level one.
        if stack:
            current = stack[-1]
            if nested := current.nested.get(tag):
                stack.append(nested)
        else:
            if group := groups.get(tag):
                stack.append(group)

        out[id(raw_segment)] = len(stack)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _segment_description(segment_class:'type') -> 'str':
    """ Returns the first line of a segment class's docstring, without its trailing period.
    """
    docstring = segment_class.__doc__
    if not docstring:
        return ''

    text = docstring.strip()
    text_lines = text.splitlines()
    first_line = text_lines[0]

    out = first_line.strip()
    if out.endswith('.'):
        out = out[:-1]

    return out

# ################################################################################################################################

def _has_value(components:'strlist') -> 'bool':
    """ Tells whether an element carries any value at all - fixed-width padding
    is whitespace and does not count.
    """
    for component_value in components:
        if component_value.strip():
            return True

    return False

# ################################################################################################################################

def _render_segment(
    lines:'strlist',
    raw_segment:'RawSegment',
    segment_class:'typenone',
    depth:'int',
    separators:'Separators',
    ) -> 'None':
    """ Renders one segment - its tag with the dictionary description on the heading line
    and each non-empty element named after its descriptor below, positional names
    covering whatever the dictionary does not declare.
    """
    tag = raw_segment.tag
    prefix = _indent * depth

    # The heading names the segment when the dictionary knows it ..
    if segment_class:
        description = _segment_description(segment_class)
    else:
        description = ''

    if description:
        lines.append(f'{prefix}{tag} - {description}')
    else:
        lines.append(f'{prefix}{tag}')

    # .. and its elements follow, one indentation level deeper.
    if segment_class:
        descriptors = _element_descriptors_by_position(segment_class)
    else:
        descriptors = {}

    element_prefix = _indent * (depth + 1)
    component_prefix = _indent * (depth + 2)

    for element_index, components in enumerate(raw_segment.elements):
        position = element_index + 1

        # An element without any value is not shown at all
        if not _has_value(components):
            continue

        descriptor = descriptors.get(position)

        # A position the dictionary does not declare keeps its positional name ..
        if descriptor is None:
            value = separators.component.join(components)
            value = value.strip()
            lines.append(f'{element_prefix}e_{position}: {value}')
            continue

        # .. a composite element shows each component with its own name ..
        if descriptor.composite:
            composite_class = _composite_classes[descriptor.composite]
            component_descriptors = _component_descriptors_by_position(composite_class)

            lines.append(f'{element_prefix}{descriptor.attr_name}:')

            for component_index, component_value in enumerate(components):
                component_position = component_index + 1
                component_value = component_value.strip()

                if not component_value:
                    continue

                component_descriptor = component_descriptors.get(component_position)

                if component_descriptor is None:
                    component_name = f'c_{component_position}'
                else:
                    component_name = component_descriptor.attr_name

                lines.append(f'{component_prefix}{component_name}: {component_value}')

            continue

        # .. and a simple element shows its wire value next to its descriptor name.
        value = separators.component.join(components)
        value = value.strip()
        lines.append(f'{element_prefix}{descriptor.attr_name}: {value}')

# ################################################################################################################################

def _render_transaction_set(lines:'strlist', message:'X12Message', separators:'Separators') -> 'None':
    """ Renders one transaction set in wire order - descriptor names come from the set's
    dictionary when it has one and the loops are indented, by the HL parent pointers
    in hierarchical sets and by the declared group leaders everywhere else.
    """
    raw_segments = message._raw_segments

    # A generic set has no dictionary of its own - the envelope classes still name its ST and SE
    is_generic = isinstance(message, X12GenericMessage)

    if is_generic:
        schema = None
    else:
        schema = _get_render_schema(type(message))

    # Hierarchical sets indent by the depth of their HL loops ..
    has_hierarchy = False

    for raw_segment in raw_segments:
        if raw_segment.tag == 'HL':
            has_hierarchy = True
            break

    if has_hierarchy:
        hierarchy_depths = _hierarchy_depths(raw_segments)
    else:
        hierarchy_depths = _group_depths({}, raw_segments)

    # .. and the declared group loops indent within their surroundings.
    if schema:
        group_depths = _group_depths(schema.groups, raw_segments)
    else:
        group_depths = _group_depths({}, raw_segments)

    for raw_segment in raw_segments:
        segment_id = id(raw_segment)
        depth = hierarchy_depths[segment_id] + group_depths[segment_id]

        # The set's own dictionary names the segment, the envelope classes cover ST and SE
        if schema:
            segment_class = schema.segment_class_by_tag.get(raw_segment.tag)
        else:
            segment_class = None

        if segment_class is None:
            segment_class = _envelope_segment_classes.get(raw_segment.tag)

        _render_segment(lines, raw_segment, segment_class, depth, separators)

# ################################################################################################################################
# ################################################################################################################################

def render_interchange(interchange:'X12Interchange') -> 'str':
    """ Renders a parsed interchange to its human-readable form - the envelope segments
    and every transaction set of every group, in document order.
    """
    lines:'strlist' = []
    separators = interchange.separators

    # The ISA opens the interchange ..
    _render_segment(lines, interchange.isa._raw_segment, ISA, 0, separators)

    # .. followed by any interchange-level acknowledgments ..
    for ta1 in interchange.ta1_list:
        _render_segment(lines, ta1._raw_segment, TA1, 0, separators)

    # .. then every group with its transaction sets ..
    for group in interchange.groups:
        _render_segment(lines, group.gs._raw_segment, GS, 0, separators)

        for transaction_set in group.transaction_sets:
            _render_transaction_set(lines, transaction_set, separators)

        _render_segment(lines, group.ge._raw_segment, GE, 0, separators)

    # .. and the IEA concludes it.
    _render_segment(lines, interchange.iea._raw_segment, IEA, 0, separators)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def extract_x12(text:'str') -> 'str':
    """ Returns the first X12 interchange embedded in the given text - the fixed-width ISA
    through its IEA trailer - or an empty string when the text carries none. This is what
    lets the audit log render documents out of payloads that wrap the EDI in other content.
    """
    search_start = 0

    while True:

        # Look for the next ISA candidate ..
        start = text.find(ISA_Tag, search_start)
        if start < 0:
            return ''

        candidate = text[start:]

        # .. a candidate that is not a well-formed fixed-width ISA is skipped ..
        try:
            separators = parse_isa(candidate)
        except X12SyntaxError:
            search_start = start + 1
            continue

        # .. the interchange ends with its IEA trailer - data cannot contain
        # .. the element separator, so this marker only ever matches the tag ..
        iea_marker = 'IEA' + separators.element
        iea_start = candidate.find(iea_marker)

        if iea_start < 0:
            search_start = start + 1
            continue

        # .. and the trailer ends with the segment terminator.
        end = candidate.find(separators.terminator, iea_start)

        if end < 0:
            search_start = start + 1
            continue

        out = candidate[:end + 1]
        return out

# ################################################################################################################################

def render_document(text:'str') -> 'str':
    """ Renders the X12 document embedded in the given text to its human-readable form,
    or returns an empty string when the text carries no parseable interchange - the entry
    point the audit log details view calls with arbitrary event payloads.
    """
    raw = extract_x12(text)
    if not raw:
        return ''

    # Payload contents come from outside sources, so anything unparseable
    # simply has no rendered form - the raw view always remains available.
    try:
        interchange = parse_x12(raw)
    except (X12EnvelopeError, X12SyntaxError, ValueError):
        return ''

    out = render_interchange(interchange)
    return out

# ################################################################################################################################
# ################################################################################################################################

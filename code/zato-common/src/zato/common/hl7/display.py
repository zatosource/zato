# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HL7 display trees - turns a parsed HL7 v2 message into a structure the dashboard renders
# as a segment tree with human-readable field names, e.g. PID-5 Patient Name: SMITH^JOHN.
# Everything is resolved from the generated model - no HL7 parsing happens here.

from __future__ import annotations

# stdlib
import re
from typing import NamedTuple

# Zato
from zato.common.hl7.audit import get_control_id, get_message_type
from zato.hl7v2.base import HL7Field, _collect_raw_segments
from zato.hl7v2.registry import get_segment_class
from zato.hl7v2.v2_9.semantic_names import SEMANTIC_NAMES

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    from zato.hl7v2.base import HL7Message
    any_ = any_
    anylist = anylist
    HL7Message = HL7Message
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class _FieldDetails(NamedTuple):
    name: str
    datatype: str

# ################################################################################################################################

field_details_dict = dict[int, _FieldDetails]

# Field names and datatypes per segment, resolved from the model once and reused
_field_details_cache:'dict[str, field_details_dict]' = {}

# What an ER7 segment line looks like - a three-character segment id followed by the field separator
_segment_line_pattern = re.compile('^[A-Z][A-Z0-9]{2}\\|')

# ################################################################################################################################
# ################################################################################################################################

def _to_label(name:'str') -> 'str':
    """ Turns a model attribute name into a display label, e.g. patient_name becomes Patient Name.
    """
    parts = name.split('_')

    capitalized:'strlist' = []

    for part in parts:
        capitalized.append(part.capitalize())

    out = ' '.join(capitalized)
    return out

# ################################################################################################################################

def _get_field_details(segment_id:'str') -> 'field_details_dict':
    """ Returns the field names and datatypes one segment declares, keyed by wire position.
    """
    if segment_id in _field_details_cache:
        out = _field_details_cache[segment_id]
        return out

    details:'field_details_dict' = {}

    # Unknown segments, such as site-specific Z-segments without a class, declare no fields at all.
    segment_class = get_segment_class(segment_id)

    if segment_class is not None:
        for name in dir(segment_class):
            attribute = getattr(segment_class, name)
            if isinstance(attribute, HL7Field):
                details[attribute.position] = _FieldDetails(name, attribute.datatype)

    _field_details_cache[segment_id] = details

    out = details
    return out

# ################################################################################################################################
# ################################################################################################################################

def _join_component(subcomponents:'strlist') -> 'str':
    """ Joins one component's subcomponents back into its wire form.
    """
    out = '&'.join(subcomponents)
    return out

# ################################################################################################################################

def _build_repetition_node(reference:'str', datatype:'str', repetition:'any_') -> 'stranydict':
    """ Builds the display node of one field repetition - its wire value plus a named node
    per component when the repetition has more than one.
    """

    # The wire value of each component first, they feed both levels of the node ..
    component_values:'strlist' = []

    for component in repetition:
        component_value = _join_component(component)
        component_values.append(component_value)

    value = '^'.join(component_values)

    # .. a single-component repetition is a scalar and needs no children ..
    components:'anylist' = []

    component_count = len(repetition)
    has_multiple_components = component_count > 1

    if has_multiple_components:

        # .. component names come from the datatype's semantic names,
        # and an unknown datatype simply has none ..
        component_names = SEMANTIC_NAMES.get(datatype)
        if component_names is None:
            component_names = {}

        for index, component_value in enumerate(component_values):

            # .. empty components are noise in a display tree ..
            if not component_value:
                continue

            component_position = index + 1
            component_reference = f'{reference}.{component_position}'

            # .. a component past the named ones keeps its wire reference as the label ..
            if component_name := component_names.get(component_position):
                component_label = _to_label(component_name)
            else:
                component_name = ''
                component_label = component_reference

            components.append({
                'position': component_position,
                'reference': component_reference,
                'name': component_name,
                'label': component_label,
                'value': component_value,
            })

    out = {'value': value, 'components': components}
    return out

# ################################################################################################################################

def _build_field_node(segment_id:'str', position:'int', field_data:'any_', field_details:'field_details_dict') -> 'stranydict':
    """ Builds the display node of one populated field, with all its repetitions.
    """
    reference = f'{segment_id}-{position}'

    # A field the model does not declare keeps its wire reference as the label
    if details := field_details.get(position):
        name = details.name
        label = _to_label(name)
        datatype = details.datatype
    else:
        name = ''
        label = reference
        datatype = ''

    # Each repetition becomes its own node ..
    repetitions:'anylist' = []
    repetition_values:'strlist' = []

    for repetition in field_data:
        repetition_node = _build_repetition_node(reference, datatype, repetition)
        repetitions.append(repetition_node)
        repetition_values.append(repetition_node['value'])

    # .. and the field's own value is all of them in wire form.
    value = '~'.join(repetition_values)

    out = {
        'position': position,
        'reference': reference,
        'name': name,
        'label': label,
        'value': value,
        'repetitions': repetitions,
    }

    return out

# ################################################################################################################################

def _build_segment_node(raw_segment:'any_') -> 'stranydict':
    """ Builds the display node of one segment with all its populated fields.
    """
    segment_id = raw_segment.segment_id
    field_details = _get_field_details(segment_id)

    fields:'anylist' = []

    for index, field_data in enumerate(raw_segment.fields):

        # An empty field has nothing to display
        if not field_data:
            continue

        # MSH-1 is the field separator and is not stored in the parsed fields,
        # so the array starts at MSH-2 there
        if segment_id == 'MSH':
            position = index + 2
        else:
            position = index + 1

        field_node = _build_field_node(segment_id, position, field_data, field_details)

        # A field whose wire value is empty has nothing to display either
        if not field_node['value']:
            continue

        fields.append(field_node)

    out = {
        'segment_id': segment_id,
        'fields': fields,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_display_tree(msg:'HL7Message') -> 'stranydict':
    """ Turns a parsed HL7 message into its display tree - the header identification
    plus one node per segment in wire order, group-nested and trailing segments included.
    """

    # All segments in wire order, descending into groups ..
    raw_message = msg._raw_message
    segments = _collect_raw_segments(raw_message.items, [])

    # .. plus any segments the structure does not claim, such as Z-segments.
    segments.extend(raw_message.extra_segments)

    segment_nodes:'anylist' = []

    for raw_segment in segments:
        segment_node = _build_segment_node(raw_segment)
        segment_nodes.append(segment_node)

    out = {
        'structure_id': msg._structure_id,
        'msg_type': get_message_type(msg),
        'control_id': get_control_id(msg),
        'segments': segment_nodes,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_lenient_field_data(field_text:'str') -> 'anylist':
    """ Turns one field's wire text into the repetition, component and subcomponent
    structure the field node builder expects.
    """
    out:'anylist' = []

    for repetition_text in field_text.split('~'):

        components:'anylist' = []

        for component_text in repetition_text.split('^'):
            subcomponents = component_text.split('&')
            components.append(subcomponents)

        out.append(components)

    return out

# ################################################################################################################################

def build_segment_display_tree(data:'str') -> 'stranydict':
    """ Builds a display tree out of ER7 segment lines without parsing them as a complete
    message - fragments and in-progress edits get their fields named all the same.
    """
    segment_nodes:'anylist' = []

    for line in data.splitlines():

        line = line.strip()

        # Only lines shaped like a segment take part
        if not _segment_line_pattern.match(line):
            continue

        tokens = line.split('|')
        segment_id = tokens[0]
        field_details = _get_field_details(segment_id)

        fields:'anylist' = []

        for index, field_text in enumerate(tokens[1:]):

            # An empty field has nothing to display
            if not field_text:
                continue

            # MSH-1 is the field separator itself, so the first token after the id is MSH-2 ..
            is_encoding_characters = False

            if segment_id == 'MSH':
                position = index + 2

                # .. and MSH-2 is the encoding characters, one opaque value that must not
                # be split by the very separators it declares.
                if position == 2:
                    is_encoding_characters = True
            else:
                position = index + 1

            if is_encoding_characters:
                field_data = [[[field_text]]]
            else:
                field_data = _build_lenient_field_data(field_text)

            field_node = _build_field_node(segment_id, position, field_data, field_details)
            fields.append(field_node)

        segment_node = {
            'segment_id': segment_id,
            'fields': fields,
        }

        segment_nodes.append(segment_node)

    out = {'segments': segment_nodes}
    return out

# ################################################################################################################################
# ################################################################################################################################

# How far each level of the rendered tree is indented
_render_field_indent = '  '
_render_component_indent = '      '

def _append_segment_lines(segment:'stranydict', lines:'strlist') -> 'None':
    """ Appends one segment block's rendered lines - the segment id and each field
    with its components underneath.
    """
    lines.append(segment['segment_id'])

    for field in segment['fields']:

        lines.append('{}{}  {}: {}'.format(_render_field_indent, field['reference'], field['label'], field['value']))

        # Components appear under their field, one per line
        for repetition in field['repetitions']:
            for component in repetition['components']:
                lines.append('{}{}  {}: {}'.format(
                    _render_component_indent, component['reference'], component['label'], component['value']))

# ################################################################################################################################

def render_display_text(tree:'stranydict') -> 'str':
    """ Renders a display tree as indented plain text - the parsed tab of the details
    overlay and any other plain-text consumer show the same segment tree the same way.
    """

    lines:'strlist' = []

    # The header line names the message
    lines.append('{} (control id {})'.format(tree['msg_type'], tree['control_id']))

    for segment in tree['segments']:

        # A blank line separates each segment block
        lines.append('')
        _append_segment_lines(segment, lines)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def render_segments_text(tree:'stranydict') -> 'str':
    """ Renders a segment-only display tree as indented plain text - there is no header
    line because a fragment has no message identity to name it with.
    """

    lines:'strlist' = []

    for segment in tree['segments']:

        # A blank line separates each segment block after the first one
        if lines:
            lines.append('')

        _append_segment_lines(segment, lines)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_and_render(data:'str') -> 'str':
    """ Parses ER7 text and renders its display tree as indented plain text.
    Text that does not parse as a complete message renders segment by segment instead,
    so fragments and in-progress edits display too - only text with no segment lines
    at all renders as an empty string.
    """

    # Imported here because this convenience is the module's only parsing entry point -
    # everything else works on messages already parsed by the caller.
    from zato.hl7v2 import parse_hl7

    # Only a complete message opens with its header segment - anything else is a fragment
    # and goes segment by segment, the full parser would misattribute its fields otherwise.
    stripped = data.lstrip()

    if not stripped.startswith('MSH|'):
        tree = build_segment_display_tree(data)
        out = render_segments_text(tree)
        return out

    try:
        message = parse_hl7(data, validate=False)
        tree = build_display_tree(message)
    except Exception:

        # A header that still does not parse renders segment by segment too
        tree = build_segment_display_tree(data)
        out = render_segments_text(tree)
        return out

    out = render_display_text(tree)
    return out

# ################################################################################################################################
# ################################################################################################################################

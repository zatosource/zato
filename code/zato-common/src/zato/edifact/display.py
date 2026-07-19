# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# EDIFACT display trees - turns wire text into the same segment display tree HL7 uses,
# with element names resolved from the typed segment classes, e.g. UNB-2 Sender: BANK123:ZZ.
# The shared shape means the text and grid renderers from the HL7 modules apply as-is,
# both formats being segment-based and reading the same way once parsed.

from __future__ import annotations

# stdlib
import re
from typing import NamedTuple

# Zato
from zato.common.hl7.display import render_segments_text
from zato.common.hl7.grid import display_tree_to_grid_nodes
from zato.edi.base import EDIComponent, EDIElement, get_composite_class
from zato.edifact.service import UNB, UNH, UNT, UNZ
from zato.edifact.syntax import UNA_Tag, parse_segments, parse_una
from zato.edifact.nl.segments import (
    ADD, AFD, ARA, ART, BEP, BLG, COM, CON, DET, GGA, GGO, IDE, KOP, NUB, OND, OPB, OPM, OPU, PAD, PID, REF, SEC, SPE,
    TXT, VRG, VRS, ZKH
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    any_ = any_
    anylist = anylist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class _ElementDetails(NamedTuple):
    name: str
    composite: str

# ################################################################################################################################

element_details_dict = dict[int, _ElementDetails]
component_names_dict = dict[int, str]

# Element names per segment tag, resolved from the typed classes once and reused
_element_details_cache:'dict[str, element_details_dict]' = {}

# Component names per composite class, resolved once and reused
_component_names_cache:'dict[str, component_names_dict]' = {}

# What an EDIFACT segment tag looks like - three uppercase letters
_segment_tag_pattern = re.compile('^[A-Z]{3}$')

# The typed segment classes whose element names feed the display tree - the service
# segments plus the Medeur dialect ones, whose tags do not collide with anything else.
_typed_segment_list = [
    UNB, UNH, UNT, UNZ,
    ADD, AFD, ARA, ART, BEP, BLG, COM, CON, DET, GGA, GGO, IDE, KOP, NUB, OND, OPB, OPM, OPU, PAD, PID, REF, SEC, SPE,
    TXT, VRG, VRS, ZKH,
]

_typed_segments:'dict[str, type]' = {}

for _segment_class in _typed_segment_list:
    _typed_segments[_segment_class._segment_tag] = _segment_class

# ################################################################################################################################
# ################################################################################################################################

def _to_label(name:'str') -> 'str':
    """ Turns a model attribute name into a display label, e.g. control_reference becomes Control Reference.
    """
    parts = name.split('_')

    capitalized:'strlist' = []

    for part in parts:
        capitalized.append(part.capitalize())

    out = ' '.join(capitalized)
    return out

# ################################################################################################################################

def _get_element_details(tag:'str') -> 'element_details_dict':
    """ Returns the element names one segment declares, keyed by wire position.
    """
    if tag in _element_details_cache:
        out = _element_details_cache[tag]
        return out

    details:'element_details_dict' = {}

    # A tag without a typed class, such as a standard UN segment
    # not modelled here, declares no elements at all.
    segment_class = _typed_segments.get(tag)

    if segment_class is not None:
        for name in dir(segment_class):
            attribute = getattr(segment_class, name)
            if isinstance(attribute, EDIElement):
                composite_name = attribute.composite
                if composite_name is None:
                    composite_name = ''
                details[attribute.position] = _ElementDetails(name, composite_name)

    _element_details_cache[tag] = details

    out = details
    return out

# ################################################################################################################################

def _get_component_names(composite_name:'str') -> 'component_names_dict':
    """ Returns the component names one composite declares, keyed by wire position -
    a simple element without a composite has none.
    """
    if composite_name in _component_names_cache:
        out = _component_names_cache[composite_name]
        return out

    names:'component_names_dict' = {}

    if composite_name:
        composite_class = get_composite_class(composite_name)

        if composite_class is not None:
            for name in dir(composite_class):
                attribute = getattr(composite_class, name)
                if isinstance(attribute, EDIComponent):
                    names[attribute.position] = name

    _component_names_cache[composite_name] = names

    out = names
    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_element_node(tag:'str', position:'int', components:'strlist', element_details:'element_details_dict') -> 'stranydict':
    """ Builds the display node of one data element - its wire value plus a named node
    per component when the element has more than one.
    """
    reference = f'{tag}-{position}'

    # An element the model does not declare keeps its wire reference as the label
    if details := element_details.get(position):
        name = details.name
        label = _to_label(name)
        composite_name = details.composite
    else:
        name = ''
        label = reference
        composite_name = ''

    value = ':'.join(components)

    # A single-component element is a scalar and needs no children ..
    component_nodes:'anylist' = []

    component_count = len(components)
    has_multiple_components = component_count > 1

    if has_multiple_components:

        component_names = _get_component_names(composite_name)

        for index, component_value in enumerate(components):

            # .. empty components are noise in a display tree ..
            if not component_value:
                continue

            component_position = index + 1
            component_reference = f'{reference}.{component_position}'

            # .. a component past the named ones keeps its wire reference as the label.
            if component_name := component_names.get(component_position):
                component_label = _to_label(component_name)
            else:
                component_name = ''
                component_label = component_reference

            component_nodes.append({
                'position': component_position,
                'reference': component_reference,
                'name': component_name,
                'label': component_label,
                'value': component_value,
            })

    # EDIFACT elements do not repeat the way HL7 fields do, so each one
    # is a single repetition in the shared display-tree shape
    repetition = {'value': value, 'components': component_nodes}

    out = {
        'position': position,
        'reference': reference,
        'name': name,
        'label': label,
        'value': value,
        'repetitions': [repetition],
    }

    return out

# ################################################################################################################################

def _build_segment_node(raw_segment:'any_') -> 'stranydict':
    """ Builds the display node of one segment with all its populated elements.
    """
    tag = raw_segment.tag
    element_details = _get_element_details(tag)

    # Medeur repeat counters ride on the tag, the way the wire reads
    if raw_segment.counters:
        counters_text = ':'.join(raw_segment.counters)
        segment_id = f'{tag}:{counters_text}'
    else:
        segment_id = tag

    fields:'anylist' = []

    for index, components in enumerate(raw_segment.elements):

        position = index + 1
        element_node = _build_element_node(tag, position, components, element_details)

        # An element whose wire value is empty has nothing to display
        if not element_node['value']:
            continue

        fields.append(element_node)

    out = {
        'segment_id': segment_id,
        'fields': fields,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_display_tree(data:'str') -> 'stranydict':
    """ Builds the display tree of EDIFACT wire text - one node per segment in wire order,
    lines that are not shaped like segments left out, so fragments display too.
    """
    separators, rest = parse_una(data)

    segment_nodes:'anylist' = []

    # A UNA advice shows as its own leaf, its service characters one opaque value
    # that must not be split by the very separators it declares
    rest_length = len(rest)
    data_length = len(data)

    if rest_length != data_length:

        consumed = data_length - rest_length
        service_characters = data[len(UNA_Tag):consumed]

        una_repetition = {'value': service_characters, 'components': []}
        una_field = {
            'position': 1,
            'reference': 'UNA-1',
            'name': 'service_characters',
            'label': 'Service Characters',
            'value': service_characters,
            'repetitions': [una_repetition],
        }

        segment_nodes.append({'segment_id': UNA_Tag, 'fields': [una_field]})

    raw_segments = parse_segments(rest, separators)

    for raw_segment in raw_segments:

        # Only tags shaped like segment tags take part - anything else is not EDIFACT
        if not _segment_tag_pattern.match(raw_segment.tag):
            continue

        segment_node = _build_segment_node(raw_segment)
        segment_nodes.append(segment_node)

    out = {'segments': segment_nodes}
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_and_build(data:'str') -> 'stranydict':
    """ Parses EDIFACT wire text into both of its dashboard views - the indented text
    rendering and the grid view nodes, each empty when nothing parses at all.
    """
    tree = build_display_tree(data)

    pretty_text = render_segments_text(tree)
    grid_nodes = display_tree_to_grid_nodes(tree)

    out = {'pretty_text': pretty_text, 'tree': grid_nodes}
    return out

# ################################################################################################################################
# ################################################################################################################################

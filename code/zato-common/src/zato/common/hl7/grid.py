# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HL7 grid views - turns a display tree from zato.common.hl7.display into the generic
# name/value/children nodes the dashboard's grid renderer consumes for every format.

from __future__ import annotations

# Zato
from zato.common.hl7.display import parse_display_tree, render_display_text, render_segments_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def _grid_node(name:'str', value:'str') -> 'stranydict':
    """ Builds one generic grid view node.
    """
    out = {'name': name, 'value': value, 'kind': 'element', 'children': []}
    return out

# ################################################################################################################################

def _component_to_grid_node(component:'stranydict') -> 'stranydict':
    """ Turns one component's display node into a grid leaf.
    """

    # An unnamed component already carries its wire reference as the label
    if component['name']:
        name = '{} {}'.format(component['reference'], component['label'])
    else:
        name = component['label']

    out = _grid_node(name, component['value'])
    return out

# ################################################################################################################################

def _field_to_grid_node(field:'stranydict') -> 'stranydict':
    """ Turns one field's display node into a grid node - components become children,
    repeated fields become one child per repetition.
    """

    # A field the model does not declare has its wire reference as its whole name
    if field['name']:
        name = '{} {}'.format(field['reference'], field['label'])
    else:
        name = field['reference']

    # The encoding characters are one opaque value that must not be split
    # by the very separators it declares
    if field['reference'] == 'MSH-2':
        out = _grid_node(name, field['value'])
        return out

    node = _grid_node(name, '')

    repetitions = field['repetitions']
    repetition_count = len(repetitions)

    # A single repetition hangs its components right off the field ..
    if repetition_count == 1:

        first_repetition = repetitions[0]
        components = first_repetition['components']

        if components:
            for component in components:
                component_node = _component_to_grid_node(component)
                node['children'].append(component_node)
        else:
            node['value'] = field['value']

    # .. while a repeated field shows one child per repetition, each named
    # after the field's reference the way repeated elements read in a document.
    else:
        for repetition in repetitions:

            repetition_node = _grid_node(field['reference'], '')
            components = repetition['components']

            if components:
                for component in components:
                    component_node = _component_to_grid_node(component)
                    repetition_node['children'].append(component_node)
            else:
                repetition_node['value'] = repetition['value']

            node['children'].append(repetition_node)

    out = node
    return out

# ################################################################################################################################

def display_tree_to_grid_nodes(tree:'stranydict') -> 'anylist':
    """ Turns a display tree into generic grid view nodes - one node per segment,
    and a complete message gets a root named the way the text header reads.
    """

    segment_nodes:'anylist' = []

    for segment in tree['segments']:

        segment_node = _grid_node(segment['segment_id'], '')

        for field in segment['fields']:
            field_node = _field_to_grid_node(field)
            segment_node['children'].append(field_node)

        segment_nodes.append(segment_node)

    # A fragment has no message identity, its segments are the top level
    if 'msg_type' not in tree:
        out = segment_nodes
        return out

    root_name = '{} (control id {})'.format(tree['msg_type'], tree['control_id'])
    root = _grid_node(root_name, '')
    root['children'] = segment_nodes

    out = [root]
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_and_build(data:'str') -> 'stranydict':
    """ Parses ER7 text into both of its dashboard views - the indented text rendering
    and the grid view nodes, each empty when nothing parses at all.
    """
    tree, is_complete = parse_display_tree(data)

    if is_complete:
        parsed_text = render_display_text(tree)
    else:
        parsed_text = render_segments_text(tree)

    grid_nodes = display_tree_to_grid_nodes(tree)

    out = {'parsed_text': parsed_text, 'parsed_tree': grid_nodes}
    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# FHIR display trees - turns a FHIR resource, already parsed from JSON, into a structure
# the dashboard renders as a labeled tree, with OperationOutcome issues summarized
# separately because they are what an operator reads first when a FHIR call fails.

from __future__ import annotations

# Zato
from zato.fhir_r4_0_1_core import py_to_label

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    any_ = any_
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The resource type whose issues get their own summary in the display tree
_operation_outcome = 'OperationOutcome'

# ################################################################################################################################
# ################################################################################################################################

def _build_node(name:'str', label:'str', value:'any_') -> 'stranydict':
    """ Builds the display node of one element - a dict fans out into one child per key,
    a list into one child per item and a scalar carries its value directly.
    """

    # Our response to produce
    node:'stranydict' = {
        'name': name,
        'label': label,
        'value': None,
        'children': [],
    }

    # A complex element - one child per key, labeled from its camelCase name ..
    if isinstance(value, dict):
        for key, item in value.items():
            child = _build_node(key, py_to_label(key), item)
            node['children'].append(child)

    # .. a repeating element - one child per item, labeled with its 1-based position ..
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child_name = f'{name}[{index}]'
            child_label = f'{label} {index + 1}'
            child = _build_node(child_name, child_label, item)
            node['children'].append(child)

    # .. and a primitive keeps its value as-is, native types included.
    else:
        node['value'] = value

    return node

# ################################################################################################################################

def _build_issue_summaries(issues:'anylist') -> 'anylist':
    """ Summarizes OperationOutcome issues down to what an operator reads first -
    the severity, the code and the most specific human-readable text the issue carries.
    """

    # Our response to produce
    out:'anylist' = []

    for issue in issues:

        # Diagnostics is the more specific text when the server sent one ..
        text = issue.get('diagnostics')

        # .. otherwise the coded details may carry a display text ..
        if text is None:
            details = issue.get('details')
            if details is not None:
                text = details.get('text')

        # .. and some servers send neither.
        if text is None:
            text = ''

        out.append({
            'severity': issue['severity'],
            'code': issue['code'],
            'text': text,
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_display_tree(resource:'stranydict') -> 'stranydict':
    """ Turns a FHIR resource, already parsed from JSON, into its display tree - the resource type
    as the header plus one labeled node per element, and for an OperationOutcome also
    a summary of its issues.
    """
    resource_type = resource['resourceType']

    # One node per element, in document order, with the type itself lifted into the header
    nodes:'anylist' = []

    for key, value in resource.items():
        if key == 'resourceType':
            continue
        node = _build_node(key, py_to_label(key), value)
        nodes.append(node)

    out = {
        'resource_type': resource_type,
        'label': py_to_label(resource_type),
        'nodes': nodes,
    }

    # A failed call's outcome gets its issues summarized so the renderer
    # does not dig through the tree for them
    if resource_type == _operation_outcome:
        out['issues'] = _build_issue_summaries(resource['issue'])

    return out

# ################################################################################################################################
# ################################################################################################################################

# How far each level of the rendered tree is indented
_render_indent = '  '

def _render_node(node:'stranydict', depth:'int', lines:'anylist') -> 'None':
    """ Renders one display node as an indented line, descending into its children.
    """
    indent = _render_indent * depth

    # A scalar carries its value on the same line, a container is a header for its children
    if node['children']:
        lines.append('{}{}:'.format(indent, node['label']))
        for child in node['children']:
            _render_node(child, depth + 1, lines)
    else:
        lines.append('{}{}: {}'.format(indent, node['label'], node['value']))

# ################################################################################################################################

def render_display_text(tree:'stranydict') -> 'str':
    """ Renders a FHIR display tree as indented plain text - the same shape
    the HL7 renderer produces, so both parsed views read alike.
    """

    lines:'anylist' = []

    # The header line names the resource
    lines.append(tree['label'])

    # An OperationOutcome's issues come first - they are what an operator reads first
    if 'issues' in tree:
        lines.append('')
        for issue in tree['issues']:
            lines.append('{}{} ({}): {}'.format(_render_indent, issue['severity'], issue['code'], issue['text']))

    lines.append('')

    for node in tree['nodes']:
        _render_node(node, 1, lines)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_and_render(data:'str') -> 'str':
    """ Parses FHIR JSON text and renders its display tree as indented plain text -
    a payload that is not a FHIR resource renders as an empty string.
    """

    # stdlib, imported here because this convenience is the module's only JSON entry point
    import json

    try:
        resource = json.loads(data)
        tree = build_display_tree(resource)
    except Exception:
        return ''

    out = render_display_text(tree)
    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.document import Arity, Comparator_Arity, NodeKind, Value_Type_Datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The indent used for every content line under a block keyword.
_indent = '    '

# ################################################################################################################################
# ################################################################################################################################

def _render_string(value:'str') -> 'str':
    """ Renders a string literal in its canonical single-quoted form.
    """

    # Escape backslashes first so escaped quotes stay unambiguous ..
    escaped = value.replace('\\', '\\\\')

    # .. then escape the quote character itself.
    escaped = escaped.replace("'", "\\'")

    out = f"'{escaped}'"
    return out

# ################################################################################################################################

def render_value(node:'anydict') -> 'str':
    """ Renders a value node in its canonical text form.
    """
    kind = node['kind']

    # References render as their bare term ..
    if kind == NodeKind.Reference:
        out = node['term']

    # .. lists render in bracket form, item by item ..
    elif kind == NodeKind.List:
        parts = []
        for item in node['items']:
            part = render_value(item)
            parts.append(part)
        joined = ', '.join(parts)
        out = f'[{joined}]'

    # .. objects render as their Python-style mapping text ..
    elif kind == NodeKind.Object:
        out = repr(node['value'])

    # .. datetime literals keep their dedicated syntax ..
    elif node.get('value_type') == Value_Type_Datetime:
        value = node['value']
        out = f"d'{value}'"

    # .. and plain literals render by their type.
    else:
        value = node['value']
        if isinstance(value, bool):
            out = 'true' if value else 'false'
        elif isinstance(value, str):
            out = _render_string(value)
        else:
            out = repr(value)

    return out

# ################################################################################################################################

def render_condition(condition:'anydict') -> 'str':
    """ Renders a single condition in its canonical sentence form.
    """
    subject = condition['subject']
    comparator = condition['comparator']
    values = condition['values']
    arity = Comparator_Arity[comparator]

    # Comparators without values are just the sentence itself ..
    if arity == Arity.None_:
        out = f'{subject} {comparator}'

    # .. between renders its two boundaries joined by and ..
    elif arity == Arity.Two:
        lower = render_value(values[0])
        upper = render_value(values[1])
        out = f'{subject} {comparator} {lower} and {upper}'

    # .. and everything else renders its values comma-joined.
    else:
        parts = []
        for value in values:
            part = render_value(value)
            parts.append(part)
        joined = ', '.join(parts)
        out = f'{subject} {comparator} {joined}'

    return out

# ################################################################################################################################

def _render_assignments(actions:'dictlist', lines:'strlist') -> 'None':
    """ Renders a list of action nodes as indented assignment lines.
    """
    for action in actions:
        value = render_value(action['value'])
        lines.append(f'{_indent}{action["target"]} = {value}')

# ################################################################################################################################

def render_document(document:'anydict') -> 'str':
    """ Renders a rule document in its canonical text form - the inverse of parsing.
    """
    lines = []

    # The name opens the rule ..
    lines.append('rule')
    lines.append(f'{_indent}{document["name"]}')

    # .. docs follow, line by line, when present ..
    if document['docs']:
        lines.append('docs')
        for docs_line in document['docs'].split('\n'):
            lines.append(f'{_indent}{docs_line}')

    # .. defaults are assignments of concrete values ..
    if document['defaults']:
        lines.append('defaults')
        for name, node in document['defaults'].items():
            value = render_value(node)
            lines.append(f'{_indent}{name} = {value}')

    # .. each condition takes one line, with its joiner at the end ..
    lines.append('when')
    joiners = document['joiners']
    for index, condition in enumerate(document['conditions']):
        text = render_condition(condition)
        if index < len(joiners):
            text = f'{text} {joiners[index]}'
        lines.append(f'{_indent}{text}')

    # .. then actions always follow ..
    lines.append('then')
    _render_assignments(document['then'], lines)

    # .. and else actions close the rule when present.
    if document['else']:
        lines.append('else')
        _render_assignments(document['else'], lines)

    out = '\n'.join(lines) + '\n'
    return out

# ################################################################################################################################

def render_documents(documents:'strdict') -> 'str':
    """ Renders multiple rule documents as one rules file.
    """
    parts = []
    for document in documents.values():
        part = render_document(document)
        parts.append(part)

    out = '\n'.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

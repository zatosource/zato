# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

class NodeKind:
    """ Kinds of tagged value nodes that a rule document may contain.
    """
    Literal   = 'literal'
    List      = 'list'
    Object    = 'object'
    Reference = 'reference'

# ################################################################################################################################
# ################################################################################################################################

class Comparator:
    """ Canonical comparator names stored in rule documents.
    """
    Is             = 'is'
    Is_Not         = 'is not'
    Is_Less_Than   = 'is less than'
    Is_At_Most     = 'is at most'
    Is_At_Least    = 'is at least'
    Is_More_Than   = 'is more than'
    Is_Between     = 'is between'
    Is_One_Of      = 'is one of'
    Is_Not_One_Of  = 'is not one of'
    Matches        = 'matches'
    Is_True        = 'is true'
    Is_False       = 'is false'

# ################################################################################################################################
# ################################################################################################################################

class Arity:
    """ How many values each comparator expects.
    """
    None_ = 'none'
    One   = 'one'
    Two   = 'two'
    Many  = 'many'

# ################################################################################################################################
# ################################################################################################################################

# A literal node whose value is the ISO-8601 text of a datetime carries this marker.
Value_Type_Datetime = 'datetime'

# References to defaults use this prefix in their term names.
Default_Prefix = 'default.'

# How many values each canonical comparator expects.
Comparator_Arity = {
    Comparator.Is:            Arity.One,
    Comparator.Is_Not:        Arity.One,
    Comparator.Is_Less_Than:  Arity.One,
    Comparator.Is_At_Most:    Arity.One,
    Comparator.Is_At_Least:   Arity.One,
    Comparator.Is_More_Than:  Arity.One,
    Comparator.Is_Between:    Arity.Two,
    Comparator.Is_One_Of:     Arity.Many,
    Comparator.Is_Not_One_Of: Arity.Many,
    Comparator.Matches:       Arity.One,
    Comparator.Is_True:       Arity.None_,
    Comparator.Is_False:      Arity.None_,
}

# Symbol aliases accepted by the parser, each mapping to its canonical comparator.
Comparator_Aliases = {
    '==':     Comparator.Is,
    '!=':     Comparator.Is_Not,
    '<':      Comparator.Is_Less_Than,
    '<=':     Comparator.Is_At_Most,
    '>=':     Comparator.Is_At_Least,
    '>':      Comparator.Is_More_Than,
    'in':     Comparator.Is_One_Of,
    'not in': Comparator.Is_Not_One_Of,
    '=~':     Comparator.Matches,
}

# Canonical comparators that compile to a plain binary operator in the when expression.
_comparator_operators = {
    Comparator.Is:           '==',
    Comparator.Is_Not:       '!=',
    Comparator.Is_Less_Than: '<',
    Comparator.Is_At_Most:   '<=',
    Comparator.Is_At_Least:  '>=',
    Comparator.Is_More_Than: '>',
}

# ################################################################################################################################
# ################################################################################################################################

def literal_node(value:'any_', value_type:'str'='') -> 'anydict':
    """ Builds a literal value node, optionally marked with a value type such as datetime.
    """
    out = {'kind': NodeKind.Literal, 'value': value}
    if value_type:
        out['value_type'] = value_type

    return out

# ################################################################################################################################

def list_node(items:'dictlist') -> 'anydict':
    """ Builds a list node holding other value nodes.
    """
    out = {'kind': NodeKind.List, 'items': items}
    return out

# ################################################################################################################################

def object_node(value:'anydict') -> 'anydict':
    """ Builds an object node holding a plain mapping.
    """
    out = {'kind': NodeKind.Object, 'value': value}
    return out

# ################################################################################################################################

def reference_node(term:'str') -> 'anydict':
    """ Builds a reference node pointing to another term or to a default.
    """
    out = {'kind': NodeKind.Reference, 'term': term}
    return out

# ################################################################################################################################

def reference_key(term:'str') -> 'str':
    """ Returns the data key a reference term resolves against, stripping the defaults prefix.
    """
    if term.startswith(Default_Prefix):
        out = term[len(Default_Prefix):]
    else:
        out = term

    return out

# ################################################################################################################################
# ################################################################################################################################

def _compile_literal(node:'anydict') -> 'str':
    """ Compiles a literal node into a when-expression fragment.
    """
    value = node['value']

    # Datetime literals keep their dedicated syntax ..
    if node.get('value_type') == Value_Type_Datetime:
        out = f"d'{value}'"

    # .. booleans use the lowercase keywords ..
    elif isinstance(value, bool):
        out = 'true' if value else 'false'

    # .. strings are double-quoted, with backslashes doubled because the engine
    # .. unicode-escape-decodes string literals, and with double quotes escaped ..
    elif isinstance(value, str):
        escaped = value.replace('\\', '\\\\')
        escaped = escaped.replace('"', '\\"')
        out = f'"{escaped}"'

    # .. and numbers render as their plain representation.
    else:
        out = repr(value)

    return out

# ################################################################################################################################

def compile_value(node:'anydict') -> 'str':
    """ Compiles a value node into a when-expression fragment.
    """
    kind = node['kind']

    # References compile to the bare data key they point to ..
    if kind == NodeKind.Reference:
        out = reference_key(node['term'])

    # .. lists compile item by item into an array literal ..
    elif kind == NodeKind.List:
        parts = []
        for item in node['items']:
            part = compile_value(item)
            parts.append(part)
        joined = ', '.join(parts)
        out = f'[{joined}]'

    # .. and everything else is a literal.
    else:
        out = _compile_literal(node)

    return out

# ################################################################################################################################

def _compile_is_true(condition:'anydict') -> 'str':
    """ Compiles an is-true condition.
    """
    subject = condition['subject']

    out = f'{subject} == true'
    return out

# ################################################################################################################################

def _compile_is_false(condition:'anydict') -> 'str':
    """ Compiles an is-false condition.
    """
    subject = condition['subject']

    out = f'{subject} == false'
    return out

# ################################################################################################################################

def _compile_between(condition:'anydict') -> 'str':
    """ Compiles a between condition into a bounds check pair.
    """
    subject = condition['subject']
    values = condition['values']

    # Compile both boundary values first ..
    lower = compile_value(values[0])
    upper = compile_value(values[1])

    # .. and wrap the pair so the joiner precedence around it never changes.
    out = f'({subject} >= {lower} and {subject} <= {upper})'
    return out

# ################################################################################################################################

def _compile_membership(condition:'anydict', keyword:'str') -> 'str':
    """ Compiles a membership condition using the given membership keyword.
    """
    subject = condition['subject']
    values = condition['values']

    # A single reference means membership in the collection it points to ..
    value_count = len(values)
    first_value = values[0]

    if value_count == 1:
        if first_value['kind'] == NodeKind.Reference:
            collection = compile_value(first_value)

            out = f'{subject} {keyword} {collection}'
            return out

    # .. otherwise the values compile into an array literal.
    parts = []
    for value in values:
        part = compile_value(value)
        parts.append(part)
    joined = ', '.join(parts)

    out = f'{subject} {keyword} [{joined}]'
    return out

# ################################################################################################################################

def _compile_one_of(condition:'anydict') -> 'str':
    """ Compiles an is-one-of condition.
    """
    out = _compile_membership(condition, 'in')
    return out

# ################################################################################################################################

def _compile_not_one_of(condition:'anydict') -> 'str':
    """ Compiles an is-not-one-of condition.
    """
    out = _compile_membership(condition, 'not in')
    return out

# ################################################################################################################################

def _compile_matches(condition:'anydict') -> 'str':
    """ Compiles a regex matching condition.
    """
    subject = condition['subject']
    values = condition['values']

    pattern = _compile_literal(values[0])

    out = f'{subject} =~ {pattern}'
    return out

# ################################################################################################################################

# Comparators that need their own compilation shape, everything else is a plain binary operator.
_condition_compilers = {
    Comparator.Is_True:       _compile_is_true,
    Comparator.Is_False:      _compile_is_false,
    Comparator.Is_Between:    _compile_between,
    Comparator.Is_One_Of:     _compile_one_of,
    Comparator.Is_Not_One_Of: _compile_not_one_of,
    Comparator.Matches:       _compile_matches,
}

# ################################################################################################################################

def compile_condition(condition:'anydict') -> 'str':
    """ Compiles a single condition into a when-expression fragment.
    """
    comparator = condition['comparator']

    # Comparators with a dedicated shape have their own compiler ..
    if compiler := _condition_compilers.get(comparator):
        out = compiler(condition)

    # .. everything else is subject, operator, value.
    else:
        subject = condition['subject']
        operator = _comparator_operators[comparator]
        value = compile_value(condition['values'][0])
        out = f'{subject} {operator} {value}'

    return out

# ################################################################################################################################

def compile_when(document:'anydict') -> 'str':
    """ Compiles a document's conditions and joiners into the when expression the engine evaluates.
    """
    conditions = document['conditions']
    joiners = document['joiners']

    # Interleave each compiled condition with the joiner that follows it ..
    parts = []
    for index, condition in enumerate(conditions):
        fragment = compile_condition(condition)
        parts.append(fragment)
        if index < len(joiners):
            parts.append(joiners[index])

    # .. and the expression is their space-joined concatenation.
    out = ' '.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

def resolve_value_node(node:'anydict', data:'anydict') -> 'any_':
    """ Resolves a value node against input data, returning a plain Python value.
    """
    kind = node['kind']

    # References read from the input data, following dotted paths ..
    if kind == NodeKind.Reference:
        out = _resolve_reference(node['term'], data)

    # .. lists resolve item by item ..
    elif kind == NodeKind.List:
        out = []
        for item in node['items']:
            resolved = resolve_value_node(item, data)
            out.append(resolved)

    # .. objects are used as they are ..
    elif kind == NodeKind.Object:
        out = node['value']

    # .. datetime literals become real datetime objects ..
    elif node.get('value_type') == Value_Type_Datetime:
        out = datetime.fromisoformat(node['value'])

    # .. and plain literals are used as they are.
    else:
        out = node['value']

    return out

# ################################################################################################################################

def _resolve_reference(term:'str', data:'anydict') -> 'any_':
    """ Resolves a reference term against input data, following dotted paths, returning None when absent.
    """
    key = reference_key(term)

    # Walk the dotted path one segment at a time ..
    current = data
    for part in key.split('.'):

        # .. a segment can only be followed through a mapping ..
        if not isinstance(current, dict):
            return None

        # .. and only if the mapping actually has it.
        if part not in current:
            return None

        current = current[part]

    return current

# ################################################################################################################################

def resolve_actions(actions:'dictlist', data:'anydict') -> 'strdict':
    """ Resolves a list of action nodes against input data into a target-to-value mapping.
    """
    out = {}
    for action in actions:
        value = resolve_value_node(action['value'], data)
        out[action['target']] = value

    return out

# ################################################################################################################################

def resolve_defaults(defaults:'anydict') -> 'strdict':
    """ Resolves default value nodes into plain Python values keyed by their names.
    """
    out = {}
    for name, node in defaults.items():
        out[name] = resolve_value_node(node, {})

    return out

# ################################################################################################################################
# ################################################################################################################################

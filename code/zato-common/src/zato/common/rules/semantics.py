# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.document import Default_Prefix, NodeKind, Value_Type_Datetime
from zato.common.rules.errors import Severity
from zato.common.rules.vocabulary import Comparators_By_Type, ErrorCode, Status_Deprecated, TermType, get_attribute, new_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# Term types that can be compared with each other through a reference.
_type_groups = {
    TermType.Number:       'number',
    TermType.Number_Range: 'number',
    TermType.Choice:       'text',
    TermType.Text:         'text',
    TermType.Yes_No:       'yes/no',
}

# ################################################################################################################################
# ################################################################################################################################

def _check_term(
    path:'str',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'anydict | None':
    """ Looks up a term used by a rule, reporting unknown terms as errors and deprecated ones as warnings.
    """
    attribute = get_attribute(vocabulary, path)

    # A term the vocabulary does not know cannot run ..
    if attribute is None:
        message = f'{path!r} is not a term of this vocabulary, the rule cannot run'
        errors.append(new_error(rule_name, block, path, ErrorCode.Unknown_Term, message))
        return None

    # .. and a deprecated one still runs but the author should know.
    if attribute['status'] == Status_Deprecated:
        message = f'{path} is deprecated - existing rules keep running but new rules should not use it'
        errors.append(new_error(rule_name, block, path, ErrorCode.Deprecated_Term, message, Severity.Warning))

    return attribute

# ################################################################################################################################
# ################################################################################################################################

def _is_number(value:'any_') -> 'bool':
    """ Returns True for numeric values - booleans are numbers to Python but not to a reader.
    """
    if isinstance(value, bool):
        out = False
    else:
        out = isinstance(value, (int, float))

    return out

# ################################################################################################################################

def _check_number(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a number term.
    """
    if not _is_number(value):
        message = f'{path} is a number, the value {value!r} is not'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))

# ################################################################################################################################

def _check_number_range(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a number range term, including the range's domain.
    """

    # The value has to be a number in the first place ..
    if not _is_number(value):
        message = f'{path} is a number, the value {value!r} is not'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))
        return

    # .. and the domain bounds the legal values.
    domain = attribute['domain']
    low = domain['low']
    high = domain['high']
    is_in_range = low <= value <= high

    if not is_in_range:
        message = f'{path} value {value} is outside {low} to {high}'
        errors.append(new_error(rule_name, block, path, ErrorCode.Out_Of_Range, message))

# ################################################################################################################################

def _check_choice(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a choice term.
    """

    # A choice value has to be text ..
    if not isinstance(value, str):
        message = f'{path} is a choice, the value {value!r} is not one of its texts'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))
        return

    # .. and one of the values the term declares.
    if value not in attribute['values']:
        choices = ', '.join(attribute['values'])
        message = f'{path} has no choice {value!r} - the choices are {choices}'
        errors.append(new_error(rule_name, block, path, ErrorCode.Choice_Value, message))

# ################################################################################################################################

def _check_text(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a text term.
    """
    if not isinstance(value, str):
        message = f'{path} is text, the value {value!r} is not'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))

# ################################################################################################################################

def _check_yes_no(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a yes/no term.
    """
    if not isinstance(value, bool):
        message = f'{path} is yes/no, the value {value!r} is neither'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))

# ################################################################################################################################

# Which check each term type runs on its literals.
_literal_checks = {
    TermType.Number:       _check_number,
    TermType.Number_Range: _check_number_range,
    TermType.Choice:       _check_choice,
    TermType.Text:         _check_text,
    TermType.Yes_No:       _check_yes_no,
}

# ################################################################################################################################

def _check_literal(
    path:'str',
    attribute:'anydict',
    node:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ Checks one literal value node against the type the term declares.
    """
    type_ = attribute['type']
    value = node['value']

    # Datetime literals have no term type to belong to.
    if node.get('value_type') == Value_Type_Datetime:
        message = f'A datetime value cannot be compared with {path}, whose type is {type_}'
        errors.append(new_error(rule_name, block, path, ErrorCode.Value_Type, message))
        return

    # Every term type runs its own check.
    check = _literal_checks[type_]
    check(path, attribute, value, rule_name, block, errors)

# ################################################################################################################################
# ################################################################################################################################

def _check_literal_node(
    subject:'str',
    attribute:'anydict',
    node:'anydict',
    document:'anydict',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ A literal node is checked against the subject's declared type.
    """
    _check_literal(subject, attribute, node, rule_name, block, errors)

# ################################################################################################################################

def _check_list_node(
    subject:'str',
    attribute:'anydict',
    node:'anydict',
    document:'anydict',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ A list node is checked item by item.
    """
    for item in node['items']:
        _check_value_node(subject, attribute, item, document, vocabulary, rule_name, block, errors)

# ################################################################################################################################

def _check_object_node(
    subject:'str',
    attribute:'anydict',
    node:'anydict',
    document:'anydict',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ Object nodes are dev-facing and opaque - the term types do not describe them, so there is nothing to check.
    """

# ################################################################################################################################

def _check_reference_node(
    subject:'str',
    attribute:'anydict',
    node:'anydict',
    document:'anydict',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ A reference node is checked for existence and for comparability with the subject.
    """
    term = node['term']

    # A default reference has to point to a default the rule declares.
    if term.startswith(Default_Prefix):
        default_name = term[len(Default_Prefix):]
        if default_name not in document['defaults']:
            message = f'{term!r} refers to a default the rule does not declare'
            errors.append(new_error(rule_name, block, term, ErrorCode.Unknown_Default, message))
        return

    # A term reference has to point to a known term ..
    other = _check_term(term, vocabulary, rule_name, block, errors)
    if other is None:
        return

    # .. and the two types have to be comparable with each other.
    subject_type = attribute['type']
    other_type = other['type']
    subject_group = _type_groups[subject_type]
    other_group = _type_groups[other_type]

    if subject_group != other_group:
        message = f'{subject} ({subject_type}) cannot be compared with {term} ({other_type})'
        errors.append(new_error(rule_name, block, term, ErrorCode.Reference_Type, message))

# ################################################################################################################################

# Which check each value node kind runs.
_value_node_checks = {
    NodeKind.Literal:   _check_literal_node,
    NodeKind.List:      _check_list_node,
    NodeKind.Object:    _check_object_node,
    NodeKind.Reference: _check_reference_node,
}

# ################################################################################################################################

def _check_value_node(
    subject:'str',
    attribute:'anydict',
    node:'anydict',
    document:'anydict',
    vocabulary:'anydict',
    rule_name:'str',
    block:'str',
    errors:'dictlist',
    ) -> 'None':
    """ Checks one value node used with the given subject term - each node kind runs its own check.
    """
    check = _value_node_checks[node['kind']]
    check(subject, attribute, node, document, vocabulary, rule_name, block, errors)

# ################################################################################################################################
# ################################################################################################################################

def validate_document(document:'anydict', vocabulary:'anydict') -> 'dictlist':
    """ Validates a parsed rule document against a vocabulary, returning a list of structured errors.

    The vocabulary is expected to have passed validate_vocabulary first - this function trusts its shape.
    The same checks guard the editor, the table cells, the scenario forms and the REST boundary,
    because they are all this one function.
    """
    errors = []
    rule_name = document['name']

    # Check each condition - the subject, the comparator against the subject's type, and every value.
    for condition in document['conditions']:
        subject = condition['subject']
        comparator = condition['comparator']

        attribute = _check_term(subject, vocabulary, rule_name, 'when', errors)
        if attribute is None:
            continue

        # The comparator has to make sense for the subject's type ..
        type_ = attribute['type']
        legal_comparators = Comparators_By_Type[type_]

        if comparator not in legal_comparators:
            message = f'{comparator!r} cannot be used with {subject}, whose type is {type_}'
            errors.append(new_error(rule_name, 'when', subject, ErrorCode.Comparator_Type, message))
            continue

        # .. and so does every value used with it.
        for node in condition['values']:
            _check_value_node(subject, attribute, node, document, vocabulary, rule_name, 'when', errors)

    # Check each action - the target term and the value assigned to it.
    for block in ('then', 'else'):
        for action in document[block]:
            target = action['target']

            attribute = _check_term(target, vocabulary, rule_name, block, errors)
            if attribute is None:
                continue

            _check_value_node(target, attribute, action['value'], document, vocabulary, rule_name, block, errors)

    return errors

# ################################################################################################################################
# ################################################################################################################################

def validate_data(data:'anydict', vocabulary:'anydict') -> 'dictlist':
    """ Validates input data against a vocabulary, returning a list of structured errors.

    Keys are the vocabulary's own dotted paths. Unknown fields and values of the wrong shape
    are reported in domain terms - this is the same validation path the editor and the REST
    boundary share, never a bare 400.
    """
    errors = []

    for path, value in data.items():
        attribute = get_attribute(vocabulary, path)

        # A field the vocabulary does not know is reported by name ..
        if attribute is None:
            message = f'{path!r} is not a field of this vocabulary'
            errors.append(new_error('', 'data', path, ErrorCode.Unknown_Field, message))
            continue

        # .. and a known one is checked exactly like a literal in a rule.
        node = {'kind': NodeKind.Literal, 'value': value}
        _check_literal(path, attribute, node, '', 'data', errors)

    return errors

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.rules.document import Comparator, Default_Prefix, NodeKind, Value_Type_Datetime
from zato.common.rules.errors import Severity

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anytuple, dictlist, generator_, strlist
    anytuple_gen = generator_[anytuple, None, None]

# ################################################################################################################################
# ################################################################################################################################

class TermType:
    """ The types a vocabulary attribute can have.
    """
    Number       = 'number'
    Number_Range = 'number range'
    Choice       = 'choice'
    Yes_No       = 'yes/no'
    Text         = 'text'

# All the types an attribute may declare.
Term_Types = {TermType.Number, TermType.Number_Range, TermType.Choice, TermType.Yes_No, TermType.Text}

# The status marking a term that keeps existing rules running but leaves every picker.
Status_Deprecated = 'deprecated'

# ################################################################################################################################
# ################################################################################################################################

class ErrorCode:
    """ Codes carried by structured vocabulary and semantic validation errors.
    """

    # Codes reported when validating a vocabulary itself.
    Bad_Name            = 'bad_name'
    Duplicate_Entity    = 'duplicate_entity'
    Duplicate_Attribute = 'duplicate_attribute'
    Duplicate_Phrase    = 'duplicate_phrase'
    Unknown_Type        = 'unknown_type'
    Missing_Values      = 'missing_values'
    Bad_Domain          = 'bad_domain'

    # Codes reported when validating a rule document against a vocabulary.
    Unknown_Term    = 'unknown_term'
    Deprecated_Term = 'deprecated_term'
    Comparator_Type = 'comparator_type'
    Value_Type      = 'value_type'
    Choice_Value    = 'choice_value'
    Out_Of_Range    = 'out_of_range'
    Unknown_Default = 'unknown_default'
    Reference_Type  = 'reference_type'

    # Codes reported when validating input data against a vocabulary.
    Unknown_Field = 'unknown_field'

# ################################################################################################################################
# ################################################################################################################################

# Comparators that make sense for number-valued terms.
_number_comparators = {
    Comparator.Is,
    Comparator.Is_Not,
    Comparator.Is_Less_Than,
    Comparator.Is_At_Most,
    Comparator.Is_At_Least,
    Comparator.Is_More_Than,
    Comparator.Is_Between,
    Comparator.Is_One_Of,
    Comparator.Is_Not_One_Of,
}

# Comparators that make sense for text-valued terms.
_text_comparators = {
    Comparator.Is,
    Comparator.Is_Not,
    Comparator.Matches,
    Comparator.Is_One_Of,
    Comparator.Is_Not_One_Of,
}

# Which comparators each term type accepts - declared once, enforced identically everywhere.
Comparators_By_Type = {
    TermType.Number:       _number_comparators,
    TermType.Number_Range: _number_comparators,
    TermType.Choice:       {Comparator.Is, Comparator.Is_Not, Comparator.Is_One_Of, Comparator.Is_Not_One_Of},
    TermType.Text:         _text_comparators,
    TermType.Yes_No:       {Comparator.Is, Comparator.Is_Not, Comparator.Is_True, Comparator.Is_False},
}

# Term types that can be compared with each other through a reference.
_type_groups = {
    TermType.Number:       'number',
    TermType.Number_Range: 'number',
    TermType.Choice:       'text',
    TermType.Text:         'text',
    TermType.Yes_No:       'yes/no',
}

# Splits camel-case boundaries when a phrase is derived from a term name.
_camel_boundary = re.compile(r'([a-z0-9])([A-Z])')

# Entity and attribute names have to be plain identifiers.
_name_pattern = re.compile(r'^[A-Za-z_]\w*$')

# ################################################################################################################################
# ################################################################################################################################

def _new_error(
    rule:'str',
    block:'str',
    field:'str',
    code:'str',
    message:'str',
    severity:'str' = Severity.Error,
    ) -> 'anydict':
    """ Builds a structured validation error, shaped like the parser's errors.
    """
    out = {
        'rule': rule,
        'block': block,
        'line': 0,
        'field': field,
        'code': code,
        'message': message,
        'severity': severity,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def term_words(name:'str') -> 'str':
    """ Turns a term name into its space-separated lowercase words, splitting camel case and underscores.
    """
    spaced = _camel_boundary.sub(r'\1 \2', name)
    spaced = spaced.replace('_', ' ')

    out = spaced.lower()
    return out

# ################################################################################################################################

def default_phrase(entity_name:'str', attribute_name:'str') -> 'str':
    """ Derives the readable phrase a term wears by default - sensible phrasing exists without any up-front work.
    """
    words = term_words(attribute_name)

    out = f'the {entity_name} {words}'
    return out

# ################################################################################################################################

def default_set_phrase(entity_name:'str', attribute_name:'str') -> 'str':
    """ Derives the default phrase for setting a term's value in an action.
    """
    phrase = default_phrase(entity_name, attribute_name)

    out = f'set {phrase} to'
    return out

# ################################################################################################################################
# ################################################################################################################################

def iter_attributes(vocabulary:'anydict') -> 'anytuple_gen':
    """ Yields every attribute in the vocabulary along with its full dotted path.
    """
    for entity in vocabulary['entities']:
        entity_name = entity['name']
        for attribute in entity['attributes']:
            path = entity_name + '.' + attribute['name']
            yield path, attribute

# ################################################################################################################################

def get_attribute(vocabulary:'anydict', path:'str') -> 'anydict | None':
    """ Looks up an attribute by its full dotted path, returning None when the vocabulary does not have it.
    """
    for candidate_path, attribute in iter_attributes(vocabulary):
        if candidate_path == path:
            out = attribute
            break
    else:
        out = None

    return out

# ################################################################################################################################

def picker_paths(vocabulary:'anydict') -> 'strlist':
    """ Returns the paths every picker offers - deprecated terms keep old rules running but never appear again.
    """
    out = []
    for path, attribute in iter_attributes(vocabulary):
        if attribute['status'] != Status_Deprecated:
            out.append(path)

    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_vocabulary(vocabulary:'anydict') -> 'dictlist':
    """ Validates the structure of a vocabulary document itself, returning a list of structured errors.

    Every attribute has to carry name, type, phrase and status, choices need their values,
    ranges need a coherent domain, and no two terms may share a phrase - two terms wearing
    the same words is exactly the ambiguity that makes rules unreadable.
    """
    errors = []

    # Phrases seen so far, each pointing back to the term that claimed it first.
    phrases_seen = {}

    # Entity names seen so far, to catch duplicates.
    entities_seen = set()

    for entity in vocabulary['entities']:
        entity_name = entity['name']

        # Entity names have to be identifiers ..
        if not _name_pattern.match(entity_name):
            message = f'Entity name is not a valid identifier -> {entity_name!r}'
            errors.append(_new_error('', 'vocabulary', entity_name, ErrorCode.Bad_Name, message))

        # .. and each may appear only once.
        if entity_name in entities_seen:
            message = f'Entity is defined more than once -> {entity_name}'
            errors.append(_new_error('', 'vocabulary', entity_name, ErrorCode.Duplicate_Entity, message))
        entities_seen.add(entity_name)

        # Attribute names seen within this entity, to catch duplicates.
        attributes_seen = set()

        for attribute in entity['attributes']:
            name = attribute['name']
            path = entity_name + '.' + name

            # Attribute names have to be identifiers ..
            if not _name_pattern.match(name):
                message = f'Attribute name is not a valid identifier -> {name!r}'
                errors.append(_new_error('', 'vocabulary', path, ErrorCode.Bad_Name, message))

            # .. and each may appear only once per entity.
            if name in attributes_seen:
                message = f'Attribute is defined more than once -> {path}'
                errors.append(_new_error('', 'vocabulary', path, ErrorCode.Duplicate_Attribute, message))
            attributes_seen.add(name)

            # The type has to be one of the term types.
            type_ = attribute['type']
            if type_ not in Term_Types:
                types = ', '.join(sorted(Term_Types))
                message = f'Unknown type {type_!r} for {path} - the types are {types}'
                errors.append(_new_error('', 'vocabulary', path, ErrorCode.Unknown_Type, message))

            # A choice without values cannot be picked from.
            if type_ == TermType.Choice:
                if not attribute.get('values'):
                    message = f'Choice term {path} has no values to choose from'
                    errors.append(_new_error('', 'vocabulary', path, ErrorCode.Missing_Values, message))

            # A range needs a coherent low-to-high domain.
            if type_ == TermType.Number_Range:
                domain = attribute.get('domain')

                # The domain itself and both of its bounds have to be present ..
                domain_is_complete = False
                if domain:
                    if 'low' in domain:
                        if 'high' in domain:
                            domain_is_complete = True

                if not domain_is_complete:
                    message = f'Number range term {path} needs a domain with low and high'
                    errors.append(_new_error('', 'vocabulary', path, ErrorCode.Bad_Domain, message))

                # .. and low has to sit below high.
                else:
                    low = domain['low']
                    high = domain['high']
                    if low >= high:
                        message = f'Number range term {path} has low {low} not below high {high}'
                        errors.append(_new_error('', 'vocabulary', path, ErrorCode.Bad_Domain, message))

            # No two terms may wear the same phrase.
            phrase = attribute['phrase']
            if phrase in phrases_seen:
                first_path = phrases_seen[phrase]
                message = f'Terms {first_path} and {path} share the phrase {phrase!r}'
                errors.append(_new_error('', 'vocabulary', path, ErrorCode.Duplicate_Phrase, message))
            else:
                phrases_seen[phrase] = path

    return errors

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
        errors.append(_new_error(rule_name, block, path, ErrorCode.Unknown_Term, message))
        return None

    # .. and a deprecated one still runs but the author should know.
    if attribute['status'] == Status_Deprecated:
        message = f'{path} is deprecated - existing rules keep running but new rules should not use it'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Deprecated_Term, message, Severity.Warning))

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
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))

# ################################################################################################################################

def _check_number_range(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a number range term, including the range's domain.
    """

    # The value has to be a number in the first place ..
    if not _is_number(value):
        message = f'{path} is a number, the value {value!r} is not'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))
        return

    # .. and the domain bounds the legal values.
    domain = attribute['domain']
    low = domain['low']
    high = domain['high']
    is_in_range = low <= value <= high

    if not is_in_range:
        message = f'{path} value {value} is outside {low} to {high}'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Out_Of_Range, message))

# ################################################################################################################################

def _check_choice(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a choice term.
    """

    # A choice value has to be text ..
    if not isinstance(value, str):
        message = f'{path} is a choice, the value {value!r} is not one of its texts'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))
        return

    # .. and one of the values the term declares.
    if value not in attribute['values']:
        choices = ', '.join(attribute['values'])
        message = f'{path} has no choice {value!r} - the choices are {choices}'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Choice_Value, message))

# ################################################################################################################################

def _check_text(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a text term.
    """
    if not isinstance(value, str):
        message = f'{path} is text, the value {value!r} is not'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))

# ################################################################################################################################

def _check_yes_no(path:'str', attribute:'anydict', value:'any_', rule_name:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks a literal used with a yes/no term.
    """
    if not isinstance(value, bool):
        message = f'{path} is yes/no, the value {value!r} is neither'
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))

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
        errors.append(_new_error(rule_name, block, path, ErrorCode.Value_Type, message))
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
            errors.append(_new_error(rule_name, block, term, ErrorCode.Unknown_Default, message))
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
        errors.append(_new_error(rule_name, block, term, ErrorCode.Reference_Type, message))

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
            errors.append(_new_error(rule_name, 'when', subject, ErrorCode.Comparator_Type, message))
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
            errors.append(_new_error('', 'data', path, ErrorCode.Unknown_Field, message))
            continue

        # .. and a known one is checked exactly like a literal in a rule.
        node = {'kind': NodeKind.Literal, 'value': value}
        _check_literal(path, attribute, node, '', 'data', errors)

    return errors

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.rules.document import Comparator
from zato.common.rules.errors import Severity

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, dictlist, generator_, strlist
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

# Splits camel-case boundaries when a phrase is derived from a term name.
_camel_boundary = re.compile(r'([a-z0-9])([A-Z])')

# Entity and attribute names have to be plain identifiers.
_name_pattern = re.compile(r'^[A-Za-z_]\w*$')

# ################################################################################################################################
# ################################################################################################################################

def new_error(
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
            errors.append(new_error('', 'vocabulary', entity_name, ErrorCode.Bad_Name, message))

        # .. and each may appear only once.
        if entity_name in entities_seen:
            message = f'Entity is defined more than once -> {entity_name}'
            errors.append(new_error('', 'vocabulary', entity_name, ErrorCode.Duplicate_Entity, message))
        entities_seen.add(entity_name)

        # Attribute names seen within this entity, to catch duplicates.
        attributes_seen = set()

        for attribute in entity['attributes']:
            name = attribute['name']
            path = entity_name + '.' + name

            # Attribute names have to be identifiers ..
            if not _name_pattern.match(name):
                message = f'Attribute name is not a valid identifier -> {name!r}'
                errors.append(new_error('', 'vocabulary', path, ErrorCode.Bad_Name, message))

            # .. and each may appear only once per entity.
            if name in attributes_seen:
                message = f'Attribute is defined more than once -> {path}'
                errors.append(new_error('', 'vocabulary', path, ErrorCode.Duplicate_Attribute, message))
            attributes_seen.add(name)

            # The type has to be one of the term types.
            type_ = attribute['type']
            if type_ not in Term_Types:
                types = ', '.join(sorted(Term_Types))
                message = f'Unknown type {type_!r} for {path} - the types are {types}'
                errors.append(new_error('', 'vocabulary', path, ErrorCode.Unknown_Type, message))

            # A choice without values cannot be picked from.
            if type_ == TermType.Choice:
                if not attribute.get('values'):
                    message = f'Choice term {path} has no values to choose from'
                    errors.append(new_error('', 'vocabulary', path, ErrorCode.Missing_Values, message))

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
                    errors.append(new_error('', 'vocabulary', path, ErrorCode.Bad_Domain, message))

                # .. and low has to sit below high.
                else:
                    low = domain['low']
                    high = domain['high']
                    if low >= high:
                        message = f'Number range term {path} has low {low} not below high {high}'
                        errors.append(new_error('', 'vocabulary', path, ErrorCode.Bad_Domain, message))

            # No two terms may wear the same phrase.
            phrase = attribute['phrase']
            if phrase in phrases_seen:
                first_path = phrases_seen[phrase]
                message = f'Terms {first_path} and {path} share the phrase {phrase!r}'
                errors.append(new_error('', 'vocabulary', path, ErrorCode.Duplicate_Phrase, message))
            else:
                phrases_seen[phrase] = path

    return errors

# ################################################################################################################################
# ################################################################################################################################

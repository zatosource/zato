# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.vocabulary import Status_Deprecated, TermType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _attribute_to_schema(attribute:'anydict') -> 'anydict':
    """ Converts one vocabulary attribute into its JSON Schema - the vocabulary's own types
    map one to one, so callers see enums, ranges and booleans rather than untyped strings.
    """
    attribute_type = attribute['type']

    # A number range carries its legal bounds ..
    if attribute_type == TermType.Number_Range:
        domain = attribute['domain']
        out:'anydict' = {'type': 'number', 'minimum': domain['low'], 'maximum': domain['high']}

    # .. a plain number has no bounds ..
    elif attribute_type == TermType.Number:
        out = {'type': 'number'}

    # .. a choice lists exactly its legal values ..
    elif attribute_type == TermType.Choice:
        out = {'enum': attribute['values']}

    # .. a yes/no is a boolean ..
    elif attribute_type == TermType.Yes_No:
        out = {'type': 'boolean'}

    # .. and everything else is text.
    else:
        out = {'type': 'string'}

    # The phrase is the business-language description of the term.
    out['description'] = attribute['phrase']

    # A deprecated term keeps existing callers running but is flagged in the document.
    if attribute['status'] == Status_Deprecated:
        out['deprecated'] = True

    return out

# ################################################################################################################################

def vocabulary_to_schema(vocabulary:'anydict') -> 'anydict':
    """ Converts one vocabulary document into the JSON Schema of a ruleset's request body.

    Callers send nested JSON, so each entity becomes one object property whose own properties
    are the entity's attributes - `{"customer": {"creditScore": 720}}` for `customer.creditScore`.
    """
    entities = {}

    for entity in vocabulary['entities']:

        attributes = {}

        for attribute in entity['attributes']:
            attributes[attribute['name']] = _attribute_to_schema(attribute)

        entities[entity['name']] = {
            'type': 'object',
            'properties': attributes,
        }

    out = {
        'type': 'object',
        'properties': entities,
    }

    return out

# ################################################################################################################################

def _attribute_example(attribute:'anydict') -> 'any_':
    """ Picks one legal example value for a vocabulary attribute.
    """
    attribute_type = attribute['type']

    # A range's low bound is always legal ..
    if attribute_type == TermType.Number_Range:
        out = attribute['domain']['low']

    # .. any number works for an unbounded one ..
    elif attribute_type == TermType.Number:
        out = 0

    # .. the first choice is as good as any ..
    elif attribute_type == TermType.Choice:
        out = attribute['values'][0]

    # .. a yes/no gets a yes ..
    elif attribute_type == TermType.Yes_No:
        out = True

    # .. and text stays empty.
    else:
        out = ''

    return out

# ################################################################################################################################

def example_from_vocabulary(vocabulary:'anydict') -> 'anydict':
    """ Synthesizes one nested example request body out of a vocabulary,
    used when a ruleset has no test scenario to show verbatim.
    """
    out:'anydict' = {}

    for entity in vocabulary['entities']:

        values = {}

        for attribute in entity['attributes']:

            # Deprecated terms keep existing rules running but never appear in examples.
            if attribute['status'] == Status_Deprecated:
                continue

            values[attribute['name']] = _attribute_example(attribute)

        if values:
            out[entity['name']] = values

    return out

# ################################################################################################################################

def nest_flat_input(flat:'anydict') -> 'anydict':
    """ Turns a flat dotted mapping into the nested JSON the REST API accepts,
    so `{"customer.creditScore": 720}` from a test scenario becomes `{"customer": {"creditScore": 720}}`.
    """
    out:'anydict' = {}

    for path, value in flat.items():

        # Walk every segment but the last, creating the nesting as needed ..
        segments = path.split('.')
        target = out

        for segment in segments[:-1]:
            if segment not in target:
                target[segment] = {}
            target = target[segment]

        # .. and the last segment carries the value itself.
        target[segments[-1]] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.document import Comparator, NodeKind, Value_Type_Datetime
from zato.common.rule_engine.references import node_reference_terms
from zato.common.rule_engine.vocabulary import TermType, default_phrase, get_attribute

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

# The entity that top-level scalar payload fields belong to when they have no entity of their own.
Default_Entity = 'input'

# The type proposed when nothing about a term's usage narrows it down.
Default_Term_Type = TermType.Text

# The name the first scenario derived from a pasted payload wears.
First_Scenario_Name = 'First scenario'

# Comparators that imply the type of the term they are used with.
_comparator_types = {
    Comparator.Is_Less_Than: TermType.Number,
    Comparator.Is_At_Most:   TermType.Number,
    Comparator.Is_At_Least:  TermType.Number,
    Comparator.Is_More_Than: TermType.Number,
    Comparator.Is_Between:   TermType.Number,
    Comparator.Matches:      TermType.Text,
    Comparator.Is_True:      TermType.Yes_No,
    Comparator.Is_False:     TermType.Yes_No,
}

# ################################################################################################################################
# ################################################################################################################################

def _infer_literal_type(value:'any_') -> 'str':
    """ Maps a plain Python value to the term type it implies.
    """

    # Booleans come first because Python considers them numbers ..
    if isinstance(value, bool):
        out = TermType.Yes_No

    # .. numbers map to the number type ..
    elif isinstance(value, (int, float)):
        out = TermType.Number

    # .. and everything else reads as text.
    else:
        out = TermType.Text

    return out

# ################################################################################################################################

def _split_path(path:'str') -> 'strtuple':
    """ Splits a dotted term path into its entity and attribute name.

    A bare name without a dot belongs to the default entity.
    """
    dot_index = path.find('.')

    if dot_index == -1:
        out = (Default_Entity, path)
    else:
        entity_name = path[:dot_index]
        attribute_name = path[dot_index+1:]
        out = (entity_name, attribute_name)

    return out

# ################################################################################################################################

def _attribute_phrase(entity_name:'str', attribute_name:'str') -> 'str':
    """ Derives the readable phrase for an attribute, treating dots in nested names as word breaks.
    """
    flat_name = attribute_name.replace('.', '_')

    out = default_phrase(entity_name, flat_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _flatten_payload(prefix:'str', mapping:'anydict', out:'anydict') -> 'None':
    """ Flattens nested mappings into dotted paths with scalar values, preserving key order.
    """
    for key, value in mapping.items():

        # Build the dotted path of this key ..
        if prefix:
            path = prefix + '.' + key
        else:
            path = key

        # .. mappings keep flattening ..
        if isinstance(value, dict):
            _flatten_payload(path, value, out)

        # .. and scalars end the recursion.
        else:
            out[path] = value

# ################################################################################################################################

def vocabulary_from_payload(payload:'anydict') -> 'anydict':
    """ Turns one example payload into vocabulary entities with typed attributes and a first test scenario.

    The derivation is deterministic - the same payload always produces the same vocabulary,
    with entities and attributes in the payload's own key order.
    """

    # Flatten the payload into dotted paths first ..
    flat = {}
    _flatten_payload('', payload, flat)

    # .. group the paths into entities with typed attributes ..
    entities = {}
    scenario_input = {}

    for path, value in flat.items():
        entity_name, attribute_name = _split_path(path)

        # A new entity starts with an empty attribute list ..
        if entity_name not in entities:
            entities[entity_name] = {'name': entity_name, 'attributes': []}

        # .. every attribute carries its inferred type and derived phrase ..
        type_ = _infer_literal_type(value)
        phrase = _attribute_phrase(entity_name, attribute_name)
        attribute = {'name': attribute_name, 'type': type_, 'phrase': phrase, 'status': ''}

        entity = entities[entity_name]
        entity['attributes'].append(attribute)

        # .. and the example value seeds the first scenario.
        full_path = entity_name + '.' + attribute_name
        scenario_input[full_path] = value

    # The scenario replays the very payload the vocabulary came from.
    scenario = {'name': First_Scenario_Name, 'input': scenario_input}

    out = {'entities': list(entities.values()), 'scenario': scenario}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _type_from_value_nodes(nodes:'dictlist') -> 'str':
    """ Infers a term type from the first literal found among value nodes, recursing into lists.
    """
    for node in nodes:
        kind = node['kind']

        # A literal implies a type directly, except datetimes, which no term type describes ..
        if kind == NodeKind.Literal:
            if node.get('value_type') == Value_Type_Datetime:
                continue

            out = _infer_literal_type(node['value'])
            break

        # .. and a list is searched item by item.
        if kind == NodeKind.List:
            inner = _type_from_value_nodes(node['items'])
            if inner != Default_Term_Type:
                out = inner
                break

    # Nothing among the values narrowed the type down.
    else:
        out = Default_Term_Type

    return out

# ################################################################################################################################

def _propose(path:'str', type_:'str', vocabulary:'anydict', proposals:'anydict') -> 'None':
    """ Records a proposal for an unknown term, keeping the first inference when a term appears more than once.
    """

    # A term the vocabulary already knows needs no proposal ..
    if get_attribute(vocabulary, path):
        return

    # .. and neither does one that was already proposed.
    if path in proposals:
        return

    entity_name, attribute_name = _split_path(path)
    phrase = _attribute_phrase(entity_name, attribute_name)

    proposals[path] = {
        'path': path,
        'entity': entity_name,
        'name': attribute_name,
        'type': type_,
        'phrase': phrase,
        'status': '',
    }

# ################################################################################################################################

def _known_or_proposed_type(path:'str', vocabulary:'anydict', proposals:'anydict') -> 'str':
    """ Returns the type of a term - from the vocabulary, from an earlier proposal, or the default.
    """
    if attribute := get_attribute(vocabulary, path):
        out = attribute['type']
    elif path in proposals:
        proposal = proposals[path]
        out = proposal['type']
    else:
        out = Default_Term_Type

    return out

# ################################################################################################################################

def infer_from_document(document:'anydict', vocabulary:'anydict') -> 'dictlist':
    """ Proposes a vocabulary term for every unknown term a parsed rule references, with the type inferred from usage.

    A pure function - document and vocabulary in, proposals out, nothing is modified.
    """
    proposals = {}

    # Condition subjects take their type from the comparator or from the values they compare against ..
    for condition in document['conditions']:
        subject = condition['subject']

        inferred = _comparator_types.get(condition['comparator'])
        if inferred is None:
            inferred = _type_from_value_nodes(condition['values'])

        _propose(subject, inferred, vocabulary, proposals)

        # .. and a term referenced as a value mirrors the type of the subject it is compared with.
        subject_type = _known_or_proposed_type(subject, vocabulary, proposals)
        for node in condition['values']:
            for term in node_reference_terms(node):
                _propose(term, subject_type, vocabulary, proposals)

    # Action targets take their type from the value assigned to them ..
    for block in ('then', 'else'):
        for action in document[block]:
            target = action['target']
            value_node = action['value']

            inferred = _type_from_value_nodes([value_node])
            _propose(target, inferred, vocabulary, proposals)

            # .. and a term referenced in an assignment mirrors the type of its target.
            target_type = _known_or_proposed_type(target, vocabulary, proposals)
            for term in node_reference_terms(value_node):
                _propose(term, target_type, vocabulary, proposals)

    out = list(proposals.values())
    return out

# ################################################################################################################################
# ################################################################################################################################

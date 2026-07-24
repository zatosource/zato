# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.openapi import example_from_vocabulary, nest_flat_input, vocabulary_to_schema
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Test_Set, \
    Definition_Type_Vocabulary, Documents_Key
from zato.server.openapi_console.rule_engine import _ruleset_operation, _scenario_example

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

# Dotted terms match the vocabulary's entity.attribute paths.
_rules_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    customer.creditScore is at least 700
then
    loan.rate = 2.9
"""

# ################################################################################################################################
# ################################################################################################################################

def _vocabulary_document() -> 'anydict':
    """ A small loan vocabulary covering every term type, including a deprecated one.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
                {'name': 'category', 'type': 'choice', 'values': ['Gold', 'Silver', 'Platinum'],
                 'phrase': "the customer's category", 'status': ''},
                {'name': 'segment', 'type': 'choice', 'values': ['Retail', 'Private'],
                 'phrase': "the customer's segment", 'status': 'deprecated'},
            ]},
            {'name': 'loan', 'attributes': [
                {'name': 'rate', 'type': 'number', 'phrase': 'the interest rate', 'status': ''},
                {'name': 'approved', 'type': 'yes/no', 'phrase': 'the loan is approved', 'status': ''},
                {'name': 'note', 'type': 'text', 'phrase': 'a free-form note', 'status': ''},
            ]},
        ],
    }

    return out

# ################################################################################################################################

def _documents(text:'str') -> 'anydict':
    """ Parses rules text into canonical documents, loud on any parse error.
    """
    documents, errors = parse_data_details(text, 'payments')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################
# ################################################################################################################################

def test_vocabulary_to_schema_maps_every_term_type() -> 'None':
    """ Each vocabulary type becomes its exact JSON Schema counterpart - enums, ranges and booleans,
    never untyped strings.
    """
    schema = vocabulary_to_schema(_vocabulary_document())

    assert schema['type'] == 'object'

    customer = schema['properties']['customer']
    assert customer['type'] == 'object'

    # A number range carries its legal bounds ..
    score = customer['properties']['creditScore']
    assert score == {
        'type': 'number',
        'minimum': 300,
        'maximum': 850,
        'description': "the customer's credit score",
    }

    # .. a choice lists exactly its legal values ..
    category = customer['properties']['category']
    assert category['enum'] == ['Gold', 'Silver', 'Platinum']

    # .. a deprecated term is flagged as such ..
    segment = customer['properties']['segment']
    assert segment['deprecated'] is True

    # .. and numbers, booleans and text keep their own types.
    loan = schema['properties']['loan']
    assert loan['properties']['rate']['type'] == 'number'
    assert loan['properties']['approved']['type'] == 'boolean'
    assert loan['properties']['note']['type'] == 'string'

# ################################################################################################################################

def test_example_from_vocabulary_is_legal_and_skips_deprecated_terms() -> 'None':
    """ The synthesized example carries one legal value per term and no deprecated ones.
    """
    example = example_from_vocabulary(_vocabulary_document())

    expected = {
        'customer': {
            'creditScore': 300,
            'category': 'Gold',
        },
        'loan': {
            'rate': 0,
            'approved': True,
            'note': '',
        },
    }
    assert example == expected

# ################################################################################################################################

def test_nest_flat_input_builds_the_shape_the_api_accepts() -> 'None':
    """ Flat dotted scenario input becomes the nested JSON callers actually send.
    """
    flat = {
        'channel': 'web',
        'customer.creditScore': 720,
        'customer.address.city': 'Prague',
    }
    nested = nest_flat_input(flat)

    expected = {
        'channel': 'web',
        'customer': {
            'creditScore': 720,
            'address': {'city': 'Prague'},
        },
    }
    assert nested == expected

# ################################################################################################################################

def test_ruleset_operation_documents_the_vocabulary_and_the_scenario(backend:'RuleSQLBackend') -> 'None':
    """ A published ruleset's operation carries the vocabulary-typed request schema
    and its first test scenario, nested, as the example.
    """
    vocabulary = backend.definitions.create(
        name='Loan approval',
        object_type=Definition_Type_Vocabulary,
        document=_vocabulary_document(),
        author=_author,
        comment='Create the vocabulary',
    )

    document = {Documents_Key: _documents(_rules_text), 'vocabulary_id': vocabulary.id}
    definition = backend.definitions.create(
        name='payments.discounts',
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment='Create the ruleset',
    )
    _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    suite_document = {
        'name': 'Loan suite',
        'scenarios': [
            {'name': 'High score gets the rate', 'input': {'customer.creditScore': 720}, 'expected': {'loan.rate': 2.9}},
        ],
    }
    _ = backend.definitions.create(
        name='Loan suite',
        object_type=Definition_Type_Test_Set,
        document=suite_document,
        author=_author,
        comment='Create the suite',
        parent_id=definition.id,
    )

    # The live definition record carries the live pointer the operation builder needs.
    published = backend.definitions.list_published_rulesets()
    assert len(published) == 1

    schemas:'anydict' = {}
    path_item = _ruleset_operation(backend, published[0], schemas)
    operation = path_item['post']

    # The request body references the vocabulary-typed component schema ..
    schema_ref = operation['requestBody']['content']['application/json']['schema']['$ref']
    assert schema_ref == '#/components/schemas/RuleEngineInput_payments_discounts'

    request_schema = schemas['RuleEngineInput_payments_discounts']
    score = request_schema['properties']['customer']['properties']['creditScore']
    assert score['minimum'] == 300
    assert score['maximum'] == 850

    # .. the example is the test scenario's input, nested the way callers send it ..
    example = operation['requestBody']['content']['application/json']['example']
    assert example == {'customer': {'creditScore': 720}}

    # .. and the operation is tagged and returns the shared decision envelope.
    assert operation['tags'] == ['Rule engine']
    response_ref = operation['responses']['200']['content']['application/json']['schema']['$ref']
    assert response_ref == '#/components/schemas/RuleEngineDecision'

# ################################################################################################################################

def test_scenario_example_is_none_without_suites(backend:'RuleSQLBackend') -> 'None':
    """ A ruleset with no test suites has no scenario to show.
    """
    document = {Documents_Key: _documents(_rules_text)}
    definition = backend.definitions.create(
        name='payments.discounts',
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment='Create the ruleset',
    )

    example = _scenario_example(backend, definition.id)
    assert example is None

# ################################################################################################################################
# ################################################################################################################################

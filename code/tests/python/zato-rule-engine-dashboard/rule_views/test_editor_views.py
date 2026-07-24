# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import CONFLICT, OK

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import create_vocabulary, parse_documents, Rules_Text, Rules_Text_Dotted, Rules_Text_Lower_Bar, \
    suite_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_validate_reports_parse_errors(client:'any_') -> 'None':
    """ Text the parser cannot accept comes back with structured errors, never an exception.
    """
    body = {'text': 'rule\n    Broken_rule\nwhen\n    credit_score frobnicates 700\nthen\n    rate = 2.9\n',
        'ruleset_name': 'loans'}

    response = post_json(client, '/rules/editor/validate/', body)
    assert response.status_code == OK

    errors = response.json()['errors']
    assert len(errors) > 0
    assert errors[0]['rule'] == 'Broken_rule'

# ################################################################################################################################

def test_validate_checks_semantics_against_a_vocabulary(client:'any_', backend:'any_') -> 'None':
    """ Known terms validate cleanly, an unknown term is reported by name.
    """
    definition = create_vocabulary(backend)

    # Clean text has no findings at all ..
    body = {'text': Rules_Text_Dotted, 'ruleset_name': 'loans', 'vocabulary_id': definition.id}
    response = post_json(client, '/rules/editor/validate/', body)
    assert response.status_code == OK
    assert response.json()['errors'] == []

    # .. while a term the vocabulary does not know is reported.
    text = Rules_Text_Dotted.replace('customer.creditScore', 'customer.height')
    body = {'text': text, 'ruleset_name': 'loans', 'vocabulary_id': definition.id}
    response = post_json(client, '/rules/editor/validate/', body)

    errors = response.json()['errors']
    assert len(errors) == 1
    assert 'customer.height' in errors[0]['message']

# ################################################################################################################################

def test_render_is_the_inverse_of_validate(client:'any_') -> 'None':
    """ Documents from a parse render back into readable rule text.
    """
    body = {'text': Rules_Text, 'ruleset_name': 'loans'}
    response = post_json(client, '/rules/editor/validate/', body)
    documents = response.json()['documents']

    response = post_json(client, '/rules/editor/render/', {'documents': documents})
    assert response.status_code == OK

    text = response.json()['text']
    assert 'credit_score is at least 700' in text
    assert 'rate = 2.9' in text

# ################################################################################################################################

def test_completion_serves_terms_with_comparators(client:'any_', backend:'any_') -> 'None':
    """ The completion payload carries every offerable term with its comparators - deprecated terms never appear.
    """
    definition = create_vocabulary(backend)

    response:'any_' = client.get(f'/rules/editor/completion/{definition.id}/')
    assert response.status_code == OK

    terms = response.json()['terms']

    by_path = {}
    for term in terms:
        by_path[term['path']] = term

    # The deprecated segment term is not offered ..
    assert 'customer.segment' not in by_path

    # .. numbers offer numeric comparators ..
    score = by_path['customer.creditScore']
    assert 'is at least' in score['comparators']
    assert score['domain'] == {'low': 300, 'high': 850}

    # .. and choices carry their closed pick list.
    category = by_path['customer.category']
    assert category['values'] == ['Gold', 'Silver', 'Platinum']
    assert 'is one of' in category['comparators']

# ################################################################################################################################

def test_save_creates_versions_and_the_index(client:'any_', backend:'any_') -> 'None':
    """ The first save creates the definition, later saves chain optimistic versions, stale saves are conflicts.
    """
    documents = parse_documents(Rules_Text)

    # The first save creates the definition with its first version ..
    body = {
        'name': 'Loans',
        'object_type': 'ruleset',
        'document': {'documents': documents},
        'comment': 'Create the ruleset',
    }
    response = post_json(client, '/rules/editor/save/', body)
    assert response.status_code == OK

    data = response.json()
    definition_id = data['definition_id']
    assert data['version'] == 1

    # .. and builds the where-used index as it goes ..
    assert backend.references.is_used('credit_score') is True

    # .. a later save chains the next version ..
    lower_bar = parse_documents(Rules_Text_Lower_Bar)
    body = {
        'definition_id': definition_id,
        'expected_current_version': 1,
        'document': {'documents': lower_bar},
        'comment': 'Lower the bar',
    }
    response = post_json(client, '/rules/editor/save/', body)
    assert response.status_code == OK
    assert response.json()['version'] == 2

    # .. and a save against a stale version is a conflict, never an overwrite.
    response = post_json(client, '/rules/editor/save/', body)
    assert response.status_code == CONFLICT

# ################################################################################################################################

def test_outcomes_run_the_edited_documents_live(client:'any_') -> 'None':
    """ The live-outcomes feed runs the edited documents against a suite, scenario by scenario.
    """
    documents = parse_documents(Rules_Text)
    body = {'documents': documents, 'test_set': suite_document()}

    response = post_json(client, '/rules/editor/outcomes/', body)
    assert response.status_code == OK

    result = response.json()
    assert result['total'] == 2
    assert result['passed'] == 1
    assert result['failed'] == 0
    assert result['explored'] == 1

# ################################################################################################################################
# ################################################################################################################################

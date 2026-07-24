# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import create_ruleset, create_vocabulary, parse_documents, Rules_Text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_vocabulary_document_is_served(client:'any_', backend:'any_') -> 'None':
    """ The vocabulary screen reads the stored document as one tree.
    """
    definition = create_vocabulary(backend)

    response:'any_' = client.get(f'/rules/vocabulary/{definition.id}/')
    assert response.status_code == OK

    vocabulary = response.json()['vocabulary']
    assert vocabulary['name'] == 'Loan approval'

    entity_names = []
    for entity in vocabulary['entities']:
        entity_names.append(entity['name'])

    assert entity_names == ['customer', 'loan']

# ################################################################################################################################

def test_where_used_reads_the_persisted_index(client:'any_', backend:'any_') -> 'None':
    """ Where-used answers from the index and reports whether a delete stays blocked.
    """
    definition = create_ruleset(backend)
    documents = parse_documents(Rules_Text)
    _ = backend.references.rebuild(definition_id=definition.id, documents=documents)

    response:'any_' = client.get('/rules/vocabulary/where-used/', {'term': 'credit_score'})
    assert response.status_code == OK

    data = response.json()
    assert data['is_used'] is True
    assert data['can_delete'] is False

    items = data['items']
    assert len(items) == 1
    assert items[0]['definition_id'] == definition.id
    assert items[0]['rule_name'] == 'loans_Preferential_rate'
    assert items[0]['role'] == 'subject'

    # A term nothing references can go.
    response:'any_' = client.get('/rules/vocabulary/where-used/', {'term': 'no_such_term'})
    data = response.json()
    assert data['is_used'] is False
    assert data['can_delete'] is True

# ################################################################################################################################

def test_rename_previews_then_applies(client:'any_', backend:'any_') -> 'None':
    """ A dry run reports the impact without changing anything, an applied rename rewrites and re-versions.
    """
    definition = create_ruleset(backend)
    documents = parse_documents(Rules_Text)
    _ = backend.references.rebuild(definition_id=definition.id, documents=documents)

    # The dry run names the affected rule but stores nothing ..
    body = {'old_term': 'credit_score', 'new_term': 'score'}
    response = post_json(client, '/rules/vocabulary/rename/', body)
    assert response.status_code == OK

    data = response.json()
    assert data['dry_run'] is True
    assert len(data['definitions']) == 1

    affected = data['definitions'][0]
    assert affected['definition_id'] == definition.id
    assert affected['impact'] == [{'rule': 'loans_Preferential_rate', 'change_count': 1}]

    unchanged = backend.definitions.get(definition.id)
    assert unchanged.current_version == 1

    # .. while the applied rename rewrites the document, bumps the version and reindexes.
    body = {'old_term': 'credit_score', 'new_term': 'score', 'dry_run': False}
    response = post_json(client, '/rules/vocabulary/rename/', body)
    assert response.status_code == OK

    changed = backend.definitions.get(definition.id)
    assert changed.current_version == 2

    assert backend.references.is_used('credit_score') is False
    assert backend.references.is_used('score') is True

# ################################################################################################################################

def test_bootstrap_builds_a_vocabulary_from_one_payload(client:'any_') -> 'None':
    """ Paste-a-payload turns one JSON example into terms with inferred types.
    """
    payload = {'customer': {'creditScore': 720, 'name': 'Jan Kowalski'}, 'amount': 50000}

    response = post_json(client, '/rules/vocabulary/bootstrap/', {'payload': payload})
    assert response.status_code == OK

    vocabulary = response.json()['vocabulary']
    assert vocabulary['entities']

    attribute_types = {}
    for entity in vocabulary['entities']:
        for attribute in entity['attributes']:
            path = entity['name'] + '.' + attribute['name']
            attribute_types[path] = attribute['type']

    assert attribute_types['customer.creditScore'] == 'number'
    assert attribute_types['customer.name'] == 'text'

# ################################################################################################################################

def test_infer_proposes_unknown_terms_from_typing(client:'any_', backend:'any_') -> 'None':
    """ An unknown term in a typed rule comes back as a proposed term with a type inferred from usage.
    """
    definition = create_vocabulary(backend)

    text = """
rule
    Tall_customers
when
    customer.height is at least 180
then
    loan.rate = 2.9
"""
    body = {'text': text, 'ruleset_name': 'loans'}
    response = post_json(client, f'/rules/vocabulary/{definition.id}/infer/', body)
    assert response.status_code == OK

    proposals = response.json()['proposals']

    paths = []
    for proposal in proposals:
        paths.append(proposal['path'])

    assert 'customer.height' in paths

# ################################################################################################################################
# ################################################################################################################################

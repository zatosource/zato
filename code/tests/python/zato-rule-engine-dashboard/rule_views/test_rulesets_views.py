# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK

# Zato
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import create_ruleset, create_test_set

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_list_filters_by_kind_and_content(client:'any_', backend:'any_') -> 'None':
    """ The list returns every definition and narrows by object type and content search.
    """
    _ = create_ruleset(backend, 'Loans')
    _ = create_test_set(backend, 'Loan suite')

    response:'any_' = client.get('/rules/rulesets/')
    assert response.status_code == OK

    items = response.json()['items']
    assert len(items) == 2

    # Narrowed to rulesets alone ..
    response:'any_' = client.get('/rules/rulesets/', {'object_type': 'ruleset'})
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['name'] == 'Loans'

    # .. and narrowed by document content.
    response:'any_' = client.get('/rules/rulesets/', {'search': 'Better rates'})
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['object_type'] == 'ruleset'

# ################################################################################################################################

def test_search_returns_rendered_hits(client:'any_', backend:'any_') -> 'None':
    """ Content search answers with rendered sentences and match positions.
    """
    definition = create_ruleset(backend)

    response:'any_' = client.get('/rules/search/', {'q': 'at least 700'})
    assert response.status_code == OK

    items = response.json()['items']
    assert len(items) == 1

    hit = items[0]
    assert hit['definition_id'] == definition.id
    assert hit['rule'] == 'loans_Preferential_rate'
    assert 'credit_score' in hit['line']

# ################################################################################################################################

def test_preview_renders_the_rules_and_the_history(client:'any_', backend:'any_') -> 'None':
    """ The preview carries the rendered rules and the definition's history.
    """
    definition = create_ruleset(backend)

    response:'any_' = client.get(f'/rules/rulesets/{definition.id}/preview/')
    assert response.status_code == OK

    data = response.json()
    assert data['definition']['name'] == 'Loans'
    assert 'credit_score is at least 700' in data['rendered']
    assert data['is_following'] is False

    event_types = []
    for event in data['events']:
        event_types.append(event['event_type'])

    assert 'definition.created' in event_types

# ################################################################################################################################

def test_publish_hot_reloads_a_ruleset(client:'any_', backend:'any_') -> 'None':
    """ Publishing makes the version live and loads its rules into the running manager.
    """
    definition = create_ruleset(backend)

    response = post_json(client, f'/rules/rulesets/{definition.id}/publish/', {'version': 1})
    assert response.status_code == OK

    data = response.json()
    assert data['version'] == 1
    assert data['rule_names'] == ['loans_Preferential_rate']

    published = backend.definitions.get(definition.id)
    assert published.live_version == 1

# ################################################################################################################################

def test_rename_previews_its_impact_without_changing_anything(client:'any_', backend:'any_') -> 'None':
    """ The dry run reports the calls the current name served and the rule names it would rewrite.
    """
    definition = create_ruleset(backend)

    body = {'new_name': 'mortgages', 'dry_run': True}
    response = post_json(client, f'/rules/rulesets/{definition.id}/rename/', body)
    assert response.status_code == OK

    data = response.json()
    assert data['old_name'] == 'Loans'
    assert data['new_name'] == 'mortgages'
    assert data['rest_call_count'] == 0
    assert data['rules'] == [{'rule': 'loans_Preferential_rate', 'new_rule': 'mortgages_Preferential_rate'}]

    # Nothing moved - the name and the stored rule names are what they were.
    unchanged = backend.definitions.get(definition.id)
    assert unchanged.name == 'Loans'
    assert unchanged.current_version == 1

# ################################################################################################################################

def test_rename_renames_the_ruleset_and_every_rule_in_it(client:'any_', backend:'any_') -> 'None':
    """ An applied rename gives the ruleset its new name and stores the rewritten rules as the next version.
    """
    definition = create_ruleset(backend)

    body = {'new_name': 'mortgages', 'dry_run': False}
    response = post_json(client, f'/rules/rulesets/{definition.id}/rename/', body)
    assert response.status_code == OK
    assert response.json()['version'] == 2

    # The definition answers to the new name, which is the REST address of the ruleset ..
    renamed = backend.definitions.get(definition.id)
    assert renamed.name == 'mortgages'

    # .. every rule of it carries the new name too ..
    documents = backend.definitions.get_document(definition.id)[Documents_Key]
    assert list(documents) == ['mortgages_Preferential_rate']

    document = documents['mortgages_Preferential_rate']
    assert document['ruleset_name'] == 'mortgages'
    assert document['full_name'] == 'mortgages_Preferential_rate'

    # .. the where-used index refers to the rule by the name it now has ..
    usages = backend.references.where_used('credit_score')
    assert usages[0].rule_name == 'mortgages_Preferential_rate'

    # .. and the rename is in the history under the name it had before.
    payloads = []
    for event in backend.events.list(definition_id=definition.id, limit=20):
        if event.event_type == 'definition.renamed':
            payloads.append(deserialize_document(event.payload))

    assert payloads == [{'old_name': 'Loans', 'new_name': 'mortgages'}]

# ################################################################################################################################

def test_rename_refuses_a_name_no_rest_path_can_carry(client:'any_', backend:'any_') -> 'None':
    """ A ruleset name is dotted words - anything else is refused before a preview even runs.
    """
    definition = create_ruleset(backend)

    body = {'new_name': 'mortgages/2', 'dry_run': True}
    response = post_json(client, f'/rules/rulesets/{definition.id}/rename/', body)
    assert response.status_code == BAD_REQUEST
    assert 'dotted words' in response.json()['error']

# ################################################################################################################################

def test_follow_feed_and_seen(client:'any_', backend:'any_', username:'str') -> 'None':
    """ Following starts the feed, an event lands in it, marking seen empties it and unfollowing stops it.
    """
    definition = create_ruleset(backend)

    response = post_json(client, f'/rules/rulesets/{definition.id}/follow/', {})
    assert response.status_code == OK
    assert response.json()['is_following'] is True

    # An event after the follow appears in the feed ..
    _ = backend.events.append(
        definition_id=definition.id,
        version=1,
        event_type='review.commented',
        actor=username,
        payload={'comment': 'Looks good'},
    )

    response:'any_' = client.get('/rules/feed/')
    items = response.json()['items']

    event_types = []
    for event in items:
        event_types.append(event['event_type'])

    assert 'review.commented' in event_types

    # .. marking seen moves the clock past it ..
    response = post_json(client, f'/rules/rulesets/{definition.id}/seen/', {})
    assert response.status_code == OK

    response:'any_' = client.get('/rules/feed/')
    assert response.json()['items'] == []

    # .. and unfollowing is definitive.
    response = post_json(client, f'/rules/rulesets/{definition.id}/unfollow/', {})
    assert response.json()['is_following'] is False

# ################################################################################################################################

def test_saved_views_are_named_and_replaceable(client:'any_') -> 'None':
    """ A saved view is stored under its name, listed, and deleted on request.
    """
    payload = {'object_type': 'ruleset', 'search_text': 'loans'}

    response = post_json(client, '/rules/views/save/', {'name': 'My rulesets', 'payload': payload})
    assert response.status_code == OK
    assert response.json()['payload'] == payload

    response:'any_' = client.get('/rules/views/')
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['name'] == 'My rulesets'

    response = post_json(client, '/rules/views/delete/', {'name': 'My rulesets'})
    assert response.status_code == OK

    response:'any_' = client.get('/rules/views/')
    assert response.json()['items'] == []

# ################################################################################################################################
# ################################################################################################################################

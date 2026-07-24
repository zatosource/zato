# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

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

def test_preview_renders_and_counts_as_a_visit(client:'any_', backend:'any_') -> 'None':
    """ The preview carries the rendered rules and recent history, and the visit lands in the recents strip.
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

    # The preview itself put the definition into the recents.
    response:'any_' = client.get('/rules/recents/')
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['definition_id'] == definition.id

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

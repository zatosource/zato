# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import Author, create_ruleset, create_test_set, parse_documents, Rules_Text_Lower_Bar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_suites_are_listed(client:'any_', backend:'any_') -> 'None':
    """ The suites list carries test sets alone.
    """
    _ = create_ruleset(backend)
    suite = create_test_set(backend)

    response:'any_' = client.get('/rules/test-sets/')
    assert response.status_code == OK

    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['id'] == suite.id
    assert items[0]['object_type'] == 'test-set'

# ################################################################################################################################

def test_validate_reports_structural_findings(client:'any_') -> 'None':
    """ A nameless suite is reported, never silently accepted.
    """
    body = {'test_set': {'name': '', 'scenarios': []}}

    response = post_json(client, '/rules/test-sets/validate/', body)
    assert response.status_code == OK
    assert len(response.json()['errors']) > 0

# ################################################################################################################################

def test_run_against_the_live_version_leaves_a_trace(client:'any_', backend:'any_') -> 'None':
    """ A run without a pinned version runs what is live and lands in the ruleset's history.
    """
    ruleset = create_ruleset(backend)
    suite = create_test_set(backend)
    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    response = post_json(client, f'/rules/test-sets/{suite.id}/run/', {'ruleset_id': ruleset.id})
    assert response.status_code == OK

    result = response.json()
    assert result['total'] == 2
    assert result['passed'] == 1
    assert result['failed'] == 0
    assert result['explored'] == 1

    # The run is on the record.
    events = backend.events.list(definition_id=ruleset.id)

    run_events = []
    for event in events:
        if event.event_type == 'test.run':
            run_events.append(event)

    assert len(run_events) == 1

# ################################################################################################################################

def test_run_pins_a_version_when_asked(client:'any_', backend:'any_') -> 'None':
    """ A pinned run exercises exactly the requested snapshot, not what is live.
    """
    ruleset = create_ruleset(backend)
    suite = create_test_set(backend)

    # Version two lowers the bar and goes live ..
    documents = parse_documents(Rules_Text_Lower_Bar)
    _ = backend.versions.create(
        definition_id=ruleset.id,
        expected_current_version=1,
        document={'documents': documents},
        author=Author,
        comment='Lower the bar',
    )
    _ = backend.versions.publish(definition_id=ruleset.id, version=2, actor=Author)

    # .. and the pinned run still exercises version one.
    body = {'ruleset_id': ruleset.id, 'version': 1}
    response = post_json(client, f'/rules/test-sets/{suite.id}/run/', body)
    assert response.status_code == OK
    assert response.json()['passed'] == 1

# ################################################################################################################################

def test_promote_actual_to_expected(client:'any_', backend:'any_') -> 'None':
    """ Promoting turns an exploration scenario into an asserting one, stored as a new suite version.
    """
    suite = create_test_set(backend)

    body = {
        'scenario_name': 'Low score explores',
        'actual': {'rate': 4.5},
        'expected_current_version': 1,
    }
    response = post_json(client, f'/rules/test-sets/{suite.id}/promote/', body)
    assert response.status_code == OK

    data = response.json()
    assert data['version'] == 2

    scenarios = {}
    for scenario in data['test_set']['scenarios']:
        scenarios[scenario['name']] = scenario

    assert scenarios['Low score explores']['expected'] == {'rate': 4.5}

# ################################################################################################################################

def test_simulation_computes_kpis(client:'any_', backend:'any_') -> 'None':
    """ Batch simulation runs one version over many scenarios with incrementally computed KPIs.
    """
    ruleset = create_ruleset(backend)

    scenarios = [
        {'name': 'High score', 'input': {'credit_score': 720}},
        {'name': 'Low score', 'input': {'credit_score': 500}},
    ]
    kpis = [
        {'name': 'Approvals', 'kind': 'count', 'field': 'approved', 'value': True},
    ]
    body = {'ruleset_id': ruleset.id, 'version': 1, 'scenarios': scenarios, 'kpis': kpis}

    response = post_json(client, '/rules/simulation/', body)
    assert response.status_code == OK

    result = response.json()
    assert result['total'] == 2
    assert result['evaluated'] == 2
    assert result['kpis'] == [{'name': 'Approvals', 'kind': 'count', 'value': 1}]

# ################################################################################################################################

def test_champion_challenger_compares_two_versions(client:'any_', backend:'any_') -> 'None':
    """ Champion and challenger run the same scenarios, their KPIs come back side by side with the differences.
    """
    ruleset = create_ruleset(backend)

    documents = parse_documents(Rules_Text_Lower_Bar)
    _ = backend.versions.create(
        definition_id=ruleset.id,
        expected_current_version=1,
        document={'documents': documents},
        author=Author,
        comment='Lower the bar',
    )

    scenarios = [
        {'name': 'Middling score', 'input': {'credit_score': 660}},
        {'name': 'High score', 'input': {'credit_score': 720}},
    ]
    kpis = [
        {'name': 'Approvals', 'kind': 'count', 'field': 'approved', 'value': True},
    ]
    body = {
        'ruleset_id': ruleset.id,
        'champion_version': 1,
        'challenger_version': 2,
        'scenarios': scenarios,
        'kpis': kpis,
    }

    response = post_json(client, '/rules/champion-challenger/', body)
    assert response.status_code == OK

    result = response.json()
    assert result['champion']['kpis'] == [{'name': 'Approvals', 'kind': 'count', 'value': 1}]
    assert result['challenger']['kpis'] == [{'name': 'Approvals', 'kind': 'count', 'value': 2}]
    assert result['diff']['changed'] == 1

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.simulation import champion_challenger, simulate, validate_kpis
from zato.common.rule_engine.sql.constants import Definition_Type_Test_Set, Event_Type_Test_Run
from zato.common.rule_engine.testing import promote_actual, run_test_set, validate_test_set
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import definition_row, json_api, read_int, read_json, required, \
    ruleset_documents, serialize_all

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How many test sets the list returns when the request does not say otherwise.
_default_limit = 100

# What the version history records when a promotion does not bring its own comment.
_default_promote_comment = 'Promote actual outcome to expected'

# ################################################################################################################################
# ################################################################################################################################

@json_api
def test_set_list(req:'any_') -> 'any_':
    """ Every stored test suite.
    """
    limit = read_int(req, 'limit', _default_limit)

    backend = get_backend()
    records = backend.definitions.list(object_type=Definition_Type_Test_Set, limit=limit)
    items = serialize_all(records, definition_row)

    out = JsonResponse({'items': items})
    return out

# ################################################################################################################################

@json_api
def test_set_validate(req:'any_') -> 'any_':
    """ Structural validation of one test-set document.
    """
    body = read_json(req)
    test_set = required(body, 'test_set')

    errors = validate_test_set(test_set)

    out = JsonResponse({'errors': errors})
    return out

# ################################################################################################################################

@json_api
def test_set_run(req:'any_', test_set_id:'int') -> 'any_':
    """ Runs one suite against a ruleset version - the live one unless the request pins another -
    with per-scenario diffs and traces, exploration scenarios included.
    """
    body = read_json(req)
    ruleset_id = required(body, 'ruleset_id')

    backend = get_backend()
    test_set = backend.definitions.get_document(test_set_id)

    # A pinned version runs as pinned, anything else runs what is live.
    if version := body.get('version'):
        pass
    else:
        live = backend.versions.get_live(ruleset_id)
        version = live.version

    documents = ruleset_documents(backend, ruleset_id, version)
    result = run_test_set(test_set, documents)

    # The run leaves its trace in the history of the ruleset it exercised.
    payload = {
        'test_set_id': test_set_id,
        'total':       result['total'],
        'passed':      result['passed'],
        'failed':      result['failed'],
        'explored':    result['explored'],
    }
    _ = backend.events.append(
        definition_id=ruleset_id,
        version=version,
        event_type=Event_Type_Test_Run,
        actor=req.user.username,
        payload=payload,
    )

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def test_set_promote(req:'any_', test_set_id:'int') -> 'any_':
    """ Promotes one scenario's actual outcome to its expected outcome, stored as a new version of the suite.
    """
    body = read_json(req)
    scenario_name = required(body, 'scenario_name')
    actual = required(body, 'actual')
    expected_current_version = required(body, 'expected_current_version')

    if comment := body.get('comment'):
        pass
    else:
        comment = _default_promote_comment

    backend = get_backend()
    test_set = backend.definitions.get_document(test_set_id)
    updated = promote_actual(test_set, scenario_name, actual)

    record = backend.versions.create(
        definition_id=test_set_id,
        expected_current_version=expected_current_version,
        document=updated,
        author=req.user.username,
        comment=comment,
    )

    out = JsonResponse({'version': record.version, 'test_set': updated})
    return out

# ################################################################################################################################

@json_api
def simulation_run(req:'any_') -> 'any_':
    """ Batch simulation - one version run over many scenarios with incrementally computed KPIs.
    """
    body = read_json(req)
    ruleset_id = required(body, 'ruleset_id')
    version = required(body, 'version')
    scenarios = required(body, 'scenarios')
    kpis = required(body, 'kpis')

    # KPI definitions that do not hold together end the request before anything runs.
    kpi_errors = validate_kpis(kpis)
    if kpi_errors:
        out = JsonResponse({'errors': kpi_errors}, status=BAD_REQUEST)
        return out

    backend = get_backend()
    documents = ruleset_documents(backend, ruleset_id, version)
    result = simulate(documents, scenarios, kpis)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def champion_challenger_run(req:'any_') -> 'any_':
    """ Champion versus challenger - two versions over the same scenarios, KPIs side by side with their differences.
    """
    body = read_json(req)
    ruleset_id = required(body, 'ruleset_id')
    champion_version = required(body, 'champion_version')
    challenger_version = required(body, 'challenger_version')
    scenarios = required(body, 'scenarios')
    kpis = required(body, 'kpis')

    # KPI definitions that do not hold together end the request before anything runs.
    kpi_errors = validate_kpis(kpis)
    if kpi_errors:
        out = JsonResponse({'errors': kpi_errors}, status=BAD_REQUEST)
        return out

    backend = get_backend()
    champion_documents = ruleset_documents(backend, ruleset_id, champion_version)
    challenger_documents = ruleset_documents(backend, ruleset_id, challenger_version)

    result = champion_challenger(champion_documents, challenger_documents, scenarios, kpis)

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################

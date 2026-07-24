# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.data import DecisionFilter
from zato.common.rule_engine.testing import evaluate_input, load_documents
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import BadRequestError, decision_row, json_api, read_int, read_json, \
    read_time, required, ruleset_documents, serialize_all, version_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDecisionRecord
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# How many decisions one page of the log returns when the request does not say otherwise.
_default_limit = 100

# ################################################################################################################################
# ################################################################################################################################

def _read_filters(req:'any_') -> 'DecisionFilter':
    """ Builds the decision-log filter from the request's query parameters, every one of them optional.
    """
    if ruleset_id := req.GET.get('ruleset_id'):
        ruleset_id = int(ruleset_id)
    else:
        ruleset_id = None

    if rules_version := req.GET.get('rules_version'):
        rules_version = int(rules_version)
    else:
        rules_version = None

    if before_id := req.GET.get('before_id'):
        before_id = int(before_id)
    else:
        before_id = None

    if is_error := req.GET.get('is_error'):
        is_error = is_error == 'true'
    else:
        is_error = None

    business_key = req.GET.get('business_key')
    outcome = req.GET.get('outcome')
    start_time = read_time(req, 'start_time')
    end_time = read_time(req, 'end_time')

    out = DecisionFilter(
        ruleset_id=ruleset_id,
        start_time=start_time,
        end_time=end_time,
        business_key=business_key,
        outcome=outcome,
        rules_version=rules_version,
        is_error=is_error,
        before_id=before_id,
    )

    return out

# ################################################################################################################################

def _decision_story(record:'RuleDecisionRecord') -> 'anydict':
    """ Returns one decision's full story, loud when the capture dial kept headers only.
    """
    payload = record.payload

    # A sampled-away story cannot be copied or replayed - only its headers remain.
    if payload is None:
        message = f'Decision {record.decision_id} kept headers only - there is no payload to work with'
        raise BadRequestError(message)

    out = json.loads(payload)
    return out

# ################################################################################################################################
# ################################################################################################################################

@json_api
def decision_list(req:'any_') -> 'any_':
    """ The decision log - filterable by ruleset, business key, outcome, version, errors and time, keyset-paged.
    """
    filters = _read_filters(req)
    limit = read_int(req, 'limit', _default_limit)

    backend = get_backend()
    records = backend.reporting.list_decisions(filters, limit=limit)
    items = serialize_all(records, decision_row)

    out = JsonResponse({'items': items})
    return out

# ################################################################################################################################

@json_api
def decision_detail(req:'any_', decision_id:'str') -> 'any_':
    """ One decision joined to the exact version of the rules that made it.
    """
    backend = get_backend()
    record = backend.decisions.get(decision_id)

    version = backend.versions.get(record.ruleset_id, record.rules_version)
    version_data = version_row(version)

    # Only documents that carry rule documents have a readable rendered form.
    document = version_data['document']
    if Documents_Key in document:
        version_data['rendered'] = render_documents(document[Documents_Key])
    else:
        version_data['rendered'] = None

    out = JsonResponse({'decision': decision_row(record), 'version': version_data})
    return out

# ################################################################################################################################

@json_api
def decision_aggregates(req:'any_') -> 'any_':
    """ Aggregates with drill-down - outcome, version and hourly counts plus the average duration, one filter for all.
    """
    filters = _read_filters(req)
    backend = get_backend()

    outcomes = _count_rows(backend.reporting.outcome_counts(filters))
    versions = _count_rows(backend.reporting.version_counts(filters))
    hourly = _count_rows(backend.reporting.hourly_counts(filters))
    average_duration_ms = backend.reporting.average_duration_ms(filters)

    out = JsonResponse({
        'outcomes': outcomes,
        'versions': versions,
        'hourly': hourly,
        'average_duration_ms': average_duration_ms,
    })
    return out

# ################################################################################################################################

def _count_rows(points:'any_') -> 'dictlist':
    """ Serializes one list of count points.
    """
    out = []

    for point in points:
        row = {'key': point.key, 'count': point.item_count}
        out.append(row)

    return out

# ################################################################################################################################

@json_api
def decision_rule_counts(req:'any_', definition_id:'int') -> 'any_':
    """ Per-rule firing counts by day, plus the rules of the live version that never fired at all.
    """
    start_time = read_time(req, 'start_time')
    end_time = read_time(req, 'end_time')

    if rules_version := req.GET.get('rules_version'):
        rules_version = int(rules_version)
    else:
        rules_version = None

    backend = get_backend()
    points = backend.reporting.daily_rule_counts(
        ruleset_id=definition_id,
        start_time=start_time,
        end_time=end_time,
        rules_version=rules_version,
    )

    fired:'dictlist' = []

    for point in points:
        row = {
            'rule_id': point.rule_id,
            'day_bucket': point.day_bucket,
            'rules_version': point.rules_version,
            'firing_count': point.firing_count,
        }
        fired.append(row)

    # The live version's rule names are the reference for what should have fired.
    live = backend.versions.get_live(definition_id)
    documents = ruleset_documents(backend, definition_id, live.version)
    known_rule_ids = list(documents)

    never_fired = backend.reporting.rules_that_never_fired(
        ruleset_id=definition_id,
        known_rule_ids=known_rule_ids,
        start_time=start_time,
        end_time=end_time,
        rules_version=rules_version,
    )

    out = JsonResponse({'fired': fired, 'never_fired': never_fired})
    return out

# ################################################################################################################################

@json_api
def decision_to_scenario(req:'any_', decision_id:'str') -> 'any_':
    """ Copies one logged decision into a ready-made test scenario - the input as given, the outputs as expected.
    """
    backend = get_backend()
    record = backend.decisions.get(decision_id)
    story = _decision_story(record)

    scenario = {
        'name': f'Decision {decision_id}',
        'input': story['input'],
        'expected': story['outputs'],
    }

    out = JsonResponse({'scenario': scenario})
    return out

# ################################################################################################################################

@json_api
def decision_replay(req:'any_', decision_id:'str') -> 'any_':
    """ Replays one logged decision's input against any stored version, drafts included.
    """
    body = read_json(req)
    version = required(body, 'version')

    backend = get_backend()
    record = backend.decisions.get(decision_id)
    story = _decision_story(record)

    documents = ruleset_documents(backend, record.ruleset_id, version)
    loaded = load_documents(documents)
    result = evaluate_input(loaded, story['input'])

    out = JsonResponse({'decision_id': decision_id, 'replayed_version': version, 'result': result})
    return out

# ################################################################################################################################
# ################################################################################################################################

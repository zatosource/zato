# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.diff import diff_documents
from zato.common.rule_engine.loading import load_live_ruleset
from zato.common.rule_engine.outcome_diff import outcome_diff
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key, Event_Type_Review_Commented
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.storage import get_backend, get_manager
from zato.rule_engine_dashboard.app.views.api import definition_row, event_row, json_api, json_api_admin, note_answer, \
    read_int, read_int_required, read_json, required, ruleset_documents, serialize_all, version_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleApprovalRecord
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many history events one timeline returns when the request does not say otherwise.
_default_timeline_limit = 100

# ################################################################################################################################
# ################################################################################################################################

@json_api
def version_timeline(req:'any_', definition_id:'int') -> 'any_':
    """ The versions screen's timeline - the definition and its history events, newest first.
    """
    limit = read_int(req, 'limit', _default_timeline_limit)

    backend = get_backend()
    record = backend.definitions.get(definition_id)
    events = backend.events.list(definition_id=definition_id, limit=limit)

    events_text = count_text(len(events), 'history event', 'history events')
    note_answer(req, f'{record.object_type} `{record.name}`, {events_text}')

    out = JsonResponse({'definition': definition_row(record), 'events': serialize_all(events, event_row)})
    return out

# ################################################################################################################################

@json_api
def version_get(req:'any_', definition_id:'int', version:'int') -> 'any_':
    """ One immutable version snapshot together with its readable rendered form.
    """
    backend = get_backend()
    record = backend.versions.get(definition_id, version)
    row = version_row(record)

    # Only documents that carry rule documents have a readable rendered form.
    document = row['document']
    if Documents_Key in document:
        row['rendered'] = render_documents(document[Documents_Key])
        rules_text = count_text(len(document[Documents_Key]), 'rule', 'rules')
        note_answer(req, f'version {version} of definition {definition_id}, {rules_text}')
    else:
        row['rendered'] = None
        note_answer(req, f'version {version} of definition {definition_id}')

    out = JsonResponse(row)
    return out

# ################################################################################################################################

@json_api
def version_diff(req:'any_', definition_id:'int') -> 'any_':
    """ The structural diff between two versions - added, deleted, renamed, updated and unchanged rules.
    """
    old_version = read_int_required(req, 'old')
    new_version = read_int_required(req, 'new')

    backend = get_backend()
    old_documents = ruleset_documents(backend, definition_id, old_version)
    new_documents = ruleset_documents(backend, definition_id, new_version)

    result = diff_documents(old_documents, new_documents)

    added_text = count_text(len(result['added']), 'rule added', 'rules added')
    deleted_text = count_text(len(result['deleted']), 'rule deleted', 'rules deleted')
    renamed_text = count_text(len(result['renamed']), 'rule renamed', 'rules renamed')
    updated_text = count_text(len(result['updated']), 'rule updated', 'rules updated')
    unchanged_text = count_text(len(result['unchanged']), 'rule unchanged', 'rules unchanged')

    versions = f'versions {old_version} and {new_version} of definition {definition_id}'
    note_answer(req, f'{versions} -> {added_text}, {deleted_text}, {renamed_text}, {updated_text}, {unchanged_text}')

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def version_rollback(req:'any_', definition_id:'int') -> 'any_':
    """ Copies a past snapshot into a new linear version, publishes it and, for rulesets, hot-reloads it.
    """
    body = read_json(req)
    source_version = required(body, 'source_version')
    expected_current_version = required(body, 'expected_current_version')
    comment = required(body, 'comment')

    backend = get_backend()
    actor = req.user.username

    restored = backend.versions.restore(
        definition_id=definition_id,
        source_version=source_version,
        expected_current_version=expected_current_version,
        actor=actor,
        comment=comment,
    )

    # A restore publishes, so a restored ruleset starts running immediately.
    record = backend.definitions.get(definition_id)
    if record.object_type == Definition_Type_Ruleset:
        _ = load_live_ruleset(get_manager(), backend, definition_id)

    note = f'{record.object_type} `{record.name}` version {source_version} restored as version {restored.version}'
    note_answer(req, note)

    out = JsonResponse({'version': restored.version})
    return out

# ################################################################################################################################

@json_api
def version_compare_outcomes(req:'any_', definition_id:'int') -> 'any_':
    """ The outcome diff of the compare screen - which decisions change between two versions and why.
    """
    body = read_json(req)
    old_version = required(body, 'old_version')
    new_version = required(body, 'new_version')
    scenarios = required(body, 'scenarios')

    backend = get_backend()
    old_documents = ruleset_documents(backend, definition_id, old_version)
    new_documents = ruleset_documents(backend, definition_id, new_version)

    result = outcome_diff(old_documents, new_documents, scenarios)

    scenarios_text = count_text(len(scenarios), 'scenario', 'scenarios')
    versions = f'versions {old_version} and {new_version} of definition {definition_id}'
    note_answer(req, f'{scenarios_text} across {versions}')

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _approval_row(record:'RuleApprovalRecord') -> 'stranydict':
    """ One immutable approval as the compare screen reads it.
    """
    out = {
        'version':      record.version,
        'content_hash': record.content_hash,
        'approver':     record.approver,
        'comment':      record.comment,
        'created_at':   record.created_at.isoformat(),
    }

    return out

# ################################################################################################################################

@json_api
def approval_status(req:'any_', definition_id:'int', version:'int') -> 'any_':
    """ The complete readable approval state of one version - the effective gate settings,
    whether the version is approved and whether the approved content still matches the stored snapshot.
    """
    backend = get_backend()
    status = backend.approvals.get_status(definition_id, version)

    # A version that was never approved has no approval row to show.
    approval = status.approval
    if approval is None:
        approval_out = None
    else:
        approval_out = _approval_row(approval)

    note = f'version {version} of definition {definition_id} -> gate enabled {status.gate_enabled}'
    note_answer(req, f'{note}, approved {status.is_approved}, content matches {status.content_matches}')

    out = JsonResponse({
        'definition_id':       status.definition_id,
        'version':             status.version,
        'gate_enabled':        status.gate_enabled,
        'allow_self_approval': status.allow_self_approval,
        'is_approved':         status.is_approved,
        'content_matches':     status.content_matches,
        'approval':            approval_out,
    })
    return out

# ################################################################################################################################

@json_api
def approval_approve(req:'any_', definition_id:'int', version:'int') -> 'any_':
    """ Binds the signed-in user to one exact version and its content hash as its one immutable approval.
    """
    body = read_json(req)

    # The comment is genuinely optional - an approval stands on its own.
    if 'comment' in body:
        comment = body['comment']
    else:
        comment = None

    backend = get_backend()
    approver = req.user.username

    record = backend.approvals.approve(
        definition_id=definition_id,
        version=version,
        approver=approver,
        comment=comment,
    )

    note_answer(req, f'version {version} of definition {definition_id} approved by `{approver}`')

    out = JsonResponse(_approval_row(record))
    return out

# ################################################################################################################################

@json_api_admin
def approval_set_gate(req:'any_', definition_id:'int') -> 'any_':
    """ Turns the publish approval gate on or off, the change itself recorded as a logged event.

    Admins alone, because switching the gate off is what decides whether anyone needs approval at all.
    """
    body = read_json(req)
    enabled = required(body, 'enabled')

    backend = get_backend()
    actor = req.user.username

    record = backend.approvals.set_gate(definition_id=definition_id, enabled=enabled, actor=actor)

    note_answer(req, f'the approval gate of definition {definition_id} is now enabled {record.gate_enabled}')

    out = JsonResponse({'gate_enabled': record.gate_enabled, 'allow_self_approval': record.allow_self_approval})
    return out

# ################################################################################################################################

@json_api_admin
def approval_set_self_approval(req:'any_', definition_id:'int') -> 'any_':
    """ Allows or forbids authors approving their own versions, the change itself recorded as a logged event.

    Admins alone, because allowing self-approval lets one person both write and approve a version.
    """
    body = read_json(req)
    allowed = required(body, 'allowed')

    backend = get_backend()
    actor = req.user.username

    record = backend.approvals.set_self_approval(definition_id=definition_id, allowed=allowed, actor=actor)

    note = f'self-approval of definition {definition_id} is now allowed {record.allow_self_approval}'
    note_answer(req, note)

    out = JsonResponse({'gate_enabled': record.gate_enabled, 'allow_self_approval': record.allow_self_approval})
    return out

# ################################################################################################################################

@json_api
def version_comment(req:'any_', definition_id:'int') -> 'any_':
    """ A review comment anchored to one rule of one version, appended to the definition's history feed.
    """
    body = read_json(req)
    version = required(body, 'version')
    anchor = required(body, 'anchor')
    text = required(body, 'text')

    backend = get_backend()
    actor = req.user.username

    payload = {'anchor': anchor, 'text': text}
    record = backend.events.append(
        definition_id=definition_id,
        version=version,
        event_type=Event_Type_Review_Commented,
        actor=actor,
        payload=payload,
    )

    note_answer(req, f'a comment on `{anchor}` in version {version} of definition {definition_id}')

    out = JsonResponse(event_row(record))
    return out

# ################################################################################################################################
# ################################################################################################################################

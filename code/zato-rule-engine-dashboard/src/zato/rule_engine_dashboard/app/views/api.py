# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from datetime import datetime
from functools import wraps
from http.client import BAD_REQUEST, CONFLICT, NOT_FOUND

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.sql import InvalidDocumentError, InvalidStoreInputError, RecordNotFoundError, \
    VersionConflictError
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.rule_engine_dashboard.app.views.common import signed_in_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDecisionRecord, RuleDefinitionRecord, RuleEventRecord, RuleFollowRecord, \
        RuleRecentRecord, RuleReferenceRecord, RuleSQLBackend, RuleVersionRecord, RuleViewRecord
    from zato.common.typing_ import any_, anydict, dictlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

class BadRequestError(Exception):
    """ A request whose parameters cannot be used - always reported with a readable message.
    """

# ################################################################################################################################
# ################################################################################################################################

def _error(message:'str', status:'int') -> 'JsonResponse':
    """ One readable error message under one HTTP status.
    """
    out = JsonResponse({'error': message}, status=status)
    return out

# ################################################################################################################################

def json_api(view:'any_') -> 'any_':
    """ Signed-in JSON endpoints - boundary and store errors become readable JSON responses with matching statuses.
    """
    @wraps(view)
    @signed_in_required
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':

        try:
            out = view(req, *args, **kwargs)
        except BadRequestError as e:
            out = _error(str(e), BAD_REQUEST)
        except RecordNotFoundError as e:
            out = _error(str(e), NOT_FOUND)
        except VersionConflictError as e:
            out = _error(str(e), CONFLICT)
        except (InvalidDocumentError, InvalidStoreInputError) as e:
            out = _error(str(e), BAD_REQUEST)

        return out

    return wrapper

# ################################################################################################################################
# ################################################################################################################################

def read_json(req:'any_') -> 'anydict':
    """ Returns the request's JSON body, loud when it is not a JSON object.
    """
    try:
        out = json.loads(req.body)
    except json.JSONDecodeError as e:
        message = f'Request body is not valid JSON -> {e}'
        raise BadRequestError(message) from e

    body_is_dict = isinstance(out, dict)
    if not body_is_dict:
        raise BadRequestError('Request body must be a JSON object')

    return out

# ################################################################################################################################

def required(body:'anydict', name:'str') -> 'any_':
    """ Returns a field every request of a given kind must carry.
    """
    if name not in body:
        message = f'Missing required field -> {name}'
        raise BadRequestError(message)

    out = body[name]
    return out

# ################################################################################################################################

def read_int(req:'any_', name:'str', default:'int') -> 'int':
    """ Returns an integer query parameter or the caller's configured default.
    """
    if value := req.GET.get(name):
        try:
            out = int(value)
        except ValueError as e:
            message = f'Invalid integer in `{name}` -> {value}'
            raise BadRequestError(message) from e
    else:
        out = default

    return out

# ################################################################################################################################

def read_int_required(req:'any_', name:'str') -> 'int':
    """ Returns an integer query parameter every request of a given kind must carry.
    """
    if value := req.GET.get(name):
        try:
            out = int(value)
        except ValueError as e:
            message = f'Invalid integer in `{name}` -> {value}'
            raise BadRequestError(message) from e
    else:
        message = f'Missing required parameter -> {name}'
        raise BadRequestError(message)

    return out

# ################################################################################################################################

def read_time(req:'any_', name:'str') -> 'datetime | None':
    """ Returns an optional ISO-8601 timestamp query parameter.
    """
    if value := req.GET.get(name):
        try:
            out = datetime.fromisoformat(value)
        except ValueError as e:
            message = f'Invalid timestamp in `{name}` -> {value}'
            raise BadRequestError(message) from e
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

def documents_of_version(record:'RuleVersionRecord') -> 'anydict':
    """ Returns the canonical rule documents one stored version snapshot carries.
    """
    payload = deserialize_document(record.document)

    # Only runnable ruleset snapshots keep rule documents - anything else cannot be diffed, run or replayed.
    if Documents_Key not in payload:
        message = f'Version {record.version} of definition {record.definition_id} has no rule documents'
        raise BadRequestError(message)

    out = payload[Documents_Key]
    return out

# ################################################################################################################################

def ruleset_documents(backend:'RuleSQLBackend', definition_id:'int', version:'int') -> 'anydict':
    """ Returns the rule documents of one stored ruleset version.
    """
    record = backend.versions.get(definition_id, version)

    out = documents_of_version(record)
    return out

# ################################################################################################################################

def serialize_all(records:'any_', serializer:'any_') -> 'dictlist':
    """ Applies one row serializer to every record of a store's answer.
    """
    out = []

    for record in records:
        row = serializer(record)
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def definition_row(record:'RuleDefinitionRecord') -> 'stranydict':
    """ One definition as a list or preview row.
    """
    out = {
        'id':              record.id,
        'name':            record.name,
        'object_type':     record.object_type,
        'parent_id':       record.parent_id,
        'current_version': record.current_version,
        'live_version':    record.live_version,
        'is_active':       record.is_active,
        'created_at':      record.created_at.isoformat(),
        'updated_at':      record.updated_at.isoformat(),
    }

    return out

# ################################################################################################################################

def version_row(record:'RuleVersionRecord') -> 'stranydict':
    """ One immutable version snapshot together with its parsed document.
    """
    document = deserialize_document(record.document)

    out = {
        'definition_id': record.definition_id,
        'version':       record.version,
        'author':        record.author,
        'comment':       record.comment,
        'created_at':    record.created_at.isoformat(),
        'document':      document,
    }

    return out

# ################################################################################################################################

def event_row(record:'RuleEventRecord') -> 'stranydict':
    """ One history event with its parsed payload.
    """
    # Not every event carries a payload, hence the boundary check.
    payload = record.payload
    if payload is None:
        parsed = None
    else:
        parsed = json.loads(payload)

    out = {
        'id':            record.id,
        'definition_id': record.definition_id,
        'version':       record.version,
        'event_type':    record.event_type,
        'actor':         record.actor,
        'created_at':    record.created_at.isoformat(),
        'payload':       parsed,
    }

    return out

# ################################################################################################################################

def decision_row(record:'RuleDecisionRecord') -> 'stranydict':
    """ One logged decision - the promoted header always, the full story when the capture dial kept it.
    """
    # The story is sampled away for some successful decisions, hence the boundary checks.
    payload = record.payload
    if payload is None:
        story = None
    else:
        story = json.loads(payload)

    fired_rule_ids = record.fired_rule_ids
    if fired_rule_ids is None:
        fired = None
    else:
        fired = json.loads(fired_rule_ids)

    out = {
        'decision_id':    record.decision_id,
        'ruleset_id':     record.ruleset_id,
        'rules_version':  record.rules_version,
        'occurred_at':    record.occurred_at.isoformat(),
        'business_key':   record.business_key,
        'outcome':        record.outcome,
        'is_error':       record.is_error,
        'duration_ms':    record.duration_ms,
        'has_payload':    record.has_payload,
        'story':          story,
        'fired_rule_ids': fired,
    }

    return out

# ################################################################################################################################

def reference_row(record:'RuleReferenceRecord') -> 'stranydict':
    """ One where-used index entry.
    """
    out = {
        'definition_id': record.definition_id,
        'rule_name':     record.rule_name,
        'term':          record.term,
        'block':         record.block,
        'role':          record.role,
    }

    return out

# ################################################################################################################################

def follow_row(record:'RuleFollowRecord') -> 'stranydict':
    """ One follow entry.
    """
    out = {
        'definition_id': record.definition_id,
        'actor':         record.actor,
        'created_at':    record.created_at.isoformat(),
        'last_seen_at':  record.last_seen_at.isoformat(),
    }

    return out

# ################################################################################################################################

def view_row(record:'RuleViewRecord') -> 'stranydict':
    """ One saved view with its parsed filter payload.
    """
    payload = json.loads(record.payload)

    out = {
        'name':       record.name,
        'payload':    payload,
        'created_at': record.created_at.isoformat(),
        'updated_at': record.updated_at.isoformat(),
    }

    return out

# ################################################################################################################################

def recent_row(record:'RuleRecentRecord') -> 'stranydict':
    """ One recently visited definition.
    """
    out = {
        'definition_id': record.definition_id,
        'visited_at':    record.visited_at.isoformat(),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

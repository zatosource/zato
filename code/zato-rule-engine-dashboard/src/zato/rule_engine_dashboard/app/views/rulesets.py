# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine import webapi
from zato.common.rule_engine.loading import publish_and_reload
from zato.common.rule_engine.references import apply_ruleset_rename, preview_ruleset_rename
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.data import DecisionFilter
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.tokens import ruleset_name_pattern
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.storage import get_backend, get_manager
from zato.rule_engine_dashboard.app.views.api import BadRequestError, definition_row, event_row, follow_row, json_api, \
    json_items, note_answer, read_int, read_json, required, serialize_all, view_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How many rows the list returns when the request does not say otherwise.
_default_limit = 100

# Where the list starts when the request does not say otherwise.
_default_offset = 0

# How many history events one preview shows.
_preview_event_limit = 20

# A rename that does not say otherwise only previews its impact.
_default_dry_run = True

# ################################################################################################################################
# ################################################################################################################################

@json_api
def ruleset_list(req:'any_') -> 'any_':
    """ The home screen's list - every definition, filterable by kind and content, paged.
    """
    object_type = req.GET.get('object_type')
    search_text = req.GET.get('search')
    include_inactive = req.GET.get('include_inactive') == 'true'
    limit = read_int(req, 'limit', _default_limit)
    offset = read_int(req, 'offset', _default_offset)

    result, note = webapi.list_definitions(
        get_backend(),
        object_type=object_type,
        search_text=search_text,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_search(req:'any_') -> 'any_':
    """ Full-text search over rendered rule sentences, each hit carrying its match position.
    """
    if query := req.GET.get('q'):
        pass
    else:
        raise BadRequestError('Missing required parameter -> q')

    result, note = webapi.search_definitions(get_backend(), query)
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_feed(req:'any_') -> 'any_':
    """ The change feed - what happened to followed definitions since they were last seen.
    """
    backend = get_backend()
    events = backend.follows.feed(req.user.username)
    items = serialize_all(events, event_row)

    out = json_items(req, items, 'unseen change', 'unseen changes')
    return out

# ################################################################################################################################

@json_api
def ruleset_preview(req:'any_', definition_id:'int') -> 'any_':
    """ Preview without opening - the definition, its rendered rules, recent history and follow state.
    """
    backend = get_backend()
    actor = req.user.username

    result, note = webapi.preview_definition(backend, definition_id)

    # The shared preview stops at the definition and its document - the history
    # and the follow state are this screen's own additions.
    events = backend.events.list(definition_id=definition_id, limit=_preview_event_limit)
    is_following = backend.follows.is_following(actor=actor, definition_id=definition_id)

    result['events'] = serialize_all(events, event_row)
    result['is_following'] = is_following

    events_text = count_text(len(events), 'history event', 'history events')
    note_answer(req, f'{note}, {events_text}')

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_publish(req:'any_', definition_id:'int') -> 'any_':
    """ Makes one stored version live - rulesets additionally hot-reload without a restart.
    """
    body = read_json(req)
    version = required(body, 'version')

    backend = get_backend()
    actor = req.user.username
    record = backend.definitions.get(definition_id)

    # Rulesets go live and start running in one step ..
    if record.object_type == Definition_Type_Ruleset:
        loaded = publish_and_reload(get_manager(), backend, definition_id=definition_id, version=version, actor=actor)
        result = {'version': loaded.version, 'rule_names': loaded.rule_names}
        rules_text = count_text(len(loaded.rule_names), 'rule', 'rules')
        note = f'ruleset `{record.name}` version {loaded.version} is live with {rules_text}'
        note_answer(req, note)

    # .. every other definition kind only moves the live pointer.
    else:
        published = backend.versions.publish(definition_id=definition_id, version=version, actor=actor)
        result = {'version': published.version, 'rule_names': []}
        note = f'{record.object_type} `{record.name}` version {published.version} is live'
        note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_rename(req:'any_', definition_id:'int') -> 'any_':
    """ Renames one ruleset and every rule name inside it - a dry run reports the impact without changing anything.

    A ruleset is addressed by name over REST, so the impact worth knowing before renaming is how many
    calls the current name has already served, next to the rule names the rename rewrites.
    """
    body = read_json(req)
    new_name = required(body, 'new_name')

    # The name is the REST path callers invoke, so it has to be one a path can carry.
    if not ruleset_name_pattern.match(new_name):
        raise BadRequestError(f'A ruleset name is dotted words, letters, digits and underscores only -> {new_name}')

    # A rename is a preview unless the request explicitly asks to apply it.
    if 'dry_run' in body:
        is_dry_run = body['dry_run']
    else:
        is_dry_run = _default_dry_run

    backend = get_backend()
    actor = req.user.username

    record = backend.definitions.get(definition_id)
    document = deserialize_document(record.document)

    # Only a stored document carrying rule documents has rule names to rewrite.
    if Documents_Key in document:
        documents = document[Documents_Key]
    else:
        documents = {}

    impact = preview_ruleset_rename(new_name, documents)

    # How much traffic the name being renamed has served, as far back as the decision log keeps.
    filters = DecisionFilter(ruleset_id=definition_id)
    rest_call_count = backend.reporting.decision_count(filters)

    result = {
        'definition_id': definition_id,
        'old_name': record.name,
        'new_name': new_name,
        'dry_run': is_dry_run,
        'rules': impact,
        'rest_call_count': rest_call_count,
    }

    rules_text = count_text(len(impact), 'rule', 'rules')
    calls_text = count_text(rest_call_count, 'logged call', 'logged calls')

    # The dry run stops at the impact report ..
    if is_dry_run:
        note = f'`{record.name}` would become `{new_name}`, {rules_text}, {calls_text}'
        note_answer(req, note)

        out = JsonResponse(result)
        return out

    # .. while an applied rename rewrites every rule of the ruleset ..
    renamed = apply_ruleset_rename(new_name, documents)
    rewritten = dict(document)
    rewritten[Documents_Key] = renamed

    # .. stores the rewrite as a new optimistic version ..
    comment = f'Rename ruleset {record.name} to {new_name}'
    version = backend.versions.create(
        definition_id=definition_id,
        expected_current_version=record.current_version,
        document=rewritten,
        author=actor,
        comment=comment,
    )

    # .. gives the definition its new name, which is what changes the address callers use ..
    _ = backend.definitions.rename(definition_id=definition_id, name=new_name, actor=actor)

    # .. and keeps the where-used index true to the rule names now stored.
    _ = backend.references.rebuild(definition_id=definition_id, documents=renamed)

    result['version'] = version.version

    note = f'`{record.name}` renamed to `{new_name}` as version {version.version}, {rules_text}'
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_follow(req:'any_', definition_id:'int') -> 'any_':
    """ Starts following one definition.
    """
    backend = get_backend()
    _ = backend.follows.follow(actor=req.user.username, definition_id=definition_id)

    note_answer(req, f'now following definition {definition_id}')

    out = JsonResponse({'definition_id': definition_id, 'is_following': True})
    return out

# ################################################################################################################################

@json_api
def ruleset_unfollow(req:'any_', definition_id:'int') -> 'any_':
    """ Stops following one definition.
    """
    backend = get_backend()
    backend.follows.unfollow(actor=req.user.username, definition_id=definition_id)

    note_answer(req, f'no longer following definition {definition_id}')

    out = JsonResponse({'definition_id': definition_id, 'is_following': False})
    return out

# ################################################################################################################################

@json_api
def follow_list(req:'any_') -> 'any_':
    """ Everything the requesting user follows - the Followed chip and the row stars read this.
    """
    backend = get_backend()
    records = backend.follows.list_followed(req.user.username)
    items = serialize_all(records, follow_row)

    out = json_items(req, items, 'followed definition', 'followed definitions')
    return out

# ################################################################################################################################

@json_api
def ruleset_mark_seen(req:'any_', definition_id:'int') -> 'any_':
    """ Moves the feed clock past everything that already happened to one followed definition.
    """
    backend = get_backend()
    backend.follows.mark_seen(actor=req.user.username, definition_id=definition_id)

    note_answer(req, f'definition {definition_id} marked as seen')

    out = JsonResponse({'definition_id': definition_id})
    return out

# ################################################################################################################################

@json_api
def view_list(req:'any_') -> 'any_':
    """ The actor's saved views.
    """
    backend = get_backend()
    records = backend.views.list(req.user.username)
    items = serialize_all(records, view_row)

    out = json_items(req, items, 'saved view', 'saved views')
    return out

# ################################################################################################################################

@json_api
def view_save(req:'any_') -> 'any_':
    """ Saves one named view, replacing any earlier payload under the same name.
    """
    body = read_json(req)
    name = required(body, 'name')
    payload = required(body, 'payload')

    backend = get_backend()
    record = backend.views.save(actor=req.user.username, name=name, payload=payload)

    note_answer(req, f'saved the view `{name}`')

    out = JsonResponse(view_row(record))
    return out

# ################################################################################################################################

@json_api
def view_delete(req:'any_') -> 'any_':
    """ Deletes one saved view by name.
    """
    body = read_json(req)
    name = required(body, 'name')

    backend = get_backend()
    backend.views.delete(actor=req.user.username, name=name)

    note_answer(req, f'deleted the view `{name}`')

    out = JsonResponse({'name': name})
    return out

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

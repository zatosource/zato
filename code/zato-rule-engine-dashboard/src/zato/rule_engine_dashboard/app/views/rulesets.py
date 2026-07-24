# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.loading import publish_and_reload
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.rule_engine_dashboard.app.storage import get_backend, get_manager
from zato.rule_engine_dashboard.app.views.api import BadRequestError, definition_row, event_row, json_api, read_int, \
    read_json, recent_row, required, serialize_all, view_row

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

    backend = get_backend()
    records = backend.definitions.list(
        object_type=object_type,
        search_text=search_text,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    items = serialize_all(records, definition_row)

    out = JsonResponse({'items': items})
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

    backend = get_backend()
    hits = backend.search.search(query)

    out = JsonResponse({'items': hits})
    return out

# ################################################################################################################################

@json_api
def ruleset_feed(req:'any_') -> 'any_':
    """ The change feed - what happened to followed definitions since they were last seen.
    """
    backend = get_backend()
    events = backend.follows.feed(req.user.username)
    items = serialize_all(events, event_row)

    out = JsonResponse({'items': items})
    return out

# ################################################################################################################################

@json_api
def ruleset_preview(req:'any_', definition_id:'int') -> 'any_':
    """ Preview without opening - the definition, its rendered rules, recent history and follow state.
    """
    backend = get_backend()
    actor = req.user.username

    record = backend.definitions.get(definition_id)
    document = deserialize_document(record.document)
    events = backend.events.list(definition_id=definition_id, limit=_preview_event_limit)
    is_following = backend.follows.is_following(actor=actor, definition_id=definition_id)

    # Only documents that carry rule documents have a readable rendered form.
    if Documents_Key in document:
        rendered = render_documents(document[Documents_Key])
    else:
        rendered = None

    # Opening a preview counts as a visit for the recents strip.
    backend.views.touch_recent(actor=actor, definition_id=definition_id)

    out = JsonResponse({
        'definition': definition_row(record),
        'document': document,
        'rendered': rendered,
        'events': serialize_all(events, event_row),
        'is_following': is_following,
    })
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

    # .. every other definition kind only moves the live pointer.
    else:
        published = backend.versions.publish(definition_id=definition_id, version=version, actor=actor)
        result = {'version': published.version, 'rule_names': []}

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def ruleset_follow(req:'any_', definition_id:'int') -> 'any_':
    """ Starts following one definition.
    """
    backend = get_backend()
    _ = backend.follows.follow(actor=req.user.username, definition_id=definition_id)

    out = JsonResponse({'definition_id': definition_id, 'is_following': True})
    return out

# ################################################################################################################################

@json_api
def ruleset_unfollow(req:'any_', definition_id:'int') -> 'any_':
    """ Stops following one definition.
    """
    backend = get_backend()
    backend.follows.unfollow(actor=req.user.username, definition_id=definition_id)

    out = JsonResponse({'definition_id': definition_id, 'is_following': False})
    return out

# ################################################################################################################################

@json_api
def ruleset_mark_seen(req:'any_', definition_id:'int') -> 'any_':
    """ Moves the feed clock past everything that already happened to one followed definition.
    """
    backend = get_backend()
    backend.follows.mark_seen(actor=req.user.username, definition_id=definition_id)

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

    out = JsonResponse({'items': items})
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

    out = JsonResponse({'name': name})
    return out

# ################################################################################################################################

@json_api
def recent_list(req:'any_') -> 'any_':
    """ The actor's recently visited definitions, newest first.
    """
    backend = get_backend()
    records = backend.views.list_recents(req.user.username)
    items = serialize_all(records, recent_row)

    out = JsonResponse({'items': items})
    return out

# ################################################################################################################################
# ################################################################################################################################

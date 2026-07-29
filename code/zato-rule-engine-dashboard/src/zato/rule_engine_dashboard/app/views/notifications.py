# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_GATEWAY, FORBIDDEN

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.notify.credentials import credentials_status, NotifyConfigError, save_credentials
from zato.common.rule_engine.notify.delivery import list_targets, send_test_message
from zato.common.rule_engine.notify.matrix import notification_matrix
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import BadRequestError, json_api, json_items, note_answer, read_json, \
    required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleNotifyDestinationRecord
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

def _admin_only(req:'any_') -> 'JsonResponse | None':
    """ Returns a refusal for non-admins, None for admins.
    """
    if req.user.is_superuser:
        out = None
    else:
        note_answer(req, 'refused, admins only')
        out = JsonResponse({'error': 'Admins only'}, status=FORBIDDEN)

    return out

# ################################################################################################################################

def destination_row(record:'RuleNotifyDestinationRecord') -> 'stranydict':
    """ One destination with its delivery status - what the ruleset's notification tab shows.
    """
    # A destination that never delivered has no timestamp yet.
    last_delivery_at = record.last_delivery_at
    if last_delivery_at is None:
        delivered_at = None
    else:
        delivered_at = last_delivery_at.isoformat()

    out = {
        'id':               record.id,
        'definition_id':    record.definition_id,
        'kind':             record.kind,
        'target':           record.target,
        'is_active':        record.is_active,
        'last_status':      record.last_status,
        'last_error':       record.last_error,
        'last_delivery_at': delivered_at,
        'created_at':       record.created_at.isoformat(),
        'created_by':       record.created_by,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@json_api
def chat_config_status(req:'any_') -> 'any_':
    """ Which chat platforms have credentials - never the credentials themselves.
    """
    if refusal := _admin_only(req):
        return refusal

    backend = get_backend()
    items = credentials_status(backend)

    out = json_items(req, items, 'chat platform', 'chat platforms')
    return out

# ################################################################################################################################

@json_api
def chat_config_save(req:'any_') -> 'any_':
    """ Stores one platform's credentials, encrypted in the rule engine database.
    """
    if refusal := _admin_only(req):
        return refusal

    body = read_json(req)
    kind = required(body, 'kind')
    values = required(body, 'values')

    backend = get_backend()
    save_credentials(backend, kind=kind, values=values, actor=req.user.username)

    note_answer(req, f'credentials of `{kind}` stored')

    out = JsonResponse({'kind': kind, 'is_configured': True})
    return out

# ################################################################################################################################

@json_api
def chat_config_test(req:'any_') -> 'any_':
    """ Sends the test message to one target so admins see their credentials work before anyone relies on them.
    """
    if refusal := _admin_only(req):
        return refusal

    body = read_json(req)
    kind = required(body, 'kind')
    target = required(body, 'target')

    backend = get_backend()

    # The platform's answer travels back to the admin verbatim - it names what to fix,
    # while configuration errors keep flowing to the shared bad-request handler.
    try:
        send_test_message(backend, kind, target)
    except NotifyConfigError:
        raise
    except Exception as e:
        note_answer(req, f'the test message to `{target}` on `{kind}` was refused -> {e}')
        out = JsonResponse({'error': str(e)}, status=BAD_GATEWAY)
        return out

    note_answer(req, f'the test message reached `{target}` on `{kind}`')

    out = JsonResponse({'kind': kind, 'target': target, 'is_delivered': True})
    return out

# ################################################################################################################################

@json_api
def target_list(req:'any_') -> 'any_':
    """ The live picker - what channels one platform offers right now.
    """
    kind = req.GET.get('kind')
    if not kind:
        raise BadRequestError('Missing required parameter -> kind')

    backend = get_backend()

    # The platform's answer travels back verbatim when the listing fails,
    # while configuration errors keep flowing to the shared bad-request handler.
    try:
        items = list_targets(backend, kind)
    except NotifyConfigError:
        raise
    except Exception as e:
        note_answer(req, f'`{kind}` could not be listed -> {e}')
        out = JsonResponse({'error': str(e)}, status=BAD_GATEWAY)
        return out

    out = json_items(req, items, f'target on `{kind}`', f'targets on `{kind}`')
    return out

# ################################################################################################################################

@json_api
def event_matrix(req:'any_') -> 'any_':
    """ The complete, fixed matrix of events destinations are notified about.
    """
    items = notification_matrix()

    out = json_items(req, items, 'event type', 'event types')
    return out

# ################################################################################################################################
# ################################################################################################################################

@json_api
def destination_list(req:'any_', definition_id:'int') -> 'any_':
    """ One ruleset's destinations with their delivery status.
    """
    backend = get_backend()
    records = backend.notifications.list_destinations(definition_id=definition_id, include_inactive=True)

    items = []
    for record in records:
        row = destination_row(record)
        items.append(row)

    out = json_items(req, items, 'destination', 'destinations')
    return out

# ################################################################################################################################

@json_api
def destination_add(req:'any_', definition_id:'int') -> 'any_':
    """ Adds one channel or person to one ruleset's notification list.
    """
    body = read_json(req)
    kind = required(body, 'kind')
    target = required(body, 'target')

    backend = get_backend()
    record = backend.notifications.add_destination(
        definition_id=definition_id,
        kind=kind,
        target=target,
        actor=req.user.username,
    )

    row = destination_row(record)

    note_answer(req, f'`{target}` on `{kind}` added to definition {definition_id}')

    out = JsonResponse(row)
    return out

# ################################################################################################################################

@json_api
def destination_delete(req:'any_', destination_id:'int') -> 'any_':
    """ Removes one destination together with its cursor and delivery status.
    """
    backend = get_backend()
    backend.notifications.delete_destination(destination_id)

    note_answer(req, f'destination {destination_id} removed')

    out = JsonResponse({'is_deleted': True})
    return out

# ################################################################################################################################
# ################################################################################################################################

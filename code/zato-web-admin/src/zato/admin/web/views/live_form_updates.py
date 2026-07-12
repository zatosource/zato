# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseBadRequest

# Zato
from zato.admin.web.util import get_pubsub_security_definitions
from zato.admin.web.views import method_allowed
from zato.common.api import SEC_DEF_TYPE_NAME
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictlist, stranydict, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Dispatch table mapping object_type -> how to fetch the current list from Zato services.
# Each entry has:
#   service_name  - the Zato service to invoke
#   fetch_func    - alternative to service_name, a callable(req) -> list of dicts, used when
#                   the page builds its list through a helper rather than a single service call
#   id_field      - field used as the unique identifier for diffing
#   id_format     - optional format string building the identifier out of several fields
#   label_format  - format string producing the exact label that the page displays for an item
#   extra_params  - additional params passed to the service invocation
#   filter_func   - optional callable(item) -> bool to exclude items from the list
#
# The fetch, the filter and the label must all match exactly what the page itself renders,
# otherwise each poll would keep reporting differences that do not exist.

def _security_basic_filter(item:'strdict') -> 'bool':

    # This must match the filter that the security groups page applies when it renders its own list.
    name = item['name']

    if name in ('ide_publisher', 'pubapi'):
        return False

    if 'zato.' in name:
        return False

    return True

# ################################################################################################################################

def _pubsub_permission_security(req:'any_') -> 'dictlist':

    # The same helper that populates the page's own dropdown, so both always agree.
    out = get_pubsub_security_definitions(req, 'create', 'permission')
    return out

# ################################################################################################################################

def _pubsub_subscription_security(req:'any_') -> 'dictlist':

    # The same helper that populates the page's own dropdown, so both always agree.
    out = get_pubsub_security_definitions(req, 'create', 'subscription')
    return out

# ################################################################################################################################

OBJECT_TYPE_CONFIG:'stranydict' = {

    'service': {
        'service_name': 'zato.service.get-list',
        'id_field': 'name',
        'label_format': '{name}',
        'extra_params': {
            'paginate': False,
        },
        'filter_func': None,
    },

    'security': {
        'service_name': 'zato.security.get-list',
        'id_field': 'id',
        'id_format': '{sec_type}/{id}',
        'label_format': '{sec_type_name}/{name}',
        'extra_params': {
            'paginate': False,
        },
        'filter_func': None,
    },

    'security_basic': {
        'service_name': 'zato.security.get-list',
        'id_field': 'id',
        'label_format': '{name}',
        'extra_params': {
            'sec_type': ['apikey', 'basic_auth'],
            'paginate': False,
        },
        'filter_func': _security_basic_filter,
    },

    'security_pubsub_permission': {
        'fetch_func': _pubsub_permission_security,
        'id_field': 'id',
        'label_format': '{name}',
        'filter_func': None,
    },

    'security_pubsub_subscription': {
        'fetch_func': _pubsub_subscription_security,
        'id_field': 'id',
        'label_format': '{name}',
        'filter_func': None,
    },

    'security_group': {
        'service_name': 'zato.groups.get-list',
        'id_field': 'id',
        'label_format': '{name}',
        'extra_params': {'group_type': 'zato-api-creds'},
        'filter_func': None,
    },

    'rest_channel': {
        'service_name': 'zato.http-soap.get-list',
        'id_field': 'id',
        'label_format': '{name}',
        'extra_params': {'connection': 'channel', 'transport': 'plain_http'},
        'filter_func': None,
    },

    'rest_outconn': {
        'service_name': 'zato.http-soap.get-list',
        'id_field': 'id',
        'label_format': '{name}',
        'extra_params': {'connection': 'outgoing', 'transport': 'plain_http'},
        'filter_func': None,
    },

    'pubsub_topic': {
        'service_name': 'zato.pubsub.topic.get-list',
        'id_field': 'id',
        'label_format': '{name}',
        'extra_params': {},
        'filter_func': None,
    },
}

# ################################################################################################################################
# ################################################################################################################################

def _fetch_list(req:'any_', object_type:'str') -> 'dictlist':
    """ Fetches the current list of objects for a given type, either through the same helper
    that the page itself uses or by invoking the appropriate Zato service.
    Returns a list of dicts, each containing the _id and _label fields plus any extra fields the JS side may need.
    """
    _fl_logger = getLogger('zato.live_form_updates')

    config = OBJECT_TYPE_CONFIG[object_type]

    # Pages that build their lists through a helper share that helper with us,
    # so the poll can never disagree with what the page displays.
    if fetch_func := config.get('fetch_func'):
        try:
            data = fetch_func(req)
        except Exception:
            _fl_logger.info('live_form_updates._fetch_list: EXCEPTION in fetch_func for %s: %s', object_type, format_exc())
            return []
    else:
        params = {'cluster_id': req.zato.cluster_id}
        params.update(config['extra_params'])

        try:
            response = req.zato.client.invoke(config['service_name'], params)
        except Exception:
            _fl_logger.info('live_form_updates._fetch_list: EXCEPTION invoking %s: %s', config['service_name'], format_exc())
            return []

        data = getattr(response, 'data', None)

    filter_func = config['filter_func']
    id_field = config['id_field']
    label_format = config['label_format']

    if data is None:
        logger.warning('live_form_updates._fetch_list: no data in response for %s', object_type)
        return []

    out = []
    for item in data:
        if filter_func and not filter_func(item):
            continue

        # Build the _id field. If id_format is specified, use it (e.g. '{sec_type}/{id}'),
        # otherwise just use the raw id_field value.
        id_format = config.get('id_format')
        if id_format:
            format_data = {}
            for key in ('id', 'sec_type', 'name'):
                format_data[key] = str(item.get(key, ''))
            entry_id = id_format.format(**format_data)
        else:
            entry_id = str(item.get(id_field, ''))

        entry = {'_id': entry_id}

        # Include extra fields that the JS side may need
        for extra in ('id', 'name', 'sec_type', 'is_active'):
            val = item.get(extra)
            if val is not None and extra not in entry:
                entry[extra] = val

        # Derive sec_type_name from sec_type if available
        sec_type = item.get('sec_type')
        if sec_type and sec_type in SEC_DEF_TYPE_NAME:
            entry['sec_type_name'] = SEC_DEF_TYPE_NAME[sec_type]

        # Build the exact label that the page displays for this item - the client snapshots
        # the displayed text, so both sides of the comparison use the same formatting.
        entry['_label'] = label_format.format(**entry)

        out.append(entry)

    logger.debug('live_form_updates._fetch_list: object_type=%s, returned %d items, sample_ids=%s',
        object_type, len(out), [x['_id'] for x in out[:3]])

    return out

# ################################################################################################################################
# ################################################################################################################################

def _compute_diff(client_items_by_id:'strdict', current_list:'dictlist') -> 'strdict':
    """ Computes the diff between what the client has and what the server currently has.

    Returns a dict with:
      created - list of new items (full item dicts)
      deleted - list of IDs that no longer exist
      renamed - list of {_id, old_labels, new_labels} for items whose labels changed
    """
    current_by_id = {}
    for item in current_list:
        current_by_id[item['_id']] = item

    created = []
    deleted = []
    renamed = []

    # Items that exist on the server but not on the client -> created
    for item_id, item in current_by_id.items():
        if item_id not in client_items_by_id:
            created.append(item)

    # Items that exist on the client but not on the server -> deleted
    for item_id in client_items_by_id:
        if item_id not in current_by_id:
            deleted.append(item_id)

    # Items that exist in both but have different labels -> renamed. The client snapshots
    # the displayed text under the 'name' key and the server formats _label the same way,
    # so an unchanged item always compares as equal.
    for item_id, client_labels in client_items_by_id.items():
        if item_id in current_by_id:
            server_item = current_by_id[item_id]
            server_labels = {'name': server_item['_label']}
            if server_labels != client_labels:
                renamed.append({
                    '_id': item_id,
                    'old_labels': client_labels,
                    'new_labels': server_labels,
                    'item': server_item,
                })

    return {
        'created': created,
        'deleted': deleted,
        'renamed': renamed,
    }

# ################################################################################################################################
# ################################################################################################################################

def _parse_request_data(request_data:'strdict') -> 'anylist':
    """ Parses the JSON request body sent by the client.
    Expected format:
    {
        "object_types": {
            "service": {
                "items": {"svc1": {"name": "svc1"}, "svc2": {"name": "svc2"}}
            },
            "security": {
                "items": {"1": {"sec_type": "basic_auth", "name": "My Auth"}, ...}
            }
        }
    }
    Returns a list of (object_type, client_items_by_id) tuples.
    """
    out = []
    object_types = request_data.get('object_types', {})

    for object_type, type_data in object_types.items():
        if object_type not in OBJECT_TYPE_CONFIG:
            logger.warning('live_form_updates: skipping unknown object_type=%s', object_type)
            continue
        client_items = type_data.get('items', {})
        out.append((object_type, client_items))

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_updates(req:'any_') -> 'HttpResponse':
    """ Single-shot endpoint for live form updates.
    The client sends a snapshot of the items it currently displays, the server fetches the current
    lists once, computes the diffs and returns them as JSON. The client polls this endpoint
    periodically for as long as a create or edit dialog is open, so a worker is only ever occupied
    for the duration of one fetch, never for the lifetime of the dialog.
    """
    updates_logger = getLogger('zato.live_form_updates')

    try:
        snapshot_json = req.body.decode('utf-8')
        request_data = loads(snapshot_json)
    except Exception:
        updates_logger.error('live_form_updates.get_updates: failed to parse snapshot: %s', format_exc())
        return HttpResponseBadRequest('Invalid JSON in request body')

    object_types = _parse_request_data(request_data)

    if not object_types:
        updates_logger.error('live_form_updates.get_updates: no valid object types, returning 400')
        return HttpResponseBadRequest('No valid object types provided')

    # Compute the diff between what the client displays and what the server has now
    all_diffs = {}

    for object_type, client_items in object_types:
        current_list = _fetch_list(req, object_type)
        diff = _compute_diff(client_items, current_list)

        has_changes = diff['created'] or diff['deleted'] or diff['renamed']

        if has_changes:
            updates_logger.info('live_form_updates.get_updates: DIFF for %s: created=%d, deleted=%d, renamed=%d',
                object_type, len(diff['created']), len(diff['deleted']), len(diff['renamed']))
            all_diffs[object_type] = diff

    response = HttpResponse(dumps(all_diffs), content_type='application/json')
    response['Cache-Control'] = 'no-cache'

    return response

# ################################################################################################################################
# ################################################################################################################################

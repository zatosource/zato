# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponseBadRequest, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.api import SEC_DEF_TYPE_NAME
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Dispatch table mapping object_type -> how to fetch the current list from Zato services.
# Each entry has:
#   service_name  - the Zato service to invoke
#   id_field      - field used as the unique identifier for diffing
#   label_fields  - fields that, if changed, indicate a rename
#   extra_params  - additional params passed to the service invocation
#   filter_func   - optional callable(item) -> bool to exclude items from the list

def _default_filter(item):
    name = item.get('name', '')
    if name in ('ide_publisher', 'pubapi'):
        return False
    if 'zato.' in name:
        return False
    return True

_service_filter = _default_filter

OBJECT_TYPE_CONFIG = {

    'service': {
        'service_name': 'zato.service.get-list',
        'id_field': 'name',
        'label_fields': ['name'],
        'extra_params': {
            'paginate': False,
        },
        'filter_func': _service_filter,
    },

    'security': {
        'service_name': 'zato.security.get-list',
        'id_field': 'id',
        'id_format': '{sec_type}/{id}',
        'label_fields': ['sec_type', 'name'],
        'extra_params': {
            'paginate': False,
        },
        'filter_func': _default_filter,
    },

    'security_basic': {
        'service_name': 'zato.security.get-list',
        'id_field': 'id',
        'label_fields': ['name'],
        'extra_params': {
            'sec_type': ['apikey', 'basic_auth'],
            'paginate': False,
        },
        'filter_func': _default_filter,
    },

    'security_group': {
        'service_name': 'zato.groups.get-list',
        'id_field': 'id',
        'label_fields': ['name'],
        'extra_params': {'group_type': 'zato-api-creds'},
        'filter_func': None,
    },

    'rest_channel': {
        'service_name': 'zato.http-soap.get-list',
        'id_field': 'id',
        'label_fields': ['name'],
        'extra_params': {'connection': 'channel', 'transport': 'plain_http'},
        'filter_func': None,
    },

    'rest_outconn': {
        'service_name': 'zato.http-soap.get-list',
        'id_field': 'id',
        'label_fields': ['name'],
        'extra_params': {'connection': 'outgoing', 'transport': 'plain_http'},
        'filter_func': None,
    },
}

# ################################################################################################################################
# ################################################################################################################################

def _fetch_list(client, cluster_id, object_type):
    """ Fetches the current list of objects for a given type by invoking the appropriate Zato service.
    Returns a list of dicts, each containing at minimum the id_field and label_fields.
    """
    config = OBJECT_TYPE_CONFIG.get(object_type)
    if not config:
        logger.warning('live_form_updates._fetch_list: unknown object_type=%s', object_type)
        return []

    params = {'cluster_id': cluster_id}
    params.update(config.get('extra_params') or {})

    logger.info('live_form_updates._fetch_list: invoking %s with params=%s for object_type=%s',
        config['service_name'], params, object_type)

    try:
        response = client.invoke(config['service_name'], params)
    except Exception:
        logger.error('live_form_updates._fetch_list: error invoking %s: %s', config['service_name'], format_exc())
        return []

    filter_func = config.get('filter_func')
    id_field = config['id_field']
    label_fields = config['label_fields']

    logger.info('live_form_updates._fetch_list: got response for %s, has_data=%s, data_type=%s',
        object_type, hasattr(response, 'data'), type(getattr(response, 'data', None)).__name__)

    data = getattr(response, 'data', None)
    if not data:
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
        for field in label_fields:
            entry[field] = str(item.get(field, ''))

        # Include extra fields that the JS side may need
        for extra in ('id', 'name', 'sec_type', 'is_active'):
            val = item.get(extra)
            if val is not None and extra not in entry:
                entry[extra] = val

        # Derive sec_type_name from sec_type if available
        sec_type = item.get('sec_type')
        if sec_type and sec_type in SEC_DEF_TYPE_NAME:
            entry['sec_type_name'] = SEC_DEF_TYPE_NAME[sec_type]

        out.append(entry)

    logger.info('live_form_updates._fetch_list: object_type=%s, returned %d items, sample_ids=%s',
        object_type, len(out), [x['_id'] for x in out[:3]])

    return out

# ################################################################################################################################
# ################################################################################################################################

def _compute_diff(client_items_by_id, current_list, label_fields):
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

    # Items that exist in both but have different labels -> renamed
    for item_id, client_labels in client_items_by_id.items():
        if item_id in current_by_id:
            server_item = current_by_id[item_id]
            server_labels = {f: server_item.get(f, '') for f in label_fields}
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

def _parse_request_data(request_data):
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
def stream(req):
    """ SSE endpoint for live form updates.
    The client POSTs a JSON body describing what object types it cares about
    and what items it currently has. The server then streams diffs as SSE events.
    """
    stream_logger = getLogger('zato.live_form_updates')

    stream_logger.info('live_form_updates.stream: VIEW CALLED, client=%s, method=%s',
        req.META.get('REMOTE_ADDR'), req.method)

    try:
        body = req.body.decode('utf-8')
        stream_logger.info('live_form_updates.stream: request body length=%d', len(body))
        stream_logger.info('live_form_updates.stream: request body=%s', body[:500])
        request_data = loads(body)
    except Exception:
        stream_logger.error('live_form_updates.stream: failed to parse request body: %s', format_exc())
        return HttpResponseBadRequest('Invalid JSON body')

    initial_object_types = _parse_request_data(request_data)
    stream_logger.info('live_form_updates.stream: parsed %d object types: %s',
        len(initial_object_types), [ot for ot, _ in initial_object_types])

    if not initial_object_types:
        stream_logger.error('live_form_updates.stream: no valid object types, returning 400')
        return HttpResponseBadRequest('No valid object types provided')

    for ot, items in initial_object_types:
        stream_logger.info('live_form_updates.stream: object_type=%s, client_items_count=%d, sample_keys=%s',
            ot, len(items), list(items.keys())[:5])

    # Capture client and cluster_id before entering the generator,
    # as the request object may not be available after the view returns.
    zato_client = req.zato.client
    cluster_id = req.zato.cluster_id

    def event_stream():

        snapshots = {}
        for object_type, client_items in initial_object_types:
            snapshots[object_type] = client_items

        try:
            yield ': connected\n\n'
            stream_logger.info('live_form_updates.stream: sent connected comment, entering loop')

            iteration = 0

            while True:
                iteration += 1
                current_time = time.time()
                all_diffs = {}

                for object_type, _ in initial_object_types:
                    config = OBJECT_TYPE_CONFIG[object_type]
                    label_fields = config['label_fields']

                    current_list = _fetch_list(zato_client, cluster_id, object_type)

                    if iteration <= 3:
                        stream_logger.info('live_form_updates.stream: iter=%d, object_type=%s, server_items=%d, snapshot_items=%d',
                            iteration, object_type, len(current_list), len(snapshots[object_type]))

                    diff = _compute_diff(snapshots[object_type], current_list, label_fields)

                    has_changes = diff['created'] or diff['deleted'] or diff['renamed']

                    if has_changes:
                        stream_logger.info('live_form_updates.stream: iter=%d, DIFF for %s: created=%d, deleted=%d, renamed=%d',
                            iteration, object_type, len(diff['created']), len(diff['deleted']), len(diff['renamed']))
                        all_diffs[object_type] = diff

                        new_snapshot = {}
                        for item in current_list:
                            new_snapshot[item['_id']] = {f: item.get(f, '') for f in label_fields}
                        snapshots[object_type] = new_snapshot

                if all_diffs:
                    msg = dumps(all_diffs)
                    stream_logger.info('live_form_updates.stream: iter=%d, sending diff, length=%d', iteration, len(msg))
                    yield 'data: {}\n\n'.format(msg)
                else:
                    # Always yield a comment so Django detects broken pipe quickly
                    yield ': ping\n\n'

                time.sleep(1)

        except GeneratorExit:
            stream_logger.info('live_form_updates.stream: client disconnected (GeneratorExit)')
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            stream_logger.info('live_form_updates.stream: client disconnected (broken pipe)')
        except Exception:
            stream_logger.error('live_form_updates.stream: error in stream: %s', format_exc())

    response = StreamingHttpResponse(
        event_stream(), # type: ignore
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Content-Encoding'] = 'identity'

    stream_logger.info('live_form_updates.stream: returning StreamingHttpResponse')
    return response

# ################################################################################################################################
# ################################################################################################################################

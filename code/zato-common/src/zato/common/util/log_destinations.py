# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone
from json import dumps, loads
from logging import getLogger
from threading import RLock
from traceback import format_exc

# requests
from requests import post as requests_post

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist
    stranydict = stranydict
    strdictlist = strdictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    File_Name      = 'log-destinations.json'
    Vendor_Splunk  = 'splunk'
    Vendor_Datadog = 'datadog'
    Vendor_Grafana = 'grafana'
    Ping_Timeout   = 10
    Ping_Message   = 'Zato test event'

# ################################################################################################################################
# ################################################################################################################################

_vendors = [ModuleCtx.Vendor_Splunk, ModuleCtx.Vendor_Datadog, ModuleCtx.Vendor_Grafana]

# One lock guards all reads and writes of the destinations file in this process.
_lock = RLock()

# ################################################################################################################################
# ################################################################################################################################

def _get_store_path(repo_location:'str') -> 'str':
    out = os.path.join(repo_location, ModuleCtx.File_Name)
    return out

# ################################################################################################################################

def _load_store(repo_location:'str') -> 'stranydict':
    """ Reads the destinations file, returning an empty per-vendor layout if the file does not exist yet.
    """
    store_path = _get_store_path(repo_location)

    # Build the default layout first ..
    out:'stranydict' = {}
    for vendor in _vendors:
        out[vendor] = []

    # .. and overlay whatever is already stored on disk.
    if os.path.exists(store_path):
        with open(store_path, 'r', encoding='utf-8') as store_file:
            data = loads(store_file.read())
        for vendor in _vendors:
            if vendor in data:
                out[vendor] = data[vendor]

    return out

# ################################################################################################################################

def _save_store(repo_location:'str', store:'stranydict') -> 'None':
    store_path = _get_store_path(repo_location)
    data = dumps(store, indent=2)

    with open(store_path, 'w', encoding='utf-8') as store_file:
        _ = store_file.write(data)

# ################################################################################################################################
# ################################################################################################################################

def get_log_destinations(repo_location:'str') -> 'stranydict':
    """ Returns all the configured destinations, grouped by vendor.
    """
    with _lock:
        store = _load_store(repo_location)

    out = {'destinations': store}
    return out

# ################################################################################################################################

def set_log_destination(repo_location:'str', vendor:'str', destination:'stranydict') -> 'stranydict':
    """ Creates a new destination or updates an existing one, matched by its id.
    """
    with _lock:
        store = _load_store(repo_location)
        items:'strdictlist' = store[vendor]

        # An incoming id means an update of an existing destination ..
        if destination_id := destination.get('id'):

            for item_index, item in enumerate(items):
                if item['id'] == destination_id:
                    items[item_index] = destination
                    break

        # .. otherwise, it is a new destination and we assign the next id ourselves.
        else:
            max_id = 0
            for item in items:
                if item['id'] > max_id:
                    max_id = item['id']

            destination['id'] = max_id + 1
            items.append(destination)

        _save_store(repo_location, store)

    out = {'destinations': store}
    return out

# ################################################################################################################################

def delete_log_destination(repo_location:'str', vendor:'str', destination_id:'int') -> 'stranydict':
    """ Deletes a destination by its id.
    """
    with _lock:
        store = _load_store(repo_location)
        items:'strdictlist' = store[vendor]

        remaining:'strdictlist' = []
        for item in items:
            if item['id'] != destination_id:
                remaining.append(item)

        store[vendor] = remaining
        _save_store(repo_location, store)

    out = {'destinations': store}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_sample_event() -> 'stranydict':
    now = datetime.now(timezone.utc)

    out = {
        'source': 'zato',
        'event_type': 'ping',
        'message': ModuleCtx.Ping_Message,
        'event_time_iso': now.isoformat(),
    }
    return out

# ################################################################################################################################

def _ping_splunk(destination:'stranydict') -> 'None':
    """ Sends a sample event to a Splunk HEC endpoint.
    """
    event = _get_sample_event()

    payload:'stranydict' = {'event': event}

    # Both are optional in HEC, include them only if configured.
    if index := destination['index']:
        payload['index'] = index

    if sourcetype := destination['sourcetype']:
        payload['sourcetype'] = sourcetype

    headers = {'Authorization': 'Splunk ' + destination['token']}

    response = requests_post(destination['address'], json=payload, headers=headers, timeout=ModuleCtx.Ping_Timeout)
    if not response.ok:
        raise Exception(f'Splunk HEC returned {response.status_code}: {response.text}')

# ################################################################################################################################

def _ping_datadog(destination:'stranydict') -> 'None':
    """ Sends a sample event to the Datadog logs intake API.
    """
    event = _get_sample_event()

    entry:'stranydict' = {
        'ddsource': destination['source'],
        'service': destination['service'],
        'message': event['message'],
    }

    # Tags are optional, include them only if configured.
    if tags := destination['tags']:
        entry['ddtags'] = tags

    headers = {'DD-API-KEY': destination['api_key']}

    response = requests_post(destination['address'], json=[entry], headers=headers, timeout=ModuleCtx.Ping_Timeout)

    # Datadog replies with 202 Accepted on success.
    if not response.ok:
        raise Exception(f'Datadog intake returned {response.status_code}: {response.text}')

# ################################################################################################################################

def _ping_grafana(destination:'stranydict') -> 'None':
    """ Sends a sample event to a Grafana Loki push endpoint.
    """
    event = _get_sample_event()

    # Stream labels arrive as "name=value" pairs separated by commas ..
    labels:'stranydict' = {}
    for pair in destination['stream_labels'].split(','):
        pair = pair.strip()
        if pair:
            name, _, value = pair.partition('=')
            labels[name.strip()] = value.strip()

    # .. Loki timestamps are nanoseconds since the Unix epoch, as strings ..
    now = datetime.now(timezone.utc)
    timestamp_ns = int(now.timestamp() * 1_000_000_000)

    payload = {
        'streams': [{
            'stream': labels,
            'values': [[f'{timestamp_ns}', dumps(event)]],
        }]
    }

    headers:'stranydict' = {}

    # The tenant header is only needed with multi-tenant Loki.
    if tenant_id := destination['tenant_id']:
        headers['X-Scope-OrgID'] = tenant_id

    # Basic auth credentials are only needed with Grafana Cloud.
    auth = None
    if username := destination['username']:
        auth = (username, destination['api_token'])

    response = requests_post(
        destination['address'], json=payload, headers=headers, auth=auth, timeout=ModuleCtx.Ping_Timeout)

    # Loki replies with 204 No Content on success.
    if not response.ok:
        raise Exception(f'Loki push returned {response.status_code}: {response.text}')

# ################################################################################################################################
# ################################################################################################################################

_ping_by_vendor = {
    ModuleCtx.Vendor_Splunk:  _ping_splunk,
    ModuleCtx.Vendor_Datadog: _ping_datadog,
    ModuleCtx.Vendor_Grafana: _ping_grafana,
}

# ################################################################################################################################
# ################################################################################################################################

def ping_log_destination(repo_location:'str', vendor:'str', destination_id:'int') -> 'stranydict':
    """ Sends a sample event to the given destination and reports the result.
    """
    with _lock:
        store = _load_store(repo_location)

    items:'strdictlist' = store[vendor]

    for item in items:
        if item['id'] == destination_id:
            destination = item
            break
    else:
        out = {'success': False, 'details': f'Destination not found: {vendor} #{destination_id}'}
        return out

    ping_func = _ping_by_vendor[vendor]

    try:
        ping_func(destination)
    except Exception as e:
        logger.warning('Log destination ping error: %s', format_exc())
        out = {'success': False, 'details': str(e)}
    else:
        out = {'success': True, 'details': 'Test event sent OK'}

    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK
from uuid import uuid4

# Zato
from zato.common.test.fhir.common import bundle_request_types

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir.handler import FHIRRequestHandler
    from zato.common.typing_ import any_, dictlist, stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

def _rewrite_references(node:'any_', url_map:'strstrdict') -> 'None':
    """ Replaces every urn:uuid reference in a resource with the server location it now resides at.
    """
    if isinstance(node, dict):
        for key in node:
            value = node[key]

            if key == 'reference':
                if isinstance(value, str):
                    if value in url_map:
                        node[key] = url_map[value]
                        continue

            _rewrite_references(value, url_map)

    elif isinstance(node, list):
        for item in node:
            _rewrite_references(item, url_map)

# ################################################################################################################################

def _apply_bundle_entry(handler:'FHIRRequestHandler', entry:'stranydict') -> 'stranydict':
    """ Applies one bundle entry per its request method and returns its response entry.
    """
    request = entry['request']
    method = request['method']
    url = request['url']

    store = handler.server.store

    # A create stores the resource under the ID assigned during reference resolution ..
    if method == 'POST':
        resource = entry['resource']
        resource_type = resource['resourceType']
        resource_id = resource['id']

        _ = store.put(resource_type, resource_id, resource)

        meta = resource['meta']
        version_id = meta['versionId']
        location = f'{resource_type}/{resource_id}/_history/{version_id}'

        out = {'response': {'status': '201 Created', 'location': location}}
        return out

    # .. an update stores the resource under the ID its URL names ..
    if method == 'PUT':
        resource = entry['resource']
        resource_type, resource_id = url.split('/', 1)

        resource['id'] = resource_id
        was_created = store.put(resource_type, resource_id, resource)

        meta = resource['meta']
        version_id = meta['versionId']
        location = f'{resource_type}/{resource_id}/_history/{version_id}'

        if was_created:
            status = '201 Created'
        else:
            status = '200 OK'

        out = {'response': {'status': status, 'location': location}}
        return out

    # .. a delete removes what its URL names ..
    if method == 'DELETE':
        resource_type, resource_id = url.split('/', 1)
        _ = store.delete(resource_type, resource_id)

        out = {'response': {'status': '204 No Content'}}
        return out

    # .. a read returns what its URL names ..
    if method == 'GET':
        resource_type, resource_id = url.split('/', 1)
        result = store.read(resource_type, resource_id)

        if result.resource is None:
            out = {'response': {'status': '404 Not Found'}}
        else:
            out = {'response': {'status': '200 OK'}, 'resource': result.resource}

        return out

    # .. and anything else is not a method bundles may carry.
    out = {'response': {'status': '400 Bad Request'}}
    return out

# ################################################################################################################################

def handle_bundle(handler:'FHIRRequestHandler') -> 'None':
    """ Handles the transaction and batch interactions - a Bundle posted to the base URL.
    Each entry is processed per its request method and urn:uuid fullUrl references
    resolve to the IDs the server assigns, across all the entries.
    """
    bundle = handler.read_body()
    if bundle is None:
        return

    # Only bundles belong at the base URL ..
    body_type = bundle.get('resourceType')
    if body_type != 'Bundle':
        handler.send_outcome(BAD_REQUEST, 'invalid', f'Expected a Bundle at the base URL, not `{body_type}`')
        return

    # .. and only the transaction and batch kinds.
    bundle_type = bundle.get('type')
    if bundle_type not in bundle_request_types:
        diagnostics = f'Expected a transaction or batch Bundle, not `{bundle_type}`'
        handler.send_outcome(BAD_REQUEST, 'invalid', diagnostics)
        return

    entries = bundle.get('entry')
    if entries is None:
        entries = []

    # First pass - assign a server ID to every resource created by the bundle,
    # so that urn:uuid references can point at the right location before anything is stored.
    url_map:'strstrdict' = {}

    for entry in entries:
        request = entry.get('request')
        if not request:
            diagnostics = 'Each entry of a transaction or batch needs a request'
            handler.send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        if request['method'] == 'POST':
            resource = entry['resource']
            resource_type = resource['resourceType']

            resource_id = uuid4().hex
            resource['id'] = resource_id

            full_url = entry.get('fullUrl')
            if full_url:
                if full_url.startswith('urn:uuid:'):
                    url_map[full_url] = f'{resource_type}/{resource_id}'

    # Second pass - resolve the references now that all the IDs are known ..
    for entry in entries:
        if 'resource' in entry:
            _rewrite_references(entry['resource'], url_map)

    # .. third pass - apply each entry and collect its response.
    response_entries:'dictlist' = []

    for entry in entries:
        response_entry = _apply_bundle_entry(handler, entry)
        response_entries.append(response_entry)

    response = {
        'resourceType': 'Bundle',
        'id': uuid4().hex,
        'type': bundle_request_types[bundle_type],
        'entry': response_entries,
    }

    handler.send_json(OK, response)

# ################################################################################################################################
# ################################################################################################################################

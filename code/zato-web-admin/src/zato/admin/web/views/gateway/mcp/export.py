# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from urllib.parse import urlsplit

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.gateway.mcp.common import _default_server_address, _export_schema_url, _export_version, \
    _sec_type_to_export_header, _slug_invalid_characters
from zato.admin.web.views.gateway.mcp_tool_sources import Connection_Source_List
from zato.common.api import Groups, MCP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def export(req:'any_', id:'str') -> 'HttpResponse':
    """ Exports an MCP gateway as a server.json-format document that the browser downloads.
    """

    # Look up the gateway by its ID ..
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})
    gateway = response.data

    gateway_name = gateway['name']
    url_path = gateway['url_path']

    # .. resolve the externally visible base address ..
    if base_address := os.environ.get('Zato_Server_Address'):
        pass
    else:
        base_address = _default_server_address

    # .. the name's namespace is the host part of that address ..
    netloc = urlsplit(base_address).netloc
    host_parts = netloc.split(':')
    host = host_parts[0]

    # .. reversing labels only makes sense for DNS names, never for IP addresses ..
    labels = host.split('.')

    is_ip_address = True
    for label in labels:
        if not label.isdigit():
            is_ip_address = False
            break

    if not is_ip_address:
        labels.reverse()

    namespace = '.'.join(labels)

    # .. the server part of the name is a slug of the gateway name ..
    slug = gateway_name.lower()
    slug = _slug_invalid_characters.sub('-', slug)

    # .. collect authentication headers from the gateway's security group members,
    # along with the names and types of the definitions themselves - never any secrets ..
    headers = []
    header_names = set()
    security_list = []

    if security_groups := gateway.get('security_groups'):
        group_id = security_groups[0]
        member_response = req.zato.client.invoke('zato.groups.get-member-list', {
            'group_type': Groups.Type.API_Clients,
            'group_id': group_id,
        })

        # .. each security type maps to one header, emitted once no matter how many members use it ..
        for member in member_response.data:
            header = _sec_type_to_export_header[member['sec_type']]
            if header['name'] not in header_names:
                header_names.add(header['name'])
                headers.append(header)

            security_list.append({
                'name': member['name'],
                'type': member['sec_type'],
            })

    # .. the tools the gateway exposes, each with its description and both schemas,
    # built server-side the same way the runtime tools/list builds them -
    # the request carries the services and every connection allow list the gateway has ..
    services = gateway.get('services') or []
    tool_list_request = {'services': services}

    for source in Connection_Source_List:

        if (allow_list := gateway.get(source.config_key)) is None:
            allow_list = []

        tool_list_request[source.config_key] = allow_list

    tool_response = req.zato.client.invoke('zato.gateway.mcp.get-tool-list', tool_list_request)
    tools = tool_response.data

    # .. build the remote endpoint description, naming the protocol revisions the gateway speaks ..
    remote = {
        'type': 'streamable-http',
        'url': base_address + url_path,
        'protocolVersions': MCP.Protocol_Versions_Supported,
    }

    if headers:
        remote['headers'] = headers

    # .. assemble the full document - server.json has no top-level place for tools
    # or security definitions, so the full details live under _meta, its extension point ..
    document = {
        '$schema': _export_schema_url,
        'name': f'{namespace}/{slug}',
        'description': f'MCP gateway {gateway_name}',
        'version': _export_version,
        'remotes': [remote],
        '_meta': {
            'zato': {
                'tools': tools,
                'security': security_list,
            },
        },
    }

    # .. and return it as a file download.
    file_name = f'mcp-{slug}.json'
    out = dumps(document, indent=2)

    http_response = HttpResponse(out, content_type='application/json') # type: ignore
    http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return http_response

# ################################################################################################################################
# ################################################################################################################################

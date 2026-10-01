# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from urllib.parse import urlsplit

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.gateway.mcp.common import _export_schema_url, _export_version, \
    _sec_type_to_export_header, _slug_invalid_characters
from zato.admin.web.views.gateway.mcp_tool_sources import Connection_Source_List
from zato.common.api import Groups, MCP, SEC_DEF_TYPE
from zato.common.util.mcp_oauth import get_metadata_url, get_server_address, parse_scopes

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
    is_oauth = bool(gateway.get('oauth'))

    # .. resolve the externally visible base address ..
    base_address = get_server_address()

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

        # .. each security type maps to one header, emitted once no matter how many members use it,
        # except that on a gateway with OAuth on a bearer definition is what the OAuth block describes ..
        for member in member_response.data:
            sec_type = member['sec_type']

            security_list.append({
                'name': member['name'],
                'type': sec_type,
            })

            if sec_type not in _sec_type_to_export_header:
                continue

            if is_oauth:
                if sec_type == SEC_DEF_TYPE.OAUTH:
                    continue

            header = _sec_type_to_export_header[sec_type]
            if header['name'] not in header_names:
                header_names.add(header['name'])
                headers.append(header)

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
    zato_meta = {
        'tools': tools,
        'security': security_list,
    }

    # .. a gateway with OAuth on says so, with its scopes and where its metadata is ..
    if is_oauth:
        zato_meta['oauth'] = {
            'scopes': parse_scopes(gateway.get('oauth_scopes') or ''),
            'resource_metadata': get_metadata_url(base_address, url_path),
        }

    document = {
        '$schema': _export_schema_url,
        'name': f'{namespace}/{slug}',
        'description': f'MCP gateway {gateway_name}',
        'version': _export_version,
        'remotes': [remote],
        '_meta': {
            'zato': zato_meta,
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

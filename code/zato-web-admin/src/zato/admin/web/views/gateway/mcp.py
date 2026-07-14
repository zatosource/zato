# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import re
from json import dumps
from urllib.parse import urlsplit

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.forms.gateway.mcp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import API_Key, GENERIC, Groups, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME
from zato.common.defaults import http_plain_server_port
from zato.common.util.tcp import get_current_ip

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_service_input_prefix = 'mcp_service_'
_security_input_prefix = 'mcp_security_'
_mcp_group_name_prefix = 'mcp.'

# The JSON Schema that exported MCP gateway documents conform to
_export_schema_url = 'https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json'

# The version of the exported document
_export_version = '1.0.0'

# Used when the server address is not configured through the environment
_default_server_address = f'http://{get_current_ip()}:{http_plain_server_port}'

# Characters that cannot appear in the exported document's name
_slug_invalid_characters = re.compile('[^a-z0-9._-]+')

# The API key header may be redefined through the environment
if _api_key_header := os.environ.get(API_Key.Env_Key):
    pass
else:
    _api_key_header = API_Key.Default_Header

# Maps security definition types to the HTTP headers MCP clients need to send
_sec_type_to_export_header = {
    SEC_DEF_TYPE.APIKEY: {
        'name': _api_key_header,
        'description': 'API key',
        'isRequired': True,
        'isSecret': True,
    },
    SEC_DEF_TYPE.BASIC_AUTH: {
        'name': 'Authorization',
        'description': 'Basic Auth credentials',
        'isRequired': True,
        'isSecret': True,
    },
}

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'gateway-mcp'
    template = 'zato/gateway/mcp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active'
    output_optional = 'url_path', 'services', 'security_groups'
    output_repeated = True

    def get_initial_input(self) -> 'strdict':

        # The type is constant for this page so it is not expected in the URL,
        # it is always added to the service request here instead.
        return {'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP}

    def on_before_append_item(self, item:'any_') -> 'any_':

        # Resolve the security member count from the auto-created group ..
        security_groups = getattr(item, 'security_groups', None) or []
        if security_groups:
            group_id = security_groups[0]
            member_response = self.req.zato.client.invoke('zato.groups.get-member-list', {
                'group_type': Groups.Type.API_Clients,
                'group_id': group_id,
            })
            item.security_member_count = len(member_response.data) if member_response.ok and member_response.data else 0
        else:
            item.security_member_count = 0

        return item

    def handle(self) -> 'strdict':
        out = {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name',
    input_optional = 'is_active', 'url_path'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict:'strdict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def pre_process_input_dict(self, input_dict:'strdict') -> 'None':

        # Collect services from the badge picker hidden inputs ..
        service_keys = [key for key in self.req.POST if key.startswith(_service_input_prefix)]
        service_names = [self.req.POST[key] for key in service_keys]

        # .. and store them so they end up in opaque data.
        input_dict['services'] = service_names

        # Collect security definitions from the security badge picker ..
        security_keys = [key for key in self.req.POST if key.startswith(_security_input_prefix)]
        member_id_list = [self.req.POST[key] for key in security_keys]

        # .. the group name is derived from the gateway name ..
        gateway_name = input_dict['name']
        group_name = _mcp_group_name_prefix + gateway_name

        # .. auto-create or update the security group with the picked members ..
        existing_groups = self.req.zato.client.invoke('zato.groups.get-list', {
            'group_type': Groups.Type.API_Clients,
        })

        group_id = None
        for group in existing_groups.data:
            if group['name'] == group_name:
                group_id = group['id']
                break

        if group_id:
            # .. update the existing group with the new member list ..
            self.req.zato.client.invoke('zato.groups.edit', {
                'id': group_id,
                'group_type': Groups.Type.API_Clients,
                'name': group_name,
                'member_id_list': member_id_list,
            })
        else:
            # .. or create a new group if one does not exist yet ..
            response = self.req.zato.client.invoke('zato.groups.create', {
                'group_type': Groups.Type.API_Clients,
                'name': group_name,
                'member_id_list': member_id_list,
            })
            group_id = response.data['id']

        # .. store the group ID so the hook can assign it to the HTTPSOAP channel.
        input_dict['security_groups'] = [group_id]

    def post_process_return_data(self, return_data:'strdict') -> 'strdict':

        # Count the services that were submitted ..
        service_keys = [key for key in self.req.POST if key.startswith(_service_input_prefix)]

        # .. and count the security definitions ..
        security_keys = [key for key in self.req.POST if key.startswith(_security_input_prefix)]

        # .. attach both counts for the JS data table to display.
        return_data['service_count'] = len(service_keys)
        return_data['security_count'] = len(security_keys)

        out = return_data
        return out

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully {} MCP gateway `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'gateway-mcp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'gateway-mcp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'gateway-mcp-delete'
    error_message = 'Could not delete MCP gateway'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of all non-internal services for the badge picker.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. get all deployed services ..
    response = req.zato.client.invoke('zato.service.get-list', {
        'cluster_id': req.zato.cluster_id,
        'name_filter': '*',
        'paginate': False,
    })

    # .. build the current assigned set if editing ..
    assigned_names:'set[str]' = set()
    if gateway_id:
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'id': gateway_id,
            'paginate': False,
        })
        logger.info('MCP get_service_list: gateway_id=%s, response.ok=%s, data_count=%s',
            gateway_id, gateway_response.ok, len(gateway_response.data) if gateway_response.data else 0)

        if gateway_response.ok and gateway_response.data:
            for gateway_item in gateway_response.data:
                item_id = gateway_item['id']
                item_services = gateway_item.get('services')
                logger.info('MCP get_service_list: item id=%s (%s) vs gateway_id=%s (%s), services=%s',
                    item_id, type(item_id).__name__, gateway_id, type(gateway_id).__name__, item_services)
                if str(item_id) == str(gateway_id):
                    assigned_names = set(item_services or [])
                    logger.info('MCP get_service_list: matched, assigned_names=%s', assigned_names)
                    break
        else:
            logger.info('MCP get_service_list: no data or not ok')

    logger.info('MCP get_service_list: final assigned_names=%s', assigned_names)

    # .. build the output list, skipping internal services ..
    items = []
    for service in response.data:
        name = service['name']

        if name.startswith('zato.') or name.startswith('pub.zato.'):
            continue

        items.append({
            'id': name,
            'name': name,
            'is_member': name in assigned_names,
        })

    # .. sort alphabetically ..
    items.sort(key=lambda item: item['name'])

    # .. and return the JSON response.
    out = dumps(items)
    return HttpResponse(out, content_type='application/json') # type: ignore

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_security_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of available security definitions (API key, Basic Auth)
    for the security badge picker, with is_member flags set based on the gateway's
    auto-created security group.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. get all available security definitions of the supported types ..
    response = req.zato.client.invoke('zato.security.get-list', {
        'sec_type': ['apikey', 'basic_auth'],
        'paginate': False,
    })

    # .. extract the items, skipping built-in and internal entries ..
    items = []
    for item in response.data:
        name = item['name']
        if name in {'ide_publisher', 'pubapi'} or 'zato.' in name:
            continue

        sec_type = item['sec_type']
        sec_type_name = SEC_DEF_TYPE_NAME[sec_type] # type: ignore
        items.append({
            'id': item['id'],
            'name': name,
            'sec_type': sec_type,
            'sec_type_name': sec_type_name,
            'is_member': False,
        })

    # .. sort by type then name ..
    items.sort(key=lambda elem: (elem['sec_type'], elem['name']))

    # .. if editing, figure out which definitions are already assigned ..
    if gateway_id:

        logger.info('MCP get_security_list: gateway_id=%s', gateway_id)

        # .. look up the gateway's security_groups field ..
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'paginate': False,
        })

        logger.info('MCP get_security_list: gateway_response.ok=%s, data_count=%s',
            gateway_response.ok, len(gateway_response.data) if gateway_response.data else 0)

        if gateway_response.ok and gateway_response.data:
            for gateway_item in gateway_response.data:
                item_id = gateway_item['id']
                logger.info('MCP get_security_list: item id=%s (%s) vs gateway_id=%s (%s), keys=%s',
                    item_id, type(item_id).__name__, gateway_id, type(gateway_id).__name__,
                    list(gateway_item.keys()))

                if str(item_id) == str(gateway_id):
                    security_groups = gateway_item.get('security_groups', [])
                    logger.info('MCP get_security_list: matched, security_groups=%s', security_groups)

                    if security_groups:
                        group_id = security_groups[0]
                        logger.info('MCP get_security_list: fetching members for group_id=%s', group_id)

                        member_response = req.zato.client.invoke('zato.groups.get-member-list', {
                            'group_type': Groups.Type.API_Clients,
                            'group_id': group_id,
                        })

                        logger.info('MCP get_security_list: member_response.ok=%s, data=%s',
                            member_response.ok, member_response.data)

                        if member_response.ok and member_response.data:
                            member_security_ids = {m['security_id'] for m in member_response.data}
                            logger.info('MCP get_security_list: member_security_ids=%s', member_security_ids)
                            for item in items:
                                if item['id'] in member_security_ids:
                                    item['is_member'] = True
                                    logger.info('MCP get_security_list: marked as assigned: id=%s name=%s', item['id'], item['name'])
                    break

    logger.info('MCP get_security_list: returning %d items, %d assigned',
        len(items), sum(1 for item in items if item['is_member']))

    # .. and return the JSON response.
    out = dumps(items)
    return HttpResponse(out, content_type='application/json') # type: ignore

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

    # .. collect authentication headers from the gateway's security group members ..
    headers = []
    header_names = set()

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

    # .. build the remote endpoint description ..
    remote = {
        'type': 'streamable-http',
        'url': base_address + url_path,
    }

    if headers:
        remote['headers'] = headers

    # .. assemble the full document ..
    document = {
        '$schema': _export_schema_url,
        'name': f'{namespace}/{slug}',
        'description': f'MCP gateway {gateway_name}',
        'version': _export_version,
        'remotes': [remote],
    }

    # .. and return it as a file download.
    file_name = f'mcp-{slug}.json'
    out = dumps(document, indent=2)

    http_response = HttpResponse(out, content_type='application/json') # type: ignore
    http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return http_response

# ################################################################################################################################
# ################################################################################################################################

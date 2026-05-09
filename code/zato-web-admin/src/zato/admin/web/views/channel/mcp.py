# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.forms.channel.mcp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import GENERIC, Groups, SEC_DEF_TYPE_NAME

# Bunch
from bunch import Bunch

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
_mcp_path_prefix = '/mcp/'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-mcp'
    template = 'zato/channel/mcp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = 'url_path', 'services', 'security_groups'
    output_repeated = True

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
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'mcp_path_prefix': _mcp_path_prefix,
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
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_MCP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def pre_process_input_dict(self, input_dict:'strdict') -> 'None':

        # Collect services from the badge picker hidden inputs ..
        service_keys = [key for key in self.req.POST if key.startswith(_service_input_prefix)]
        service_names = [self.req.POST[key] for key in service_keys]

        # .. and store them so they end up in opaque data.
        input_dict['services'] = service_names

        # .. prepend the mandatory /mcp/ prefix to the user-supplied suffix ..
        url_path = input_dict.get('url_path', '')
        input_dict['url_path'] = _mcp_path_prefix + url_path.lstrip('/')

        # Collect security definitions from the security badge picker ..
        security_keys = [key for key in self.req.POST if key.startswith(_security_input_prefix)]
        member_id_list = [self.req.POST[key] for key in security_keys]

        # .. the group name is derived from the channel name ..
        channel_name = input_dict['name']
        group_name = _mcp_group_name_prefix + channel_name

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
        return 'Successfully {} MCP channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-mcp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-mcp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-mcp-delete'
    error_message = 'Could not delete MCP channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of all non-internal services for the badge picker.
    """

    # The channel ID is provided when editing an existing channel ..
    channel_id = req.GET.get('channel_id')

    # .. get all deployed services ..
    response = req.zato.client.invoke('zato.service.get-list', {
        'cluster_id': req.zato.cluster_id,
        'name_filter': '*',
        'paginate': False,
    })

    # .. build the current assigned set if editing ..
    assigned_names:'set[str]' = set()
    if channel_id:
        channel_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
            'id': channel_id,
            'paginate': False,
        })
        logger.info('MCP get_service_list: channel_id=%s, response.ok=%s, data_count=%s',
            channel_id, channel_response.ok, len(channel_response.data) if channel_response.data else 0)

        if channel_response.ok and channel_response.data:
            for channel_item in channel_response.data:
                item_id = channel_item['id']
                item_services = channel_item.get('services')
                logger.info('MCP get_service_list: item id=%s (%s) vs channel_id=%s (%s), services=%s',
                    item_id, type(item_id).__name__, channel_id, type(channel_id).__name__, item_services)
                if str(item_id) == str(channel_id):
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
    for the security badge picker, with is_member flags set based on the channel's
    auto-created security group.
    """

    # The channel ID is provided when editing an existing channel ..
    channel_id = req.GET.get('channel_id')

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
    if channel_id:

        logger.info('MCP get_security_list: channel_id=%s', channel_id)

        # .. look up the channel's security_groups field ..
        channel_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
            'paginate': False,
        })

        logger.info('MCP get_security_list: channel_response.ok=%s, data_count=%s',
            channel_response.ok, len(channel_response.data) if channel_response.data else 0)

        if channel_response.ok and channel_response.data:
            for channel_item in channel_response.data:
                item_id = channel_item['id']
                logger.info('MCP get_security_list: item id=%s (%s) vs channel_id=%s (%s), keys=%s',
                    item_id, type(item_id).__name__, channel_id, type(channel_id).__name__,
                    list(channel_item.keys()))

                if str(item_id) == str(channel_id):
                    security_groups = channel_item.get('security_groups', [])
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

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import re
from json import dumps, loads
from urllib.parse import urlsplit

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.gateway.mcp import CreateForm, EditForm
from zato.admin.web.util import get_server_directory
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import API_Key, GENERIC, Groups, MCP, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME
from zato.common.defaults import http_plain_server_port
from zato.common.skills.api import get_skill_name_list
from zato.common.util.api import asbool
from zato.common.util.safeguards.common import Mode_Clean, SafeguardConfig, Url_Mode_Remove
from zato.common.util.tcp import get_current_ip
from zato.common.util.truncate.tokens import Default_Characters_Per_Token, Size_Cap_Mode_Truncate

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strdictlist, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_service_input_prefix = 'mcp_service_'
_security_input_prefix = 'mcp_security_'
_skill_input_prefix = 'mcp_skill_'
_mcp_group_name_prefix = 'mcp.'

# The multi-step wizard template, serving both the create and the edit page.
_wizard_template = 'zato/gateway/mcp-wizard.html'

# What the fields the gateway list's size caps popover reads and writes are named after.
_row_edit_prefix = 'mcp-row'

# The two flags a row of the gateway list turns over where it stands.
_inline_flag_names = ['is_active', 'allow_agent_filters']

# The two lines a row edits in a small form of their own.
_inline_text_names = ['name', 'url_path']

# Everything the size caps popover holds, edited on the list without the wizard being opened.
_inline_size_cap_names = ['max_response_size', 'min_size_threshold', 'characters_per_token', 'size_cap_mode']

# Everything a row of the gateway list may change without the wizard being opened -
# the services and the security members travel separately, each as one JSON list.
_inline_field_names = _inline_flag_names + _inline_text_names + _inline_size_cap_names

# What the list's size caps cell says of a gateway that caps nothing.
_no_size_cap_label = 'No cap'

# Checkboxes persisted in the gateway's opaque configuration - absent from POST means unchecked, i.e. False.
_shaping_checkbox_fields = (
    'validate_input',
    'is_audit_log_active',
    'allow_agent_filters',
    'safeguards_strip_nulls',
    'safeguards_collapse_whitespace',
    'safeguards_strip_base64',
    'safeguards_pii_enabled',
    'safeguards_pii_validate',
    'safeguards_pii_stable_replacements',
    'safeguards_secrets_enabled',
    'safeguards_normalize_unicode',
    'safeguards_sanitize_markup',
    'safeguards_url_policy_enabled',
)

# Response shaping integer fields - an empty input means zero, which disables the cap or the threshold.
_shaping_int_fields = (
    'max_response_size',
    'min_size_threshold',
)

# Response shaping multi-selects - always stored as lists of detector or land names.
_shaping_list_fields = (
    'safeguards_pii_lands',
    'safeguards_pii_detectors',
    'safeguards_pii_exclude',
)

# Response shaping selects - these always carry a value while their stage is enabled.
_shaping_choice_fields = (
    'size_cap_mode',
    'safeguards_unicode_mode',
    'safeguards_markup_mode',
    'safeguards_url_mode',
)

# The documented default of each select - a disabled stage keeps its select
# out of the POST and the default is what gets stored then.
_choice_field_defaults = {
    'size_cap_mode':           Size_Cap_Mode_Truncate,
    'safeguards_unicode_mode': Mode_Clean,
    'safeguards_markup_mode':  Mode_Clean,
    'safeguards_url_mode':     Url_Mode_Remove,
}

# All the response shaping fields the dashboard persists in the gateway's opaque configuration.
_shaping_fields = _shaping_checkbox_fields + _shaping_int_fields + _shaping_list_fields + _shaping_choice_fields + \
    ('characters_per_token', 'safeguards_url_allow_list')

# What each response shaping field renders as in the data table when a gateway's config predates it
# or when a falsy value was filtered out on the way from the backend.
_shaping_display_defaults = {
    'validate_input':                      False,
    'is_audit_log_active':                 False,
    'allow_agent_filters':                 False,
    'safeguards_strip_nulls':              False,
    'safeguards_collapse_whitespace':      False,
    'safeguards_strip_base64':             False,
    'safeguards_pii_enabled':              False,
    'safeguards_pii_validate':             False,
    'safeguards_pii_stable_replacements':  False,
    'safeguards_secrets_enabled':          False,
    'safeguards_normalize_unicode':        False,
    'safeguards_sanitize_markup':          False,
    'safeguards_url_policy_enabled':       False,
    'max_response_size':                   '',
    'min_size_threshold':                  '',
    'characters_per_token':                Default_Characters_Per_Token,
    'size_cap_mode':                       Size_Cap_Mode_Truncate,
    'safeguards_pii_lands':                '',
    'safeguards_pii_detectors':            '',
    'safeguards_pii_exclude':              '',
    'safeguards_unicode_mode':             Mode_Clean,
    'safeguards_markup_mode':              Mode_Clean,
    'safeguards_url_allow_list':           '',
    'safeguards_url_mode':                 Url_Mode_Remove,
}

# The server's simple-type parser turns 0 and 1 into booleans on their way into the opaque
# storage, so these numeric fields may come back as bools and have to be read as numbers again.
_numeric_shaping_fields = _shaping_int_fields + ('characters_per_token',)

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

def numeric_from_bool(value:'any_') -> 'any_':
    """ The opaque storage stores 0 as False and 1 as True, so a numeric field read back
    from it turns these two values into numbers again - False means no value at all.
    """
    if value is False:
        out = ''
    elif value is True:
        out = 1
    else:
        out = value

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_size_cap_label(max_response_size:'any_', size_cap_mode:'str') -> 'str':
    """ Says in one line what the list's size caps cell shows - how many tokens a response
    may carry and what happens over the cap, or that nothing is capped at all.
    """
    if not max_response_size:
        return _no_size_cap_label

    amount = int(max_response_size)

    out = f'{amount:,} tokens, {size_cap_mode}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def save_security_group(req:'any_', gateway_name:'str', member_id_list:'list') -> 'int':
    """ Wraps the security definitions picked for a gateway in one group of the gateway's
    own, named after it, creating or updating the group, and returns the group's id.
    """
    group_name = _mcp_group_name_prefix + gateway_name

    # A gateway saved before already has a group of that name, so the picks carried
    # now replace the ones the group was left with the last time around ..
    existing_groups = req.zato.client.invoke('zato.groups.get-list', {
        'group_type': Groups.Type.API_Clients,
    })

    group_id = None
    for group in existing_groups.data:
        if group['name'] == group_name:
            group_id = group['id']
            break

    if group_id:
        # .. update the existing group with the new member list ..
        req.zato.client.invoke('zato.groups.edit', {
            'id': group_id,
            'group_type': Groups.Type.API_Clients,
            'name': group_name,
            'member_id_list': member_id_list,
        })
    else:
        # .. or create a new group if one does not exist yet.
        response = req.zato.client.invoke('zato.groups.create', {
            'group_type': Groups.Type.API_Clients,
            'name': group_name,
            'member_id_list': member_id_list,
        })
        group_id = response.data['id']

    out = group_id
    return out

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
    output_optional = ('url_path', 'services', 'security_groups') + _shaping_fields
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

        # Response shaping fields absent from the item - because the gateway predates them
        # or because a falsy value was filtered out on the way - render as their defaults,
        # so the data table's hidden columns always carry definite values for the edit form.
        for name, default_value in _shaping_display_defaults.items():
            if not hasattr(item, name):
                setattr(item, name, default_value)

        # The numeric fields the opaque storage stored as booleans are numbers again
        # before the hidden columns are rendered.
        for name in _numeric_shaping_fields:
            value = getattr(item, name)
            value = numeric_from_bool(value)
            setattr(item, name, value)

        # What the size caps cell of this row says before it is clicked
        item.size_cap_label = get_size_cap_label(item.max_response_size, item.size_cap_mode)

        return item

    def handle(self) -> 'strdict':

        # Creating and editing happen in the wizard on its own page, so the list renders
        # no dialog - the row form is what the size caps popover edits a row through.
        out = {
            'show_search_form': True,
            'row_form': CreateForm(prefix=_row_edit_prefix),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name',
    input_optional = ('is_active', 'url_path') + _shaping_fields
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict:'strdict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def pre_process_input_dict(self, input_dict:'strdict') -> 'None':

        # Checkboxes arrive as 'on' when ticked and are absent from POST otherwise, except that
        # names with a boolean prefix, e.g. is_audit_log_active, were already turned
        # into a bool by set_input upstream ..
        for name in _shaping_checkbox_fields:
            value = input_dict[name]
            input_dict[name] = value is True or value == 'on'

        # .. a select of a disabled stage is excluded from the POST altogether,
        # so an absent value means the stage's documented default ..
        for name in _shaping_choice_fields:
            if not input_dict[name]:
                input_dict[name] = _choice_field_defaults[name]

        # .. the PII validate checkbox is only ever absent along with its whole
        # stage, in which case its documented default holds too ..
        if not input_dict['safeguards_pii_enabled']:
            input_dict['safeguards_pii_validate'] = SafeguardConfig.pii_validate

        # .. integer fields arrive as strings and an empty input means zero ..
        for name in _shaping_int_fields:
            if value := input_dict[name]:
                input_dict[name] = int(value)
            else:
                input_dict[name] = 0

        # .. the characters-per-token ratio is a float with a well-known default ..
        if value := input_dict['characters_per_token']:
            input_dict['characters_per_token'] = float(value)
        else:
            input_dict['characters_per_token'] = Default_Characters_Per_Token

        # .. multi-selects arrive as a plain string when only one option is picked
        # and are absent when nothing is - both normalize to a list ..
        for name in _shaping_list_fields:
            value = input_dict[name]
            if not value:
                input_dict[name] = []
            elif isinstance(value, str):
                input_dict[name] = [value]

        # .. the URL allow list is a comma-separated string of host suffixes ..
        hosts = []
        if value := input_dict['safeguards_url_allow_list']:
            for host in value.split(','):
                host = host.strip()
                if host:
                    hosts.append(host)
        input_dict['safeguards_url_allow_list'] = hosts

        # Collect services from the badge picker hidden inputs ..
        service_keys = [key for key in self.req.POST if key.startswith(_service_input_prefix)]
        service_names = [self.req.POST[key] for key in service_keys]

        # .. and store them so they end up in opaque data.
        input_dict['services'] = service_names

        # Collect the skills the gateway serves as MCP prompts ..
        skill_names:'strlist' = []

        for key in self.req.POST:
            if key.startswith(_skill_input_prefix):
                skill_names.append(self.req.POST[key])

        # .. and store them so they end up in opaque data too.
        input_dict['skills'] = skill_names

        # Collect security definitions from the security badge picker ..
        security_keys = [key for key in self.req.POST if key.startswith(_security_input_prefix)]
        member_id_list = [self.req.POST[key] for key in security_keys]

        # .. auto-create or update the gateway's own security group with the picked members
        # and store the group ID so the hook can assign it to the HTTPSOAP channel.
        group_id = save_security_group(self.req, input_dict['name'], member_id_list)
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
    items:'strdictlist' = []
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
    items:'strdictlist' = []
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

@method_allowed('POST')
def get_skill_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of user skills for the skills badge picker, with is_member
    flags set based on the gateway's allow list.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. skills live on disk under the server's config/repo directory ..
    server_directory = get_server_directory()
    repo_location = os.path.join(server_directory, 'config', 'repo')
    skill_names = get_skill_name_list(repo_location)

    # .. build the current allow list if editing ..
    assigned_names:'strset' = set()
    if gateway_id:
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'paginate': False,
        })

        if gateway_response.ok:
            if gateway_response.data:
                for gateway_item in gateway_response.data:
                    if str(gateway_item['id']) == gateway_id:

                        # A gateway saved without the key serves no skills
                        gateway_skills = gateway_item.get('skills')
                        if gateway_skills is None:
                            gateway_skills = []

                        assigned_names = set(gateway_skills)
                        break

    # .. each skill directory is one badge ..
    items:'strdictlist' = []
    for name in skill_names:
        items.append({
            'id': name,
            'name': name,
            'is_member': name in assigned_names,
        })

    # .. and return the JSON response.
    serialized = dumps(items)
    payload = serialized.encode('utf-8')

    out = HttpResponse(payload, content_type='application/json')
    return out

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
    # built server-side the same way the runtime tools/list builds them ..
    services = gateway.get('services') or []
    tool_response = req.zato.client.invoke('zato.gateway.mcp.get-tool-list', {'services': services})
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

@method_allowed('GET')
def wizard_create(req:'any_') -> 'TemplateResponse':
    """ A multi-step wizard for a new MCP gateway.
    """
    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': CreateForm(),
        'is_edit': False,
        'item_id': '',
    }

    out = TemplateResponse(req, _wizard_template, return_data)
    return out

# ################################################################################################################################

def _read_gateway(req:'any_', id:'str') -> 'strdict':
    """ One gateway as it currently stands, every response shaping field it predates
    filled in with its default.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'MCP gateway with id `{id}` could not be read')

    item_dict = response.data

    # A gateway stored before a field existed says nothing about it, so what the pages
    # open on is the very default a new gateway would be created with
    for name, default_value in _shaping_display_defaults.items():
        if name not in item_dict:
            item_dict[name] = default_value

    # The numeric fields the opaque storage stored as booleans are numbers again
    # before the edit form is prefilled with them.
    for name in _numeric_shaping_fields:
        item_dict[name] = numeric_from_bool(item_dict[name])

    return item_dict

# ################################################################################################################################

@method_allowed('GET')
def wizard_edit(req:'any_', id:'str') -> 'TemplateResponse':
    """ The same wizard, opened on one existing MCP gateway.
    """
    item_dict = _read_gateway(req, id)

    # The URL allow list is stored as a list of host suffixes and edited as one comma-separated line
    allow_list = item_dict['safeguards_url_allow_list']
    if isinstance(allow_list, list):
        item_dict['safeguards_url_allow_list'] = ', '.join(allow_list)

    # The edit endpoint reads its input under the edit- prefix, which is what the form
    # is built with and what the wizard's own fieldPrefix mirrors
    form = EditForm(prefix='edit')
    populate_form_initial(form, item_dict)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],
    }

    out = TemplateResponse(req, _wizard_template, return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def inline_edit(req:'any_', id:'str') -> 'JsonResponse':
    """ Stores what the gateway list edited without leaving the page - only the fields posted change.
    """
    item_dict = _read_gateway(req, id)

    for name in _inline_field_names:
        if name in req.POST:
            value = req.POST[name]

            # A flag travels as the word it is written with, a text line as itself ..
            if name in _inline_flag_names:
                value = asbool(value)

            # .. the token counts as strings, an empty input meaning no cap or no threshold ..
            elif name in _shaping_int_fields:
                if value:
                    value = int(value)
                else:
                    value = 0

            # .. and the ratio as a float with a well-known default.
            elif name == 'characters_per_token':
                if value:
                    value = float(value)
                else:
                    value = Default_Characters_Per_Token

            item_dict[name] = value

    # The services the gateway exposes arrive as one JSON list of their names
    if 'services' in req.POST:
        item_dict['services'] = loads(req.POST['services'])

    # The security definitions arrive as one JSON list of member ids, and the group
    # of the gateway's own is brought in line with them before the gateway is saved
    if 'security' in req.POST:
        member_id_list = loads(req.POST['security'])
        group_id = save_security_group(req, item_dict['name'], member_id_list)
        item_dict['security_groups'] = [group_id]

    response = req.zato.client.invoke('zato.generic.connection.edit', item_dict)

    if not response.ok:
        raise Exception(f'MCP gateway with id `{id}` could not be saved')

    # The two token counts go back the way the page renders them - a zero means no cap
    # or no threshold and shows as an empty input rather than as a number
    max_response_size = item_dict['max_response_size']
    min_size_threshold = item_dict['min_size_threshold']

    size_cap_mode = item_dict['size_cap_mode']

    # What the row now says of itself
    out = JsonResponse({
        'name': item_dict['name'],
        'url_path': item_dict['url_path'],
        'is_active': asbool(item_dict['is_active']),
        'allow_agent_filters': asbool(item_dict['allow_agent_filters']),
        'max_response_size': max_response_size if max_response_size else '',
        'min_size_threshold': min_size_threshold if min_size_threshold else '',
        'characters_per_token': item_dict['characters_per_token'],
        'size_cap_mode': size_cap_mode,
        'size_cap_label': get_size_cap_label(max_response_size, size_cap_mode),
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

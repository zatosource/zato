# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import re

# Zato
from zato.admin.web import alerts_tab
from zato.common.alerting.object_config import alert_type_mcp
from zato.common.api import API_Key, CONNECTION, GENERIC, Groups, SEC_DEF_TYPE
from zato.common.util.api import asbool
from zato.common.util.gateway import get_mcp_group_name
from zato.common.util.safeguards.common import Mode_Clean, Url_Mode_Remove
from zato.common.util.safeguards.masking import Default_Masking_Custom_Enabled
from zato.common.util.truncate.tokens import Default_Characters_Per_Token, Size_Cap_Mode_Truncate

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intlist, intnone, strdict, strdictlist, strlist, strlistnone, strnone
    any_ = any_
    anylist = anylist
    intlist = intlist
    intnone = intnone
    strdictlist = strdictlist
    strlist = strlist
    strlistnone = strlistnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_service_input_prefix = 'mcp_service_'
_security_input_prefix = 'mcp_security_'
_skill_input_prefix = 'mcp_skill_'

# Security definitions the security picker does not list - a save keeps them in the gateway's group as they are.
_hidden_security_names = {'ide_publisher', 'pubapi'}
_hidden_security_name_part = 'zato.'

# Fields the wizard does not edit, which a save of the wizard keeps as they are stored.
_wizard_kept_field_names = ('session_ttl', 'invoke_timeout')

# The multi-step wizard template, serving both the create and the edit page.
_wizard_template = 'zato/gateway/mcp-wizard.html'

# What the fields the gateway list's size caps popover reads and writes are named after.
_row_edit_prefix = 'mcp-row'

# The alert settings a gateway carries and the names they travel under between the wizard and the backend.
_alert_type = alert_type_mcp
_alert_field_names = alerts_tab.get_storage_field_names(_alert_type)

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
    'oauth',
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
    ('characters_per_token', 'safeguards_url_allow_list', 'oauth_scopes')

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
    'oauth':                               False,
    'oauth_scopes':                        '',
    'max_response_size':                   0,
    'min_size_threshold':                  0,
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
    SEC_DEF_TYPE.OAUTH: {
        'name': 'Authorization',
        'description': 'Bearer token',
        'isRequired': True,
        'isSecret': True,
    },
}

# The hidden inputs the wizard writes the data masking answers and the hook services into on save -
# each list travels as one input per item, all of them under the same name.
_masking_sets_input           = 'mcp_masking_set'
_masking_excluded_input       = 'mcp_masking_excluded'
_masking_custom_fields_input  = 'mcp_masking_custom_field'
_masking_custom_enabled_input = 'mcp_masking_custom_enabled'
_request_hook_input           = 'mcp_request_hook_service'
_response_hook_input          = 'mcp_response_hook_service'

# What a gateway that predates data masking or the hook services is opened with.
_masking_state_defaults = {
    'safeguards_masking_sets': [],
    'safeguards_masking_excluded': [],
    'safeguards_masking_custom_fields': [],
    'safeguards_masking_custom_enabled': Default_Masking_Custom_Enabled,
    'request_hook_service': '',
    'response_hook_service': '',
}

# ################################################################################################################################
# ################################################################################################################################

def get_masking_state(item_dict:'strdict') -> 'strdict':
    """ The data masking answers and the hook services of one gateway, in the shape the wizard's
    scripts seed their state from - a key the gateway predates takes its default.
    """
    values:'strdict' = {}

    for name, default_value in _masking_state_defaults.items():
        if (value := item_dict.get(name)) is None:
            value = default_value
        values[name] = value

    out = {
        'sets': values['safeguards_masking_sets'],
        'excluded': values['safeguards_masking_excluded'],
        'customFields': values['safeguards_masking_custom_fields'],
        'isCustomEnabled': values['safeguards_masking_custom_enabled'],
        'requestHook': values['request_hook_service'],
        'responseHook': values['response_hook_service'],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_masking_input(post:'any_', input_dict:'strdict') -> 'None':
    """ Moves the data masking answers and the hook services the wizard wrote into its hidden inputs
    over to the keys the gateway's opaque configuration stores them under.
    """
    input_dict['safeguards_masking_sets'] = post.getlist(_masking_sets_input)
    input_dict['safeguards_masking_excluded'] = post.getlist(_masking_excluded_input)
    input_dict['safeguards_masking_custom_fields'] = post.getlist(_masking_custom_fields_input)
    input_dict['safeguards_masking_custom_enabled'] = asbool(post[_masking_custom_enabled_input])
    input_dict['request_hook_service'] = post[_request_hook_input]
    input_dict['response_hook_service'] = post[_response_hook_input]

# ################################################################################################################################
# ################################################################################################################################

def numeric_from_bool(value:'any_') -> 'any_':
    """ The opaque storage stores 0 as False and 1 as True, so a numeric field read back
    from it turns these two values into numbers again.
    """
    if value is False:
        out = 0
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

def size_cap_for_display(value:'any_') -> 'any_':
    """ A token count as an input renders it - a zero means no cap or no threshold and shows as an empty input.
    """
    if value:
        out = value
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

def is_hidden_security_name(name:'str') -> 'bool':
    """ Whether the security picker leaves out the definition of that name.
    """
    out = name in _hidden_security_names or _hidden_security_name_part in name
    return out

# ################################################################################################################################
# ################################################################################################################################

def read_gateway(req:'any_', id:'any_') -> 'strdict':
    """ One MCP gateway as it is stored, refusing an id of a connection of any other type.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'MCP gateway with id `{id}` could not be read')

    out = response.data

    if out['type_'] != GENERIC.CONNECTION.TYPE.GATEWAY_MCP:
        raise Exception(f'Connection with id `{id}` is not an MCP gateway')

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_stored_group_list(item_dict:'strdict') -> 'anylist':
    """ The security groups a stored gateway lists, by id, or by name if an earlier import stored them so.
    """
    if 'security_groups' in item_dict:
        out = item_dict['security_groups']
        if out is None:
            out = []
    else:
        out = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_group_id(stored_group_list:'anylist', group_id:'int') -> 'anylist':
    """ The stored security groups of a gateway with the gateway's own group among them.
    """
    out = list(stored_group_list)

    if group_id not in out:
        out.append(group_id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def find_group_id(req:'any_', group_name:'str') -> 'intnone':
    """ Returns the id of the API clients group of that name, or None if there is no such group.
    """
    response = req.zato.client.invoke('zato.groups.get-list', {
        'group_type': Groups.Type.API_Clients,
    })

    out:'intnone' = None

    for group in response.data:
        if group['name'] == group_name:
            out = group['id']
            break

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_group_id_list(req:'any_', stored_group_list:'anylist') -> 'intlist':
    """ The ids of the security groups a gateway lists, with the groups listed by name resolved to their ids.
    """
    group_name_to_id:'strdict' = {}
    has_names = False

    for item in stored_group_list:
        if isinstance(item, str):
            has_names = True
            break

    if has_names:
        response = req.zato.client.invoke('zato.groups.get-list', {
            'group_type': Groups.Type.API_Clients,
        })
        for group in response.data:
            group_name_to_id[group['name']] = group['id']

    out:'intlist' = []

    for item in stored_group_list:
        if isinstance(item, str):
            if item in group_name_to_id:
                out.append(group_name_to_id[item])
        else:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_group_member_list(req:'any_', group_id:'int') -> 'strdictlist':
    """ The members of one API clients group.
    """
    response = req.zato.client.invoke('zato.groups.get-member-list', {
        'group_type': Groups.Type.API_Clients,
        'group_id': group_id,
    })

    out = response.data
    return out

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroupChange:
    """ The security group of a gateway's own, named after the gateway, brought in line with the security
    definitions picked for it. The members the group held before the change are kept, so that a save
    of the gateway that the server refuses returns the group to them.
    """

    def __init__(self, req:'any_', gateway_name:'str', is_create:'bool') -> 'None':
        self.req = req
        self.gateway_name = gateway_name
        self.is_create = is_create
        self.group_name = get_mcp_group_name(gateway_name)
        self.group_id:'intnone' = None

        # None means that the group did not exist before the change
        self.previous_member_id_list:'strlistnone' = None

        # Whether the group has been created or its members replaced, which is what a revert undoes
        self.is_applied = False

    def _find_channel_using_group(self, group_id:'int') -> 'strnone':
        """ Returns the name of an HTTP channel that the group secures, or None if no channel uses it.
        """
        response = self.req.zato.client.invoke('zato.http-soap.get-list', {
            'connection': CONNECTION.CHANNEL,
            'paginate': False,
        })

        out:'strnone' = None

        for channel in response.data:
            if 'security_groups' in channel:
                if security_groups := channel['security_groups']:
                    if group_id in security_groups:
                        out = channel['name']
                        break

        return out

    def _raise_if_not_ok(self, response:'any_') -> 'None':
        """ Stops the save of the gateway when the groups service refused the change of its group.
        """
        if not response.ok:
            raise Exception(response.details)

    def _set_members(self, member_id_list:'strlist') -> 'None':
        """ Replaces the members of the existing group with the given ones.
        """
        response = self.req.zato.client.invoke('zato.groups.edit', {
            'id': self.group_id,
            'group_type': Groups.Type.API_Clients,
            'name': self.group_name,
            'member_id_list': member_id_list,
            'skip_gateway_name': self.gateway_name,
        })
        self._raise_if_not_ok(response)

    def apply(self, member_id_list:'strlist') -> 'int':
        """ Creates the group with the given members, or replaces the members of the existing one,
        and returns the group's id.
        """
        group_id = find_group_id(self.req, self.group_name)

        # A gateway saved before already has its group, whose current members are kept before they are replaced ..
        if group_id:

            # .. a new gateway takes over a group of its name only if no channel uses it ..
            if self.is_create:
                if channel_name := self._find_channel_using_group(group_id):
                    raise Exception(f'Security group `{self.group_name}` is already in use by channel `{channel_name}`')

            self.group_id = group_id

            previous_member_id_list:'strlist' = []
            new_member_id_list = list(member_id_list)

            for member in get_group_member_list(self.req, group_id):
                member_id = f'{member["sec_type"]}-{member["security_id"]}'
                previous_member_id_list.append(member_id)

                # .. the members the picker does not list stay in the group ..
                if is_hidden_security_name(member['name']):
                    if member_id not in new_member_id_list:
                        new_member_id_list.append(member_id)

            self.previous_member_id_list = previous_member_id_list
            self._set_members(new_member_id_list)
            self.is_applied = True

        # .. while a gateway saved for the first time receives a new one.
        else:
            response = self.req.zato.client.invoke('zato.groups.create', {
                'group_type': Groups.Type.API_Clients,
                'name': self.group_name,
                'member_id_list': member_id_list,
            })
            self._raise_if_not_ok(response)
            group_id = response.data['id']
            self.group_id = group_id
            self.is_applied = True

        out = group_id
        return out

    def revert(self) -> 'None':
        """ Returns the group to the state it was in before the change - a group created by the change is deleted
        and an existing one receives its previous members back.
        """
        if not self.is_applied:
            return

        if self.previous_member_id_list is None:
            _ = self.req.zato.client.invoke('zato.groups.delete', {'id': self.group_id})
        else:
            self._set_members(self.previous_member_id_list)

        logger.info('Security group `%s` of an MCP gateway returned to its state before the refused save', self.group_name)

# ################################################################################################################################
# ################################################################################################################################

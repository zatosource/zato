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
from zato.common.api import API_Key, Groups, SEC_DEF_TYPE
from zato.common.defaults import http_plain_server_port
from zato.common.util.safeguards.common import Mode_Clean, Url_Mode_Remove
from zato.common.util.tcp import get_current_ip
from zato.common.util.truncate.tokens import Default_Characters_Per_Token, Size_Cap_Mode_Truncate

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

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

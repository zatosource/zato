# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.gateway.mcp import CreateForm, EditForm
from zato.admin.web.views import method_allowed
from zato.admin.web.views.gateway.mcp.common import _alert_type, _inline_field_names, _inline_flag_names, \
    _numeric_shaping_fields, _shaping_display_defaults, _shaping_int_fields, _wizard_template, get_size_cap_label, \
    numeric_from_bool, save_security_group
from zato.admin.web.views.gateway.mcp_tool_sources import build_tool_sources, Tool_Source_List
from zato.common.util.api import asbool
from zato.common.util.truncate.tokens import Default_Characters_Per_Token

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict
    any_ = any_
    strdict = strdict

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def wizard_create(req:'any_') -> 'TemplateResponse':
    """ A multi-step wizard for a new MCP gateway.
    """
    form = CreateForm(req=req)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': False,
        'item_id': '',
        'tool_sources': build_tool_sources(req, {}),
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
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
    form = EditForm(prefix='edit', req=req)

    # A duration is stored as seconds and a size as bytes, each edited as a count with a unit
    alerts_tab.split_unit_fields(_alert_type, item_dict)
    populate_form_initial(form, item_dict)

    # What the gateway already exposes, per source - the Tools card opens on these picks
    assigned_by_key:'strdict' = {}

    for source in Tool_Source_List:

        if (assigned := item_dict.get(source.config_key)) is None:
            assigned = []

        assigned_by_key[source.key] = assigned

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],
        'tool_sources': build_tool_sources(req, assigned_by_key),
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
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

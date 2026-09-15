# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.channel.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import method_allowed, get_http_channel_security_id, SecurityList
from zato.admin.web.views.channel.hl7.mllp.common import _alert_type, _get_security_group_id, _Inline_Field_Names, \
    _Inline_Flag_Names, _MTLS_Select_Prefix, _No_Previous_Default, _REST_Channel_Name_Prefix, _Wizard_Template
from zato.admin.web.views.channel.hl7.mllp.index import get_match_values
from zato.common.api import GENERIC, Groups, SEC_DEF_TYPE
from zato.common.hl7.mllp.fields import get_match_label
from zato.common.util.api import asbool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist
    any_ = any_
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def _get_rest_security_key_list(req:'any_', mllp_name:'str') -> 'strlist':
    """ The definitions the channel's REST bridge authenticates its callers with, each in the
    sec_type/id form the wizard's security rows are built from. Two or more of them are kept in
    a group of the channel's own, which is where the whole list is read back from.
    """
    out = []

    group_name = _REST_Channel_Name_Prefix + mllp_name
    group_id = _get_security_group_id(req, group_name)

    if not group_id:
        return out

    response = req.zato.client.invoke('zato.groups.get-member-list', {
        'group_type': Groups.Type.API_Clients,
        'group_id': group_id,
    })

    for member in response.data:
        sec_type = member['sec_type']
        security_id = member['security_id']
        out.append(f'{sec_type}/{security_id}')

    return out

# ################################################################################################################################

def _populate_rest_bridge(req:'any_', item_dict:'stranydict', rest_channel_id:'int') -> 'None':
    """ Puts the path and the security definition of the backing REST channel under the two
    fields the wizard's REST popover opens with. An MLLP channel stores neither of them - both
    belong to the REST channel it keeps alongside itself.
    """
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': rest_channel_id,
    })

    rest_channel = response.data

    item_dict['rest_url_path'] = rest_channel.url_path
    item_dict['rest_security_id'] = get_http_channel_security_id(rest_channel)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def wizard_create(req:'any_') -> 'TemplateResponse':
    """ A multi-step wizard for a new HL7 MLLP channel.
    """
    security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, [SEC_DEF_TYPE.BASIC_AUTH])
    mtls_security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, [SEC_DEF_TYPE.MTLS])

    form = CreateForm(req=req, security_list=security_list, mtls_security_list=mtls_security_list)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': False,
        'item_id': '',
        'rest_channel_id': 0,
        'security_key_list': [],
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

@method_allowed('GET')
def wizard_edit(req:'any_', id:'str') -> 'TemplateResponse':
    """ The same wizard, opened on one existing HL7 MLLP channel.
    """

    # The URL points to one channel, so one channel is what is fetched - the page renders
    # nothing about any of the others ..
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{id}` could not be read')

    item_dict = response.data

    # .. the mTLS select carries a definition's type alongside its id, while a channel stores
    # the id alone, so what was stored is put back into the shape the select offers ..
    if 'security_id' in item_dict:
        security_id = item_dict['security_id']
        if security_id:
            item_dict['security_id'] = f'{_MTLS_Select_Prefix}{security_id}'

    # .. the REST bridge, if there is one, says what its path and its security are ..
    rest_channel_id = 0

    if 'rest_channel_id' in item_dict:
        stored_rest_channel_id = item_dict['rest_channel_id']

        # A channel that never had a bridge may still carry the key with nothing under it,
        # and what the page is given goes into the form as text, so a null would reach
        # the save as the word it is written with rather than as no channel at all
        if stored_rest_channel_id:
            rest_channel_id = stored_rest_channel_id

    if rest_channel_id:
        _populate_rest_bridge(req, item_dict, rest_channel_id)

    security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, [SEC_DEF_TYPE.BASIC_AUTH])
    mtls_security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, [SEC_DEF_TYPE.MTLS])

    # .. the edit endpoint reads its input under the edit- prefix, which is what the form
    # .. is built with and what the wizard's own fieldPrefix mirrors ..
    form = EditForm(prefix='edit', req=req, security_list=security_list, mtls_security_list=mtls_security_list)

    # A duration is stored as seconds and edited as a count with a unit
    alerts_tab.split_unit_fields(_alert_type, item_dict)
    populate_form_initial(form, item_dict)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],

        # The id of the backing REST channel travels with the save, so a channel renamed here
        # keeps the REST channel it already has rather than being given a second one
        'rest_channel_id': rest_channel_id,
        'security_key_list': _get_rest_security_key_list(req, item_dict['name']),
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

def _save_channel(req:'any_', item_dict:'stranydict') -> 'None':
    """ Saves a channel the way any other edit of it would.
    """
    channel_id = item_dict['id']
    response = req.zato.client.invoke('zato.generic.connection.edit', item_dict)

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{channel_id}` could not be saved')

# ################################################################################################################################

def _read_channel(req:'any_', id:'str') -> 'stranydict':
    """ One channel as it currently stands.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{id}` could not be read')

    out = response.data
    return out

# ################################################################################################################################

def _is_default(item:'stranydict') -> 'bool':
    """ Whether a channel holds the default flag. A generic connection carries the flag only once
    something has set it, so a channel that never has is not the default.
    """
    if 'is_default' not in item:
        return False

    out = asbool(item['is_default'])
    return out

# ################################################################################################################################

def _clear_other_default(req:'any_', id:'str') -> 'int':
    """ Takes the default flag off whichever other channel held it, returning its id, zero if none did.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
    })

    for item in response.data:

        # The channel just made the default is not the one being cleared
        if str(item['id']) == str(id):
            continue

        if _is_default(item):
            other = _read_channel(req, item['id'])
            other['is_default'] = False
            _save_channel(req, other)

            out = item['id']
            return out

    return _No_Previous_Default

# ################################################################################################################################

@method_allowed('POST')
def inline_edit(req:'any_', id:'str') -> 'JsonResponse':
    """ Stores what the channel list edited without leaving the page - only the fields posted change.
    """
    item_dict = _read_channel(req, id)

    for name in _Inline_Field_Names:
        if name in req.POST:
            value = req.POST[name]

            # A flag travels as the word it is written with, everything else as itself
            if name in _Inline_Flag_Names:
                value = asbool(value)

            item_dict[name] = value

    # A row may be left with neither a service nor a destination, one of the two being
    # cleared before the other is picked in the panel that comes next
    service = item_dict['service']

    _save_channel(req, item_dict)

    # A flag comes back from storage as the word it was written with as readily as the thing itself
    is_active = asbool(item_dict['is_active'])
    is_default = _is_default(item_dict)

    # Only one channel is the default, and the page is told which row lost it
    if is_default:
        default_cleared_id = _clear_other_default(req, id)
    else:
        default_cleared_id = _No_Previous_Default

    # What the row now says of itself
    out = JsonResponse({
        'is_active': is_active,
        'is_default': is_default,
        'match_label': get_match_label(get_match_values(lambda name: item_dict[name])),
        'default_cleared_id': default_cleared_id,
        'service': service,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

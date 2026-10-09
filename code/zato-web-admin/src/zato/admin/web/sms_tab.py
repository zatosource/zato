# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Django side of the Config tab of the SMS dialogs - the provider fields the outgoing connection and the channel
# forms share, the field lists of both connection types, the timeout and the polling schedule as a count with a unit,
# and the outgoing connection a channel's form creates and edits along with the channel.

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab, delivery_tab
from zato.admin.web.forms import add_select, health_check_run_unit_choices, health_check_unit_for_form, \
    health_check_unit_to_scheduler
from zato.common.alerting.object_config import alert_type_sms_outgoing
from zato.common.api import GENERIC, SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict, strtuple

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler

# The fields of the Provider and Messages sections, shared by both forms
Provider_Field_Names = (SMS.Field_Provider, SMS.Field_Host, SMS.Field_Username, SMS.Field_Sender)

# The fields that are stored encrypted and never shown again
Secret_Field_Names = (SMS.Field_Secret, SMS.Field_Signature_Secret)

# The outgoing connection's own fields beyond its name and its secrets
Outgoing_Required_Field_Names = (SMS.Field_Provider, SMS.Field_Username, SMS.Field_Sender)
Outgoing_Optional_Field_Names = (SMS.Field_Host, SMS.Field_Channel_Name, SMS.Field_Pool_Size, SMS.Field_Timeout)
Outgoing_Field_Names = Outgoing_Required_Field_Names + Outgoing_Optional_Field_Names

# The unit select of the timeout
Timeout_Unit_Field_Name = delivery_tab.unit_field_name(SMS.Field_Timeout)

# The channel's own fields
Channel_Required_Field_Names = (SMS.Field_Service, SMS.Field_Receive_Mode)
Channel_Optional_Field_Names = (_scheduler.Field_Run_Every, _scheduler.Field_Run_Unit)

# The ID of a channel's outgoing connection, a hidden field of the channel's form
Outconn_ID_Field_Name = 'outconn_id'

# The fields of an outgoing connection that a channel's edit copies from the stored connection
Outgoing_Stored_Field_Names = Outgoing_Field_Names + tuple(delivery_tab.retry_field_defaults) + \
    tuple(delivery_tab.field_defaults) + alerts_tab.get_storage_field_names(alert_type_sms_outgoing)

# The provider select lists every provider under its human-readable name
_provider_choices = []

for _provider_name in SMS.ProviderList:
    _provider_choices.append({'id': _provider_name, 'name': SMS.ProviderHuman[_provider_name]})

# The polling schedule's unit select names a unit in the singular, the scheduler in the plural
poll_unit_choices = health_check_run_unit_choices

# ################################################################################################################################
# ################################################################################################################################

def add_provider_fields(form:'any_') -> 'None':
    """ Adds the provider, host, credential and sender fields to a create or edit form.
    """
    form.fields[SMS.Field_Provider] = forms.ChoiceField(widget=forms.Select())
    form.fields[SMS.Field_Host] = forms.CharField(
        required=False, widget=forms.TextInput(), initial=SMS.Default_Host[SMS.Provider.Twilio])
    form.fields[SMS.Field_Username] = forms.CharField(widget=forms.TextInput())
    form.fields[SMS.Field_Secret] = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    form.fields[SMS.Field_Signature_Secret] = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    form.fields[SMS.Field_Sender] = forms.CharField(widget=forms.TextInput())

    add_select(form, SMS.Field_Provider, _provider_choices, needs_initial_select=False)

# ################################################################################################################################

def add_timeout_fields(form:'any_') -> 'None':
    """ Adds the timeout as a count with a unit select to a create or edit form.
    """
    count, unit = delivery_tab.split_duration(SMS.Default_Timeout)

    form.fields[SMS.Field_Timeout] = forms.CharField(widget=forms.TextInput(), initial=count)
    form.fields[Timeout_Unit_Field_Name] = forms.ChoiceField(
        required=False, choices=delivery_tab.duration_unit_choices, initial=unit, widget=forms.Select())

# ################################################################################################################################

def join_timeout(params:'any_', prefix:'str', input_dict:'stranydict') -> 'None':
    """ Turns the timeout's count and unit of a form into the seconds it is stored as, in place.
    """
    unit = params.get(prefix + Timeout_Unit_Field_Name)
    if unit is None:
        unit = delivery_tab.Duration_Unit_Smallest

    input_dict[SMS.Field_Timeout] = delivery_tab.join_duration(int(input_dict[SMS.Field_Timeout]), unit)

# ################################################################################################################################

def split_timeout(item:'any_') -> 'None':
    """ Turns the timeout's seconds on a listed connection into the count and the unit the edit form shows, in place.
    """
    count, unit = delivery_tab.split_duration(int(item[SMS.Field_Timeout]))
    item[SMS.Field_Timeout] = count
    item[Timeout_Unit_Field_Name] = unit

# ################################################################################################################################

def poll_unit_for_form(unit:'str') -> 'str':
    """ The polling unit a listed channel shows on the form - a webhook channel shows the default.
    """
    out = health_check_unit_for_form(unit)
    return out

# ################################################################################################################################

def poll_unit_for_scheduler(unit:'str') -> 'str':
    """ The polling unit of a form in the scheduler's vocabulary.
    """
    out = health_check_unit_to_scheduler[unit]
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_provider_config() -> 'stranydict':
    """ The provider data of the Config tab's JavaScript - names, default hosts and the providers with a signature secret
    or a required host.
    """
    out = {
        'providers': SMS.ProviderList,
        'provider_human': SMS.ProviderHuman,
        'default_host': SMS.Default_Host,
        'providers_with_signature_secret': SMS.Providers_With_Signature_Secret,
        'providers_requiring_host': SMS.Providers_Requiring_Host,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _outconn_identity(channel_name:'str', is_active:'bool') -> 'stranydict':
    """ The type and name fields of the outgoing connection of a channel - the connection is named after the channel.
    """
    out = {
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
        'name': channel_name,
        'is_active': is_active,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        SMS.Field_Channel_Name: channel_name,
    }

    return out

# ################################################################################################################################

def _provider_input(form_input:'any_') -> 'stranydict':
    """ The provider fields of a channel's form, the empty secrets excluded, as an empty secret keeps the stored one.
    """
    out = {}

    for name in Provider_Field_Names:
        out[name] = form_input[name]

    for name in Secret_Field_Names:
        value = form_input[name]
        if value:
            out[name] = value

    return out

# ################################################################################################################################

def build_outconn_create_input(cluster_id:'any_', channel_name:'str', is_active:'bool', form_input:'any_') -> 'stranydict':
    """ The request that creates the outgoing connection of a new channel - the provider fields of the form
    and the defaults of every other field.
    """
    out = {'cluster_id': cluster_id}
    out.update(_outconn_identity(channel_name, is_active))
    out.update(_provider_input(form_input))

    return out

# ################################################################################################################################

def build_outconn_edit_input(
    cluster_id:'any_',
    channel_name:'str',
    is_active:'bool',
    form_input:'any_',
    stored:'anydict',
) -> 'stranydict':
    """ The request that edits the outgoing connection of a channel - every stored field of the connection,
    with the provider fields of the form over them.
    """
    out = {'cluster_id': cluster_id, 'id': stored['id']}

    for name in Outgoing_Stored_Field_Names:
        if name in stored:
            out[name] = stored[name]

    out.update(_outconn_identity(channel_name, is_active))
    out.update(_provider_input(form_input))

    return out

# ################################################################################################################################

def find_outconn(items:'any_', outconn_id:'int') -> 'anydict':
    """ The outgoing connection of that ID among the listed ones.
    """
    for item in items:
        if item['id'] == outconn_id:
            return item

    raise ValueError(f'Outgoing SMS connection `{outconn_id}` does not exist')

# ################################################################################################################################

def outconn_field_names() -> 'strtuple':
    """ The fields of a channel's outgoing connection that the channel's row has.
    """
    out = (Outconn_ID_Field_Name,) + Provider_Field_Names
    return out

# ################################################################################################################################
# ################################################################################################################################

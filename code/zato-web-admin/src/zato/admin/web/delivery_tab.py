# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Delivery tab of an outgoing connection's create and edit forms - the retry settings, the queue switch and
# the dead-letter queue settings - what a form sends and what a listed row carries, shared by every outgoing
# connection type that can deliver through a queue. The lines themselves are in shared/delivery-tab.html.

# Django
from django import forms

# Zato
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# Each option is the action's stored value and the label a form shows for it
dlq_action_choices = (
    (_dlq.Action.Keep, 'Keep in DLQ'),
    (_dlq.Action.Retry, 'Retry'),
    (_dlq.Action.Forward, 'Forward to topic'),
    (_dlq.Action.Discard, 'Discard'),
)

# ################################################################################################################################

# The units a number of seconds is shown in, smallest first - an option's value is the noun in the singular,
# which a summary reads a count with - `1 second`, `2 minutes` - and its label the plural.
Duration_Units = (
    ('second', 1),
    ('minute', 60),
    ('hour', 3600),
    ('day', 86400),
)

Duration_Unit_Smallest = Duration_Units[0][0]

duration_unit_choices = []

for _unit_name, _ in Duration_Units:
    duration_unit_choices.append((_unit_name, _unit_name + 's'))

# A count of seconds is stored as one number and edited as a count with a unit select named after it,
# which is a field of the form alone
Unit_Field_Suffix = '_unit'

# The stored fields that are counts of seconds
duration_fields = (_retry.Field_Sleep_Time, _retry.Field_Backoff_Threshold, _dlq.Field_Retry_Interval)

# ################################################################################################################################

def unit_field_name(name:'str') -> 'str':
    """ The name of the unit select of a count of seconds.
    """
    out = name + Unit_Field_Suffix
    return out

# ################################################################################################################################

def split_duration(seconds:'int') -> 'tuple[int, str]':
    """ A number of seconds as a count and the largest unit dividing it evenly - 86400 is one day, 3600 is one hour,
    120 is two minutes, 90 is ninety seconds.
    """
    unit_seconds = Duration_Units[0][1]
    out_unit = Duration_Unit_Smallest

    for unit_name, candidate_seconds in Duration_Units:
        if seconds % candidate_seconds == 0:
            unit_seconds = candidate_seconds
            out_unit = unit_name

    out_count = seconds // unit_seconds

    return out_count, out_unit

# ################################################################################################################################

def join_duration(count:'int', unit_name:'str') -> 'int':
    """ A count of one unit back as seconds - what split_duration took apart.
    """
    out = 0

    for candidate_name, unit_seconds in Duration_Units:
        if candidate_name == unit_name:
            out = count * unit_seconds

    return out

# ################################################################################################################################
# ################################################################################################################################

# Every queue and DLQ field and its default - a connection that predates the fields carries none of them
field_defaults = {
    _queue.Field_Use_Queue: _queue.Default_Use_Queue,
    _dlq.Field_Use_DLQ: _dlq.Default_Use_DLQ,
    _dlq.Field_Action: _dlq.Default_Action,
    _dlq.Field_Retries: _dlq.Default_Retries,
    _dlq.Field_Retry_Interval: _dlq.Default_Retry_Interval,
    _dlq.Field_Forward_To: _dlq.Default_Forward_To,
    _dlq.Field_Keep_Header: _dlq.Default_Keep_Header,
}

# A checkbox is on when its name is in the POST data at all
bool_fields = (_queue.Field_Use_Queue, _dlq.Field_Use_DLQ, _dlq.Field_Keep_Header)

# A count is sent as an integer
int_fields = (_dlq.Field_Retries, _dlq.Field_Retry_Interval)

# ################################################################################################################################
# ################################################################################################################################

def add_delivery_fields(form:'any_', is_edit:'bool'=False) -> 'None':
    """ Adds the queue switch, the DLQ fields and the unit selects of the counts of seconds to a create or edit form,
    whose own retry fields the tab reads as well. The two switches are the tab's own lines, the rest are hidden
    and edited in the tab's popovers. An edit form's checkboxes start unchecked, the item that opens the form checks them.
    """
    if is_edit:
        use_dlq_attrs = {}
        keep_header_attrs = {}
    else:
        use_dlq_attrs = {'checked':'checked'}
        keep_header_attrs = {'checked':'checked'}

    form.fields[_queue.Field_Use_Queue] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    form.fields[_dlq.Field_Use_DLQ] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs=use_dlq_attrs))
    form.fields[_dlq.Field_Action] = forms.ChoiceField(
        required=False, choices=dlq_action_choices, initial=_dlq.Default_Action, widget=forms.Select())
    form.fields[_dlq.Field_Retries] = forms.CharField(required=False, initial=_dlq.Default_Retries, widget=forms.TextInput())
    form.fields[_dlq.Field_Forward_To] = forms.ChoiceField(required=False, widget=forms.Select())
    form.fields[_dlq.Field_Keep_Header] = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs=keep_header_attrs))

    # The default number of seconds is shown as a count and a unit too
    count, unit = split_duration(_dlq.Default_Retry_Interval)
    form.fields[_dlq.Field_Retry_Interval] = forms.CharField(required=False, initial=count, widget=forms.TextInput())
    form.fields[unit_field_name(_dlq.Field_Retry_Interval)] = forms.ChoiceField(
        required=False, choices=duration_unit_choices, initial=unit, widget=forms.Select())

    # The retry fields are the form's own, each count of seconds among them gets its unit select
    for name in (_retry.Field_Sleep_Time, _retry.Field_Backoff_Threshold):
        count, unit = split_duration(form.fields[name].initial)
        form.fields[name].initial = count
        form.fields[unit_field_name(name)] = forms.ChoiceField(
            required=False, choices=duration_unit_choices, initial=unit, widget=forms.Select())

# ################################################################################################################################
# ################################################################################################################################

def get_message_fields(params:'any_', prefix:'str'='') -> 'stranydict':
    """ The queue and DLQ fields a create or edit form submitted, typed the way they are stored -
    a checkbox is a bool, a count is an int and anything left empty gets its default.
    """
    out = {}

    for name, default in field_defaults.items():
        value = params.get(prefix + name)

        if name in bool_fields:
            out[name] = bool(value)

        elif name in int_fields:
            if value:
                out[name] = int(value)
            else:
                out[name] = default

        else:
            if value is None:
                out[name] = default
            else:
                out[name] = value

    return out

# ################################################################################################################################

def join_unit_fields(params:'any_', prefix:'str', message:'stranydict') -> 'None':
    """ Turns each count of seconds in a message, entered as a count of the unit its select says, into the number
    of seconds it is stored as, in place. The form's default unit stands for a form without the select.
    """
    for name in duration_fields:
        unit = params.get(prefix + unit_field_name(name))
        if unit is None:
            unit = Duration_Unit_Smallest
        message[name] = join_duration(message[name], unit)

# ################################################################################################################################

def fill_row(row:'any_', item:'any_') -> 'None':
    """ The queue and DLQ fields of a listed connection that its edit form reads off the row - they are opaque attributes,
    so a connection that predates them carries no values, in which case the defaults are displayed.
    """
    for name, default in field_defaults.items():
        value = item.get(name)
        if value is None:
            value = default
        setattr(row, name, value)

# ################################################################################################################################

def split_unit_fields(row:'any_') -> 'None':
    """ Turns each count of seconds on a listed connection into the count and the unit the edit form shows, in place -
    the retry fields are on the row by the time this runs, and so are the DLQ fields.
    """
    for name in duration_fields:
        count, unit = split_duration(row[name])
        row[name] = count
        row[unit_field_name(name)] = unit

# ################################################################################################################################
# ################################################################################################################################

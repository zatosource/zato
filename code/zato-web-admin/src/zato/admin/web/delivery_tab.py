# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Django side of the Delivery tab of an outgoing connection's create and edit forms.

# Django
from django import forms

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.delivery_config import Delivery_Bool_Fields, Delivery_Field_Defaults, Delivery_Int_Fields

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

dlq_action_choices = (
    (_dlq.Action.Keep, 'Keep in DLQ'),
    (_dlq.Action.Retry, 'Retry'),
    (_dlq.Action.Forward, 'Forward to topic'),
    (_dlq.Action.Discard, 'Discard'),
)

# ################################################################################################################################

# The units a number of seconds is shown in, smallest first
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

# The suffix of the unit select of a count of seconds
Unit_Field_Suffix = '_unit'

# The fields that are counts of seconds
duration_fields = (_retry.Field_Sleep_Time, _retry.Field_Backoff_Threshold, _dlq.Field_Retry_Interval)

# ################################################################################################################################

def unit_field_name(name:'str') -> 'str':
    """ The name of the unit select of a count of seconds.
    """
    out = name + Unit_Field_Suffix
    return out

# ################################################################################################################################

def split_duration(seconds:'int') -> 'tuple[int, str]':
    """ A number of seconds as a count and the largest unit dividing it evenly.
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
    """ A count of one unit as seconds.
    """
    out = 0

    for candidate_name, unit_seconds in Duration_Units:
        if candidate_name == unit_name:
            out = count * unit_seconds

    return out

# ################################################################################################################################
# ################################################################################################################################

field_defaults = Delivery_Field_Defaults
bool_fields = Delivery_Bool_Fields
int_fields = Delivery_Int_Fields

# ################################################################################################################################
# ################################################################################################################################

def add_delivery_fields(form:'any_', is_edit:'bool'=False) -> 'None':
    """ Adds the queue switch, the DLQ fields and the unit selects to a create or edit form.
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

    count, unit = split_duration(_dlq.Default_Retry_Interval)
    form.fields[_dlq.Field_Retry_Interval] = forms.CharField(required=False, initial=count, widget=forms.TextInput())
    form.fields[unit_field_name(_dlq.Field_Retry_Interval)] = forms.ChoiceField(
        required=False, choices=duration_unit_choices, initial=unit, widget=forms.Select())

    # The retry fields are the form's own
    for name in (_retry.Field_Sleep_Time, _retry.Field_Backoff_Threshold):
        count, unit = split_duration(form.fields[name].initial)
        form.fields[name].initial = count
        form.fields[unit_field_name(name)] = forms.ChoiceField(
            required=False, choices=duration_unit_choices, initial=unit, widget=forms.Select())

# ################################################################################################################################
# ################################################################################################################################

def get_message_fields(params:'any_', prefix:'str'='') -> 'stranydict':
    """ The queue and DLQ fields a form submitted, typed as stored.
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
    """ Turns each count of a unit in a message into seconds, in place.
    """
    for name in duration_fields:
        unit = params.get(prefix + unit_field_name(name))
        if unit is None:
            unit = Duration_Unit_Smallest
        message[name] = join_duration(message[name], unit)

# ################################################################################################################################

def fill_row(row:'any_', item:'any_') -> 'None':
    """ Copies the queue and DLQ fields of a listed connection onto its row, with defaults filled in.
    """
    for name, default in field_defaults.items():
        value = item.get(name)
        if value is None:
            value = default
        setattr(row, name, value)

# ################################################################################################################################

def split_unit_fields(row:'any_') -> 'None':
    """ Turns each count of seconds on a row into a count and a unit, in place.
    """
    for name in duration_fields:
        count, unit = split_duration(row[name])
        row[name] = count
        row[unit_field_name(name)] = unit

# ################################################################################################################################
# ################################################################################################################################

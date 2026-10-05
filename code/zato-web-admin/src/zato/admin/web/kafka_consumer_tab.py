# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Django side of the Consumer and Routing tabs of a Kafka channel's create and edit forms.

# stdlib
from json import dumps, loads

# Django
from django import forms

# Zato
from zato.admin.web.delivery_tab import duration_unit_choices, join_duration, split_duration, Unit_Field_Suffix, unit_field_name
from zato.admin.web.forms import add_select
from zato.admin.web.kafka_producer_tab import _unit_choices, join_unit, Select_Class, Size_Units, split_unit
from zato.common.api import KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    any_ = any_
    anylist = anylist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_consumer = KAFKA.Consumer
_routing = KAFKA.Routing

# The topic list, one topic per line
Field_Topics = _consumer.Field_Topics

# The routing rules, as a JSON list
Field_Routing = _consumer.Field_Routing

# The scratch fields one rule is edited through
Routing_Field_Prefix = 'routing_'

Field_Routing_Topic = Routing_Field_Prefix + _routing.Key_Topic
Field_Routing_Header_Name = Routing_Field_Prefix + _routing.Key_Header_Name
Field_Routing_Header_Value = Routing_Field_Prefix + _routing.Key_Header_Value
Field_Routing_Service = Routing_Field_Prefix + _routing.Key_Service

Routing_Scratch_Fields = (
    Field_Routing_Topic,
    Field_Routing_Header_Name,
    Field_Routing_Header_Value,
    Field_Routing_Service,
)

# The fields that carry a unit select, each with its units
size_unit_fields = {
    _consumer.Field_Max_Message_Size: Size_Units,
}

duration_unit_fields = (
    _consumer.Field_Dedup_TTL,
)

# ################################################################################################################################
# ################################################################################################################################

# The hidden columns of a list page's row, in this order
Consumer_Field_Names = (
    _consumer.Field_Topics,
    _consumer.Field_Auto_Offset_Reset,
    _consumer.Field_Max_Message_Size,
    unit_field_name(_consumer.Field_Max_Message_Size),
    _consumer.Field_Max_In_Flight,
    _consumer.Field_Should_Deliver_Tombstones,
    _consumer.Field_Dedup_Header,
    _consumer.Field_Dedup_TTL,
    unit_field_name(_consumer.Field_Dedup_TTL),
    _consumer.Field_Routing,
)

# ################################################################################################################################

def get_consumer_tab_config() -> 'stranydict':
    """ What a list page hands its JS about the tabs, through a json_script element.
    """
    out = {
        'field_names': list(Consumer_Field_Names),
        'unit_field_suffix': Unit_Field_Suffix,
        'routing_keys': list(_routing.KeyList),
        'routing_field_prefix': Routing_Field_Prefix,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_consumer_fields(form:'any_', is_edit:'bool'=False) -> 'None':
    """ Adds the Consumer and Routing tabs' fields to a create or edit form.
    """
    form.fields[Field_Topics] = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}))

    form.fields[_consumer.Field_Auto_Offset_Reset] = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={'class':Select_Class}))
    add_select(form, _consumer.Field_Auto_Offset_Reset, KAFKA.AUTO_OFFSET_RESET(), needs_initial_select=False)
    form.fields[_consumer.Field_Auto_Offset_Reset].initial = _consumer.Default_Auto_Offset_Reset

    form.fields[_consumer.Field_Should_Deliver_Tombstones] = forms.BooleanField(
        required=False, widget=forms.CheckboxInput())

    form.fields[_consumer.Field_Max_In_Flight] = forms.CharField(
        required=False, initial=_consumer.Default_Max_In_Flight, widget=forms.TextInput())

    form.fields[_consumer.Field_Dedup_Header] = forms.CharField(
        required=False, initial=_consumer.Default_Dedup_Header, widget=forms.TextInput())

    for name, units in size_unit_fields.items():
        count, unit = split_unit(_consumer.Defaults[name], units)
        form.fields[name] = forms.CharField(required=False, initial=count, widget=forms.TextInput())
        form.fields[unit_field_name(name)] = forms.ChoiceField(
            required=False, choices=_unit_choices(units), initial=unit, widget=forms.Select())

    for name in duration_unit_fields:
        count, unit = split_duration(_consumer.Defaults[name])
        form.fields[name] = forms.CharField(required=False, initial=count, widget=forms.TextInput())
        form.fields[unit_field_name(name)] = forms.ChoiceField(
            required=False, choices=duration_unit_choices, initial=unit, widget=forms.Select())

    form.fields[Field_Routing] = forms.CharField(required=False, initial='[]', widget=forms.HiddenInput())

    form.fields[Field_Routing_Topic] = forms.CharField(required=False, widget=forms.TextInput())
    form.fields[Field_Routing_Header_Name] = forms.CharField(required=False, widget=forms.TextInput())
    form.fields[Field_Routing_Header_Value] = forms.CharField(required=False, widget=forms.TextInput())
    form.fields[Field_Routing_Service] = forms.ChoiceField(required=False, widget=forms.Select())

# ################################################################################################################################

def copy_service_choices(form:'any_') -> 'None':
    """ A rule's service is picked from the same services the channel's own service is.
    """
    form.fields[Field_Routing_Service].choices = list(form.fields['service'].choices)

# ################################################################################################################################
# ################################################################################################################################

def parse_routing(value:'str') -> 'anylist':
    """ The routing rules as a list, out of the JSON text a form or a listing carries.
    """
    if not value:
        return []

    out = loads(value)
    return out

# ################################################################################################################################

def get_consumer_fields(params:'any_', prefix:'str'='') -> 'stranydict':
    """ The consumer's fields a form submitted, typed as stored.
    """
    out = {}

    for name, default in _consumer.Defaults.items():

        # An unchecked checkbox is not submitted at all.
        if name in _consumer.BoolFieldList:
            out[name] = (prefix + name) in params
            continue

        value = params[prefix + name]

        if name in size_unit_fields:
            units = size_unit_fields[name]
            unit = params[prefix + unit_field_name(name)]
            if value:
                out[name] = join_unit(int(value), unit, units)
            else:
                out[name] = default

        elif name in duration_unit_fields:
            unit = params[prefix + unit_field_name(name)]
            if value:
                out[name] = join_duration(int(value), unit)
            else:
                out[name] = default

        elif name in _consumer.IntFieldList:
            if value:
                out[name] = int(value)
            else:
                out[name] = default

        elif name == Field_Routing:
            out[name] = dumps(parse_routing(value))

        elif name == Field_Topics:
            out[name] = value.strip()

        else:
            if value:
                out[name] = value
            else:
                out[name] = default

    return out

# ################################################################################################################################

def fill_row(item:'any_') -> 'None':
    """ Fills in the consumer's fields a listed channel does not carry with their defaults
    and turns each stored number into a count and a unit, in place.
    """
    for name, default in _consumer.Defaults.items():
        if item.get(name) is None:
            item[name] = default

    # A channel stored before the list has `topic` alone.
    if not item[Field_Topics]:
        if 'topic' in item:
            item[Field_Topics] = item['topic']

    for name, units in size_unit_fields.items():
        count, unit = split_unit(item[name], units)
        item[name] = count
        item[unit_field_name(name)] = unit

    for name in duration_unit_fields:
        count, unit = split_duration(item[name])
        item[name] = count
        item[unit_field_name(name)] = unit

    # The rules travel as JSON text.
    item[Field_Routing] = dumps(parse_routing(item[Field_Routing]))

    # What the list shows of the topics
    item['topics_text'] = ', '.join(split_topics(item[Field_Topics]))

# ################################################################################################################################

def split_topics(text:'str') -> 'strlist':
    """ The topic names out of a text with one per line or a comma between them.
    """
    out:'strlist' = []

    for line in text.replace(',', '\n').splitlines():
        line = line.strip()
        if line:
            out.append(line)

    return out

# ################################################################################################################################
# ################################################################################################################################

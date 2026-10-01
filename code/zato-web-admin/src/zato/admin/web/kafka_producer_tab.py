# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Django side of the Producer tab of an outgoing Kafka connection's create and edit forms.

# Django
from django import forms

# Zato
from zato.admin.web.delivery_tab import Unit_Field_Suffix, unit_field_name
from zato.admin.web.forms import add_select
from zato.common.api import KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_producer = KAFKA.Producer

# The class alerts-tab.css sizes a select on a line under
Select_Class = 'alerts-tab-select'

# ################################################################################################################################

# The units each stored number is shown in, smallest first - the noun in the singular and how many stored ones it stands for
Size_Units = (
    ('byte', 1),
    ('kilobyte', 1000),
    ('megabyte', 1000000),
)

Linger_Units = (
    ('millisecond', 1),
    ('second', 1000),
)

Timeout_Units = (
    ('second', 1),
    ('minute', 60),
)

# The fields that carry a unit select, each with its units
unit_fields = {
    _producer.Field_Max_Message_Size: Size_Units,
    _producer.Field_Linger_Ms: Linger_Units,
    _producer.Field_Send_Timeout: Timeout_Units,
}

# ################################################################################################################################

def _unit_choices(units:'any_') -> 'list':
    """ An option's value is the noun in the singular and its label the plural.
    """
    out = []

    for unit_name, _ in units:
        out.append((unit_name, unit_name + 's'))

    return out

# ################################################################################################################################

def split_unit(value:'int', units:'any_') -> 'tuple[int, str]':
    """ A stored number as a count and the largest unit dividing it evenly.
    """
    unit_size = units[0][1]
    out_unit = units[0][0]

    # Zero divides evenly by everything and is shown in the smallest unit
    if value:
        for unit_name, candidate_size in units:
            if value % candidate_size == 0:
                unit_size = candidate_size
                out_unit = unit_name

    out_count = value // unit_size

    return out_count, out_unit

# ################################################################################################################################

def join_unit(count:'int', unit_name:'str', units:'any_') -> 'int':
    """ A count of one unit back as the stored number.
    """
    out = 0

    for candidate_name, unit_size in units:
        if candidate_name == unit_name:
            out = count * unit_size

    return out

# ################################################################################################################################
# ################################################################################################################################

# The hidden columns of a list page's row the tab's fields travel in, in this order - the list page's template,
# its JS config and the row builder all read this one list
Producer_Field_Names = (
    _producer.Field_Compression,
    _producer.Field_Acks,
    _producer.Field_Is_Idempotent,
    _producer.Field_Max_Message_Size,
    unit_field_name(_producer.Field_Max_Message_Size),
    _producer.Field_Linger_Ms,
    unit_field_name(_producer.Field_Linger_Ms),
    _producer.Field_Send_Timeout,
    unit_field_name(_producer.Field_Send_Timeout),
)

# ################################################################################################################################

def get_producer_tab_config() -> 'stranydict':
    """ What a list page hands its JS about the tab, through a json_script element.
    """
    out = {
        'field_names': list(Producer_Field_Names),
        'unit_field_suffix': Unit_Field_Suffix,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_producer_fields(form:'any_', is_edit:'bool'=False) -> 'None':
    """ Adds the producer's fields and the unit selects to a create or edit form - the compression method select
    and the exactly-once switch sit on their lines and everything else is hidden behind the tab's popovers.
    """
    # A new connection starts with the switch on, an edited one shows what it has
    if is_edit:
        is_idempotent_attrs = {}
    else:
        is_idempotent_attrs = {'checked':'checked'}

    form.fields[_producer.Field_Compression] = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={'class':Select_Class}))
    form.fields[_producer.Field_Acks] = forms.ChoiceField(required=False, widget=forms.Select())
    form.fields[_producer.Field_Is_Idempotent] = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs=is_idempotent_attrs))

    add_select(form, _producer.Field_Compression, KAFKA.COMPRESSION(), needs_initial_select=False)
    add_select(form, _producer.Field_Acks, KAFKA.ACKS(), needs_initial_select=False)

    form.fields[_producer.Field_Compression].initial = _producer.Default_Compression
    form.fields[_producer.Field_Acks].initial = _producer.Default_Acks

    for name, units in unit_fields.items():
        count, unit = split_unit(_producer.Defaults[name], units)
        form.fields[name] = forms.CharField(required=False, initial=count, widget=forms.TextInput())
        form.fields[unit_field_name(name)] = forms.ChoiceField(
            required=False, choices=_unit_choices(units), initial=unit, widget=forms.Select())

# ################################################################################################################################
# ################################################################################################################################

def get_producer_fields(params:'any_', prefix:'str'='') -> 'stranydict':
    """ The producer's fields a form submitted, typed as stored, with each count and its unit joined into the stored number.
    """
    out = {}

    for name, default in _producer.Defaults.items():
        value = params.get(prefix + name)

        if name == _producer.Field_Is_Idempotent:
            out[name] = bool(value)

        elif name in unit_fields:
            units = unit_fields[name]
            unit = params.get(prefix + unit_field_name(name))
            if unit is None:
                unit = units[0][0]
            if value:
                out[name] = join_unit(int(value), unit, units)
            else:
                out[name] = default

        else:
            if value:
                out[name] = value
            else:
                out[name] = default

    return out

# ################################################################################################################################

def fill_row(item:'any_') -> 'None':
    """ Fills in the producer's fields a listed connection does not carry yet with their defaults
    and turns each stored number into a count and a unit, in place.
    """
    for name, default in _producer.Defaults.items():
        if item.get(name) is None:
            item[name] = default

    for name, units in unit_fields.items():
        count, unit = split_unit(int(item[name]), units)
        item[name] = count
        item[unit_field_name(name)] = unit

# ################################################################################################################################
# ################################################################################################################################

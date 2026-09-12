# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an object's create and edit forms - its fields, its lines and the configuration its JavaScript reads.

# Django
from django import forms

# Zato
from zato.admin.web.alerts_tab_lines import Checkbox_On_Value, Edit_Hint, field_display, field_how_it_works, Line_Kind_Pick, \
    Line_Kind_Popover, Line_Kind_Toggle, Tab_Label, type_lines, unit_fields
from zato.admin.web.alerts_tab_picks import get_empty_html, get_pick_choices, Pick_Select_Class
from zato.common.alerting import config_map
from zato.common.alerting.object_config import Field_Prefix, get_defaults as get_storage_defaults, get_field_names, \
    Is_Active_Field, storage_name, Unit_Field_Suffix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strtuple
    any_ = any_
    anydict = anydict
    anylist = anylist
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

def form_field_name(name:'str') -> 'str':
    """ The name a field of the tab goes by on the form and in storage.
    """
    out = storage_name(name)
    return out

# ################################################################################################################################

def get_type_fields(alert_type:'str') -> 'anylist':
    """ The number and toggle fields of an alert type, in the order the rule definition lists them.
    """
    out = config_map.type_fields[alert_type]
    return out

# ################################################################################################################################

def get_unit_field_names(alert_type:'str') -> 'strlist':
    """ The unit selects the lines of an alert type name, in the order the lines do.
    """
    out:'strlist' = []

    for line in type_lines[alert_type]:
        if 'unit_field' in line:
            out.append(line['unit_field'])

    return out

# ################################################################################################################################

def get_duration_field_names(alert_type:'str') -> 'strlist':
    """ The fields of an alert type stored as seconds and edited as a count with a unit.
    """
    out:'strlist' = []

    for field in get_type_fields(alert_type):
        if field['kind'] == config_map.Kind_Duration:
            out.append(field['name'])

    return out

# ################################################################################################################################

def get_field_kinds(alert_type:'str') -> 'anydict':
    """ The kind of each field of an alert type.
    """
    out:'anydict' = {}

    for field in get_type_fields(alert_type):
        out[field['name']] = field['kind']

    return out

# ################################################################################################################################

def get_toggle_field_names(alert_type:'str') -> 'strlist':
    """ The fields of an alert type a checkbox stands for - the Active switch and the type's toggles.
    """
    out:'strlist' = [Is_Active_Field]

    for field in get_type_fields(alert_type):
        if field['kind'] in (config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle):
            out.append(field['name'])

    return out

# ################################################################################################################################

def get_field_label(name:'str') -> 'str':
    """ What a field is called where it is edited, with its unit after it when it has one.
    """
    label, unit = field_display[name]

    if unit:
        out = f'{label} ({unit})'
    else:
        out = label

    return out

# ################################################################################################################################

def get_defaults(alert_type:'str') -> 'anydict':
    """ The default value of each field of an alert type, a duration as a count and a unit.
    """
    out = get_storage_defaults(alert_type)

    for name in get_duration_field_names(alert_type):
        count, unit_name = config_map.split_duration(out[name])
        out[name] = count
        out[name + Unit_Field_Suffix] = unit_name

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_storage_field_names(alert_type:'str') -> 'strtuple':
    """ The names the tab's fields travel under between the form and the backend, the unit selects included.
    """
    names:'strlist' = []

    for name in get_field_names(alert_type):
        names.append(form_field_name(name))

    for unit_field_name in get_unit_field_names(alert_type):
        names.append(form_field_name(unit_field_name))

    out = tuple(names)
    return out

# ################################################################################################################################

def get_checkbox_field_names(alert_type:'str') -> 'strtuple':
    """ The storage names of the tab's fields a checkbox stands for.
    """
    names:'strlist' = []

    for name in get_toggle_field_names(alert_type):
        names.append(form_field_name(name))

    out = tuple(names)
    return out

# ################################################################################################################################

def pre_process_alert_item(alert_type:'str', name:'str', value:'any_') -> 'any_':
    """ One field of the tab as the backend stores it - a checkbox as a boolean, a number as an integer,
    a text without the whitespace around it.
    """
    field_kinds = get_field_kinds(alert_type)
    own_name = name[len(Field_Prefix):]

    is_number = False
    is_text = False

    if own_name in field_kinds:
        if field_kinds[own_name] in (config_map.Kind_Number, config_map.Kind_Duration):
            is_number = True
        elif field_kinds[own_name] == config_map.Kind_Text:
            is_text = True

    if name in get_checkbox_field_names(alert_type):
        out = value == Checkbox_On_Value
    elif is_number:
        out = int(value)
    elif is_text:
        out = value.strip()
    else:
        out = value

    return out

# ################################################################################################################################

def join_durations(alert_type:'str', input_dict:'anydict') -> 'None':
    """ Turns each duration's count and unit in a form's input into the seconds it is stored as, in place.
    """
    for name in get_duration_field_names(alert_type):
        count_name = form_field_name(name)
        unit_name = form_field_name(name + Unit_Field_Suffix)

        if count_name in input_dict:
            if unit_name in input_dict:
                input_dict[count_name] = config_map.join_duration(input_dict[count_name], input_dict[unit_name])
                del input_dict[unit_name]

# ################################################################################################################################

def split_durations(alert_type:'str', item:'any_') -> 'None':
    """ Turns each duration's seconds on a listed object into the count and the unit the edit form shows, in place.
    """
    for name in get_duration_field_names(alert_type):
        count_name = form_field_name(name)
        unit_name = form_field_name(name + Unit_Field_Suffix)

        if count_name in item:
            count, unit = config_map.split_duration(item[count_name])
            item[count_name] = count
            item[unit_name] = unit

    for unit_field_name in get_unit_field_names(alert_type):
        storage_unit_name = form_field_name(unit_field_name)

        if storage_unit_name not in item:
            item[storage_unit_name] = unit_fields[unit_field_name]['initial']

# ################################################################################################################################
# ################################################################################################################################

def get_pick_lines(alert_type:'str') -> 'anylist':
    """ The pick lines of an alert type, in the order the tab lists them.
    """
    out:'anylist' = []

    for line in type_lines[alert_type]:
        if line['kind'] == Line_Kind_Pick:
            out.append(line)

    return out

# ################################################################################################################################

def get_pick_field_names(alert_type:'str') -> 'strlist':
    """ The fields the pick lines of an alert type stand on.
    """
    out:'strlist' = []

    for line in get_pick_lines(alert_type):
        out.append(line['fields'][0])

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_alerts_fields(form:'any_', alert_type:'str', request:'any_') -> 'None':
    """ Adds the fields of the Alerts tab to a form.
    """
    defaults = get_defaults(alert_type)

    is_active_default = defaults[Is_Active_Field]
    is_active_name = form_field_name(Is_Active_Field)
    form.fields[is_active_name] = forms.BooleanField(required=False, initial=is_active_default, widget=forms.CheckboxInput())

    for field in get_type_fields(alert_type):
        name = field['name']
        default = defaults[name]

        if field['kind'] in (config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle):
            form_field = forms.BooleanField(required=False, initial=default, widget=forms.CheckboxInput())
        elif field['kind'] == config_map.Kind_Time_Slots:
            form_field = forms.CharField(required=False, initial=default, widget=forms.HiddenInput())
        elif field['kind'] == config_map.Kind_Text:
            form_field = forms.CharField(required=False, initial=default, widget=forms.TextInput())
        else:
            form_field = forms.IntegerField(required=False, initial=default, min_value=1, widget=forms.NumberInput())

        field_name = form_field_name(name)
        form.fields[field_name] = form_field

    for unit_field_name in get_unit_field_names(alert_type):
        unit_field = unit_fields[unit_field_name]

        if unit_field_name in defaults:
            initial = defaults[unit_field_name]
        else:
            initial = unit_field['initial']

        field_name = form_field_name(unit_field_name)
        form.fields[field_name] = forms.ChoiceField(
            required=False, choices=unit_field['choices'], initial=initial, widget=forms.Select())

    for line in get_pick_lines(alert_type):
        field_name = form_field_name(line['fields'][0])
        choices = get_pick_choices(request, line)
        widget = forms.Select(attrs={'class': Pick_Select_Class})
        form.fields[field_name] = forms.ChoiceField(required=False, choices=choices, widget=widget)

# ################################################################################################################################

def get_alerts_tab_context(form:'any_', alert_type:'str') -> 'anydict':
    """ What the tab's template needs for one form - the sections of lines and the hidden fields under them.
    """
    sections:'anylist' = []
    section_by_label:'anydict' = {}
    hidden_fields:'anylist' = []

    for line in type_lines[alert_type]:

        section_label = line['section']

        if section_label not in section_by_label:
            section = {'label': section_label, 'lines': []}
            section_by_label[section_label] = section
            sections.append(section)

        row = {
            'name': line['name'],
            'kind': line['kind'],
            'label': line['label'],
            'is_active_line': line['fields'][0] == Is_Active_Field,
        }

        if line['kind'] in (Line_Kind_Toggle, Line_Kind_Pick):
            field_name = form_field_name(line['fields'][0])
            row['field'] = form[field_name]

            if line['kind'] == Line_Kind_Pick:
                option_count = len(row['field'].field.choices)
                has_options = option_count > 1
                row['has_options'] = has_options
                row['empty_html'] = get_empty_html(line)
        else:
            for field_name in line['fields']:
                hidden_field_name = form_field_name(field_name)
                hidden_fields.append(form[hidden_field_name])

            if 'unit_field' in line:
                unit_field_name = form_field_name(line['unit_field'])
                hidden_fields.append(form[unit_field_name])

        section_by_label[section_label]['lines'].append(row)

    out = {
        'tab_label': Tab_Label,
        'sections': sections,
        'hidden_fields': hidden_fields,
        'edit_hint': Edit_Hint,
    }

    return out

# ################################################################################################################################

def get_alerts_tab_config(alert_type:'str') -> 'anydict':
    """ What the tab's JavaScript needs to know about a page's alert fields.
    """
    field_kinds = get_field_kinds(alert_type)

    field_labels:'anydict' = {}
    how_it_works_by_field:'anydict' = {Is_Active_Field: field_how_it_works[Is_Active_Field]}

    for line in get_pick_lines(alert_type):
        pick_field_name = line['fields'][0]
        how_it_works_by_field[pick_field_name] = field_how_it_works[pick_field_name]

    for field in get_type_fields(alert_type):
        name = field['name']
        field_labels[name] = get_field_label(name)
        how_it_works_by_field[name] = field_how_it_works[name]

    for unit_field_name in get_unit_field_names(alert_type):
        how_it_works_by_field[unit_field_name] = field_how_it_works[unit_field_name]

    lines:'anylist' = []

    for line in type_lines[alert_type]:

        entry = {
            'name': line['name'],
            'kind': line['kind'],
            'label': line['label'],
            'fields': line['fields'],
            'how_it_works': line['how_it_works'],
        }

        if line['kind'] == Line_Kind_Popover:
            entry['title'] = line['title']
            entry['summary'] = line['summary']
            entry['rows'] = line['rows']

            if 'unit_field' in line:
                entry['unit_field'] = line['unit_field']

            if 'slots_field' in line:
                entry['slots_field'] = line['slots_field']

            if 'text_fields' in line:
                entry['text_fields'] = line['text_fields']

            if 'off_field' in line:
                entry['off_field'] = line['off_field']
                entry['summary_off'] = line['summary_off']

        if line['kind'] == Line_Kind_Pick:
            entry['field'] = line['fields'][0]
            entry['live_type'] = line['live_type']

        if 'depends_on' in line:
            entry['depends_on'] = line['depends_on']

        lines.append(entry)

    duration_units:'anylist' = []

    for unit_name, unit_seconds in config_map.Duration_Units:
        duration_units.append({'name': unit_name, 'seconds': unit_seconds})

    storage_field_names = list(get_storage_field_names(alert_type))
    checkbox_field_names = list(get_checkbox_field_names(alert_type))

    out = {
        'alert_type': alert_type,
        'tab_label': Tab_Label,
        'field_prefix': Field_Prefix,
        'is_active_field': Is_Active_Field,
        'pick_fields': get_pick_field_names(alert_type),
        'lines': lines,
        'field_kinds': field_kinds,
        'toggle_kinds': [config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle],
        'field_labels': field_labels,
        'field_how_it_works': how_it_works_by_field,
        'edit_hint': Edit_Hint,
        'slots_kind': config_map.Kind_Time_Slots,
        'duration_kind': config_map.Kind_Duration,
        'text_kind': config_map.Kind_Text,
        'duration_units': duration_units,
        'storage_field_names': storage_field_names,
        'checkbox_field_names': checkbox_field_names,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

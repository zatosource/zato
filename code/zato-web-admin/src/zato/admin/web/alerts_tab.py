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
    Line_Kind_Popover, Line_Kind_Toggle, Tab_Label, type_lines as shared_type_lines, unit_fields
from zato.admin.web.alerts_tab_lines_llm import llm_lines
from zato.admin.web.alerts_tab_lines_mcp import mcp_lines
from zato.admin.web.alerts_tab_lines_queue import add_queue_lines
from zato.admin.web.alerts_tab_picks import get_empty_html, get_pick_choices, Pick_Select_Class
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_llm, alert_type_mcp, Field_Prefix, \
    get_defaults as get_storage_defaults, get_field_kinds, get_field_names, Is_Active_Field, storage_name, Unit_Field_Suffix
from zato.common.alerting.time_slots import Slot_Is_On, Slot_Seconds, Slot_Time_From, Slot_Time_To

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

# The lines of every alert type - the ones alerts_tab_lines.py builds, the LLM and MCP ones built from them
# in modules of their own and the queue delivery ones the outgoing connections carry on top of their own
type_lines:'anydict' = dict(shared_type_lines)
type_lines[alert_type_llm] = llm_lines()
type_lines[alert_type_mcp] = mcp_lines()
add_queue_lines(type_lines)

# The kinds of field stored as one number and edited as a count with a unit select - a duration's seconds,
# an amount's ones and a size's bytes - each with what splits the stored number for the form and what joins the form's two back
_unit_kinds:'anydict' = {
    config_map.Kind_Duration: (config_map.split_duration, config_map.join_duration),
    config_map.Kind_Amount: (config_map.split_amount, config_map.join_amount),
    config_map.Kind_Size: (config_map.split_size, config_map.join_size),
}

# The kinds of field that accept a fraction - seconds such as 7.5, amounts such as 2.5 millions and sizes such as
# 1.5 gigabytes - and the step their number inputs carry so the browser takes the fraction
fractional_kinds = [config_map.Kind_Seconds, config_map.Kind_Amount, config_map.Kind_Size]
Fractional_Step = 'any'

# ################################################################################################################################
# ################################################################################################################################

def _same_name(name:'str') -> 'str':
    """ The name a field of the page's own form goes by on it - its own.
    """
    out = name
    return out

# ################################################################################################################################

def get_type_fields(alert_type:'str') -> 'anylist':
    """ The number and toggle fields of an alert type, in the order the rule definition lists them.
    """
    out = config_map.type_fields[alert_type]
    return out

# ################################################################################################################################

def is_page_line(line:'anydict') -> 'bool':
    """ Whether a line edits fields of the page's own form rather than alert settings.
    """
    out = 'page_fields' in line
    return out

# ################################################################################################################################

def get_page_lines(alert_type:'str') -> 'anylist':
    """ The lines of an alert type that edit fields of the page's own form, in the order the tab lists them.
    """
    out:'anylist' = []

    for line in type_lines[alert_type]:
        if is_page_line(line):
            out.append(line)

    return out

# ################################################################################################################################

def get_line_unit_field_names(line:'anydict') -> 'strlist':
    """ The unit selects of one line - the ones its fields carry of their own, then the one after its last number.
    """
    out:'strlist' = []

    if 'field_units' in line:
        out.extend(line['field_units'].values())

    if 'unit_field' in line:
        out.append(line['unit_field'])

    return out

# ################################################################################################################################

def get_page_field_names(alert_type:'str') -> 'strlist':
    """ The fields of the page's own form the tab edits, the unit selects included.
    """
    out:'strlist' = []

    for line in get_page_lines(alert_type):
        out.extend(line['fields'])
        out.extend(get_line_unit_field_names(line))

    return out

# ################################################################################################################################

def get_unit_field_names(alert_type:'str') -> 'strlist':
    """ The unit selects the lines of an alert type add to the form, in the order the lines do -
    a page line's unit select is the page's own.
    """
    out:'strlist' = []

    for line in type_lines[alert_type]:
        if is_page_line(line):
            continue

        out.extend(get_line_unit_field_names(line))

    return out

# ################################################################################################################################

def get_unit_kind_fields(alert_type:'str') -> 'anylist':
    """ The fields of an alert type stored as one number and edited as a count with a unit - its durations and its amounts.
    """
    out:'anylist' = []

    for field in get_type_fields(alert_type):
        if field['kind'] in _unit_kinds:
            out.append(field)

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

def get_form_defaults(alert_type:'str') -> 'anydict':
    """ The default value of each field of an alert type as the form shows it, a duration and an amount as a count and a unit.
    """
    out = get_storage_defaults(alert_type)

    for field in get_unit_kind_fields(alert_type):
        name = field['name']
        split, _ = _unit_kinds[field['kind']]
        count, unit_name = split(out[name])
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
        names.append(storage_name(name))

    for unit_field_name in get_unit_field_names(alert_type):
        names.append(storage_name(unit_field_name))

    out = tuple(names)
    return out

# ################################################################################################################################

def get_checkbox_field_names(alert_type:'str') -> 'strtuple':
    """ The storage names of the tab's fields a checkbox stands for.
    """
    names:'strlist' = []

    for name in get_toggle_field_names(alert_type):
        names.append(storage_name(name))

    out = tuple(names)
    return out

# ################################################################################################################################

def pre_process_alert_item(alert_type:'str', name:'str', value:'any_') -> 'any_':
    """ One field of the tab as the backend stores it - a checkbox as a boolean, a number as an integer,
    a fractional one as a float that reads as an integer when it is whole, a text without the whitespace around it.
    """
    field_kinds = get_field_kinds(alert_type)
    own_name = name[len(Field_Prefix):]

    is_number = False
    is_fraction = False
    is_text = False

    if own_name in field_kinds:
        if field_kinds[own_name] in (config_map.Kind_Number, config_map.Kind_Duration):
            is_number = True
        elif field_kinds[own_name] in fractional_kinds:
            is_fraction = True
        elif field_kinds[own_name] == config_map.Kind_Text:
            is_text = True

    if name in get_checkbox_field_names(alert_type):
        out = value == Checkbox_On_Value
    elif is_number:
        out = int(value)
    elif is_fraction:
        out = config_map.to_screen_value(float(value), False)
    elif is_text:
        out = value.strip()
    else:
        out = value

    return out

# ################################################################################################################################

def join_unit_fields(alert_type:'str', input_dict:'anydict') -> 'None':
    """ Turns each duration's and each amount's count and unit in a form's input into the one number it is stored as,
    in place - a duration's seconds, an amount's ones.
    """
    for field in get_unit_kind_fields(alert_type):
        count_name = storage_name(field['name'])
        unit_name = storage_name(field['name'] + Unit_Field_Suffix)
        _, join = _unit_kinds[field['kind']]

        if count_name in input_dict:
            if unit_name in input_dict:
                input_dict[count_name] = join(input_dict[count_name], input_dict[unit_name])
                del input_dict[unit_name]

# ################################################################################################################################

def split_unit_fields(alert_type:'str', item:'any_') -> 'None':
    """ Turns each duration's seconds and each amount's ones on a listed object into the count and the unit
    the edit form shows, in place.
    """
    for field in get_unit_kind_fields(alert_type):
        count_name = storage_name(field['name'])
        unit_name = storage_name(field['name'] + Unit_Field_Suffix)
        split, _ = _unit_kinds[field['kind']]

        if count_name in item:
            count, unit = split(item[count_name])
            item[count_name] = count
            item[unit_name] = unit

    for unit_field_name in get_unit_field_names(alert_type):
        storage_unit_name = storage_name(unit_field_name)

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
    defaults = get_form_defaults(alert_type)

    is_active_default = defaults[Is_Active_Field]
    is_active_name = storage_name(Is_Active_Field)
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
        elif field['kind'] in fractional_kinds:
            form_field = forms.FloatField(
                required=False, initial=default, widget=forms.NumberInput(attrs={'step': Fractional_Step}))
        else:
            form_field = forms.IntegerField(required=False, initial=default, min_value=1, widget=forms.NumberInput())

        field_name = storage_name(name)
        form.fields[field_name] = form_field

    for unit_field_name in get_unit_field_names(alert_type):
        unit_field = unit_fields[unit_field_name]

        if unit_field_name in defaults:
            initial = defaults[unit_field_name]
        else:
            initial = unit_field['initial']

        field_name = storage_name(unit_field_name)
        form.fields[field_name] = forms.ChoiceField(
            required=False, choices=unit_field['choices'], initial=initial, widget=forms.Select())

    for line in get_pick_lines(alert_type):
        field_name = storage_name(line['fields'][0])
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
            'is_always_on': 'always_on' in line,
        }

        # A page line's fields go by their own names on the form, everyone else's by their alert names
        if is_page_line(line):
            to_form_name = _same_name
        else:
            to_form_name = storage_name

        if line['kind'] in (Line_Kind_Toggle, Line_Kind_Pick):
            field_name = to_form_name(line['fields'][0])
            row['field'] = form[field_name]

            if line['kind'] == Line_Kind_Pick:
                option_count = len(row['field'].field.choices)
                has_options = option_count > 1
                row['has_options'] = has_options
                row['empty_html'] = get_empty_html(line)
        else:
            for field_name in line['fields']:
                hidden_field_name = to_form_name(field_name)
                hidden_fields.append(form[hidden_field_name])

            for unit_field_name in get_line_unit_field_names(line):
                hidden_fields.append(form[to_form_name(unit_field_name)])

        section_by_label[section_label]['lines'].append(row)

    # Every field of the tab in storage order - a page that builds its own lines, e.g. a wizard's
    # Alerts popup, renders them all hidden and mirrors the ones it shows
    fields:'anylist' = []

    for storage_field_name in get_storage_field_names(alert_type):
        fields.append(form[storage_field_name])

    out = {
        'tab_label': Tab_Label,
        'sections': sections,
        'hidden_fields': hidden_fields,
        'fields': fields,
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

    # The fields of the page's own form the tab edits are counts, each with the label and the help of its own
    page_field_names = get_page_field_names(alert_type)

    for line in get_page_lines(alert_type):
        for name in line['fields']:
            field_kinds[name] = config_map.Kind_Number
            field_labels[name] = get_field_label(name)

    for name in page_field_names:
        how_it_works_by_field[name] = field_how_it_works[name]

    lines:'anylist' = []

    for line in type_lines[alert_type]:

        entry = {
            'name': line['name'],
            'section': line['section'],
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

            if 'field_units' in line:
                entry['field_units'] = line['field_units']

            if 'slots_field' in line:
                entry['slots_field'] = line['slots_field']

            if 'text_fields' in line:
                entry['text_fields'] = line['text_fields']

            if 'off_field' in line:
                entry['off_field'] = line['off_field']
                entry['summary_off'] = line['summary_off']

            if 'summary_empty' in line:
                entry['summary_empty'] = line['summary_empty']

        if line['kind'] == Line_Kind_Pick:
            entry['field'] = line['fields'][0]
            entry['live_type'] = line['live_type']
            entry['empty_html'] = get_empty_html(line)

        if 'depends_on' in line:
            entry['depends_on'] = line['depends_on']

        lines.append(entry)

    duration_units:'anylist' = []

    for unit_name, unit_seconds in config_map.Duration_Units:
        duration_units.append({'name': unit_name, 'seconds': unit_seconds})

    storage_field_names = list(get_storage_field_names(alert_type))
    checkbox_field_names = list(get_checkbox_field_names(alert_type))

    # The kinds of line the tab lists and the keys of one time slot, so the JavaScript never spells them itself
    line_kinds = {
        'popover': Line_Kind_Popover,
        'toggle': Line_Kind_Toggle,
        'pick': Line_Kind_Pick,
    }

    slot_keys = {
        'time_from': Slot_Time_From,
        'time_to': Slot_Time_To,
        'is_on': Slot_Is_On,
        'seconds': Slot_Seconds,
    }

    out = {
        'alert_type': alert_type,
        'tab_label': Tab_Label,
        'field_prefix': Field_Prefix,
        'is_active_field': Is_Active_Field,
        'pick_fields': get_pick_field_names(alert_type),
        'page_fields': page_field_names,
        'lines': lines,
        'field_kinds': field_kinds,
        'toggle_kinds': [config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle],
        'field_labels': field_labels,
        'field_how_it_works': how_it_works_by_field,
        'edit_hint': Edit_Hint,
        'slots_kind': config_map.Kind_Time_Slots,
        'duration_kind': config_map.Kind_Duration,
        'text_kind': config_map.Kind_Text,
        'fractional_kinds': fractional_kinds,
        'fractional_step': Fractional_Step,
        'duration_units': duration_units,
        'storage_field_names': storage_field_names,
        'checkbox_field_names': checkbox_field_names,
        'line_kinds': line_kinds,
        'slot_keys': slot_keys,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

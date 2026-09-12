# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The reusable Alerts tab of an object's create and edit forms - the per-object alert
# settings that the dedicated alert rules screen used to hold for a whole connection type.
#
# The tab is written as decision lines (static/js/common/decision-lines.js), one question
# per line. A line's answer is either a switch, a summary link opening a popover micro-form
# (static/js/common/micro-forms.js) with the numbers behind it, or a select picking a
# connection. The rendered Django fields stay the single source of every value - the numbers
# sit hidden under the lines and the popovers read and write them, the switches and the
# selects are the lines' own answers.
#
# A page names its alert type and gets the form fields, the lines the template renders
# and the configuration the tab's JavaScript reads, all from the one field definition
# that config_map holds and zato.common.alerting.object_config shares with enmasse
# and the server - the names, the kinds, the defaults and the storage names are theirs.
#
# The lines themselves are in alerts_tab_lines and the connection selects in alerts_tab_picks,
# both read through this module.

# Django
from django import forms

# Zato
from zato.admin.web.alerts_tab_lines import Active_Label, Arrival_Overdue_Unit_Default, Arrival_Overdue_Unit_Field, \
    Checkbox_On_Value, Edit_Hint, field_display, field_how_it_works, Line_Kind_Pick, Line_Kind_Popover, Line_Kind_Toggle, Section_Callers, Section_Core, \
    Section_Failures, Section_Thresholds, Section_Traffic, Silence_Slots_Field, Silence_Window_Unit_Field, Tab_Label, \
    type_lines, unit_fields, Window_Unit_Field
from zato.admin.web.alerts_tab_picks import Email_Empty_Text, get_empty_html, get_pick_choices, Live_Type_Email_Connection, \
    Live_Type_LLM_Connection, LLM_Empty_Text, Pick_Select_Class
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_channels, alert_type_file_transfer, Field_Prefix, \
    get_defaults as get_storage_defaults, get_field_names, Is_Active_Field, storage_name, Unit_Field_Suffix

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

# The names the pages and the tests reach for through this module
Active_Label = Active_Label
alert_type_channels = alert_type_channels
alert_type_file_transfer = alert_type_file_transfer
Arrival_Overdue_Unit_Default = Arrival_Overdue_Unit_Default
Arrival_Overdue_Unit_Field = Arrival_Overdue_Unit_Field
Checkbox_On_Value = Checkbox_On_Value
Edit_Hint = Edit_Hint
Email_Empty_Text = Email_Empty_Text
Field_Prefix = Field_Prefix
field_display = field_display
field_how_it_works = field_how_it_works
Line_Kind_Pick = Line_Kind_Pick
Line_Kind_Popover = Line_Kind_Popover
Line_Kind_Toggle = Line_Kind_Toggle
Live_Type_Email_Connection = Live_Type_Email_Connection
Live_Type_LLM_Connection = Live_Type_LLM_Connection
LLM_Empty_Text = LLM_Empty_Text
Pick_Select_Class = Pick_Select_Class
Section_Callers = Section_Callers
Section_Core = Section_Core
Section_Failures = Section_Failures
Section_Thresholds = Section_Thresholds
Section_Traffic = Section_Traffic
Silence_Slots_Field = Silence_Slots_Field
Silence_Window_Unit_Field = Silence_Window_Unit_Field
Tab_Label = Tab_Label
type_lines = type_lines
Window_Unit_Field = Window_Unit_Field

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
    """ The kind of each field of an alert type - a number or a toggle.
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
    """ The default value of each field of an alert type, read from the seeded default rules
    so that the tab and the rules never disagree about what a new object starts with -
    except that a duration is a count and a unit on the tab, not a number of seconds.
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
    """ The names the tab's fields travel under between the form and the backend - every field
    of the type under the alert_ prefix, the unit selects included, in the order the tab lists them.
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
    """ One field of the tab as the backend stores it - a checkbox arrives as 'on' when checked and as nothing
    otherwise and becomes a boolean, a number arrives as text and becomes an integer, a unit and the email
    and LLM connections travel as the strings they are.
    """
    if name in get_checkbox_field_names(alert_type):
        out = value == Checkbox_On_Value
        return out

    field_kinds = get_field_kinds(alert_type)
    own_name = name[len(Field_Prefix):]

    if own_name in field_kinds and field_kinds[own_name] in (config_map.Kind_Number, config_map.Kind_Duration):
        out = int(value)
        return out

    return value

# ################################################################################################################################

def join_durations(alert_type:'str', input_dict:'anydict') -> 'None':
    """ Turns each duration's count and unit in a form's input into the seconds it is stored as, in place,
    and takes the unit out - it is not stored, the seconds say what it was.
    """
    for name in get_duration_field_names(alert_type):
        count_name = form_field_name(name)
        unit_name = form_field_name(name + Unit_Field_Suffix)

        if count_name in input_dict and unit_name in input_dict:
            input_dict[count_name] = config_map.join_duration(input_dict[count_name], input_dict[unit_name])
            del input_dict[unit_name]

# ################################################################################################################################

def split_durations(alert_type:'str', item:'any_') -> 'None':
    """ Turns each duration's seconds on a listed object into the count and the unit the edit form shows,
    in place, and gives a unit select the object does not carry a value for its default.
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
    """ The fields the pick lines of an alert type stand on - the email and the LLM connection.
    """
    out:'strlist' = []

    for line in get_pick_lines(alert_type):
        out.append(line['fields'][0])

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_alerts_fields(form:'forms.Form', alert_type:'str', req:'any_') -> 'None':
    """ Adds the fields of the Alerts tab to a form - the active toggle first, then the type's
    own numbers and toggles, the unit selects its lines name, then the connection selects of the pick lines.
    """
    defaults = get_defaults(alert_type)

    is_active_default = defaults[Is_Active_Field]
    form.fields[form_field_name(Is_Active_Field)] = forms.BooleanField(
        required=False, initial=is_active_default, widget=forms.CheckboxInput())

    for field in get_type_fields(alert_type):
        name = field['name']
        default = defaults[name]

        if field['kind'] in (config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle):
            form_field = forms.BooleanField(required=False, initial=default, widget=forms.CheckboxInput())
        elif field['kind'] == config_map.Kind_Time_Slots:
            form_field = forms.CharField(required=False, initial=default, widget=forms.HiddenInput())
        else:
            form_field = forms.IntegerField(required=False, initial=default, min_value=1, widget=forms.NumberInput())

        form.fields[form_field_name(name)] = form_field

    for unit_field_name in get_unit_field_names(alert_type):
        unit_field = unit_fields[unit_field_name]

        # A duration's unit starts where the seeded rules put it, any other unit where its own table says
        if unit_field_name in defaults:
            initial = defaults[unit_field_name]
        else:
            initial = unit_field['initial']

        form.fields[form_field_name(unit_field_name)] = forms.ChoiceField(
            required=False, choices=unit_field['choices'], initial=initial, widget=forms.Select())

    for line in get_pick_lines(alert_type):
        form.fields[form_field_name(line['fields'][0])] = forms.ChoiceField(
            required=False, choices=get_pick_choices(req, line), widget=forms.Select(attrs={'class': Pick_Select_Class}))

# ################################################################################################################################

def get_alerts_tab_context(form:'forms.Form', alert_type:'str') -> 'anydict':
    """ Everything the tab's template needs for one form - the sections of lines and the fields
    that sit hidden under the lines for the popovers and the panel to read and write.
    """
    sections:'anylist' = []
    section_by_label:'anydict' = {}
    hidden_fields:'anylist' = []

    for line in type_lines[alert_type]:

        section_label = line['section']

        # Sections come in the order their first line does
        if section_label not in section_by_label:
            section = {'label': section_label, 'lines': []}
            section_by_label[section_label] = section
            sections.append(section)

        # The Active line is the one that stays lit when the switch is off and the rest is dimmed
        row = {
            'name': line['name'],
            'kind': line['kind'],
            'label': line['label'],
            'is_active_line': line['fields'][0] == Is_Active_Field,
        }

        # A switch and a select are answered on the line itself, a popover line
        # is answered in its popover and its fields wait hidden under the lines.
        if line['kind'] in (Line_Kind_Toggle, Line_Kind_Pick):
            row['field'] = form[form_field_name(line['fields'][0])]

            # A select with nothing to list is swapped for the sentence with the create links until there is
            if line['kind'] == Line_Kind_Pick:
                row['has_options'] = len(row['field'].field.choices) > 1
                row['empty_html'] = get_empty_html(line)
        else:
            for field_name in line['fields']:
                hidden_fields.append(form[form_field_name(field_name)])

            # The unit select of a line waits hidden alongside its number
            if 'unit_field' in line:
                hidden_fields.append(form[form_field_name(line['unit_field'])])

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
    """ What the tab's JavaScript needs to know about a page's alert fields - the lines with their
    fields and summaries, what each field is called and what it means, how the pick lines encode
    their values and where their create entries lead, and which hidden cells of a row the fields travel in.
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

            if 'unit_field' in line:
                entry['unit_field'] = line['unit_field']

            if 'rows' in line:
                entry['rows'] = line['rows']

            if 'slots_field' in line:
                entry['slots_field'] = line['slots_field']

            if 'off_field' in line:
                entry['off_field'] = line['off_field']
                entry['summary_off'] = line['summary_off']

        if line['kind'] == Line_Kind_Pick:
            entry['field'] = line['fields'][0]
            entry['live_type'] = line['live_type']

        if 'depends_on' in line:
            entry['depends_on'] = line['depends_on']

        lines.append(entry)

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
        'duration_units': config_map.Duration_Units,
        'storage_field_names': list(get_storage_field_names(alert_type)),
        'checkbox_field_names': list(get_checkbox_field_names(alert_type)),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

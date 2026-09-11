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
# (static/js/common/micro-forms.js) with the numbers behind it, or a chip opening a panel
# to pick from. The
# rendered Django fields stay the single source of every value - the numbers and the
# email select sit hidden under the lines and the popovers read and write them.
#
# A page names its alert type and gets the form fields, the lines the template renders
# and the configuration the tab's JavaScript reads, all from the one field definition
# that config_map holds and zato.common.alerting.object_config shares with enmasse
# and the server - the names, the kinds, the defaults and the storage names are theirs.

# Django
from django import forms
from django.urls import reverse

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_file_transfer, Email_Conn_Separator, Email_Conn_Type_IMAP, \
    Email_Conn_Type_SMTP, Email_Connection_Field, encode_email_connection, field_display as shared_field_display, \
    field_help, Field_Prefix, get_defaults as get_storage_defaults, get_field_names, Is_Active_Field, storage_name, \
    Unit_Field_Suffix
from zato.common.api import EMAIL
from zato.common.defaults import default_cluster_id

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

# The units a time is given in - a select that sits right after the number in its popover.
# An option's value is the noun in the singular and its label the plural, which is how
# the summary reads "1 hour" and "2 hours" off the select.
duration_unit_choices = []

for _unit_name, _ignored_seconds in config_map.Duration_Units:
    duration_unit_choices.append((_unit_name, _unit_name + 's'))

# The unit of the time a file may fail to arrive for - a number of its own with a unit the tab
# keeps next to it, stored with the number so that the edit form reads the way it was saved.
Arrival_Overdue_Unit_Field = 'arrival_overdue' + Unit_Field_Suffix
Arrival_Overdue_Unit_Default = 'hour'

# The unit of the window the failure counts are measured over - a duration field's unit select
# is named after the field and its default comes from the seeded rules with the count. The unit
# is not stored, the window is a number of seconds in storage and is split back on the way out.
Window_Unit_Field = config_map.Window_Field_Name + Unit_Field_Suffix

# The unit selects of the tab, by name - what each offers and what a new object starts with
unit_fields = {
    Arrival_Overdue_Unit_Field: {'choices': duration_unit_choices, 'initial': Arrival_Overdue_Unit_Default},
    Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
}

# What the tab is called in the tab strip
Tab_Label = 'Alerts'

# What the first line of the tab, the one switching the rest on and off, is called
Active_Label = 'Active'

# What the link opening a line's popover says beside its summary
Edit_Hint = 'Click to edit'

# What a checkbox arrives as from the browser when it is checked
Checkbox_On_Value = 'on'

# ################################################################################################################################
# ################################################################################################################################

# The kinds a line of the tab can be of - a summary link opening a popover with the
# numbers behind it, a switch answered on the spot, or a chip opening a panel to pick from.
Line_Kind_Popover = 'popover'
Line_Kind_Toggle = 'toggle'
Line_Kind_Email = 'email'

# ################################################################################################################################
# ################################################################################################################################

# The email connection select - what an empty group says and what the entry that opens the create form is named.
Email_No_Selection_Value = ''
Email_No_Selection_Label = 'Select a connection'
Email_None_Value = 'zato-none'
Email_None_Label = '(None)'
Email_Create_New_Value = 'zato-create-new'
Email_Create_New_Label = 'Add new ...'

# What the panel picking a connection is called and what a picked row says of itself
Email_Panel_Title = 'Email connection'
Email_Remove_Label = 'click to remove'

# The option groups of the select, in the order they are shown, each with the service listing its connections
_email_groups = [
    {'kind': Email_Conn_Type_SMTP, 'label': 'SMTP', 'url_name': 'email-smtp', 'service': 'zato.email.smtp.get-list'},
    {'kind': Email_Conn_Type_IMAP, 'label': 'Microsoft 365', 'url_name': 'email-imap', 'service': 'zato.email.imap.get-list'},
]

# ################################################################################################################################
# ################################################################################################################################

# What a field is called in its popover, where the shared label reads as a column header rather than a question
_popover_labels = {
    'window':          'In the last',
    'arrival_overdue': 'Alert after',
}

# What each field is called where it is edited and the unit its value is in
field_display = dict(shared_field_display)

for _popover_name, _popover_label in _popover_labels.items():
    _ignored_label, _popover_unit = shared_field_display[_popover_name]
    field_display[_popover_name] = (_popover_label, _popover_unit)

# What each field means, shown by the how-it-works badge of a popover - the shared texts and the unit selects' own
field_how_it_works = dict(field_help)
field_how_it_works[Window_Unit_Field] = 'Whether the window is in minutes, hours or days.'
field_how_it_works[Arrival_Overdue_Unit_Field] = 'Whether the time a file may fail to arrive for is in minutes, hours or days.'

# ################################################################################################################################
# ################################################################################################################################

# The sections the lines of a tab are grouped under - the core settings first,
# the switches and the email connection, then the thresholds that raise an alert.
Section_Core = 'Core settings'
Section_Thresholds = 'Thresholds'

# The lines of the tab for each alert type, in the order they are read. A line names the
# question, the fields answering it and, for a popover line, the title of its micro-form and
# the sentence its summary link reads as - `{field}` is the field's value,
# `{field|singular|plural}` the value with the right one of the two nouns after it and
# `{unit_field@count_field}` the count with the unit select's noun after it, in the singular
# or the plural as the count says. A popover line with a `unit_field` shows that select
# right after the last of its numbers.
# The Active line is a toggle like any other, only it is the one that dims the rest when off.
type_lines = {
    alert_type_file_transfer: [
        {
            'name': 'active',
            'section': Section_Core,
            'kind': Line_Kind_Toggle,
            'label': Active_Label,
            'fields': [Is_Active_Field],
            'how_it_works': field_how_it_works[Is_Active_Field],
        },
        {
            'name': 'use_llm',
            'section': Section_Core,
            'kind': Line_Kind_Toggle,
            'label': 'Use LLM',
            'fields': ['use_llm'],
            'how_it_works': field_how_it_works['use_llm'],
        },
        {
            'name': 'test_transfers',
            'section': Section_Core,
            'kind': Line_Kind_Toggle,
            'label': 'Test transfers',
            'fields': ['test_transfers'],
            'how_it_works': field_how_it_works['test_transfers'],
        },
        {
            'name': 'email',
            'section': Section_Core,
            'kind': Line_Kind_Email,
            'label': 'Email connection',
            'title': Email_Panel_Title,
            'fields': [Email_Connection_Field],
            'how_it_works': field_how_it_works[Email_Connection_Field],
        },
        {
            'name': 'failures_in_a_row',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Failures in a row',
            'title': 'Failures in a row',
            'fields': ['consecutive_failures'],
            'summary': 'Alert after {consecutive_failures|failure|failures} in a row',
            'how_it_works': 'How many transfers may fail one after another before an alert is raised.',
        },
        {
            'name': 'failures_over_time',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Failures over time',
            'title': 'Failures over time',
            'fields': ['warning_failures', 'error_failures', 'window'],
            'unit_field': Window_Unit_Field,
            'summary': 'Warning at {warning_failures|failure|failures}, error at {error_failures}, ' + \
                f'in the last {{{Window_Unit_Field}@window}}',
            'how_it_works': 'How many failures in the window raise a warning, how many count as errors ' + \
                'and how long the window is, in minutes, hours or days.',
        },
        {
            'name': 'overdue_files',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Overdue files',
            'title': 'Overdue files',
            'fields': ['arrival_overdue'],
            'unit_field': Arrival_Overdue_Unit_Field,
            'summary': f'Alert after {{{Arrival_Overdue_Unit_Field}@arrival_overdue}} without a file',
            'how_it_works': 'How long a file may fail to arrive, in minutes, hours or days, before an alert is raised.',
        },
    ],
}

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
    connection travel as the strings they are.
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

def _get_email_connection_names(req:'any_', group:'anydict') -> 'strlist':
    """ The names of the email connections of one group - every SMTP connection there is,
    and among the IMAP ones only those of the Microsoft 365 kind, the only ones that can send.
    """
    out:'strlist' = []

    response = req.zato.client.invoke(group['service'], {'cluster_id': req.zato.cluster_id})

    for item in response:

        if group['kind'] == Email_Conn_Type_IMAP:
            if item.server_type != EMAIL.IMAP.ServerType.Microsoft365:
                continue

        out.append(item.name)

    return out

# ################################################################################################################################

def get_email_connection_choices(req:'any_') -> 'anylist':
    """ The grouped choices of the email connection select - one group per kind of connection,
    each listing its connections or saying that there are none, and each ending with the entry
    that opens the page where a new one is created.
    """
    out:'anylist' = [(Email_No_Selection_Value, Email_No_Selection_Label)]

    for group in _email_groups:
        kind = group['kind']
        options:'anylist' = []

        names = _get_email_connection_names(req, group)

        for name in names:
            value = encode_email_connection(kind, name)
            options.append((value, name))

        # An empty group says so instead of collapsing to only the create entry,
        # so that a reader can tell there are no such connections at a glance.
        if not names:
            options.append((encode_email_connection(kind, Email_None_Value), Email_None_Label))

        options.append((encode_email_connection(kind, Email_Create_New_Value), Email_Create_New_Label))

        out.append((group['label'], options))

    return out

# ################################################################################################################################

def get_email_groups() -> 'anylist':
    """ The groups of the email select as the tab's JavaScript needs them - each kind with its label
    and the page its create entry takes the user to, the kind's own page with its create form open.
    """
    out:'anylist' = []

    for group in _email_groups:
        url = reverse(group['url_name'])

        out.append({
            'kind': group['kind'],
            'label': group['label'],
            'create_url': f'{url}?cluster={default_cluster_id}&create=1',
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

class EmailConnectionSelect(forms.Select):
    """ The email connection select - the entry saying a group has no connections is there to be read, not chosen.
    """
    def create_option(self, name:'str', value:'any_', label:'any_', selected:'any_', index:'any_',
        subindex:'any_'=None, attrs:'any_'=None) -> 'anydict':

        out = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        if str(value).endswith(Email_Conn_Separator + Email_None_Value):
            out['attrs']['disabled'] = True

        return out

# ################################################################################################################################

def add_alerts_fields(form:'forms.Form', alert_type:'str', req:'any_') -> 'None':
    """ Adds the fields of the Alerts tab to a form - the active toggle first, then the type's
    own numbers and toggles, the unit selects its lines name, then the email connection select.
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

    form.fields[form_field_name(Email_Connection_Field)] = forms.ChoiceField(
        required=False, choices=get_email_connection_choices(req), widget=EmailConnectionSelect())

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

        # A switch is answered on the line itself, everything else is answered
        # in a popover or a panel and its fields wait hidden under the lines.
        if line['kind'] == Line_Kind_Toggle:
            row['field'] = form[form_field_name(line['fields'][0])]
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
    fields and summaries, what each field is called and what it means, how the email select encodes
    its values and where its create entries lead, and which hidden cells of a row the fields travel in.
    """
    field_kinds = get_field_kinds(alert_type)

    field_labels:'anydict' = {}
    how_it_works_by_field:'anydict' = {Is_Active_Field: field_how_it_works[Is_Active_Field], Email_Connection_Field: field_how_it_works[Email_Connection_Field]}

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

        if line['kind'] == Line_Kind_Email:
            entry['title'] = line['title']

        lines.append(entry)

    out = {
        'alert_type': alert_type,
        'tab_label': Tab_Label,
        'field_prefix': Field_Prefix,
        'is_active_field': Is_Active_Field,
        'email_field': Email_Connection_Field,
        'lines': lines,
        'field_kinds': field_kinds,
        'toggle_kinds': [config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle],
        'field_labels': field_labels,
        'field_how_it_works': how_it_works_by_field,
        'edit_hint': Edit_Hint,
        'email_kind_separator': Email_Conn_Separator,
        'email_no_selection_value': Email_No_Selection_Value,
        'email_no_selection_label': Email_No_Selection_Label,
        'email_none_value': Email_None_Value,
        'email_create_new_value': Email_Create_New_Value,
        'email_remove_label': Email_Remove_Label,
        'email_groups': get_email_groups(),
        'storage_field_names': list(get_storage_field_names(alert_type)),
        'checkbox_field_names': list(get_checkbox_field_names(alert_type)),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

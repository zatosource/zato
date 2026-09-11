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
# that config_map holds.

# Django
from django import forms
from django.urls import reverse

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import Default_Window_Seconds_By_Source
from zato.common.alerting.seed.api import build_ruleset_document, default_rulesets
from zato.common.audit_log.api import AuditSource
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine.sql.constants import Documents_Key

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

# Every form field of the tab is named with this prefix, which is also the prefix
# the values are stored under in the object's opaque attributes.
Field_Prefix = 'alert_'

# The two fields every alert type has around its own ones
Is_Active_Field = 'is_active'
Email_Connection_Field = 'email_connection'

# What the tab is called in the tab strip
Tab_Label = 'Alerts'

# What the first line of the tab, the one switching the rest on and off, is called
Active_Label = 'Active'

# What the link opening a line's popover says beside its summary
Edit_Hint = 'Click to edit'

# Which alert type each object type's settings follow
alert_type_file_transfer = 'file_transfer'

# The window the failure counts of a type are measured over - it is the collectors' own
# window, said in minutes on the tab so that a reader knows how long "in a window" is.
Seconds_Per_Minute = 60
window_minutes = {
    alert_type_file_transfer: Default_Window_Seconds_By_Source[AuditSource.File_Outgoing] // Seconds_Per_Minute,
}

# ################################################################################################################################
# ################################################################################################################################

# The kinds a line of the tab can be of - a summary link opening a popover with the
# numbers behind it, a switch answered on the spot, or a chip opening a panel to pick from.
Line_Kind_Popover = 'popover'
Line_Kind_Toggle = 'toggle'
Line_Kind_Email = 'email'

# ################################################################################################################################
# ################################################################################################################################

# The email connection select - how a chosen connection is encoded in its value,
# what an empty group says and what the entry that opens the create form is named.
Email_Kind_SMTP = 'smtp'
Email_Kind_IMAP = 'imap'
Email_Kind_Separator = ':'
Email_No_Selection_Value = ''
Email_No_Selection_Label = 'Select a connection'
Email_None_Value = 'zato-none'
Email_None_Label = '(None)'
Email_Create_New_Value = 'zato-create-new'
Email_Create_New_Label = 'Add new ...'

# What the panel picking a connection is called and what a picked row says of itself
Email_Panel_Title = 'Email connection'
Email_Remove_Label = 'click to remove'

# The option groups of the select, in the order they are shown
_email_groups = [
    {'kind': Email_Kind_SMTP, 'label': 'SMTP', 'url_name': 'email-smtp'},
    {'kind': Email_Kind_IMAP, 'label': 'Microsoft 365', 'url_name': 'email-imap'},
]

# What the connections of each kind are, until the lookup through the backend services is in place.
# The Microsoft 365 group has entries and the SMTP one has none so that both states of a group can be seen.
_placeholder_email_connections = {
    Email_Kind_SMTP: [],
    Email_Kind_IMAP: ['ops.m365', 'finance.m365'],
}

# ################################################################################################################################
# ################################################################################################################################

# What each field is called where it is edited and the unit its value is in
field_display = {
    'consecutive_failures': ('Consecutive failures', ''),
    'error_rate':           ('Error rate', '%'),
    'alert_threshold':      ('Alert threshold', '%'),
    'max_latency':          ('Max latency', 'ms'),
    'max_query_time':       ('Max query time', 'ms'),
    'warning_latency':      ('Warning latency', 'ms'),
    'critical_latency':     ('Critical latency', 'ms'),
    'max_tool_call_time':   ('Max tool-call time', 'ms'),
    'health_alerts':        ('Health alerts', ''),
    'max_call_time':        ('Max call time', 'ms'),
    'auth_failures':        ('Auth failures', ''),
    'warning_failures':     ('Warning failures', ''),
    'critical_failures':    ('Critical failures', ''),
    'arrival_overdue':      ('Arrival overdue', 'windows'),
    'test_transfers':       ('Test transfers', ''),
    'overdue_multiplier':   ('Overdue multiplier', ''),
    'start_delay':          ('Start delay', 'ms'),
    'certificate_warning':  ('Certificate warning', 'days'),
    'outstanding_backlog':  ('Outstanding backlog', ''),
    'feed_silence':         ('Feed silence', 's'),
    'use_llm':              ('Use LLM', ''),
}

# What each field means, shown by the how-it-works badge of a popover
field_how_it_works = {
    Is_Active_Field:        'Whether alerts are raised for this object at all. Off means nothing below is measured.',
    'consecutive_failures': 'How many failures in a row raise an alert.',
    'error_rate':           'The share of failed calls, in percent, that raises an alert.',
    'alert_threshold':      'The error rate, in percent, at which an alert is escalated.',
    'max_latency':          'Calls slower than this many milliseconds count as slow.',
    'max_query_time':       'Queries slower than this many milliseconds count as slow.',
    'warning_latency':      'Completions slower than this many milliseconds raise a warning.',
    'critical_latency':     'Completions slower than this many milliseconds are critical.',
    'max_tool_call_time':   'Tool calls slower than this many milliseconds count as slow.',
    'health_alerts':        'Whether the Microsoft service health feed raises alerts of its own.',
    'max_call_time':        'Calls slower than this many milliseconds count as slow.',
    'auth_failures':        'How many authentication failures in a row raise an alert.',
    'warning_failures':     f'How many failures in {window_minutes[alert_type_file_transfer]} minutes raise a warning.',
    'critical_failures':    f'How many failures in {window_minutes[alert_type_file_transfer]} minutes count as critical.',
    'arrival_overdue':      'How many arrival windows may pass without a file before an alert.',
    'test_transfers':       'Whether periodic test transfers run against this connection.',
    'overdue_multiplier':   'How many intervals late a job may run before an alert.',
    'start_delay':          'How many milliseconds late a job may start before an alert.',
    'certificate_warning':  'How many days before expiry a certificate raises an alert.',
    'outstanding_backlog':  'How many outstanding messages raise an alert.',
    'feed_silence':         'How many seconds of silence from a feed raise an alert.',
    'use_llm':              'Whether alerts above the alert threshold are diagnosed by the LLM.',
    Email_Connection_Field: 'The SMTP or Microsoft 365 connection that sends the alert emails.',
}

# ################################################################################################################################
# ################################################################################################################################

# The sections the lines of a tab are grouped under - the core settings first,
# the switches and the email connection, then the thresholds that raise an alert.
Section_Core = 'Core settings'
Section_Thresholds = 'Thresholds'

# The lines of the tab for each alert type, in the order they are read. A line names the
# question, the fields answering it and, for a popover line, the title of its micro-form and
# the sentence its summary link reads as - `{field}` is the field's value and
# `{field|singular|plural}` the value with the right one of the two nouns after it.
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
            'summary': '{consecutive_failures|failure|failures} one after another',
            'how_it_works': 'How many transfers may fail one after another before an alert is raised.',
        },
        {
            'name': 'failures_in_a_window',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': f'Failures in {window_minutes[alert_type_file_transfer]} minutes',
            'title': f'Failures in {window_minutes[alert_type_file_transfer]} minutes',
            'fields': ['warning_failures', 'critical_failures'],
            'summary': 'warning at {warning_failures}, critical at {critical_failures}',
            'how_it_works': f'How many failures within {window_minutes[alert_type_file_transfer]} minutes ' + \
                'raise a warning and how many count as critical.',
        },
        {
            'name': 'escalation',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Escalation',
            'title': 'Escalation',
            'fields': ['alert_threshold'],
            'summary': f'above {{alert_threshold}}% failed in {window_minutes[alert_type_file_transfer]} minutes',
            'how_it_works': f'The share of transfers failed in {window_minutes[alert_type_file_transfer]} minutes, ' + \
                'in percent, above which an alert is escalated.',
        },
        {
            'name': 'overdue_files',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Overdue files',
            'title': 'Overdue files',
            'fields': ['arrival_overdue'],
            'summary': 'after {arrival_overdue|missed arrival window|missed arrival windows}',
            'how_it_works': 'How many arrival windows may pass without a file before it counts as overdue.',
        },
    ],
}

# ################################################################################################################################
# ################################################################################################################################

def form_field_name(name:'str') -> 'str':
    """ The name a field of the tab goes by on the form and in storage.
    """
    out = Field_Prefix + name
    return out

# ################################################################################################################################

def get_type_fields(alert_type:'str') -> 'anylist':
    """ The number and toggle fields of an alert type, in the order the rule definition lists them.
    """
    out = config_map.type_fields[alert_type]
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
    so that the tab and the rules never disagree about what a new object starts with.
    """
    ruleset_name = config_map.type_to_ruleset[alert_type]

    # The seed table pairs each ruleset's name with the text form of its rules ..
    zrules_contents = ''
    for name, contents in default_rulesets:
        if name == ruleset_name:
            zrules_contents = contents

    # .. which parses into the same documents the store keeps ..
    document = build_ruleset_document(ruleset_name, zrules_contents)
    documents = document[Documents_Key]

    # .. and the screen values are read from them the way the alert rules screen reads them.
    out = config_map.read_type_values(alert_type, documents)
    out[Is_Active_Field] = True
    out[Email_Connection_Field] = Email_No_Selection_Value

    return out

# ################################################################################################################################

def encode_email_connection(kind:'str', name:'str') -> 'str':
    """ One select value naming both the kind of the email connection and the connection itself.
    """
    out = kind + Email_Kind_Separator + name
    return out

# ################################################################################################################################

def _get_email_connection_names(kind:'str') -> 'strlist':
    """ The names of the email connections of one kind.
    """
    out = _placeholder_email_connections[kind]
    return out

# ################################################################################################################################

def get_email_connection_choices() -> 'anylist':
    """ The grouped choices of the email connection select - one group per kind of connection,
    each listing its connections or saying that there are none, and each ending with the entry
    that opens the page where a new one is created.
    """
    out:'anylist' = [(Email_No_Selection_Value, Email_No_Selection_Label)]

    for group in _email_groups:
        kind = group['kind']
        options:'anylist' = []

        names = _get_email_connection_names(kind)

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

        if str(value).endswith(Email_Kind_Separator + Email_None_Value):
            out['attrs']['disabled'] = True

        return out

# ################################################################################################################################

def add_alerts_fields(form:'forms.Form', alert_type:'str') -> 'None':
    """ Adds the fields of the Alerts tab to a form - the active toggle first, then the type's
    own numbers and toggles, then the email connection select.
    """
    defaults = get_defaults(alert_type)

    is_active_default = defaults[Is_Active_Field]
    form.fields[form_field_name(Is_Active_Field)] = forms.BooleanField(
        required=False, initial=is_active_default, widget=forms.CheckboxInput())

    for field in get_type_fields(alert_type):
        name = field['name']
        default = defaults[name]

        if field['kind'] == config_map.Kind_Toggle:
            form_field = forms.BooleanField(required=False, initial=default, widget=forms.CheckboxInput())
        else:
            form_field = forms.IntegerField(required=False, initial=default, min_value=1, widget=forms.NumberInput())

        form.fields[form_field_name(name)] = form_field

    form.fields[form_field_name(Email_Connection_Field)] = forms.ChoiceField(
        required=False, choices=get_email_connection_choices(), widget=EmailConnectionSelect())

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
    its values and where its create entries lead.
    """
    field_kinds = get_field_kinds(alert_type)

    field_labels:'anydict' = {}
    how_it_works_by_field:'anydict' = {Is_Active_Field: field_how_it_works[Is_Active_Field], Email_Connection_Field: field_how_it_works[Email_Connection_Field]}

    for field in get_type_fields(alert_type):
        name = field['name']
        field_labels[name] = get_field_label(name)
        how_it_works_by_field[name] = field_how_it_works[name]

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
        'field_labels': field_labels,
        'field_how_it_works': how_it_works_by_field,
        'edit_hint': Edit_Hint,
        'email_kind_separator': Email_Kind_Separator,
        'email_no_selection_value': Email_No_Selection_Value,
        'email_no_selection_label': Email_No_Selection_Label,
        'email_none_value': Email_None_Value,
        'email_create_new_value': Email_Create_New_Value,
        'email_remove_label': Email_Remove_Label,
        'email_groups': get_email_groups(),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

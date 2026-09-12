# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines of the reusable Alerts tab, one table per alert type - what each line is called, which
# fields answer it, what its popover is titled and what its summary reads as - with the unit selects,
# the labels and the sections the lines stand on. zato.admin.web.alerts_tab builds the forms, the
# template context and the JavaScript configuration off these tables.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_channels, alert_type_file_transfer, Email_Connection_Field, \
    field_display as shared_field_display, field_help, Is_Active_Field, LLM_Connection_Field, Unit_Field_Suffix
from zato.admin.web.alerts_tab_picks import Email_Empty_Text, email_kinds, Live_Type_Email_Connection, \
    Live_Type_LLM_Connection, llm_kinds, LLM_Empty_Text

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

# The windows of a channel's own measures, each a duration with a unit select of its own
Server_Errors_Window_Unit_Field = 'server_errors_window' + Unit_Field_Suffix
Latency_Window_Unit_Field = 'latency_window' + Unit_Field_Suffix
Auth_Failures_Window_Unit_Field = 'auth_failures_window' + Unit_Field_Suffix
Client_Errors_Window_Unit_Field = 'client_errors_window' + Unit_Field_Suffix

# The unit of the silence a channel that expects traffic tolerates - a duration like the window
Silence_Window_Unit_Field = config_map.Silence_Window_Field_Name + Unit_Field_Suffix

# The unit selects of the tab, by name - what each offers and what a new object starts with
unit_fields = {
    Arrival_Overdue_Unit_Field: {'choices': duration_unit_choices, 'initial': Arrival_Overdue_Unit_Default},
    Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Server_Errors_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Latency_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Auth_Failures_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Client_Errors_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Silence_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
}

# The time slots of a channel's silence alert - ranges of the day with a switch and a silence of
# their own, kept as one JSON list the popover's time slots kit reads and writes whole.
Silence_Slots_Field = config_map.Silence_Slots_Field_Name

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
# numbers behind it, a switch answered on the spot, or a select picking a connection.
Line_Kind_Popover = 'popover'
Line_Kind_Toggle = 'toggle'
Line_Kind_Pick = 'pick'

# ################################################################################################################################
# ################################################################################################################################

# What a field is called in its popover, where the shared label reads as a column header rather than a question
_popover_labels = {
    'window':               'In the last',
    'server_errors_window': 'In the last',
    'latency_window':       'In the last',
    'auth_failures_window': 'In the last',
    'client_errors_window': 'In the last',
    'arrival_overdue':      'Alert after',
    'silence_window':       'Alert after',
    'traffic_expected':     'Alerts on',
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
field_how_it_works[Silence_Window_Unit_Field] = 'Whether the silence a channel tolerates is in minutes, hours or days.'

for _window_unit_field in (Server_Errors_Window_Unit_Field, Latency_Window_Unit_Field, Auth_Failures_Window_Unit_Field,
    Client_Errors_Window_Unit_Field):
    field_how_it_works[_window_unit_field] = field_how_it_works[Window_Unit_Field]

# ################################################################################################################################
# ################################################################################################################################

# The sections the lines of a tab are grouped under - the core settings first,
# the switches and the connections, then the thresholds that raise an alert.
Section_Core = 'Core settings'
Section_Thresholds = 'Thresholds'

# The sections a channel's thresholds are split into - what fails, who calls and how the traffic flows
Section_Failures = 'Failures'
Section_Callers = 'Callers'
Section_Traffic = 'Traffic'

# The lines of the tab for each alert type, in the order they are read. A line names the
# question, the fields answering it and, for a popover line, the title of its micro-form and
# the sentence its summary link reads as - `{field}` is the field's value,
# `{field|singular|plural}` the value with the right one of the two nouns after it and
# `{unit_field@count_field}` the count with the unit select's noun after it, in the singular
# or the plural as the count says, and `{slots_field#singular|plural}` the number of time slots
# with the right noun after it, set off with a comma and left out altogether when there are none. A popover line with a `unit_field`
# shows that select right after the last of its numbers, its `rows` say which fields share a row
# of the popover when they are not all on one, a `slots_field` is a list of time slots the
# popover's kit edits under the numbers, and a popover line with an `off_field` toggle among its
# fields reads as its `summary_off` while that toggle is off. A pick line names the kinds of
# connection its select lists, whether its values carry the kind, the type the live form updates
# poll knows its connections as and what its select says when there is nothing to list, and a
# line with a `depends_on` toggle is dimmed while that toggle is off.
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
            'name': 'llm',
            'section': Section_Core,
            'kind': Line_Kind_Pick,
            'label': 'LLM connection',
            'fields': [LLM_Connection_Field],
            'kinds': llm_kinds,
            'encode_kind': False,
            'live_type': Live_Type_LLM_Connection,
            'empty_text': LLM_Empty_Text,
            'depends_on': 'use_llm',
            'how_it_works': field_how_it_works[LLM_Connection_Field],
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
            'kind': Line_Kind_Pick,
            'label': 'Email connection',
            'fields': [Email_Connection_Field],
            'kinds': email_kinds,
            'encode_kind': True,
            'live_type': Live_Type_Email_Connection,
            'empty_text': Email_Empty_Text,
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
    alert_type_channels: [
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
            'name': 'llm',
            'section': Section_Core,
            'kind': Line_Kind_Pick,
            'label': 'LLM connection',
            'fields': [LLM_Connection_Field],
            'kinds': llm_kinds,
            'encode_kind': False,
            'live_type': Live_Type_LLM_Connection,
            'empty_text': LLM_Empty_Text,
            'depends_on': 'use_llm',
            'how_it_works': field_how_it_works[LLM_Connection_Field],
        },
        {
            'name': 'email',
            'section': Section_Core,
            'kind': Line_Kind_Pick,
            'label': 'Email connection',
            'fields': [Email_Connection_Field],
            'kinds': email_kinds,
            'encode_kind': True,
            'live_type': Live_Type_Email_Connection,
            'empty_text': Email_Empty_Text,
            'how_it_works': field_how_it_works[Email_Connection_Field],
        },
        {
            'name': 'failures_in_a_row',
            'section': Section_Failures,
            'kind': Line_Kind_Popover,
            'label': 'Failures in a row',
            'title': 'Failures in a row',
            'fields': ['consecutive_failures'],
            'summary': 'Alert after {consecutive_failures|failed call|failed calls} in a row',
            'how_it_works': 'How many calls may fail one after another before an alert is raised.',
        },
        {
            'name': 'error_rate',
            'section': Section_Failures,
            'kind': Line_Kind_Popover,
            'label': 'Error rate',
            'title': 'Error rate',
            'fields': ['error_rate', 'window'],
            'rows': [['error_rate'], ['window']],
            'unit_field': Window_Unit_Field,
            'summary': 'Alert at {error_rate}% failed calls ' + f'in the last {{{Window_Unit_Field}@window}}',
            'how_it_works': 'The share of failed calls, in percent, that raises an alert, ' + \
                'and how long the window the share is measured over.',
        },
        {
            'name': 'server_errors',
            'section': Section_Failures,
            'kind': Line_Kind_Popover,
            'label': 'Server errors',
            'title': 'Server errors',
            'fields': ['server_errors', 'server_errors_window'],
            'rows': [['server_errors'], ['server_errors_window']],
            'unit_field': Server_Errors_Window_Unit_Field,
            'summary': 'Alert at {server_errors}% calls answered with a 5xx ' + \
                f'in the last {{{Server_Errors_Window_Unit_Field}@server_errors_window}}',
            'how_it_works': 'The share of calls answered with a 5xx status, in percent, that raises an alert, ' + \
                'and how long the window the share is measured over.',
        },
        {
            'name': 'rejected_callers',
            'section': Section_Callers,
            'kind': Line_Kind_Popover,
            'label': 'Rejected callers',
            'title': 'Rejected callers',
            'fields': ['auth_failures', 'auth_failures_window'],
            'rows': [['auth_failures'], ['auth_failures_window']],
            'unit_field': Auth_Failures_Window_Unit_Field,
            'summary': 'Alert after {auth_failures|rejected call|rejected calls} with a 401 or a 403 ' + \
                f'in the last {{{Auth_Failures_Window_Unit_Field}@auth_failures_window}}',
            'how_it_works': 'How many calls answered with a 401 or a 403 raise an alert, ' + \
                'and how long the window they are counted over.',
        },
        {
            'name': 'bad_requests',
            'section': Section_Callers,
            'kind': Line_Kind_Popover,
            'label': 'Bad requests',
            'title': 'Bad requests',
            'fields': ['client_errors', 'client_errors_window'],
            'rows': [['client_errors'], ['client_errors_window']],
            'unit_field': Client_Errors_Window_Unit_Field,
            'summary': 'Alert after {client_errors|bad request|bad requests} with any other 4xx ' + \
                f'in the last {{{Client_Errors_Window_Unit_Field}@client_errors_window}}',
            'how_it_works': 'How many calls answered with a 4xx other than 401 or 403 raise an alert, ' + \
                'and how long the window they are counted over.',
        },
        {
            'name': 'slow_responses',
            'section': Section_Traffic,
            'kind': Line_Kind_Popover,
            'label': 'Slow responses',
            'title': 'Slow responses',
            'fields': ['max_latency', 'latency_window'],
            'rows': [['max_latency'], ['latency_window']],
            'unit_field': Latency_Window_Unit_Field,
            'summary': 'Alert when responses average over {max_latency} ms ' + \
                f'in the last {{{Latency_Window_Unit_Field}@latency_window}}',
            'how_it_works': 'Responses averaging more than this many milliseconds raise an alert, ' + \
                'and how long the window they are averaged over.',
        },
        {
            'name': 'silence',
            'section': Section_Traffic,
            'kind': Line_Kind_Popover,
            'label': 'No requests received',
            'title': 'No requests received',
            'fields': ['traffic_expected', 'silence_window', Silence_Slots_Field],
            'unit_field': Silence_Window_Unit_Field,
            'slots_field': Silence_Slots_Field,
            'off_field': 'traffic_expected',
            'summary_off': 'Alerts off',
            'summary': f'Alert after {{{Silence_Window_Unit_Field}@silence_window}} without a request' + \
                f'{{{Silence_Slots_Field}#range of the day with its own settings|ranges of the day with their own settings}}',
            'how_it_works': 'Whether a channel that receives no requests raises an alert and after how long, ' + \
                'all day or in ranges of the day with a switch and a silence of their own.',
        },
    ],
}

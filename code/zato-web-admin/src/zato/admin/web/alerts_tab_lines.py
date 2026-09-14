# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines of the Alerts tab, one table per alert type, with the unit selects, the labels and the sections they stand on.

# Zato
from zato.admin.web.alerts_tab_picks import Email_Empty_Text, email_kinds, Live_Type_Email_Connection, \
    Live_Type_LLM_Connection, llm_kinds, LLM_Empty_Text
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_channels, alert_type_fhir, alert_type_file_transfer, \
    alert_type_mllp_channel, alert_type_rest, alert_type_soap, Email_Connection_Field, field_display as shared_field_display, \
    field_help, get_defaults, Is_Active_Field, LLM_Connection_Field, Unit_Field_Suffix
from zato.common.api import HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# An option's value is the noun in the singular and its label the plural
duration_unit_choices:'anylist' = []

for _unit_name, _ in config_map.Duration_Units:
    duration_unit_choices.append((_unit_name, _unit_name + 's'))

# The unit of the time a file may fail to arrive for, stored with the number
Arrival_Overdue_Unit_Field   = 'arrival_overdue' + Unit_Field_Suffix
Arrival_Overdue_Unit_Default = 'hour'

# The unit selects of the durations, named after their fields and not stored
Window_Unit_Field               = config_map.Window_Field_Name + Unit_Field_Suffix
Server_Errors_Window_Unit_Field = 'server_errors_window' + Unit_Field_Suffix
Latency_Window_Unit_Field       = 'latency_window' + Unit_Field_Suffix
Auth_Failures_Window_Unit_Field = 'auth_failures_window' + Unit_Field_Suffix
Client_Errors_Window_Unit_Field = 'client_errors_window' + Unit_Field_Suffix
Silence_Window_Unit_Field       = config_map.Silence_Window_Field_Name + Unit_Field_Suffix
Status_Codes_Window_Unit_Field  = 'status_codes_window' + Unit_Field_Suffix
Connection_Failures_Window_Unit_Field = 'connection_failures_window' + Unit_Field_Suffix
Faults_Window_Unit_Field        = 'faults_window' + Unit_Field_Suffix
Outcomes_Window_Unit_Field      = 'outcomes_window' + Unit_Field_Suffix
Acks_Window_Unit_Field          = 'acks_window' + Unit_Field_Suffix

# The unit selects of the tab, by name
unit_fields:'anydict' = {
    Arrival_Overdue_Unit_Field: {'choices': duration_unit_choices, 'initial': Arrival_Overdue_Unit_Default},
    Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Server_Errors_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Latency_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Auth_Failures_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Client_Errors_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Silence_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Status_Codes_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Connection_Failures_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Faults_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Outcomes_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
    Acks_Window_Unit_Field: {'choices': duration_unit_choices, 'initial': config_map.Duration_Unit_Smallest},
}

# The JSON list of time slots of a channel's silence alert
Silence_Slots_Field = config_map.Silence_Slots_Field_Name

# The status codes an outgoing connection alerts on, as typed, and what the field shows before anything is typed -
# the default the seeded rule carries, so the two can never drift apart
Status_Codes_Field = config_map.Status_Codes_Field_Name
Status_Codes_Default = get_defaults(alert_type_rest)[Status_Codes_Field]

# The SOAP fault codes an outgoing SOAP connection alerts on, as typed, with the seeded default the same way
Fault_Codes_Field = config_map.Fault_Codes_Field_Name
Fault_Codes_Default = get_defaults(alert_type_soap)[Fault_Codes_Field]

# The OperationOutcome issue codes an outgoing FHIR connection alerts on, as typed, with the seeded default the same way
Outcome_Codes_Field = config_map.Outcome_Codes_Field_Name
Outcome_Codes_Default = get_defaults(alert_type_fhir)[Outcome_Codes_Field]

# The negative acknowledgment codes an MLLP channel alerts on, as typed, with the seeded default the same way
Ack_Codes_Field = config_map.Ack_Codes_Field_Name
Ack_Codes_Default = get_defaults(alert_type_mllp_channel)[Ack_Codes_Field]

# How often an outgoing connection is pinged - fields of the connection's own form rather than alert settings,
# which the tab edits in place, so they carry no alert prefix and travel outside of the alert settings
Health_Check_Run_Every_Field = HTTP_SOAP.HealthCheck.Field_Run_Every
Health_Check_Run_Unit_Field = HTTP_SOAP.HealthCheck.Field_Run_Unit
Health_Check_Summary_Empty = 'No health checks'

Tab_Label = 'Alerts'
Active_Label = 'Active'
Edit_Hint = 'Click to edit'

# What a checked checkbox arrives as from the browser
Checkbox_On_Value = 'on'

# ################################################################################################################################
# ################################################################################################################################

Line_Kind_Popover = 'popover'
Line_Kind_Toggle = 'toggle'
Line_Kind_Pick = 'pick'

# ################################################################################################################################
# ################################################################################################################################

# What a field is called in its popover
_popover_labels = {
    'window':               'In the last',
    'server_errors_window': 'In the last',
    'latency_window':       'In the last',
    'auth_failures_window': 'In the last',
    'client_errors_window': 'In the last',
    'status_codes_window':  'In the last',
    'connection_failures_window': 'In the last',
    'faults_window':        'In the last',
    'outcomes_window':      'In the last',
    'acks_window':          'In the last',
    'status_code_threshold': 'Alert after',
    'fault_threshold':      'Alert after',
    'outcome_threshold':    'Alert after',
    'ack_threshold':        'Alert after',
    'connection_failures':  'Alert after',
    'arrival_overdue':      'Alert after',
    'silence_window':       'Alert after',
    'traffic_expected':     'Alerts on',
}

field_display = dict(shared_field_display)

for _popover_name, _popover_label in _popover_labels.items():
    _, _popover_unit = shared_field_display[_popover_name]
    field_display[_popover_name] = (_popover_label, _popover_unit)

field_how_it_works = dict(field_help)
field_how_it_works[Window_Unit_Field] = 'Whether the window is in minutes, hours or days.'
field_how_it_works[Arrival_Overdue_Unit_Field] = 'Whether the time a file may fail to arrive for is in minutes, hours or days.'
field_how_it_works[Silence_Window_Unit_Field] = 'Whether the silence a channel tolerates is in minutes, hours or days.'

for _window_unit_field in (Server_Errors_Window_Unit_Field, Latency_Window_Unit_Field, Auth_Failures_Window_Unit_Field,
    Client_Errors_Window_Unit_Field, Status_Codes_Window_Unit_Field, Connection_Failures_Window_Unit_Field,
    Faults_Window_Unit_Field, Outcomes_Window_Unit_Field, Acks_Window_Unit_Field):
    field_how_it_works[_window_unit_field] = field_how_it_works[Window_Unit_Field]

field_display[Health_Check_Run_Every_Field] = ('Ping every', '')
field_how_it_works[Health_Check_Run_Every_Field] = 'How often the connection is pinged, e.g. every 5 minutes. ' + \
    'Leave empty for no health checks.'
field_how_it_works[Health_Check_Run_Unit_Field] = 'Whether the time between pings is in seconds, minutes, hours or days.'

# ################################################################################################################################
# ################################################################################################################################

Section_Core = 'Core settings'
Section_Thresholds = 'Thresholds'

Section_Health = 'Health check'
Section_Failures = 'Failures'
Section_Callers = 'Callers'
Section_Traffic = 'Traffic'

# ################################################################################################################################
# ################################################################################################################################

# The core lines every type's tab opens with - the Active switch, the LLM switch with its connection and the email connection

def _active_line() -> 'anydict':
    out = {
        'name': 'active',
        'section': Section_Core,
        'kind': Line_Kind_Toggle,
        'label': Active_Label,
        'fields': [Is_Active_Field],
        'how_it_works': field_how_it_works[Is_Active_Field],
    }
    return out

def _use_llm_line() -> 'anydict':
    out = {
        'name': 'use_llm',
        'section': Section_Core,
        'kind': Line_Kind_Toggle,
        'label': 'Use LLM',
        'fields': ['use_llm'],
        'how_it_works': field_how_it_works['use_llm'],
    }
    return out

def _llm_line() -> 'anydict':
    out = {
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
    }
    return out

def _email_line() -> 'anydict':
    out = {
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
    }
    return out

# The lines a connection's failed calls are measured by - how many in a row and what share of the recent traffic

def _failures_in_a_row_line() -> 'anydict':
    out = {
        'name': 'failures_in_a_row',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Failures in a row',
        'title': 'Failures in a row',
        'fields': ['consecutive_failures'],
        'rows': [['consecutive_failures']],
        'summary': 'Alert after {consecutive_failures|failed call|failed calls} in a row',
        'how_it_works': 'How many calls may fail one after another before an alert is raised.',
    }
    return out

def _error_rate_line() -> 'anydict':
    out = {
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
    }
    return out

def _slow_responses_line() -> 'anydict':
    out = {
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
    }
    return out

# ################################################################################################################################

# A connection's health check - each ping counts towards the lines below the way a call of the connection's own does,
# under a source of its own, so a connection with no traffic is still measured. The check runs whether or not
# the alerts are active, its pings being what they read.
def _health_check_line() -> 'anydict':
    out = {
        'name': 'health_check',
        'section': Section_Health,
        'kind': Line_Kind_Popover,
        'label': 'Schedule',
        'title': 'Health check',
        'fields': [Health_Check_Run_Every_Field],
        'rows': [[Health_Check_Run_Every_Field]],
        'unit_field': Health_Check_Run_Unit_Field,
        'page_fields': True,
        'always_on': True,
        'summary': f'Ping every {{{Health_Check_Run_Unit_Field}@{Health_Check_Run_Every_Field}}}',
        'summary_empty': Health_Check_Summary_Empty,
        'how_it_works': 'How often the connection is pinged, if at all. Each ping counts towards the alerts below ' + \
            'the way a call of your own does, only apart from your own traffic - failed pings in a row raise an alert ' + \
            'without any of your calls failing, and the other way round.',
    }
    return out

# ################################################################################################################################

def _status_codes_line() -> 'anydict':
    out = {
        'name': 'status_codes',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Status codes',
        'title': 'Status codes',
        'fields': [Status_Codes_Field, 'status_code_threshold', 'status_codes_window'],
        'rows': [[Status_Codes_Field], ['status_code_threshold', 'status_codes_window']],
        'unit_field': Status_Codes_Window_Unit_Field,
        'text_fields': {Status_Codes_Field: Status_Codes_Default},
        'summary': 'Alert after {status_code_threshold|response|responses} with ' + f'{{{Status_Codes_Field}}} ' + \
            f'in the last {{{Status_Codes_Window_Unit_Field}@status_codes_window}}',
        'how_it_works': 'Which status codes raise an alert - three-digit codes such as 401 or 403 and whole classes ' + \
            'such as 4xx or 5xx, each one a chip, typed and added with Enter, removed with its cross - how many responses ' + \
            'with one of them do, and how long the window they are counted over.',
    }
    return out

# ################################################################################################################################

def _connection_failures_line() -> 'anydict':
    out = {
        'name': 'connection_failures',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Connection failures',
        'title': 'Connection failures',
        'fields': ['connection_failures', 'connection_failures_window'],
        'rows': [['connection_failures'], ['connection_failures_window']],
        'unit_field': Connection_Failures_Window_Unit_Field,
        'summary': 'Alert after {connection_failures|timeout or connection failure|timeouts or connection failures} ' + \
            f'in the last {{{Connection_Failures_Window_Unit_Field}@connection_failures_window}}',
        'how_it_works': 'How many calls that failed before any response arrived - a timeout, a refused or reset ' + \
            'connection, a name that does not resolve, a TLS failure - raise an alert, ' + \
            'and how long the window they are counted over.',
    }
    return out

# ################################################################################################################################

# The faults an outgoing SOAP connection alerts on - counted by the fault code the envelope carries, apart from the status codes
def _soap_faults_line() -> 'anydict':
    out = {
        'name': 'soap_faults',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'SOAP faults',
        'title': 'SOAP faults',
        'fields': [Fault_Codes_Field, 'fault_threshold', 'faults_window'],
        'rows': [[Fault_Codes_Field], ['fault_threshold', 'faults_window']],
        'unit_field': Faults_Window_Unit_Field,
        'text_fields': {Fault_Codes_Field: Fault_Codes_Default},
        'summary': 'Alert after {fault_threshold|fault|faults} with ' + f'{{{Fault_Codes_Field}}} ' + \
            f'in the last {{{Faults_Window_Unit_Field}@faults_window}}',
        'how_it_works': 'Which SOAP fault codes raise an alert - Receiver and Server are the endpoint\'s own faults, ' + \
            'Sender and Client the caller\'s, and a code of the endpoint\'s own keeps its prefix, e.g. x:Timeout, ' + \
            'each one a chip, typed and added with Enter, removed with its cross - how many faults with one of them do, ' + \
            'and how long the window they are counted over. A fault is counted here by its code and never as a status code.',
    }
    return out

# ################################################################################################################################

# The operation outcomes an outgoing FHIR connection alerts on - counted by the issue code the OperationOutcome carries,
# apart from the status codes
def _operation_outcomes_line() -> 'anydict':
    out = {
        'name': 'operation_outcomes',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Operation outcomes',
        'title': 'Operation outcomes',
        'fields': [Outcome_Codes_Field, 'outcome_threshold', 'outcomes_window'],
        'rows': [[Outcome_Codes_Field], ['outcome_threshold', 'outcomes_window']],
        'unit_field': Outcomes_Window_Unit_Field,
        'text_fields': {Outcome_Codes_Field: Outcome_Codes_Default},
        'summary': 'Alert after {outcome_threshold|outcome|outcomes} with ' + f'{{{Outcome_Codes_Field}}} ' + \
            f'in the last {{{Outcomes_Window_Unit_Field}@outcomes_window}}',
        'how_it_works': 'Which FHIR issue codes raise an alert - the code is what the server\'s OperationOutcome says went wrong, ' + \
            'exception, transient, timeout, throttled, lock-error, no-store and too-costly being the server\'s own trouble, ' + \
            'invalid, required and value a wrong request, not-found a missing resource, security, login, forbidden and expired ' + \
            'a refused caller - each one a chip, typed and added with Enter, removed with its cross - how many outcomes with one ' + \
            'of them do, and how long the window they are counted over. An OperationOutcome is counted here by its issue code ' + \
            'and never as a status code.',
    }
    return out

# ################################################################################################################################

# The negative acknowledgments an MLLP channel alerts on - counted by the code of the ACK the channel sent back
def _negative_acks_line() -> 'anydict':
    out = {
        'name': 'negative_acks',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Negative acks',
        'title': 'Negative acks',
        'fields': [Ack_Codes_Field, 'ack_threshold', 'acks_window'],
        'rows': [[Ack_Codes_Field], ['ack_threshold', 'acks_window']],
        'unit_field': Acks_Window_Unit_Field,
        'text_fields': {Ack_Codes_Field: Ack_Codes_Default},
        'summary': 'Alert after {ack_threshold|ack|acks} with ' + f'{{{Ack_Codes_Field}}} ' + \
            f'in the last {{{Acks_Window_Unit_Field}@acks_window}}',
        'how_it_works': 'Which acknowledgment codes the channel sent back raise an alert - AE and CE say the service ' + \
            'failed to process a message, AR and CR that the message was rejected - each one a chip, typed and added ' + \
            'with Enter, removed with its cross - how many acknowledgments with one of them do, and how long the window ' + \
            'they are counted over. The alerts read the channel\'s audit log, so the audit log option under Logging ' + \
            'and errors has to be on for anything to be counted.',
    }
    return out

# ################################################################################################################################

# A channel that receives nothing - what it receives is a request for an HTTP channel and a message for an MLLP one.
# The summary says only whether the alerts are on and how many rules there are - the all-day one and one per range of
# the day with its own settings - the rules themselves are for the popover to explain.
def _silence_line(noun:'str') -> 'anydict':
    out = {
        'name': 'silence',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': f'On no {noun}s',
        'title': f'On no {noun}s',
        'fields': ['traffic_expected', 'silence_window', Silence_Slots_Field],
        'rows': [['traffic_expected', 'silence_window', Silence_Slots_Field]],
        'unit_field': Silence_Window_Unit_Field,
        'slots_field': Silence_Slots_Field,
        'off_field': 'traffic_expected',
        'summary_off': 'Alerts off',
        'summary': f'Alerts on ({{{Silence_Slots_Field}#rule|rules}})',
        'how_it_works': f'Whether a channel that receives no {noun}s raises an alert and after how long, ' + \
            'all day or in ranges of the day with a switch and a silence of their own.',
    }
    return out

# ################################################################################################################################

# The lines of an outgoing HTTP connection of any kind - a line of the kind's own, the SOAP faults or the FHIR operation
# outcomes, goes right after the status codes
def _http_lines(*, extra_failure_line:'anydict | None'=None) -> 'anylist':
    out = [
        _active_line(),
        _use_llm_line(),
        _llm_line(),
        _email_line(),
        _health_check_line(),
        _failures_in_a_row_line(),
        _error_rate_line(),
        _status_codes_line(),
    ]

    if extra_failure_line:
        out.append(extra_failure_line)

    out.append(_connection_failures_line())
    out.append(_slow_responses_line())

    return out

# ################################################################################################################################
# ################################################################################################################################

# The lines of the tab for each alert type, in the order they are read. In a summary, `{field}` is the field's value,
# `{field|singular|plural}` the value with the right noun after it, `{unit_field@count_field}` the count with the unit
# select's noun after it and `{slots_field#singular|plural}` the number of rules a slots field stands for - the all-day
# one plus one per time slot - with the right noun after it. A popover line's `rows` say which fields share a row, its `unit_field` follows the last
# of its numbers, its `slots_field` is a list of time slots and it reads as its `summary_off` while its `off_field` is off.
# A line with a `depends_on` toggle is dimmed while that toggle is off. A line's `text_fields` are lists of names
# edited as chips and stored comma-separated, each with the seeded default it starts from. A line with `page_fields` edits fields of the page's own
# form rather than alert settings - they carry no alert prefix and the page sends them on its own - it reads as its
# `summary_empty` while its first field is empty, and one that is `always_on` is not dimmed when Active is off.
type_lines:'anydict' = {
    alert_type_file_transfer: [
        _active_line(),
        _use_llm_line(),
        _llm_line(),
        {
            'name': 'test_transfers',
            'section': Section_Core,
            'kind': Line_Kind_Toggle,
            'label': 'Test transfers',
            'fields': ['test_transfers'],
            'how_it_works': field_how_it_works['test_transfers'],
        },
        _email_line(),
        {
            'name': 'failures_in_a_row',
            'section': Section_Thresholds,
            'kind': Line_Kind_Popover,
            'label': 'Failures in a row',
            'title': 'Failures in a row',
            'fields': ['consecutive_failures'],
            'rows': [['consecutive_failures']],
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
            'rows': [['warning_failures', 'error_failures', 'window']],
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
            'rows': [['arrival_overdue']],
            'unit_field': Arrival_Overdue_Unit_Field,
            'summary': f'Alert after {{{Arrival_Overdue_Unit_Field}@arrival_overdue}} without a file',
            'how_it_works': 'How long a file may fail to arrive, in minutes, hours or days, before an alert is raised.',
        },
    ],
    alert_type_channels: [
        _active_line(),
        _use_llm_line(),
        _llm_line(),
        _email_line(),
        _failures_in_a_row_line(),
        _error_rate_line(),
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
        _slow_responses_line(),
        _silence_line('request'),
    ],
    alert_type_mllp_channel: [
        _active_line(),
        _use_llm_line(),
        _llm_line(),
        _email_line(),
        _failures_in_a_row_line(),
        _error_rate_line(),
        _negative_acks_line(),
        _slow_responses_line(),
        _silence_line('message'),
    ],
    alert_type_rest: _http_lines(),
    alert_type_soap: _http_lines(extra_failure_line=_soap_faults_line()),
    alert_type_fhir: _http_lines(extra_failure_line=_operation_outcomes_line()),
}

# ################################################################################################################################
# ################################################################################################################################

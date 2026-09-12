# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one map between the alert config screen and the rule documents - which ruleset
# each screen type reads and writes, which rules' defaults each screen field is tied to
# and which fields speak percent while their rules speak a fraction. The web admin's
# config screen and the CLI's enmasse importer and exporter both work through
# the helpers here, so a value shown, a value saved and a value imported
# are always the same value.

from __future__ import annotations

# Zato
from zato.common.alerting.collectors.common import Measure_Auth_Failures, Measure_Client_Errors, Measure_Connection_Failures, \
    Measure_Error_Rate, Measure_File_Runs, Measure_Latency, Measure_Server_Errors, Measure_Silence, Measure_Status_Codes
from zato.common.audit_log.common import AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strintdict, strlist
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The kinds a screen field comes in - a number backed by rule defaults, a duration backed
# by a rule default counted in seconds and shown as a count with a unit, a toggle backed
# by the active flags of whole rules, a ruleset toggle backed by one key every rule
# document of the ruleset carries, a JSON list of time slots kept per object and backed by no rule,
# or a text backed by a rule default that is a string, e.g. the status codes a connection alerts on.
Kind_Number         = 'number'
Kind_Duration       = 'duration'
Kind_Toggle         = 'toggle'
Kind_Ruleset_Toggle = 'ruleset_toggle'
Kind_Time_Slots     = 'time_slots'
Kind_Text           = 'text'

# The time slots of an object that has none
Time_Slots_Default = '[]'

# The status codes an outgoing connection alerts on - the field and the rule default it reads and writes
Status_Codes_Field_Name = 'status_codes'
Status_Codes_Default = 'status_codes'

# The rule default a type's window field reads and writes - how far back the
# error-rate and failure-count facts of the type's sources are measured over.
Window_Seconds_Default = 'window_seconds'
Window_Field_Name = 'window'

# The silence a channel tolerates and the time slots with a silence of their own
Silence_Window_Field_Name = 'silence_window'
Silence_Slots_Field_Name  = 'silence_slots'

# The key a duration field names the measures it is the window of under
Measures_Key = 'measures'

# The measures the one window of a connection type drives - its error rate and its latency,
# and for file transfer connections the runs of their schedules as well.
_call_measures = [Measure_Error_Rate, Measure_Latency]
_file_transfer_measures = [Measure_Error_Rate, Measure_Latency, Measure_File_Runs]

# The units a duration is shown in, smallest first - the noun in the singular and its seconds.
# A screen picks the largest unit dividing the seconds evenly, so 86400 reads as one day.
Duration_Units = [
    ('minute', 60),
    ('hour', 3600),
    ('day', 86400),
]
Duration_Unit_Smallest = Duration_Units[0][0]

# The rule document key saying whether the LLM explains every alert the ruleset raises -
# the Use LLM switch of a type reads and writes it on every rule of the type.
Explain_With_LLM_Key = 'explain_with_llm'

# Percent fields are stored as fractions - the screen says 10, the rule says 0.1.
Percent_Multiplier = 100

# ################################################################################################################################
# ################################################################################################################################

# Which ruleset each screen type reads and writes, in the order the rows render.
type_to_ruleset = {
    'rest':          'alerts_rest',
    'sql':           'alerts_sql',
    'llm':           'alerts_llm',
    'mcp':           'alerts_mcp',
    'microsoft':     'alerts_microsoft',
    'email':         'alerts_email',
    'odoo':          'alerts_odoo',
    'file_transfer': 'alerts_file_transfer',
    'scheduler':     'alerts_scheduler',
    'channels':      'alerts_channels',
    'common':        'alerts_common',
}

# ################################################################################################################################

# The audit sources each screen type's rules match on - what the type's window
# is the measuring window of. A source no type names, the health checks above all,
# is measured over the collectors' own default window.
type_sources:'dict[str, strlist]' = {
    'rest':          [AuditSource.REST_Outgoing, AuditSource.SOAP_Outgoing],
    'sql':           [AuditSource.SQL_Outgoing],
    'llm':           [AuditSource.LLM],
    'mcp':           [AuditSource.MCP],
    'microsoft':     [AuditSource.Microsoft_Cloud],
    'email':         [AuditSource.Email_SMTP, AuditSource.Email_IMAP],
    'odoo':          [AuditSource.Odoo],
    'file_transfer': [AuditSource.File_Outgoing],
    'scheduler':     [AuditSource.Scheduler],
    'channels':      [AuditSource.REST_Channel, AuditSource.SOAP_Channel, AuditSource.MLLP_Channel],
}

# ################################################################################################################################

# The fields of each type, in their screen order. A number field names the rules
# whose defaults it is tied to - the first rule that holds the default answers a read,
# every rule that holds it takes a write, which is how a threshold shared by a warning
# rule and its error sibling stays consistent. A duration field is a number of seconds
# the screen shows as a count with a unit. A toggle field names the rules
# whose active flags it reads and writes whole, and a ruleset toggle names the
# document key it reads off the first rule and writes onto every rule of the type.
type_fields:'dict[str, list[stranydict]]' = {
    'rest': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Error_Rate]},
        {'name': Status_Codes_Field_Name, 'kind': Kind_Text, 'rules': ['Status_Codes'],
            'default': Status_Codes_Default},
        {'name': 'status_code_threshold', 'kind': Kind_Number, 'rules': ['Status_Codes'],
            'default': 'status_code_threshold', 'is_percent': False},
        {'name': 'status_codes_window', 'kind': Kind_Duration, 'rules': ['Status_Codes'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Status_Codes]},
        {'name': 'connection_failures', 'kind': Kind_Number, 'rules': ['Connection_Failures'],
            'default': 'connection_failure_threshold', 'is_percent': False},
        {'name': 'connection_failures_window', 'kind': Kind_Duration, 'rules': ['Connection_Failures'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Connection_Failures]},
        {'name': 'max_latency', 'kind': Kind_Number, 'rules': ['Slow_Responses'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'latency_window', 'kind': Kind_Duration, 'rules': ['Slow_Responses'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Latency]},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'sql': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'max_query_time', 'kind': Kind_Number, 'rules': ['Slow_Queries'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'llm': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'warning_latency', 'kind': Kind_Number, 'rules': ['Slow_Completions'],
            'default': 'warning_avg_duration_ms', 'is_percent': False},
        {'name': 'error_latency', 'kind': Kind_Number, 'rules': ['Slow_Completions_Error', 'Slow_Completions'],
            'default': 'error_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'mcp': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Server_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'max_tool_call_time', 'kind': Kind_Number, 'rules': ['Slow_Tool_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'microsoft': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'health_alerts', 'kind': Kind_Toggle, 'rules': ['Service_Degraded', 'Service_Interrupted']},
        {'name': 'max_call_time', 'kind': Kind_Number, 'rules': ['Slow_API_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'email': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'auth_failures', 'kind': Kind_Number, 'rules': ['Auth_Failures'],
            'default': 'auth_failure_threshold', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'odoo': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'auth_failures', 'kind': Kind_Number, 'rules': ['Auth_Failures'],
            'default': 'auth_failure_threshold', 'is_percent': False},
        {'name': 'max_call_time', 'kind': Kind_Number, 'rules': ['Slow_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'file_transfer': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'warning_failures', 'kind': Kind_Number, 'rules': ['Transfer_Failures'],
            'default': 'warning_failure_count', 'is_percent': False},
        {'name': 'error_failures', 'kind': Kind_Number, 'rules': ['Transfer_Failures_Error', 'Transfer_Failures'],
            'default': 'error_failure_count', 'is_percent': False},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Transfer_Failures', 'Transfer_Failures_Error'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _file_transfer_measures},
        {'name': 'arrival_overdue', 'kind': Kind_Number, 'rules': ['Arrival_Overdue'],
            'default': 'arrival_overdue_multiplier', 'is_percent': False},
        {'name': 'test_transfers', 'kind': Kind_Toggle, 'rules': ['Test_Transfer_Failing']},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'scheduler': [
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Job_Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Job_Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': _call_measures},
        {'name': 'overdue_multiplier', 'kind': Kind_Number, 'rules': ['Missed_Run'],
            'default': 'overdue_multiplier', 'is_percent': False},
        {'name': 'start_delay', 'kind': Kind_Number, 'rules': ['Start_Delay'],
            'default': 'max_start_delay_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'channels': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Channel_Failing'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Channel_Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Channel_Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Error_Rate]},
        {'name': 'server_errors', 'kind': Kind_Number, 'rules': ['Server_Errors'],
            'default': 'server_error_rate_threshold', 'is_percent': True},
        {'name': 'server_errors_window', 'kind': Kind_Duration, 'rules': ['Server_Errors'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Server_Errors]},
        {'name': 'max_latency', 'kind': Kind_Number, 'rules': ['Slow_Responses'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'latency_window', 'kind': Kind_Duration, 'rules': ['Slow_Responses'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Latency]},
        {'name': 'auth_failures', 'kind': Kind_Number, 'rules': ['Auth_Failures'],
            'default': 'auth_failure_threshold', 'is_percent': False},
        {'name': 'auth_failures_window', 'kind': Kind_Duration, 'rules': ['Auth_Failures'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Auth_Failures]},
        {'name': 'client_errors', 'kind': Kind_Number, 'rules': ['Client_Errors'],
            'default': 'client_error_threshold', 'is_percent': False},
        {'name': 'client_errors_window', 'kind': Kind_Duration, 'rules': ['Client_Errors'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Client_Errors]},
        {'name': 'traffic_expected', 'kind': Kind_Toggle, 'rules': ['Channel_Silent']},
        {'name': Silence_Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Channel_Silent'],
            'default': 'silence_seconds', 'is_percent': False, 'measures': [Measure_Silence]},
        {'name': Silence_Slots_Field_Name, 'kind': Kind_Time_Slots},
        {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
    ],
    'common': [
        {'name': 'certificate_warning', 'kind': Kind_Number, 'rules': ['Certificate_Expiring'],
            'default': 'cert_warning_days', 'is_percent': False},
        {'name': 'outstanding_backlog', 'kind': Kind_Number, 'rules': ['Outstanding_Backlog'],
            'default': 'outstanding_threshold', 'is_percent': False},
        {'name': 'feed_silence', 'kind': Kind_Number, 'rules': ['Feed_Silent'],
            'default': 'silent_threshold_seconds', 'is_percent': False},
    ],
}

# ################################################################################################################################
# ################################################################################################################################

def rule_full_name(ruleset_name:'str', rule_name:'str') -> 'str':
    """ The key one rule's document sits under - the ruleset's name joined with the rule's own.
    """
    out = f'{ruleset_name}_{rule_name}'
    return out

# ################################################################################################################################

def is_rule_active(rule_document:'stranydict') -> 'bool':
    """ Whether one rule matches at all - a rule is active unless it says otherwise,
    the same reading the sweep applies.
    """
    out = rule_document.get('is_active') is not False
    return out

# ################################################################################################################################

def to_screen_value(value:'float', is_percent:'bool') -> 'float | int':
    """ One rule value in the units the screen speaks - percent fields scale up
    and whole numbers drop the trailing fraction.
    """
    if is_percent:
        value = value * Percent_Multiplier

    # A whole number reads as one - 10, not 10.0
    if isinstance(value, float):
        if value.is_integer():
            value = int(value)

    return value

# ################################################################################################################################

def to_rule_value(value:'float', is_percent:'bool') -> 'float | int':
    """ One screen value in the units the rules speak - percent fields scale down.
    """
    if is_percent:
        value = value / Percent_Multiplier

    return value

# ################################################################################################################################

def split_duration(seconds:'int') -> 'tuple[int | float, str]':
    """ A number of seconds as a count and the largest unit dividing it evenly - 86400 is one day,
    600 is ten minutes. Seconds no unit divides evenly are a fraction of the smallest unit.
    """

    # Our response to produce - the smallest unit unless a larger one divides evenly
    unit_seconds = Duration_Units[0][1]
    out_unit = Duration_Unit_Smallest

    for unit_name, candidate_seconds in Duration_Units:
        if seconds % candidate_seconds == 0:
            unit_seconds = candidate_seconds
            out_unit = unit_name

    out_count = to_screen_value(seconds / unit_seconds, False)

    return out_count, out_unit

# ################################################################################################################################

def join_duration(count:'float', unit_name:'str') -> 'int':
    """ A count of one unit back as seconds - what split_duration took apart.
    """

    # Our response to produce
    out = 0

    for candidate_name, unit_seconds in Duration_Units:
        if candidate_name == unit_name:
            out = int(count * unit_seconds)

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_number(documents:'stranydict', ruleset_name:'str', field:'stranydict') -> 'float | int | None':
    """ One number field's screen value, read from the first of its rules that still
    holds the default - None when no rule does, e.g. after a person deleted the rule.
    """

    # Our response to produce
    out = None

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)

        if rule_document := documents.get(full_name):

            defaults = rule_document.get('defaults')

            if defaults:
                if entry := defaults.get(field['default']):
                    out = to_screen_value(entry['value'], field['is_percent'])
                    break

    return out

# ################################################################################################################################

def read_text(documents:'stranydict', ruleset_name:'str', field:'stranydict') -> 'str | None':
    """ One text field's value, read from the first of its rules that still holds the default -
    None when no rule does.
    """

    # Our response to produce
    out = None

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)

        if rule_document := documents.get(full_name):

            defaults = rule_document.get('defaults')

            if defaults:
                if entry := defaults.get(field['default']):
                    out = entry['value']
                    break

    return out

# ################################################################################################################################

def read_toggle(documents:'stranydict', ruleset_name:'str', field:'stranydict') -> 'bool':
    """ One toggle field's state - on only when every rule it names exists and is active.
    """

    # Our response to produce
    out = True

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)
        rule_document = documents.get(full_name)

        if not rule_document:
            out = False
            break

        if not is_rule_active(rule_document):
            out = False
            break

    return out

# ################################################################################################################################

def read_ruleset_toggle(documents:'stranydict', field:'stranydict') -> 'bool':
    """ One ruleset toggle's state - the key's value on the first rule of the type,
    every rule carrying the same one. A ruleset with no rules or a rule that never
    had the key, e.g. one a person wrote by hand, reads as off.
    """

    # Our response to produce
    out = False

    for rule_document in documents.values():
        out = rule_document.get(field['key']) is True
        break

    return out

# ################################################################################################################################

def read_window_seconds(documents:'stranydict', type_name:'str') -> 'int | None':
    """ How many seconds one type's window rules measure over - None when the type has
    no window field or the rule holding the default is gone.
    """

    # Our response to produce
    out = None

    ruleset_name = type_to_ruleset[type_name]

    for field in type_fields[type_name]:
        if field['kind'] == Kind_Duration:
            out = read_number(documents, ruleset_name, field)
            break

    return out

# ################################################################################################################################

def read_window_seconds_by_measure(documents:'stranydict', type_name:'str') -> 'strintdict':
    """ The window of each measure one type's duration fields drive, in seconds - a field whose rule
    is gone contributes nothing, so a type with no window rule at all reads as an empty dict.
    """

    # Our response to produce
    out:'strintdict' = {}

    ruleset_name = type_to_ruleset[type_name]

    for field in type_fields[type_name]:

        if field['kind'] != Kind_Duration:
            continue

        window_seconds = read_number(documents, ruleset_name, field)

        if window_seconds is None:
            continue

        for measure in field[Measures_Key]:
            out[measure] = int(window_seconds)

    return out

# ################################################################################################################################

def read_type_values(type_name:'str', documents:'stranydict') -> 'stranydict':
    """ Every screen value of one type, keyed by field name - numbers in screen units,
    durations in seconds, toggles as booleans. A field whose rule is gone is absent rather than invented.
    """

    # Our response to produce
    out:'stranydict' = {}

    ruleset_name = type_to_ruleset[type_name]

    for field in type_fields[type_name]:

        if field['kind'] == Kind_Toggle:
            out[field['name']] = read_toggle(documents, ruleset_name, field)
        elif field['kind'] == Kind_Ruleset_Toggle:
            out[field['name']] = read_ruleset_toggle(documents, field)
        elif field['kind'] == Kind_Time_Slots:
            out[field['name']] = Time_Slots_Default
        elif field['kind'] == Kind_Text:
            text = read_text(documents, ruleset_name, field)

            if text is not None:
                out[field['name']] = text
        else:
            value = read_number(documents, ruleset_name, field)

            if value is not None:
                out[field['name']] = value

    return out

# ################################################################################################################################

def is_type_active(documents:'stranydict') -> 'bool':
    """ Whether one type shows as active - any of its rules being active is enough,
    all of them inactive means the type is off.
    """

    # Our response to produce
    out = False

    for rule_document in documents.values():
        if is_rule_active(rule_document):
            out = True
            break

    return out

# ################################################################################################################################
# ################################################################################################################################

def write_number(documents:'stranydict', ruleset_name:'str', field:'stranydict', value:'float') -> 'bool':
    """ Writes one number field into every rule of its type that holds the default,
    in rule units. Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    rule_value = to_rule_value(value, field['is_percent'])

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)

        if rule_document := documents.get(full_name):

            defaults = rule_document.get('defaults')

            if defaults:
                if entry := defaults.get(field['default']):
                    if entry['value'] != rule_value:
                        entry['value'] = rule_value
                        out = True

    return out

# ################################################################################################################################

def write_text(documents:'stranydict', ruleset_name:'str', field:'stranydict', value:'str') -> 'bool':
    """ Writes one text field into every rule of its type that holds the default.
    Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)

        if rule_document := documents.get(full_name):

            defaults = rule_document.get('defaults')

            if defaults:
                if entry := defaults.get(field['default']):
                    if entry['value'] != value:
                        entry['value'] = value
                        out = True

    return out

# ################################################################################################################################

def write_toggle(documents:'stranydict', ruleset_name:'str', field:'stranydict', is_active:'bool') -> 'bool':
    """ Flips the rules one toggle field names. Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    for rule_name in field['rules']:

        full_name = rule_full_name(ruleset_name, rule_name)

        if rule_document := documents.get(full_name):
            if is_rule_active(rule_document) != is_active:
                rule_document['is_active'] = is_active
                out = True

    return out

# ################################################################################################################################

def write_ruleset_toggle(documents:'stranydict', field:'stranydict', value:'bool') -> 'bool':
    """ Writes one ruleset toggle's key onto every rule of the type, so whichever rule
    fires carries the type's answer. Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    for rule_document in documents.values():
        if rule_document.get(field['key']) is not value:
            rule_document[field['key']] = value
            out = True

    return out

# ################################################################################################################################

def write_type_values(type_name:'str', documents:'stranydict', values:'stranydict') -> 'bool':
    """ Writes the given screen values of one type into its documents - only the fields
    present in the input are touched. Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    ruleset_name = type_to_ruleset[type_name]

    for field in type_fields[type_name]:

        if field['name'] not in values:
            continue

        value = values[field['name']]

        if field['kind'] == Kind_Toggle:
            changed = write_toggle(documents, ruleset_name, field, value)
        elif field['kind'] == Kind_Ruleset_Toggle:
            changed = write_ruleset_toggle(documents, field, value)
        elif field['kind'] == Kind_Time_Slots:
            continue
        elif field['kind'] == Kind_Text:
            changed = write_text(documents, ruleset_name, field, value)
        else:
            changed = write_number(documents, ruleset_name, field, value)

        out = out or changed

    return out

# ################################################################################################################################

def set_type_active(documents:'stranydict', is_active:'bool') -> 'bool':
    """ Flips every rule of one type at once - what the row's badge toggle does.
    Returns whether anything actually changed.
    """

    # Our response to produce
    out = False

    for rule_document in documents.values():
        if is_rule_active(rule_document) != is_active:
            rule_document['is_active'] = is_active
            out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

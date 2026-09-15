# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fields of each alert type, as the config screen and the Alerts tab list them - the tables
# config_map reads and writes rule documents through. They live here so that the map itself
# stays readable, and config_map re-exports every name defined here.

from __future__ import annotations

# Zato
from zato.common.alerting.collectors.common import Measure_Ack_Codes, Measure_Auth_Failures, Measure_Client_Errors, \
    Measure_Connection_Failures, Measure_Error_Rate, Measure_File_Runs, Measure_Latency, Measure_Operation_Outcomes, \
    Measure_Refusals, Measure_Server_Errors, Measure_Silence, Measure_SOAP_Faults, Measure_Status_Codes, Measure_Tokens, \
    Measure_Truncations

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The kinds a screen field comes in - a number backed by rule defaults, a duration backed
# by a rule default counted in seconds and shown as a count with a unit, a number of seconds backed
# by a rule default counted in milliseconds and shown fractional, an amount backed by a rule default counted
# in ones and shown as a fractional count with a unit of thousands, millions or billions, a toggle backed
# by the active flags of whole rules, a ruleset toggle backed by one key every rule
# document of the ruleset carries, a JSON list of time slots kept per object and backed by no rule,
# or a text backed by a rule default that is a string, e.g. the status codes a connection alerts on.
Kind_Number         = 'number'
Kind_Duration       = 'duration'
Kind_Seconds        = 'seconds'
Kind_Amount         = 'amount'
Kind_Toggle         = 'toggle'
Kind_Ruleset_Toggle = 'ruleset_toggle'
Kind_Time_Slots     = 'time_slots'
Kind_Text           = 'text'

# The status codes an outgoing connection alerts on - the field and the rule default it reads and writes
Status_Codes_Field_Name = 'status_codes'
Status_Codes_Default = 'status_codes'

# The SOAP fault codes an outgoing SOAP connection alerts on - the field and the rule default it reads and writes
Fault_Codes_Field_Name = 'fault_codes'
Fault_Codes_Default = 'fault_codes'

# The FHIR OperationOutcome issue codes an outgoing FHIR connection alerts on - the field and the rule default it reads and writes
Outcome_Codes_Field_Name = 'outcome_codes'
Outcome_Codes_Default = 'outcome_codes'

# The negative acknowledgment codes an MLLP channel alerts on - the field and the rule default it reads and writes
Ack_Codes_Field_Name = 'ack_codes'
Ack_Codes_Default = 'ack_codes'

# The rule default a type's window field reads and writes - how far back the
# error-rate and failure-count facts of the type's sources are measured over.
Window_Seconds_Default = 'window_seconds'
Window_Field_Name = 'window'

# The silence a channel tolerates and the time slots with a silence of their own
Silence_Window_Field_Name = 'silence_window'
Silence_Slots_Field_Name  = 'silence_slots'

# The rule document key saying whether the LLM explains every alert the ruleset raises -
# the Use LLM switch of a type reads and writes it on every rule of the type.
Explain_With_LLM_Key = 'explain_with_llm'

# The measures the one window of a connection type drives - its error rate and its latency,
# and for file transfer connections the runs of their schedules as well.
_call_measures = [Measure_Error_Rate, Measure_Latency]
_file_transfer_measures = [Measure_Error_Rate, Measure_Latency, Measure_File_Runs]

# ################################################################################################################################
# ################################################################################################################################

# The fields of each type, in their screen order. A number field names the rules
# whose defaults it is tied to - the first rule that holds the default answers a read,
# every rule that holds it takes a write, which is how a threshold shared by a warning
# rule and its error sibling stays consistent. A duration field is a number of seconds
# the screen shows as a count with a unit. A toggle field names the rules
# whose active flags it reads and writes whole, and a ruleset toggle names the
# document key it reads off the first rule and writes onto every rule of the type.

# The fields of an outgoing HTTP connection of any kind - the SOAP type lists them all with its faults
# right after the status codes, the FHIR type with its operation outcomes there, so the tabs read the same
# wherever they overlap.
_http_failure_fields:'list[stranydict]' = [
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
]

_soap_fault_fields:'list[stranydict]' = [
    {'name': Fault_Codes_Field_Name, 'kind': Kind_Text, 'rules': ['SOAP_Faults'],
        'default': Fault_Codes_Default},
    {'name': 'fault_threshold', 'kind': Kind_Number, 'rules': ['SOAP_Faults'],
        'default': 'fault_threshold', 'is_percent': False},
    {'name': 'faults_window', 'kind': Kind_Duration, 'rules': ['SOAP_Faults'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_SOAP_Faults]},
]

_fhir_outcome_fields:'list[stranydict]' = [
    {'name': Outcome_Codes_Field_Name, 'kind': Kind_Text, 'rules': ['Operation_Outcomes'],
        'default': Outcome_Codes_Default},
    {'name': 'outcome_threshold', 'kind': Kind_Number, 'rules': ['Operation_Outcomes'],
        'default': 'outcome_threshold', 'is_percent': False},
    {'name': 'outcomes_window', 'kind': Kind_Duration, 'rules': ['Operation_Outcomes'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Operation_Outcomes]},
]

# The calls that got no response at all - the HTTP connections and the outgoing MLLP ones count them alike
_connection_failure_fields:'list[stranydict]' = [
    {'name': 'connection_failures', 'kind': Kind_Number, 'rules': ['Connection_Failures'],
        'default': 'connection_failure_threshold', 'is_percent': False},
    {'name': 'connection_failures_window', 'kind': Kind_Duration, 'rules': ['Connection_Failures'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Connection_Failures]},
]

# How long the responses take - every type that has a Slow_Responses rule reads these two
_latency_fields:'list[stranydict]' = [
    {'name': 'max_latency', 'kind': Kind_Number, 'rules': ['Slow_Responses'],
        'default': 'max_avg_duration_ms', 'is_percent': False},
    {'name': 'latency_window', 'kind': Kind_Duration, 'rules': ['Slow_Responses'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Latency]},
]

_use_llm_fields:'list[stranydict]' = [
    {'name': 'use_llm', 'kind': Kind_Ruleset_Toggle, 'key': Explain_With_LLM_Key},
]

_http_traffic_fields:'list[stranydict]' = _connection_failure_fields + _latency_fields + _use_llm_fields

# What is an LLM connection's own - completions the provider cut short at the token limit, completions it refused,
# both of which arrive as an HTTP 200, and the tokens every call used, added up over a window of their own
_llm_completion_fields:'list[stranydict]' = [
    {'name': 'truncations', 'kind': Kind_Number, 'rules': ['Truncated_Completions'],
        'default': 'truncation_threshold', 'is_percent': False},
    {'name': 'truncations_window', 'kind': Kind_Duration, 'rules': ['Truncated_Completions'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Truncations]},
    {'name': 'refusals', 'kind': Kind_Number, 'rules': ['Refusals'],
        'default': 'refusal_threshold', 'is_percent': False},
    {'name': 'refusals_window', 'kind': Kind_Duration, 'rules': ['Refusals'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Refusals]},
]

# How long completions take, in seconds on the screen and in milliseconds in the rules
_llm_latency_fields:'list[stranydict]' = [
    {'name': 'warning_latency', 'kind': Kind_Seconds, 'rules': ['Slow_Completions'],
        'default': 'warning_avg_duration_ms', 'is_percent': False},
    {'name': 'error_latency', 'kind': Kind_Seconds, 'rules': ['Slow_Completions_Error', 'Slow_Completions'],
        'default': 'error_avg_duration_ms', 'is_percent': False},
    {'name': 'latency_window', 'kind': Kind_Duration, 'rules': ['Slow_Completions', 'Slow_Completions_Error'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Latency]},
]

# The tokens a connection may use in its window - a count in ones the screen shows in thousands, millions or billions
_llm_token_fields:'list[stranydict]' = [
    {'name': 'token_budget', 'kind': Kind_Amount, 'rules': ['Token_Budget'],
        'default': 'token_budget', 'is_percent': False},
    {'name': 'token_budget_window', 'kind': Kind_Duration, 'rules': ['Token_Budget'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Tokens]},
]

# The negative acknowledgments of MLLP - the ones a channel sent back or the ones an outgoing connection was answered
_ack_fields:'list[stranydict]' = [
    {'name': Ack_Codes_Field_Name, 'kind': Kind_Text, 'rules': ['Negative_Acks'],
        'default': Ack_Codes_Default},
    {'name': 'ack_threshold', 'kind': Kind_Number, 'rules': ['Negative_Acks'],
        'default': 'ack_threshold', 'is_percent': False},
    {'name': 'acks_window', 'kind': Kind_Duration, 'rules': ['Negative_Acks'],
        'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Ack_Codes]},
]

type_fields:'dict[str, list[stranydict]]' = {
    'rest': _http_failure_fields + _http_traffic_fields,
    'soap': _http_failure_fields + _soap_fault_fields + _http_traffic_fields,
    'fhir': _http_failure_fields + _fhir_outcome_fields + _http_traffic_fields,
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
    'llm': _http_failure_fields + _connection_failure_fields + _llm_completion_fields + _llm_latency_fields + \
        _llm_token_fields + _use_llm_fields,
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
    'mllp_channel': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Channel_Failing'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Error_Rate]},
    ] + _ack_fields + _latency_fields + [
        {'name': 'traffic_expected', 'kind': Kind_Toggle, 'rules': ['Channel_Silent']},
        {'name': Silence_Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Channel_Silent'],
            'default': 'silence_seconds', 'is_percent': False, 'measures': [Measure_Silence]},
        {'name': Silence_Slots_Field_Name, 'kind': Kind_Time_Slots},
    ] + _use_llm_fields,
    'mllp_outgoing': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': Window_Field_Name, 'kind': Kind_Duration, 'rules': ['Error_Rate'],
            'default': Window_Seconds_Default, 'is_percent': False, 'measures': [Measure_Error_Rate]},
    ] + _ack_fields + _connection_failure_fields + _latency_fields + _use_llm_fields,
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

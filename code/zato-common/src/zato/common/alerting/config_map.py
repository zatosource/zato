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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The kinds a screen field comes in - a number backed by rule defaults
# or a toggle backed by the active flags of whole rules.
Kind_Number = 'number'
Kind_Toggle = 'toggle'

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

# The fields of each type, in their screen order. A number field names the rules
# whose defaults it is tied to - the first rule that holds the default answers a read,
# every rule that holds it takes a write, which is how a threshold shared by a warning
# rule and its critical sibling stays consistent. A toggle field names the rules
# whose active flags it reads and writes whole.
type_fields:'dict[str, list[stranydict]]' = {
    'rest': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'max_latency', 'kind': Kind_Number, 'rules': ['Slow_Responses'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'sql': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'max_query_time', 'kind': Kind_Number, 'rules': ['Slow_Queries'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'llm': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'warning_latency', 'kind': Kind_Number, 'rules': ['Slow_Completions'],
            'default': 'warning_avg_duration_ms', 'is_percent': False},
        {'name': 'critical_latency', 'kind': Kind_Number, 'rules': ['Slow_Completions_Critical', 'Slow_Completions'],
            'default': 'critical_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'mcp': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Server_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'max_tool_call_time', 'kind': Kind_Number, 'rules': ['Slow_Tool_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'microsoft': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'health_alerts', 'kind': Kind_Toggle, 'rules': ['Service_Degraded', 'Service_Interrupted']},
        {'name': 'max_call_time', 'kind': Kind_Number, 'rules': ['Slow_API_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'email': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'auth_failures', 'kind': Kind_Number, 'rules': ['Auth_Failures'],
            'default': 'auth_failure_threshold', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'odoo': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'auth_failures', 'kind': Kind_Number, 'rules': ['Auth_Failures'],
            'default': 'auth_failure_threshold', 'is_percent': False},
        {'name': 'max_call_time', 'kind': Kind_Number, 'rules': ['Slow_Calls'],
            'default': 'max_avg_duration_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'file_transfer': [
        {'name': 'consecutive_failures', 'kind': Kind_Number, 'rules': ['Connection_Down'],
            'default': 'max_consecutive_failures', 'is_percent': False},
        {'name': 'warning_failures', 'kind': Kind_Number, 'rules': ['Transfer_Failures'],
            'default': 'warning_failure_count', 'is_percent': False},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'critical_failures', 'kind': Kind_Number, 'rules': ['Transfer_Failures_Critical', 'Transfer_Failures'],
            'default': 'critical_failure_count', 'is_percent': False},
        {'name': 'arrival_overdue', 'kind': Kind_Number, 'rules': ['Arrival_Overdue'],
            'default': 'arrival_overdue_multiplier', 'is_percent': False},
        {'name': 'test_transfers', 'kind': Kind_Toggle, 'rules': ['Test_Transfer_Failing']},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Error_Rate_Diagnose']},
    ],
    'scheduler': [
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Job_Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'alert_threshold', 'kind': Kind_Number, 'rules': ['Job_Error_Rate_Diagnose'],
            'default': 'error_rate_threshold', 'is_percent': True},
        {'name': 'overdue_multiplier', 'kind': Kind_Number, 'rules': ['Missed_Run'],
            'default': 'overdue_multiplier', 'is_percent': False},
        {'name': 'start_delay', 'kind': Kind_Number, 'rules': ['Start_Delay'],
            'default': 'max_start_delay_ms', 'is_percent': False},
        {'name': 'use_llm', 'kind': Kind_Toggle, 'rules': ['Job_Error_Rate_Diagnose']},
    ],
    'channels': [
        {'name': 'error_rate', 'kind': Kind_Number, 'rules': ['Channel_Error_Rate'],
            'default': 'error_rate_threshold', 'is_percent': True},
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

def read_type_values(type_name:'str', documents:'stranydict') -> 'stranydict':
    """ Every screen value of one type, keyed by field name - numbers in screen units,
    toggles as booleans. A field whose rule is gone is absent rather than invented.
    """

    # Our response to produce
    out:'stranydict' = {}

    ruleset_name = type_to_ruleset[type_name]

    for field in type_fields[type_name]:

        if field['kind'] == Kind_Toggle:
            out[field['name']] = read_toggle(documents, ruleset_name, field)
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

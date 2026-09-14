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
from zato.common.alerting.config_map_fields import _call_measures as _call_measures, \
    _file_transfer_measures as _file_transfer_measures, Ack_Codes_Default as Ack_Codes_Default, \
    Ack_Codes_Field_Name as Ack_Codes_Field_Name, Explain_With_LLM_Key as Explain_With_LLM_Key, \
    Fault_Codes_Default as Fault_Codes_Default, Fault_Codes_Field_Name as Fault_Codes_Field_Name, \
    Kind_Duration as Kind_Duration, Kind_Number as Kind_Number, Kind_Ruleset_Toggle as Kind_Ruleset_Toggle, \
    Kind_Text as Kind_Text, Kind_Time_Slots as Kind_Time_Slots, Kind_Toggle as Kind_Toggle, \
    Outcome_Codes_Default as Outcome_Codes_Default, Outcome_Codes_Field_Name as Outcome_Codes_Field_Name, \
    Silence_Slots_Field_Name as Silence_Slots_Field_Name, Silence_Window_Field_Name as Silence_Window_Field_Name, \
    Status_Codes_Default as Status_Codes_Default, Status_Codes_Field_Name as Status_Codes_Field_Name, \
    type_fields as type_fields, Window_Field_Name as Window_Field_Name, Window_Seconds_Default as Window_Seconds_Default
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

# The kinds a field comes in, the field name constants and the field tables of each type live in config_map_fields
# and are re-exported here, so everything about the map is still read through this one module.

# The time slots of an object that has none
Time_Slots_Default = '[]'

# The key a duration field names the measures it is the window of under
Measures_Key = 'measures'

# The units a duration is shown in, smallest first - the noun in the singular and its seconds.
# A screen picks the largest unit dividing the seconds evenly, so 86400 reads as one day.
Duration_Units = [
    ('minute', 60),
    ('hour', 3600),
    ('day', 86400),
]
Duration_Unit_Smallest = Duration_Units[0][0]

# Percent fields are stored as fractions - the screen says 10, the rule says 0.1.
Percent_Multiplier = 100

# ################################################################################################################################
# ################################################################################################################################

# Which ruleset each screen type reads and writes, in the order the rows render.
type_to_ruleset = {
    'rest':          'alerts_rest',
    'soap':          'alerts_soap',
    'fhir':          'alerts_fhir',
    'sql':           'alerts_sql',
    'llm':           'alerts_llm',
    'mcp':           'alerts_mcp',
    'microsoft':     'alerts_microsoft',
    'email':         'alerts_email',
    'odoo':          'alerts_odoo',
    'file_transfer': 'alerts_file_transfer',
    'scheduler':     'alerts_scheduler',
    'channels':      'alerts_channels',
    'mllp_channel':  'alerts_mllp_channel',
    'mllp_outgoing': 'alerts_mllp_outgoing',
    'common':        'alerts_common',
}

# ################################################################################################################################

# The audit sources each screen type's rules match on - what the type's window
# is the measuring window of. A source no type names, the health checks above all,
# is measured over the collectors' own default window.
type_sources:'dict[str, strlist]' = {
    'rest':          [AuditSource.REST_Outgoing],
    'soap':          [AuditSource.SOAP_Outgoing],
    'fhir':          [AuditSource.FHIR],
    'sql':           [AuditSource.SQL_Outgoing],
    'llm':           [AuditSource.LLM],
    'mcp':           [AuditSource.MCP],
    'microsoft':     [AuditSource.Microsoft_Cloud],
    'email':         [AuditSource.Email_SMTP, AuditSource.Email_IMAP],
    'odoo':          [AuditSource.Odoo],
    'file_transfer': [AuditSource.File_Outgoing],
    'scheduler':     [AuditSource.Scheduler],
    'channels':      [AuditSource.REST_Channel, AuditSource.SOAP_Channel],
    'mllp_channel':  [AuditSource.MLLP_Channel],
    'mllp_outgoing': [AuditSource.MLLP_Outgoing],
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

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert settings one object carries of its own - a file transfer connection above all.
# The settings are the fields of the object's alert type from config_map, with an Active
# switch before them and an email connection after them, stored flat in the object's
# opaque attributes under the alert_ prefix. The Dashboard's Alerts tab, the generic
# connection services and enmasse all go through the helpers here, so what is shown,
# what is stored and what is imported are always the same values under the same names.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.seed.api import build_ruleset_document, default_rulesets
from zato.common.api import GENERIC
from zato.common.rule_engine.sql.constants import Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strstrdict
    anydict = anydict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The key an object's alert settings sit under in enmasse YAML
Alerts_Key = 'alerts'

# Every stored alert setting is named with this prefix, e.g. alert_is_active
Field_Prefix = 'alert_'

# The two fields every alert type has around its own ones
Is_Active_Field = 'is_active'
Email_Connection_Field = 'email_connection'

# A duration is stored in seconds and shown as a count with a unit select named after the field
Unit_Field_Suffix = '_unit'

# The action config key an alert's own email connection travels under, from the sweep to the engine's email action
Email_Connection_Config_Key = 'email_connection'

# The kinds of the two fields above - the type's own fields carry the kinds config_map gives them
Kind_Active = 'active'
Kind_Email = 'email'

# The email connection an object sends its alerts through is one string naming both the kind
# of the connection and the connection itself, e.g. smtp:ops.smtp or imap:ops.m365.
Email_Conn_Type_SMTP = 'smtp'
Email_Conn_Type_IMAP = 'imap'
Email_Conn_Separator = ':'
email_conn_types = [Email_Conn_Type_SMTP, Email_Conn_Type_IMAP]

# What a new object starts with
Is_Active_Default = True
Email_Connection_Default = ''

# Which alert type each connection type's settings follow
alert_type_file_transfer = 'file_transfer'

conn_type_to_alert_type:'strstrdict' = {
    GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: alert_type_file_transfer,
    GENERIC.CONNECTION.TYPE.OUTCONN_FTP:  alert_type_file_transfer,
    GENERIC.CONNECTION.TYPE.OUTCONN_SMB:  alert_type_file_transfer,
}

# ################################################################################################################################
# ################################################################################################################################

# What each field is called where it is shown and the unit its value is in - shared by the alert
# rules screen and the Alerts tab, so a field is never called two things on two screens.
field_display = {
    'consecutive_failures': ('Consecutive failures', ''),
    'error_rate':           ('Error rate', '%'),
    'max_latency':          ('Max latency', 'ms'),
    'max_query_time':       ('Max query time', 'ms'),
    'warning_latency':      ('Warning latency', 'ms'),
    'error_latency':        ('Error latency', 'ms'),
    'max_tool_call_time':   ('Max tool-call time', 'ms'),
    'health_alerts':        ('Health alerts', ''),
    'max_call_time':        ('Max call time', 'ms'),
    'auth_failures':        ('Auth failures', ''),
    'warning_failures':     ('Warning failures', ''),
    'error_failures':       ('Error failures', ''),
    'window':               ('Window', ''),
    'arrival_overdue':      ('Arrival overdue', ''),
    'test_transfers':       ('Test transfers', ''),
    'overdue_multiplier':   ('Overdue multiplier', ''),
    'start_delay':          ('Start delay', 'ms'),
    'certificate_warning':  ('Certificate warning', 'days'),
    'outstanding_backlog':  ('Outstanding backlog', ''),
    'feed_silence':         ('Feed silence', 's'),
    'use_llm':              ('Use LLM', ''),
}

# What each field means, shown where a person edits it
field_help = {
    Is_Active_Field:        'Whether alerts are raised for this object at all. Off means nothing below is measured.',
    'consecutive_failures': 'How many failures in a row raise an alert.',
    'error_rate':           'The share of failed calls, in percent, that raises an alert.',
    'max_latency':          'Calls slower than this many milliseconds count as slow.',
    'max_query_time':       'Queries slower than this many milliseconds count as slow.',
    'warning_latency':      'Completions slower than this many milliseconds raise a warning.',
    'error_latency':        'Completions slower than this many milliseconds are errors.',
    'max_tool_call_time':   'Tool calls slower than this many milliseconds count as slow.',
    'health_alerts':        'Whether the Microsoft service health feed raises alerts of its own.',
    'max_call_time':        'Calls slower than this many milliseconds count as slow.',
    'auth_failures':        'How many authentication failures in a row raise an alert.',
    'warning_failures':     'How many failures in the window raise a warning.',
    'error_failures':       'How many failures in the window count as errors.',
    'window':               'How long the window is, in minutes, hours or days.',
    'arrival_overdue':      'How long a file may fail to arrive before an alert is raised.',
    'test_transfers':       'Whether periodic test transfers run against this connection.',
    'overdue_multiplier':   'How many intervals late a job may run before an alert.',
    'start_delay':          'How many milliseconds late a job may start before an alert.',
    'certificate_warning':  'How many days before expiry a certificate raises an alert.',
    'outstanding_backlog':  'How many outstanding messages raise an alert.',
    'feed_silence':         'How many seconds of silence from a feed raise an alert.',
    'use_llm':              'Whether the LLM explains every alert raised for this type.',
    Email_Connection_Field: 'The SMTP or Microsoft 365 connection that sends the alert emails.',
}

# ################################################################################################################################
# ################################################################################################################################

def storage_name(name:'str') -> 'str':
    """ The name a field goes by in storage - the field's own name under the alert_ prefix.
    """
    out = Field_Prefix + name
    return out

# ################################################################################################################################

def get_field_names(alert_type:'str') -> 'strlist':
    """ The fields of an alert type in their order - the Active switch, the type's own fields
    as config_map lists them, the email connection.
    """
    out:'strlist' = [Is_Active_Field]

    for field in config_map.type_fields[alert_type]:
        out.append(field['name'])

    out.append(Email_Connection_Field)

    return out

# ################################################################################################################################

def get_field_kinds(alert_type:'str') -> 'strstrdict':
    """ The kind of each field of an alert type - active, email, or one of config_map's kinds.
    """
    out:'strstrdict' = {Is_Active_Field: Kind_Active}

    for field in config_map.type_fields[alert_type]:
        out[field['name']] = field['kind']

    out[Email_Connection_Field] = Kind_Email

    return out

# ################################################################################################################################

# The defaults of each alert type once read - the seeded rules are parsed once per process, not per object listed
_defaults_by_type:'anydict' = {}

def get_defaults(alert_type:'str') -> 'anydict':
    """ The default value of each field of an alert type, read from the seeded default rules so that
    no default is ever typed twice - numbers in screen units, durations in seconds, toggles as booleans.
    """
    if alert_type in _defaults_by_type:
        out = dict(_defaults_by_type[alert_type])
        return out

    ruleset_name = config_map.type_to_ruleset[alert_type]

    # The seed table pairs each ruleset's name with the text form of its rules ..
    zrules_contents = ''
    for name, contents in default_rulesets:
        if name == ruleset_name:
            zrules_contents = contents

    # .. which parses into the same documents the store keeps ..
    document = build_ruleset_document(ruleset_name, zrules_contents)
    documents = document[Documents_Key]

    # .. and the values are read from them the way the alert rules screen reads them.
    out:'anydict' = {Is_Active_Field: Is_Active_Default}
    out.update(config_map.read_type_values(alert_type, documents))
    out[Email_Connection_Field] = Email_Connection_Default

    # Callers get a copy of their own, so what one does to it never shows in the next one's
    _defaults_by_type[alert_type] = dict(out)

    return out

# ################################################################################################################################
# ################################################################################################################################

def to_storage(alert_type:'str', values:'anydict') -> 'anydict':
    """ The given values under their storage names - only the fields present on input.
    """
    out:'anydict' = {}

    for name in get_field_names(alert_type):
        if name in values:
            out[storage_name(name)] = values[name]

    return out

# ################################################################################################################################

def from_storage(alert_type:'str', item:'anydict') -> 'anydict':
    """ The alert settings of one stored object under their own names - only the fields the object carries.
    """
    out:'anydict' = {}

    for name in get_field_names(alert_type):
        key = storage_name(name)
        if key in item:
            out[name] = item[key]

    return out

# ################################################################################################################################

def apply_defaults(alert_type:'str', item:'anydict') -> 'None':
    """ Fills in, in place, every alert setting a stored object does not carry yet with its default,
    so that an object created before a field existed reads the same as one created after.
    """
    defaults = get_defaults(alert_type)

    for name, default in defaults.items():
        key = storage_name(name)
        if key not in item:
            item[key] = default

# ################################################################################################################################
# ################################################################################################################################

def encode_email_connection(kind:'str', name:'str') -> 'str':
    """ One value naming both the kind of an email connection and the connection itself.
    """
    out = kind + Email_Conn_Separator + name
    return out

# ################################################################################################################################

def decode_email_connection(value:'str') -> 'tuple[str, str]':
    """ The kind and the name an email connection value was encoded from. A value without
    the separator has no kind, which is for the caller to reject.
    """
    separator_index = value.find(Email_Conn_Separator)

    if separator_index == -1:
        out_kind = ''
        out_name = value
    else:
        out_kind = value[:separator_index]
        out_name = value[separator_index + len(Email_Conn_Separator):]

    return out_kind, out_name

# ################################################################################################################################
# ################################################################################################################################

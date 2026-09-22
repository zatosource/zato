# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert settings one object carries of its own - a file transfer connection above all.
# The settings are the fields of the object's alert type from config_map, with an Active
# switch before them and an email connection and an LLM connection after them, stored flat
# in the object's opaque attributes under the alert_ prefix. The Dashboard's Alerts tab, the generic
# connection services and enmasse all go through the helpers here, so what is shown,
# what is stored and what is imported are always the same values under the same names.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import channel_sources as channel_sources, outgoing_sources as outgoing_sources
from zato.common.alerting.seed.api import build_ruleset_document, default_rulesets
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.audit_log.common import AuditSource
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

# The three fields every alert type has around its own ones
Is_Active_Field = 'is_active'
Email_Connection_Field = 'email_connection'
LLM_Connection_Field = 'llm_connection'

# A duration is stored in seconds and shown as a count with a unit select named after the field
Unit_Field_Suffix = '_unit'

# The action config keys an alert's own email and LLM connections travel under, from the sweep
# to the engine's email action and to the explain service
Email_Connection_Config_Key = 'email_connection'
LLM_Connection_Config_Key = 'llm_connection'

# The kinds of the three fields above - the type's own fields carry the kinds config_map gives them
Kind_Active = 'active'
Kind_Email = 'email'
Kind_LLM = 'llm'

# The email connection an object sends its alerts through is one string naming both the kind
# of the connection and the connection itself, e.g. smtp:ops.smtp or imap:ops.m365.
Email_Conn_Type_SMTP = 'smtp'
Email_Conn_Type_IMAP = 'imap'
Email_Conn_Separator = ':'
email_conn_types = [Email_Conn_Type_SMTP, Email_Conn_Type_IMAP]

# What a new object starts with
Is_Active_Default = True
Email_Connection_Default = ''
LLM_Connection_Default = ''

# Which alert type each connection type's settings follow
alert_type_file_transfer = 'file_transfer'
alert_type_channels = 'channels'
alert_type_rest = 'rest'
alert_type_soap = 'soap'
alert_type_fhir = 'fhir'
alert_type_mllp_channel = 'mllp_channel'
alert_type_mllp_outgoing = 'mllp_outgoing'

# An outgoing LLM connection's settings follow the cluster-level llm type, so the connection and the alerts_llm ruleset are one type
alert_type_llm = 'llm'

# An MCP gateway's settings follow the mcp type - the gateway is the only writer of the mcp audit source
alert_type_mcp = 'mcp'

conn_type_to_alert_type:'strstrdict' = {
    GENERIC.CONNECTION.TYPE.OUTCONN_SFTP:     alert_type_file_transfer,
    GENERIC.CONNECTION.TYPE.OUTCONN_FTP:      alert_type_file_transfer,
    GENERIC.CONNECTION.TYPE.OUTCONN_SMB:      alert_type_file_transfer,
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: alert_type_fhir,
    GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: alert_type_mllp_channel,
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: alert_type_mllp_outgoing,
    GENERIC.CONNECTION.TYPE.OUTCONN_LLM:      alert_type_llm,
    GENERIC.CONNECTION.TYPE.GATEWAY_MCP:      alert_type_mcp,
}

# The HTTPSOAP rows that carry alert settings of their own, by connection and transport -
# REST and SOAP channels under the channels type, outgoing REST connections under the rest type,
# outgoing SOAP connections under the soap type, which is the rest type plus the SOAP faults
alert_type_by_http_soap:'dict[tuple[str, str], str]' = {
    (CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP):  alert_type_channels,
    (CONNECTION.CHANNEL, URL_TYPE.SOAP):        alert_type_channels,
    (CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP): alert_type_rest,
    (CONNECTION.OUTGOING, URL_TYPE.SOAP):       alert_type_soap,
}

# The two alert types of outgoing HTTP connections - what asks whether a row is an outgoing one asks for both
alert_types_outgoing_http = (alert_type_rest, alert_type_soap)

# The HTTPSOAP rows that carry channel alert settings - REST and SOAP channels
Alert_Channel_Connection = CONNECTION.CHANNEL
Alert_Channel_Transports = (URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP)

# The transport the HTTPSOAP rows of each channel source go by
transport_by_channel_source:'strstrdict' = {
    AuditSource.REST_Channel: URL_TYPE.PLAIN_HTTP,
    AuditSource.SOAP_Channel: URL_TYPE.SOAP,
}

# The transport the HTTPSOAP rows of each outgoing source go by - a connection's own traffic
# and its health check both point at the row of that transport
transport_by_outgoing_source:'strstrdict' = {
    AuditSource.REST_Outgoing:        URL_TYPE.PLAIN_HTTP,
    AuditSource.REST_Outgoing_Health: URL_TYPE.PLAIN_HTTP,
    AuditSource.SOAP_Outgoing:        URL_TYPE.SOAP,
    AuditSource.SOAP_Outgoing_Health: URL_TYPE.SOAP,
}

# ################################################################################################################################
# ################################################################################################################################

def get_alert_type(connection:'str', transport:'str') -> 'str':
    """ The alert type an HTTPSOAP row of the given connection and transport carries settings under -
    the channels type for a REST or SOAP channel, the rest type for an outgoing REST connection,
    the soap type for an outgoing SOAP connection, an empty string for a row that carries none.
    """
    key = (connection, transport)

    if key in alert_type_by_http_soap:
        out = alert_type_by_http_soap[key]
    else:
        out = ''

    return out

# ################################################################################################################################

def is_alert_channel(connection:'str', transport:'str') -> 'bool':
    """ Whether an HTTPSOAP row of the given connection and transport carries channel alert settings.
    """
    if connection != Alert_Channel_Connection:
        return False

    out = transport in Alert_Channel_Transports
    return out

# ################################################################################################################################
# ################################################################################################################################

# What each field is called where it is shown and the unit its value is in - shared by the alert
# rules screen and the Alerts tab, so a field is never called two things on two screens.
field_display = {
    'consecutive_failures': ('Consecutive failures', ''),
    'error_rate':           ('Error rate', '%'),
    'max_latency':          ('Max latency', 'ms'),
    'max_query_time':       ('Max query time', 'ms'),
    'warning_latency':      ('Warning latency', 's'),
    'error_latency':        ('Error latency', 's'),
    'invalid_calls':        ('Invalid tool calls', ''),
    'invalid_calls_window': ('Invalid tool calls window', ''),
    'rejections':           ('Rejected responses', ''),
    'rejections_window':    ('Rejected responses window', ''),
    'throttled_calls':      ('Throttled calls', ''),
    'throttled_calls_window': ('Throttled calls window', ''),
    'repeat_calls':         ('Repeated calls', ''),
    'repeat_calls_window':  ('Repeated calls window', ''),
    'volume_budget':        ('Response volume', ''),
    'volume_budget_window': ('Response volume window', ''),
    'max_tools':            ('Max tools', ''),
    'health_alerts':        ('Health alerts', ''),
    'max_call_time':        ('Max call time', 'ms'),
    'auth_failures':        ('Auth failures', ''),
    'auth_failures_window': ('Auth failures window', ''),
    'server_errors':        ('Server errors', '%'),
    'server_errors_window': ('Server errors window', ''),
    'client_errors':        ('Client errors', ''),
    'client_errors_window': ('Client errors window', ''),
    'latency_window':       ('Latency window', ''),
    'status_codes':         ('Status codes', ''),
    'status_code_threshold': ('Responses', ''),
    'status_codes_window':  ('Status codes window', ''),
    'connection_failures':  ('Connection failures', ''),
    'connection_failures_window': ('Connection failures window', ''),
    'dlq_messages':         ('DLQ messages', ''),
    'queue_depth':          ('Queue depth', ''),
    'fault_codes':          ('Fault codes', ''),
    'fault_threshold':      ('Faults', ''),
    'faults_window':        ('Faults window', ''),
    'outcome_codes':        ('Outcome codes', ''),
    'outcome_threshold':    ('Outcomes', ''),
    'outcomes_window':      ('Outcomes window', ''),
    'ack_codes':            ('Ack codes', ''),
    'ack_threshold':        ('Acknowledgments', ''),
    'acks_window':          ('Acks window', ''),
    'truncations':          ('Truncated responses', ''),
    'truncations_window':   ('Truncations window', ''),
    'refusals':             ('Refusals', ''),
    'refusals_window':      ('Refusals window', ''),
    'token_budget':         ('Token budget', ''),
    'token_budget_window':  ('Token budget window', ''),
    'traffic_expected':     ('Alert on silence', ''),
    'silence_window':       ('Silence', ''),
    'silence_slots':        ('Time ranges', ''),
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
    'warning_latency':      'Calls slower than this many seconds raise a warning - a fraction such as 7.5 is fine.',
    'error_latency':        'Calls slower than this many seconds are errors - a fraction such as 12.5 is fine.',
    'invalid_calls':        'How many tool calls in the window naming a tool the gateway does not expose, or passing ' + \
                            'arguments its schema refuses, raise an alert - the agent\'s mistake rather than the backend\'s.',
    'invalid_calls_window': 'How long the window the invalid tool calls are counted over is.',
    'rejections':           'How many tool responses in the window refused by a safeguard in reject mode or by the size cap ' + \
                            'in block mode raise an alert.',
    'rejections_window':    'How long the window the rejected responses are counted over is.',
    'throttled_calls':      'How many requests in the window answered 429 by a security definition\'s rate limit raise an alert.',
    'throttled_calls_window': 'How long the window the throttled requests are counted over is.',
    'repeat_calls':         'How many times one session may call one tool in the window before an alert - an agent ' + \
                            'stuck in a loop calls the same tool over and over.',
    'repeat_calls_window':  'How long the window the repeated calls are counted over is.',
    'volume_budget':        'How many bytes of tool responses, added up across every call in the window, raise an alert - ' + \
                            'a count in kilobytes, megabytes or gigabytes, a fraction such as 2.5 is fine.',
    'volume_budget_window': 'How long the window the response bytes are added up over is.',
    'max_tools':            'How many tools the gateway may expose before an alert - the most capable models degrade past ' + \
                            '20 to 25 tools, and the alert stays open until the count drops.',
    'health_alerts':        'Whether the Microsoft service health feed raises alerts of its own.',
    'max_call_time':        'Calls slower than this many milliseconds count as slow.',
    'auth_failures':        'How many authentication failures in the window raise an alert.',
    'auth_failures_window': 'How long the window the authentication failures are counted over is.',
    'server_errors':        'The share of calls answered with a 5xx status, in percent, that raises an alert.',
    'server_errors_window': 'How long the window the 5xx responses are counted over is.',
    'client_errors':        'How many calls answered with a 4xx status other than 401 or 403 raise an alert.',
    'client_errors_window': 'How long the window the 4xx responses are counted over is.',
    'latency_window':       'How long the window the response times are averaged over is.',
    'status_codes':         'The status codes that count, comma-separated - three-digit codes such as 401 or 403 ' + \
                            'and whole classes such as 4xx or 5xx.',
    'status_code_threshold': 'How many responses with one of the status codes in the window raise an alert.',
    'status_codes_window':  'How long the window the responses are counted over is.',
    'connection_failures':  'How many calls that failed before any response arrived - a timeout, a refused connection, ' + \
                            'a TLS failure - raise an alert.',
    'connection_failures_window': 'How long the window the connection failures are counted over is.',
    'dlq_messages':         'How many messages in the connection\'s DLQ raise an alert - one is one message somebody has to ' + \
                            'look at, and the alert stays open until the DLQ is emptied.',
    'queue_depth':          'How many messages waiting in the connection\'s queue raise an alert - a deep queue is a receiving ' + \
                            'system that has been unavailable for a while.',
    'fault_codes':          'The SOAP fault codes that count, comma-separated - Receiver and Server are the endpoint\'s own faults, ' + \
                            'Sender and Client the caller\'s, and a code of the endpoint\'s own is written with its prefix, e.g. x:Timeout.',
    'fault_threshold':      'How many faults with one of the fault codes in the window raise an alert.',
    'faults_window':        'How long the window the faults are counted over is.',
    'outcome_codes':        'The FHIR OperationOutcome issue codes that count, comma-separated - exception, transient, timeout, ' + \
                            'throttled, lock-error, no-store and too-costly are the server\'s own trouble, invalid, required and value ' + \
                            'a wrong request, not-found a missing resource, security, login, forbidden and expired a refused caller.',
    'outcome_threshold':    'How many OperationOutcomes with one of the issue codes in the window raise an alert.',
    'outcomes_window':      'How long the window the OperationOutcomes are counted over is.',
    'ack_codes':            'The negative acknowledgment codes that count, comma-separated - AE and CE say the service failed ' + \
                            'to process a message, AR and CR that the message was rejected.',
    'ack_threshold':        'How many negative acknowledgments with one of the codes in the window raise an alert.',
    'acks_window':          'How long the window the acknowledgments are counted over is.',
    'truncations':          'How many responses cut short in the window raise an alert - a completion the provider stopped ' + \
                            'generating at its token limit, or a tool response the gateway\'s size cap trimmed, so the reply ' + \
                            'arrived with a 200 but is incomplete.',
    'truncations_window':   'How long the window the truncated responses are counted over is.',
    'refusals':             'How many refused completions in the window raise an alert - the provider declined to answer ' + \
                            'or a content filter blocked the prompt or the reply, most of them arriving with a 200.',
    'refusals_window':      'How long the window the refusals are counted over is.',
    'token_budget':         'How many tokens, input and output added up across every call, raise an alert - a count in ' + \
                            'thousands, millions or billions, a fraction such as 2.5 is fine.',
    'token_budget_window':  'How long the window the tokens are added up over is.',
    'traffic_expected':     'Whether a channel or a gateway that receives no requests for the time below raises an alert.',
    'silence_window':       'How long the channel or the gateway may go without a request, in minutes, hours or days.',
    'silence_slots':        'The ranges of the day with a silence and a switch of their own.',
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
    LLM_Connection_Field:   'The LLM connection that explains the alerts when Use LLM is on.',
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
    as config_map lists them, the email connection, the LLM connection.
    """
    out:'strlist' = [Is_Active_Field]

    for field in config_map.type_fields[alert_type]:
        out.append(field['name'])

    out.append(Email_Connection_Field)
    out.append(LLM_Connection_Field)

    return out

# ################################################################################################################################

def get_field_kinds(alert_type:'str') -> 'strstrdict':
    """ The kind of each field of an alert type - active, email, llm, or one of config_map's kinds.
    """
    out:'strstrdict' = {Is_Active_Field: Kind_Active}

    for field in config_map.type_fields[alert_type]:
        out[field['name']] = field['kind']

    out[Email_Connection_Field] = Kind_Email
    out[LLM_Connection_Field] = Kind_LLM

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
    out[LLM_Connection_Field] = LLM_Connection_Default

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

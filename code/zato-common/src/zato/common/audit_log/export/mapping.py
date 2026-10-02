# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from calendar import timegm
from dataclasses import dataclass
from datetime import datetime

# OpenTelemetry
from opentelemetry.proto.common.v1.common_pb2 import AnyValue, ArrayValue, KeyValue
from opentelemetry.proto.logs.v1.logs_pb2 import LogRecord, SEVERITY_NUMBER_ERROR, SEVERITY_NUMBER_INFO, \
     SEVERITY_NUMBER_WARN

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.common import AuditOutcome
from zato.common.audit_log.export.data import build_data_attributes, build_payload_attributes, has_data_export

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What every column and attr attribute name starts with
    Prefix      = 'zato.audit'
    Attr_Prefix = 'zato.audit.attr'

    # The event's own id in the audit database
    Event_ID = 'zato.audit.event_id'

    # The standard names of the severities
    Severity_Info  = 'INFO'
    Severity_Warn  = 'WARN'
    Severity_Error = 'ERROR'

# ################################################################################################################################
# ################################################################################################################################

# The columns that become attributes - data has its own mapping and server_name is a resource attribute
_columns = (
    'source', 'event_type', 'object_name', 'cid', 'cid_sequence', 'msg_id', 'correl_id', 'ext_client_id', 'endpoint',
    'sub_key', 'size', 'priority', 'outcome', 'status', 'application_outcome', 'classification', 'duration_ms',
    'pub_time_iso',
)

_info  = (SEVERITY_NUMBER_INFO,  ModuleCtx.Severity_Info)
_warn  = (SEVERITY_NUMBER_WARN,  ModuleCtx.Severity_Warn)
_error = (SEVERITY_NUMBER_ERROR, ModuleCtx.Severity_Error)

# The severity of each outcome any writer uses
severity_by_outcome:'stranydict' = {
    '':                                          _info,
    AuditOutcome.OK:                             _info,
    AuditOutcome.Running:                        _info,
    AuditOutcome.Expired:                        _warn,
    AuditOutcome.Error:                          _error,
    SCHEDULER.OUTCOME.TIMEOUT:                   _error,
    SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT: _warn,
}

_nanoseconds_per_second      = 1_000_000_000
_nanoseconds_per_microsecond = 1000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class QueuedEvent:

    # The event as it was written
    event_id: int
    values:   'stranydict'
    attrs:    'stranydict'
    bodies:   'stranydict'

    # When it was handed to the export
    observed_ns: int

    # Whether its object sends payloads along
    is_payload_active: bool

# ################################################################################################################################
# ################################################################################################################################

def _iso_to_ns(value:'str') -> 'int':
    """ Turns an event's UTC time in ISO format into nanoseconds since the epoch.
    """
    parsed = datetime.fromisoformat(value)
    seconds = timegm(parsed.utctimetuple())

    out = seconds * _nanoseconds_per_second + parsed.microsecond * _nanoseconds_per_microsecond
    return out

# ################################################################################################################################

def get_severity(outcome:'str') -> 'anytuple':
    """ Returns the severity number and text of an outcome.
    """
    out = severity_by_outcome[outcome]
    return out

# ################################################################################################################################

def _bool_value(value:'bool') -> 'AnyValue':
    out = AnyValue(bool_value=value)
    return out

def _str_value(value:'str') -> 'AnyValue':
    out = AnyValue(string_value=value)
    return out

def _int_value(value:'int') -> 'AnyValue':
    out = AnyValue(int_value=value)
    return out

def _float_value(value:'float') -> 'AnyValue':
    out = AnyValue(double_value=value)
    return out

def _tuple_value(value:'anytuple') -> 'AnyValue':
    items = []
    for item in value:
        items.append(to_any_value(item))
    out = AnyValue(array_value=ArrayValue(values=items))
    return out

# The OTLP form of each attribute type - bool has its own entry so it is never taken for an int
_any_value_by_type = {
    bool:  _bool_value,
    str:   _str_value,
    int:   _int_value,
    float: _float_value,
    tuple: _tuple_value,
    list:  _tuple_value,
}

# ################################################################################################################################

def to_any_value(value:'any_') -> 'AnyValue':
    """ Turns one attribute value into its OTLP form - anything that is not a known type travels as its text,
    so one unusual value never costs the record it is part of.
    """
    value_type = type(value)

    if builder := _any_value_by_type.get(value_type):
        out = builder(value)
    else:
        out = _str_value(str(value))

    return out

# ################################################################################################################################

def to_key_values(attributes:'stranydict') -> 'anylist':
    """ Turns a dict of attributes into their OTLP form.
    """
    out:'anylist' = []

    for key, value in attributes.items():
        any_value = to_any_value(value)
        out.append(KeyValue(key=key, value=any_value))

    return out

# ################################################################################################################################

def build_attributes(event:'QueuedEvent', max_payload_size:'int') -> 'stranydict':
    """ Builds all the attributes of one event's record - its columns, its attrs, its data and, if its object
    sends them, its payloads.
    """
    values = event.values

    out:'stranydict' = {
        ModuleCtx.Event_ID: event.event_id,
    }

    # Columns, with empty strings left out ..
    for name in _columns:
        value = values[name]
        if value == '':
            continue
        out[f'{ModuleCtx.Prefix}.{name}'] = value

    # .. attrs with their original types, except that a missing value is not an attribute ..
    for name, value in event.attrs.items():
        if value is None:
            continue
        out[f'{ModuleCtx.Attr_Prefix}.{name}'] = value

    # .. the data document's exported keys ..
    source = values['source']
    event_type = values['event_type']

    if has_data_export(source, event_type):
        build_data_attributes(source, event_type, values['data'], out)

    # .. and payloads only for an object that sends them.
    elif event.is_payload_active:
        build_payload_attributes(values['data'], event.bodies, max_payload_size, out)

    return out

# ################################################################################################################################

def build_log_record(event:'QueuedEvent', max_payload_size:'int') -> 'LogRecord':
    """ Builds the OTLP log record of one audit event.
    """
    values = event.values

    severity_number, severity_text = get_severity(values['outcome'])

    # The one-line message a log viewer shows
    body = '{} {} {} {}'.format(values['source'], values['event_type'], values['object_name'], values['outcome'])

    attributes = build_attributes(event, max_payload_size)
    key_values = to_key_values(attributes)
    time_unix_nano = _iso_to_ns(values['event_time_iso'])
    event_name = f'{ModuleCtx.Prefix}.' + values['event_type']

    out = LogRecord(
        time_unix_nano=time_unix_nano,
        observed_time_unix_nano=event.observed_ns,
        severity_number=severity_number,
        severity_text=severity_text,
        body=_str_value(body),
        attributes=key_values,
        event_name=event_name,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

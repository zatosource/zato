# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The measurement defaults every fact producer shares, the resting fact each one
# starts from and the newest-failing-event reads the rate producers attach to
# their facts. The thresholds live in the alert rules - the rule engine decides
# what the measures mean, the collectors only report them.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import is_event_type_resubmittable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The window a source with no window rule of its own is measured over - each type's
# rules carry their own window_seconds default and the sweep hands those to the collectors.
Default_Window_Seconds = 300

# A health check runs on an interval a person chose, which reaches into the hours,
# so the health sources are measured over an hour unless the sweep says otherwise.
Health_Window_Seconds = 3600

# The event types the outstanding measures pair up - sent-not-acked is the canonical absence check.
Default_Begin_Event_Type = AuditEvent.Message_Sent
Default_End_Event_Type   = AuditEvent.Ack_Received

# How many newest outcomes of one object the consecutive-failure measure looks at.
Default_Consecutive_Depth = 3

# The probe sources - each probe collector reads the events one probe job writes.
Probe_Source_Certificate      = AuditSource.Certificate
Probe_Source_Microsoft_Health = AuditSource.Microsoft_Health
Probe_Source_Test_Transfer    = AuditSource.Test_Transfer

# The attr the certificate probe writes its days-left measure under.
Attr_Days_Left = 'days_left'

# The measures a window drives - a duration field of the config map names the ones it is the window of,
# and the merger runs each collector over the window of its own measure.
Measure_Error_Rate    = 'error_rate'
Measure_Latency       = 'latency'
Measure_Auth_Failures = 'auth_failures'
Measure_Client_Errors = 'client_errors'
Measure_Server_Errors = 'server_errors'
Measure_Silence       = 'silence'
Measure_File_Runs     = 'file_runs'

# The measures of an outgoing connection's responses - how many came with each status code
# and how many calls failed before any response arrived
Measure_Status_Codes        = 'status_codes'
Measure_Connection_Failures = 'connection_failures'

# The key a merged fact carries the window of each of its measures under
Window_Seconds_By_Measure_Key = 'window_seconds_by_measure'

# The one event type of a source that carries a call's outcome - a channel writes a request
# event and a response event per call, and only the response says how the call went.
# A source absent from here has every one of its events counted.
response_event_type_by_source = {
    AuditSource.REST_Channel: AuditEvent.Response_Sent,
    AuditSource.SOAP_Channel: AuditEvent.Response_Sent,
}

# The channels - the sources with a response event, which are the ones whose rows carry alert settings of their own
channel_sources = tuple(response_event_type_by_source)

# ################################################################################################################################
# ################################################################################################################################

def is_source(source:'str') -> 'any_':
    """ The predicate picking the rows of one audit source.
    """
    out = event_table.c.source == source
    return out

# ################################################################################################################################

def is_object(object_name:'str') -> 'any_':
    """ The predicate picking the rows about one object.
    """
    out = event_table.c.object_name == object_name
    return out

# ################################################################################################################################

def is_failed() -> 'any_':
    """ The predicate picking the rows that failed.
    """
    out = event_table.c.outcome == AuditOutcome.Error
    return out

# ################################################################################################################################

def is_recent(window_start_iso:'str') -> 'any_':
    """ The predicate picking the rows from the start of a window onwards.
    """
    out = event_table.c.event_time_iso >= window_start_iso
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_fact(source:'str', object_name:'str') -> 'stranydict':
    """ One per-object fact in its resting state - every measure present, every measure zero,
    so a rule referencing any of them always finds a value.
    """
    out = {
        'source': source,
        'object_name': object_name,
        'error_rate': 0.0,
        'error_count': 0,
        'total_count': 0,
        'window_seconds': 0,
        Window_Seconds_By_Measure_Key: {},
        'outstanding': 0,
        'oldest_waiting_seconds': 0,
        'silent_seconds': 0,

        # How many of the object's newest outcomes are errors, without a break -
        # the measure behind every connection-down rule.
        'consecutive_failures': 0,

        # The average duration of the object's completed calls within the window.
        'avg_duration_ms': 0,

        # How many authentication failures the window holds - a channel's 401 and 403 responses count here too.
        'auth_failure_count': 0,

        # The failed responses of a channel by what they say about the caller and the service -
        # every 4xx other than 401 and 403 is the caller's, every 5xx the service's, the rate
        # being the share of 5xx among the channel's responses in the window.
        'client_error_count': 0,
        'server_error_count': 0,
        'server_error_rate': 0.0,

        # The responses of an outgoing connection - how many arrived with each status code, e.g. {'503': 2},
        # how many of them carried a code the connection alerts on and how many calls failed before
        # any response arrived, be it a timeout, a refused connection or a TLS failure.
        'status_counts': {},
        'status_code_count': 0,
        'connection_failure_count': 0,

        # How many days the object's TLS certificate has left. Zero means unmeasured,
        # which is why the certificate rules also require a value of at least one.
        'cert_days_left': 0,

        # The health state the remote service reports about itself - empty means unmeasured.
        'health_state': '',

        # Whether the object's newest test transfer check failed.
        'test_transfer_failed': 0,

        # The scheduler measures - how late the job's runs start and how far past
        # its own interval the newest run is. A ratio of 2.0 means twice the interval
        # has passed with no run.
        'start_delay_ms': 0,
        'overdue_ratio': 0.0,

        # The file transfer arrival measures - how long ago a schedule's newest file
        # arrived and how far past the schedule's own arrival window that moment is.
        'seconds_since_last_arrival': 0,
        'arrival_overdue_ratio': 0.0,

        # The daily expectation and run facts of a file transfer schedule.
        'expected_files_missing': 0,
        'delivered_today': 0,
        'last_run_status': '',
        'list_failed_streak': 0,
        'runs_failed_in_window': 0,
        'failed_files_in_window': 0,
        'runs_interrupted_in_window': 0,

        # The quarantine and verification facts of a file transfer connection.
        'quarantined_count': 0,
        'verify_failed_count': 0,

        # The id of the object's newest failing event and whether that event's type
        # can be resubmitted per its source's declaration - what lets an alert
        # deep-link straight at the message that failed.
        'last_error_event_id': 0,
        'is_resubmittable': 0,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_newest_error_events(
    engine:'Engine',
    *,
    window_start_iso:'str' = '',
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dict':
    """ The newest failing event of each (source, object) pair - its id and event type,
    keyed by the pair. The type is what says whether that failure can be resubmitted
    from the audit log page.
    """

    # Our response to produce
    out:'dict' = {}

    conditions = [
        event_table.c.outcome == AuditOutcome.Error,
    ]

    # The optional criteria narrow the measures only when set
    if window_start_iso:
        conditions.append(event_table.c.event_time_iso >= window_start_iso)

    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    # The newest failing event of each pair is the one with the highest id
    latest_ids = select(func.max(event_table.c.id)).where(and_(*conditions)).group_by(
        event_table.c.source, event_table.c.object_name)

    statement = select(
        event_table.c.id,
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.event_type,
    ).where(event_table.c.id.in_(latest_ids))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for event_id, row_source, row_object_name, event_type in rows:
        out[(row_source, row_object_name)] = (event_id, event_type)

    return out

# ################################################################################################################################

def apply_newest_error(fact:'stranydict', newest_errors:'dict') -> 'None':
    """ Puts the fact's newest failing event on it - its id, and whether its type
    is resubmittable per the source's own declaration.
    """
    key = (fact['source'], fact['object_name'])

    # An object whose window holds no failing event has nothing to point at
    if key not in newest_errors:
        return

    event_id, event_type = newest_errors[key]

    fact['last_error_event_id'] = event_id

    if is_event_type_resubmittable(fact['source'], event_type):
        fact['is_resubmittable'] = 1

# ################################################################################################################################
# ################################################################################################################################

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
from sqlalchemy import and_, func, or_, select

# Zato
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import is_event_type_resubmittable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, intnone, stranydict
    any_ = any_
    Engine = Engine
    intnone = intnone
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

# The measure of an outgoing SOAP connection's faults - how many responses came as a fault of each fault code
Measure_SOAP_Faults = 'soap_faults'

# The measure of an outgoing FHIR connection's operation outcomes - how many responses came as an OperationOutcome of each issue code
Measure_Operation_Outcomes = 'operation_outcomes'

# The measure of the negative acknowledgments of MLLP - how many acks a channel sent, or an outgoing connection
# was answered, with each negative code
Measure_Ack_Codes = 'ack_codes'

# The measures of an outgoing LLM connection's completions - how many tokens they used, input and output added up,
# how many were cut short by the token limit and how many the provider refused, the last two arriving as an HTTP 200
Measure_Tokens      = 'tokens'
Measure_Truncations = 'truncations'
Measure_Refusals    = 'refusals'

# The measures of an MCP gateway's tool calls - the calls naming a tool the gateway does not have or arguments
# its schema refuses, the responses a safeguard or the size cap refused, the callers a rate limit answered 429,
# one session calling one tool over and over, the responses the size cap cut short and the bytes of every response
Measure_Invalid_Calls    = 'invalid_calls'
Measure_Rejections       = 'rejections'
Measure_Throttled        = 'throttled_calls'
Measure_Repeat_Calls     = 'repeat_calls'
Measure_MCP_Truncations  = 'mcp_truncations'
Measure_Volume           = 'volume'

# The key a merged fact carries the window of each of its measures under
Window_Seconds_By_Measure_Key = 'window_seconds_by_measure'

# The one event type of a source that carries a call's outcome - a channel writes a request
# event and a response event per call, an MLLP channel a message-received and an ack-sent one, an outgoing
# MLLP connection a message-sent and an ack-received one, an outgoing
# REST or SOAP connection a request-sent and a response-received one, as does each ping of its health check,
# and only the response says how the call went. A source absent from here has every one of its events counted.
response_event_type_by_source = {
    AuditSource.REST_Channel:         AuditEvent.Response_Sent,
    AuditSource.SOAP_Channel:         AuditEvent.Response_Sent,
    AuditSource.MLLP_Channel:         AuditEvent.Ack_Sent,
    AuditSource.MLLP_Outgoing:        AuditEvent.Ack_Received,
    AuditSource.REST_Outgoing:        AuditEvent.Response_Received,
    AuditSource.SOAP_Outgoing:        AuditEvent.Response_Received,
    AuditSource.REST_Outgoing_Health: AuditEvent.Response_Received,
    AuditSource.SOAP_Outgoing_Health: AuditEvent.Response_Received,
    AuditSource.FHIR:                 AuditEvent.Response_Received,
    AuditSource.FHIR_Health:          AuditEvent.Response_Received,

    # An LLM connection writes one row per call, the response one, so nothing is lost by naming it here,
    # and the outgoing status collector reads every source it counts through this map
    AuditSource.LLM:                  AuditEvent.Response_Received,

    # An MCP gateway writes one row per request, and only its tool calls say how the backend fares -
    # an initialize or a tools/list row counted alongside them would water down every rate
    AuditSource.MCP:                  AuditEvent.MCP_Tools_Call,
}

# Which row of a call's pair can be sent again, by the row the failure was recorded on. A call
# fails on its response and what goes out again is its request.
resubmit_event_type_by_response = {
    AuditSource.REST_Outgoing: {AuditEvent.Response_Received: AuditEvent.Request_Sent},
    AuditSource.SOAP_Outgoing: {AuditEvent.Response_Received: AuditEvent.Request_Sent},
    AuditSource.FHIR:          {AuditEvent.Response_Received: AuditEvent.Request_Sent},
    AuditSource.MLLP_Outgoing: {AuditEvent.Ack_Received:      AuditEvent.Message_Sent},
}

# The one event type a source's failure streak is counted over - a source absent from here has every
# stream of its own counted and reports the highest. An MCP gateway's auth-failed and rate-limited rows
# are error rows about its callers, not its backend, so its streak is its tool calls' alone.
streak_event_type_by_source = {
    AuditSource.MCP: AuditEvent.MCP_Tools_Call,
}

# The event a channel writes the moment a call arrives - its newest one says when the channel last heard from anyone.
# An MCP gateway's is its tool call, so a gateway agents keep initializing against but never call is silent.
request_event_type_by_source = {
    AuditSource.REST_Channel: AuditEvent.Request_Received,
    AuditSource.SOAP_Channel: AuditEvent.Request_Received,
    AuditSource.MLLP_Channel: AuditEvent.Message_Received,
    AuditSource.MCP:          AuditEvent.MCP_Tools_Call,
}

# The channels - the sources whose rows are the calls a service received, and whose HTTPSOAP rows carry
# alert settings under the channels type
channel_sources = (AuditSource.REST_Channel, AuditSource.SOAP_Channel)

# Every channel - the HTTP ones and the MLLP channels, whose generic rows carry alert settings under the
# mllp_channel type - the sources whose rows name the service that answered and the caller that asked ..
all_channel_sources = (AuditSource.REST_Channel, AuditSource.SOAP_Channel, AuditSource.MLLP_Channel)

# .. and whose silence is measured, each off its own request event - the MCP gateways among them,
# whose generic rows carry alert settings under the mcp type
silence_sources = all_channel_sources + (AuditSource.MCP,)

# The outgoing connections whose responses are counted by their status code - the HTTPSOAP rows carrying
# alert settings under the rest and soap types, the FHIR generic connections under the fhir type and the LLM
# ones under the llm type, whose wrapper writes one row per call with the provider's status
outgoing_sources = (AuditSource.REST_Outgoing, AuditSource.SOAP_Outgoing, AuditSource.FHIR, AuditSource.LLM)

# The sources whose acknowledgments are counted by their code - the acks an MLLP channel sent back and
# the ones an outgoing MLLP connection was answered, each read off its own response event
ack_sources = (AuditSource.MLLP_Channel, AuditSource.MLLP_Outgoing)

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

def is_outcome_row() -> 'any_':
    """ The predicate picking the rows that say how a call went - every row of a source without a response
    event type, and the response rows alone of a source with one, so an MCP gateway's initialize, tools/list
    and auth-failed rows never stand in for its tool calls.
    """
    response_sources = list(response_event_type_by_source)

    alternatives = [event_table.c.source.not_in(response_sources)]

    for response_source, response_event_type in response_event_type_by_source.items():
        alternatives.append(and_(
            event_table.c.source == response_source,
            event_table.c.event_type == response_event_type,
        ))

    out = or_(*alternatives)
    return out

# ################################################################################################################################

def is_streak_row() -> 'any_':
    """ The predicate picking the rows a failure streak is counted over - every row of every source but the
    gateways, whose rejected credentials and throttled callers are error rows of their own types and would
    otherwise read as the backend failing, so a gateway's streak is counted over its tool calls alone.
    """
    streak_sources = list(streak_event_type_by_source)

    alternatives = [event_table.c.source.not_in(streak_sources)]

    for streak_source, streak_event_type in streak_event_type_by_source.items():
        alternatives.append(and_(
            event_table.c.source == streak_source,
            event_table.c.event_type == streak_event_type,
        ))

    out = or_(*alternatives)
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
        # how many of them carried a code the connection alerts on, by code and in all, and how many calls
        # failed before any response arrived, be it a timeout, a refused connection or a TLS failure.
        'status_counts': {},
        'status_code_counts': {},
        'status_code_count': 0,
        'connection_failure_count': 0,

        # The faults of an outgoing SOAP connection - how many arrived with each fault code, e.g. {'Receiver': 2},
        # how many of them carried a code the connection alerts on, by code and in all. A fault is counted
        # here by its code and never among the status codes above. An outgoing FHIR connection's OperationOutcomes
        # are counted the same way under the same first key, by their issue code, and the ones the connection
        # alerts on under the two keys after them, and so are the negative acks an MLLP channel sent, by their
        # MSA-1 code, the ones the channel alerts on under the last two.
        'fault_counts': {},
        'fault_code_counts': {},
        'fault_count': 0,
        'outcome_code_counts': {},
        'outcome_count': 0,
        'ack_code_counts': {},
        'ack_count': 0,

        # The completions of an LLM connection - the tokens its calls used within the window, in all and
        # split into the prompt's and the answer's, how many answers the provider cut short for running out
        # of tokens and how many it declined to give, both of which arrive as an HTTP 200.
        'token_count': 0,
        'input_token_count': 0,
        'output_token_count': 0,
        'truncation_count': 0,
        'refusal_count': 0,

        # The tool calls of an MCP gateway - how many named a tool the gateway does not have or passed arguments
        # its schema refused, how many responses a safeguard or the size cap refused, how many callers a rate
        # limit answered 429, how many times one session called one tool the most and which session and tool
        # that was, the bytes of every response added up and how many tools the gateway exposes right now.
        # The responses the size cap cut short count under truncation_count above.
        'invalid_call_count': 0,
        'rejection_count': 0,
        'throttled_count': 0,
        'repeat_call_count': 0,
        'repeat_call_tool': '',
        'repeat_call_session': '',
        'volume_bytes': 0,
        'tool_count': 0,

        # The queue delivery of an outgoing connection - how many messages wait in its queue and how many its DLQ
        # holds right now, both read off the connection itself rather than the audit log, so neither has a window
        'queue_depth': 0,
        'dlq_depth': 0,

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
    """ The newest failing event of each (source, object) pair - its id, event type and
    correlation id, keyed by the pair. The type is what says whether that failure can be
    resubmitted from the audit log page, the correlation id what finds its request.
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
        event_table.c.cid,
    ).where(event_table.c.id.in_(latest_ids))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for event_id, row_source, row_object_name, event_type, cid in rows:
        out[(row_source, row_object_name)] = (event_id, event_type, cid)

    return out

# ################################################################################################################################

def find_paired_request_id(
    engine:'Engine',
    source:'str',
    object_name:'str',
    cid:'str',
    event_type:'str',
    before_event_id:'int',
    ) -> 'intnone':
    """ The request one failing response answers - the newest row of the request type that this
    connection wrote under the same correlation id before the failure. One service call may make
    several requests under the one correlation id, so the newest is the one that failed.
    """
    conditions = [
        event_table.c.source == source,
        event_table.c.object_name == object_name,
        event_table.c.cid == cid,
        event_table.c.event_type == event_type,
        event_table.c.id < before_event_id,
    ]

    statement = select(func.max(event_table.c.id)).where(and_(*conditions))

    with engine.connect() as connection:
        row = connection.execute(statement).first()

    # Our response to produce
    out:'intnone' = None

    # A row from before the pair existed has no such request behind it.
    if row is not None:
        out = row[0]

    return out

# ################################################################################################################################

def apply_newest_error(fact:'stranydict', newest_errors:'dict', engine:'Engine') -> 'None':
    """ Puts the fact's newest failing event on it - its id, and whether its type is resubmittable
    per the source's own declaration. A failure recorded on the response of a call points at the
    request that call went out as.
    """
    source = fact['source']
    key = (source, fact['object_name'])

    # An object whose window holds no failing event has nothing to point at
    if key not in newest_errors:
        return

    event_id, event_type, cid = newest_errors[key]

    if source in resubmit_event_type_by_response:
        paired_types = resubmit_event_type_by_response[source]

        if event_type in paired_types:
            if cid:
                paired_type = paired_types[event_type]
                paired_id = find_paired_request_id(engine, source, fact['object_name'], cid, paired_type, event_id)

                # A response whose request is gone keeps pointing at itself.
                if paired_id is not None:
                    event_id = paired_id
                    event_type = paired_type

    fact['last_error_event_id'] = event_id

    if is_event_type_resubmittable(source, event_type):
        fact['is_resubmittable'] = 1

# ################################################################################################################################
# ################################################################################################################################

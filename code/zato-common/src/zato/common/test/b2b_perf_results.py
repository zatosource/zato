# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import loads
from math import ceil

# Zato
from zato.common.test.b2b_perf_common import Max_Ack_Latency_P99_Ms, Max_Commits_Per_Second, Max_Statements_Per_Second, \
    MessageKind, Min_Transactions_Per_Second, PerfRole, RecordType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, floatnone, intlist, stranydict, strlist
    anydict = anydict
    floatnone = floatnone
    intlist = intlist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

floatlist     = list[float]
strtracedict  = dict[str, 'MessageTrace']
recordlist    = list['stranydict']

# ################################################################################################################################
# ################################################################################################################################

_milliseconds_per_second = 1000

_kilobytes_per_megabyte = 1024

# A transaction due within one interval of either end of the measurement window may be handed over on either side of it.
_window_edge_transactions = 2

# The kinds of message that start a business transaction, and the kind of the message that completes each.
_initiating_kinds = {
    MessageKind.Request: MessageKind.Response,
    MessageKind.Notification: MessageKind.Signal,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessageTrace:
    """ What happened to one message during a run, as the records of both parties have it.
    """
    message_id: str
    kind:       str = ''
    ref:        str = ''

    # When the message was handed over, and when its acknowledgment ended its exchange, as seconds since the epoch.
    started_at: float = 0.0
    acked_at:   'floatnone' = None

    # How many deliveries the sender made, and whether it gave up.
    attempts:  int = 0
    is_failed: bool = False

    # How many times the application of the receiver processed it, first and again as a possible duplicate.
    deliveries:   int = 0
    redeliveries: int = 0
    delivered_at: 'floatnone' = None

    # The faults of the partner, and where the business transaction the message refers to stands after it.
    faults:      'strlist'
    match_state: str = ''
    is_matched:  bool = False

    # When the message first arrived at its receiver, when the receiver answered it on that connection,
    # and how long the answer took.
    arrived_at:      'floatnone' = None
    received_at:     'floatnone' = None
    receive_seconds: 'floatnone' = None

    # The deadline of the business transaction of the message, and when the check that ended the transaction started,
    # if the deadline passed.
    deadline:     'floatnone' = None
    timed_out_at: 'floatnone' = None

    @property
    def is_delivered(self) -> 'bool':
        total = self.deliveries + self.redeliveries

        out = total > 0
        return out

# ################################################################################################################################

@dataclass(init=False)
class PerfResult:
    """ The measurements of one run.
    """
    window_start:     float
    window_end:       float
    duration_seconds: float

    # The transactions started in the measurement window, and how many of them completed.
    offered_transactions:    int
    transactions:            int
    transactions_per_second: float

    # The acknowledgment latency of the messages sent in the measurement window.
    ack_p50_ms: float
    ack_p95_ms: float
    ack_p99_ms: float

    # How long the receivers took to answer the messages sent in the measurement window, from arrival to answer.
    receive_p50_ms: float
    receive_p99_ms: float

    # What the engine of the host ran in the measurement window, and the most resident memory of the host.
    statements_per_second: float
    commits_per_second:    float
    rss_max_mb:            float

    # The resends of the host, and the selects of the stored bytes of messages it ran in the whole run.
    resends:      int
    body_selects: int

    # The messages no application received, and those an application received more than once without the flag.
    lost:       'strlist'
    duplicated: 'strlist'

    traces: 'strtracedict'

# ################################################################################################################################
# ################################################################################################################################

def read_records(path:'str') -> 'recordlist':
    """ Returns the records of one party in the order it wrote them.
    """
    with open(path, encoding='utf8') as records_file:
        lines = records_file.readlines()

    out:'recordlist' = []

    for line in lines:
        record = loads(line)
        out.append(record)

    return out

# ################################################################################################################################

def percentile(values:'floatlist', fraction:'float') -> 'float':
    """ Returns the value below which the given fraction of the values fall, by the nearest rank.
    """
    if not values:
        return 0.0

    ordered = sorted(values)
    count = len(ordered)
    rank = ceil(fraction * count)
    index = max(rank, 1) - 1

    out = ordered[index]
    return out

# ################################################################################################################################

def _trace(traces:'strtracedict', message_id:'str') -> 'MessageTrace':

    if not (out := traces.get(message_id)):
        out = MessageTrace()
        out.message_id = message_id
        out.faults = []
        traces[message_id] = out

    return out

# ################################################################################################################################

def _apply_sent(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.kind = record['kind']
    trace.ref = record['ref']
    trace.started_at = record['started_at']
    trace.attempts += 1

# ################################################################################################################################

def _apply_attempt(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.attempts += 1

# ################################################################################################################################

def _apply_ack(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.acked_at = record['at']

# ################################################################################################################################

def _apply_failed(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.is_failed = True

# ################################################################################################################################

def _apply_delivered(trace:'MessageTrace', record:'stranydict') -> 'None':

    if record['is_possible_duplicate']:
        trace.redeliveries += 1
    else:
        trace.deliveries += 1

    if trace.delivered_at is None:
        trace.delivered_at = record['at']

# ################################################################################################################################

def _apply_fault(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.faults.append(record['fault'])

# ################################################################################################################################

def _apply_matched(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.is_matched = True
    trace.match_state = record['state']

# ################################################################################################################################

def _apply_received(trace:'MessageTrace', record:'stranydict') -> 'None':

    # A message posted again is answered again, and only its first arrival counts.
    if trace.arrived_at is None:
        trace.arrived_at = record['arrived_at']
        trace.received_at = record['at']
        trace.receive_seconds = record['at'] - record['arrived_at']

# ################################################################################################################################

def _apply_timed_out(trace:'MessageTrace', record:'stranydict') -> 'None':
    trace.deadline = record['deadline']
    trace.timed_out_at = record['checked_at']

# ################################################################################################################################

# How each record of a message changes its trace.
_appliers = {
    RecordType.Sent: _apply_sent,
    RecordType.Attempt: _apply_attempt,
    RecordType.Ack: _apply_ack,
    RecordType.Failed: _apply_failed,
    RecordType.Delivered: _apply_delivered,
    RecordType.Fault: _apply_fault,
    RecordType.Matched: _apply_matched,
    RecordType.Received: _apply_received,
    RecordType.Timed_Out: _apply_timed_out,
}

# ################################################################################################################################

def build_traces(records:'recordlist') -> 'strtracedict':
    """ Returns the trace of each message the records of both parties name.
    """
    out:'strtracedict' = {}

    for record in records:
        if applier := _appliers.get(record['type']):
            trace = _trace(out, record['id'])
            applier(trace, record)

    return out

# ################################################################################################################################

def find_summary(records:'recordlist', role:'str') -> 'stranydict':
    """ Returns the last summary a party wrote, which is that of the process that ran until the end.
    """
    summaries:'recordlist' = []

    for record in records:
        if record['type'] == RecordType.Summary:
            if record['role'] == role:
                summaries.append(record)

    out = summaries[-1]
    return out

# ################################################################################################################################

def _completed_refs(traces:'strtracedict') -> 'set[str]':
    """ Returns the messages that a delivered response or a delivered signal refers to.
    """
    out:'set[str]' = set()

    for trace in traces.values():
        if trace.kind not in _initiating_kinds:
            if trace.is_delivered:
                out.add(trace.ref)

    return out

# ################################################################################################################################

def _is_in_window(trace:'MessageTrace', window_start:'float', window_end:'float') -> 'bool':

    if trace.started_at < window_start:
        out = False
    else:
        out = trace.started_at < window_end

    return out

# ################################################################################################################################

def compute_result(
    records:'recordlist',
    window_start:'float',
    window_end:'float',
    rss_samples_kb:'intlist',
    ) -> 'PerfResult':
    """ Returns the measurements of a run from the records of both parties and the samples of the memory of the host.
    """
    traces = build_traces(records)
    completed_refs = _completed_refs(traces)
    summary = find_summary(records, PerfRole.Host)

    duration = window_end - window_start

    offered = 0
    completed = 0
    latencies:'floatlist' = []
    receive_latencies:'floatlist' = []
    lost:'strlist' = []
    duplicated:'strlist' = []

    for message_id, trace in traces.items():

        # A message that was handed over and that no application received is lost ..
        if trace.started_at:
            if not trace.is_delivered:
                lost.append(message_id)

        # .. one that an application received more than once without the flag is duplicated ..
        if trace.deliveries > 1:
            duplicated.append(message_id)

        if not _is_in_window(trace, window_start, window_end):
            continue

        # .. the latency counts the messages handed over in the window ..
        if trace.acked_at is not None:
            latency = trace.acked_at - trace.started_at
            latency_ms = latency * _milliseconds_per_second
            latencies.append(latency_ms)

        # .. and so does the time each receiver took to answer ..
        if trace.receive_seconds is not None:
            receive_latency_ms = trace.receive_seconds * _milliseconds_per_second
            receive_latencies.append(receive_latency_ms)

        # .. and so do the transactions.
        if trace.kind in _initiating_kinds:
            offered += 1

            if message_id in completed_refs:
                completed += 1

    if rss_samples_kb:
        rss_max_kb = max(rss_samples_kb)
    else:
        rss_max_kb = 0

    out = PerfResult()
    out.window_start = window_start
    out.window_end = window_end
    out.duration_seconds = duration
    out.offered_transactions = offered
    out.transactions = completed
    out.transactions_per_second = completed / duration
    out.ack_p50_ms = percentile(latencies, 0.50)
    out.ack_p95_ms = percentile(latencies, 0.95)
    out.ack_p99_ms = percentile(latencies, 0.99)
    out.receive_p50_ms = percentile(receive_latencies, 0.50)
    out.receive_p99_ms = percentile(receive_latencies, 0.99)
    out.statements_per_second = summary['statements'] / duration
    out.commits_per_second = summary['commits'] / duration
    out.rss_max_mb = rss_max_kb / _kilobytes_per_megabyte
    out.resends = summary['resends']
    out.body_selects = summary['body_selects']
    out.lost = lost
    out.duplicated = duplicated
    out.traces = traces

    return out

# ################################################################################################################################

def check_criteria(result:'PerfResult') -> 'strlist':
    """ Returns each criterion of a steady run that the result does not meet.
    """
    out:'strlist' = []

    required_transactions = Min_Transactions_Per_Second * result.duration_seconds
    counted_transactions = result.transactions + _window_edge_transactions

    if counted_transactions < required_transactions:
        out.append(f'{result.transactions_per_second:.1f} transactions per second, below {Min_Transactions_Per_Second}')

    if result.ack_p99_ms >= Max_Ack_Latency_P99_Ms:
        out.append(f'Acknowledgment latency p99 {result.ack_p99_ms:.0f} ms, not below {Max_Ack_Latency_P99_Ms} ms')

    if result.lost:
        out.append(f'{len(result.lost)} lost deliveries')

    if result.duplicated:
        out.append(f'{len(result.duplicated)} duplicated deliveries')

    if result.commits_per_second > Max_Commits_Per_Second:
        out.append(f'{result.commits_per_second:.1f} commits per second, above {Max_Commits_Per_Second}')

    if result.statements_per_second > Max_Statements_Per_Second:
        out.append(f'{result.statements_per_second:.1f} statements per second, above {Max_Statements_Per_Second}')

    return out

# ################################################################################################################################

def result_properties(result:'PerfResult') -> 'stranydict':
    """ Returns the measurements of a run by name, as a test reports them.
    """
    out:'stranydict' = {
        'offered_transactions': result.offered_transactions,
        'transactions': result.transactions,
        'transactions_per_second': round(result.transactions_per_second, 1),
        'ack_p50_ms': round(result.ack_p50_ms, 1),
        'ack_p95_ms': round(result.ack_p95_ms, 1),
        'ack_p99_ms': round(result.ack_p99_ms, 1),
        'receive_p50_ms': round(result.receive_p50_ms, 1),
        'receive_p99_ms': round(result.receive_p99_ms, 1),
        'statements_per_second': round(result.statements_per_second, 1),
        'commits_per_second': round(result.commits_per_second, 1),
        'rss_max_mb': round(result.rss_max_mb, 1),
        'resends': result.resends,
        'body_selects': result.body_selects,
        'lost': len(result.lost),
        'duplicated': len(result.duplicated),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

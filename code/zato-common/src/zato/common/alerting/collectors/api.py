# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The merger - runs every fact producer and folds their measures into one fact
# per (source, object) pair, with zero as the resting value, so a rule can
# reference any measure without erroring out. Each windowed measure is taken over
# the window of its own line - the type's, a source's or an object's own.

from __future__ import annotations

# Zato
from zato.common.alerting.collectors.backlogs import collect_feed_silent_facts, collect_outstanding_facts
from zato.common.alerting.collectors.channels import collect_channel_silence_facts, collect_channel_status_facts
from zato.common.alerting.collectors.common import new_fact, Default_Begin_Event_Type, Default_End_Event_Type, \
    Default_Window_Seconds, Health_Window_Seconds, Measure_Auth_Failures, Measure_Client_Errors, Measure_Error_Rate, \
    Measure_File_Runs, Measure_Latency, Measure_Server_Errors, Window_Seconds_By_Measure_Key
from zato.common.alerting.collectors.file_transfer import collect_file_transfer_facts
from zato.common.alerting.collectors.probes import collect_certificate_facts, collect_health_facts, \
    collect_test_transfer_facts
from zato.common.alerting.collectors.rates import collect_auth_failure_facts, collect_consecutive_failure_facts, \
    collect_error_rate_facts, collect_latency_facts
from zato.common.alerting.collectors.scheduler import collect_scheduler_facts
from zato.common.audit_log.common import health_sources, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict, callable_, dictlist, stranydict, strintdict, strset
    anydict = anydict
    callable_ = callable_
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strintdict = strintdict
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

def _collect_auth_failure_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ The authentication failures of every object - the failed authentication events of the sources
    that write them, and the 401 and 403 responses of the channels, which have no such event of their own.
    """
    out = collect_auth_failure_facts(engine, window_seconds, now, source=source, object_name=object_name)
    out.extend(collect_channel_status_facts(engine, window_seconds, now, source=source, object_name=object_name))

    return out

# ################################################################################################################################

# The windowed collectors by the measure that drives each - every one takes the engine, the window,
# the moment and the optional source and object to narrow to. The status collector answers three
# measures, so it runs once per measure and each run keeps the keys of its own measure alone.
_collector_by_measure:'dict[str, callable_]' = {
    Measure_Error_Rate:    collect_error_rate_facts,
    Measure_Latency:       collect_latency_facts,
    Measure_Auth_Failures: _collect_auth_failure_facts,
    Measure_Client_Errors: collect_channel_status_facts,
    Measure_Server_Errors: collect_channel_status_facts,
}

# The fact keys each windowed measure owns - what a run over one measure's window is allowed
# to say, so two runs of one collector over two windows never overwrite each other's numbers.
# The error rate's keys include the fact's window, which is what window_seconds keeps meaning.
_keys_by_measure:'dict[str, tuple[str, ...]]' = {
    Measure_Error_Rate:    ('error_rate', 'error_count', 'total_count', 'window_seconds', 'last_error_event_id',
        'is_resubmittable'),
    Measure_Latency:       ('avg_duration_ms',),
    Measure_Auth_Failures: ('auth_failure_count',),
    Measure_Client_Errors: ('client_error_count',),
    Measure_Server_Errors: ('server_error_count', 'server_error_rate'),
}

# ################################################################################################################################
# ################################################################################################################################

def _window_of(windows:'strintdict', measure:'str', default:'int') -> 'int':
    """ The window of one measure in a per-measure dict, the default when the dict has none for it.
    """
    if measure in windows:
        out = windows[measure]
    else:
        out = default

    return out

# ################################################################################################################################

def _keep_measure(fact:'stranydict', measure:'str', window_seconds:'int') -> 'stranydict':
    """ A fact reduced to what one measure's run may say - the measure's own keys and the window it was taken over.
    """
    out = {
        'source': fact['source'],
        'object_name': fact['object_name'],
        Window_Seconds_By_Measure_Key: {measure: window_seconds},
    }

    for key in _keys_by_measure[measure]:
        out[key] = fact[key]

    return out

# ################################################################################################################################

def _collect_measure(
    engine:'Engine',
    measure:'str',
    now:'datetime',
    window_seconds:'int',
    window_seconds_by_source:'anydict',
    window_seconds_by_object:'anydict',
    ) -> 'dictlist':
    """ One windowed measure over every object - the default window first, then each source with a window
    of its own for the measure again over that one, then each object with one of its own, the narrower
    run replacing what the wider one said about the same pair.
    """
    collect = _collector_by_measure[measure]

    facts = collect(engine, window_seconds, now)

    # Keyed by pair, so a narrower run replaces the wider one's fact
    by_object:'dict[tuple[str, str], stranydict]' = {}

    for fact in facts:
        by_object[(fact['source'], fact['object_name'])] = _keep_measure(fact, measure, window_seconds)

    for source, windows in window_seconds_by_source.items():

        if measure not in windows:
            continue

        source_window = windows[measure]

        # The default run of this source steps aside whole, a source with a window of its own
        # is measured over that window and nothing else
        for key in list(by_object):
            if key[0] == source:
                del by_object[key]

        for fact in collect(engine, source_window, now, source=source):
            by_object[(source, fact['object_name'])] = _keep_measure(fact, measure, source_window)

    for source, windows_by_object in window_seconds_by_object.items():
        for object_name, windows in windows_by_object.items():

            if measure not in windows:
                continue

            object_window = windows[measure]
            key = (source, object_name)

            if key in by_object:
                del by_object[key]

            for fact in collect(engine, object_window, now, source=source, object_name=object_name):
                by_object[key] = _keep_measure(fact, measure, object_window)

    # Our response to produce
    out = list(by_object.values())
    return out

# ################################################################################################################################

def _merge_facts(fact_lists:'list[dictlist]') -> 'dictlist':
    """ One merged fact per (source, object) pair - every fact list lands in the same fact of its pair,
    only the measures a producer actually took overwriting the resting zeroes, and the per-measure
    windows of every run gathered into one dict.
    """
    by_object:'dict[tuple[str, str], stranydict]' = {}

    for fact_list in fact_lists:
        for fact in fact_list:

            key = (fact['source'], fact['object_name'])

            if key not in by_object:
                by_object[key] = new_fact(fact['source'], fact['object_name'])

            merged = by_object[key]

            for name, value in fact.items():

                if name == Window_Seconds_By_Measure_Key:
                    merged[name].update(value)
                    continue

                # Only the measures this producer actually took overwrite the resting zeroes
                if value:
                    merged[name] = value

    out = list(by_object.values())
    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_facts(
    engine:'Engine',
    metrics_by_name:'stranydict',
    source:'str',
    now:'datetime',
    *,
    window_seconds:'int' = Default_Window_Seconds,
    window_seconds_by_source:'anydict | None' = None,
    window_seconds_by_object:'anydict | None' = None,
    begin_event_type:'str' = Default_Begin_Event_Type,
    end_event_type:'str' = Default_End_Event_Type,
    job_intervals:'strintdict | None' = None,
    arrival_windows:'strintdict | None' = None,
    schedule_expectations:'anydict | None' = None,
    silence_expected_names:'strset | None' = None,
    ) -> 'dictlist':
    """ Runs every fact producer and merges their measures into one fact
    per (source, object) pair - the input the alert rules match over. The per-source
    windows come from the rules' window_seconds defaults, by source and then by measure -
    a source without one is measured over window_seconds, the health sources over their own hour,
    and an object with windows of its own, by source, then by object name and then by measure, over those.
    The silence of a REST channel is measured for the channels named as expecting traffic alone.
    """
    if window_seconds_by_source is None:
        window_seconds_by_source = {}

    if window_seconds_by_object is None:
        window_seconds_by_object = {}

    if job_intervals is None:
        job_intervals = {}

    if arrival_windows is None:
        arrival_windows = {}

    if schedule_expectations is None:
        schedule_expectations = {}

    if silence_expected_names is None:
        silence_expected_names = set()

    # The health sources keep their hour unless a rule names them
    window_seconds_by_source = dict(window_seconds_by_source)

    for health_source in health_sources:
        if health_source not in window_seconds_by_source:
            window_seconds_by_source[health_source] = {
                Measure_Error_Rate: Health_Window_Seconds,
                Measure_Latency: Health_Window_Seconds,
            }

    # The counters that measure one source each take that source's window
    if AuditSource.Scheduler in window_seconds_by_source:
        scheduler_window_seconds = _window_of(window_seconds_by_source[AuditSource.Scheduler], Measure_Error_Rate, window_seconds)
    else:
        scheduler_window_seconds = window_seconds

    if AuditSource.File_Outgoing in window_seconds_by_source:
        run_window_seconds = _window_of(window_seconds_by_source[AuditSource.File_Outgoing], Measure_File_Runs, window_seconds)
    else:
        run_window_seconds = window_seconds

    # The schedules measured over a window of their own - the run facts are keyed by schedule name
    run_window_seconds_by_object:'strintdict' = {}

    if AuditSource.File_Outgoing in window_seconds_by_object:
        for object_name, windows in window_seconds_by_object[AuditSource.File_Outgoing].items():
            if Measure_File_Runs in windows:
                run_window_seconds_by_object[object_name] = windows[Measure_File_Runs]

    # The windowed measures, each over the windows of its own line
    windowed_fact_lists:'list[dictlist]' = []

    for measure in _collector_by_measure:
        windowed_fact_lists.append(
            _collect_measure(engine, measure, now, window_seconds, window_seconds_by_source, window_seconds_by_object))

    consecutive_facts = collect_consecutive_failure_facts(engine, now)
    outstanding_facts = collect_outstanding_facts(engine, begin_event_type, end_event_type, now)
    silent_facts = collect_feed_silent_facts(metrics_by_name, source)
    channel_silent_facts = collect_channel_silence_facts(engine, now, silence_expected_names)
    certificate_facts = collect_certificate_facts(engine, now)
    health_facts = collect_health_facts(engine, now)
    test_transfer_facts = collect_test_transfer_facts(engine, now)
    scheduler_facts = collect_scheduler_facts(engine, scheduler_window_seconds, now, job_intervals)
    file_transfer_facts = collect_file_transfer_facts(engine, now, arrival_windows, schedule_expectations, run_window_seconds,
        run_window_seconds_by_object)

    fact_lists = windowed_fact_lists + [
        consecutive_facts,
        outstanding_facts,
        silent_facts,
        channel_silent_facts,
        certificate_facts,
        health_facts,
        test_transfer_facts,
        scheduler_facts,
        file_transfer_facts,
    ]

    out = _merge_facts(fact_lists)
    return out

# ################################################################################################################################
# ################################################################################################################################

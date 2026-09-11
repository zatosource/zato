# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The merger - runs every fact producer and folds their measures into one fact
# per (source, object) pair, with zero as the resting value, so a rule can
# reference any measure without erroring out.

from __future__ import annotations

# Zato
from zato.common.alerting.collectors.backlogs import collect_feed_silent_facts, collect_outstanding_facts
from zato.common.alerting.collectors.common import Default_Begin_Event_Type, Default_End_Event_Type, \
    Default_Window_Seconds, Health_Window_Seconds
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
    from zato.common.typing_ import anydict, dictlist, stranydict, strintdict
    anydict = anydict
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

def collect_facts(
    engine:'Engine',
    metrics_by_name:'stranydict',
    source:'str',
    now:'datetime',
    *,
    window_seconds:'int' = Default_Window_Seconds,
    window_seconds_by_source:'strintdict | None' = None,
    window_seconds_by_object:'anydict | None' = None,
    begin_event_type:'str' = Default_Begin_Event_Type,
    end_event_type:'str' = Default_End_Event_Type,
    job_intervals:'strintdict | None' = None,
    arrival_windows:'strintdict | None' = None,
    schedule_expectations:'anydict | None' = None,
    ) -> 'dictlist':
    """ Runs every fact producer and merges their measures into one fact
    per (source, object) pair - the input the alert rules match over. The per-source
    windows come from the rules' window_seconds defaults, a source without one
    is measured over window_seconds, the health sources over their own hour, and an
    object with a window of its own, by source and then by object name, over that one.
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

    # The health sources keep their hour unless a rule names them
    window_seconds_by_source = dict(window_seconds_by_source)

    for health_source in health_sources:
        if health_source not in window_seconds_by_source:
            window_seconds_by_source[health_source] = Health_Window_Seconds

    # The counters that measure one source each take that source's window
    if AuditSource.Scheduler in window_seconds_by_source:
        scheduler_window_seconds = window_seconds_by_source[AuditSource.Scheduler]
    else:
        scheduler_window_seconds = window_seconds

    if AuditSource.File_Outgoing in window_seconds_by_source:
        run_window_seconds = window_seconds_by_source[AuditSource.File_Outgoing]
    else:
        run_window_seconds = window_seconds

    # The schedules measured over a window of their own - the run facts are keyed by schedule name
    if AuditSource.File_Outgoing in window_seconds_by_object:
        run_window_seconds_by_object = window_seconds_by_object[AuditSource.File_Outgoing]
    else:
        run_window_seconds_by_object = {}

    error_rate_facts = collect_error_rate_facts(engine, window_seconds, now)
    latency_facts = collect_latency_facts(engine, window_seconds, now)
    consecutive_facts = collect_consecutive_failure_facts(engine, now)
    auth_failure_facts = collect_auth_failure_facts(engine, window_seconds, now)
    outstanding_facts = collect_outstanding_facts(engine, begin_event_type, end_event_type, now)
    silent_facts = collect_feed_silent_facts(metrics_by_name, source)
    certificate_facts = collect_certificate_facts(engine, now)
    health_facts = collect_health_facts(engine, now)
    test_transfer_facts = collect_test_transfer_facts(engine, now)
    scheduler_facts = collect_scheduler_facts(engine, scheduler_window_seconds, now, job_intervals)
    file_transfer_facts = collect_file_transfer_facts(engine, now, arrival_windows, schedule_expectations, run_window_seconds,
        run_window_seconds_by_object)

    # A source with a window of its own is measured again over that window,
    # and its own measures replace the default-window ones below.
    override_error_rate_facts:'dictlist' = []
    override_latency_facts:'dictlist' = []

    for override_source, override_window in window_seconds_by_source.items():
        override_error_rate_facts.extend(collect_error_rate_facts(engine, override_window, now, source=override_source))
        override_latency_facts.extend(collect_latency_facts(engine, override_window, now, source=override_source))

    # The default-window measures of an overridden source step aside
    overridden_sources = set(window_seconds_by_source)

    kept_error_rate_facts:'dictlist' = []
    kept_latency_facts:'dictlist' = []

    for fact in error_rate_facts:
        if fact['source'] not in overridden_sources:
            kept_error_rate_facts.append(fact)

    for fact in latency_facts:
        if fact['source'] not in overridden_sources:
            kept_latency_facts.append(fact)

    error_rate_facts = kept_error_rate_facts
    latency_facts = kept_latency_facts

    error_rate_facts.extend(override_error_rate_facts)
    latency_facts.extend(override_latency_facts)

    # An object with a window of its own is measured once more over that window,
    # and its own measures replace the ones its source's window gave it.
    object_error_rate_facts:'dictlist' = []
    object_latency_facts:'dictlist' = []
    overridden_objects:'set[tuple[str, str]]' = set()

    for object_source, windows_by_object in window_seconds_by_object.items():
        for object_name, object_window in windows_by_object.items():
            overridden_objects.add((object_source, object_name))
            object_error_rate_facts.extend(
                collect_error_rate_facts(engine, object_window, now, source=object_source, object_name=object_name))
            object_latency_facts.extend(
                collect_latency_facts(engine, object_window, now, source=object_source, object_name=object_name))

    if overridden_objects:

        kept_error_rate_facts = []
        kept_latency_facts = []

        for fact in error_rate_facts:
            if (fact['source'], fact['object_name']) not in overridden_objects:
                kept_error_rate_facts.append(fact)

        for fact in latency_facts:
            if (fact['source'], fact['object_name']) not in overridden_objects:
                kept_latency_facts.append(fact)

        error_rate_facts = kept_error_rate_facts
        latency_facts = kept_latency_facts

        error_rate_facts.extend(object_error_rate_facts)
        latency_facts.extend(object_latency_facts)

    # One merged fact per (source, object) pair - later measures land in the same fact
    by_object:'dict[tuple[str, str], stranydict]' = {}

    fact_lists = (
        error_rate_facts,
        latency_facts,
        consecutive_facts,
        auth_failure_facts,
        outstanding_facts,
        silent_facts,
        certificate_facts,
        health_facts,
        test_transfer_facts,
        scheduler_facts,
        file_transfer_facts,
    )

    for fact_list in fact_lists:
        for fact in fact_list:

            key = (fact['source'], fact['object_name'])

            if key in by_object:
                merged = by_object[key]

                # Only the measures this producer actually took overwrite the resting zeroes
                for name, value in fact.items():
                    if value:
                        merged[name] = value
            else:
                by_object[key] = fact

    out = list(by_object.values())
    return out

# ################################################################################################################################
# ################################################################################################################################

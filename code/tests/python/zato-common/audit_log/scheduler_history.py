# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from os import environ

# Zato
from common import delete_all_events
from zato.common.api import SCHEDULER
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx
from zato.common.audit_log.scheduler import append_job_log_entry, record_job_complete, record_job_start, record_job_timeout
from zato.common.audit_log.scheduler_query import get_chart_data, get_history_page, get_history_since, get_job_aggregates, \
    get_log_entries, get_run_detail, get_timeline_events_since, Chart_Bucket_Count
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The job whose runs the scenario records and reads back
_job_name = 'audit.test.scheduler-job'
_job_id = 5001

# A second job proving that per-job aggregates and history are kept apart
_other_job_name = 'audit.test.other-scheduler-job'
_other_job_id = 5002

# The service the jobs invoke
_service_name = 'audit.test.scheduler-service'

# ################################################################################################################################
# ################################################################################################################################

def _start_run(audit_log:'AuditLog', job_name:'str', job_id:'int', current_run:'int', delay_ms:'int') -> 'int':
    """ Records the start of one run, returning its event id.
    """
    now = utcnow()
    planned_fire_time_iso = now.isoformat()

    out = record_job_start(
        audit_log,
        job_name,
        cid=f'cid-scheduler-{job_id}-{current_run}',
        job_id=job_id,
        current_run=current_run,
        planned_fire_time_iso=planned_fire_time_iso,
        delay_ms=delay_ms,
        service=_service_name,
    )

    assert isinstance(out, int)
    return out

# ################################################################################################################################

def _run_running_record_checks(audit_log:'AuditLog') -> 'int':
    """ Starts the first run and confirms its running record reads back the way
    the history screens expect, opening system log entry included.
    """
    event_id = _start_run(audit_log, _job_name, _job_id, 1, 250)

    page = get_history_page(_job_id, _job_name, 0, 10, '')
    records = page['records']

    assert len(records) == 1

    record = records[0]

    assert record['job_id'] == _job_id
    assert record['job_name'] == _job_name
    assert record['outcome'] == SCHEDULER.OUTCOME.RUNNING
    assert record['current_run'] == 1
    assert record['delay_ms'] == 250
    assert record['duration_ms'] is None
    assert record['error'] is None
    assert record['planned_fire_time_iso']
    assert record['actual_fire_time_iso']
    assert record['log_summary'] == {'system': 1, 'info': 0, 'warn': 0, 'error': 0}

    # A running record does not count towards the completed total
    assert page['total'] == 0

    return event_id

# ################################################################################################################################

def _run_log_entry_checks(event_id:'int') -> 'None':
    """ Appends log lines of several levels and confirms they read back in order,
    with the incremental index only ever fetching what a tail has not seen yet.
    """
    now = utcnow()
    timestamp_iso = now.isoformat()

    append_job_log_entry(event_id, timestamp_iso, 'INFO', 'Processing the input file')
    append_job_log_entry(event_id, timestamp_iso, 'WARNING', 'The input file is unusually large')
    append_job_log_entry(event_id, timestamp_iso, 'ERROR', 'Could not reach the downstream system')

    # The opening system line comes first, then the three appended above ..
    entries = get_log_entries(_job_name, 1, 0)

    assert len(entries) == 4
    assert entries[0]['level'] == 'SYSTEM'
    assert entries[1] == {'timestamp_iso': timestamp_iso, 'level': 'INFO', 'message': 'Processing the input file'}
    assert entries[2]['level'] == 'WARNING'
    assert entries[3]['level'] == 'ERROR'

    # .. and asking from an index returns only what follows it.
    entries = get_log_entries(_job_name, 1, 2)

    assert len(entries) == 2
    assert entries[0]['level'] == 'WARNING'
    assert entries[1]['level'] == 'ERROR'

# ################################################################################################################################

def _run_completion_checks(event_id:'int') -> 'None':
    """ Completes the first run and confirms the very same record now carries the final
    outcome, its duration and the closing system log line.
    """
    record_job_complete(event_id, outcome=SCHEDULER.OUTCOME.OK, duration_ms=1250, error='')

    page = get_history_page(_job_id, _job_name, 0, 10, '')
    records = page['records']

    # Still one record - the run was updated in place, not written anew
    assert len(records) == 1

    record = records[0]

    assert record['outcome'] == SCHEDULER.OUTCOME.OK
    assert record['duration_ms'] == 1250
    assert record['error'] is None

    # The run closed with its own system entry, so there are two of them now
    assert record['log_summary']['system'] == 2

    # A completed run counts towards the total
    assert page['total'] == 1

# ################################################################################################################################

def _run_error_and_timeout_checks(audit_log:'AuditLog') -> 'None':
    """ Records a failed run and a timed-out one - the failure through its event id,
    the timeout located by job id and run number, the way the scheduler process reports it.
    """

    # The second run fails with a traceback ..
    error_event_id = _start_run(audit_log, _job_name, _job_id, 2, 10)
    record_job_complete(error_event_id, outcome=SCHEDULER.OUTCOME.ERROR, duration_ms=740,
        error='Traceback (most recent call last): the downstream system rejected the request')

    # .. and the third one times out.
    _ = _start_run(audit_log, _job_name, _job_id, 3, 15)
    record_job_timeout(_job_id, 3, elapsed_ms=30000, error='Timed out after 30s')

    page = get_history_page(_job_id, _job_name, 0, 10, '')
    records = page['records']

    # Newest first - the timeout, the failure, then the first run
    assert len(records) == 3
    assert page['total'] == 3

    assert records[0]['outcome'] == SCHEDULER.OUTCOME.TIMEOUT
    assert records[0]['duration_ms'] == 30000
    assert records[0]['error'] == 'Timed out after 30s'

    assert records[1]['outcome'] == SCHEDULER.OUTCOME.ERROR
    assert records[1]['duration_ms'] == 740
    assert records[1]['error'] == 'Traceback (most recent call last): the downstream system rejected the request'

    assert records[2]['outcome'] == SCHEDULER.OUTCOME.OK

# ################################################################################################################################

def _run_outcome_filter_checks() -> 'None':
    """ Confirms an outcome filter narrows a page down to the outcomes it names.
    """
    page = get_history_page(_job_id, _job_name, 0, 10, SCHEDULER.OUTCOME.ERROR)
    records = page['records']

    assert len(records) == 1
    assert records[0]['outcome'] == SCHEDULER.OUTCOME.ERROR
    assert page['total'] == 1

# ################################################################################################################################

def _run_detail_checks() -> 'None':
    """ Confirms a single run reads back with its neighbouring run numbers,
    which is what the run detail screen's navigation is drawn out of.
    """
    detail = get_run_detail(_job_id, _job_name, 2)

    record = detail['record']

    assert record['current_run'] == 2
    assert record['outcome'] == SCHEDULER.OUTCOME.ERROR

    assert detail['prev_run'] == 1
    assert detail['next_run'] == 3

    # A run that never happened has no record and no neighbours
    detail = get_run_detail(_job_id, _job_name, 99)

    assert detail == {'record': None, 'prev_run': None, 'next_run': None}

# ################################################################################################################################

def _run_history_since_checks(since_iso:'str') -> 'None':
    """ Confirms an incremental poll returns only the records added since its marker.
    """
    result = get_history_since(_job_id, _job_name, since_iso, '')
    rows = result['rows']

    # Only the two runs recorded after the marker come back, newest first
    assert len(rows) == 2
    assert rows[0]['current_run'] == 3
    assert rows[1]['current_run'] == 2

    # The total spans the whole history regardless of the marker
    assert result['total'] == 3

# ################################################################################################################################

def _run_other_job_and_aggregate_checks(audit_log:'AuditLog') -> 'None':
    """ Runs a second job once and confirms the per-job aggregates keep the two apart -
    counts, the newest run's details and the recent-outcome strip.
    """
    other_event_id = _start_run(audit_log, _other_job_name, _other_job_id, 1, 5)
    record_job_complete(other_event_id, outcome=SCHEDULER.OUTCOME.OK, duration_ms=90, error='')

    aggregates = get_job_aggregates()

    assert set(aggregates) == {_job_name, _other_job_name}

    aggregate = aggregates[_job_name]

    assert aggregate['outcome_counts'][SCHEDULER.OUTCOME.OK] == 1
    assert aggregate['outcome_counts'][SCHEDULER.OUTCOME.ERROR] == 1
    assert aggregate['outcome_counts'][SCHEDULER.OUTCOME.TIMEOUT] == 1
    assert aggregate['outcome_counts'][SCHEDULER.OUTCOME.RUNNING] == 0

    assert aggregate['last_outcome'] == SCHEDULER.OUTCOME.TIMEOUT
    assert aggregate['last_duration_ms'] == 30000
    assert aggregate['last_run_utc']
    assert aggregate['recent_outcomes'] == [SCHEDULER.OUTCOME.OK, SCHEDULER.OUTCOME.ERROR, SCHEDULER.OUTCOME.TIMEOUT]

    other_aggregate = aggregates[_other_job_name]

    assert other_aggregate['outcome_counts'][SCHEDULER.OUTCOME.OK] == 1
    assert other_aggregate['last_outcome'] == SCHEDULER.OUTCOME.OK
    assert other_aggregate['recent_outcomes'] == [SCHEDULER.OUTCOME.OK]

# ################################################################################################################################

def _run_chart_and_timeline_checks() -> 'None':
    """ Confirms the chart buckets count every completed run and the timeline
    reads newest first across all the jobs.
    """
    chart = get_chart_data()
    buckets = chart['buckets']

    assert len(buckets) == Chart_Bucket_Count
    assert chart['min_time_iso']
    assert chart['max_time_iso']

    totals:'anydict' = {'ok': 0, 'error': 0, 'timeout': 0, 'skipped_already_in_flight': 0}

    for bucket in buckets:
        totals['ok'] += bucket['ok']
        totals['error'] += bucket['error']
        totals['timeout'] += bucket['timeout']
        totals['skipped_already_in_flight'] += bucket['skipped_already_in_flight']

    assert totals == {'ok': 2, 'error': 1, 'timeout': 1, 'skipped_already_in_flight': 0}, totals

    # The timeline spans both jobs, newest first - the other job ran last
    timeline = get_timeline_events_since()

    assert len(timeline) == 4
    assert timeline[0]['job_name'] == _other_job_name
    assert timeline[0]['outcome'] == SCHEDULER.OUTCOME.OK

    # A marker set after everything ran returns nothing new
    now = utcnow()
    timeline = get_timeline_events_since(now.isoformat())

    assert timeline == []

# ################################################################################################################################

def _run_enabled_switch_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms the scheduler honors the audit log switch like every other source -
    with the log off, starting a run records nothing and returns no event id.
    """
    env_name = AuditLogCtx.Env_Enabled
    previous = environ.get(env_name)

    environ[env_name] = 'False'

    try:
        now = utcnow()
        result = record_job_start(
            audit_log,
            _job_name,
            cid='cid-scheduler-switched-off',
            job_id=_job_id,
            current_run=4,
            planned_fire_time_iso=now.isoformat(),
            delay_ms=0,
            service=_service_name,
        )

        assert result is None
    finally:
        # A variable that was not there before is removed rather than left behind
        if previous is None:
            _ = environ.pop(env_name, None)
        else:
            environ[env_name] = previous

    # Nothing was written while the switch was off
    page = get_history_page(_job_id, _job_name, 0, 10, '')
    assert len(page['records']) == 3

# ################################################################################################################################
# ################################################################################################################################

def run_scheduler_history_scenario() -> 'None':
    """ The scheduler history scenario every backend must pass: one audit event per run
    updated in place from running to its final outcome, log lines as event body rows
    with incremental tailing, run detail navigation, incremental history polls, per-job
    aggregates, the pre-aggregated chart, the cross-job timeline and the audit log switch.
    """
    delete_all_events()

    audit_log = AuditLog(_server_name)

    event_id = _run_running_record_checks(audit_log)

    _run_log_entry_checks(event_id)
    _run_completion_checks(event_id)

    # The marker for the incremental poll checks - the failed and the timed-out runs follow it
    now = utcnow()
    since_iso = now.isoformat()

    _run_error_and_timeout_checks(audit_log)
    _run_outcome_filter_checks()
    _run_detail_checks()
    _run_history_since_checks(since_iso)
    _run_other_job_and_aggregate_checks(audit_log)
    _run_chart_and_timeline_checks()
    _run_enabled_switch_checks(audit_log)

# ################################################################################################################################
# ################################################################################################################################

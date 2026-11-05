# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess
import sys
from datetime import timedelta
from shutil import rmtree
from tempfile import mkdtemp
from time import monotonic, sleep

# SQLAlchemy
from sqlalchemy import func, select, text

# Zato
from active_standby_worker import Mode_Background, Mode_Resubmit
from common import delete_all_events
from zato.common.audit_log.api import event_body_table, event_table, get_audit_engine, get_source_env_suffix, \
    AuditEvent, AuditLog, AuditSource, Env_Retention_Days_Prefix
from zato.common.audit_log.common import event_count_table
from zato.common.audit_log.dedup import build_dedup_key, get_in_doubt
from zato.common.audit_log.resubmit import run_once, Action_Resend, DuplicateResubmitException
from zato.common.audit_log.retention import run_retention, Env_Content_Retention_Days
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intlist, strlist
    any_ = any_
    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-active-standby'

# The channel the test events belong to
_channel_name = 'audit.test.active-standby'

# The process that the two servers' background work and the interrupted resubmission run in
_worker_path = os.path.join(os.path.dirname(__file__), 'active_standby_worker.py')

# How long the background work of both servers runs at once
_background_seconds = 30

# How many events of each age one round of writes adds while the background work runs
_round_size = 50

# The ages of the events - recent ones, ones whose content is expired and ones whose rows are expired
_fresh_age_days = 0
_content_expired_age_days = 12
_row_expired_age_days = 45

# How many days of content and of rows the scenario keeps
_content_retention_days = 7
_row_retention_days = 30

# The variable holding the row retention of the source of the test events
_env_row_retention_days = f'{Env_Retention_Days_Prefix}{get_source_env_suffix(AuditSource.MLLP_Channel)}'

# How long the resubmission process has to start its dispatch
_resubmit_start_timeout_seconds = 60

# How often the test looks for the marker of the started dispatch
_marker_poll_seconds = 0.1

# The resubmission interrupted by the takeover
_resubmit_payload = 'active-standby-payload'
_resubmit_cid = 'cid-active-standby-resubmit'
_resubmit_actor = 'resubmit.operator'

# The minute and key of each event, grouped, against the stored counts - the rows where the two differ.
_count_mismatch_query = """
with raw_counts as (
    select date_trunc('minute', e.event_time at time zone 'UTC') at time zone 'UTC' as period_start,
        e.source, e.object_name, e.event_type, e.outcome, e.status, count(*) as event_count
    from {event_table} e
    group by 1, 2, 3, 4, 5, 6
),
stored_counts as (
    select c.period_start, c.source, c.object_name, c.event_type, c.outcome, c.status, sum(c.event_count) as event_count
    from {count_table} c
    group by 1, 2, 3, 4, 5, 6
    having sum(c.event_count) != 0
)
select r.period_start, r.source, r.event_count, s.period_start, s.source, s.event_count
from raw_counts r
full outer join stored_counts s
    on  r.period_start = s.period_start
    and coalesce(r.source, '')      = coalesce(s.source, '')
    and coalesce(r.object_name, '') = coalesce(s.object_name, '')
    and coalesce(r.event_type, '')  = coalesce(s.event_type, '')
    and coalesce(r.outcome, '')     = coalesce(s.outcome, '')
    and coalesce(r.status, '')      = coalesce(s.status, '')
where r.event_count is distinct from s.event_count
"""

# ################################################################################################################################
# ################################################################################################################################

def _insert_events(audit_log:'AuditLog', count:'int', age_days:'int') -> 'intlist':
    """ Writes events with a body and an attribute each and backdates them by the given number of days in one statement.
    """
    out:'intlist' = []

    for _ in range(count):
        event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Interchange_Received, _channel_name,
            cid=f'cid-active-standby-{age_days}', data='active-standby', attrs={'age_days': f'{age_days}'},
            bodies={'request': f'active-standby-{age_days}'}, needs_id=True)
        out.append(event_id)

    if age_days:

        event_time = utcnow() - timedelta(days=age_days)

        backdate_events = event_table.update()
        backdate_events = backdate_events.where(event_table.c.id.in_(out))
        backdate_events = backdate_events.values(event_time=event_time)

        backdate_bodies = event_body_table.update()
        backdate_bodies = backdate_bodies.where(event_body_table.c.event_id.in_(out))
        backdate_bodies = backdate_bodies.values(event_time=event_time)

        with get_audit_engine().begin() as connection:
            _ = connection.execute(backdate_events)
            _ = connection.execute(backdate_bodies)

    return out

# ################################################################################################################################

def _count_rows(table_id_column:'any_', ids:'intlist') -> 'int':
    """ Counts the rows of one table that belong to the given events.
    """
    query = select(func.count())
    query = query.where(table_id_column.in_(ids))

    with get_audit_engine().connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def _get_count_mismatches() -> 'strlist':
    """ Returns each minute and key whose stored count differs from the events that exist.
    """
    query = _count_mismatch_query.format(event_table=event_table.name, count_table=event_count_table.name)
    out:'strlist' = []

    with get_audit_engine().connect() as connection:
        for row in connection.execute(text(query)):
            out.append(f'{tuple(row)}')

    return out

# ################################################################################################################################

def _start_worker(*args:'str') -> 'subprocess.Popen[str]':
    """ Starts one worker process with the environment of the test, which points it at the same audit database.
    """
    command = [sys.executable, _worker_path, *args]
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return out

# ################################################################################################################################

def _run_concurrent_background_checks(audit_log:'AuditLog') -> 'None':
    """ Runs the retention, the count compaction and the search index merge of two servers at once against one database
    while events of every age keep arriving, and confirms that the counts equal the events that exist, that no event
    was deleted before its time, and that each expired one was deleted.
    """
    os.environ[Env_Content_Retention_Days] = f'{_content_retention_days}'
    os.environ[_env_row_retention_days] = f'{_row_retention_days}'

    fresh_ids:'intlist' = []
    content_expired_ids:'intlist' = []
    row_expired_ids:'intlist' = []

    try:

        # Both servers start their background work ..
        workers = [
            _start_worker(Mode_Background, f'{_background_seconds}'),
            _start_worker(Mode_Background, f'{_background_seconds}'),
        ]

        # .. events of every age keep arriving while it runs ..
        while workers[0].poll() is None or workers[1].poll() is None:
            fresh_ids.extend(_insert_events(audit_log, _round_size, _fresh_age_days))
            content_expired_ids.extend(_insert_events(audit_log, _round_size, _content_expired_age_days))
            row_expired_ids.extend(_insert_events(audit_log, _round_size, _row_expired_age_days))

        # .. each of them completes without an error ..
        for worker in workers:
            output, _ = worker.communicate()
            assert worker.returncode == 0, output

        # .. and one more run covers the events written after their last one.
        run_retention(get_audit_engine(), utcnow())

    finally:
        _ = os.environ.pop(Env_Content_Retention_Days, None)
        _ = os.environ.pop(_env_row_retention_days, None)

    # Recent events keep their rows and their content ..
    assert _count_rows(event_table.c.id, fresh_ids) == len(fresh_ids)
    assert _count_rows(event_body_table.c.event_id, fresh_ids) == len(fresh_ids)

    # .. events past the content cutoff keep their rows without their content ..
    assert _count_rows(event_table.c.id, content_expired_ids) == len(content_expired_ids)
    assert _count_rows(event_body_table.c.event_id, content_expired_ids) == 0

    # .. events past the row cutoff are gone ..
    assert _count_rows(event_table.c.id, row_expired_ids) == 0

    # .. and the counts equal the events that exist, which a deletion counted twice would make differ.
    mismatches = _get_count_mismatches()
    assert not mismatches, mismatches

# ################################################################################################################################

def _run_in_doubt_checks(audit_log:'AuditLog') -> 'None':
    """ Kills a server while one resubmission is in progress and confirms that its successor lists the resubmission
    as in doubt and does not run it a second time.
    """
    event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Interchange_Received, _channel_name,
        cid=_resubmit_cid, data=_resubmit_payload, needs_id=True)

    work_dir = mkdtemp(prefix='zato-audit-active-standby-')
    marker_path = os.path.join(work_dir, 'dispatch-started')

    try:

        # The server being replaced starts the resubmission ..
        worker = _start_worker(Mode_Resubmit, f'{event_id}', _resubmit_payload, _resubmit_cid, _resubmit_actor,
            marker_path)

        deadline = monotonic() + _resubmit_start_timeout_seconds

        while not os.path.exists(marker_path):
            assert worker.poll() is None, worker.communicate()[0]
            assert monotonic() < deadline, 'The resubmission did not start its dispatch'
            sleep(_marker_poll_seconds)

        # .. and is killed while it is in progress.
        os.kill(worker.pid, signal.SIGKILL)
        _ = worker.communicate()

    finally:
        rmtree(work_dir, ignore_errors=True)

    # The successor lists the resubmission as in doubt ..
    dedup_key = build_dedup_key(Action_Resend, event_id, _resubmit_payload)
    in_doubt = get_in_doubt(get_audit_engine())

    assert len(in_doubt) == 1
    assert in_doubt[0]['dedup_key'] == dedup_key
    assert in_doubt[0]['cid'] == _resubmit_cid
    assert in_doubt[0]['action'] == Action_Resend

    # .. and the same resubmission on the successor does not dispatch anything.
    dispatched:'strlist' = []

    def resubmit_one() -> 'None':
        dispatched.append(_resubmit_cid)

    is_rejected = False

    try:
        _ = run_once(Action_Resend, event_id, _resubmit_payload, 'cid-active-standby-successor', _resubmit_actor,
            resubmit_one)
    except DuplicateResubmitException:
        is_rejected = True

    assert is_rejected
    assert not dispatched

# ################################################################################################################################

def run_active_standby_scenario() -> 'None':
    """ What the audit log on PostgreSQL goes through while a replaced server and its successor overlap.
    """
    delete_all_events()
    audit_log = AuditLog(_server_name)

    _run_concurrent_background_checks(audit_log)
    _run_in_doubt_checks(audit_log)

    delete_all_events()

# ################################################################################################################################
# ################################################################################################################################

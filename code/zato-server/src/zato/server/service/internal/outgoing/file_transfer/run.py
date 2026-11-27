# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lifecycle of a file transfer run's audit row - opened, updated per phase and file, closed.

# stdlib
from dataclasses import dataclass, field
from datetime import datetime, time as datetime_time, timezone
from hashlib import sha256
from logging import getLogger
from time import monotonic
from traceback import format_exc

# gevent
from gevent import spawn

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.file_transfer_run import build_ledger_body, close_run_event, count_delivered_since, \
    find_running_runs, Interrupted_Note, Phase_Claiming, Phase_Connecting, Phase_Done, Run_Ledger_Max_Entries, \
    Run_Status_Clean, Run_Status_Empty, Run_Status_Failed, Run_Status_Interrupted, Run_Status_List_Failed, \
    Run_Status_No_Directory, Run_Status_Partial, Run_Status_Running, Run_Status_Unchanged, update_run_event, \
    write_run_exchanges, write_run_progress
from zato.common.util.api import utcnow
from zato.common.util.logging_ import file_transfer_logger_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anylist, intnone, stranydict, strintdict, strlist, strset, strstrdict
    from zato.server.service import Service
    AuditLog = AuditLog
    any_ = any_
    Greenlet = Greenlet
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(file_transfer_logger_name)

# The suffix a claimed file is renamed with
_claim_suffix = FileTransfer.Scheduler.Claim_Suffix

# The newest listing fingerprint of each schedule, keyed by connection and schedule.
_last_listing:'stranydict' = {}

# The count of files each schedule delivered today, keyed by connection and schedule.
_delivered_today:'stranydict' = {}

# The key of the zato context in a service's request context.
_zato_ctx_key = 'zato.zato_ctx'

# The scheduler context of a run not fired by the scheduler.
_no_scheduler_context = {'job_id': 0, 'current_run': 0}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RunContext:
    """ The state of one run - its row, counts, ledger and start time.
    """
    event_id:      'intnone' = None
    audit_log:     'AuditLog | None' = None
    conn_name:     str = ''
    schedule_name: str = ''
    directory:     str = ''
    run_cid:       str = ''
    started:       float = 0.0
    data:          'stranydict' = field(default_factory=dict)
    ledger:        'anylist' = field(default_factory=list)
    skip_reasons:  'strintdict' = field(default_factory=dict)
    fingerprint:   str = ''
    is_unchanged:  bool = False
    ensured_directories: 'strset' = field(default_factory=set)

# ################################################################################################################################

    def elapsed_ms(self) -> 'int':
        elapsed = monotonic() - self.started
        out = int(elapsed * 1000)
        return out

# ################################################################################################################################

    def save(self, **changes:'object') -> 'None':
        """ Writes the changes into the run's data and commits its row before returning.
        """
        self.data.update(changes)

        # The row receives the whole data, so a progress write still pending for the run is not needed ..
        _progress_writer.discard(self)

        # .. and the data is committed now.
        update_run_event(self.event_id, data=self.data)

# ################################################################################################################################

    def note_progress(self, **changes:'object') -> 'None':
        """ Writes the changes into the run's data, which its row receives in the background,
        without the run waiting for a commit.
        """
        self.data.update(changes)
        _progress_writer.note(self)

# ################################################################################################################################

    def set_phase(self, phase:'str', current_file:'str'='') -> 'None':
        """ Sets the run's phase and, in a file phase, its current file, as the run's progress.
        """
        changes:'stranydict' = {'phase': phase}

        if current_file:
            changes['current_file'] = current_file

        self.note_progress(**changes)

# ################################################################################################################################

    def begin_claim(self, file_name:'str') -> 'None':
        """ Commits the file the run is about to claim as its current file, so that a run interrupted
        from now on releases the claim of the file.
        """
        self.save(phase=Phase_Claiming, current_file=file_name)

# ################################################################################################################################

    def count_skip(self, reason:'str') -> 'None':
        if not (count := self.skip_reasons.get(reason)):
            count = 0

        self.skip_reasons[reason] = count + 1

# ################################################################################################################################
# ################################################################################################################################

class _ProgressWriter:
    """ Writes the progress of the runs of this process to their rows in a greenlet of its own, so that no run waits
    for a commit of what only a view of a run in progress reads. A run noted again before its row is written
    is written once, with its data as it is when the write is requested.

    A write of progress never replaces newer data that a run committed itself, because the writes of the audit log
    commit in the order they are requested and a run does not change its data while it waits for its own commit.
    """

    def __init__(self) -> 'None':

        # The runs whose progress is not written yet, by the ids of their rows
        self._pending:'dict[int, RunContext]' = {}

        # The greenlet that writes the pending runs, if one was started
        self._writer:'Greenlet | None' = None

# ################################################################################################################################

    def note(self, run:'RunContext') -> 'None':
        """ Marks a run as one whose progress its row is to receive, starting the greenlet that writes it if none runs.
        """

        # A run without a row, e.g. one of a turned-off audit log, has nothing to write ..
        if run.event_id is None:
            return

        # .. otherwise the run is pending ..
        self._pending[run.event_id] = run

        # .. and the greenlet that writes the pending runs is started unless one is about to run or runs already.
        if self._writer is None or self._writer.dead:
            self._writer = spawn(self._write_pending)

# ################################################################################################################################

    def discard(self, run:'RunContext') -> 'None':
        """ Drops the pending progress of a run whose row receives its whole data in another write.
        """
        if run.event_id is not None:
            _ = self._pending.pop(run.event_id, None)

# ################################################################################################################################

    def _write_pending(self) -> 'None':
        """ Writes the pending runs, all of them in one transaction, until no run is pending.
        """
        while self._pending:

            # Take all the runs pending now ..
            progress = [(event_id, run.data) for event_id, run in self._pending.items()]
            self._pending.clear()

            # .. and write them - a failed write leaves the rows as they were, and the next write
            # .. of each run replaces its whole data.
            try:
                write_run_progress(progress)
            except Exception:
                logger.warning('Could not write the progress of %d run(s) -> `%s`', len(progress), format_exc())

# ################################################################################################################################
# ################################################################################################################################

# The one writer of the progress of the runs of this process
_progress_writer = _ProgressWriter()

# ################################################################################################################################
# ################################################################################################################################

def _new_run_context() -> 'RunContext':
    out = RunContext()
    out.data = {}
    out.ledger = []
    out.skip_reasons = {}
    out.ensured_directories = set()

    return out

# ################################################################################################################################

def error_summary(error:'str') -> 'str':
    """ The last line of a traceback.
    """
    stripped = error.strip()
    error_lines = stripped.splitlines()

    out = error_lines[-1]
    return out

# ################################################################################################################################

def get_scheduler_context(service:'Service') -> 'stranydict':
    """ The scheduler's job id and run number, both zero when the scheduler did not fire the run.
    """
    zato_ctx = service.request_ctx.get(_zato_ctx_key)

    if zato_ctx is None:
        out = dict(_no_scheduler_context)
    else:
        out = {
            'job_id': zato_ctx['scheduler_job_id'],
            'current_run': zato_ctx['scheduler_current_run'],
        }

    return out

# ################################################################################################################################

def local_day_start_utc(now_local:'datetime') -> 'datetime':
    """ The local day's midnight in UTC.
    """
    today = now_local.date()
    day_start_local = datetime.combine(today, datetime_time.min, tzinfo=now_local.tzinfo)

    out = day_start_local.astimezone(timezone.utc)
    return out

# ################################################################################################################################

def get_delivered_today(conn_name:'str', schedule_name:'str') -> 'int':
    """ How many files a schedule delivered today, local time, counted from the audit database once a day.
    """
    now = datetime.now()
    now_local = now.astimezone()
    today_date = now_local.date()
    today = today_date.isoformat()
    key = f'{conn_name}|{schedule_name}'

    if counter := _delivered_today.get(key):
        if counter['day'] == today:
            out = counter['count']
            return out

    since = local_day_start_utc(now_local)
    count = count_delivered_since(conn_name, schedule_name, since)

    _delivered_today[key] = {'day': today, 'count': count}

    out = count
    return out

# ################################################################################################################################

def add_delivered_today(conn_name:'str', schedule_name:'str') -> 'int':
    """ Adds one to today's count and returns it.
    """
    _ = get_delivered_today(conn_name, schedule_name)

    key = f'{conn_name}|{schedule_name}'
    counter = _delivered_today[key]
    counter['count'] += 1

    out = counter['count']
    return out

# ################################################################################################################################

def listing_fingerprint(entries:'anylist') -> 'str':
    """ The SHA-256 of the sorted names, sizes and modification times of the entries.
    """
    lines:'strlist' = []

    for entry in entries:
        lines.append(f'{entry.name}|{entry.size}|{entry.last_modified_iso}')

    lines.sort()
    joined = '\n'.join(lines)
    hasher = sha256(joined.encode('utf8'))

    out = hasher.hexdigest()
    return out

# ################################################################################################################################

def _release_interrupted_claim(conn:'any_', data:'stranydict', current_file:'str') -> 'None':
    """ Renames the claim of the file an interrupted run was in the middle of back to the file's own name
    and records the outcome in the run's data.
    """
    full_path = f'{data["remote_path"]}/{current_file}'
    claim_path = full_path + _claim_suffix

    try:

        # The run may have been interrupted before its claim or after its ack, so there may be no claim at all
        if not conn.exists(claim_path):
            return

        _ = conn.move(claim_path, full_path)

    except Exception:
        release_error = format_exc()
        logger.info('Could not release the claim on `%s` -> `%s`', claim_path, release_error)
        data['claim_released'] = False
        data['release_error'] = error_summary(release_error)

    else:
        data['claim_released'] = True

# ################################################################################################################################

def close_interrupted_runs(audit_log:'AuditLog', conn_name:'str', schedule_name:'str', conn:'any_') -> 'None':
    """ Closes the runs this server left marked as running as interrupted,
    releasing the claim of the file each of them was in the middle of.
    """
    running = find_running_runs(conn_name, schedule_name, audit_log.server_name)

    for event_id, data in running:

        if current_file := data.get('current_file'):
            _release_interrupted_claim(conn, data, current_file)

        data['note'] = Interrupted_Note
        data['phase'] = Phase_Done
        update_run_event(event_id, outcome=AuditOutcome.Error, status=Run_Status_Interrupted, data=data)

# ################################################################################################################################

def open_run(
    audit_log:'AuditLog',
    conn_name:'str',
    directory:'str',
    run_cid:'str',
    schedule:'stranydict',
    scheduler_context:'stranydict',
    ) -> 'RunContext':
    """ Writes the run's row as running and returns the run's context.
    """
    schedule_name = schedule['name']
    delivered_today = get_delivered_today(conn_name, schedule_name)

    # Our response to produce
    out = _new_run_context()

    out.audit_log = audit_log
    out.conn_name = conn_name
    out.schedule_name = schedule_name
    out.directory = directory
    out.run_cid = run_cid
    out.started = monotonic()

    out.data = {
        'schedule': schedule_name,
        'remote_path': directory,
        'phase': Phase_Connecting,
        'job_id': scheduler_context['job_id'],
        'current_run': scheduler_context['current_run'],
        'expected_files': schedule['expected_files'],
        'expected_by': schedule['expected_by'],
        'delivered_today': delivered_today,
        'entries': 0,
        'candidates': 0,
        'picked_up': 0,
        'processed': 0,
        'failed': 0,
        'skipped': 0,
        'acked': 0,
        'ack_failed': 0,
        'quarantined': 0,
    }

    # The scheduler's run number is a searchable attribute.
    attrs_extra = {'current_run': scheduler_context['current_run']}

    out.event_id = record_schedule_event(audit_log, conn_name, AuditEvent.Run_Completed, directory,
        cid=run_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Running,
        status=Run_Status_Running, extra=out.data, attrs_extra=attrs_extra)

    return out

# ################################################################################################################################

def note_listing(run:'RunContext', entries:'anylist', list_ms:'int') -> 'None':
    """ Records the listing's size and whether it is the same as the previous run's.
    """
    key = f'{run.conn_name}|{run.schedule_name}'
    fingerprint = listing_fingerprint(entries)

    run.fingerprint = fingerprint

    if previous := _last_listing.get(key):
        if previous['fingerprint'] == fingerprint:
            run.is_unchanged = True
            run.data['unchanged_since_event_id'] = previous['event_id']
            run.data['unchanged_since_iso'] = previous['event_time_iso']

    entry_count = len(entries)
    run.note_progress(entries=entry_count, list_ms=list_ms)

# ################################################################################################################################

def note_exchanges(run:'RunContext', conn:'any_') -> 'None':
    """ Stores what the run said to the server while checking and listing the directory
    and what the server said back, as the run's request and response bodies.
    """
    exchanges = conn.take_exchanges()

    now = utcnow()
    write_run_exchanges(run.event_id, now, exchanges)

# ################################################################################################################################

def remember_listing(run:'RunContext') -> 'None':
    """ Remembers the run's listing fingerprint for the next run, unless the run repeated the previous one.
    """
    if run.is_unchanged:
        return

    key = f'{run.conn_name}|{run.schedule_name}'
    now = utcnow()

    _last_listing[key] = {
        'fingerprint': run.fingerprint,
        'event_id': run.event_id,
        'event_time_iso': now.isoformat(),
    }

# ################################################################################################################################

def _status_for(run:'RunContext') -> 'str':
    """ The run's status, read off its counts.
    """
    data = run.data

    if data['failed']:
        if data['processed']:
            out = Run_Status_Partial
        else:
            out = Run_Status_Failed

    elif data['ack_failed']:
        out = Run_Status_Partial

    elif data['processed']:
        out = Run_Status_Clean

    elif run.is_unchanged:
        out = Run_Status_Unchanged

    else:
        out = Run_Status_Empty

    return out

# ################################################################################################################################

def close_run(run:'RunContext') -> 'None':
    """ Closes the run's row with its counts, status and ledger, an unchanged run writes no ledger.
    """
    data = run.data
    duration_ms = run.elapsed_ms()

    data['phase'] = Phase_Done
    data['skip_reasons'] = run.skip_reasons
    data.pop('current_file', None)

    skip_counts = run.skip_reasons.values()
    data['skipped'] = sum(skip_counts)

    # A run that processed or failed a file is never unchanged ..
    delivered_nothing = data['processed'] == 0
    if delivered_nothing:
        if data['failed']:
            delivered_nothing = False

    if not delivered_nothing:
        run.is_unchanged = False
        data.pop('unchanged_since_event_id', None)
        data.pop('unchanged_since_iso', None)

    status = _status_for(run)

    # .. a failed file or ack makes the run an error ..
    has_failures = data['failed'] > 0
    if not has_failures:
        has_failures = data['ack_failed'] > 0

    if has_failures:
        outcome = AuditOutcome.Error
    else:
        outcome = AuditOutcome.OK

    # .. a changed listing writes the ledger ..
    bodies:'strstrdict' = {}

    if not run.is_unchanged:
        ledger_count = len(run.ledger)
        if ledger_count > Run_Ledger_Max_Entries:
            data['ledger_overflow'] = ledger_count - Run_Ledger_Max_Entries

        bodies[AuditBody.Run_Ledger] = build_ledger_body(run.ledger)

    # .. which is committed together with the closed row.
    _close(run, outcome, status, duration_ms, bodies)
    remember_listing(run)

# ################################################################################################################################

def _close(run:'RunContext', outcome:'str', status:'str', duration_ms:'int', bodies:'strstrdict') -> 'None':
    """ Commits the closed row of a run with its bodies, which replaces any progress of the run still pending.
    """
    _progress_writer.discard(run)

    now = utcnow()
    close_run_event(run.event_id, outcome=outcome, status=status, duration_ms=duration_ms, data=run.data,
        event_time=now, bodies=bodies)

# ################################################################################################################################

def close_run_no_directory(run:'RunContext') -> 'None':
    """ Closes the run's row with the no-directory status - a directory that is not there is an error of the run.
    """
    run.data['phase'] = Phase_Done
    duration_ms = run.elapsed_ms()

    _close(run, AuditOutcome.Error, Run_Status_No_Directory, duration_ms, {})

# ################################################################################################################################

def close_run_list_failed(run:'RunContext', phase:'str', error:'str') -> 'None':
    """ Closes the run's row with the list-failed status, the phase and the error's last line, the traceback as a body.
    """
    run.data['phase'] = phase
    run.data['error'] = error_summary(error)
    duration_ms = run.elapsed_ms()

    bodies = {AuditBody.Error: error}
    _close(run, AuditOutcome.Error, Run_Status_List_Failed, duration_ms, bodies)

# ################################################################################################################################
# ################################################################################################################################

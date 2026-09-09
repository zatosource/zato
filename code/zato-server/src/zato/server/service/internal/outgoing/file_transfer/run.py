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
from time import monotonic

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.file_transfer_run import count_delivered_since, find_running_runs, Interrupted_Note, \
    Phase_Connecting, Phase_Done, Run_Ledger_Max_Entries, Run_Status_Clean, Run_Status_Empty, Run_Status_Failed, \
    Run_Status_Interrupted, Run_Status_List_Failed, Run_Status_No_Directory, Run_Status_Partial, Run_Status_Running, \
    Run_Status_Unchanged, update_run_event, write_run_error, write_run_ledger
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, intnone, stranydict, strintdict, strlist
    from zato.server.service import Service
    AuditLog = AuditLog

# ################################################################################################################################
# ################################################################################################################################

# The newest listing fingerprint of each schedule, keyed by connection and schedule.
_last_listing:'stranydict' = {}

# The count of files each schedule delivered today, keyed by connection and schedule.
_delivered_today:'stranydict' = {}

# The key of the zato context in a service's WSGI environment.
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

# ################################################################################################################################

    def elapsed_ms(self) -> 'int':
        elapsed = monotonic() - self.started
        out = int(elapsed * 1000)
        return out

# ################################################################################################################################

    def update(self, **changes:'object') -> 'None':
        """ Writes the changes into the run's data and its row.
        """
        self.data.update(changes)
        update_run_event(self.event_id, data=self.data)

# ################################################################################################################################

    def set_phase(self, phase:'str', current_file:'str'='') -> 'None':
        """ Sets the run's phase and, in a file phase, its current file.
        """
        changes:'stranydict' = {'phase': phase}

        if current_file:
            changes['current_file'] = current_file

        self.update(**changes)

# ################################################################################################################################

    def count_skip(self, reason:'str') -> 'None':
        if not (count := self.skip_reasons.get(reason)):
            count = 0

        self.skip_reasons[reason] = count + 1

# ################################################################################################################################
# ################################################################################################################################

def _new_run_context() -> 'RunContext':
    out = RunContext()
    out.data = {}
    out.ledger = []
    out.skip_reasons = {}

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
    zato_ctx = service.wsgi_environ.get(_zato_ctx_key)

    if zato_ctx is None:
        out = dict(_no_scheduler_context)
    else:
        out = {
            'job_id': zato_ctx['scheduler_job_id'],
            'current_run': zato_ctx['scheduler_current_run'],
        }

    return out

# ################################################################################################################################

def local_day_start_utc_iso(now_local:'datetime') -> 'str':
    """ The local day's midnight as a UTC ISO timestamp.
    """
    today = now_local.date()
    day_start_local = datetime.combine(today, datetime_time.min, tzinfo=now_local.tzinfo)
    day_start_utc = day_start_local.astimezone(timezone.utc)

    out = day_start_utc.isoformat()
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

    since_iso = local_day_start_utc_iso(now_local)
    count = count_delivered_since(conn_name, schedule_name, since_iso)

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

def close_interrupted_runs(audit_log:'AuditLog', conn_name:'str', schedule_name:'str') -> 'None':
    """ Closes the runs this server left marked as running as interrupted.
    """
    running = find_running_runs(conn_name, schedule_name, audit_log.server_name)

    for event_id, data in running:
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
        'taken': 0,
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
    run.update(entries=entry_count, list_ms=list_ms)

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
    took_nothing = data['processed'] == 0
    if took_nothing:
        if data['failed']:
            took_nothing = False

    if not took_nothing:
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

    # .. and a changed listing writes the ledger.
    if not run.is_unchanged:
        ledger_count = len(run.ledger)
        if ledger_count > Run_Ledger_Max_Entries:
            data['ledger_overflow'] = ledger_count - Run_Ledger_Max_Entries

        now = utcnow()
        now_iso = now.isoformat()
        write_run_ledger(run.event_id, now_iso, run.ledger)

    update_run_event(run.event_id, outcome=outcome, status=status, duration_ms=duration_ms, data=data)
    remember_listing(run)

# ################################################################################################################################

def close_run_no_directory(run:'RunContext') -> 'None':
    """ Closes the run's row with the no-directory status.
    """
    run.data['phase'] = Phase_Done
    duration_ms = run.elapsed_ms()

    update_run_event(run.event_id, outcome=AuditOutcome.OK, status=Run_Status_No_Directory,
        duration_ms=duration_ms, data=run.data)

# ################################################################################################################################

def close_run_list_failed(run:'RunContext', phase:'str', error:'str') -> 'None':
    """ Closes the run's row with the list-failed status, the phase and the error's last line, the traceback as a body.
    """
    run.data['phase'] = phase
    run.data['error'] = error_summary(error)
    duration_ms = run.elapsed_ms()

    update_run_event(run.event_id, outcome=AuditOutcome.Error, status=Run_Status_List_Failed,
        duration_ms=duration_ms, data=run.data)

    now = utcnow()
    now_iso = now.isoformat()
    write_run_error(run.event_id, now_iso, error)

# ################################################################################################################################
# ################################################################################################################################

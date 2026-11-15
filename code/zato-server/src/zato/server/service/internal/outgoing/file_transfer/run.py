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

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.file_transfer_run import count_delivered_since, find_latest_listing, find_running_runs, \
    Interrupted_Note, Key_Listing_Fingerprint, Key_Listing_Time_Iso, Phase_Connecting, Phase_Done, Run_Ledger_Max_Entries, \
    Run_Status_Clean, Run_Status_Empty, Run_Status_Failed, Run_Status_Interrupted, Run_Status_List_Failed, \
    Run_Status_No_Directory, Run_Status_Partial, Run_Status_Running, Run_Status_Unchanged, update_run_event, write_run_error, \
    write_run_exchanges, write_run_ledger, write_run_listing
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.common.util.logging_ import file_transfer_logger_name
from zato.server.process_instance import get_process_binding, is_process_instance_live

# Zato - Rust
from zato_ipc_core.zato_ipc_core import SharedRegionFull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anylist, intnone, stranydict, strintdict, strlist, strset
    from zato.server.process_instance import ProcessBinding
    from zato.server.service import Service
    from zato_ipc_core.zato_ipc_core import SharedRegion
    AuditLog = AuditLog
    SharedRegion = SharedRegion
    ProcessBinding = ProcessBinding
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(file_transfer_logger_name)

# The suffix a claimed file is renamed with
_claim_suffix = FileTransfer.Scheduler.Claim_Suffix

# The count of files each schedule delivered today, keyed by connection and schedule, in a process that no arbiter bound.
_delivered_today:'stranydict' = {}

# The first part of the key of the keyed lock of the region whose counter holds the deliveries of a schedule today.
_delivered_today_key_prefix = 'file_transfer.delivered_today|'

# The counter holds the ordinal of the local day above these bits and the count of the deliveries of that day within them,
# so a worker that sets the day and a worker that adds a delivery change one word.
_day_shift = 32
_count_mask = (1 << _day_shift) - 1

# The key of the zato context in a service's request context.
_zato_ctx_key = 'zato.zato_ctx'

# The scheduler context of a run not fired by the scheduler.
_no_scheduler_context = {'job_id': 0, 'current_run': 0}

# The key of the process instance of the worker that opened a run, in the run's data.
_key_process_instance = 'process_instance'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeliveredTodayCell:
    """ The counter of the region that holds the day and the count of the deliveries of a schedule.
    """
    region: 'SharedRegion'
    entry: int

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

def _pack_day_count(day:'int', count:'int') -> 'int':
    out = (day << _day_shift) | count
    return out

# ################################################################################################################################

def _unpack_day_count(value:'int') -> 'tuple[int, int]':
    day = value >> _day_shift
    count = value & _count_mask

    return day, count

# ################################################################################################################################

def _get_delivered_today_cell(key:'str') -> 'DeliveredTodayCell | None':
    """ The counter of the region of the server for the deliveries of a schedule today,
    or None in a process that no arbiter bound and in a worker whose region has no entry left for the schedule.
    """
    binding = get_process_binding()

    if binding is None:
        return None

    try:
        entry = binding.region.lock_entry(_delivered_today_key_prefix + key)

    # With the lock table full, the schedule counts its deliveries today in this worker alone
    except SharedRegionFull:
        logger.error('Schedule `%s` counts its deliveries today in this worker alone, the lock table is full', key)
        return None

    out = DeliveredTodayCell()
    out.region = binding.region
    out.entry = entry

    return out

# ################################################################################################################################

def _get_local_delivered_today(key:'str', conn_name:'str', schedule_name:'str', now_local:'datetime') -> 'int':
    """ How many files a schedule delivered today, counted from the audit database once a day in this process.
    """
    today_date = now_local.date()
    today = today_date.isoformat()

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

def _get_shared_delivered_today(
    cell:'DeliveredTodayCell',
    conn_name:'str',
    schedule_name:'str',
    now_local:'datetime',
    ) -> 'int':
    """ How many files a schedule delivered today, counted from the audit database by the first run of the day in any worker.
    """
    today_date = now_local.date()
    today = today_date.toordinal()

    while True:

        current = cell.region.lock_counter(cell.entry)
        day, count = _unpack_day_count(current)

        if day == today:
            return count

        since = local_day_start_utc(now_local)
        count = count_delivered_since(conn_name, schedule_name, since)
        value = _pack_day_count(today, count)

        # The first worker that counted the day sets it, and a worker that another one preceded reads the counter again
        if cell.region.lock_counter_replace(cell.entry, current, value):
            return count

# ################################################################################################################################

def _get_delivered_today(cell:'DeliveredTodayCell | None', key:'str', conn_name:'str', schedule_name:'str') -> 'int':
    now = datetime.now()
    now_local = now.astimezone()

    if cell is None:
        out = _get_local_delivered_today(key, conn_name, schedule_name, now_local)
    else:
        out = _get_shared_delivered_today(cell, conn_name, schedule_name, now_local)

    return out

# ################################################################################################################################

def get_delivered_today(conn_name:'str', schedule_name:'str') -> 'int':
    """ How many files a schedule delivered today, local time, counted from the audit database once a day.
    """
    key = f'{conn_name}|{schedule_name}'
    cell = _get_delivered_today_cell(key)

    out = _get_delivered_today(cell, key, conn_name, schedule_name)
    return out

# ################################################################################################################################

def add_delivered_today(conn_name:'str', schedule_name:'str') -> 'int':
    """ Adds one to today's count and returns it.
    """
    key = f'{conn_name}|{schedule_name}'
    cell = _get_delivered_today_cell(key)

    _ = _get_delivered_today(cell, key, conn_name, schedule_name)

    if cell is None:
        counter = _delivered_today[key]
        counter['count'] += 1
        out = counter['count']

    # The addition by fetch-add includes the deliveries that every other worker added in the meantime
    else:
        value = cell.region.lock_counter_add(cell.entry, 1)
        _, out = _unpack_day_count(value)

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

def _is_run_in_progress(binding:'ProcessBinding | None', data:'stranydict') -> 'bool':
    """ Whether a run that is marked as running is still in progress in the process that opened it.
    """

    # A process that no arbiter started has no region to check an instance against,
    # and it concludes every running run of its server ..
    if binding is None:
        out = False

    # .. a run without an instance was opened by such a process ..
    elif _key_process_instance not in data:
        out = False

    # .. and any other run is in progress as long as the process of its instance runs.
    else:
        out = is_process_instance_live(binding, data[_key_process_instance])

    return out

# ################################################################################################################################

def close_interrupted_runs(audit_log:'AuditLog', conn_name:'str', schedule_name:'str', conn:'any_') -> 'None':
    """ Closes as interrupted the runs of this server that are marked as running and are no longer in progress,
    releasing the claim of the file each of them was in the middle of.
    """
    running = find_running_runs(conn_name, schedule_name, audit_log.server_name)
    binding = get_process_binding()

    for event_id, data in running:

        # A run of a process that still runs keeps its row and its claim.
        if _is_run_in_progress(binding, data):
            continue

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

    # The run records the process instance of its worker, by which a later run tells it from an interrupted one.
    if binding := get_process_binding():
        out.data[_key_process_instance] = binding.instance

    # The scheduler's run number is a searchable attribute.
    attrs_extra = {'current_run': scheduler_context['current_run']}

    out.event_id = record_schedule_event(audit_log, conn_name, AuditEvent.Run_Completed, directory,
        cid=run_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Running,
        status=Run_Status_Running, extra=out.data, attrs_extra=attrs_extra)

    return out

# ################################################################################################################################

def note_listing(run:'RunContext', entries:'anylist', list_ms:'int') -> 'None':
    """ Records the listing's size and whether it is the same as the one of the previous run through any worker.
    """
    audit_log = cast_('AuditLog', run.audit_log)
    fingerprint = listing_fingerprint(entries)

    run.fingerprint = fingerprint

    if previous := find_latest_listing(run.conn_name, run.schedule_name, audit_log.server_name):
        if previous['fingerprint'] == fingerprint:
            run.is_unchanged = True
            run.data['unchanged_since_event_id'] = previous['event_id']
            run.data['unchanged_since_iso'] = previous['event_time_iso']

    entry_count = len(entries)
    run.update(entries=entry_count, list_ms=list_ms)

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
    """ Keeps the run's listing fingerprint in the data of its row for the next run, unless the run repeated the previous one.
    """
    if run.is_unchanged:
        return

    now = utcnow()

    run.data[Key_Listing_Fingerprint] = run.fingerprint
    run.data[Key_Listing_Time_Iso] = now.isoformat()

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

    # .. and a changed listing writes the ledger.
    if not run.is_unchanged:
        ledger_count = len(run.ledger)
        if ledger_count > Run_Ledger_Max_Entries:
            data['ledger_overflow'] = ledger_count - Run_Ledger_Max_Entries

        now = utcnow()
        write_run_ledger(run.event_id, now, run.ledger)

    remember_listing(run)
    update_run_event(run.event_id, outcome=outcome, status=status, duration_ms=duration_ms, data=data)

    # The next run finds the fingerprint through the attribute, which is written after the data that carries it
    if not run.is_unchanged:
        write_run_listing(run.event_id, run.schedule_name)

# ################################################################################################################################

def close_run_no_directory(run:'RunContext') -> 'None':
    """ Closes the run's row with the no-directory status - a directory that is not there is an error of the run.
    """
    run.data['phase'] = Phase_Done
    duration_ms = run.elapsed_ms()

    update_run_event(run.event_id, outcome=AuditOutcome.Error, status=Run_Status_No_Directory,
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
    write_run_error(run.event_id, now, error)

# ################################################################################################################################
# ################################################################################################################################

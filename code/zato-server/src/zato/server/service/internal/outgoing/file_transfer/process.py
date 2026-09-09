# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.file_transfer_run import build_ledger_record, Decision_Failed, Decision_Quarantined, \
    Decision_Skipped, Decision_Taken, find_seen_before, iso_days_ago, load_attempt_memory, Phase_Acking, \
    Phase_Checking_Directory, Phase_Claiming, Phase_Delivering, Phase_Listing, Phase_Reading, Phase_Waiting, \
    Retry_Memory_Days, Seen_Before_Window_Days, Skip_Claimed_Elsewhere
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.util.api import new_cid_server, utcnow
from zato.common.util.file_transfer_scheduler import apply_schedule_defaults
from zato.server.service.internal.outgoing.file_transfer.candidates import get_candidates, get_file_name, \
    keep_entries_past_backoff, keep_stable_entries
from zato.server.service.internal.outgoing.file_transfer.run import add_delivered_today, close_interrupted_runs, \
    close_run, close_run_list_failed, close_run_no_directory, error_summary, get_scheduler_context, note_listing, open_run

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.server.service import Service
    from zato.server.service.internal.outgoing.file_transfer.candidates import Selection
    from zato.server.service.internal.outgoing.file_transfer.run import RunContext
    AuditLog = AuditLog

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The statuses one file's handling ends with.
_status_processed   = 'processed'
_status_failed      = 'failed'
_status_skipped     = 'skipped'
_status_quarantined = 'quarantined'

# The ledger decision of each file status.
_decision_for_status = {
    _status_processed:   Decision_Taken,
    _status_failed:      Decision_Failed,
    _status_skipped:     Decision_Skipped,
    _status_quarantined: Decision_Quarantined,
}

# The error of a claim lost to another consumer.
_claim_lost_error = 'Already claimed by another consumer'

# Milliseconds per second.
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FileResult:
    """ The result of one file's handling.
    """
    status:        str = ''
    reason:        str = ''
    file_cid:      str = ''
    attempt:       int = 0
    error:         str = ''
    is_acked:      bool = False
    is_ack_failed: bool = False

# ################################################################################################################################
# ################################################################################################################################

def _elapsed_ms(start:'float') -> 'int':
    elapsed = monotonic() - start
    out = int(elapsed * _ms_per_second)
    return out

# ################################################################################################################################

def _get_move_destination(conn:'any_', move_directory:'str', file_name:'str') -> 'str':
    """ The destination path of a moved file, with a timestamp suffix if the name is already taken.
    """
    out = f'{move_directory}/{file_name}'

    # The name is free ..
    if not conn.exists(out):
        return out

    # .. or it is taken and the file is given a timestamp suffix.
    now = datetime.now(timezone.utc)
    stamp = now.strftime(_scheduler.Collision_Suffix_Format)

    out = f'{move_directory}/{file_name}.{stamp}'
    return out

# ################################################################################################################################

def _resolve_subdirectory(directory:'str', subdirectory:'str') -> 'str':
    """ The subdirectory as an absolute path, relative ones are under the directory.
    """
    if subdirectory.startswith('/'):
        out = subdirectory
    else:
        out = f'{directory}/{subdirectory}'

    return out

# ################################################################################################################################

def _move_out_of_the_way(conn:'any_', destination_directory:'str', file_name:'str', current_path:'str') -> 'str':
    """ Moves a file into the directory, creating the directory if needed, and returns the new path.
    """
    if not conn.exists(destination_directory):
        _ = conn.create_directory(destination_directory)

    out = _get_move_destination(conn, destination_directory, file_name)
    _ = conn.move(current_path, out)

    return out

# ################################################################################################################################

def _ack_one_file(
    conn,         # type: any_
    schedule,     # type: stranydict
    directory,    # type: str
    file_name,    # type: str
    full_path,    # type: str
    current_path, # type: str
    ) -> 'str':
    """ Moves or deletes a delivered file and returns the path it was moved to, empty if deleted.
    """

    # Our response to produce
    out = ''

    if schedule['on_success'] == _scheduler.OnSuccess.Move:
        move_directory = _resolve_subdirectory(directory, schedule['move_directory'])
        out = _move_out_of_the_way(conn, move_directory, file_name, current_path)
    else:
        _ = conn.delete_file(current_path)

    # In marker mode, the marker is deleted with its file.
    if schedule['ready_how'] == _scheduler.ReadyHow.Marker:
        marker_path = full_path + schedule['marker_suffix']
        _ = conn.delete_file(marker_path)

    return out

# ################################################################################################################################

def _release_claim(service:'Service', conn:'any_', full_path:'str', current_path:'str', failure:'stranydict') -> 'None':
    """ Renames a claimed file back to its original name and records the outcome in the failure data.
    """
    if current_path == full_path:
        return

    try:
        _ = conn.move(current_path, full_path)
    except Exception:
        release_error = format_exc()
        service.logger.info('Could not release the claim on `%s` -> `%s`', current_path, release_error)
        failure['claim_released'] = False
        failure['release_error'] = error_summary(release_error)
    else:
        failure['claim_released'] = True

# ################################################################################################################################

def _quarantine_one_file(
    service,       # type: Service
    conn,          # type: any_
    schedule,      # type: stranydict
    directory,     # type: str
    file_name,     # type: str
    current_path,  # type: str
    failure,       # type: stranydict
    ) -> 'str':
    """ Moves a file to the quarantine directory and returns its new path, empty if the move failed.
    """
    quarantine_directory = _resolve_subdirectory(directory, schedule['quarantine_directory'])

    try:
        out = _move_out_of_the_way(conn, quarantine_directory, file_name, current_path)
    except Exception:
        quarantine_error = format_exc()
        service.logger.warning('Could not quarantine `%s` in `%s` -> `%s`', current_path, quarantine_directory,
            quarantine_error)
        failure['quarantine_error'] = error_summary(quarantine_error)
        out = ''

    return out

# ################################################################################################################################

def _process_one_file(
    service,   # type: Service
    conn,      # type: any_
    context,   # type: stranydict
    schedule,  # type: stranydict
    directory, # type: str
    entry,     # type: any_
    attempt,   # type: int
    first_failed_iso, # type: str
    run,       # type: RunContext
    ) -> 'FileResult':
    """ Claims, reads, delivers and acks one file, quarantining it after its last allowed attempt.
    """

    # Our response to produce
    out = FileResult()
    out.attempt = attempt

    # Local aliases
    conn_name     = context[_scheduler.Extra_Conn_Name]
    conn_type     = context[_scheduler.Extra_Conn_Type]
    schedule_name = schedule['name']
    service_name  = schedule['service']
    max_attempts  = schedule['max_attempts']

    # The run's cid is the correlation id of every event of the run ..
    run_cid = run.run_cid

    # .. and the file's cid is shared by the schedule-level and connection-level events of the file.
    file_cid = new_cid_server()
    conn.cid = file_cid
    out.file_cid = file_cid

    audit_log:'AuditLog' = conn.wrapper.audit_log

    file_name = get_file_name(entry)
    full_path = f'{directory}/{file_name}'

    # The path the file is read from, changed by a claim.
    current_path = full_path

    # The scheduler's run number is a searchable attribute of every event of the file.
    attrs_extra = {'current_run': run.data['current_run']}

    # The data a reprocess needs to rebuild the item.
    event_extra:'stranydict' = {
        'conn_type': conn_type,
        'last_modified': entry.last_modified_iso,
        'attempt': attempt,
        'max_attempts': max_attempts,
    }

    # With claiming on, the file is renamed before it is read, a failed rename means another consumer claimed it.
    if schedule['should_claim']:
        run.set_phase(Phase_Claiming, file_name)
        claim_path = full_path + _scheduler.Claim_Suffix
        try:
            _ = conn.move(full_path, claim_path)
        except Exception:
            service.logger.info('File `%s` already claimed by another consumer, skipping', full_path)
            _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Claimed, full_path,
                cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Error,
                file_name=file_name, error=_claim_lost_error, attrs_extra=attrs_extra)
            out.status = _status_skipped
            out.reason = Skip_Claimed_Elsewhere
            return out
        current_path = claim_path

    read_ms = 0
    service_ms = 0

    try:
        # Download the file ..
        run.set_phase(Phase_Reading, file_name)
        read_start = monotonic()
        data = conn.read(current_path)
        read_ms = _elapsed_ms(read_start)

        # .. look up an earlier delivery of the same checksum ..
        hasher = sha256(data)
        checksum = hasher.hexdigest()
        seen_before_since = iso_days_ago(Seen_Before_Window_Days)
        seen_before = find_seen_before(conn_name, schedule_name, checksum, seen_before_since)

        # .. and invoke the target service under the file's cid.
        run.set_phase(Phase_Delivering, file_name)
        item = FileTransferItem(conn_type, conn_name, schedule_name, directory, file_name, full_path,
            entry.size, entry.last_modified_iso, data)

        service_start = monotonic()
        _ = service.invoke(service_name, item, cid=file_cid)
        service_ms = _elapsed_ms(service_start)

    except Exception:

        error = format_exc()
        out.error = error_summary(error)

        service.logger.warning('Could not invoke `%s` with file `%s` from `%s` -> `%s`',
            service_name, full_path, conn_name, error)

        failure = dict(event_extra)
        failure['read_ms'] = read_ms
        failure['service_ms'] = service_ms

        # The last allowed attempt quarantines the file ..
        is_last_attempt = max_attempts > 0
        if is_last_attempt:
            is_last_attempt = attempt >= max_attempts

        if is_last_attempt:
            quarantine_path = _quarantine_one_file(service, conn, schedule, directory, file_name, current_path, failure)
            if quarantine_path:
                failure['quarantine_path'] = quarantine_path
                out.status = _status_quarantined
            else:
                _release_claim(service, conn, full_path, current_path, failure)
                out.status = _status_failed

        # .. an earlier one leaves it in place for the next run.
        else:
            _release_claim(service, conn, full_path, current_path, failure)
            out.status = _status_failed

        _ = record_schedule_event(audit_log, conn_name, AuditEvent.Delivery_Failed, full_path,
            cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Error,
            file_name=file_name, service=service_name, size=entry.size, error=error, duration_ms=read_ms + service_ms,
            extra=failure, attrs_extra=attrs_extra)

        if out.status == _status_quarantined:
            quarantined = {
                'conn_type': conn_type,
                'attempts': attempt,
                'quarantine_path': failure['quarantine_path'],
                'first_failed_iso': first_failed_iso,
                'error': out.error,
            }
            _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Quarantined, full_path,
                cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Error,
                file_name=file_name, service=service_name, size=entry.size, extra=quarantined, attrs_extra=attrs_extra)

        return out

    # The delivery is recorded before the file is acked.
    delivered = dict(event_extra)
    delivered['read_ms'] = read_ms
    delivered['service_ms'] = service_ms

    if seen_before:
        delivered['seen_before_event_id'] = seen_before['event_id']
        delivered['seen_before_iso'] = seen_before['event_time_iso']
        delivered['seen_before_file_name'] = seen_before['file_name']

    # The delivery carries today's count against the schedule's expectation.
    delivered_today = add_delivered_today(conn_name, schedule_name)
    run.data['delivered_today'] = delivered_today

    delivered['delivered_today'] = delivered_today
    delivered['expected_files'] = schedule['expected_files']
    delivered['expected_by'] = schedule['expected_by']

    delivered_attrs = dict(attrs_extra)
    delivered_attrs['checksum'] = checksum

    _ = record_schedule_event(audit_log, conn_name, AuditEvent.Delivered, full_path,
        cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.OK,
        file_name=file_name, service=service_name, size=entry.size, duration_ms=read_ms + service_ms,
        extra=delivered, attrs_extra=delivered_attrs)

    out.status = _status_processed

    # A failed ack is recorded for this file alone and the run carries on.
    run.set_phase(Phase_Acking, file_name)
    ack_start = monotonic()

    try:
        destination = _ack_one_file(conn, schedule, directory, file_name, full_path, current_path)
    except Exception:
        ack_ms = _elapsed_ms(ack_start)
        error = format_exc()
        service.logger.warning('Could not put file `%s` out of the way after `%s` took it -> `%s`',
            full_path, service_name, error)
        _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Acked, full_path,
            cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.Error,
            file_name=file_name, service=service_name, error=error, duration_ms=ack_ms,
            extra={'ack_ms': ack_ms}, attrs_extra=attrs_extra)
        out.is_ack_failed = True
        return out

    ack_ms = _elapsed_ms(ack_start)

    # What the ack did with the file.
    if destination:
        acked:'stranydict' = {'moved_to': destination}
    else:
        acked = {'deleted': True}

    acked['ack_ms'] = ack_ms

    _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Acked, full_path,
        cid=file_cid, correl_id=run_cid, schedule=schedule_name, outcome=AuditOutcome.OK,
        file_name=file_name, service=service_name, duration_ms=ack_ms, extra=acked, attrs_extra=attrs_extra)

    out.is_acked = True
    return out

# ################################################################################################################################

def _note_skips(run:'RunContext', selection:'Selection') -> 'None':
    """ Adds the skipped entries of a selection to the ledger and the skip counts.
    """
    for entry, reason, next_attempt_iso in selection.skipped:
        name = get_file_name(entry)
        record = build_ledger_record(name, entry.size, entry.last_modified_iso, Decision_Skipped,
            reason=reason, next_attempt_iso=next_attempt_iso)
        run.ledger.append(record)
        run.count_skip(reason)

# ################################################################################################################################

def _note_first_failure(data:'stranydict', name:'str', error:'str') -> 'None':
    """ Records the first failed file and its error, later failures do not replace it.
    """
    if data.get('first_failed_file'):
        return

    data['first_failed_file'] = name
    data['first_failed_error'] = error

# ################################################################################################################################

def _note_file_result(run:'RunContext', entry:'any_', result:'FileResult', duration_ms:'int') -> 'None':
    """ Adds one file's result to the run's counts and ledger.
    """
    data = run.data
    name = get_file_name(entry)
    decision = _decision_for_status[result.status]

    if result.status == _status_processed:
        data['processed'] += 1
        if result.is_acked:
            data['acked'] += 1
        if result.is_ack_failed:
            data['ack_failed'] += 1

    elif result.status == _status_failed:
        data['failed'] += 1
        _note_first_failure(data, name, result.error)

    elif result.status == _status_quarantined:
        data['failed'] += 1
        data['quarantined'] += 1
        _note_first_failure(data, name, result.error)

    else:
        run.count_skip(result.reason)

    record = build_ledger_record(name, entry.size, entry.last_modified_iso, decision,
        reason=result.reason, file_cid=result.file_cid, duration_ms=duration_ms, attempt=result.attempt)
    run.ledger.append(record)

    run.update()

# ################################################################################################################################

def _select_files(
    conn,      # type: any_
    schedule,  # type: stranydict
    directory, # type: str
    entries,   # type: anylist
    run,       # type: RunContext
    ) -> 'anylist':
    """ The files the run takes, as (entry, attempt, first_failed_iso) triples, the rest go into the ledger.
    """

    # Keep only what the schedule may pick up ..
    selection = get_candidates(schedule, entries)
    _note_skips(run, selection)
    candidates = selection.kept
    candidate_count = len(candidates)

    # .. in stability mode, keep the files that stopped changing ..
    if candidates:
        if schedule['ready_how'] == _scheduler.ReadyHow.Stability:
            run.set_phase(Phase_Waiting)
            wait_start = monotonic()
            selection = keep_stable_entries(conn, directory, candidates, schedule['stability_delay'])
            run.data['stability_wait_ms'] = _elapsed_ms(wait_start)
            _note_skips(run, selection)
            candidates = selection.kept

    # .. and keep the files past their retry backoff.
    if candidates:
        since_iso = iso_days_ago(Retry_Memory_Days)
        memory = load_attempt_memory(run.conn_name, run.schedule_name, since_iso)
        now = utcnow()
        selection = keep_entries_past_backoff(candidates, memory, schedule['retry_backoff'], now)
        _note_skips(run, selection)
        out = selection.kept
    else:
        out = []

    taken_count = len(out)
    run.update(candidates=candidate_count, taken=taken_count)

    return out

# ################################################################################################################################

def process_files(service:'Service', context:'stranydict') -> 'None':
    """ One run of a file transfer schedule, the context is the extra data of the schedule's job.
    """

    # Local aliases
    conn_name     = context[_scheduler.Extra_Conn_Name]
    conn_type     = context[_scheduler.Extra_Conn_Type]
    schedule      = context[_scheduler.Extra_Schedule]
    schedule_name = schedule['name']

    apply_schedule_defaults(schedule)

    # The run's cid.
    run_cid = service.cid

    # The directory without a trailing slash.
    directory = schedule['directory'].rstrip('/')

    # Each connection type has its own facade on the service.
    facade_attr = FileTransfer.Facade_Attr[conn_type]
    facade = getattr(service, facade_attr)
    conn = facade[conn_name]

    audit_log:'AuditLog' = conn.wrapper.audit_log

    # Interrupted runs are closed before the new one opens ..
    close_interrupted_runs(audit_log, conn_name, schedule_name)

    # .. and the new run's row is written before the directory is touched.
    scheduler_context = get_scheduler_context(service)
    run = open_run(audit_log, conn_name, directory, run_cid, schedule, scheduler_context)

    # A connection or listing error closes the run as list-failed with the phase it failed in.
    phase = Phase_Checking_Directory
    entries:'anylist' = []
    list_ms = 0

    try:
        run.set_phase(Phase_Checking_Directory)
        directory_exists = conn.exists(directory)

        if directory_exists:
            phase = Phase_Listing
            run.set_phase(Phase_Listing)
            list_start = monotonic()
            entries = conn.list(directory)
            list_ms = _elapsed_ms(list_start)

    except Exception:
        error = format_exc()
        service.logger.warning('Could not list `%s` in `%s` -> `%s`', directory, conn_name, error)
        close_run_list_failed(run, phase, error)
        raise

    # A missing directory means nothing to do.
    if not directory_exists:
        service.logger.info('Directory `%s` does not exist in `%s`, nothing to do', directory, conn_name)
        close_run_no_directory(run)
        return

    note_listing(run, entries, list_ms)

    # An empty directory means nothing to do ..
    if not entries:
        close_run(run)
        return

    # .. otherwise each file is handled on its own, a failed file does not end the run.
    taken = _select_files(conn, schedule, directory, entries, run)

    for index, (entry, attempt, first_failed_iso) in enumerate(taken, 1):

        file_name = get_file_name(entry)
        run.update(taken_so_far=index, current_file=file_name)
        file_start = monotonic()

        try:
            result = _process_one_file(service, conn, context, schedule, directory, entry, attempt,
                first_failed_iso, run)
        except Exception:
            error = format_exc()
            service.logger.warning('Could not handle file `%s` from `%s` -> `%s`', file_name, conn_name, error)
            result = FileResult()
            result.status = _status_failed
            result.attempt = attempt
            result.error = error_summary(error)

        duration_ms = _elapsed_ms(file_start)
        _note_file_result(run, entry, result, duration_ms)

    # The run's row is closed.
    close_run(run)

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit events one file transfer schedule run writes - every file's events under
# the file's own cid, plus the run summary with its counts under the run's cid.
# The schedule engine runs for real against a local directory behind the same client
# interface the SMB wrapper drives, so no remote server is needed.

# stdlib
import os
from hashlib import sha256
from json import loads
from time import monotonic

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.db_env.database import get_database_engine
from zato.common.audit_log.attachment import list_attachments
from zato.common.audit_log.file_transfer import Operation_Move, Operation_Read
from zato.common.audit_log.file_transfer_run import Phase_Claiming, Phase_Done, Phase_Listing, Run_Status_Empty, \
    Run_Status_Interrupted, Run_Status_No_Directory, Run_Status_Running
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_
from zato.common.util.file_transfer_scheduler import apply_schedule_defaults
from zato.server.service.internal.outgoing.file_transfer.process import process_files
from zato.server.service.internal.outgoing.file_transfer.run import close_run, open_run

# Test support
from audit_env import audit_db_env
from schedule_stub import events_of_type, get_attrs, get_events, new_environment, new_schedule, Ack_Error, \
    AckRefusingClient, ClaimObservingClient, ClaimRefusingClient, Connection_Name, Directory, FailingOnceServiceStub, FailingServiceStub, \
    File_Content, File_Name, Release_Error, ReleaseRefusingClient, Run_Cid, Schedule_Name, Service_Error, Service_Logger_Name, \
    ServiceStub, Target_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intnone
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The cid of a run that stopped in the middle of a file
_interrupted_run_cid = 'cid-file-transfer-interrupted-1'

# The scheduler context of a run not fired by the scheduler
_no_scheduler_context = {'job_id': 0, 'current_run': 0}

# The cid of a run besides the one a test checks
_other_run_cid = 'cid-file-transfer-other-1'

# The second file of a directory with two files
_second_file_name = 'summary.csv'

# How long a test waits for the progress of a run to reach its row, and how often it reads the row
_progress_wait_seconds    = 10
_progress_poll_interval   = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _get_run_row(event_id:'intnone') -> 'any_':
    """ The row of the run with the given event id.
    """
    for event in get_events():
        if event['id'] == event_id:
            out = event
            break
    else:
        raise Exception(f'No row of run `{event_id}`')

    return out

# ################################################################################################################################

def _wait_for_entries(event_id:'intnone', entries:'int') -> 'any_':
    """ Waits until the run's row carries the given entry count in its data and returns the row.
    """
    deadline = monotonic() + _progress_wait_seconds

    while True:
        row = _get_run_row(event_id)
        data = loads(row['data'])

        if data['entries'] == entries:
            return row

        if monotonic() > deadline:
            raise Exception(f'Entries {entries} did not reach the row of run `{event_id}` -> {data}')

        gevent_sleep(_progress_poll_interval)

# ################################################################################################################################

def _get_read_event(events:'any_') -> 'any_':
    """ The one event that recorded the read operation.
    """
    for item in events:
        if item['event_type'] == AuditEvent.Request_Sent:
            if loads(item['data'])['operation'] == Operation_Read:
                out = item
                break
    else:
        raise Exception('No read event found')

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_processed_file_shares_one_cid_and_carries_the_schedule(tmp_path:'any_') -> 'None':
    """ One file taken with claiming on writes all its events - the claim rename, the read,
    the hand-over, the archive move and the ack - under the file's own cid, with the run's
    cid in every schedule-level event and the run summary written last.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True)

        process_files(cast_('any_', service), context)

        # The target service received the file once, with the bytes and the context
        assert len(service.invoked) == 1

        service_name, item = service.invoked[0]
        assert service_name == Target_Service
        assert service.contents[0] == File_Content
        assert item.file_name == File_Name
        assert item.schedule_name == Schedule_Name

        # The file itself was moved into the archive directory
        assert os.path.exists(os.path.join(base_dir, Directory, _scheduler.Default_Move_Directory, File_Name))
        assert not os.path.exists(os.path.join(base_dir, Directory, File_Name))

        # The events, in order - the run's own row, opened first and closed with the summary,
        # then the claim rename, the read, the hand-over, the archive move and the ack.
        events = get_events()
        assert len(events) == 6

        run_completed, claim_move, read, delivered, ack_move, acked = events

        assert loads(claim_move['data'])['operation'] == Operation_Move
        assert loads(read['data'])['operation'] == Operation_Read
        assert delivered['event_type'] == AuditEvent.Delivered
        assert loads(ack_move['data'])['operation'] == Operation_Move
        assert acked['event_type'] == AuditEvent.File_Acked
        assert run_completed['event_type'] == AuditEvent.Run_Completed

        # Every event of the file, connection-level and schedule-level alike, shares one cid ..
        file_cid = claim_move['cid']
        assert file_cid != Run_Cid

        for event in (read, delivered, ack_move, acked):
            assert event['cid'] == file_cid

        # .. the schedule-level events say which run took the file ..
        assert delivered['correl_id'] == Run_Cid
        assert acked['correl_id'] == Run_Cid

        # .. and the summary belongs to the run itself.
        assert run_completed['cid'] == Run_Cid
        assert run_completed['correl_id'] == Run_Cid

        # Everything about the hand-over is searchable
        delivered_attrs = get_attrs(delivered['id'])
        assert delivered_attrs['schedule'] == Schedule_Name
        assert delivered_attrs['file_name'] == File_Name
        assert delivered_attrs['service'] == Target_Service

        # The ack says where the file went
        acked_summary = loads(acked['data'])
        assert acked_summary['moved_to'] == f'{Directory}/{_scheduler.Default_Move_Directory}/{File_Name}'

        # The summary counts what the run saw and did
        run_summary = loads(run_completed['data'])
        assert run_summary['entries'] == 1
        assert run_summary['candidates'] == 1
        assert run_summary['processed'] == 1
        assert run_summary['failed'] == 0

# ################################################################################################################################

def test_a_run_summary_counts_a_failure_next_to_a_success(tmp_path:'any_') -> 'None':
    """ A file the target service refuses never ends the run for the file behind it,
    and the run summary tells the two apart.
    """
    class OneFileFails(ServiceStub):

        def invoke(self, service_name:'str', item:'any_', cid:'str'='') -> 'None':
            if item.file_name == 'bad.csv':
                raise Exception(Service_Error)
            super().invoke(service_name, item, cid)

    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path,
            service_class=OneFileFails, file_names=['bad.csv', 'good.csv'])
        context[_scheduler.Extra_Schedule] = new_schedule()

        with expected_records(Service_Logger_Name):
            process_files(cast_('any_', service), context)

        # Only the accepted file reached the target service ..
        assert len(service.invoked) == 1
        assert service.invoked[0][1].file_name == 'good.csv'

        # .. the refused one stayed in place for the next run ..
        assert os.path.exists(os.path.join(base_dir, Directory, 'bad.csv'))

        # .. and the summary counts both outcomes.
        events = get_events()
        run_completed = events_of_type(events, AuditEvent.Run_Completed)[0]

        run_summary = loads(run_completed['data'])
        assert run_summary['entries'] == 2
        assert run_summary['candidates'] == 2
        assert run_summary['processed'] == 1
        assert run_summary['failed'] == 1

# ################################################################################################################################

def test_a_lost_claim_is_recorded(tmp_path:'any_') -> 'None':
    """ A file another consumer claimed first is skipped, which the trail says
    without counting the file as processed or failed.
    """
    with audit_db_env():

        service, context, _ = new_environment(tmp_path, client_class=ClaimRefusingClient)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True)

        process_files(cast_('any_', service), context)

        # Nothing reached the target service
        assert service.invoked == []

        events = get_events()

        # The lost claim is on record with what went wrong
        claimed = events_of_type(events, AuditEvent.File_Claimed)[0]

        assert claimed['outcome'] == AuditOutcome.Error
        assert 'Already claimed by another consumer' in claimed['data']

        # The run summary counts the file as neither processed nor failed
        run_completed = events_of_type(events, AuditEvent.Run_Completed)[0]

        run_summary = loads(run_completed['data'])
        assert run_summary['candidates'] == 1
        assert run_summary['processed'] == 0
        assert run_summary['failed'] == 0

# ################################################################################################################################

def test_a_failing_service_leaves_the_error_and_the_file(tmp_path:'any_') -> 'None':
    """ A target service that is down leaves a delivery-failed event with the error text
    and the file stays in place for the next run.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path, service_class=FailingServiceStub)
        context[_scheduler.Extra_Schedule] = new_schedule()

        with expected_records(Service_Logger_Name):
            process_files(cast_('any_', service), context)

        # The file was never lost - it waits for the next run
        assert os.path.exists(os.path.join(base_dir, Directory, File_Name))

        events = get_events()

        failed = events_of_type(events, AuditEvent.Delivery_Failed)[0]

        assert failed['outcome'] == AuditOutcome.Error
        assert Service_Error in failed['data']

        failed_attrs = get_attrs(failed['id'])
        assert failed_attrs['schedule'] == Schedule_Name
        assert failed_attrs['service'] == Target_Service

        run_completed = events_of_type(events, AuditEvent.Run_Completed)[0]

        run_summary = loads(run_completed['data'])
        assert run_summary['processed'] == 0
        assert run_summary['failed'] == 1

# ################################################################################################################################

def test_a_deleting_schedule_says_so_in_the_ack(tmp_path:'any_') -> 'None':
    """ A schedule that deletes what it took says so in the file's ack.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule(on_success=_scheduler.OnSuccess.Delete)

        process_files(cast_('any_', service), context)

        # The file is gone rather than archived
        assert not os.path.exists(os.path.join(base_dir, Directory, File_Name))

        events = get_events()

        acked = events_of_type(events, AuditEvent.File_Acked)[0]

        acked_summary = loads(acked['data'])
        assert acked_summary['deleted'] is True

# ################################################################################################################################

def test_the_read_carries_a_checksum(tmp_path:'any_') -> 'None':
    """ The read event carries a SHA-256 digest of the bytes as a searchable attribute.
    """
    with audit_db_env():

        service, context, _ = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule()

        process_files(cast_('any_', service), context)

        events = get_events()
        read = _get_read_event(events)

        attrs = get_attrs(read['id'])
        assert attrs['checksum'] == sha256(File_Content).hexdigest()

# ################################################################################################################################

def test_content_is_stored_on_read_when_opted_in(tmp_path:'any_') -> 'None':
    """ A connection with content storage turned on keeps the picked-up bytes
    as an attachment of the read event.
    """
    with audit_db_env():

        service, context, _ = new_environment(tmp_path, should_store_content=True)
        context[_scheduler.Extra_Schedule] = new_schedule()

        process_files(cast_('any_', service), context)

        events = get_events()
        read = _get_read_event(events)

        engine = get_database_engine()
        items = list_attachments(engine, read['id'])

        assert len(items) == 1
        assert items[0]['filename'] == File_Name
        assert items[0]['is_content_kept'] is True

# ################################################################################################################################

def test_a_missing_directory_leaves_a_run_summary_with_the_note(tmp_path:'any_') -> 'None':
    """ When the polled directory does not exist, the run summary is still written
    and its status names the reason.
    """
    with audit_db_env():

        service, context, _ = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule(directory='share/not-there')

        with expected_records(Service_Logger_Name):
            process_files(cast_('any_', service), context)

        events = get_events()
        assert len(events) == 1

        run_completed = events[0]

        assert run_completed['event_type'] == AuditEvent.Run_Completed
        assert run_completed['source'] == AuditSource.File_Outgoing

        assert run_completed['outcome'] == AuditOutcome.Error
        assert run_completed['status'] == Run_Status_No_Directory

        run_summary = loads(run_completed['data'])
        assert run_summary['entries'] == 0

# ################################################################################################################################

def test_a_claim_left_by_an_interrupted_run_is_released(tmp_path:'any_') -> 'None':
    """ A run that stopped in the middle of a file leaves the file under its claim name,
    and the next run renames it back before it lists the directory, so the file is delivered.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path)

        schedule = new_schedule(should_claim=True)
        apply_schedule_defaults(schedule)
        context[_scheduler.Extra_Schedule] = schedule

        # A run that claimed the file before it stopped ..
        audit_log = service.smb[Connection_Name].wrapper.audit_log
        interrupted = open_run(audit_log, Connection_Name, Directory, _interrupted_run_cid, schedule, _no_scheduler_context)
        interrupted.begin_claim(File_Name)

        # .. with the file still under its claim name.
        file_path = os.path.join(base_dir, Directory, File_Name)
        claim_path = file_path + _scheduler.Claim_Suffix
        os.rename(file_path, claim_path)

        process_files(cast_('any_', service), context)

        # The file was released and delivered ..
        assert len(service.invoked) == 1
        assert service.invoked[0][1].file_name == File_Name
        assert not os.path.exists(claim_path)

        # .. and the interrupted run says that its claim was released.
        events = get_events()
        run_completed = events_of_type(events, AuditEvent.Run_Completed)
        interrupted_row = run_completed[0]

        assert interrupted_row['cid'] == _interrupted_run_cid
        assert interrupted_row['status'] == Run_Status_Interrupted

        interrupted_summary = loads(interrupted_row['data'])
        assert interrupted_summary['claim_released'] is True

# ################################################################################################################################

def test_a_file_whose_ack_failed_is_acked_by_the_next_run(tmp_path:'any_') -> 'None':
    """ A file delivered while its ack fails stays under its claim name, and the next run acks it
    before it lists the directory, without delivering it again.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path, client_class=AckRefusingClient)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True)

        file_path = os.path.join(base_dir, Directory, File_Name)
        claim_path = file_path + _scheduler.Claim_Suffix
        archive_path = os.path.join(base_dir, Directory, _scheduler.Default_Move_Directory, File_Name)

        # The first run delivers the file and fails to ack it ..
        with expected_records(Service_Logger_Name):
            process_files(cast_('any_', service), context)

        assert len(service.invoked) == 1
        assert os.path.exists(claim_path)
        assert not os.path.exists(archive_path)

        # .. and the next run acks it without delivering it again.
        process_files(cast_('any_', service), context)

        assert len(service.invoked) == 1
        assert not os.path.exists(claim_path)
        assert os.path.exists(archive_path)

        # The trail has the failed ack and the successful one, both under the cid of the file.
        events = get_events()
        acked = events_of_type(events, AuditEvent.File_Acked)

        failed_ack, retried_ack = acked

        assert failed_ack['outcome'] == AuditOutcome.Error
        assert Ack_Error in failed_ack['data']

        assert retried_ack['outcome'] == AuditOutcome.OK
        assert retried_ack['cid'] == failed_ack['cid']

        retried_summary = loads(retried_ack['data'])
        assert retried_summary['moved_to'] == f'{Directory}/{_scheduler.Default_Move_Directory}/{File_Name}'

# ################################################################################################################################

def test_a_claim_that_could_not_be_released_is_released_by_the_next_run(tmp_path:'any_') -> 'None':
    """ A file whose delivery fails stays under its claim name when the claim cannot be released,
    and the next run releases it before it lists the directory, so the file is delivered.
    """
    with audit_db_env():

        service, context, base_dir = new_environment(tmp_path,
            client_class=ReleaseRefusingClient, service_class=FailingOnceServiceStub)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True, retry_backoff=0)

        file_path = os.path.join(base_dir, Directory, File_Name)
        claim_path = file_path + _scheduler.Claim_Suffix
        archive_path = os.path.join(base_dir, Directory, _scheduler.Default_Move_Directory, File_Name)

        # The first run fails to deliver the file and fails to release its claim ..
        with expected_records(Service_Logger_Name):
            process_files(cast_('any_', service), context)

        assert service.invoked == []
        assert os.path.exists(claim_path)

        # .. and the next run releases the claim and delivers the file.
        process_files(cast_('any_', service), context)

        assert len(service.invoked) == 1
        assert service.invoked[0][1].file_name == File_Name
        assert not os.path.exists(claim_path)
        assert os.path.exists(archive_path)

        # The trail has the failed delivery with the claim that was not released.
        events = get_events()
        failed = events_of_type(events, AuditEvent.Delivery_Failed)[0]

        failed_summary = loads(failed['data'])
        assert failed_summary['claim_released'] is False
        assert Release_Error in failed_summary['release_error']

# ################################################################################################################################

def test_each_file_is_committed_as_current_before_its_claim(tmp_path:'any_') -> 'None':
    """ The run's row names the file the run is about to claim before the file is renamed to its claim name,
    so a run interrupted after any rename releases the claim.
    """
    with audit_db_env():

        file_names = [File_Name, _second_file_name]

        service, context, _ = new_environment(tmp_path, client_class=ClaimObservingClient, file_names=file_names)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True)

        process_files(cast_('any_', service), context)

        assert len(service.invoked) == 2

        # The row read at the moment of each claim rename names the file that was being claimed.
        wrapper = service.smb[Connection_Name].wrapper
        with wrapper.client(should_block=True, block_timeout=0) as client:
            data_at_claim = client.data_at_claim

        assert len(data_at_claim) == 2

        claimed_files = set()

        for data in data_at_claim:
            assert data['phase'] == Phase_Claiming
            claimed_files.add(data['current_file'])

        assert claimed_files == set(file_names)

# ################################################################################################################################

def test_the_newest_progress_of_a_run_reaches_its_row(tmp_path:'any_') -> 'None':
    """ The progress of a run is written to its row in the background, and of several notes
    made before the write the row receives the newest.
    """
    with audit_db_env():

        service, _, _ = new_environment(tmp_path)

        schedule = new_schedule()
        apply_schedule_defaults(schedule)

        audit_log = service.smb[Connection_Name].wrapper.audit_log
        run = open_run(audit_log, Connection_Name, Directory, Run_Cid, schedule, _no_scheduler_context)

        # Several notes of progress ..
        run.set_phase(Phase_Listing)
        run.note_progress(entries=3)
        run.note_progress(entries=5)

        # .. reach the row as the newest of them.
        row = _wait_for_entries(run.event_id, 5)
        data = loads(row['data'])

        assert data['phase'] == Phase_Listing
        assert row['status'] == Run_Status_Running

# ################################################################################################################################

def test_the_progress_of_a_closed_run_keeps_its_closed_row(tmp_path:'any_') -> 'None':
    """ The progress of a run still pending when the run closes leaves the closed row as the run closed it.
    """
    with audit_db_env():

        service, _, _ = new_environment(tmp_path)

        schedule = new_schedule()
        apply_schedule_defaults(schedule)

        audit_log = service.smb[Connection_Name].wrapper.audit_log

        # A run closes while its progress is pending ..
        closed = open_run(audit_log, Connection_Name, Directory, Run_Cid, schedule, _no_scheduler_context)
        closed.note_progress(entries=3)
        close_run(closed)

        # .. the progress of another run reaches its row, so the writer has run since ..
        other = open_run(audit_log, Connection_Name, Directory, _other_run_cid, schedule, _no_scheduler_context)
        other.note_progress(entries=7)
        _ = _wait_for_entries(other.event_id, 7)

        # .. and the closed run's row is still the one it closed with.
        row = _get_run_row(closed.event_id)
        data = loads(row['data'])

        assert row['status'] == Run_Status_Empty
        assert data['phase'] == Phase_Done
        assert data['entries'] == 3

# ################################################################################################################################
# ################################################################################################################################

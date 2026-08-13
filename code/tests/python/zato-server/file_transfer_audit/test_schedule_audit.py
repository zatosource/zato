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

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import list_attachments
from zato.common.audit_log.file_transfer import Operation_Move, Operation_Read
from zato.common.typing_ import cast_
from zato.server.service.internal.outgoing.file_transfer.process import process_files

# Test support
from audit_env import audit_db_env
from schedule_stub import events_of_type, get_attrs, get_events, new_environment, new_schedule, ClaimRefusingClient, \
    Directory, FailingServiceStub, File_Content, File_Name, Run_Cid, Schedule_Name, Service_Error, ServiceStub, Target_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
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
    with audit_db_env(tmp_path):

        service, context, base_dir = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule(should_claim=True)

        process_files(cast_('any_', service), context)

        # The target service received the file once, with the bytes and the context
        assert len(service.invoked) == 1

        service_name, item = service.invoked[0]
        assert service_name == Target_Service
        assert item.data == File_Content
        assert item.file_name == File_Name
        assert item.schedule_name == Schedule_Name

        # The file itself was moved into the archive directory
        assert os.path.exists(os.path.join(base_dir, Directory, _scheduler.Default_Move_Directory, File_Name))
        assert not os.path.exists(os.path.join(base_dir, Directory, File_Name))

        # The events, in order - the claim rename, the read, the hand-over,
        # the archive move, the ack and the run summary.
        events = get_events()
        assert len(events) == 6

        claim_move, read, delivered, ack_move, acked, run_completed = events

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

        def invoke(self, service_name:'str', item:'any_') -> 'None':
            if item.file_name == 'bad.csv':
                raise Exception(Service_Error)
            super().invoke(service_name, item)

    with audit_db_env(tmp_path):

        service, context, base_dir = new_environment(tmp_path,
            service_class=OneFileFails, file_names=['bad.csv', 'good.csv'])
        context[_scheduler.Extra_Schedule] = new_schedule()

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
    with audit_db_env(tmp_path):

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
    with audit_db_env(tmp_path):

        service, context, base_dir = new_environment(tmp_path, service_class=FailingServiceStub)
        context[_scheduler.Extra_Schedule] = new_schedule()

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
    with audit_db_env(tmp_path):

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
    with audit_db_env(tmp_path):

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
    with audit_db_env(tmp_path):

        service, context, _ = new_environment(tmp_path, should_store_content=True)
        context[_scheduler.Extra_Schedule] = new_schedule()

        process_files(cast_('any_', service), context)

        events = get_events()
        read = _get_read_event(events)

        engine = get_audit_engine()
        items = list_attachments(engine, read['id'])

        assert len(items) == 1
        assert items[0]['filename'] == File_Name
        assert items[0]['is_content_kept'] is True

# ################################################################################################################################

def test_a_missing_directory_leaves_a_run_summary_with_the_note(tmp_path:'any_') -> 'None':
    """ When the polled directory does not exist, the run summary is still written
    and its note names the reason.
    """
    with audit_db_env(tmp_path):

        service, context, _ = new_environment(tmp_path)
        context[_scheduler.Extra_Schedule] = new_schedule(directory='share/not-there')

        process_files(cast_('any_', service), context)

        events = get_events()
        assert len(events) == 1

        run_completed = events[0]

        assert run_completed['event_type'] == AuditEvent.Run_Completed
        assert run_completed['source'] == AuditSource.File_Outgoing

        run_summary = loads(run_completed['data'])
        assert run_summary['entries'] == 0
        assert run_summary['note'] == 'Directory does not exist'

# ################################################################################################################################
# ################################################################################################################################

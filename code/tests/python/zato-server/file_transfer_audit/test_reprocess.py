# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Reprocessing a file transfer from the audit log - the stored file content is handed
# to the schedule's target service again and the new attempt is recorded as its own event
# linked to the original one. An event with no stored content cannot be reprocessed.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import event_link_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.audit_log.resubmit import source_resubmit_actions, is_event_type_resubmittable
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.service.internal.audit_log import ReprocessFileTransfer
from zato.server.service.internal.outgoing.file_transfer.process import process_files

# Test support
from audit_env import audit_db_env, Server_Name
from schedule_stub import events_of_type, get_events, new_environment, new_schedule, File_Content, File_Name, \
    Schedule_Name, Target_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The name of the service the resubmit catalog points file transfer events at
Reprocess_Service = 'zato.audit-log.file-transfer-reprocess'

# The cid the reprocess itself runs with
Reprocess_Cid = 'cid-reprocess-1'

# What the failing reprocess target says
Reprocess_Error = 'The target system is still down'

# ################################################################################################################################
# ################################################################################################################################

class ServerStub:
    """ Stands in for the server the reprocess service runs on - it remembers
    what was handed to the target service.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name
        self.invoked:'any_' = []

    def invoke(self, service_name:'str', item:'any_') -> 'None':
        self.invoked.append((service_name, item))

# ################################################################################################################################

class FailingServerStub(ServerStub):
    """ A server whose target service is still down - every invocation fails.
    """

    def invoke(self, service_name:'str', item:'any_') -> 'None':
        raise Exception(Reprocess_Error)

# ################################################################################################################################
# ################################################################################################################################

def _run_reprocess(event_id:'int', server:'ServerStub') -> 'stranydict':
    """ Runs the reprocess service over one stored event and returns the report it produced.
    """
    harness = Bunch()
    harness.cid = Reprocess_Cid
    harness.server = server
    harness.request = Bunch(input=Bunch(event_id=event_id))
    harness.response = Bunch(payload=Bunch())

    ReprocessFileTransfer.handle(cast_('any_', harness))

    out = loads(harness.response.payload.response_data)
    return out

# ################################################################################################################################

def _run_one_schedule(tmp_path:'any_', *, should_store_content:'bool') -> 'None':
    """ One schedule run over one file - it writes the events the reprocess reads back.
    """
    service, context, _ = new_environment(tmp_path, should_store_content=should_store_content)
    context[_scheduler.Extra_Schedule] = new_schedule()

    process_files(cast_('any_', service), context)

# ################################################################################################################################

def _get_parents(event_id:'int') -> 'intlist':
    """ The ids of the events one event names as its parents.
    """
    engine = get_audit_engine()

    query = select(event_link_table.c.parent_event_id)
    query = query.where(event_link_table.c.child_event_id == event_id)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_catalog_offers_reprocess_for_deliveries() -> 'None':
    """ The audit log page renders its per-row actions out of the catalog,
    which says a delivery of either outcome can be run through the service again.
    """
    actions = source_resubmit_actions[AuditSource.File_Outgoing]

    assert actions[AuditEvent.Delivered]['service'] == Reprocess_Service
    assert actions[AuditEvent.Delivery_Failed]['service'] == Reprocess_Service

    assert is_event_type_resubmittable(AuditSource.File_Outgoing, AuditEvent.Delivered)
    assert is_event_type_resubmittable(AuditSource.File_Outgoing, AuditEvent.Delivery_Failed)
    assert not is_event_type_resubmittable(AuditSource.File_Outgoing, AuditEvent.Run_Completed)

# ################################################################################################################################

def test_a_reprocess_reinvokes_the_service_with_the_archived_bytes(tmp_path:'any_') -> 'None':
    """ A reprocess hands the archived bytes to the schedule's target service again
    and leaves the new attempt as its own event linked to the original one.
    """
    with audit_db_env(tmp_path):

        _run_one_schedule(tmp_path, should_store_content=True)

        delivered = events_of_type(get_events(), AuditEvent.Delivered)[0]

        server = ServerStub()
        report = _run_reprocess(delivered['id'], server)

        assert report['is_ok'] is True
        assert report['cid'] == Reprocess_Cid

        # The target service received the same file again, rebuilt in full
        assert len(server.invoked) == 1

        service_name, item = server.invoked[0]
        assert service_name == Target_Service
        assert item.data == File_Content
        assert item.file_name == File_Name
        assert item.schedule_name == Schedule_Name

        # The new attempt is its own event, sharing the original run's correlation id
        # and naming the original event as its parent
        new_event = events_of_type(get_events(), AuditEvent.Delivered)[1]

        assert new_event['id'] == report['event_id']
        assert new_event['cid'] == Reprocess_Cid
        assert new_event['correl_id'] == delivered['cid']

        assert _get_parents(new_event['id']) == [delivered['id']]

# ################################################################################################################################

def test_a_failed_reprocess_is_recorded_too(tmp_path:'any_') -> 'None':
    """ A reprocess whose target service is still down comes back as a report
    with the error inside, and the failed attempt is on record with the same links.
    """
    with audit_db_env(tmp_path):

        _run_one_schedule(tmp_path, should_store_content=True)

        delivered = events_of_type(get_events(), AuditEvent.Delivered)[0]

        report = _run_reprocess(delivered['id'], FailingServerStub())

        assert report['is_ok'] is False
        assert Reprocess_Error in report['error']

        # The failed attempt is linked the same way a successful one is
        failed = events_of_type(get_events(), AuditEvent.Delivery_Failed)[0]

        assert failed['cid'] == Reprocess_Cid
        assert failed['correl_id'] == delivered['cid']
        assert Reprocess_Error in failed['data']

        assert _get_parents(failed['id']) == [delivered['id']]

# ################################################################################################################################

def test_an_event_without_stored_content_refuses(tmp_path:'any_') -> 'None':
    """ When the read event stored no bytes, there is nothing to hand to the service again
    and the report carries the error saying so.
    """
    with audit_db_env(tmp_path):

        _run_one_schedule(tmp_path, should_store_content=False)

        delivered = events_of_type(get_events(), AuditEvent.Delivered)[0]

        server = ServerStub()
        report = _run_reprocess(delivered['id'], server)

        assert report['is_ok'] is False
        assert 'stored no file content' in report['error']

        # Nothing reached the target service
        assert server.invoked == []

# ################################################################################################################################

def test_only_deliveries_can_be_reprocessed(tmp_path:'any_') -> 'None':
    """ A run summary is not a file hand-over - asking to reprocess one refuses.
    """
    with audit_db_env(tmp_path):

        _run_one_schedule(tmp_path, should_store_content=True)

        run_completed = events_of_type(get_events(), AuditEvent.Run_Completed)[0]

        report = _run_reprocess(run_completed['id'], ServerStub())

        assert report['is_ok'] is False
        assert 'can be reprocessed' in report['error']

# ################################################################################################################################
# ################################################################################################################################

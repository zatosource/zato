# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_sql.env import database_env
from support import attributes_of, build_config, decode_records, wait_for_bodies, wait_until, FakeSender, Server_Name
from zato.common.api import SCHEDULER
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.export.api import get_audit_export, set_audit_export, AuditExport, ModuleCtx as APICtx
from zato.common.audit_log.export.data import ModuleCtx as DataCtx
from zato.common.audit_log.export.mapping import ModuleCtx as MappingCtx
from zato.common.audit_log.file_transfer import record_file_transfer
from zato.common.audit_log.file_transfer_run import update_run_event
from zato.common.audit_log.scheduler import record_job_complete, record_job_start, record_job_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from opentelemetry.proto.logs.v1.logs_pb2 import LogRecord
    from zato.common.typing_ import any_, stranydict

    log_record_list = list[LogRecord]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

def _column(name:'str') -> 'str':
    out = f'{MappingCtx.Prefix}.{name}'
    return out

def _attr(name:'str') -> 'str':
    out = f'{MappingCtx.Attr_Prefix}.{name}'
    return out

def _data(name:'str') -> 'str':
    out = f'{DataCtx.Data_Prefix}.{name}'
    return out

def _payload(name:'str') -> 'str':
    out = f'{DataCtx.Payload_Prefix}.{name}'
    return out

# ################################################################################################################################

def _read_row(event_id:'int') -> 'stranydict':
    """ The event's row as the database holds it.
    """
    engine = get_audit_engine()
    query = select(event_table).where(event_table.c.id == event_id)

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    assert row is not None

    out = dict(row)
    return out

# ################################################################################################################################

def wait_for_bodies_briefly(sender:'FakeSender') -> 'bool':
    """ Gives the worker a moment and says whether anything arrived - for tests expecting nothing to.
    """
    def check() -> 'bool':
        return len(sender.bodies) > 0

    out = wait_until(check, timeout=0.2)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _HookTestCase(TestCase):
    """ An audit log on a temporary SQLite file with the export on, over a fake sender.
    """

    def setUp(self) -> 'None':
        self.directory = mkdtemp(prefix='zato-audit-export-')
        db_path = os.path.join(self.directory, 'audit.db')

        self.env = database_env(_env_prefix, {'type': AuditLogCtx.Type_SQLite, 'name': db_path})
        _ = self.env.__enter__()

        self.saved_enabled = os.environ.pop(AuditLogCtx.Env_Enabled, None)

        self.sender = FakeSender()
        self.export = self.build_export(batch_size=1, flush_interval_ms=20)

        self.audit_log = AuditLog(Server_Name, flush_max_size=1, flush_max_wait_ms=1)

    def tearDown(self) -> 'None':
        set_audit_export(None)
        self.export.queue.flush_and_stop(1.0)

        # The switch goes back to what it was, a test that turned it off included
        _ = os.environ.pop(AuditLogCtx.Env_Enabled, None)

        if self.saved_enabled is not None:
            os.environ[AuditLogCtx.Env_Enabled] = self.saved_enabled

        _ = self.env.__exit__(None, None, None)
        rmtree(self.directory, ignore_errors=True)

# ################################################################################################################################

    def build_export(self, **overrides:'any_') -> 'AuditExport':
        """ Builds the process-wide export over the fake sender and registers it.
        """
        config = build_config(**overrides)

        out = AuditExport(config, service_name=APICtx.Service_Server, server_name=Server_Name, cluster_name='test-cluster',
            instance_id='deploy-1', version='4.1')

        # The real sender is replaced before anything is sent
        out.queue.sender.close()
        out.queue.sender = self.sender

        set_audit_export(out)

        return out

# ################################################################################################################################

    def records(self) -> 'log_record_list':
        out = self.sender.get_records()
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestHandOff(_HookTestCase):

    def test_committed_events_are_handed_off_with_their_ids(self) -> 'None':

        self.assertIs(get_audit_export(), self.export)

        first_id = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
            cid='cid-1', endpoint='/billing/invoices', size=120, outcome=AuditOutcome.OK, data='{"invoice_id": "INV-1"}',
            attrs={'method': 'POST', 'retries': 2})

        second_id = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'billing.invoices',
            cid='cid-1', endpoint='/billing/invoices', size=64, outcome=AuditOutcome.Error, status='500')

        self.assertIsNotNone(first_id)
        self.assertIsNotNone(second_id)

        self.assertTrue(wait_for_bodies(self.sender, 2))

        records = self.records()
        self.assertEqual(len(records), 2)

        first = attributes_of(records[0])
        second = attributes_of(records[1])

        # The ids are the ones the database gave ..
        self.assertEqual(first[MappingCtx.Event_ID], first_id)
        self.assertEqual(second[MappingCtx.Event_ID], second_id)

        # .. the columns are what the rows hold ..
        if first_id:
            row = _read_row(first_id)

            self.assertEqual(first[_column('cid')], row['cid'])
            self.assertEqual(first[_column('cid_sequence')], row['cid_sequence'])
            self.assertEqual(first[_column('source')], row['source'])
            self.assertEqual(first[_column('event_type')], row['event_type'])
            self.assertEqual(first[_column('object_name')], row['object_name'])
            self.assertEqual(first[_column('endpoint')], row['endpoint'])
            self.assertEqual(first[_column('size')], row['size'])
            self.assertEqual(first[_column('outcome')], row['outcome'])
            self.assertEqual(first[_column('classification')], row['classification'])

            # .. the record's time is the row's time ..
            event_time = datetime.fromisoformat(row['event_time_iso'])
            expected_ns = int(event_time.timestamp()) * 1_000_000_000 + event_time.microsecond * 1000
            self.assertEqual(records[0].time_unix_nano, expected_ns)

        # .. the attrs are the dict as it was given ..
        self.assertEqual(first[_attr('method')], 'POST')
        self.assertEqual(first[_attr('retries')], 2)

        # .. and the second event has its sequence and severity.
        self.assertEqual(second[_column('cid_sequence')], 2)
        self.assertEqual(second[_column('status')], '500')
        self.assertEqual(records[1].severity_text, 'ERROR')

        # A REST channel's data never leaves without the payload flag
        self.assertNotIn(_payload('data'), first)

        # The resource names the process
        request = decode_records(self.sender.bodies[0])
        self.assertEqual(len(request), 1)

        stats = self.export.queue.get_stats()
        self.assertEqual(stats['emitted'], 2)
        self.assertEqual(stats['exported'], 2)
        self.assertEqual(stats['dropped'], 0)

# ################################################################################################################################

    def test_buffered_writer_hands_off_after_its_flush(self) -> 'None':

        audit_log = AuditLog(Server_Name, flush_max_size=3, flush_max_wait_ms=60000)

        for index in range(3):
            out = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
                cid=f'cid-buffered-{index}', outcome=AuditOutcome.OK)
            self.assertIsNone(out)

        self.assertTrue(wait_for_bodies(self.sender, 1))

        records = self.records()
        self.assertEqual(len(records), 3)

        ids = []
        for record in records:
            ids.append(attributes_of(record)[MappingCtx.Event_ID])

        self.assertEqual(ids, sorted(ids))
        self.assertGreater(ids[0], 0)

        for event_id in ids:
            row = _read_row(event_id)
            self.assertEqual(row['source'], AuditSource.REST_Channel)

# ################################################################################################################################

    def test_nothing_when_the_audit_log_is_off(self) -> 'None':

        os.environ[AuditLogCtx.Env_Enabled] = 'false'

        out = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
            cid='cid-off', outcome=AuditOutcome.OK)

        self.assertIsNone(out)
        self.assertEqual(self.export.queue.get_stats()['emitted'], 0)

        # Nothing was written, so nothing can arrive
        self.assertFalse(wait_for_bodies_briefly(self.sender))
        self.assertEqual(self.sender.attempts, [])

# ################################################################################################################################

    def test_nothing_for_an_unselected_source(self) -> 'None':

        self.export.queue.flush_and_stop(1.0)
        self.export = self.build_export(batch_size=1, flush_interval_ms=20, sources={AuditSource.MCP})

        rest_id = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
            cid='cid-rest', outcome=AuditOutcome.OK)

        mcp_id = self.audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, 'billing',
            cid='cid-mcp', endpoint='billing.invoice.get', outcome=AuditOutcome.OK, data='{"method": "tools/call"}')

        # Both are in the database ..
        self.assertIsNotNone(rest_id)
        self.assertIsNotNone(mcp_id)

        # .. only the MCP one was handed off.
        self.assertTrue(wait_for_bodies(self.sender, 1))

        records = self.records()
        self.assertEqual(len(records), 1)

        attributes = attributes_of(records[0])
        self.assertEqual(attributes[MappingCtx.Event_ID], mcp_id)
        self.assertEqual(attributes[_column('source')], AuditSource.MCP)
        self.assertEqual(attributes[_data('method')], 'tools/call')

        self.assertEqual(self.export.queue.get_stats()['emitted'], 1)

# ################################################################################################################################

    def test_no_export_means_no_hand_off(self) -> 'None':

        set_audit_export(None)

        out = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
            cid='cid-no-export', outcome=AuditOutcome.OK)

        self.assertIsNotNone(out)
        self.assertEqual(self.export.queue.get_stats()['emitted'], 0)

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadFlag(_HookTestCase):

    def test_flag_off_keeps_no_payload_in_the_queue(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'billing.invoices',
            cid='cid-flag-off', outcome=AuditOutcome.OK, data='{"invoice_id": "INV-1"}',
            bodies={AuditBody.Request: '{"invoice_id": "INV-1"}'})

        self.assertTrue(wait_for_bodies(self.sender, 1))

        attributes = attributes_of(self.records()[0])

        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

        self.assertNotIn('INV-1', str(attributes))

# ################################################################################################################################

    def test_flag_on_sends_the_payload(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'billing.invoices',
            cid='cid-flag-on', outcome=AuditOutcome.OK, data='{"status": "accepted"}',
            bodies={AuditBody.Request: '{"invoice_id": "INV-1"}', AuditBody.Response: '{"status": "accepted"}'},
            is_export_payload_active=True)

        self.assertTrue(wait_for_bodies(self.sender, 1))

        attributes = attributes_of(self.records()[0])

        self.assertEqual(attributes[_payload('data')], '{"status": "accepted"}')
        self.assertEqual(attributes[_payload(AuditBody.Request)], '{"invoice_id": "INV-1"}')
        self.assertEqual(attributes[_payload(AuditBody.Response)], '{"status": "accepted"}')
        self.assertNotIn(DataCtx.Payload_Truncated, attributes)

# ################################################################################################################################

    def test_payload_is_cut_to_the_configured_size(self) -> 'None':

        self.export.queue.flush_and_stop(1.0)
        self.export = self.build_export(batch_size=1, flush_interval_ms=20, max_payload_size=8)

        _ = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'billing.invoices',
            cid='cid-flag-cut', outcome=AuditOutcome.OK, data='{"status": "accepted"}', is_export_payload_active=True)

        self.assertTrue(wait_for_bodies(self.sender, 1))

        attributes = attributes_of(self.records()[0])

        self.assertEqual(attributes[_payload('data')], '{"status')
        self.assertIs(attributes[DataCtx.Payload_Truncated], True)

# ################################################################################################################################
# ################################################################################################################################

class TestUpdatedRows(_HookTestCase):

    def test_scheduler_completion_hands_the_row_off_again(self) -> 'None':

        event_id = record_job_start(self.audit_log, 'nightly.cleanup',
            cid='cid-job-1', job_id=12, current_run=3, planned_fire_time_iso='2026-03-01T02:00:00+00:00',
            delay_ms=15, service='demo.cleanup')

        self.assertIsNotNone(event_id)

        if event_id:
            self.assertTrue(wait_for_bodies(self.sender, 1))

            record_job_complete(event_id, outcome=SCHEDULER.OUTCOME.OK, duration_ms=250, error='')

            self.assertTrue(wait_for_bodies(self.sender, 2))

            records = self.records()
            running = attributes_of(records[0])
            finished = attributes_of(records[1])

            # The same event twice, running first and finished second ..
            self.assertEqual(running[MappingCtx.Event_ID], event_id)
            self.assertEqual(finished[MappingCtx.Event_ID], event_id)

            self.assertEqual(running[_column('outcome')], SCHEDULER.OUTCOME.RUNNING)
            self.assertEqual(finished[_column('outcome')], SCHEDULER.OUTCOME.OK)
            self.assertEqual(finished[_column('duration_ms')], 250)

            # .. with the attrs read back as numbers ..
            self.assertEqual(finished[_attr('job_id')], 12)
            self.assertEqual(finished[_attr('current_run')], 3)
            self.assertEqual(finished[_attr('delay_ms')], 15)

            # .. and the same time as the row.
            self.assertEqual(records[0].time_unix_nano, records[1].time_unix_nano)
            self.assertEqual(records[1].severity_text, 'INFO')

# ################################################################################################################################

    def test_scheduler_timeout_hands_the_row_off_again(self) -> 'None':

        event_id = record_job_start(self.audit_log, 'nightly.cleanup',
            cid='cid-job-2', job_id=21, current_run=7, planned_fire_time_iso='2026-03-01T02:00:00+00:00',
            delay_ms=0, service='demo.cleanup')

        self.assertIsNotNone(event_id)
        self.assertTrue(wait_for_bodies(self.sender, 1))

        record_job_timeout(21, 7, elapsed_ms=60000, error='Timed out')

        self.assertTrue(wait_for_bodies(self.sender, 2))

        records = self.records()
        timed_out = attributes_of(records[1])

        self.assertEqual(timed_out[MappingCtx.Event_ID], event_id)
        self.assertEqual(timed_out[_column('outcome')], SCHEDULER.OUTCOME.TIMEOUT)
        self.assertEqual(timed_out[_column('duration_ms')], 60000)
        self.assertEqual(records[1].severity_text, 'ERROR')

        # The scheduler's data is an error message, not a document, and it does not leave
        self.assertNotIn('Timed out', str(timed_out))

# ################################################################################################################################

    def test_file_transfer_update_hands_the_row_off_again(self) -> 'None':

        event_id = record_file_transfer(self.audit_log, 'reports.sftp', 'upload', '/outgoing/report.csv',
            cid='cid-file-1', outcome=AuditOutcome.Running, size=4096)

        self.assertIsNotNone(event_id)
        self.assertTrue(wait_for_bodies(self.sender, 1))

        update_run_event(event_id, outcome=AuditOutcome.Error, status='permission-denied', duration_ms=900,
            data={'operation': 'upload', 'error': 'Permission denied'})

        self.assertTrue(wait_for_bodies(self.sender, 2))

        records = self.records()
        started = attributes_of(records[0])
        failed = attributes_of(records[1])

        self.assertEqual(started[MappingCtx.Event_ID], event_id)
        self.assertEqual(failed[MappingCtx.Event_ID], event_id)

        self.assertEqual(started[_column('outcome')], AuditOutcome.Running)
        self.assertEqual(failed[_column('outcome')], AuditOutcome.Error)
        self.assertEqual(failed[_column('status')], 'permission-denied')
        self.assertEqual(failed[_column('duration_ms')], 900)

        # The updated summary leaves in full, as the first one did
        self.assertEqual(started[_data('remote_path')], '/outgoing/report.csv')
        self.assertEqual(failed[_data('error')], 'Permission denied')
        self.assertEqual(failed[_data('operation')], 'upload')

        self.assertEqual(records[1].severity_text, 'ERROR')

# ################################################################################################################################

    def test_updates_of_an_unselected_source_are_not_handed_off(self) -> 'None':

        self.export.queue.flush_and_stop(1.0)
        self.export = self.build_export(batch_size=1, flush_interval_ms=20, sources={AuditSource.MCP})

        event_id = record_job_start(self.audit_log, 'nightly.cleanup',
            cid='cid-job-3', job_id=31, current_run=1, planned_fire_time_iso='2026-03-01T02:00:00+00:00',
            delay_ms=0, service='demo.cleanup')

        if event_id:
            record_job_complete(event_id, outcome=SCHEDULER.OUTCOME.OK, duration_ms=1, error='')

        self.assertFalse(wait_for_bodies_briefly(self.sender))
        self.assertEqual(self.export.queue.get_stats()['emitted'], 0)

# ################################################################################################################################

    def test_update_of_a_row_that_was_never_written(self) -> 'None':

        update_run_event(987654, outcome=AuditOutcome.Error)

        self.assertFalse(wait_for_bodies_briefly(self.sender))
        self.assertEqual(self.export.queue.get_stats()['emitted'], 0)

# ################################################################################################################################
# ################################################################################################################################

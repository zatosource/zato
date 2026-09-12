# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from json import dumps

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors.common import Probe_Source_Test_Transfer
from zato.common.alerting.collectors.evidence import collect_baseline, collect_deliveries, collect_failed_events, \
    collect_measure_rows, collect_quarantined, collect_test_transfers, collect_troubled_runs, collect_verify_failed, \
    measure_to_evidence
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.file_transfer_run import Run_Status_Clean, Run_Status_Failed, Run_Status_Interrupted, \
    Run_Status_List_Failed
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

_server_name = 'test-evidence-server'

# The connections and schedules the tests write events about
_conn_name = 'partner.acme.sftp'
_other_conn_name = 'partner.other.sftp'
_schedule_name = 'acme.invoices.in'
_other_schedule_name = 'other.invoices.in'

_window_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _backdate(event_id:'int', event_time:'datetime') -> 'None':
    engine = get_audit_engine()

    statement = update(event_table).where(event_table.c.id == event_id).values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _fact(object_name:'str'=_conn_name, source:'str'=AuditSource.File_Outgoing, window_seconds:'int'=_window_seconds) -> 'dict':
    out = {
        'source': source,
        'object_name': object_name,
        'window_seconds': window_seconds,
    }
    return out

# ################################################################################################################################

def _seed_transfer(audit_log:'AuditLog', cid:'str', outcome:'str', *, object_name:'str'=_conn_name, data:'str'='',
    endpoint:'str'='') -> 'int':

    out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, object_name, cid=cid, outcome=outcome,
        data=data, endpoint=endpoint)

    return out

# ################################################################################################################################

def _seed_run(audit_log:'AuditLog', cid:'str', schedule:'str', outcome:'str', status:'str') -> 'int':

    run_data = dumps({'schedule': schedule, 'failed': 1})

    out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Run_Completed, _conn_name, cid=cid, outcome=outcome,
        status=status, data=run_data)

    return out

# ################################################################################################################################

def _seed_delivery(audit_log:'AuditLog', cid:'str', schedule:'str') -> 'int':

    out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Delivered, _conn_name, cid=cid, outcome=AuditOutcome.OK,
        attrs={'schedule': schedule}, endpoint=f'/incoming/{cid}.xml')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFailedEvents:

    def test_only_the_failed_events_of_the_object_within_the_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'ok-1', AuditOutcome.OK)
        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Permission denied', endpoint='/outbox/INV-1.xml')
        _ = _seed_transfer(audit_log, 'err-other', AuditOutcome.Error, object_name=_other_conn_name, data='Other')

        old_id = _seed_transfer(audit_log, 'err-old', AuditOutcome.Error, data='Too old')
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        _ = _seed_transfer(audit_log, 'err-2', AuditOutcome.Error, data='Connection reset', endpoint='/outbox/INV-2.xml')

        rows = collect_failed_events(engine, _fact(), now)

        assert len(rows) == 2
        assert rows[0]['data'] == 'Connection reset'
        assert rows[0]['endpoint'] == '/outbox/INV-2.xml'
        assert rows[1]['data'] == 'Permission denied'

    def test_a_row_carries_the_columns_the_document_reads(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Permission denied')

        row = collect_failed_events(engine, _fact(), now)[0]

        assert set(row) == {'id', 'event_time_iso', 'event_type', 'endpoint', 'outcome', 'status', 'duration_ms', 'data',
            'ext_client_id'}
        assert row['outcome'] == AuditOutcome.Error
        assert row['event_type'] == AuditEvent.Message_Sent

    def test_a_fact_without_a_window_uses_the_default_one(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Now')

        old_id = _seed_transfer(audit_log, 'err-old', AuditOutcome.Error, data='Weeks ago')
        _backdate(old_id, now - timedelta(days=30))

        rows = collect_failed_events(engine, _fact(window_seconds=0), now)

        assert len(rows) == 1
        assert rows[0]['data'] == 'Now'

# ################################################################################################################################
# ################################################################################################################################

class TestTroubledRuns:

    def test_only_the_schedules_own_troubled_runs(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_run(audit_log, 'run-clean', _schedule_name, AuditOutcome.OK, Run_Status_Clean)
        _ = _seed_run(audit_log, 'run-failed', _schedule_name, AuditOutcome.Error, Run_Status_Failed)
        _ = _seed_run(audit_log, 'run-interrupted', _schedule_name, AuditOutcome.OK, Run_Status_Interrupted)
        _ = _seed_run(audit_log, 'run-list-failed', _schedule_name, AuditOutcome.OK, Run_Status_List_Failed)
        _ = _seed_run(audit_log, 'run-other', _other_schedule_name, AuditOutcome.Error, Run_Status_Failed)

        old_id = _seed_run(audit_log, 'run-old', _schedule_name, AuditOutcome.Error, Run_Status_Failed)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        rows = collect_troubled_runs(engine, _fact(_schedule_name), now)

        statuses = []

        for row in rows:
            statuses.append(row['status'])

        assert statuses == [Run_Status_List_Failed, Run_Status_Interrupted, Run_Status_Failed]

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveries:

    def test_only_the_schedules_deliveries_joined_on_the_attr(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_delivery(audit_log, 'del-1', _schedule_name)
        _ = _seed_delivery(audit_log, 'del-other', _other_schedule_name)
        _ = _seed_delivery(audit_log, 'del-2', _schedule_name)

        old_id = _seed_delivery(audit_log, 'del-old', _schedule_name)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        rows = collect_deliveries(engine, _fact(_schedule_name), now)

        endpoints = []

        for row in rows:
            endpoints.append(row['endpoint'])

        assert endpoints == ['/incoming/del-2.xml', '/incoming/del-1.xml']

# ################################################################################################################################
# ################################################################################################################################

class TestProbesAndFileEvents:

    def test_test_transfers_read_the_probe_rows_of_the_connection(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(Probe_Source_Test_Transfer, AuditEvent.Run_Completed, _conn_name, cid='probe-1',
            outcome=AuditOutcome.Error, data='Permission denied')
        _ = audit_log.insert(Probe_Source_Test_Transfer, AuditEvent.Run_Completed, _other_conn_name, cid='probe-other',
            outcome=AuditOutcome.Error, data='Other')
        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Not a probe')

        rows = collect_test_transfers(engine, _fact(), now)

        assert len(rows) == 1
        assert rows[0]['data'] == 'Permission denied'

    def test_quarantined_and_verify_failed_read_their_own_event_types(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.File_Quarantined, _conn_name, cid='q-1',
            outcome=AuditOutcome.Error, endpoint='/in/bad.xml', data='Retries exhausted')
        _ = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Verify_Failed, _conn_name, cid='v-1',
            outcome=AuditOutcome.Error, endpoint='/in/short.xml', data='Size mismatch')
        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Neither')

        quarantined = collect_quarantined(engine, _fact(), now)
        verify_failed = collect_verify_failed(engine, _fact(), now)

        assert len(quarantined) == 1
        assert quarantined[0]['endpoint'] == '/in/bad.xml'

        assert len(verify_failed) == 1
        assert verify_failed[0]['endpoint'] == '/in/short.xml'

# ################################################################################################################################
# ################################################################################################################################

class TestMeasureRows:

    def test_each_measure_is_mapped_to_its_query(self) -> 'None':

        assert measure_to_evidence['error_count'] is collect_failed_events
        assert measure_to_evidence['runs_failed_in_window'] is collect_troubled_runs
        assert measure_to_evidence['arrival_overdue_ratio'] is collect_deliveries
        assert measure_to_evidence['test_transfer_failed'] is collect_test_transfers
        assert measure_to_evidence['quarantined_count'] is collect_quarantined
        assert measure_to_evidence['verify_failed_count'] is collect_verify_failed

    def test_the_rows_of_all_measures_come_together_once_each_newest_first(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        first_id = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='One')
        _ = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.File_Quarantined, _conn_name, cid='q-1',
            outcome=AuditOutcome.Error, data='Quarantined')
        last_id = _seed_transfer(audit_log, 'err-2', AuditOutcome.Error, data='Two')

        rows = collect_measure_rows(engine, _fact(), ['error_count', 'error_rate', 'quarantined_count'], now)

        ids = []

        for row in rows:
            ids.append(row['id'])

        assert len(rows) == 3
        assert ids[0] == last_id
        assert ids[-1] == first_id

    def test_an_unmapped_measure_reads_the_failed_events(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='One')

        rows = collect_measure_rows(engine, _fact(), ['outstanding'], now)

        assert len(rows) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestBaseline:

    def test_the_successes_the_streak_and_the_last_ok_before_it(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'ok-1', AuditOutcome.OK, endpoint='/out/1.xml')
        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Reset')
        _ = _seed_transfer(audit_log, 'ok-2', AuditOutcome.OK, endpoint='/out/2.xml')
        _ = _seed_transfer(audit_log, 'err-2', AuditOutcome.Error, data='Denied')
        _ = _seed_transfer(audit_log, 'err-3', AuditOutcome.Error, data='Denied')

        baseline = collect_baseline(engine, _fact(), now)

        assert baseline['ok_count'] == 2
        assert baseline['last_ok']['endpoint'] == '/out/2.xml'
        assert baseline['streak_count'] == 2
        assert baseline['streak_start_iso'] != ''
        assert baseline['last_ok_before_streak']['endpoint'] == '/out/2.xml'
        assert baseline['test_transfers_on'] is False
        assert baseline['test_transfer'] is None

    def test_a_success_as_the_newest_event_means_no_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Reset')
        _ = _seed_transfer(audit_log, 'ok-1', AuditOutcome.OK)

        baseline = collect_baseline(engine, _fact(), now)

        assert baseline['streak_count'] == 0
        assert baseline['last_ok_before_streak'] is None

    def test_a_streak_with_no_success_before_it(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'err-1', AuditOutcome.Error, data='Reset')

        baseline = collect_baseline(engine, _fact(), now)

        assert baseline['ok_count'] == 0
        assert baseline['last_ok'] is None
        assert baseline['streak_count'] == 1
        assert baseline['last_ok_before_streak'] is None

    def test_a_schedule_reads_its_baseline_under_the_owning_connection(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_transfer(audit_log, 'ok-1', AuditOutcome.OK)

        baseline = collect_baseline(engine, _fact(_schedule_name), now, baseline_object_name=_conn_name)

        assert baseline['ok_count'] == 1

    def test_the_newest_test_transfer_when_they_are_on(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(Probe_Source_Test_Transfer, AuditEvent.Run_Completed, _conn_name, cid='probe-1',
            outcome=AuditOutcome.OK)
        _ = audit_log.insert(Probe_Source_Test_Transfer, AuditEvent.Run_Completed, _conn_name, cid='probe-2',
            outcome=AuditOutcome.Error, data='Permission denied')

        baseline = collect_baseline(engine, _fact(), now, test_transfers_on=True)

        assert baseline['test_transfers_on'] is True
        assert baseline['test_transfer']['outcome'] == AuditOutcome.Error
        assert baseline['test_transfer']['data'] == 'Permission denied'

    def test_test_transfers_on_without_a_result_yet(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        baseline = collect_baseline(engine, _fact(), now, test_transfers_on=True)

        assert baseline['test_transfers_on'] is True
        assert baseline['test_transfer'] is None

# ################################################################################################################################
# ################################################################################################################################

def _seed_channel_call(audit_log:'AuditLog', cid:'str', status:'str', *, caller:'str'='partner-a') -> 'int':
    """ The request and the response one call of a REST channel leaves behind - the request always arrives fine,
    the response carries the status and the outcome.
    """
    if status.startswith('2'):
        outcome = AuditOutcome.OK
        data = ''
    else:
        outcome = AuditOutcome.Error
        data = 'Rejected'

    _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name, cid=cid, outcome=AuditOutcome.OK,
        ext_client_id=caller)

    out = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _channel_name, cid=cid, outcome=outcome,
        status=status, data=data, ext_client_id=caller, endpoint='orders.get')

    return out

# ################################################################################################################################

# The REST channel the channel baseline tests seed calls for
_channel_name = 'orders.api'

# ################################################################################################################################
# ################################################################################################################################

class TestChannelBaseline:

    def test_a_channels_baseline_counts_its_responses_not_its_requests(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_channel_call(audit_log, 'call-1', '200 OK')
        _ = _seed_channel_call(audit_log, 'call-2', '200 OK')
        _ = _seed_channel_call(audit_log, 'call-3', '401 Unauthorized', caller='partner-b')
        _ = _seed_channel_call(audit_log, 'call-4', '401 Unauthorized', caller='partner-b')

        baseline = collect_baseline(engine, _fact(_channel_name, AuditSource.REST_Channel), now)

        # Two calls went through - the OK request halves of the rejected calls count for nothing
        assert baseline['ok_count'] == 2
        assert baseline['last_ok']['endpoint'] == 'orders.get'

        # The two rejections are the streak, unbroken by the requests that arrived between them
        assert baseline['streak_count'] == 2
        assert baseline['last_ok_before_streak']['endpoint'] == 'orders.get'

    def test_a_channel_whose_newest_call_went_through_has_no_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_channel_call(audit_log, 'call-1', '500 Internal Server Error')
        _ = _seed_channel_call(audit_log, 'call-2', '200 OK')

        baseline = collect_baseline(engine, _fact(_channel_name, AuditSource.REST_Channel), now)

        assert baseline['ok_count'] == 1
        assert baseline['streak_count'] == 0
        assert baseline['last_ok_before_streak'] is None

    def test_a_channels_failed_rows_carry_their_callers(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_channel_call(audit_log, 'call-1', '401 Unauthorized', caller='partner-b')

        rows = collect_failed_events(engine, _fact(_channel_name, AuditSource.REST_Channel), now)

        assert len(rows) == 1
        assert rows[0]['status'] == '401 Unauthorized'
        assert rows[0]['ext_client_id'] == 'partner-b'
        assert rows[0]['endpoint'] == 'orders.get'

# ################################################################################################################################
# ################################################################################################################################

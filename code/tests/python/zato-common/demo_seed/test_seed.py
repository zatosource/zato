# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.alerting.model import AlertState
from zato.common.audit_log.api import event_link_table, event_table, get_audit_engine, AuditEvent, AuditLink, AuditLog, \
    AuditOutcome, AuditSource
from zato.common.audit_log.common import alert_table, event_dedup_table
from zato.common.demo.seed import get_demo_rule_defs, purge_demo_data, seed_demo_data, Actor_Admin, Actor_Operator, \
    Burst_End_Hour, Burst_Start_Hour, Channel_Clinic, Channel_Lab, Channel_Main, Clinic_Silent_Hour, Outconn_FHIR, \
    Outconn_Forward, SeedConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The server name all the seeded events are written under
_server_name = 'test-demo-seed-server'

# A fixed moment the assertions hinge on - a midday, so the day's curve has hours behind it
_now = datetime(2026, 7, 15, 12, 30, 0)

# ################################################################################################################################
# ################################################################################################################################

def _small_config() -> 'SeedConfig':
    """ A run small enough to keep the tests quick while every scenario still appears.
    """
    out = SeedConfig()
    out.messages_per_day = 30
    out.burst_message_count = 15
    out.fhir_pair_count = 5

    return out

# ################################################################################################################################

def _run_seed() -> 'any_':
    audit_log = AuditLog(_server_name, flush_max_size=1)
    engine = get_audit_engine()

    out = seed_demo_data(audit_log, engine, now=_now, config=_small_config())
    return out

# ################################################################################################################################

def _get_events(**where:'any_') -> 'anylist':
    engine = get_audit_engine()

    statement = select(event_table)

    for name, value in where.items():
        statement = statement.where(event_table.c[name] == value)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    out = [row._asdict() for row in rows]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSeedContents:

    def test_a_run_writes_the_full_data_set(self) -> 'None':
        """ One run produces the traffic, the alerts, the dedup entries,
        the config history and the FHIR pairs, all at once.
        """
        result = _run_seed()

        # Every message writes at least its receipt and its acknowledgment
        assert result.message_count == 7 * 30 + 15
        assert result.event_count > result.message_count * 2

        # The three lifecycle states and the three rules
        assert result.alert_count == 3
        assert result.rule_names == [rule_def['name'] for rule_def in get_demo_rule_defs()]

        # The ledger holds the reprocess claim, a completed resend and an in-doubt one
        assert result.dedup_count == 3

        # Five creations, one edit and one view record
        assert result.config_event_count == 7

        assert result.fhir_pair_count == 5
        assert result.channel_names == [Channel_Main, Channel_Lab, Channel_Clinic]

# ################################################################################################################################

    def test_the_traffic_spans_the_whole_week(self) -> 'None':
        """ The received events cover every day of the span, none of them
        dated into the future.
        """
        _ = _run_seed()

        events = _get_events(event_type=AuditEvent.Message_Received, source=AuditSource.HL7)

        days = set()

        for event in events:
            when = datetime.fromisoformat(event['event_time_iso'])
            assert when <= _now
            days.add(when.date())

        assert len(days) == 7

# ################################################################################################################################

    def test_the_lab_burst_is_visible(self) -> 'None':
        """ The previous day's burst window holds far more lab failures
        than the rest of the week combined.
        """
        _ = _run_seed()

        burst_day = _now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        burst_start = burst_day + timedelta(hours=Burst_Start_Hour)
        burst_end = burst_day + timedelta(hours=Burst_End_Hour)

        events = _get_events(
            event_type=AuditEvent.Ack_Sent, object_name=Channel_Lab, outcome=AuditOutcome.Error)

        inside = 0
        outside = 0

        for event in events:
            when = datetime.fromisoformat(event['event_time_iso'])

            if burst_start <= when < burst_end:
                inside += 1
            else:
                outside += 1

        assert inside > outside

# ################################################################################################################################

    def test_the_clinic_went_silent(self) -> 'None':
        """ The clinic channel has traffic before the cutoff and nothing after it.
        """
        _ = _run_seed()

        cutoff = _now.replace(hour=Clinic_Silent_Hour, minute=0, second=0, microsecond=0)

        events = _get_events(event_type=AuditEvent.Message_Received, object_name=Channel_Clinic)
        assert events

        for event in events:
            when = datetime.fromisoformat(event['event_time_iso'])
            assert when <= cutoff

# ################################################################################################################################

    def test_the_forwarded_pairs_exist(self) -> 'None':
        """ Forwarded messages have their sent and acknowledgment events
        on the outgoing connection, sharing the receipt's cid. The in-flight
        sends are their own story and stand apart from the pairs.
        """
        _ = _run_seed()

        sent_events = _get_events(event_type=AuditEvent.Message_Sent, object_name=Outconn_Forward)
        forwarded_events = [event for event in sent_events if not event['cid'].startswith('demo-if-')]
        assert forwarded_events

        received_cids = {event['cid'] for event in _get_events(event_type=AuditEvent.Message_Received)}

        for event in forwarded_events:
            assert event['cid'] in received_cids

# ################################################################################################################################

    def test_the_in_flight_sends_are_outstanding(self) -> 'None':
        """ A few recent sends have no acknowledgment yet - the outstanding
        filter's demo cases.
        """
        _ = _run_seed()

        sent_events = _get_events(event_type=AuditEvent.Message_Sent, object_name=Outconn_Forward)
        acked_cids = {event['cid'] for event in _get_events(event_type=AuditEvent.Ack_Received)}

        outstanding = [event for event in sent_events if event['cid'] not in acked_cids]

        assert len(outstanding) == 3

# ################################################################################################################################

    def test_the_batch_has_its_lineage(self) -> 'None':
        """ The batch writes a parent row and children linked to it.
        """
        _ = _run_seed()

        parent_events = _get_events(event_type=AuditEvent.Interchange_Received)
        assert len(parent_events) == 1

        parent_id = parent_events[0]['id']

        engine = get_audit_engine()

        statement = select(event_link_table).where(event_link_table.c.parent_event_id == parent_id)
        statement = statement.where(event_link_table.c.link_type == AuditLink.Batch_Item_Of)

        with engine.connect() as connection:
            rows = connection.execute(statement).fetchall()

        assert len(rows) == 3

# ################################################################################################################################

    def test_the_repair_story_is_linked(self) -> 'None':
        """ The reprocessed message points back at the failed original
        through its correlation id and a resubmit link.
        """
        _ = _run_seed()

        repair_events = _get_events(cid='demo-rp-00000001', event_type=AuditEvent.Message_Received)
        assert len(repair_events) == 1

        repair = repair_events[0]
        assert repair['correl_id'].startswith('demo-')

        engine = get_audit_engine()

        statement = select(event_link_table).where(event_link_table.c.child_event_id == repair['id'])
        statement = statement.where(event_link_table.c.link_type == AuditLink.Resubmit_Of)

        with engine.connect() as connection:
            rows = connection.execute(statement).fetchall()

        assert len(rows) == 1

# ################################################################################################################################

    def test_the_alerts_cover_all_three_states(self) -> 'None':
        """ One alert is unobserved, one observed and one resolved,
        each with the expected people on it.
        """
        _ = _run_seed()

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(select(alert_table)).fetchall()

        alerts = {row._asdict()['state']: row._asdict() for row in rows}

        assert len(alerts) == 3

        assert alerts[AlertState.Unobserved]['object_name'] == Channel_Clinic
        assert alerts[AlertState.Unobserved]['count'] > 1

        assert alerts[AlertState.Observed]['object_name'] == Channel_Lab
        assert alerts[AlertState.Observed]['observed_by'] == Actor_Admin
        assert alerts[AlertState.Observed]['count'] == 3

        assert alerts[AlertState.Resolved]['object_name'] == Outconn_Forward
        assert alerts[AlertState.Resolved]['resolved_by'] == Actor_Operator

# ################################################################################################################################

    def test_the_dedup_ledger_has_an_in_doubt_entry(self) -> 'None':
        """ The ledger holds completed claims and one still in doubt.
        """
        _ = _run_seed()

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(select(event_dedup_table)).fetchall()

        entries = [row._asdict() for row in rows]
        in_doubt = [entry for entry in entries if not entry['completed_iso']]

        assert len(entries) == 3
        assert len(in_doubt) == 1

# ################################################################################################################################

    def test_the_config_history_is_present(self) -> 'None':
        """ The config events tell the story - creations, one edit
        and one view-access record.
        """
        _ = _run_seed()

        created = _get_events(source=AuditSource.Config, event_type=AuditEvent.Config_Created)
        edited = _get_events(source=AuditSource.Config, event_type=AuditEvent.Config_Edited)
        viewed = _get_events(source=AuditSource.Config, event_type=AuditEvent.Content_Viewed)

        assert len(created) == 5
        assert len(edited) == 1
        assert len(viewed) == 1

        assert edited[0]['object_name'] == Channel_Lab

# ################################################################################################################################

    def test_the_fhir_pairs_are_present(self) -> 'None':
        """ Every FHIR request has its response on the same cid.
        """
        _ = _run_seed()

        requests = _get_events(source=AuditSource.FHIR, event_type=AuditEvent.Request_Sent)
        responses = _get_events(source=AuditSource.FHIR, event_type=AuditEvent.Response_Received)

        assert len(requests) == 5
        assert len(responses) == 5

        request_cids = {event['cid'] for event in requests}
        response_cids = {event['cid'] for event in responses}

        assert request_cids == response_cids

        for event in requests:
            assert event['object_name'] == Outconn_FHIR

# ################################################################################################################################
# ################################################################################################################################

class TestSeedBehaviour:

    def test_a_rerun_replaces_the_previous_data_set(self) -> 'None':
        """ Importing twice leaves one data set, not two stacked ones.
        """
        first = _run_seed()
        second = _run_seed()

        assert first.event_count == second.event_count
        assert first.alert_count == second.alert_count
        assert first.dedup_count == second.dedup_count

# ################################################################################################################################

    def test_the_same_seed_is_reproducible(self) -> 'None':
        """ Two runs with one seed produce the same events at the same moments.
        """
        _ = _run_seed()
        first_events = [(event['cid'], event['event_time_iso']) for event in _get_events(source=AuditSource.HL7)]

        _ = _run_seed()
        second_events = [(event['cid'], event['event_time_iso']) for event in _get_events(source=AuditSource.HL7)]

        assert sorted(first_events) == sorted(second_events)

# ################################################################################################################################

    def test_the_purge_removes_everything(self) -> 'None':
        """ The purge leaves no demo rows behind in any of the tables.
        """
        _ = _run_seed()

        engine = get_audit_engine()
        purge_demo_data(engine)

        with engine.connect() as connection:
            events = connection.execute(select(event_table)).fetchall()
            alerts = connection.execute(select(alert_table)).fetchall()
            dedups = connection.execute(select(event_dedup_table)).fetchall()

        assert events == []
        assert alerts == []
        assert dedups == []

# ################################################################################################################################
# ################################################################################################################################

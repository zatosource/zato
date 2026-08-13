# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from json import loads
from time import monotonic

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, AuditBody, AuditEvent, AuditLink, AuditOutcome, AuditSource
from zato.common.audit_log.common import alert_table, event_dedup_table
from zato.common.audit_log.reports import Range_Week
from zato.common.audit_log.usage import get_usage
from zato.common.demo.seed import get_demo_rule_defs, purge_demo_data, seed_demo_data, \
    Actors, Burst_End_Hour, Burst_Start_Hour, Channel_Clinic, Channel_Lab, Channel_Main, Clinic_Silent_Hour, \
    Facilities_By_Channel, FHIR_Error_Status, FHIR_Save_Method, In_Flight_Count, Outconn_FHIR, Outconn_Forward, \
    Routes_By_Channel, SeedConfig
from zato.common.hl7.feed import MSH3_Index, MSH4_Index

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

# How long one default-size run may take end to end - a week of 1200 messages
# per day is about 8,500 messages and their events. The writes land in one bulk
# transaction, so nearly all of this budget covers content generation, with ample
# headroom for slow CI machines
_max_seed_seconds = 15.0

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
    engine = get_audit_engine()

    out = seed_demo_data(engine, server_name=_server_name, now=_now, config=_small_config())
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

def _get_request_bodies(object_name:'str') -> 'anylist':
    """ The stored message bodies of everything one channel received.
    """
    engine = get_audit_engine()

    events = _get_events(event_type=AuditEvent.Message_Received, object_name=object_name)
    event_ids = [event['id'] for event in events]

    statement = select(event_body_table.c.data).where(event_body_table.c.event_id.in_(event_ids))
    statement = statement.where(event_body_table.c.kind == AuditBody.Request)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    out = [row[0] for row in rows]
    return out

# ################################################################################################################################

def _get_msh_fields(message_text:'str') -> 'anylist':
    """ The pipe-split MSH segment of one message, index 0 being the segment name.
    """
    msh_line = message_text.partition('\r')[0]

    out = msh_line.split('|')
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

        # The ledger holds one reprocess claim per resubmit chain,
        # a completed resend and an in-doubt one
        assert result.resubmit_count > 0
        assert result.dedup_count == result.resubmit_count + 2

        # Five creations, one edit and the view-access records
        assert result.view_count > 0
        assert result.config_event_count == 6 + result.view_count

        assert result.fhir_pair_count == 5
        assert result.channel_names == [Channel_Main, Channel_Lab, Channel_Clinic]

# ################################################################################################################################

    def test_the_traffic_spans_the_whole_week(self) -> 'None':
        """ The received events cover every day of the span, none of them
        dated into the future.
        """
        _ = _run_seed()

        events = _get_events(event_type=AuditEvent.Message_Received, source=AuditSource.MLLP_Channel)

        days = set()

        for event in events:
            when = datetime.fromisoformat(event['event_time_iso'])
            assert when <= _now
            days.add(when.date())

        assert len(days) == 7

# ################################################################################################################################

    def test_no_event_lands_on_a_whole_second(self) -> 'None':
        """ Every event carries the fraction of a second it happened on - a data set
        whose moments all sit on a whole second reads as made up.
        """
        _ = _run_seed()

        for event in _get_events():
            when = datetime.fromisoformat(event['event_time_iso'])
            assert when.microsecond, event['event_time_iso']

# ################################################################################################################################

    def test_no_body_carries_a_made_up_msh7(self) -> 'None':
        """ No stored message body carries a fixed whole-second MSH-7 -
        every acknowledgment and batch header holds its own moment.
        """
        _ = _run_seed()

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(select(event_body_table.c.data)).fetchall()

        for row in rows:
            assert '20260101000000' not in row[0]

# ################################################################################################################################

    def test_every_channel_names_its_own_senders(self) -> 'None':
        """ A seeded body says where it came from - its channel's own route in MSH-3
        and one of the facilities that channel hears from in MSH-4, with each
        acknowledgment filed under that same facility.
        """
        _ = _run_seed()

        for channel_name, facilities in Facilities_By_Channel.items():

            route = Routes_By_Channel[channel_name]

            bodies = _get_request_bodies(channel_name)
            assert bodies

            for body in bodies:
                msh_fields = _get_msh_fields(body)

                assert msh_fields[MSH3_Index] == route, body
                assert msh_fields[MSH4_Index] in facilities, body

            ack_events = _get_events(event_type=AuditEvent.Ack_Sent, object_name=channel_name)
            assert ack_events

            for event in ack_events:
                assert event['ext_client_id'] in facilities

# ################################################################################################################################

    def test_the_usage_report_names_the_clinics(self) -> 'None':
        """ The callers the channel-usage page shows for the clinic channel are
        the facilities that channel hears from, each with calls of its own.
        """
        _ = _run_seed()

        rows = get_usage(_now, Range_Week, [AuditSource.MLLP_Channel], [Channel_Clinic])

        callers = set()

        for row in rows:
            assert row.calls > 0
            callers.add(row.caller)

        assert callers == set(Facilities_By_Channel[Channel_Clinic])

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

        assert len(outstanding) == In_Flight_Count

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

    def test_the_resubmit_chains_are_linked(self) -> 'None':
        """ Every reprocessed message points back at its parent through
        its correlation id and a resubmit link, and says who asked for it.
        """
        result = _run_seed()

        received = _get_events(event_type=AuditEvent.Message_Received, source=AuditSource.MLLP_Channel)
        chain_events = [event for event in received if event['cid'].startswith('demo-rp')]

        # Every chain has its first hop, and every few chains a second one
        assert len(chain_events) >= result.resubmit_count

        engine = get_audit_engine()

        for event in chain_events:

            assert event['correl_id'].startswith('demo-')

            # The resubmit link to the parent
            statement = select(event_link_table).where(event_link_table.c.child_event_id == event['id'])
            statement = statement.where(event_link_table.c.link_type == AuditLink.Resubmit_Of)

            with engine.connect() as connection:
                rows = connection.execute(statement).fetchall()

            assert len(rows) == 1

            # Who asked for the resubmit rides on the receipt
            statement = select(event_attr_table).where(event_attr_table.c.event_id == event['id'])
            statement = statement.where(event_attr_table.c.name == 'actor')

            with engine.connect() as connection:
                attr_rows = [row._asdict() for row in connection.execute(statement)]

            assert len(attr_rows) == 1
            assert attr_rows[0]['value'] in Actors

# ################################################################################################################################

    def test_the_alerts_cover_all_three_shapes(self) -> 'None':
        """ One alert repeats since the morning, one folded yesterday's burst
        and one was a single occurrence - each with its dedup count.
        """
        _ = _run_seed()

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(select(alert_table)).fetchall()

        alerts = {row._asdict()['object_name']: row._asdict() for row in rows}

        assert len(alerts) == 3

        assert alerts[Channel_Clinic]['count'] > 1
        assert alerts[Channel_Lab]['count'] == 3
        assert alerts[Outconn_Forward]['count'] == 1

# ################################################################################################################################

    def test_the_dedup_ledger_has_an_in_doubt_entry(self) -> 'None':
        """ The ledger holds one completed claim per resubmit chain, each with
        its actor, a completed resend and one claim still in doubt.
        """
        result = _run_seed()

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(select(event_dedup_table)).fetchall()

        entries = [row._asdict() for row in rows]
        in_doubt = [entry for entry in entries if not entry['completed_iso']]
        reprocessed = [entry for entry in entries if entry['action'] == 'reprocess']

        assert len(entries) == result.resubmit_count + 2
        assert len(in_doubt) == 1
        assert len(reprocessed) == result.resubmit_count

        for entry in reprocessed:
            assert entry['actor'] in Actors

# ################################################################################################################################

    def test_the_config_history_is_present(self) -> 'None':
        """ The config events tell the story - creations, one edit
        and the view-access records.
        """
        result = _run_seed()

        created = _get_events(source=AuditSource.Config, event_type=AuditEvent.Config_Created)
        edited = _get_events(source=AuditSource.Config, event_type=AuditEvent.Config_Edited)
        viewed = _get_events(source=AuditSource.Config, event_type=AuditEvent.Content_Viewed)

        assert len(created) == 5
        assert len(edited) == 1
        assert len(viewed) == result.view_count

        assert edited[0]['object_name'] == Channel_Lab

# ################################################################################################################################

    def test_the_fhir_pairs_are_present(self) -> 'None':
        """ Every FHIR request has its response on the same cid, some of them refused,
        and a save carries the resource it wrote.
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

        # The connection has failures of its own, and each one says what the server refused with
        failed = [event for event in responses if event['outcome'] == AuditOutcome.Error]
        assert failed

        for event in failed:
            assert event['status'] == FHIR_Error_Status

        # A save is the pair that stored a body - what the browser shows and a resend repeats
        saves = [loads(event['data']) for event in requests if loads(event['data'])['payload']]
        assert saves

        for stored in saves:
            assert stored['method'] == FHIR_Save_Method
            assert stored['path'].endswith(loads(stored['payload'])['id'])

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
        first_events = [(event['cid'], event['event_time_iso']) for event in _get_events(source=AuditSource.MLLP_Channel)]

        _ = _run_seed()
        second_events = [(event['cid'], event['event_time_iso']) for event in _get_events(source=AuditSource.MLLP_Channel)]

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

    def test_a_full_size_run_is_fast(self) -> 'None':
        """ The default-size run - a whole week of traffic - lands in the database
        in one bulk transaction, so the import stays fast enough to sit behind
        a button in the UI.
        """
        engine = get_audit_engine()

        start = monotonic()
        result = seed_demo_data(engine, server_name=_server_name, now=_now)
        elapsed = monotonic() - start

        # The run really was the full-size one
        assert result.event_count > result.message_count * 2

        assert elapsed < _max_seed_seconds, f'Seed took {elapsed:.2f}s, expected under {_max_seed_seconds}s'

# ################################################################################################################################
# ################################################################################################################################

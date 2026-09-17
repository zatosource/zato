# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MLLP channel collectors - the negative acknowledgments a channel sent land in its fault counts by their
# code, a positive ack counts nothing, the error rate and the latency read the acks alone rather than the
# messages received alongside them, and the silence of an MLLP channel is read off its newest message received.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import collect_ack_code_facts, collect_channel_silence_facts, \
    collect_consecutive_failure_facts, collect_error_rate_facts, collect_facts, collect_latency_facts, Measure_Ack_Codes, \
    Window_Seconds_By_Measure_Key
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.hl7.audit import audit_ack_sent, audit_message_received
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import stranydict
    datetime = datetime
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The channels the tests seed messages for
_channel_name = 'adt.intake'
_other_channel_name = 'orm.intake'

# The sending facility of the messages
_facility = 'GENERAL_HOSPITAL'

# The window the measures cover in these tests, in seconds
_window_seconds = 3600

# The message and the ack the rows carry as their bodies
_message_text = 'MSH|^~\\&|ADT|GENERAL_HOSPITAL|ZATO|ZATO|20260914||ADT^A01|MSG-1|P|2.5\rPID|||123'
_ack_text = 'MSH|^~\\&|ZATO|ZATO|ADT|GENERAL_HOSPITAL|20260914||ACK^A01|ACK-1|P|2.5\rMSA|{code}|MSG-1'

# ################################################################################################################################
# ################################################################################################################################

def _backdate(event_id:'int', event_time:'datetime') -> 'None':
    """ Moves one stored event back in time.
    """
    engine = get_audit_engine()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _seed_message(
    audit_log:'AuditLog',
    cid:'str',
    ack_code:'str',
    *,
    object_name:'str' = _channel_name,
    duration_ms:'int' = 20,
    ) -> 'int':
    """ Stores the two events one message of an MLLP channel leaves behind - the message as it arrived and the
    acknowledgment as it left, the ack carrying the code and the outcome. Returns the id of the ack row.
    """
    attrs = {'msg_type': 'ADT^A01', 'mrn': '123', 'facility': _facility, 'ack_status': ''}

    _ = audit_message_received(audit_log, object_name, _message_text, cid=cid, msg_id=cid, attrs=attrs)

    out = audit_ack_sent(audit_log, object_name, ack_code, _ack_text.format(code=ack_code), cid=cid, msg_id=cid,
        facility=_facility, duration_ms=duration_ms)

    return out

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str') -> 'stranydict':
    """ The one fact of an MLLP channel among the facts collected.
    """
    for fact in facts:
        if fact['source'] == AuditSource.MLLP_Channel:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestAckCodes:

    def test_the_negative_acks_land_in_the_fault_counts_by_their_code(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ack-1', 'AR')
        _ = _seed_message(audit_log, 'ack-2', 'AR')
        _ = _seed_message(audit_log, 'ack-3', 'AR')
        _ = _seed_message(audit_log, 'ack-4', 'AE')

        fact = _fact_of(collect_ack_code_facts(engine, _window_seconds, now), _channel_name)

        assert fact['fault_counts'] == {'AR': 3, 'AE': 1}
        assert fact['window_seconds'] == _window_seconds

    def test_a_positive_ack_counts_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ok-1', 'AA')
        _ = _seed_message(audit_log, 'ok-2', 'CA')

        assert collect_ack_code_facts(engine, _window_seconds, now) == []

    def test_each_channel_gets_its_own_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'one-1', 'AR')
        _ = _seed_message(audit_log, 'two-1', 'CE', object_name=_other_channel_name)
        _ = _seed_message(audit_log, 'two-2', 'CE', object_name=_other_channel_name)

        facts = collect_ack_code_facts(engine, _window_seconds, now)

        assert _fact_of(facts, _channel_name)['fault_counts'] == {'AR': 1}
        assert _fact_of(facts, _other_channel_name)['fault_counts'] == {'CE': 2}

    def test_a_channel_asked_for_by_name_is_measured_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'one-1', 'AR')
        _ = _seed_message(audit_log, 'two-1', 'CE', object_name=_other_channel_name)

        facts = collect_ack_code_facts(engine, _window_seconds, now, source=AuditSource.MLLP_Channel,
            object_name=_other_channel_name)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _other_channel_name

    def test_another_source_measures_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'one-1', 'AR')

        assert collect_ack_code_facts(engine, _window_seconds, now, source=AuditSource.REST_Channel) == []

    def test_acks_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_message(audit_log, 'old-1', 'AR')
        _ = _seed_message(audit_log, 'new-1', 'AE')

        _backdate(old_id, now - timedelta(seconds=_window_seconds * 2))

        fact = _fact_of(collect_ack_code_facts(engine, _window_seconds, now), _channel_name)

        assert fact['fault_counts'] == {'AE': 1}

# ################################################################################################################################
# ################################################################################################################################

class TestAcksAlone:

    def test_the_error_rate_reads_the_acks_and_not_the_messages_received(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two messages acknowledged negatively out of four - the four OK message-received rows must not dilute it
        _ = _seed_message(audit_log, 'rate-1', 'AA')
        _ = _seed_message(audit_log, 'rate-2', 'AR')
        _ = _seed_message(audit_log, 'rate-3', 'AE')
        _ = _seed_message(audit_log, 'rate-4', 'AA')

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _channel_name)

        assert fact['total_count'] == 4
        assert fact['error_count'] == 2
        assert fact['error_rate'] == 0.5

    def test_the_failures_in_a_row_are_not_broken_by_the_messages_received(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'row-1', 'AA')
        _ = _seed_message(audit_log, 'row-2', 'AR')
        _ = _seed_message(audit_log, 'row-3', 'AR')
        _ = _seed_message(audit_log, 'row-4', 'AE')

        fact = _fact_of(collect_consecutive_failure_facts(engine, now), _channel_name)

        assert fact['consecutive_failures'] == 3

    def test_the_latency_is_the_acks_duration(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'lat-1', 'AA', duration_ms=100)
        _ = _seed_message(audit_log, 'lat-2', 'AA', duration_ms=300)

        fact = _fact_of(collect_latency_facts(engine, _window_seconds, now), _channel_name)

        assert fact['avg_duration_ms'] == 200

# ################################################################################################################################
# ################################################################################################################################

class TestSilence:

    def test_an_mllp_channels_silence_is_read_off_its_newest_message_received(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        ack_id = _seed_message(audit_log, 'sil-1', 'AA')

        # The message came in a quarter of an hour ago, its ack right after it
        _backdate(ack_id - 1, now - timedelta(seconds=900))
        _backdate(ack_id, now - timedelta(seconds=899))

        facts = collect_channel_silence_facts(engine, now, {_channel_name})

        assert len(facts) == 1
        assert facts[0]['source'] == AuditSource.MLLP_Channel
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['silent_seconds'] == 900

    def test_a_channel_not_expecting_traffic_is_not_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'sil-1', 'AA')

        assert collect_channel_silence_facts(engine, now, {_other_channel_name}) == []

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFacts:

    def test_an_mllp_channel_fact_carries_every_measure_at_once(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'all-1', 'AA', duration_ms=100)
        _ = _seed_message(audit_log, 'all-2', 'AR', duration_ms=300)
        _ = _seed_message(audit_log, 'all-3', 'AR', duration_ms=200)

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            silence_expected_names={_channel_name})

        fact = _fact_of(facts, _channel_name)

        assert fact['total_count'] == 3
        assert fact['error_count'] == 2
        assert fact['consecutive_failures'] == 2
        assert fact['avg_duration_ms'] == 200
        assert fact['fault_counts'] == {'AR': 2}
        assert fact['silent_seconds'] == 0
        assert fact[Window_Seconds_By_Measure_Key][Measure_Ack_Codes] == _window_seconds

        # Nothing HTTP is measured about an MLLP channel
        assert fact['auth_failure_count'] == 0
        assert fact['client_error_count'] == 0
        assert fact['server_error_count'] == 0
        assert fact['status_counts'] == {}

    def test_the_acks_window_of_the_source_applies_to_the_ack_codes_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_message(audit_log, 'win-1', 'AR')
        _ = _seed_message(audit_log, 'win-2', 'AE')

        # The older reject is half an hour old - outside a ten-minute acks window, inside the hour of everything else
        _backdate(old_id - 1, now - timedelta(seconds=1800))
        _backdate(old_id, now - timedelta(seconds=1800))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            window_seconds_by_source={AuditSource.MLLP_Channel: {Measure_Ack_Codes: 600}})

        fact = _fact_of(facts, _channel_name)

        assert fact['fault_counts'] == {'AE': 1}
        assert fact['error_count'] == 2
        assert fact[Window_Seconds_By_Measure_Key][Measure_Ack_Codes] == 600

    def test_the_newest_failure_pointed_at_is_the_ack_itself(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ev-0', 'AA')
        ack_id = _seed_message(audit_log, 'ev-1', 'AR')

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds)
        fact = _fact_of(facts, _channel_name)

        # The ack row carries the negative outcome, the message-received row before it is always OK
        assert fact['last_error_event_id'] == ack_id
        assert fact['error_count'] == 1

# ################################################################################################################################
# ################################################################################################################################

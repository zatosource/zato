# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing MLLP collectors - the negative acknowledgments a connection was answered land in its fault counts by
# their code, a positive ack counts nothing, a message no acknowledgment came back for lands in the connection failures
# and not in the fault counts, and the error rate and the latency read the acks alone rather than the messages sent
# alongside them or the deliveries a channel made through the connection.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import collect_ack_code_facts, collect_consecutive_failure_facts, \
    collect_error_rate_facts, collect_facts, collect_latency_facts, collect_mllp_connection_failure_facts, \
    Measure_Ack_Codes, Measure_Connection_Failures, Window_Seconds_By_Measure_Key
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.destination.audit import record_hop
from zato.common.destination.constants import DestinationType
from zato.common.destination.model import new_entry
from zato.common.hl7.audit import audit_ack_received, audit_message_sent, ACKStatus
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import intnone, stranydict
    datetime = datetime
    intnone = intnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The connections the tests seed messages for
_conn_name = 'lab.results'
_other_conn_name = 'adt.outbound'

# The remote systems the connections send to
_address = 'lab.example.com:2575'

# The window the measures cover in these tests, in seconds
_window_seconds = 3600

# The message the sent rows carry as their body
_message_text = 'MSH|^~\\&|ZATO|ZATO|LAB|LAB_SYSTEM|20260914||ORU^R01|MSG-1|P|2.5\rPID|||123'

# What a remote system says when it rejects a message
_reject_text = 'Unknown patient'

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
    object_name:'str' = _conn_name,
    duration_ms:'int' = 20,
    ) -> 'int':
    """ Stores the two events one message of an outgoing MLLP connection leaves behind - the message as it left and
    the acknowledgment as it arrived, or the timeout marker when none did. Returns the id of the ack row.
    """
    attrs = {'msg_type': 'ORU^R01', 'mrn': '123', 'facility': 'ZATO'}

    _ = audit_message_sent(audit_log, object_name, _message_text, cid=cid, msg_id=cid, attrs=attrs, endpoint=_address)

    if ack_code == ACKStatus.Timeout:
        error_text = ''
    elif ack_code in (ACKStatus.Application_Accept, ACKStatus.Commit_Accept):
        error_text = ''
    else:
        error_text = _reject_text

    out = audit_ack_received(audit_log, object_name, ack_code, cid=cid, msg_id=cid, duration_ms=duration_ms,
        error_text=error_text)

    return out

# ################################################################################################################################

def _seed_delivery(audit_log:'AuditLog', cid:'str', *, error:'str' = '') -> 'intnone':
    """ Stores the delivery a channel made through the connection as one of its destinations - a request-sent
    row under the connection's name that no measure of the connection is to read.
    """
    entry = new_entry('lab', DestinationType.MLLP, _conn_name)

    out = record_hop(audit_log, 'adt.intake', entry, _message_text, cid=cid, sequence=1, attempt=1, duration_ms=5,
        error=error)

    return out

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str') -> 'stranydict':
    """ The one fact of an outgoing MLLP connection among the facts collected.
    """
    for fact in facts:
        if fact['source'] == AuditSource.MLLP_Outgoing:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestAckCodes:

    def test_the_negative_acks_answered_land_in_the_fault_counts_by_their_code(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ack-1', 'AR')
        _ = _seed_message(audit_log, 'ack-2', 'AR')
        _ = _seed_message(audit_log, 'ack-3', 'AR')
        _ = _seed_message(audit_log, 'ack-4', 'AE')

        fact = _fact_of(collect_ack_code_facts(engine, _window_seconds, now), _conn_name)

        assert fact['source'] == AuditSource.MLLP_Outgoing
        assert fact['fault_counts'] == {'AR': 3, 'AE': 1}
        assert fact['window_seconds'] == _window_seconds

    def test_a_positive_ack_counts_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ok-1', 'AA')
        _ = _seed_message(audit_log, 'ok-2', 'CA')

        assert collect_ack_code_facts(engine, _window_seconds, now) == []

    def test_a_timeout_is_not_a_negative_ack(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'to-1', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'to-2', ACKStatus.Timeout)

        assert collect_ack_code_facts(engine, _window_seconds, now) == []

    def test_each_connection_gets_its_own_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'one-1', 'AR')
        _ = _seed_message(audit_log, 'two-1', 'CE', object_name=_other_conn_name)
        _ = _seed_message(audit_log, 'two-2', 'CE', object_name=_other_conn_name)

        facts = collect_ack_code_facts(engine, _window_seconds, now)

        assert _fact_of(facts, _conn_name)['fault_counts'] == {'AR': 1}
        assert _fact_of(facts, _other_conn_name)['fault_counts'] == {'CE': 2}

    def test_the_outgoing_source_asked_for_is_measured_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'one-1', 'AR')

        assert collect_ack_code_facts(engine, _window_seconds, now, source=AuditSource.MLLP_Channel) == []

        facts = collect_ack_code_facts(engine, _window_seconds, now, source=AuditSource.MLLP_Outgoing, object_name=_conn_name)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _conn_name

    def test_acks_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_message(audit_log, 'old-1', 'AR')
        _ = _seed_message(audit_log, 'new-1', 'AE')

        _backdate(old_id, now - timedelta(seconds=_window_seconds * 2))

        fact = _fact_of(collect_ack_code_facts(engine, _window_seconds, now), _conn_name)

        assert fact['fault_counts'] == {'AE': 1}

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionFailures:

    def test_the_timeouts_land_in_the_connection_failures(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'to-1', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'to-2', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'ok-1', 'AA')

        fact = _fact_of(collect_mllp_connection_failure_facts(engine, _window_seconds, now), _conn_name)

        assert fact['connection_failure_count'] == 2
        assert fact['fault_counts'] == {}
        assert fact['window_seconds'] == _window_seconds

    def test_a_negative_ack_is_not_a_connection_failure(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ack-1', 'AR')
        _ = _seed_message(audit_log, 'ack-2', 'AE')

        assert collect_mllp_connection_failure_facts(engine, _window_seconds, now) == []

    def test_another_source_measures_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'to-1', ACKStatus.Timeout)

        assert collect_mllp_connection_failure_facts(engine, _window_seconds, now, source=AuditSource.FHIR) == []

    def test_timeouts_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_message(audit_log, 'old-1', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'new-1', ACKStatus.Timeout)

        _backdate(old_id, now - timedelta(seconds=_window_seconds * 2))

        fact = _fact_of(collect_mllp_connection_failure_facts(engine, _window_seconds, now), _conn_name)

        assert fact['connection_failure_count'] == 1

# ################################################################################################################################
# ################################################################################################################################

class TestAcksAlone:

    def test_the_error_rate_reads_the_acks_and_not_the_messages_sent(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two messages failed out of four - the four OK message-sent rows must not dilute it
        _ = _seed_message(audit_log, 'rate-1', 'AA')
        _ = _seed_message(audit_log, 'rate-2', 'AR')
        _ = _seed_message(audit_log, 'rate-3', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'rate-4', 'AA')

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _conn_name)

        assert fact['total_count'] == 4
        assert fact['error_count'] == 2
        assert fact['error_rate'] == 0.5

    def test_the_deliveries_a_channel_made_through_the_connection_are_left_out(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'rate-1', 'AA')
        _ = _seed_message(audit_log, 'rate-2', 'AR')

        # Three failed deliveries under the connection's name - request-sent rows the ack measures never read
        _ = _seed_delivery(audit_log, 'hop-1', error='Connection refused')
        _ = _seed_delivery(audit_log, 'hop-2', error='Connection refused')
        _ = _seed_delivery(audit_log, 'hop-3', error='Connection refused')

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _conn_name)

        assert fact['total_count'] == 2
        assert fact['error_count'] == 1

        assert collect_mllp_connection_failure_facts(engine, _window_seconds, now) == []

    def test_the_failures_in_a_row_are_not_broken_by_the_messages_sent(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'row-1', 'AA')
        _ = _seed_message(audit_log, 'row-2', 'AR')
        _ = _seed_message(audit_log, 'row-3', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'row-4', 'AE')

        fact = _fact_of(collect_consecutive_failure_facts(engine, now), _conn_name)

        assert fact['consecutive_failures'] == 3

    def test_the_latency_is_the_acks_duration(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'lat-1', 'AA', duration_ms=100)
        _ = _seed_message(audit_log, 'lat-2', 'AA', duration_ms=300)

        fact = _fact_of(collect_latency_facts(engine, _window_seconds, now), _conn_name)

        assert fact['avg_duration_ms'] == 200

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFacts:

    def test_an_outgoing_mllp_fact_carries_every_measure_at_once(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'all-1', 'AA', duration_ms=100)
        _ = _seed_message(audit_log, 'all-2', 'AR', duration_ms=300)
        _ = _seed_message(audit_log, 'all-3', ACKStatus.Timeout, duration_ms=200)

        facts = collect_facts(engine, {}, AuditSource.MLLP_Outgoing, now, window_seconds=_window_seconds)

        fact = _fact_of(facts, _conn_name)

        assert fact['total_count'] == 3
        assert fact['error_count'] == 2
        assert fact['consecutive_failures'] == 2
        assert fact['avg_duration_ms'] == 200
        assert fact['fault_counts'] == {'AR': 1}
        assert fact['connection_failure_count'] == 1
        assert fact[Window_Seconds_By_Measure_Key][Measure_Ack_Codes] == _window_seconds
        assert fact[Window_Seconds_By_Measure_Key][Measure_Connection_Failures] == _window_seconds

        # Nothing HTTP and nothing of a channel is measured about an outgoing connection
        assert fact['status_counts'] == {}
        assert fact['auth_failure_count'] == 0
        assert fact['silent_seconds'] == 0

    def test_the_windows_of_the_source_apply_to_their_own_measures_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_ack_id = _seed_message(audit_log, 'win-1', 'AR')
        old_timeout_id = _seed_message(audit_log, 'win-2', ACKStatus.Timeout)
        _ = _seed_message(audit_log, 'win-3', 'AE')
        _ = _seed_message(audit_log, 'win-4', ACKStatus.Timeout)

        # The older reject and timeout are half an hour old - outside ten-minute windows of their own,
        # inside the hour of everything else
        for event_id in (old_ack_id, old_timeout_id):
            _backdate(event_id - 1, now - timedelta(seconds=1800))
            _backdate(event_id, now - timedelta(seconds=1800))

        windows = {Measure_Ack_Codes: 600, Measure_Connection_Failures: 600}
        facts = collect_facts(engine, {}, AuditSource.MLLP_Outgoing, now, window_seconds=_window_seconds,
            window_seconds_by_source={AuditSource.MLLP_Outgoing: windows})

        fact = _fact_of(facts, _conn_name)

        assert fact['fault_counts'] == {'AE': 1}
        assert fact['connection_failure_count'] == 1
        assert fact['error_count'] == 4
        assert fact[Window_Seconds_By_Measure_Key][Measure_Ack_Codes] == 600
        assert fact[Window_Seconds_By_Measure_Key][Measure_Connection_Failures] == 600

    def test_the_newest_failure_points_at_the_message_its_ack_answered(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_message(audit_log, 'ev-0', 'AA')
        ack_id = _seed_message(audit_log, 'ev-1', ACKStatus.Timeout)

        facts = collect_facts(engine, {}, AuditSource.MLLP_Outgoing, now, window_seconds=_window_seconds)
        fact = _fact_of(facts, _conn_name)

        # The ack row carries the failed outcome but nothing goes out again from it - the message
        # it never answered is what the operator sends once more, so the link lands one row earlier,
        # and it is the newest message of this cid rather than any message the cid names.
        assert fact['last_error_event_id'] == ack_id - 1
        assert fact['is_resubmittable'] == 1
        assert fact['error_count'] == 1

# ################################################################################################################################
# ################################################################################################################################

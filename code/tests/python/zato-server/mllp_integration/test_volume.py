# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import time
from time import monotonic

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine, func, select

# Zato
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome
from zato.common.hl7.feed import run_feed, FeedConfig, FeedItem
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# Zato - test helpers
from conftest import wait_for_port_open

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The volume proof is opt-in - it runs for minutes under sustained load,
# so it only starts when the environment asks for it, like test-as2-live does.
_is_volume_enabled = bool(os.environ.get('Zato_Test_HL7_Volume'))

# Per-message trace diagnostics - opt-in through the environment
_is_trace_enabled = bool(os.environ.get('Zato_HL7_Trace'))

# How hard and how long to push, overridable from the environment -
# the defaults prove the property in minutes, a full-hour run is one variable away.
_rate_per_minute  = int(os.environ.get('Zato_Test_HL7_Volume_Rate', '3000'))
_duration_seconds = int(os.environ.get('Zato_Test_HL7_Volume_Duration', '120'))
_error_ratio      = float(os.environ.get('Zato_Test_HL7_Volume_Error_Ratio', '0.02'))

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 10.0
_recv_buffer_size = 4096
_max_message_size = 2_000_000

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'

# How long to wait for the buffered writer to flush its tail after the run
_flush_wait_seconds = 15.0

# Latency in the last third of the run may not exceed this multiple of the first third -
# the flat-insert-latency assertion, with margin for measurement noise on small medians.
_latency_growth_factor = 3.0

# Small medians drown in scheduler noise - growth below this absolute margin is flat
_latency_noise_margin_ms = 5.0

# The audit database may not take up more than this many bytes per event row -
# the bounded-growth assertion, covering the row, its attributes and its body.
_max_bytes_per_event = 4096

# ################################################################################################################################
# ################################################################################################################################

class _PersistentMLLPSender:
    """ Sends framed messages over one long-lived TCP connection and reads each ACK -
    how a real ADT feed talks to a channel, without per-message connection cost.
    """

    def __init__(self, host:'str', port:'int') -> 'None':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(_socket_timeout)
        self.socket.connect((host, port))
        self.decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

    def send(self, item:'FeedItem') -> 'bytes':
        """ Sends one feed item and returns the raw ACK bytes.
        """
        # Trace diagnostics - each send is announced before the socket write so a stall
        # is attributable to the exact control id that never came back.
        send_start = monotonic()

        if _is_trace_enabled:
            print(f'[CLIENT] sending {item.control_id}', flush=True)

        framed_message = frame_encode(item.text.encode('utf-8'), _start_sequence, _end_sequence)
        self.socket.sendall(framed_message)

        while True:
            chunk = self.socket.recv(_recv_buffer_size)

            if not chunk:
                raise Exception('Connection closed before receiving a complete ACK')

            self.decoder.feed(chunk)
            message = self.decoder.next_message()

            if message is not None:
                if _is_trace_enabled:
                    round_trip_ms = (monotonic() - send_start) * 1000
                    print(f'[CLIENT] ack for {item.control_id} after {round_trip_ms:.1f}ms', flush=True)
                out = message
                return out

    def close(self) -> 'None':
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

def _ensure_schema(audit_db_path:'str') -> 'None':
    """ Creates the audit schema if it is not there yet - in a standalone volume run
    the baseline is read before the server ever wrote an event, and creating
    from the same metadata is exactly what the server itself would do.
    """
    engine = create_engine(f'sqlite:///{audit_db_path}')
    event_table.metadata.create_all(engine)
    engine.dispose()

# ################################################################################################################################

def _median(values:'anylist') -> 'float':
    """ Returns the median of a list of numbers.
    """
    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2:
        out = ordered[middle]
    else:
        out = (ordered[middle - 1] + ordered[middle]) / 2

    return out

# ################################################################################################################################

def _count_events(audit_db_path:'str', event_type:'str', outcome:'str'='') -> 'int':
    """ Returns how many events of one type the audit database holds.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(func.count()).select_from(event_table)
    query = query.where(event_table.c.event_type == event_type)

    if outcome:
        query = query.where(event_table.c.outcome == outcome)

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    engine.dispose()
    return out

# ################################################################################################################################

def _count_all_events(audit_db_path:'str') -> 'int':
    """ Returns how many event rows the audit database holds in total.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(func.count()).select_from(event_table)

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    engine.dispose()
    return out

# ################################################################################################################################

def _get_db_size(audit_db_path:'str') -> 'int':
    """ Returns the on-disk size of the audit database - the main file plus
    the write-ahead log, because under WAL mode recent writes live there
    until a checkpoint moves them over.
    """

    out = os.path.getsize(audit_db_path)

    wal_path = audit_db_path + '-wal'

    if os.path.exists(wal_path):
        out += os.path.getsize(wal_path)

    return out

# ################################################################################################################################

def _wait_for_event_count(audit_db_path:'str', event_type:'str', expected_count:'int') -> 'int':
    """ Polls until the expected number of events landed - the buffered writer
    flushes on max-wait, so the tail of the run arrives shortly after it ends.
    """

    deadline = time.monotonic() + _flush_wait_seconds

    while time.monotonic() < deadline:

        out = _count_events(audit_db_path, event_type)

        if out >= expected_count:
            return out

        time.sleep(0.5)

    out = _count_events(audit_db_path, event_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skipif(not _is_volume_enabled, reason='Volume tests run only when Zato_Test_HL7_Volume is set')
class TestHL7Volume:
    """ The volume proof - a sustained feed of thousands of messages a minute with
    an injected error mix, asserting flat insert latency and bounded audit-DB growth.
    The demonstrated answer to the database-bloat complaint: the audit trail keeps up
    and its storage stays proportional to what actually happened.
    """

    accept_channel_id:'int' = 0
    error_channel_id:'int' = 0

# ################################################################################################################################

    def test_01_create_channels(self, zato_client:'object', mllp_port:'int') -> 'None':
        """ Creates the audited channels the feed runs against - the default route
        accepts, and the feed's injected failures route to a service that raises.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-hl7-volume-accept',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            is_default=True,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.accept_channel_id = response['id']

        # The feed marks its injected failures with this MSH-3 value
        config = FeedConfig()

        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-hl7-volume-error',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.error',
            msh3_sending_app=config.error_sending_application,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.error_channel_id = response['id']

        wait_for_port_open(mllp_port)

# ################################################################################################################################

    def test_02_sustained_load(self, zato_server:'dict', mllp_port:'int') -> 'None':
        """ Runs the sample feed at the configured rate for the configured duration,
        then reads the proof out of the latency measurements and the audit database.
        """
        audit_db_path = zato_server['audit_db_path']

        # How many messages the configured rate and duration amount to
        count = int(_rate_per_minute * _duration_seconds / 60)

        # The schema must exist before the baseline can be read
        _ensure_schema(audit_db_path)

        # The baseline the growth assertions measure against - the audit tests
        # that ran earlier in this session left their own rows behind.
        events_before = _count_all_events(audit_db_path)
        received_before = _count_events(audit_db_path, AuditEvent.Message_Received)
        acks_before = _count_events(audit_db_path, AuditEvent.Ack_Sent)
        error_acks_before = _count_events(audit_db_path, AuditEvent.Ack_Sent, AuditOutcome.Error)

        db_size_before = _get_db_size(audit_db_path)

        config = FeedConfig()
        config.rate_per_minute = _rate_per_minute
        config.error_ratio = _error_ratio

        sender = _PersistentMLLPSender('127.0.0.1', mllp_port)

        try:
            result = run_feed(sender.send, count, config)
        finally:
            sender.close()

        assert result.sent_count == count

        # Flat insert latency: the run's last third may not be meaningfully slower
        # than its first third - sustained load must not degrade the write path.
        third = count // 3

        first_third_median = _median(result.durations_ms[:third])
        last_third_median = _median(result.durations_ms[-third:])

        allowed = max(first_third_median * _latency_growth_factor, first_third_median + _latency_noise_margin_ms)
        assert last_third_median <= allowed, (first_third_median, last_third_median)

        # Every message wrote its receipt and its acknowledgment - the buffered
        # writer is given time to flush the tail of the run first.
        received_count = _wait_for_event_count(audit_db_path, AuditEvent.Message_Received, received_before + count)
        assert received_count == received_before + count, (received_before, received_count)

        acks_count = _wait_for_event_count(audit_db_path, AuditEvent.Ack_Sent, acks_before + count)
        assert acks_count == acks_before + count, (acks_before, acks_count)

        # The injected failures are all visible as negative acknowledgments
        error_acks_count = _count_events(audit_db_path, AuditEvent.Ack_Sent, AuditOutcome.Error)
        assert error_acks_count == error_acks_before + result.error_injected_count, \
            (error_acks_before, error_acks_count, result.error_injected_count)

        # Bounded growth: the database grew proportionally to the events written,
        # with each event's row, attributes and body staying under the cap.
        events_after = _count_all_events(audit_db_path)
        db_size_after = _get_db_size(audit_db_path)

        events_written = events_after - events_before
        bytes_written = db_size_after - db_size_before

        bytes_per_event = bytes_written / events_written
        assert bytes_per_event <= _max_bytes_per_event, (bytes_written, events_written, bytes_per_event)

# ################################################################################################################################

    def test_03_cleanup(self, zato_client:'object') -> 'None':
        """ Deletes the channels this module created.
        """

        for channel_id in (self.__class__.error_channel_id, self.__class__.accept_channel_id):
            if channel_id:
                zato_client.delete(f'{_generic_service_name}.delete', id=channel_id) # type: ignore[union-attr]

# ################################################################################################################################
# ################################################################################################################################

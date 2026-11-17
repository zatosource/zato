# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import random
import socket
import threading
import time
from statistics import median, quantiles

# pytest
import pytest

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.test.perf_report import report_result, start_measurement

# Zato - test helpers
from conftest import wait_for_port_open
from mllp_live_util import sample_adt_a01

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, stranydict

    AdminClient = AdminClient

# ################################################################################################################################
# ################################################################################################################################

# The volume measurements are opt-in - they run for minutes under sustained load,
# so they only start when the environment asks for it.
_is_volume_enabled = bool(os.environ.get('Zato_Test_HL7_Volume'))

# How hard and how long the sustained feed pushes, overridable from the environment -
# the defaults prove the property in minutes, a full-hour run is one variable away.
_rate_per_minute  = int(os.environ.get('Zato_Test_HL7_Volume_Rate', '3000'))
_duration_seconds = int(os.environ.get('Zato_Test_HL7_Volume_Duration', '120'))
_error_ratio      = float(os.environ.get('Zato_Test_HL7_Volume_Error_Ratio', '0.02'))

# The seed that makes the injected failures of a feed reproducible
_feed_seed = 12345

# The MSH-3 sending application of the sample messages, and the one that marks a message as an injected failure,
# which the error channel routes to a service that raises
_sending_application       = b'|SendApp|'
_error_sending_application = 'ERROR_FEED_SYSTEM'

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 30.0
_recv_buffer_size = 4096
_host             = '127.0.0.1'

# The positive acknowledgment code
_ack_accepted = 'AA'

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'
_audit_counts_service    = 'test.hl7.audit-counts'

# How long to wait for the buffered writer to flush its tail after the run, and how often to look
_flush_wait_seconds = 15.0
_flush_poll_seconds = 0.5

# Latency in the last third of the run may not exceed this multiple of the first third -
# the flat-insert-latency assertion, with margin for measurement noise on small medians.
_latency_growth_factor = 3.0

# Small medians drown in scheduler noise - growth below this absolute margin is flat
_latency_noise_margin_ms = 5.0

# The audit database may not take up more than this many bytes per event row -
# the bounded-growth assertion, covering the row, its attributes and its body.
_max_bytes_per_event = 4096

# How many messages each measurement of the throughput of the channel sends
_sequential_message_count       = 1_000
_concurrent_thread_count        = 10
_concurrent_messages_per_thread = 100
_persistent_message_count       = 2_000
_size_message_count             = 50

# The sizes of the messages of the measurement of large messages, in bytes, and the OBX segment that pads them
_message_sizes = (1_000, 10_000, 100_000, 1_000_000)
_padding_prefix = b'\rOBX|1|TX|PAD^Padding||'

# How many cut points the percentiles are read from, and the cut point of each percentile
_quantile_count = 100
_p50_index = 49
_p95_index = 94
_p99_index = 98

_milliseconds_per_second = 1000.0
_seconds_per_minute      = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _new_message(control_id:'str', is_error:'bool') -> 'bytes':
    """ Returns a sample ADT^A01 message under the given control ID, marked as an injected failure if requested.
    """
    out = sample_adt_a01(control_id)

    if is_error:
        error_application = f'|{_error_sending_application}|'.encode()
        out = out.replace(_sending_application, error_application, 1)

    return out

# ################################################################################################################################

def _new_padded_message(control_id:'str', size:'int') -> 'bytes':
    """ Returns a sample message padded with an OBX segment to the given size in bytes.
    """
    message = sample_adt_a01(control_id)
    padding_size = size - len(message) - len(_padding_prefix)

    out = message + _padding_prefix + (b'X' * padding_size)
    return out

# ################################################################################################################################

def _get_latency_figures(durations:'list[float]') -> 'stranydict':
    """ Returns the count and the percentiles of durations given in seconds, in milliseconds.
    """
    cut_points = quantiles(durations, n=_quantile_count, method='inclusive')

    out:'stranydict' = {
        'count': len(durations),
        'p50_ms': cut_points[_p50_index] * _milliseconds_per_second,
        'p95_ms': cut_points[_p95_index] * _milliseconds_per_second,
        'p99_ms': cut_points[_p99_index] * _milliseconds_per_second,
        'max_ms': max(durations) * _milliseconds_per_second,
    }

    return out

# ################################################################################################################################

def _get_rate_figures(count:'int', seconds:'float') -> 'stranydict':
    """ Returns how many messages were sent, in how many seconds, and how many per second.
    """
    out:'stranydict' = {
        'count': count,
        'seconds': seconds,
        'per_second': count / seconds,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class _PersistentSender:
    """ Sends framed messages over one long-lived TCP connection and reads each acknowledgment,
    which is how a real ADT feed sends to a channel.
    """

    def __init__(self, port:'int') -> 'None':
        self.socket = socket.create_connection((_host, port), timeout=_socket_timeout)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.buffer = b''

# ################################################################################################################################

    def send(self, message:'bytes') -> 'bytes':
        """ Sends one message and returns its acknowledgment without the framing.
        """
        self.socket.sendall(_start_sequence + message + _end_sequence)

        while _end_sequence not in self.buffer:
            chunk = self.socket.recv(_recv_buffer_size)

            if not chunk:
                raise Exception('Connection closed before receiving a complete acknowledgment')

            self.buffer += chunk

        frame, self.buffer = self.buffer.split(_end_sequence, 1)

        out = frame.removeprefix(_start_sequence)
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

def _new_client(port:'int') -> 'HL7MLLPClient':
    """ Returns a client that sends each message on a connection of its own.
    """
    out = HL7MLLPClient(_host, port, _start_sequence, _end_sequence, receive_timeout=_socket_timeout)
    return out

# ################################################################################################################################

def _send_accepted(client:'HL7MLLPClient', message:'bytes', control_id:'str') -> 'None':
    """ Sends one message on a connection of its own and fails unless the channel accepts it.
    """
    result = client.send(message, control_id)
    assert result.ack_code == _ack_accepted, (control_id, result.ack_code, result.error_text)

# ################################################################################################################################

def _get_audit_counts(zato_client:'AdminClient') -> 'anydict':
    """ Returns how many events of each kind the audit log holds and the size of the Zato database.
    """
    out = zato_client.invoke(_audit_counts_service)
    return out

# ################################################################################################################################

def _wait_for_audit_counts(zato_client:'AdminClient', received:'int', acks:'int') -> 'anydict':
    """ Polls until the audit log holds the expected number of received messages and acknowledgments - the buffered
    writer flushes on max-wait, so the tail of a run arrives shortly after it ends.
    """
    deadline = time.monotonic() + _flush_wait_seconds

    while True:
        out = _get_audit_counts(zato_client)

        if out['received'] >= received and out['acks'] >= acks:
            return out

        if time.monotonic() > deadline:
            return out

        time.sleep(_flush_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skipif(not _is_volume_enabled, reason='Volume tests run only when Zato_Test_HL7_Volume is set')
class TestHL7Volume:
    """ The volume measurements of a real server over its MLLP channel - a sustained feed with an injected error mix,
    asserting flat insert latency and bounded growth of the audit log, and the throughput of the channel
    for senders that connect per message, concurrently, with large messages and over one connection.
    Each records its figures with the settings of the measured server.
    """

    accept_channel_id:'int' = 0
    error_channel_id:'int' = 0

# ################################################################################################################################

    def test_01_create_channels(self, zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Creates the audited channels that the measurements send to - the default route accepts,
        and the injected failures route to a service that raises.
        """
        response = zato_client.create(
            f'{_generic_service_name}.create',
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

        response = zato_client.create(
            f'{_generic_service_name}.create',
            name='test-hl7-volume-error',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.error',
            msh3_sending_app=_error_sending_application,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.error_channel_id = response['id']

        wait_for_port_open(mllp_port)

# ################################################################################################################################

    def test_02_sustained_load(self, zato_server:'anydict', zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Runs a feed at the configured rate for the configured duration over one connection, then reads
        the proof out of the latencies and the audit log, and records the figures of the run.
        """
        measurement = start_measurement(zato_client, zato_server['database'])

        # How many messages the configured rate and duration amount to, and which of them are injected failures
        count = int(_rate_per_minute * _duration_seconds / _seconds_per_minute)
        feed_random = random.Random(_feed_seed)

        is_error_list:'list[bool]' = []

        for _ in range(count):
            is_error_list.append(feed_random.random() < _error_ratio)

        error_count = sum(is_error_list)

        # The baseline that the growth assertions measure against - the audit tests
        # that ran earlier in this session left their own rows behind.
        before = _get_audit_counts(zato_client)

        interval = _seconds_per_minute / _rate_per_minute
        durations:'list[float]' = []

        sender = _PersistentSender(mllp_port)

        try:
            run_start = time.monotonic()

            for index, is_error in enumerate(is_error_list):

                # The pacing is drift-free - each send is scheduled off the start of the run, not off the previous send.
                wait = run_start + (index * interval) - time.monotonic()

                if wait > 0:
                    time.sleep(wait)

                message = _new_message(f'FEED{index:08d}', is_error)

                send_start = time.monotonic()
                _ = sender.send(message)
                durations.append(time.monotonic() - send_start)

            run_seconds = time.monotonic() - run_start

        finally:
            sender.close()

        # Flat insert latency: the last third of the run may not be meaningfully slower
        # than its first third - sustained load must not degrade the write path.
        third = count // 3

        first_third_median = median(durations[:third]) * _milliseconds_per_second
        last_third_median = median(durations[-third:]) * _milliseconds_per_second

        allowed = max(first_third_median * _latency_growth_factor, first_third_median + _latency_noise_margin_ms)
        assert last_third_median <= allowed, (first_third_median, last_third_median)

        # Every message wrote its receipt and its acknowledgment ..
        after = _wait_for_audit_counts(zato_client, before['received'] + count, before['acks'] + count)

        assert after['received'] == before['received'] + count, (before, after)
        assert after['acks'] == before['acks'] + count, (before, after)

        # .. the injected failures are all visible as negative acknowledgments ..
        assert after['error_acks'] == before['error_acks'] + error_count, (before, after, error_count)

        # .. and the database grew proportionally to the events written, with each event's row,
        # .. attributes and body staying under the cap.
        events_written = after['events'] - before['events']
        bytes_written = after['database_size'] - before['database_size']

        bytes_per_event = bytes_written / events_written
        assert bytes_per_event <= _max_bytes_per_event, (bytes_written, events_written, bytes_per_event)

        _ = report_result(measurement, 'hl7-mllp-sustained-feed', {
            'messages': _get_rate_figures(count, run_seconds),
            'injected_failures': error_count,
            'round_trip': _get_latency_figures(durations),
            'first_third_median_ms': first_third_median,
            'last_third_median_ms': last_third_median,
            'audit_events_written': events_written,
            'database_bytes_per_event': bytes_per_event,
        })

# ################################################################################################################################

    def test_03_connection_per_message(self, zato_server:'anydict', zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Sends messages one after another, each on a connection of its own, which is the costliest thing
        that a sender can do, and records the throughput and the round trips.
        """
        measurement = start_measurement(zato_client, zato_server['database'])
        client = _new_client(mllp_port)

        durations:'list[float]' = []
        run_start = time.monotonic()

        for index in range(_sequential_message_count):
            control_id = f'SEQ{index:06d}'

            send_start = time.monotonic()
            _send_accepted(client, sample_adt_a01(control_id), control_id)
            durations.append(time.monotonic() - send_start)

        run_seconds = time.monotonic() - run_start

        _ = report_result(measurement, 'hl7-mllp-connection-per-message', {
            'messages': _get_rate_figures(_sequential_message_count, run_seconds),
            'round_trip': _get_latency_figures(durations),
        })

# ################################################################################################################################

    def test_04_concurrent_senders(self, zato_server:'anydict', zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Sends messages from several threads at once, each message on a connection of its own,
        and records the aggregate throughput.
        """
        measurement = start_measurement(zato_client, zato_server['database'])
        errors:'list[str]' = []

        def _send_all(thread_index:'int') -> 'None':
            client = _new_client(mllp_port)

            try:
                for message_index in range(_concurrent_messages_per_thread):
                    control_id = f'CON{thread_index:03d}{message_index:04d}'
                    _send_accepted(client, sample_adt_a01(control_id), control_id)
            except Exception as exception:
                errors.append(f'Thread {thread_index}: {exception}')

        threads:'list[threading.Thread]' = []

        for thread_index in range(_concurrent_thread_count):
            thread = threading.Thread(target=_send_all, args=(thread_index,))
            threads.append(thread)

        run_start = time.monotonic()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        run_seconds = time.monotonic() - run_start

        assert not errors, errors

        message_count = _concurrent_thread_count * _concurrent_messages_per_thread

        _ = report_result(measurement, 'hl7-mllp-concurrent-senders', {
            'threads': _concurrent_thread_count,
            'messages': _get_rate_figures(message_count, run_seconds),
        })

# ################################################################################################################################

    def test_05_message_sizes(self, zato_server:'anydict', zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Sends messages of rising sizes, each on a connection of its own, and records the bytes per second
        and the round trips of each size.
        """
        measurement = start_measurement(zato_client, zato_server['database'])
        client = _new_client(mllp_port)

        figures:'stranydict' = {}

        for size in _message_sizes:

            durations:'list[float]' = []
            run_start = time.monotonic()

            for index in range(_size_message_count):
                control_id = f'BIG{size:07d}{index:03d}'
                message = _new_padded_message(control_id, size)

                send_start = time.monotonic()
                _send_accepted(client, message, control_id)
                durations.append(time.monotonic() - send_start)

            run_seconds = time.monotonic() - run_start

            figures[f'bytes_{size}'] = {
                'bytes': _get_rate_figures(size * _size_message_count, run_seconds),
                'round_trip': _get_latency_figures(durations),
            }

        _ = report_result(measurement, 'hl7-mllp-message-sizes', figures)

# ################################################################################################################################

    def test_06_persistent_connection(self, zato_server:'anydict', zato_client:'AdminClient', mllp_port:'int') -> 'None':
        """ Sends messages one after another over one connection, as fast as the channel acknowledges them,
        and records the throughput and the round trips.
        """
        measurement = start_measurement(zato_client, zato_server['database'])
        sender = _PersistentSender(mllp_port)

        durations:'list[float]' = []

        try:
            run_start = time.monotonic()

            for index in range(_persistent_message_count):
                control_id = f'PERS{index:06d}'

                send_start = time.monotonic()
                ack = sender.send(sample_adt_a01(control_id))
                durations.append(time.monotonic() - send_start)

                assert f'MSA|{_ack_accepted}|{control_id}'.encode() in ack, ack

            run_seconds = time.monotonic() - run_start

        finally:
            sender.close()

        _ = report_result(measurement, 'hl7-mllp-persistent-connection', {
            'messages': _get_rate_figures(_persistent_message_count, run_seconds),
            'round_trip': _get_latency_figures(durations),
        })

# ################################################################################################################################

    def test_07_cleanup(self, zato_client:'AdminClient') -> 'None':
        """ Deletes the channels that this module created.
        """
        for channel_id in (self.__class__.error_channel_id, self.__class__.accept_channel_id):
            if channel_id:
                _ = zato_client.delete(f'{_generic_service_name}.delete', id=channel_id)

# ################################################################################################################################
# ################################################################################################################################

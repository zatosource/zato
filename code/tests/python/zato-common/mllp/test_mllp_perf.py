# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import threading
import time

# Zato
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

from conftest import sample_adt_a01, start_sequence, end_sequence, perf_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# Step 13 - Sequential throughput
_sequential_message_count           = 10_000
_sequential_throughput_threshold    = 500

# Step 14 - Concurrent throughput
_concurrent_thread_count            = 10
_concurrent_messages_per_thread     = 1_000
_concurrent_throughput_threshold    = 1_000

# Step 14 - Large message sizes and counts
_large_message_count_per_size       = 100
_large_message_size_1kb             = 1_000
_large_message_size_10kb            = 10_000
_large_message_size_100kb           = 100_000
_large_message_size_1mb             = 1_000_000
_bytes_per_megabyte                 = 1_000_000

# Step 14 - New connection per message
_new_connection_message_count       = 1_000
_new_connection_throughput_threshold = 200

# Step 14 - Persistent connection
_persistent_message_count           = 10_000
_persistent_throughput_threshold    = 2_000

# Shared
_max_message_size                   = 2_000_000
_recv_buffer_size                   = 4096
_socket_timeout                     = 30.0
_milliseconds_per_second            = 1000.0

# ################################################################################################################################
# ################################################################################################################################
# Step 13 - Sequential throughput
# ################################################################################################################################
# ################################################################################################################################

class TestSequentialThroughput:
    """ Measures how many messages per second a single client can send sequentially,
    each on a new TCP connection.
    """

# ################################################################################################################################

    def test_sequential_throughput(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ Sends many messages sequentially, each on a fresh connection,
        and measures throughput and average latency.
        """

        start_time = time.perf_counter()

        for index in range(_sequential_message_count):
            control_id = f'SEQ{index:06d}'
            client = make_client(mllp_server)
            _ = client.send(sample_adt_a01(control_id), control_id=control_id)

        elapsed = time.perf_counter() - start_time

        messages_per_second = _sequential_message_count / elapsed
        average_latency_milliseconds = (elapsed / _sequential_message_count) * _milliseconds_per_second

        perf_log('Sequential throughput', messages_per_second, 'msg/s', threshold=_sequential_throughput_threshold)
        perf_log('Sequential avg latency', average_latency_milliseconds, 'ms')

        assert messages_per_second > _sequential_throughput_threshold

# ################################################################################################################################
# ################################################################################################################################
# Step 14 - Concurrent, large, churn, persistent
# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentThroughput:
    """ Measures throughput with multiple threads sending in parallel.
    """

# ################################################################################################################################

    def test_concurrent_throughput(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ Spawns multiple threads, each sending many messages, and measures
        the aggregate wall-clock throughput.
        """

        errors:'list[str]' = []

        def _thread_worker(thread_index:'int') -> 'None':
            try:
                for message_index in range(_concurrent_messages_per_thread):
                    control_id = f'CON{thread_index:03d}{message_index:04d}'
                    client = make_client(mllp_server)
                    _ = client.send(sample_adt_a01(control_id), control_id=control_id)
            except Exception as exception:
                errors.append(f'Thread {thread_index}: {exception}')

        threads:'list[threading.Thread]' = []

        for thread_index in range(_concurrent_thread_count):
            thread = threading.Thread(target=_thread_worker, args=(thread_index,))
            threads.append(thread)

        start_time = time.perf_counter()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        elapsed = time.perf_counter() - start_time

        total_messages = _concurrent_thread_count * _concurrent_messages_per_thread
        messages_per_second = total_messages / elapsed

        perf_log(f'Concurrent ({_concurrent_thread_count} threads)', messages_per_second, 'msg/s',
            threshold=_concurrent_throughput_threshold)

        assert len(errors) == 0, f'Thread errors: {errors}'
        assert messages_per_second > _concurrent_throughput_threshold

# ################################################################################################################################
# ################################################################################################################################

class TestLargeMessageThroughput:
    """ Measures throughput for messages of various sizes.
    """

# ################################################################################################################################

    def test_large_message_throughput(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ Sends batches of messages at different sizes and reports MB/s and latency.
        """

        size_configs = [
            ('1 KB messages', _large_message_size_1kb),
            ('10 KB messages', _large_message_size_10kb),
            ('100 KB messages', _large_message_size_100kb),
            ('1 MB messages', _large_message_size_1mb),
        ]

        for label, target_size in size_configs:

            # Build a padded message to reach the target size ..
            base_message = sample_adt_a01(f'BIG{target_size:07d}')
            padding_needed = target_size - len(base_message)

            if padding_needed > 0:
                padding_segment = b'\rOBX|1|TX|PAD^Padding||' + (b'X' * (padding_needed - 25))
                padded_message = base_message + padding_segment
            else:
                padded_message = base_message

            total_bytes = len(padded_message) * _large_message_count_per_size

            start_time = time.perf_counter()

            for _ in range(_large_message_count_per_size):
                client = make_client(mllp_server)
                _ = client.send(padded_message, control_id=f'BIG{target_size:07d}')

            elapsed = time.perf_counter() - start_time

            megabytes_per_second = (total_bytes / _bytes_per_megabyte) / elapsed
            average_latency_milliseconds = (elapsed / _large_message_count_per_size) * _milliseconds_per_second

            perf_log(label, megabytes_per_second, 'MB/s')
            perf_log(f'{label} avg latency', average_latency_milliseconds, 'ms')

# ################################################################################################################################
# ################################################################################################################################

class TestNewConnectionPerMessage:
    """ Measures throughput when every message opens and closes a new TCP connection.
    """

# ################################################################################################################################

    def test_new_connection_per_message(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ Sends messages each on a fresh connection to measure connection setup overhead.
        """

        start_time = time.perf_counter()

        for index in range(_new_connection_message_count):
            control_id = f'NEWC{index:06d}'
            client = make_client(mllp_server)
            _ = client.send(sample_adt_a01(control_id), control_id=control_id)

        elapsed = time.perf_counter() - start_time

        messages_per_second = _new_connection_message_count / elapsed

        perf_log('New connection per message', messages_per_second, 'msg/s',
            threshold=_new_connection_throughput_threshold)

        assert messages_per_second > _new_connection_throughput_threshold

# ################################################################################################################################
# ################################################################################################################################

class TestPersistentConnection:
    """ Measures throughput on a single persistent TCP connection using raw sockets.
    """

# ################################################################################################################################

    def test_persistent_connection(self, mllp_server:'int') -> 'None':
        """ Sends many messages on one raw socket without reconnecting.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)
        raw_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        decoder = FrameDecoder(start_sequence, end_sequence, _max_message_size)

        try:

            start_time = time.perf_counter()
            ack_count = 0

            for index in range(_persistent_message_count):

                # Send a framed message ..
                control_id = f'PERS{index:06d}'
                message = sample_adt_a01(control_id)
                framed = frame_encode(message, start_sequence, end_sequence)
                raw_socket.sendall(framed)

                # .. read until we get the ACK for this message ..
                while True:
                    chunk = raw_socket.recv(_recv_buffer_size)

                    if not chunk:
                        raise ConnectionError('Socket closed during persistent connection benchmark')

                    decoder.feed(chunk)

                    while True:
                        ack_message = decoder.next_message()

                        if ack_message is None:
                            break

                        ack_count += 1

                    if ack_count > index:
                        break

            elapsed = time.perf_counter() - start_time

            messages_per_second = _persistent_message_count / elapsed

            perf_log('Persistent connection', messages_per_second, 'msg/s',
                threshold=_persistent_throughput_threshold)

            assert messages_per_second > _persistent_throughput_threshold

        finally:
            raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################

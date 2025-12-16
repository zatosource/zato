# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent monkey patching must be first
from gevent import monkey
monkey.patch_all()

# stdlib
import argparse
import sys
import time
from datetime import datetime

# gevent
from gevent import sleep as gsleep

# Local
from zato.common.nats_.client import NATSClient
from zato.common.nats_.exc import NATSTimeoutError, NATSJetStreamError
from zato.common.nats_.const import Consumer_Ack_Explicit, Consumer_Deliver_All, Err_Consumer_Already_Exists
from zato.common.nats_.model import ConsumerConfig, StreamConfig

# ################################################################################################################################
# ################################################################################################################################

def parse_range(range_str: str) -> tuple:
    """ Parses a range string like '0-300' or '150-500' into (start, end) tuple.
    """
    parts = range_str.split('-')
    if len(parts) != 2:
        raise ValueError(f'Invalid range format: {range_str}. Expected format: start-end (e.g., 0-300)')

    start = int(parts[0])
    end = int(parts[1])

    if start > end:
        raise ValueError(f'Start ({start}) must be <= end ({end})')

    return start, end

# ################################################################################################################################

def generate_stream_names(start: int, end: int) -> list:
    """ Generates stream names from start to end (inclusive).
    """
    streams = []
    for i in range(start, end + 1):
        streams.append(f'demo-{i:04d}')
    return streams

# ################################################################################################################################

def generate_subject(stream_name: str) -> str:
    """ Generates subject name for a stream.
    """
    return stream_name.replace('-', '.')

# ################################################################################################################################

def run_subscriber(host: str, port: int, start: int, end: int) -> None:
    """ Subscribes to streams, fetches and acks messages.
    """
    stream_names = generate_stream_names(start, end)
    print(f'Subscribing to {len(stream_names)} streams: {stream_names[0]} to {stream_names[-1]}')

    client = NATSClient()
    client.connect(host=host, port=port)
    client.start_reader()
    js = client.jetstream()

    # Ensure streams exist and create consumers
    consumers = []
    for stream_name in stream_names:
        subject = generate_subject(stream_name)

        # Create stream if needed
        config = StreamConfig(
            name=stream_name,
            subjects=[subject],
        )
        try:
            js.create_stream(config)
        except NATSJetStreamError as e:
            if 'already in use' not in str(e).lower():
                raise

        # Create consumer
        consumer_name = f'{stream_name}-consumer'
        consumer_config = ConsumerConfig(
            name=consumer_name,
            deliver_policy=Consumer_Deliver_All,
            ack_policy=Consumer_Ack_Explicit,
        )

        try:
            js.create_consumer(stream_name, consumer_config)
        except NATSJetStreamError as e:
            if e.err_code != Err_Consumer_Already_Exists:
                raise

        consumers.append((stream_name, consumer_name))

    print(f'Created/using {len(consumers)} consumers')
    print('Waiting for messages... (Ctrl+C to stop)')

    msg_count = 0
    ack_count = 0
    start_time = None
    last_report = time.time()

    try:
        while True:
            for stream_name, consumer_name in consumers:
                try:
                    msgs = js.fetch(stream_name, consumer_name, batch=10, timeout=0.1)
                    for msg in msgs:
                        if start_time is None:
                            start_time = time.time()
                        msg_count += 1
                        js.ack(msg)
                        ack_count += 1
                except NATSTimeoutError:
                    pass

            # Report every second
            now = time.time()
            if now - last_report >= 1.0:
                if start_time:
                    elapsed = now - start_time
                    rate = msg_count / elapsed if elapsed > 0 else 0
                    print(f'[{datetime.now().isoformat()}] Received/acked {msg_count} messages, {rate:.0f} msg/sec')
                last_report = now

            gsleep(0)

    except KeyboardInterrupt:
        print(f'\nTotal received: {msg_count} messages, acked: {ack_count}')
        if start_time:
            elapsed = time.time() - start_time
            rate = msg_count / elapsed if elapsed > 0 else 0
            print(f'Average rate: {rate:.0f} msg/sec over {elapsed:.1f} seconds')
    finally:
        client.close()

# ################################################################################################################################

def run_publisher(host: str, port: int, start: int, end: int) -> None:
    """ Publishes messages to streams as fast as possible.
    """
    stream_names = generate_stream_names(start, end)
    print(f'Publishing to {len(stream_names)} streams: {stream_names[0]} to {stream_names[-1]}')

    client = NATSClient()
    client.connect(host=host, port=port)
    client.start_reader()
    js = client.jetstream()

    # Ensure streams exist
    for stream_name in stream_names:
        subject = generate_subject(stream_name)
        config = StreamConfig(
            name=stream_name,
            subjects=[subject],
        )
        try:
            js.create_stream(config)
            print(f'Created stream {stream_name}')
        except NATSJetStreamError as e:
            if 'already in use' in str(e).lower():
                pass  # Stream exists
            else:
                raise

    print('Publishing messages... (Ctrl+C to stop)')

    msg_count = 0
    start_time = time.time()
    last_report = start_time
    data = b'X' * 5120  # 5 KB message

    try:
        while True:
            for stream_name in stream_names:
                subject = generate_subject(stream_name)
                js.publish(subject, data)
                msg_count += 1

            # Report every second
            now = time.time()
            if now - last_report >= 1.0:
                elapsed = now - start_time
                rate = msg_count / elapsed if elapsed > 0 else 0
                print(f'[{datetime.now().isoformat()}] Published {msg_count} messages, {rate:.0f} msg/sec')
                last_report = now

            gsleep(0)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        rate = msg_count / elapsed if elapsed > 0 else 0
        print(f'\nTotal published: {msg_count} messages')
        print(f'Average rate: {rate:.0f} msg/sec over {elapsed:.1f} seconds')
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def main() -> None:
    parser = argparse.ArgumentParser(description='NATS JetStream Performance Test')
    parser.add_argument('command', choices=['sub', 'pub'], help='Command: sub or pub')
    parser.add_argument('range', help='Stream range (e.g., 0-300 or 150-500)')
    parser.add_argument('--host', default='127.0.0.1', help='NATS server host')
    parser.add_argument('--port', type=int, default=4222, help='NATS server port')

    args = parser.parse_args()

    try:
        start, end = parse_range(args.range)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    if args.command == 'sub':
        run_subscriber(args.host, args.port, start, end)
    else:
        run_publisher(args.host, args.port, start, end)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import os
import sys
import time
from datetime import datetime

# redis
import redis

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
        streams.append(f'demo:{i:04d}')
    return streams

# ################################################################################################################################

def run_subscriber(host: str, port: int, start: int, end: int) -> None:
    """ Subscribes to streams, reads and acks messages. Each subscriber gets its own consumer group for fan-out.
    """
    stream_names = generate_stream_names(start, end)
    print(f'Subscribing to {len(stream_names)} streams: {stream_names[0]} to {stream_names[-1]}')

    client = redis.Redis(host=host, port=port, decode_responses=False)

    # Each subscriber process gets unique consumer group for fan-out
    group_name = f'perftest-group-{os.getpid()}'
    consumer_name = 'consumer'

    for stream_name in stream_names:
        try:
            client.xgroup_create(stream_name, group_name, id='0', mkstream=True)
        except redis.ResponseError as e:
            if 'BUSYGROUP' not in str(e):
                raise

    print(f'Created consumer group "{group_name}" on {len(stream_names)} streams')
    print('Waiting for messages... (Ctrl+C to stop)')

    msg_count = 0
    ack_count = 0
    start_time = None
    last_report = time.time()

    # Build streams dict for XREADGROUP
    streams_dict = {name: '>' for name in stream_names}

    try:
        while True:
            results = client.xreadgroup(
                group_name,
                consumer_name,
                streams_dict,
                count=10,
                block=100
            )

            if results:
                for stream_name, messages in results:
                    for msg_id, msg_data in messages:
                        if start_time is None:
                            start_time = time.time()
                        msg_count += 1
                        client.xack(stream_name, group_name, msg_id)
                        ack_count += 1

            now = time.time()
            if now - last_report >= 1.0:
                if start_time:
                    elapsed = now - start_time
                    rate = msg_count / elapsed if elapsed > 0 else 0
                    print(f'[{datetime.now().isoformat()}] Received/acked {msg_count} messages, {rate:.0f} msg/sec')
                last_report = now

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

    client = redis.Redis(host=host, port=port, decode_responses=False)

    print('Publishing messages... (Ctrl+C to stop)')

    msg_count = 0
    start_time = time.time()
    last_report = start_time
    data = b'X' * 5120  # 5 KB message

    try:
        while True:
            for stream_name in stream_names:
                client.xadd(stream_name, {'data': data})
                msg_count += 1

            now = time.time()
            if now - last_report >= 1.0:
                elapsed = now - start_time
                rate = msg_count / elapsed if elapsed > 0 else 0
                print(f'[{datetime.now().isoformat()}] Published {msg_count} messages, {rate:.0f} msg/sec')
                last_report = now

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
    parser = argparse.ArgumentParser(description='Redis Streams Performance Test')
    parser.add_argument('command', choices=['sub', 'pub'], help='Command: sub or pub')
    parser.add_argument('range', help='Stream range (e.g., 0-300 or 150-500)')
    parser.add_argument('--host', default='127.0.0.1', help='Redis server host')
    parser.add_argument('--port', type=int, default=6379, help='Redis server port')

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

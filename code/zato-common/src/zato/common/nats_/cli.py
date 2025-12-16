# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import json
import signal
import sys
from datetime import datetime

# Local
from .client import NATSClient
from .const import Consumer_Ack_Explicit, Consumer_Deliver_All, Default_Host, Default_Num_Replicas, \
     Default_Port, Default_Timeout, Err_Consumer_Already_Exists, No_Limit, Stream_Retention_Limits, \
     Stream_Storage_File
from .exc import NATSError, NATSJetStreamError, NATSNoRespondersError, NATSTimeoutError
from .model import ConsumerConfig, StreamConfig

# ################################################################################################################################
# ################################################################################################################################

def format_msg(msg, show_headers=True):
    """ Formats a message for display.
    """
    output = []
    output.append(f'Subject: {msg.subject}')
    if msg.reply:
        output.append(f'Reply: {msg.reply}')
    if show_headers and msg.headers:
        output.append(f'Headers: {json.dumps(msg.headers, indent=2)}')
    output.append(f'Data: {msg.data.decode("utf-8", errors="replace")}')
    return '\n'.join(output)

# ################################################################################################################################
# ################################################################################################################################

def cmd_pub(args):
    """ Publishes a message to a subject.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        headers = None
        if args.header:
            headers = {}
            for h in args.header:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()

        data = args.data.encode('utf-8') if args.data else b''

        client.publish(args.subject, data, headers=headers)
        client.flush()

        print(f'Published {len(data)} bytes to "{args.subject}"')

    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_sub(args):
    """ Subscribes to a subject and prints messages.
    """
    client = NATSClient()
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False
        print('\nInterrupted')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        sub = client.subscribe(args.subject, queue=args.queue or '')
        print(f'Subscribed to "{args.subject}"' + (f' (queue: {args.queue})' if args.queue else ''))
        print('Waiting for messages... (Ctrl+C to quit)\n')

        count = 0
        while running:
            try:
                msg = sub.next_msg(timeout=1.0)
                count += 1
                print(f'[{datetime.now().isoformat()}] Message #{count}')
                print(format_msg(msg, show_headers=not args.no_headers))
                print('-' * 40)

                if args.max_msgs and count >= args.max_msgs:
                    print(f'Received {args.max_msgs} messages, exiting.')
                    break

            except NATSTimeoutError:
                continue

    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_request(args):
    """ Sends a request and waits for a response.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        headers = None
        if args.header:
            headers = {}
            for h in args.header:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()

        data = args.data.encode('utf-8') if args.data else b''

        msg = client.request(args.subject, data, timeout=args.request_timeout, headers=headers)

        print('Response:')
        print(format_msg(msg, show_headers=not args.no_headers))

    except NATSNoRespondersError:
        print('Error: No responders available', file=sys.stderr)
        sys.exit(1)
    except NATSTimeoutError:
        print('Error: Request timed out', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_pub(args):
    """ Publishes a message to JetStream.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        headers = None
        if args.header:
            headers = {}
            for h in args.header:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()

        data = args.data.encode('utf-8') if args.data else b''

        js = client.jetstream()
        ack = js.publish(
            args.subject,
            data,
            timeout=args.request_timeout,
            headers=headers,
            msg_id=args.msg_id,
        )

        print(f'Published to stream "{ack.stream}", sequence: {ack.seq}')
        if ack.duplicate:
            print('(duplicate message)')

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_sub(args):
    """ Subscribes to a JetStream stream and prints messages.
    """
    client = NATSClient()
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False
        print('\nInterrupted')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        # Ensure consumer exists
        if args.consumer:
            consumer_name = args.consumer
        else:
            nuid = client._nuid.next()
            nuid = nuid.decode()
            consumer_name = f'cli-consumer-{nuid}'

        consumer_config = ConsumerConfig(
            name=consumer_name,
            durable_name=args.durable,
            deliver_policy=args.deliver_policy,
            ack_policy=Consumer_Ack_Explicit,
            filter_subject=args.filter_subject,
        )

        try:
            js = client.jetstream()
            js.create_consumer(args.stream, consumer_config, timeout=args.request_timeout)
            print(f'Created consumer "{consumer_name}" on stream "{args.stream}"')
        except NATSJetStreamError as e:
            if e.err_code == Err_Consumer_Already_Exists:
                print(f'Using existing consumer "{consumer_name}" on stream "{args.stream}"')
            else:
                raise

        print('Waiting for messages... (Ctrl+C to quit)\n')

        count = 0
        while running:
            try:
                msgs = js.fetch(
                    args.stream,
                    consumer_name,
                    batch=args.batch,
                    timeout=args.fetch_timeout,
                )

                for msg in msgs:
                    count += 1
                    print(f'[{datetime.now().isoformat()}] Message #{count}')
                    print(format_msg(msg, show_headers=not args.no_headers))

                    if args.ack:
                        js.ack(msg)
                        print('(acknowledged)')

                    print('-' * 40)

                    if args.max_msgs and count >= args.max_msgs:
                        print(f'Received {args.max_msgs} messages, exiting.')
                        running = False
                        break

            except NATSTimeoutError:
                continue

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_stream_create(args):
    """ Creates a JetStream stream.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        config = StreamConfig(
            name=args.name,
            subjects=args.subjects.split(',') if args.subjects else [],
            storage=args.storage,
            retention=args.retention,
            max_msgs=args.max_msgs_limit,
            max_bytes=args.max_bytes,
            max_age=args.max_age,
            num_replicas=args.replicas,
        )

        js = client.jetstream()
        info = js.create_stream(config, timeout=args.request_timeout)

        print(f'Created stream "{args.name}"')
        print(f'  Subjects: {info.config.subjects}')
        print(f'  Storage: {info.config.storage}')
        print(f'  Retention: {info.config.retention}')
        print(f'  Replicas: {info.config.num_replicas}')

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_stream_delete(args):
    """ Deletes a JetStream stream.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        if not args.force:
            confirm = input(f'Delete stream "{args.name}"? [y/N]: ')
            if confirm.lower() != 'y':
                print('Cancelled')
                return

        js = client.jetstream()
        success = js.delete_stream(args.name, timeout=args.request_timeout)

        if success:
            print(f'Deleted stream "{args.name}"')
        else:
            print(f'Failed to delete stream "{args.name}"', file=sys.stderr)
            sys.exit(1)

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_stream_info(args):
    """ Returns information about a JetStream stream.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        js = client.jetstream()
        info = js.stream_info(args.name, timeout=args.request_timeout)

        print(f'Stream: {info.config.name}')
        print(f'  Description: {info.config.description or "(none)"}')
        print(f'  Subjects: {info.config.subjects}')
        print(f'  Storage: {info.config.storage}')
        print(f'  Retention: {info.config.retention}')
        print(f'  Replicas: {info.config.num_replicas}')
        print(f'State:')
        print(f'  Messages: {info.state.messages}')
        print(f'  Bytes: {info.state.bytes}')
        print(f'  First sequence: {info.state.first_seq}')
        print(f'  Last sequence: {info.state.last_seq}')
        print(f'  Consumers: {info.state.consumer_count}')

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def cmd_js_stream_purge(args):
    """ Purges messages from a JetStream stream.
    """
    client = NATSClient()

    try:
        client.connect(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            user=args.user,
            password=args.password,
            token=args.token,
        )

        if not args.force:
            confirm = input(f'Purge all messages from stream "{args.name}"? [y/N]: ')
            if confirm.lower() != 'y':
                print('Cancelled')
                return

        js = client.jetstream()
        purged = js.purge_stream(args.name, timeout=args.request_timeout)
        print(f'Purged {purged} messages from stream "{args.name}"')

    except NATSJetStreamError as e:
        print(f'JetStream error: {e.description}', file=sys.stderr)
        sys.exit(1)
    except NATSError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

def add_common_args(parser):
    """ Adds common connection arguments to a parser.
    """
    parser.add_argument('-s', '--host', default=Default_Host, help='NATS server host')
    parser.add_argument('-p', '--port', type=int, default=Default_Port, help='NATS server port')
    parser.add_argument('-t', '--timeout', type=float, default=Default_Timeout, help='Connection timeout')
    parser.add_argument('--user', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--token', help='Token for authentication')
    parser.add_argument('--request-timeout', type=float, default=Default_Timeout, help='Request timeout')

# ################################################################################################################################
# ################################################################################################################################

def main():
    """ Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        prog='nats',
        description='NATS Client CLI',
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # pub command
    pub_parser = subparsers.add_parser('pub', help='Publish a message')
    add_common_args(pub_parser)
    pub_parser.add_argument('subject', help='Subject to publish to')
    pub_parser.add_argument('data', nargs='?', default='', help='Message data')
    pub_parser.add_argument('-H', '--header', action='append', help='Header in Key:Value format (can be repeated)')
    pub_parser.set_defaults(func=cmd_pub)

    # sub command
    sub_parser = subparsers.add_parser('sub', help='Subscribe to a subject')
    add_common_args(sub_parser)
    sub_parser.add_argument('subject', help='Subject to subscribe to')
    sub_parser.add_argument('-q', '--queue', help='Queue group name')
    sub_parser.add_argument('--max-msgs', type=int, help='Maximum messages to receive')
    sub_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
    sub_parser.set_defaults(func=cmd_sub)

    # request command
    req_parser = subparsers.add_parser('request', help='Send a request')
    add_common_args(req_parser)
    req_parser.add_argument('subject', help='Subject to send request to')
    req_parser.add_argument('data', nargs='?', default='', help='Request data')
    req_parser.add_argument('-H', '--header', action='append', help='Header in Key:Value format (can be repeated)')
    req_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
    req_parser.set_defaults(func=cmd_request)

    # js pub command
    js_pub_parser = subparsers.add_parser('js-pub', help='Publish to JetStream')
    add_common_args(js_pub_parser)
    js_pub_parser.add_argument('subject', help='Subject to publish to')
    js_pub_parser.add_argument('data', nargs='?', default='', help='Message data')
    js_pub_parser.add_argument('-H', '--header', action='append', help='Header in Key:Value format (can be repeated)')
    js_pub_parser.add_argument('--msg-id', help='Message ID for deduplication')
    js_pub_parser.set_defaults(func=cmd_js_pub)

    # js sub command
    js_sub_parser = subparsers.add_parser('js-sub', help='Subscribe to JetStream')
    add_common_args(js_sub_parser)
    js_sub_parser.add_argument('stream', help='Stream name')
    js_sub_parser.add_argument('--consumer', help='Consumer name')
    js_sub_parser.add_argument('--durable', help='Durable consumer name')
    js_sub_parser.add_argument('--filter-subject', help='Filter subject')
    js_sub_parser.add_argument('--deliver-policy', default=Consumer_Deliver_All, choices=['all', 'last', 'new'], help='Delivery policy')
    js_sub_parser.add_argument('--batch', type=int, default=1, help='Batch size (default: 1)')
    js_sub_parser.add_argument('--fetch-timeout', type=float, default=Default_Timeout, help='Fetch timeout')
    js_sub_parser.add_argument('--max-msgs', type=int, help='Maximum messages to receive')
    js_sub_parser.add_argument('--ack', action='store_true', help='Acknowledge messages')
    js_sub_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
    js_sub_parser.set_defaults(func=cmd_js_sub)

    # js stream create command
    js_stream_create_parser = subparsers.add_parser('js-stream-create', help='Create a JetStream stream')
    add_common_args(js_stream_create_parser)
    js_stream_create_parser.add_argument('name', help='Stream name')
    js_stream_create_parser.add_argument('--subjects', help='Comma-separated list of subjects')
    js_stream_create_parser.add_argument('--storage', default=Stream_Storage_File, choices=['file', 'memory'], help='Storage type')
    js_stream_create_parser.add_argument('--retention', default=Stream_Retention_Limits, choices=['limits', 'interest', 'workqueue'],
                                         help='Retention policy')
    js_stream_create_parser.add_argument('--max-msgs-limit', type=int, default=No_Limit, help='Maximum messages')
    js_stream_create_parser.add_argument('--max-bytes', type=int, default=No_Limit, help='Maximum bytes')
    js_stream_create_parser.add_argument('--max-age', type=int, default=0, help='Maximum age in nanoseconds')
    js_stream_create_parser.add_argument('--replicas', type=int, default=Default_Num_Replicas, help='Number of replicas')
    js_stream_create_parser.set_defaults(func=cmd_js_stream_create)

    # js stream delete command
    js_stream_delete_parser = subparsers.add_parser('js-stream-delete', help='Delete a JetStream stream')
    add_common_args(js_stream_delete_parser)
    js_stream_delete_parser.add_argument('name', help='Stream name')
    js_stream_delete_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    js_stream_delete_parser.set_defaults(func=cmd_js_stream_delete)

    # js stream info command
    js_stream_info_parser = subparsers.add_parser('js-stream-info', help='Get stream information')
    add_common_args(js_stream_info_parser)
    js_stream_info_parser.add_argument('name', help='Stream name')
    js_stream_info_parser.set_defaults(func=cmd_js_stream_info)

    # js stream purge command
    js_stream_purge_parser = subparsers.add_parser('js-stream-purge', help='Purge stream messages')
    add_common_args(js_stream_purge_parser)
    js_stream_purge_parser.add_argument('name', help='Stream name')
    js_stream_purge_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    js_stream_purge_parser.set_defaults(func=cmd_js_stream_purge)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

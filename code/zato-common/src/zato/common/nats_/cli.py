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
import json
import logging
import readline
import shlex
import signal
import sys
from datetime import datetime
from pathlib import Path
from traceback import format_exc

# gevent
from gevent import spawn, sleep as gsleep
from gevent.lock import RLock

# colorama (optional)
try:
    from colorama import init as colorama_init, Fore, Style
    has_colorama = True
except ImportError:
    has_colorama = False
    colorama_init = lambda: None
    class Fore:
        GREEN = YELLOW = CYAN = MAGENTA = BLUE = RED = WHITE = ''
    class Style:
        RESET_ALL = ''

# Zato
from zato.common.typing_ import any_

from zato.common.nats_.client import NATSClient
from zato.common.nats_.const import Consumer_Ack_Explicit, Consumer_Deliver_All, Default_Host, \
     Default_Num_Replicas, Default_Port, Default_Timeout, Err_Consumer_Already_Exists, No_Limit, \
     Stream_Retention_Limits, Stream_Storage_File
from zato.common.nats_.exc import NATSError, NATSJetStreamError, NATSNoRespondersError, NATSTimeoutError
from zato.common.nats_.model import ConsumerConfig, Msg, StreamConfig

# ################################################################################################################################
# ################################################################################################################################

class NATSCLI:
    """ NATS command-line interface.
    """

    commands = [
        'pub', 'sub', 'request',
        'js-pub', 'js-sub',
        'js-stream-create', 'js-stream-delete', 'js-stream-info', 'js-stream-purge',
        'greenlets', 'help', 'exit', 'quit',
    ]

    colors = [
        Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA,
        Fore.BLUE, Fore.RED, Fore.WHITE,
    ]

    history_file = Path.home() / '.nats_cli_history'

    def __init__(self) -> None:
        colorama_init()
        self.running = True
        self.parser = self._build_parser()
        self.greenlets: 'list' = []
        self.greenlet_info: 'dict' = {}  # gid -> {'subject': str, 'started': datetime}
        self.greenlet_id = 0
        self.print_lock = RLock()
        self.reader_client: 'NATSClient | None' = None
        self.writer_client: 'NATSClient | None' = None

    # ############################################################################################################################

    def _signal_handler(self, sig:'int', frame:'any_') -> 'None':
        self.running = False
        print('\nInterrupted')

    # ############################################################################################################################

    def _get_color(self, gid:'int') -> 'str':
        """ Returns a color for the given greenlet ID.
        """
        return self.colors[gid % len(self.colors)]

    # ############################################################################################################################

    def _cprint(self, gid:'int', msg:'str') -> 'None':
        """ Prints a message with color based on greenlet ID.
        """
        color = self._get_color(gid)
        ts = datetime.now().isoformat()
        with self.print_lock:
            print(f'{ts} {color}[G{gid}]{Style.RESET_ALL} {msg}')

    # ############################################################################################################################

    def _get_reader_client(self, args:'argparse.Namespace') -> 'NATSClient':
        """ Returns the reader client connection for subscriptions.
        """
        needs_connect = False

        if self.reader_client is None:
            needs_connect = True
        elif not self.reader_client.is_connected:
            needs_connect = True

        if needs_connect:
            self.reader_client = NATSClient()
            self.reader_client.connect(
                host=args.host,
                port=args.port,
                timeout=args.timeout,
                user=args.user,
                password=args.password,
                token=args.token,
                verbose=args.verbose,
            )
            self.reader_client.start_reader()
        return self.reader_client

    # ############################################################################################################################

    def _get_writer_client(self, args:'argparse.Namespace') -> 'NATSClient':
        """ Returns the writer client connection for publishing.
        """
        needs_connect = False

        if self.writer_client is None:
            needs_connect = True
        elif not self.writer_client.is_connected:
            needs_connect = True

        if needs_connect:
            self.writer_client = NATSClient()
            self.writer_client.connect(
                host=args.host,
                port=args.port,
                timeout=args.timeout,
                user=args.user,
                password=args.password,
                token=args.token,
                verbose=args.verbose,
            )
        return self.writer_client

    # ############################################################################################################################

    def _format_time_ago(self, dt:'datetime') -> 'str':
        """ Formats a datetime as time ago string.
        """
        delta = datetime.now() - dt
        seconds = int(delta.total_seconds())

        if seconds < 60:
            unit = 'second' if seconds == 1 else 'seconds'
            return f'{seconds} {unit} ago'

        minutes = seconds // 60
        if minutes < 60:
            unit = 'minute' if minutes == 1 else 'minutes'
            return f'{minutes} {unit} ago'

        hours = minutes // 60
        unit = 'hour' if hours == 1 else 'hours'
        return f'{hours} {unit} ago'

    # ############################################################################################################################

    def _list_greenlets(self) -> 'None':
        """ Lists active greenlets.
        """
        # Remove dead greenlets and their info
        alive = []
        for g, gid in self.greenlets:
            if not g.dead:
                alive.append((g, gid))
            else:
                self.greenlet_info.pop(gid, None)
        self.greenlets = alive

        if not self.greenlets:
            print('No active greenlets.')
            return

        print(f'Active greenlets: {len(self.greenlets)}')
        for g, gid in self.greenlets:
            color = self._get_color(gid)
            info = self.greenlet_info.get(gid, {})
            subject = info.get('subject', '?')
            started = info.get('started')
            time_ago = self._format_time_ago(started) if started else '?'
            print(f'  {color}[G{gid}]{Style.RESET_ALL} {subject} (started {time_ago})')

    # ############################################################################################################################

    def _cleanup_greenlets(self) -> 'None':
        """ Kills all greenlets and closes clients.
        """
        self.running = False
        for g, gid in self.greenlets:
            if not g.dead:
                g.kill()
        self.greenlets.clear()
        self.greenlet_info.clear()

        if self.reader_client:
            self.reader_client.close()
            self.reader_client = None
        if self.writer_client:
            self.writer_client.close()
            self.writer_client = None

    # ############################################################################################################################

    def _format_msg(self, msg:'Msg', show_headers:'bool'=True) -> 'str':
        """ Formats a message for display.
        """
        output = []
        output.append(f'Subject: {msg.subject}')
        if msg.reply:
            output.append(f'Reply: {msg.reply}')
        if show_headers and msg.headers:
            headers_str = json.dumps(msg.headers, indent=2)
            output.append(f'Headers: {headers_str}')
        data_str = msg.data.decode('utf-8', errors='replace')
        output.append(f'Data: {data_str}')
        return '\n'.join(output)

    # ############################################################################################################################

    def _add_common_args(self, parser:'argparse.ArgumentParser') -> 'None':
        """ Adds common connection arguments to a parser.
        """
        _ = parser.add_argument('-s', '--host', default=Default_Host, help='NATS server host')
        _ = parser.add_argument('-p', '--port', type=int, default=Default_Port, help='NATS server port')
        _ = parser.add_argument('-t', '--timeout', type=float, default=Default_Timeout, help='Connection timeout')
        _ = parser.add_argument('--user', help='Username for authentication')
        _ = parser.add_argument('--password', help='Password for authentication')
        _ = parser.add_argument('--token', help='Token for authentication')
        _ = parser.add_argument('--request-timeout', type=float, default=Default_Timeout, help='Request timeout')
        _ = parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')

    # ############################################################################################################################

    def _build_parser(self) -> 'argparse.ArgumentParser':
        """ Builds the argument parser.
        """
        parser = argparse.ArgumentParser(
            prog='nats',
            description='NATS Client CLI',
            add_help=False,
        )
        _ = parser.add_argument('--help', action='help', help='Show this help message and exit')

        subparsers = parser.add_subparsers(dest='command', help='Commands')

        # pub command
        pub_parser = subparsers.add_parser('pub', help='Publish a message', add_help=False)
        self._add_common_args(pub_parser)
        _ = pub_parser.add_argument('subject', help='Subject to publish to')
        _ = pub_parser.add_argument('data', nargs='?', default='', help='Message data')
        _ = pub_parser.add_argument('multiplier', nargs='?', default=None, help='* for repeat')
        _ = pub_parser.add_argument('repeat', nargs='?', type=int, default=1, help='Repeat count')
        _ = pub_parser.add_argument('data_multiplier', nargs='?', default=None, help='* for data multiply')
        _ = pub_parser.add_argument('data_repeat', nargs='?', type=int, default=1, help='Data multiply count')
        _ = pub_parser.add_argument('-h', '--header', action='append', help='Header in Key:Value format')
        _ = pub_parser.set_defaults(func=self.cmd_pub)

        # sub command
        sub_parser = subparsers.add_parser('sub', help='Subscribe to a subject')
        self._add_common_args(sub_parser)
        _ = sub_parser.add_argument('subject', help='Subject to subscribe to')
        _ = sub_parser.add_argument('-q', '--queue', help='Queue group name')
        _ = sub_parser.add_argument('--max-msgs', type=int, help='Maximum messages to receive')
        _ = sub_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
        _ = sub_parser.set_defaults(func=self.cmd_sub)

        # request command
        req_parser = subparsers.add_parser('request', help='Send a request', add_help=False)
        self._add_common_args(req_parser)
        _ = req_parser.add_argument('subject', help='Subject to send request to')
        _ = req_parser.add_argument('data', nargs='?', default='', help='Request data')
        _ = req_parser.add_argument('-h', '--header', action='append', help='Header in Key:Value format')
        _ = req_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
        _ = req_parser.set_defaults(func=self.cmd_request)

        # js pub command
        js_pub_parser = subparsers.add_parser('js-pub', help='Publish to JetStream', add_help=False)
        self._add_common_args(js_pub_parser)
        _ = js_pub_parser.add_argument('subject', help='Subject to publish to')
        _ = js_pub_parser.add_argument('data', nargs='?', default='', help='Message data')
        _ = js_pub_parser.add_argument('multiplier', nargs='?', default=None, help='* for repeat')
        _ = js_pub_parser.add_argument('repeat', nargs='?', type=int, default=1, help='Repeat count')
        _ = js_pub_parser.add_argument('data_multiplier', nargs='?', default=None, help='* for data multiply')
        _ = js_pub_parser.add_argument('data_repeat', nargs='?', type=int, default=1, help='Data multiply count')
        _ = js_pub_parser.add_argument('-h', '--header', action='append', help='Header in Key:Value format')
        _ = js_pub_parser.add_argument('--msg-id', help='Message ID for deduplication')
        _ = js_pub_parser.set_defaults(func=self.cmd_js_pub)

        # js sub command
        js_sub_parser = subparsers.add_parser('js-sub', help='Subscribe to JetStream')
        self._add_common_args(js_sub_parser)
        _ = js_sub_parser.add_argument('stream', help='Stream name')
        _ = js_sub_parser.add_argument('--consumer', help='Consumer name')
        _ = js_sub_parser.add_argument('--durable', help='Durable consumer name')
        _ = js_sub_parser.add_argument('--filter-subject', help='Filter subject')
        _ = js_sub_parser.add_argument('--deliver-policy', default=Consumer_Deliver_All,
            choices=['all', 'last', 'new'], help='Delivery policy')
        _ = js_sub_parser.add_argument('--batch', type=int, default=1, help='Batch size')
        _ = js_sub_parser.add_argument('--fetch-timeout', type=float, default=Default_Timeout, help='Fetch timeout')
        _ = js_sub_parser.add_argument('--max-msgs', type=int, help='Maximum messages to receive')
        _ = js_sub_parser.add_argument('--ack', action='store_true', help='Acknowledge messages')
        _ = js_sub_parser.add_argument('--no-headers', action='store_true', help='Do not display headers')
        _ = js_sub_parser.set_defaults(func=self.cmd_js_sub)

        # js stream create command
        js_stream_create_parser = subparsers.add_parser('js-stream-create', help='Create a JetStream stream')
        self._add_common_args(js_stream_create_parser)
        _ = js_stream_create_parser.add_argument('name', help='Stream name')
        _ = js_stream_create_parser.add_argument('--subjects', help='Comma-separated list of subjects')
        _ = js_stream_create_parser.add_argument('--storage', default=Stream_Storage_File,
            choices=['file', 'memory'], help='Storage type')
        _ = js_stream_create_parser.add_argument('--retention', default=Stream_Retention_Limits,
            choices=['limits', 'interest', 'workqueue'], help='Retention policy')
        _ = js_stream_create_parser.add_argument('--max-msgs-limit', type=int, default=No_Limit, help='Maximum messages')
        _ = js_stream_create_parser.add_argument('--max-bytes', type=int, default=No_Limit, help='Maximum bytes')
        _ = js_stream_create_parser.add_argument('--max-age', type=int, default=0, help='Maximum age in nanoseconds')
        _ = js_stream_create_parser.add_argument('--replicas', type=int, default=Default_Num_Replicas,
            help='Number of replicas')
        _ = js_stream_create_parser.set_defaults(func=self.cmd_js_stream_create)

        # js stream delete command
        js_stream_delete_parser = subparsers.add_parser('js-stream-delete', help='Delete a JetStream stream')
        self._add_common_args(js_stream_delete_parser)
        _ = js_stream_delete_parser.add_argument('name', help='Stream name')
        _ = js_stream_delete_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
        _ = js_stream_delete_parser.set_defaults(func=self.cmd_js_stream_delete)

        # js stream info command
        js_stream_info_parser = subparsers.add_parser('js-stream-info', help='Get stream information')
        self._add_common_args(js_stream_info_parser)
        _ = js_stream_info_parser.add_argument('name', help='Stream name')
        _ = js_stream_info_parser.set_defaults(func=self.cmd_js_stream_info)

        # js stream purge command
        js_stream_purge_parser = subparsers.add_parser('js-stream-purge', help='Purge stream messages')
        self._add_common_args(js_stream_purge_parser)
        _ = js_stream_purge_parser.add_argument('name', help='Stream name')
        _ = js_stream_purge_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
        _ = js_stream_purge_parser.set_defaults(func=self.cmd_js_stream_purge)

        return parser

    # ############################################################################################################################

    def cmd_pub(self, args:'argparse.Namespace') -> 'None':
        """ Publishes a message to a subject.
        """
        try:
            client = self._get_writer_client(args)

            headers = None
            if args.header:
                headers = {}
                for h in args.header:
                    key, value = h.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    headers[key] = value

            data_str = args.data if args.data else ''

            # Multiply data if * N specified
            if args.data_multiplier == '*':
                data_str = data_str * args.data_repeat

            data = data_str.encode('utf-8')

            repeat = args.repeat if args.multiplier == '*' else 1

            with self.print_lock:
                for _ in range(repeat):
                    client.publish(args.subject, data, headers=headers)
                client.flush()

            if repeat > 1:
                print(f'Published {len(data)} bytes to "{args.subject}" x {repeat}')
            else:
                print(f'Published {len(data)} bytes to "{args.subject}"')

        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_sub(self, args:'argparse.Namespace') -> 'None':
        """ Subscribes to a subject and prints messages. Runs as a greenlet.
        """
        self.greenlet_id += 1
        gid = self.greenlet_id

        def sub_worker():
            try:
                client = self._get_reader_client(args)

                queue = args.queue if args.queue else ''
                sub = client.subscribe(args.subject, queue=queue)

                msg = f'Subscribed to "{args.subject}"'
                if args.queue:
                    msg += f' (queue: {args.queue})'
                self._cprint(gid, msg)
                self._cprint(gid, 'Waiting for messages...')

                count = 0
                while self.running:
                    try:
                        msg = sub.next_msg(timeout=1.0)
                        count += 1
                        self._cprint(gid, f'[{datetime.now().isoformat()}] Message #{count}')
                        self._cprint(gid, self._format_msg(msg, show_headers=not args.no_headers))
                        self._cprint(gid, '-' * 40)

                        if args.max_msgs and count >= args.max_msgs:
                            self._cprint(gid, f'Received {args.max_msgs} messages, exiting.')
                            break

                    except NATSTimeoutError:
                        continue

            except NATSError:
                self._cprint(gid, f'Error: {format_exc()}')

        g = spawn(sub_worker)
        self.greenlets.append((g, gid))
        self.greenlet_info[gid] = {'subject': args.subject, 'started': datetime.now()}
        self._cprint(gid, f'Started subscription greenlet for "{args.subject}"')

    # ############################################################################################################################

    def cmd_request(self, args:'argparse.Namespace') -> 'None':
        """ Sends a request and waits for a response.
        """
        try:
            client = self._get_writer_client(args)

            headers = None
            if args.header:
                headers = {}
                for h in args.header:
                    key, value = h.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    headers[key] = value

            data = args.data.encode('utf-8') if args.data else b''

            msg = client.request(args.subject, data, timeout=args.request_timeout, headers=headers)

            print('Response:')
            print(self._format_msg(msg, show_headers=not args.no_headers))

        except NATSNoRespondersError:
            print('Error: No responders available', file=sys.stderr)
        except NATSTimeoutError:
            print('Error: Request timed out', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_js_pub(self, args:'argparse.Namespace') -> 'None':
        """ Publishes a message to JetStream.
        """
        try:
            client = self._get_writer_client(args)

            headers = None
            if args.header:
                headers = {}
                for h in args.header:
                    key, value = h.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    headers[key] = value

            data_str = args.data if args.data else ''

            # Multiply data if * N specified
            if args.data_multiplier == '*':
                data_str = data_str * args.data_repeat

            data = data_str.encode('utf-8')

            js = client.jetstream()

            repeat = args.repeat if args.multiplier == '*' else 1

            for i in range(repeat):
                msg_id = args.msg_id
                if msg_id and repeat > 1:
                    msg_id = f'{args.msg_id}-{i}'

                ack = js.publish(
                    args.subject,
                    data,
                    timeout=args.request_timeout,
                    headers=headers,
                    msg_id=msg_id,
                )

                if repeat == 1:
                    print(f'Published to stream "{ack.stream}", sequence: {ack.seq}')
                    if ack.duplicate:
                        print('(duplicate message)')

            if repeat > 1:
                print(f'Published {repeat} messages to stream "{ack.stream}"')

        except NATSNoRespondersError:
            print("Error: No responders available. Is JetStream enabled? Run 'nats-server -js'", file=sys.stderr)
        except NATSJetStreamError:
            print(f'JetStream error: {format_exc()}', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_js_sub(self, args:'argparse.Namespace') -> 'None':
        """ Subscribes to a JetStream stream and prints messages. Runs as a greenlet.
        """
        self.greenlet_id += 1
        gid = self.greenlet_id

        def js_sub_worker():
            try:
                client = self._get_reader_client(args)

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
                    _ = js.create_consumer(args.stream, consumer_config, timeout=args.request_timeout)
                    self._cprint(gid, f'Created consumer "{consumer_name}" on stream "{args.stream}"')
                except NATSJetStreamError as e:
                    if e.err_code == Err_Consumer_Already_Exists:
                        self._cprint(gid, f'Using existing consumer "{consumer_name}" on stream "{args.stream}"')
                    else:
                        raise

                self._cprint(gid, 'Waiting for messages...')

                count = 0
                while self.running:
                    try:
                        msgs = js.fetch(
                            args.stream,
                            consumer_name,
                            batch=args.batch,
                            timeout=args.fetch_timeout,
                        )

                        for msg in msgs:
                            count += 1
                            self._cprint(gid, f'[{datetime.now().isoformat()}] Message #{count}')
                            self._cprint(gid, self._format_msg(msg, show_headers=not args.no_headers))

                            if args.ack:
                                js.ack(msg)
                                self._cprint(gid, '(acknowledged)')

                            self._cprint(gid, '-' * 40)

                            if args.max_msgs and count >= args.max_msgs:
                                self._cprint(gid, f'Received {args.max_msgs} messages, exiting.')
                                return

                    except NATSTimeoutError:
                        continue

            except NATSNoRespondersError:
                self._cprint(gid, "Error: No responders available. Is JetStream enabled? Run 'nats-server -js'")
            except NATSJetStreamError:
                self._cprint(gid, f'JetStream error: {format_exc()}')
            except NATSError:
                self._cprint(gid, f'Error: {format_exc()}')

        g = spawn(js_sub_worker)
        self.greenlets.append((g, gid))
        subject = f'stream:{args.stream}'
        if args.filter_subject:
            subject += f' filter:{args.filter_subject}'
        self.greenlet_info[gid] = {'subject': subject, 'started': datetime.now()}
        self._cprint(gid, f'Started JetStream subscription greenlet for stream "{args.stream}"')

    # ############################################################################################################################

    def cmd_js_stream_create(self, args:'argparse.Namespace') -> 'None':
        """ Creates a JetStream stream.
        """
        try:
            client = self._get_writer_client(args)

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

        except NATSNoRespondersError:
            print("Error: No responders available. Is JetStream enabled? Run 'nats-server -js'", file=sys.stderr)
        except NATSJetStreamError:
            print(f'JetStream error: {format_exc()}', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_js_stream_delete(self, args:'argparse.Namespace') -> 'None':
        """ Deletes a JetStream stream.
        """
        try:
            if not args.force:
                confirm = input(f'Delete stream "{args.name}"? [y/N]: ')
                if confirm.lower() != 'y':
                    print('Cancelled')
                    return

            client = self._get_writer_client(args)
            js = client.jetstream()
            success = js.delete_stream(args.name, timeout=args.request_timeout)

            if success:
                print(f'Deleted stream "{args.name}"')
            else:
                print(f'Failed to delete stream "{args.name}"', file=sys.stderr)

        except NATSNoRespondersError:
            print("Error: No responders available. Is JetStream enabled? Run 'nats-server -js'", file=sys.stderr)
        except NATSJetStreamError:
            print(f'JetStream error: {format_exc()}', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_js_stream_info(self, args:'argparse.Namespace') -> 'None':
        """ Returns information about a JetStream stream.
        """
        try:
            client = self._get_writer_client(args)
            js = client.jetstream()
            info = js.stream_info(args.name, timeout=args.request_timeout)

            print(f'Stream: {info.config.name}')
            description = info.config.description if info.config.description else '(none)'
            print(f'  Description: {description}')
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

        except NATSNoRespondersError:
            print("Error: No responders available. Is JetStream enabled? Run 'nats-server -js'", file=sys.stderr)
        except NATSJetStreamError:
            print(f'JetStream error: {format_exc()}', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def cmd_js_stream_purge(self, args:'argparse.Namespace') -> 'None':
        """ Purges messages from a JetStream stream.
        """
        try:
            if not args.force:
                confirm = input(f'Purge all messages from stream "{args.name}"? [y/N]: ')
                if confirm.lower() != 'y':
                    print('Cancelled')
                    return

            client = self._get_writer_client(args)
            js = client.jetstream()
            purged = js.purge_stream(args.name, timeout=args.request_timeout)
            print(f'Purged {purged} messages from stream "{args.name}"')

        except NATSNoRespondersError:
            print("Error: No responders available. Is JetStream enabled? Run 'nats-server -js'", file=sys.stderr)
        except NATSJetStreamError:
            print(f'JetStream error: {format_exc()}', file=sys.stderr)
        except NATSError:
            print(f'Error: {format_exc()}', file=sys.stderr)

    # ############################################################################################################################

    def _completer(self, text:'str', state:'int') -> 'str | None':
        """ Tab completion for commands.
        """
        options = [cmd for cmd in self.commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    # ############################################################################################################################

    def interactive_loop(self) -> 'None':
        """ Runs an interactive command loop.
        """
        _ = readline.parse_and_bind('tab: complete')
        _ = readline.set_completer(self._completer)
        _ = readline.set_completer_delims(' ')
        _ = readline.set_auto_history(False)

        # Load history for this session, deduplicated
        if self.history_file.exists():
            seen = set()
            unique_lines = []
            with open(self.history_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line not in seen:
                        seen.add(line)
                        unique_lines.append(line)

            # Add unique lines to readline history
            for line in unique_lines:
                readline.add_history(line)

            # Rewrite file with deduplicated history
            with open(self.history_file, 'w') as f:
                for line in unique_lines:
                    f.write(line + '\n')

        print('NATS Client')
        print('Type "help" for available commands, "exit" or "quit" to exit.\n')

        last_command = ''
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_command = lines[-1].strip()

        while True:
            try:
                line = input('nats> ')
                line = line.strip()

                if not line:
                    continue

                # Add to history only if different from last command
                if line != last_command:
                    readline.add_history(line)
                    last_command = line

                    # Append to history file immediately
                    with open(self.history_file, 'a') as f:
                        _ = f.write(line + '\n')

                if line in ('exit', 'quit'):
                    self._cleanup_greenlets()
                    print('Bye.')
                    break

                if line == 'help':
                    self.parser.print_help()
                    print()
                    continue

                if line == 'greenlets':
                    self._list_greenlets()
                    continue

                try:
                    argv = shlex.split(line)
                except ValueError:
                    print(f'Error parsing command: {format_exc()}')
                    continue

                try:
                    args = self.parser.parse_args(argv)
                except SystemExit:
                    continue

                if args.command is None:
                    self.parser.print_help()
                    continue

                try:
                    args.func(args)
                    gsleep(0)  # Yield to greenlets
                except SystemExit:
                    pass

            except KeyboardInterrupt:
                self._cleanup_greenlets()
                print('\nBye.')
                break
            except EOFError:
                self._cleanup_greenlets()
                print('\nBye.')
                break

    # ############################################################################################################################

    def run(self) -> 'None':
        """ Main entry point.
        """
        args = self.parser.parse_args()

        if args.command is None:
            self.interactive_loop()
        else:
            args.func(args)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point for the CLI.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    cli = NATSCLI()
    cli.run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

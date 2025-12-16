# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import json
import readline
import shlex
import signal
import sys
from datetime import datetime

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
        'help', 'exit', 'quit',
    ]

    def __init__(self) -> None:
        self.running = True
        self.parser = self._build_parser()

    # ############################################################################################################################

    def _signal_handler(self, sig:'int', frame:'any_') -> 'None':
        self.running = False
        print('\nInterrupted')

    # ############################################################################################################################

    def _format_msg(self, msg:'Msg', show_headers:'bool'=True) -> 'str':
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
        client = NATSClient()

        try:
            client.connect(
                host=args.host,
                port=args.port,
                timeout=args.timeout,
                user=args.user,
                password=args.password,
                token=args.token,
                verbose=args.verbose,
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

    # ############################################################################################################################

    def cmd_sub(self, args:'argparse.Namespace') -> 'None':
        """ Subscribes to a subject and prints messages.
        """
        client = NATSClient()
        self.running = True

        _ = signal.signal(signal.SIGINT, self._signal_handler)
        _ = signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            client.connect(
                host=args.host,
                port=args.port,
                timeout=args.timeout,
                user=args.user,
                password=args.password,
                token=args.token,
                verbose=args.verbose,
            )

            sub = client.subscribe(args.subject, queue=args.queue or '')
            print(f'Subscribed to "{args.subject}"' + (f' (queue: {args.queue})' if args.queue else ''))
            print('Waiting for messages... (Ctrl+C to quit)\n')

            count = 0
            while self.running:
                try:
                    msg = sub.next_msg(timeout=1.0)
                    count += 1
                    print(f'[{datetime.now().isoformat()}] Message #{count}')
                    print(self._format_msg(msg, show_headers=not args.no_headers))
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

    # ############################################################################################################################

    def cmd_request(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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
            print(self._format_msg(msg, show_headers=not args.no_headers))

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

    # ############################################################################################################################

    def cmd_js_pub(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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

    # ############################################################################################################################

    def cmd_js_sub(self, args:'argparse.Namespace') -> 'None':
        """ Subscribes to a JetStream stream and prints messages.
        """
        client = NATSClient()
        self.running = True

        _ = signal.signal(signal.SIGINT, self._signal_handler)
        _ = signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            client.connect(
                host=args.host,
                port=args.port,
                timeout=args.timeout,
                user=args.user,
                password=args.password,
                token=args.token,
                verbose=args.verbose,
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
                _ = js.create_consumer(args.stream, consumer_config, timeout=args.request_timeout)
                print(f'Created consumer "{consumer_name}" on stream "{args.stream}"')
            except NATSJetStreamError as e:
                if e.err_code == Err_Consumer_Already_Exists:
                    print(f'Using existing consumer "{consumer_name}" on stream "{args.stream}"')
                else:
                    raise

            print('Waiting for messages... (Ctrl+C to quit)\n')

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
                        print(f'[{datetime.now().isoformat()}] Message #{count}')
                        print(self._format_msg(msg, show_headers=not args.no_headers))

                        if args.ack:
                            js.ack(msg)
                            print('(acknowledged)')

                        print('-' * 40)

                        if args.max_msgs and count >= args.max_msgs:
                            print(f'Received {args.max_msgs} messages, exiting.')
                            self.running = False
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

    # ############################################################################################################################

    def cmd_js_stream_create(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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

    # ############################################################################################################################

    def cmd_js_stream_delete(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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

    # ############################################################################################################################

    def cmd_js_stream_info(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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

    # ############################################################################################################################

    def cmd_js_stream_purge(self, args:'argparse.Namespace') -> 'None':
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
                verbose=args.verbose,
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
        _ = readline.set_completer(self._completer)
        _ = readline.parse_and_bind('tab: complete')
        _ = readline.set_auto_history(False)

        print('NATS Client')
        print('Type "help" for available commands, "exit" or "quit" to exit.\n')

        last_command = ''

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

                if line in ('exit', 'quit'):
                    print('Bye.')
                    break

                if line == 'help':
                    self.parser.print_help()
                    print()
                    continue

                try:
                    argv = shlex.split(line)
                except ValueError as e:
                    print(f'Error parsing command: {e}')
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
                except SystemExit:
                    pass

            except KeyboardInterrupt:
                print('\nBye.')
                break
            except EOFError:
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
    cli = NATSCLI()
    cli.run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

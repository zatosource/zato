# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import argparse
import logging
import os
import sys
import threading
from dataclasses import dataclass
from json import dumps
from logging import getLogger
from traceback import format_exc

# gevent
import gevent

# Zato
from zato.common.pubsub.server.rest import PubSubRESTServer, GunicornApplication
from zato.common.pubsub.util import get_broker_config, cleanup_broker_impl
from zato.common.util.api import as_bool, new_cid_cli

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydictnone

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

class GreenletFormatter(logging.Formatter):
    def format(self, record):
        # Get process info
        process_id = os.getpid()

        # Get thread info
        thread = threading.current_thread()
        thread_name = thread.name
        thread_id = thread.ident

        # Get greenlet info
        current_greenlet = gevent.getcurrent()
        greenlet_name = getattr(current_greenlet, 'name', 'Greenlet-0')
        greenlet_id = id(current_greenlet)

        # Add custom fields to record
        record.process_id = process_id
        record.thread_name = thread_name
        record.thread_id = thread_id
        record.greenlet_name = greenlet_name
        record.greenlet_id = greenlet_id

        return super().format(record)

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
if _needs_details:
    log_format += ' - Process: %(process_id)s, Thread: %(thread_name)s (id: %(thread_id)s), Greenlet name: %(greenlet_name)s, Greenlet id: %(greenlet_id)s'

logging.basicConfig(level=logging.INFO, format=log_format)

# Set the custom formatter on the root logger only if details are needed
root_logger = logging.getLogger()
if _needs_details and root_logger.handlers:
    formatter = GreenletFormatter(log_format)
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class OperationResult:
    """ Result of an operation.
    """
    is_ok: 'bool' = False
    message: 'str' = ''
    details: 'anydictnone' = None

# ################################################################################################################################
# ################################################################################################################################

def get_parser() -> 'argparse.ArgumentParser':
    """ Create and return the command line argument parser.
    """
    parser = argparse.ArgumentParser(description='Zato PubSub REST API Server')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Start server command
    start_parser = subparsers.add_parser('start', help='Start the PubSub REST API server')
    _ = start_parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    _ = start_parser.add_argument('--port', type=int, default=44556, help='Port to bind to')

    _ = start_parser.add_argument('--workers', type=int, default=1, help='Number of gunicorn workers')
    _ = start_parser.add_argument('--has_debug', action='store_true', help='Enable has_debug mode')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up AMQP bindings and queues')
    _ = cleanup_parser.add_argument('--has_debug', action='store_true', help='Enable has_debug mode')
    _ = cleanup_parser.add_argument('--management-port', type=int, default=15672, help='RabbitMQ management port')

    # List connections command
    connections_parser = subparsers.add_parser('list-connections', help='List and analyze RabbitMQ connections')
    _ = connections_parser.add_argument('--has_debug', action='store_true', help='Enable has_debug mode')
    _ = connections_parser.add_argument('--management-port', type=int, default=15672, help='RabbitMQ management port')
    _ = connections_parser.add_argument('--output', type=str, default='json', choices=['json', 'pretty'], help='Output format')


    # Enmasse command
    enmasse_parser = subparsers.add_parser('enmasse', help='Run enmasse import with demo configuration')
    _ = enmasse_parser.add_argument('--has_debug', action='store_true', help='Enable debug mode')

    return parser

# ################################################################################################################################

def start_server(args:'argparse.Namespace') -> 'OperationResult':
    """ Start the PubSub REST API server.
    """
    try:
        # Create server application
        app = PubSubRESTServer(
            host=args.host,
            port=args.port,
        )

        # Configure gunicorn options
        options = {
            'bind': f'{args.host}:{args.port}',
            'workers': args.workers,
            'worker_class': 'gevent',
            'timeout': 30,
            'keepalive': 2,
            'loglevel': 'has_debug' if args.has_debug else 'info',
            'proc_name': 'zato-pubsub-rest',
            'preload_app': True,
        }

        # Start gunicorn application
        logger.info(f'Starting PubSub REST API server on {args.host}:{args.port}')
        worker_text = 'worker' if args.workers == 1 else 'workers'
        logger.info(f'Using {args.workers} {worker_text}')

        # Run the gunicorn application
        GunicornApplication(app, options).run()

        return OperationResult(is_ok=True, message='Server stopped')
    except Exception as e:
        message = f'Error starting server: {format_exc()}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def cleanup_broker(args:'argparse.Namespace') -> 'OperationResult':
    """ Clean up AMQP bindings and queues.
    """
    try:
        # Get broker configuration
        broker_config = get_broker_config()

        # Call the implementation function
        result = cleanup_broker_impl(broker_config, args.management_port)

        if result['errors']:
            error_message = f"Cleanup completed with errors: {'; '.join(result['errors'])}"
            logger.error(error_message)
            return OperationResult(is_ok=False, message=error_message)
        else:
            success_message = f"Cleanup completed successfully. Removed {result['queues_removed']} queues and {result['bindings_removed']} bindings."
            logger.info(success_message)
            return OperationResult(is_ok=True, message=success_message)

    except Exception as e:
        message = f'Error during cleanup: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message)

# ################################################################################################################################

def list_connections(args:'argparse.Namespace') -> 'OperationResult':
    """ List and analyze RabbitMQ connections.
    """
    try:

        cid = new_cid_cli()
        logger.info(f'[{cid}] Listing RabbitMQ connections')

        # Create a temporary server instance to use its list_connections method
        server = PubSubRESTServer(host='0.0.0.0', port=44556)

        # Get connection information
        result = server.list_connections(cid, args.management_port)

        # Format and print the output
        if args.output == 'pretty':
            print('\nRabbitMQ Connection Analysis:')
            print(f'Total connections: {result['total_connections']}')

            print('\nConnection Types:')
            for conn_type, count in result['connection_types'].items():
                print(f'  - {conn_type}: {count}')

            print('\nConsumers per Queue:')
            for queue, count in result['consumers_per_queue'].items():
                print(f'  - {queue}: {count}')

            print('\nBackend Subscription Keys:')
            for key in result['backend_sub_keys']:
                print(f'  - {key}')
        else:
            print(dumps(result, indent=2))

        return OperationResult(is_ok=True, message='Connection analysis completed successfully')

    except Exception as e:
        message = f'Error analyzing connections: {e}'
        logger.error(message)
        logger.error(format_exc())
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the CLI.
    Returns an integer exit code - 0 for success, non-zero for failure.
    """
    parser = get_parser()
    args = parser.parse_args()

    # Handle commands
    if args.command == 'start':
        result = start_server(args)
        return 0 if result.is_ok else 1

    elif args.command == 'cleanup':
        result = cleanup_broker(args)
        return 0 if result.is_ok else 1

    elif args.command == 'list-connections':
        result = list_connections(args)
        return 0 if result.is_ok else 1

    elif args.command == 'enmasse':
        from zato.common.pubsub.cli_enmasse import run_enmasse_command
        return run_enmasse_command(args)

    else:
        parser.print_help()
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

"""
# Health check endpoint:
curl http://localhost:44556/pubsub/health; echo

echo '{"data":"Hello World"}' > post_data.json
ab -n 100000 -c 100 -p post_data.json -T 'application/json' -A 'demo:demo' http://localhost:44556/pubsub/topic/demo.1

# Publish a message to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/topic/demo.1 -d '{"data":"Hello World"}'; echo

echo '{"data":"Hello World"}' > /tmp/payload.json && ab -n ${1:-200000} -c 100 -A demo:demo -T "application/json" -p /tmp/payload.json http://localhost:44556/pubsub/topic/demo.1
N=${1:-100}; for ((i=1; i<=$N; i++)); do curl -s -u demo:demo -X POST http://localhost:44556/pubsub/topic/demo.1 -d '{"data":"Hello World"}' >/dev/null; printf "\rProgress: %d/%d" $i $N; done; echo

# Subscribe to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/subscribe/topic/demo.1; echo

# Unsubscribe from a topic:
curl -u demo:demo -X DELETE http://localhost:44556/pubsub/subscribe/topic/demo.1

# Get admin diagnostics (logs topics, users, subscriptions etc.):
curl -u demo:demo -X GET http://localhost:44556/pubsub/admin/diagnostics; echo

curl -u demo:demo -X POST http://localhost:44556/pubsub/subscribe/topic/demo.1; echo
curl -u demo:demo -X POST http://localhost:44556/pubsub/topic/demo.1 -H "Content-Type: application/json" -d '{"data": "First message", "priority": 15, expiration: 25000}'; echo
curl -u demo:demo -X POST http://localhost:44556/pubsub/topic/demo.1 -H "Content-Type: application/json" -d '{"data": "Second message", "priority": 5}'; echo
curl -u demo:demo -X POST http://localhost:44556/pubsub/messages/get -H "Content-Type: application/json" -d '{"max_messages": 10, "max_len": 1000000}'; echo
curl -u demo:demo -X POST http://localhost:44556/pubsub/unsubscribe/topic/demo.1; echo
"""

# ################################################################################################################################
# ################################################################################################################################

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
import time
from dataclasses import dataclass
from json import dumps
from logging import getLogger
from traceback import format_exc

# gevent
import gevent

# gunicorn
from gunicorn.app.base import BaseApplication

# prometheus
from prometheus_client import Histogram

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.server.rest_publish import PubSubRESTServerPublish
from zato.common.pubsub.server.rest_pull import PubSubRESTServerPull
from zato.common.pubsub.util import get_broker_config, cleanup_broker_impl
from zato.common.util.api import as_bool, new_cid_cli

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydictnone, dictnone
    from zato.common.pubsub.server.rest_base import PubSubRESTServer

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))
_default_port_publish = PubSub.REST_Server.Default_Port_Publish
_default_port_pull = PubSub.REST_Server.Default_Port_Get

# Metrics
gunicorn_request_time = Histogram('zato_pubsub_gunicorn_request_seconds', 'Gunicorn request processing time')

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

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process_id)s:%(thread_name)s:%(greenlet_name)s - %(name)s:%(lineno)d - %(message)s'
if _needs_details:
    log_format += ', Greenlet id: %(greenlet_id)s'

logging.basicConfig(level=logging.INFO, format=log_format)

# Set the custom formatter on the root logger
root_logger = logging.getLogger()
if root_logger.handlers:
    formatter = GreenletFormatter(log_format)
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GunicornApplication(BaseApplication):
    """ Gunicorn application wrapper for the PubSub REST API.
    """
    def __init__(self, app:'PubSubRESTServer', options:'dictnone'=None):
        self.options = options or {}
        self.options.setdefault('post_fork', self.on_post_fork)
        self.application = app
        super().__init__()

    def load_config(self):
        # Apply valid configuration options
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None: # type: ignore
                self.cfg.set(key.lower(), value) # type: ignore

        # We need to set this one explicitly because otherwise gunicorn insists it be an int (min=1)
        object.__setattr__(self.cfg, 'graceful_timeout', 0.05)

    def load(self):
        return self.application

    def on_post_fork(self, server, worker):
        address = self.cfg.address[0] # type: ignore
        host, port = address[0], address[1] # type: ignore
        address_str = f'{host}:{port}'
        logger.info(f'Setting up PubSub REST server at {address_str}')


        self.application.init_broker_client()
        self.application.setup()

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
    _ = start_parser.add_argument('--host', default=PubSub.REST_Server.Default_Host, help='Host to bind to')
    _ = start_parser.add_argument('--port', type=int, help='Port to bind to (defaults: 40100 for publish, 40200 for pull)')
    _ = start_parser.add_argument('--workers', type=int, default=PubSub.REST_Server.Default_Threads, help='Number of worker processes')
    _ = start_parser.add_argument('--has-debug', action='store_true', help='Enable debug logging')

    server_type_group = start_parser.add_mutually_exclusive_group(required=True)

    _ = server_type_group.add_argument('--publish', action='store_true', help='Start server in publish mode')
    _ = server_type_group.add_argument('--pull', action='store_true', help='Start server in pull mode')

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
        # Set default port based on server type
        if args.publish:
            default_port = _default_port_publish
            server_type = 'Publish'
            proc_type = 'publish'
        else:
            default_port = _default_port_pull
            server_type = 'Pull'
            proc_type = 'pull'

        # Use provided port or default
        port = args.port if args.port else default_port

        # Pin process to specific CPU core
        available_cores = os.sched_getaffinity(0)
        max_core = max(available_cores)

        if args.publish:
            os.sched_setaffinity(0, {max_core - 1})
        else:
            os.sched_setaffinity(0, {max_core})

        # Create server application based on mode
        if args.publish:
            app = PubSubRESTServerPublish(
                host=args.host,
                port=port,
            )
        else:
            app = PubSubRESTServerPull(
                host=args.host,
                port=port,
            )

        # Wrap app with timing middleware
        def timing_middleware(app):
            def middleware(environ, start_response):
                start_time = time.time()
                try:
                    result = app(environ, start_response)
                    return result
                finally:
                    duration = time.time() - start_time
                    gunicorn_request_time.observe(duration)
            return middleware

        wrapped_app = timing_middleware(app)

        # Configure gunicorn options
        options = {
            'bind': f'{args.host}:{port}',
            'workers': args.workers,
            'worker_class': 'sync',
            'timeout': 30,
            'keepalive': 2,
            'loglevel': 'has_debug' if args.has_debug else 'info',
            'proc_name': f'zato-pubsub-rest-{proc_type}',
            'preload_app': False,
            'max_requests': 0,
            'worker_connections': 20000,
            'backlog': 20000,
        }

        # Start gunicorn application
        logger.info(f'Starting PubSub REST API {server_type} server on {args.host}:{port}')
        worker_text = 'worker' if args.workers == 1 else 'workers'
        logger.info(f'Using {args.workers} {worker_text}')

        # Run the gunicorn application
        gunicorn_app = GunicornApplication(wrapped_app, options)
        gunicorn_app.run()

        return OperationResult(is_ok=True, message='Server stopped')
    except KeyboardInterrupt:
        logger.info('Server stopped by user')
        return OperationResult(is_ok=True, message='Server stopped by user')
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
        server = PubSubRESTServerPublish(host='0.0.0.0', port=_default_port_publish)

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

f"""
# Health check endpoint:
curl http://localhost:40100/pubsub/health; echo

echo '{"data":"Hello World"}' > post_data.json
ab -n 100000 -c 100 -p post_data.json -T 'application/json' -A 'demo:demo' http://localhost:40100/pubsub/topic/demo.1

# Publish a message to a topic:
curl -u demo:demo -X POST http://localhost:40100/pubsub/topic/demo.1 -d '{"data":"Hello World"}'; echo

echo '{"data":"Hello World"}' > /tmp/payload.json && ab -n ${1:-200000} -c 100 -A demo:demo -T "application/json" -p /tmp/payload.json http://localhost:40100/pubsub/topic/demo.1
N=${1:-100}; for ((i=1; i<=$N; i++)); do curl -s -u demo:demo -X POST http://localhost:40100/pubsub/topic/demo.1 -d '{"data":"Hello World"}' >/dev/null; printf "\rProgress: %d/%d" $i $N; done; echo

curl -u demo:demo -X POST http://localhost:40100/pubsub/subscribe/topic/demo.1; echo

curl -u demo:demo -X DELETE http://localhost:40100/pubsub/subscribe/topic/demo.1

# Get admin diagnostics (logs topics, users, subscriptions etc.):
curl -u demo:demo -X GET http://localhost:40100/pubsub/admin/diagnostics; echo

# Get messages from queue:
curl -u demo:demo -X POST http://localhost:40200/pubsub/messages/get -d '{"max_messages": 10, "max_len": 1000000}'; echo
curl -u demo:demo -X POST http://localhost:40200/pubsub/messages/get -d '{"max_messages": 10}'; echo

curl -u demo:demo -X POST http://localhost:40100/pubsub/subscribe/topic/demo.1; echo
curl -u demo:demo -X POST http://localhost:40100/pubsub/topic/demo.1 -d '{"data": "First message", "priority": 7, "expiration": 250000000}'; echo
curl -u demo:demo -X POST http://localhost:40100/pubsub/topic/demo.1 -d '{"data": "Second message", "priority": 5}'; echo
curl -u demo:demo -X POST http://localhost:40200/pubsub/messages/get -d '{"max_messages": 10}'; echo
curl -u demo:demo -X POST http://localhost:40100/pubsub/unsubscribe/topic/demo.1; echo
"""

# ################################################################################################################################
# ################################################################################################################################

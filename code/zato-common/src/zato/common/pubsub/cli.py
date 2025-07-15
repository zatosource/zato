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
import requests
from dataclasses import dataclass
from json import dumps
from logging import basicConfig, DEBUG, getLogger, INFO
from traceback import format_exc
from urllib.parse import quote

# Zato
from zato.common.pubsub.backend import Backend
from zato.common.pubsub.server import PubSubRESTServer, GunicornApplication
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydictnone

# ################################################################################################################################
# ################################################################################################################################

# Setup basic logging
basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(process)s:%(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = getLogger(__name__)

# Default paths
DEFAULT_YAML_CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'users.yaml'
)

# ################################################################################################################################
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
    _ = start_parser.add_argument('--yaml-config', type=str, default=DEFAULT_YAML_CONFIG,
                                help='Path to YAML configuration file with users, topics, and subscriptions')
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
    _ = connections_parser.add_argument('--yaml-config', type=str, default=DEFAULT_YAML_CONFIG,
                                    help='Path to YAML configuration file with users, topics, and subscriptions')

    return parser

# ################################################################################################################################

def start_server(args:'argparse.Namespace') -> 'OperationResult':
    """ Start the PubSub REST API server.
    """
    try:
        # Set up logging level
        level = DEBUG if args.has_debug else INFO
        basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )

        # Create server application
        app = PubSubRESTServer(
            host=args.host,
            port=args.port,
            yaml_config_file=args.yaml_config,
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
        message = f'Error starting server: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def cleanup_broker(args:'argparse.Namespace') -> 'OperationResult':
    """ Clean up AMQP bindings and queues.
    """
    try:
        # Set up logging level
        level = DEBUG if args.has_debug else INFO
        basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )

        # Get broker configuration
        broker_config = get_broker_config()

        # Extract host from address (remove port if present)
        host = broker_config.address.split(':')[0] if ':' in broker_config.address else broker_config.address
        management_port = args.management_port

        # URL encode the vhost
        encoded_vhost = quote(broker_config.vhost, safe='')

        # Build HTTP API base URL
        api_base_url = f'http://{host}:{management_port}/api'
        auth = (broker_config.username, broker_config.password)

        logger.info(f'Connecting to RabbitMQ API at: {api_base_url}')

        # Find and remove all queues with specified prefixes
        try:
            # Define the prefixes to clean up
            prefixes = ['zpsk', 'zato-reply-']

            # Get all queues
            logger.info(f'Listing queues with prefixes: {prefixes}')
            queues_url = f'{api_base_url}/queues/{encoded_vhost}'
            response = requests.get(queues_url, auth=auth)

            if response.status_code == 200:
                all_queues = response.json()

                # Process each prefix
                for prefix in prefixes:
                    matching_queues = [queue for queue in all_queues if queue['name'].startswith(prefix)]
                    queue_count = len(matching_queues)
                    if queue_count == 1:
                        logger.info(f'Found 1 queue with prefix {prefix}')
                    else:
                        logger.info(f'Found {queue_count} queues with prefix {prefix}')

                    # Delete each matching queue
                    for queue in matching_queues:
                        queue_name = queue['name']
                        logger.info(f'Removing queue: {queue_name}')

                        # Delete the queue - empty all arguments to force deletion
                        queue_url = f'{api_base_url}/queues/{encoded_vhost}/{queue_name}'
                        delete_response = requests.delete(
                            queue_url,
                            auth=auth,
                            params={'if-unused': 'false', 'if-empty': 'false'}
                        )

                        if delete_response.status_code in (200, 204):
                            logger.info(f'Successfully removed queue: {queue_name}')
                        else:
                            logger.error(f'Failed to remove queue: {delete_response.status_code}, {delete_response.text}')
            else:
                logger.error(f'Failed to list queues: {response.status_code}, {response.text}')

        except Exception as e:
            logger.error(f'Error removing queues: {e}')

        # List all bindings from pubsubapi exchange
        try:
            logger.info('Listing bindings from pubsubapi exchange')
            bindings_url = f'{api_base_url}/exchanges/{encoded_vhost}/pubsubapi/bindings/source'
            response = requests.get(bindings_url, auth=auth)

            if response.status_code == 200:
                bindings = response.json()
                binding_count = len(bindings)
                if binding_count == 1:
                    logger.info('Found 1 binding for pubsubapi exchange')
                else:
                    logger.info(f'Found {binding_count} bindings for pubsubapi exchange')

                # Remove all bindings from pubsubapi exchange
                for binding in bindings:
                    queue_name = binding.get('destination')

                    # Only process if the destination is a queue
                    if binding.get('destination_type') == 'queue':

                        routing_key = binding.get('routing_key', '')
                        logger.info(f'Removing binding: queue={queue_name}, routing_key={routing_key} from exchange=pubsubapi')

                        # Delete the binding
                        unbind_url = f'{api_base_url}/bindings/{encoded_vhost}/e/pubsubapi/q/{queue_name}/{quote(routing_key, safe="")}'
                        delete_response = requests.delete(unbind_url, auth=auth)

                        if delete_response.status_code in (200, 204):
                            logger.info(f'Successfully removed binding for queue: {queue_name}')
                        else:
                            logger.error(f'Failed to remove binding: {delete_response.status_code}, {delete_response.text}')
            else:
                logger.error(f'Failed to list bindings: {response.status_code}, {response.text}')

        except Exception as e:
            logger.error(f'Error removing bindings: {e}')

        return OperationResult(is_ok=True, message='Cleanup completed successfully')

    except Exception as e:
        message = f'Error during cleanup: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def list_connections(args:'argparse.Namespace') -> 'OperationResult':
    """ List and analyze RabbitMQ connections.
    """
    try:
        # Set up logging level
        level = DEBUG if args.has_debug else INFO
        basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(process)s:%(threadName)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )

        cid = new_cid()
        logger.info(f'[{cid}] Listing RabbitMQ connections')

        # Create a temporary server instance to use its list_connections method
        server = PubSubRESTServer(host='0.0.0.0', port=44556, yaml_config_file=args.yaml_config)

        # We need to initialize the backend but don't need to run the full setup
        # server.backend = Backend() # type: ignore

        # Get connection information
        result = server.list_connections(cid, args.management_port)

        # Format and print the output
        if args.output == 'pretty':
            print('\nRabbitMQ Connection Analysis:')
            print(f"Total connections: {result['total_connections']}")

            print('\nConnection Types:')
            for conn_type, count in result['connection_types'].items():
                print(f"  - {conn_type}: {count}")

            print('\nConsumers per Queue:')
            for queue, count in result['consumers_per_queue'].items():
                print(f"  - {queue}: {count}")

            print('\nBackend Subscription Keys:')
            for key in result['backend_sub_keys']:
                print(f"  - {key}")
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
ab -n 100000 -c 100 -p post_data.json -T 'application/json' -A 'demo:demo' http://localhost:44556/pubsub/topic/my.topic

# Publish a message to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/topic/my.topic -d '{"data":"Hello World"}'; echo

echo '{"data":"Hello World"}' > /tmp/payload.json && ab -n ${1:-200000} -c 100 -A demo:demo -T "application/json" -p /tmp/payload.json http://localhost:44556/pubsub/topic/my.topic
N=${1:-100}; for ((i=1; i<=$N; i++)); do curl -s -u demo:demo -X POST http://localhost:44556/pubsub/topic/my.topic -d '{"data":"Hello World"}' >/dev/null; printf "\rProgress: %d/%d" $i $N; done; echo

# Subscribe to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/subscribe/topic/my.topic; echo

# Unsubscribe from a topic:
curl -u demo:demo -X DELETE http://localhost:44556/pubsub/subscribe/topic/my.topic

# Get admin diagnostics (logs topics, users, subscriptions etc.):
curl -u demo:demo -X GET http://localhost:44556/pubsub/admin/diagnostics; echo
"""

# ################################################################################################################################
# ################################################################################################################################

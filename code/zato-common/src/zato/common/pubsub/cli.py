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
import json
import logging
import os
import sys
import requests
from dataclasses import dataclass
from logging import basicConfig, DEBUG, getLogger, INFO
from urllib.parse import quote

# Zato
from zato.common.pubsub.server import PubSubRESTServer, GunicornApplication
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, str_

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
DEFAULT_USERS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'users.json'
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(frozen=True)
class UserInfo:
    """ Information about a user.
    """
    username: 'str'

    def __hash__(self) -> 'int':
        """ Make this class hashable for use in sets.
        """
        return hash(self.username)

    def __eq__(self, other:'str') -> 'bool':
        """ Define equality based on username.
        """
        if not isinstance(other, UserInfo):
            return False
        return self.username == other.username

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
    _ = start_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')
    _ = start_parser.add_argument('--workers', type=int, default=1, help='Number of gunicorn workers')
    _ = start_parser.add_argument('--has_debug', action='store_true', help='Enable has_debug mode')

    # List users command
    list_users_parser = subparsers.add_parser('list-users', help='List users from users JSON file')
    _ = list_users_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')

    # Create user command
    create_user_parser = subparsers.add_parser('create-user', help='Create a new user')
    _ = create_user_parser.add_argument('--username', type=str, required=True, help='Username')
    _ = create_user_parser.add_argument('--password', type=str, required=True, help='Password')
    _ = create_user_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up AMQP bindings and queues')
    _ = cleanup_parser.add_argument('--has_debug', action='store_true', help='Enable has_debug mode')
    _ = cleanup_parser.add_argument('--management-port', type=int, default=15672, help='RabbitMQ management port')

    return parser

# ################################################################################################################################

def validate_users_file(users_file:'str_') -> 'OperationResult':
    """ Validate that the users file exists and is readable.
    """
    if not os.path.exists(users_file):
        message = f'Users file {users_file} does not exist'
        logger.error(message)
        return OperationResult(is_ok=False, message=message)

    if not os.path.isfile(users_file):
        message = f'Users file {users_file} is not a file'
        logger.error(message)
        return OperationResult(is_ok=False, message=message)

    try:
        with open(users_file, 'r') as f:
            json.load(f)
        return OperationResult(is_ok=True, message='Users file is valid')
    except Exception as e:
        message = f'Error reading users file {users_file}: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def list_users(args:'argparse.Namespace') -> 'any_':
    """ List users from the specified users file.
    """
    validation_result = validate_users_file(args.users_file)
    if not validation_result.is_ok:
        return validation_result

    try:
        with open(args.users_file, 'r') as f:
            users_list = json.load(f)

        logger.info(f'Users in {args.users_file}:')
        users = []
        for user_dict in users_list:
            for username in user_dict:
                logger.info(f'  - {username}')
                users.append(UserInfo(username=username))

        return users
    except Exception as e:
        message = f'Error listing users: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def create_user(args:'argparse.Namespace') -> 'OperationResult':
    """ Create a new user in the specified users file.
    """
    users_file = args.users_file
    username = args.username
    password = args.password

    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(users_file), exist_ok=True)

    # Read existing users or create empty list
    try:
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users_list = json.load(f)
        else:
            users_list = []

        # Check if user already exists
        for user_dict in users_list:
            if username in user_dict:
                message = f'User {username} already exists'
                logger.error(message)
                return OperationResult(is_ok=False, message=message)

        # Add new user
        _ = users_list.append({username: password})

        # Write updated users file
        with open(users_file, 'w') as f:
            json.dump(users_list, f, indent=2)

        message = f'User {username} created successfully'
        logger.info(message)
        return OperationResult(is_ok=True, message=message)
    except Exception as e:
        message = f'Error creating user: {e}'
        logger.error(message)
        return OperationResult(is_ok=False, message=message, details={'error': str(e)})

# ################################################################################################################################

def start_server(args:'argparse.Namespace') -> 'OperationResult':
    """ Start the PubSub REST API server.
    """
    validation_result = validate_users_file(args.users_file)
    if not validation_result.is_ok:
        return validation_result

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
            users_file=args.users_file,
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

        return OperationResult(is_ok=True, message='Cleanup completed successfully')

    except Exception as e:
        message = f'Error during cleanup: {e}'
        logger.error(message)
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

    elif args.command == 'list-users':

        result = list_users(args)

        # If we got a list of users, it was successful
        if isinstance(result, list):
            return 0

        # Otherwise it's an OperationResult indicating failure
        return 0 if result.is_ok else 1

    elif args.command == 'create-user':
        result = create_user(args)
        return 0 if result.is_ok else 1

    elif args.command == 'cleanup':
        result = cleanup_broker(args)
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

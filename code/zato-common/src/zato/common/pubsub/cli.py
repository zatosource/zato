# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from logging import basicConfig, DEBUG, getLogger, INFO

# Zato
from zato.common.pubsub.server import PubSubRESTServer, GunicornApplication

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, str_

# ################################################################################################################################
# ################################################################################################################################

# Setup basic logging
basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
            has_debug=args.has_debug
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

# Publish a message to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/topic/my.topic -d '{"data":"Hello World"}'; echo

echo '{"data":"Hello World"}' > /tmp/payload.json && ab -n ${1:-200000} -c 100 -A demo:demo -T "application/json" -p /tmp/payload.json http://localhost:44556/pubsub/topic/my.topic
N=${1:-100}; for ((i=1; i<=$N; i++)); do curl -s -u demo:demo -X POST http://localhost:44556/pubsub/topic/my.topic -d '{"data":"Hello World"}' >/dev/null; printf "\rProgress: %d/%d" $i $N; done; echo

# Subscribe to a topic:
curl -u demo:demo -X POST http://localhost:44556/pubsub/subscribe/topic/my.topic; echo

# Unsubscribe from a topic:
curl -u demo:demo -X DELETE http://localhost:44556/pubsub/subscribe/topic/my.topic
"""

# ################################################################################################################################
# ################################################################################################################################

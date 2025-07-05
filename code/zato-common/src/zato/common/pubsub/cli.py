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
from logging import basicConfig, getLogger, INFO, DEBUG
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# gunicorn
from gunicorn.config import Config

# Zato
from zato.common.pubsub.server import PubSubRESTServer, GunicornApplication

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

def get_parser() -> 'argparse.ArgumentParser':
    """ Create and return the command line argument parser.
    """
    parser = argparse.ArgumentParser(description='Zato PubSub REST API Server')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Start server command
    start_parser = subparsers.add_parser('start', help='Start the PubSub REST API server')
    start_parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    start_parser.add_argument('--port', type=int, default=44556, help='Port to bind to')
    start_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')
    start_parser.add_argument('--workers', type=int, default=1, help='Number of gunicorn workers')
    start_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # List users command
    list_users_parser = subparsers.add_parser('list-users', help='List users from users JSON file')
    list_users_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')
    
    # Create user command
    create_user_parser = subparsers.add_parser('create-user', help='Create a new user')
    create_user_parser.add_argument('--username', type=str, required=True, help='Username')
    create_user_parser.add_argument('--password', type=str, required=True, help='Password')
    create_user_parser.add_argument('--users-file', type=str, default=DEFAULT_USERS_FILE, help='Path to users JSON file')
    
    return parser

# ################################################################################################################################

def validate_users_file(users_file:'str') -> 'bool':
    """ Validate that the users file exists and is readable.
    """
    if not os.path.exists(users_file):
        logger.error(f'Users file {users_file} does not exist')
        return False
        
    if not os.path.isfile(users_file):
        logger.error(f'Users file {users_file} is not a file')
        return False
        
    try:
        with open(users_file, 'r') as f:
            json.load(f)
        return True
    except Exception as e:
        logger.error(f'Error reading users file {users_file}: {e}')
        return False

# ################################################################################################################################

def list_users(args:'argparse.Namespace') -> 'int':
    """ List users from the specified users file.
    """
    if not validate_users_file(args.users_file):
        return 1
        
    try:
        with open(args.users_file, 'r') as f:
            users_list = json.load(f)
            
        logger.info(f'Users in {args.users_file}:')
        for user_dict in users_list:
            for username, _ in user_dict.items():
                logger.info(f'  - {username}')
                
        return 0
    except Exception as e:
        logger.error(f'Error listing users: {e}')
        return 1

# ################################################################################################################################

def create_user(args:'argparse.Namespace') -> 'int':
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
                logger.error(f'User {username} already exists')
                return 1
                
        # Add new user
        users_list.append({username: password})
        
        # Write updated users file
        with open(users_file, 'w') as f:
            json.dump(users_list, f, indent=2)
            
        logger.info(f'User {username} created successfully')
        return 0
    except Exception as e:
        logger.error(f'Error creating user: {e}')
        return 1

# ################################################################################################################################

def start_server(args:'argparse.Namespace') -> 'int':
    """ Start the PubSub REST API server.
    """
    if not validate_users_file(args.users_file):
        return 1
        
    try:
        # Set up logging level
        level = DEBUG if args.debug else INFO
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
            debug=args.debug
        )
        
        # Configure gunicorn options
        options = {
            'bind': f'{args.host}:{args.port}',
            'workers': args.workers,
            'worker_class': 'gevent',
            'timeout': 30,
            'keepalive': 2,
            'loglevel': 'debug' if args.debug else 'info',
            'proc_name': 'zato-pubsub-rest',
            'preload_app': True,
        }
        
        # Start gunicorn application
        logger.info(f'Starting PubSub REST API server on {args.host}:{args.port}')
        logger.info(f'Using {args.workers} worker(s)')
        
        # Run the gunicorn application
        GunicornApplication(app, options).run()
        
        return 0
    except Exception as e:
        logger.error(f'Error starting server: {e}')
        return 1

# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the CLI.
    """
    parser = get_parser()
    args = parser.parse_args()
    
    if args.command == 'start':
        return start_server(args)
    elif args.command == 'list-users':
        return list_users(args)
    elif args.command == 'create-user':
        return create_user(args)
    else:
        parser.print_help()
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################

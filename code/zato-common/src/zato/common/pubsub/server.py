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
import signal
from typing import Dict

# gevent
from gevent import sleep

# Zato
from zato.broker.client import BrokerClient
from zato.common.pubsub.common import BrokerConfig
from zato.common.pubsub.models import MessageData
from zato.common.pubsub.rest_api import RESTAPIServer
from zato.common.pubsub.subscription import SubscriptionManager
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('zato.pubsub.rest')

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServer:
    """ Main class for the PubSub REST API server that integrates with Zato's broker client.
    """
    
    def __init__(self, host='0.0.0.0', port=8080, users=None):
        self.host = host
        self.port = port
        self.users = users or {}
        self.broker_config = get_broker_config()
        self.broker_client = None
        self.rest_api = None
        self.running = False
        
        logger.info('PubSub REST Server initialized')
        
    def _init_broker_client(self):
        """ Initialize the broker client for AMQP communication.
        """
        try:
            logger.info(f'Connecting to broker at {self.broker_config.address}')
            # BrokerClient gets broker_config internally via get_broker_config()
            self.broker_client = BrokerClient(
                server=None,  # No server object in this context
                context=self,  # Use self as the context for callbacks
                queue_name='pubsub-rest-api'  # Queue name for this component
            )
            return True
        except Exception as e:
            logger.error(f'Failed to initialize broker client: {e}', exc_info=True)
            return False
            
    def _publish_to_amqp(self, topic_name, message_data):
        """ Publish a message to AMQP using the broker client.
        """
        try:
            if not self.broker_client:
                if not self._init_broker_client():
                    return False
                    
            # Convert MessageData to a format suitable for BrokerClient
            message = {
                'msg_id': message_data.msg_id,
                'topic_name': topic_name,
                'data': message_data.data,
                'mime_type': message_data.mime_type,
                'priority': message_data.priority,
                'expiration': message_data.expiration,
                'correl_id': message_data.correl_id,
                'in_reply_to': message_data.in_reply_to,
            }
            
            # Publish through broker client
            self.broker_client.publish(message)
            logger.info(f'Message {message_data.msg_id} published to AMQP topic {topic_name}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to publish message to AMQP: {e}', exc_info=True)
            return False
            
    def start(self):
        """ Start the PubSub REST API server.
        """
        # Initialize the broker client if needed
        if not self.broker_client:
            self._init_broker_client()
            
        # Initialize the REST API server with the broker client
        self.rest_api = RESTAPIServer(
            host=self.host, 
            port=self.port, 
            users=self.users,
            broker_client=self.broker_client  # Pass the broker client directly
        )
        
        # Start the REST API server
        self.rest_api.start()
        self.running = True
        
        logger.info(f'PubSub REST API server started on {self.host}:{self.port}')
        
    def stop(self):
        """ Stop the PubSub REST API server.
        """
        if self.rest_api:
            self.rest_api.stop()
            
        if self.broker_client:
            self.broker_client.close()
            
        self.running = False
        logger.info('PubSub REST API server stopped')

# ################################################################################################################################
# ################################################################################################################################

def load_users_from_file(file_path):
    """ Load users from a JSON file.
    Format: {"username": "password", ...}
    """
    try:
        with open(file_path, 'r') as f:
            users = json.load(f)
        logger.info(f'Loaded {len(users)} users from {file_path}')
        return users
    except Exception as e:
        logger.error(f'Failed to load users from {file_path}: {e}')
        return {}

# ################################################################################################################################

def main():
    """ Main entry point for the PubSub REST API server.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Zato PubSub REST API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--users-file', help='Path to JSON file with username:password mappings')
    parser.add_argument('--log-level', default='INFO', help='Logging level (default: INFO)')
    args = parser.parse_args()
    
    # Configure logging level
    logging.getLogger('zato').setLevel(getattr(logging, args.log_level.upper()))
    
    # Load users if specified
    users = {}
    if args.users_file:
        users = load_users_from_file(args.users_file)
    
    # Create and start the server
    server = PubSubRESTServer(args.host, args.port, users)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info('Received shutdown signal, stopping server...')
        server.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the server
        server.start()
        
        # Keep the main thread running
        while server.running:
            sleep(1)
            
    except Exception as e:
        logger.error(f'Error in main loop: {e}', exc_info=True)
        server.stop()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

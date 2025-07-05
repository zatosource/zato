# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from dataclasses import asdict
from json import dumps, loads
from logging import getLogger
from typing import Any, Dict, List, Tuple, Optional, Union

# gevent
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized, BadRequest, MethodNotAllowed
from werkzeug.middleware.proxy_fix import ProxyFix

# gunicorn
from gunicorn.app.base import BaseApplication

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import new_cid
from zato.common.pubsub.models import PubMessage, PubResponse, Message, MessagesResponse, SimpleResponse, User
from zato.common.pubsub.models import Subscription, Topic, subscription_list, message_list, topic_list
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Constants for message ID generation
MSG_ID_PREFIX = 'zpsm'
SUB_KEY_PREFIX = 'zpsk.rest'

# Default configuration values
DEFAULT_PORT = 44556
DEFAULT_HOST = '0.0.0.0'
DEFAULT_WORKERS = 1

# ################################################################################################################################
# ################################################################################################################################

def generate_msg_id() -> 'str':
    """ Generate a unique message ID with prefix.
    """
    return f'{MSG_ID_PREFIX}{uuid.uuid4().hex[:24]}'

# ################################################################################################################################

def generate_sub_key() -> 'str':
    """ Generate a unique subscription key with prefix.
    """
    return f'{SUB_KEY_PREFIX}.{uuid.uuid4().hex[:6]}'

# ################################################################################################################################

def load_users(users_file:'str') -> 'Dict[str, str]':
    """ Load users from a JSON file.
    """
    logger.info(f'Loading users from {users_file}')
    try:
        with open(users_file, 'r') as f:
            users_list = json.load(f)
            
        # Convert the list of single-pair dicts to a single dict
        users = {}
        for user_dict in users_list:
            for username, password in user_dict.items():
                users[username] = password
                
        logger.info(f'Loaded {len(users)} users')
        return users
    except Exception as e:
        logger.error(f'Error loading users: {e}')
        return {}

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServer:
    """ Main server class for the Pub/Sub REST API.
    """
    def __init__(
        self,
        host:'str'=DEFAULT_HOST,
        port:'int'=DEFAULT_PORT,
        users_file:'str'='',
        debug:'bool'=False
        ) -> 'None':
        
        # Basic server configuration
        self.host = host
        self.port = port
        self.debug = debug
        
        # Initialize broker client
        self.broker_client = BrokerClient()
        
        # Set up URL routing
        self.url_map = Map([
            # Topic operations
            Rule('/pubsub/topic/<topic_name>', endpoint='handle_topic', methods=['POST', 'PATCH', 'GET']),
            
            # Subscription operations
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='handle_subscribe', methods=['POST', 'DELETE']),
            
            # Health check
            Rule('/pubsub/health', endpoint='handle_health', methods=['GET']),
        ])
        
        # Load users if a file is provided
        self.users = {}
        if users_file:
            self.users = load_users(users_file)
        
        # In-memory storage for topics, subscriptions, and messages
        self.topics:'Dict[str, Topic]' = {}  # topic_name -> Topic
        self.subscriptions:'Dict[str, Dict[str, Subscription]]' = {}  # topic_name -> {endpoint_name -> Subscription}
        self.messages:'Dict[str, Dict[str, List[Message]]]' = {}  # topic_name -> {endpoint_name -> [Message]}
        
        logger.info(f'PubSubRESTServer initialized on {host}:{port} with debug={debug}')

    # ################################################################################################################################

    def authenticate(self, auth_header:'Optional[str]') -> 'Tuple[bool, str]':
        """ Authenticate a request using HTTP Basic Auth.
        Returns a tuple of (is_authenticated, endpoint_name).
        """
        if not auth_header:
            logger.warning('No Authorization header present')
            return False, ''
            
        if not auth_header.startswith('Basic '):
            logger.warning('Authorization header is not Basic')
            return False, ''
            
        try:
            encoded = auth_header[6:]  # Remove 'Basic ' prefix
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            if username in self.users and self.users[username] == password:
                logger.debug(f'Authenticated user: {username}')
                return True, username
                
            logger.warning(f'Authentication failed for user: {username}')
            return False, ''
        except Exception as e:
            logger.error(f'Error during authentication: {e}')
            return False, ''

    # ################################################################################################################################

    def publish_message(
        self,
        topic_name:'str',
        msg:'PubMessage',
        endpoint_name:'str'
        ) -> 'PubResponse':
        """ Publish a message to a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Publishing message to topic {topic_name} from {endpoint_name}')
        
        # Create topic if it doesn't exist
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
            self.subscriptions[topic_name] = {}
            self.messages[topic_name] = {}
            logger.info(f'[{cid}] Created new topic: {topic_name}')
        
        # Generate message ID and calculate size
        msg_id = generate_msg_id()
        data_str = dumps(msg.data) if not isinstance(msg.data, str) else msg.data
        size = len(data_str.encode('utf-8'))
        
        # Set timestamps
        now = datetime.utcnow()
        pub_time_iso = now.isoformat()
        expiration_time = now + timedelta(seconds=msg.expiration)
        expiration_time_iso = expiration_time.isoformat()
        
        # Create message object
        message = Message(
            data=msg.data,
            topic_name=topic_name,
            msg_id=msg_id,
            correl_id=msg.correl_id,
            in_reply_to=msg.in_reply_to,
            priority=msg.priority,
            ext_client_id=msg.ext_client_id,
            pub_time_iso=pub_time_iso,
            recv_time_iso=pub_time_iso,  # Same as pub_time for direct API calls
            expiration=msg.expiration,
            expiration_time_iso=expiration_time_iso,
            size=size,
            delivery_count=0,
        )
        
        # Distribute message to all subscribers
        for endpoint_name, subscription in self.subscriptions[topic_name].items():
            if endpoint_name not in self.messages[topic_name]:
                self.messages[topic_name][endpoint_name] = []
                
            # Copy the message and set the subscription key
            msg_copy = Message(**asdict(message))
            msg_copy.sub_key = subscription.sub_key
            msg_copy.delivery_count += 1
            
            # Add to the subscriber's queue
            self.messages[topic_name][endpoint_name].append(msg_copy)
            logger.debug(f'[{cid}] Delivered message {msg_id} to {endpoint_name} on topic {topic_name}')
        
        # Return success response
        return PubResponse(
            is_ok=True,
            msg_id=msg_id,
            cid=cid,
        )

    # ################################################################################################################################

    def retrieve_messages(
        self,
        topic_name:'str',
        endpoint_name:'str',
        destructive:'bool'=False
        ) -> 'MessagesResponse':
        """ Retrieve messages for a subscriber from a topic.
        If destructive is True, messages are removed from the queue.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Retrieving messages from topic {topic_name} for {endpoint_name} (destructive={destructive})')
        
        # Check if topic and subscription exist
        if topic_name not in self.topics:
            logger.warning(f'[{cid}] Topic {topic_name} does not exist')
            return MessagesResponse(is_ok=True, messages=[])
            
        if topic_name not in self.subscriptions or endpoint_name not in self.subscriptions[topic_name]:
            logger.warning(f'[{cid}] No subscription for {endpoint_name} to topic {topic_name}')
            return MessagesResponse(is_ok=True, messages=[])
            
        # Get messages for this endpoint
        if topic_name in self.messages and endpoint_name in self.messages[topic_name]:
            messages = list(self.messages[topic_name][endpoint_name])  # Make a copy
            
            # Sort by priority (high to low) then by receive time (newest first)
            messages.sort(key=lambda m: (-m.priority, m.recv_time_iso), reverse=True)
            
            # Remove messages if destructive
            if destructive:
                logger.info(f'[{cid}] Removing {len(messages)} messages for {endpoint_name} on topic {topic_name}')
                self.messages[topic_name][endpoint_name] = []
                
            return MessagesResponse(is_ok=True, messages=messages)
        
        # No messages found
        return MessagesResponse(is_ok=True, messages=[])

    # ################################################################################################################################

    def subscribe(
        self,
        topic_name:'str',
        endpoint_name:'str'
        ) -> 'SimpleResponse':
        """ Subscribe an endpoint to a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Subscribing {endpoint_name} to topic {topic_name}')
        
        # Create topic if it doesn't exist
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
            self.subscriptions[topic_name] = {}
            self.messages[topic_name] = {}
            logger.info(f'[{cid}] Created new topic: {topic_name}')
            
        # Check if already subscribed
        if topic_name in self.subscriptions and endpoint_name in self.subscriptions[topic_name]:
            logger.info(f'[{cid}] Endpoint {endpoint_name} already subscribed to {topic_name}')
            return SimpleResponse(is_ok=True)
            
        # Create subscription
        sub_key = generate_sub_key()
        subscription = Subscription(
            topic_name=topic_name,
            endpoint_name=endpoint_name,
            sub_key=sub_key
        )
        
        # Store subscription
        if topic_name not in self.subscriptions:
            self.subscriptions[topic_name] = {}
        self.subscriptions[topic_name][endpoint_name] = subscription
        
        # Initialize message queue
        if topic_name not in self.messages:
            self.messages[topic_name] = {}
        self.messages[topic_name][endpoint_name] = []
        
        logger.info(f'[{cid}] Successfully subscribed {endpoint_name} to {topic_name} with key {sub_key}')
        return SimpleResponse(is_ok=True)

    # ################################################################################################################################

    def unsubscribe(
        self,
        topic_name:'str',
        endpoint_name:'str'
        ) -> 'SimpleResponse':
        """ Unsubscribe an endpoint from a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Unsubscribing {endpoint_name} from topic {topic_name}')
        
        # Check if subscription exists
        if topic_name in self.subscriptions and endpoint_name in self.subscriptions[topic_name]:
            # Remove subscription
            del self.subscriptions[topic_name][endpoint_name]
            
            # Remove messages
            if topic_name in self.messages and endpoint_name in self.messages[topic_name]:
                del self.messages[topic_name][endpoint_name]
                
            logger.info(f'[{cid}] Successfully unsubscribed {endpoint_name} from {topic_name}')
        else:
            logger.info(f'[{cid}] No subscription found for {endpoint_name} to {topic_name}')
            
        return SimpleResponse(is_ok=True)

    # ################################################################################################################################

    def dispatch_request(self, request:'Request') -> 'Response':
        """ Dispatch incoming requests to the appropriate handler.
        """
        # Generate correlation ID for this request
        cid = new_cid()
        
        # Set response headers
        headers = {
            'X-Zato-CID': cid,
            'Content-Type': 'application/json'
        }
        
        try:
            # Match URL pattern
            adapter = self.url_map.bind_to_environ(request.environ)
            endpoint, values = adapter.match()
            
            # Skip auth for health endpoint
            if endpoint == 'handle_health':
                return self.handle_health(request, **values)
                
            # Authenticate request
            is_authenticated, endpoint_name = self.authenticate(request.headers.get('Authorization'))
            if not is_authenticated:
                logger.warning(f'[{cid}] Authentication failed for request to {request.path}')
                return Response(
                    dumps({'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}),
                    status=401,
                    headers=headers
                )
                
            # Dispatch to handler
            values['endpoint_name'] = endpoint_name
            handler = getattr(self, endpoint)
            return handler(request, **values)
            
        except HTTPException as e:
            # Handle HTTP exceptions
            logger.error(f'[{cid}] HTTP error: {e}')
            return Response(
                dumps({'is_ok': False, 'cid': cid, 'details': str(e)}),
                status=e.code,
                headers=headers
            )
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f'[{cid}] Unexpected error: {e}')
            return Response(
                dumps({'is_ok': False, 'cid': cid, 'details': 'Internal server error'}),
                status=500,
                headers=headers
            )

    # ################################################################################################################################

    def handle_health(self, request:'Request', **values) -> 'Response':
        """ Health check endpoint.
        """
        return Response(
            dumps({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}),
            status=200,
            content_type='application/json'
        )

    # ################################################################################################################################

    def handle_topic(self, request:'Request', topic_name:'str', endpoint_name:'str', **values) -> 'Response':
        """ Handle topic operations: publish, retrieve, read.
        """
        # POST = publish message
        if request.method == 'POST':
            try:
                data = request.get_json()
                msg = PubMessage(
                    data=data.get('data'),
                    priority=data.get('priority', 5),
                    expiration=data.get('expiration', 86400),
                    correl_id=data.get('correl_id', ''),
                    in_reply_to=data.get('in_reply_to', ''),
                    ext_client_id=data.get('ext_client_id', '')
                )
                result = self.publish_message(topic_name, msg, endpoint_name)
                return Response(
                    dumps(asdict(result)),
                    status=200,
                    content_type='application/json'
                )
            except Exception as e:
                logger.exception(f'Error publishing message: {e}')
                return Response(
                    dumps({'is_ok': False, 'cid': new_cid(), 'details': str(e)}),
                    status=400,
                    content_type='application/json'
                )
                
        # PATCH = retrieve messages (destructive)
        elif request.method == 'PATCH':
            result = self.retrieve_messages(topic_name, endpoint_name, destructive=True)
            return Response(
                dumps(asdict(result)),
                status=200,
                content_type='application/json'
            )
            
        # GET = read messages (non-destructive)
        elif request.method == 'GET':
            result = self.retrieve_messages(topic_name, endpoint_name, destructive=False)
            return Response(
                dumps(asdict(result)),
                status=200,
                content_type='application/json'
            )
            
        # Other methods not allowed
        return Response(
            dumps({'is_ok': False, 'cid': new_cid(), 'details': 'Method not allowed'}),
            status=405,
            content_type='application/json'
        )

    # ################################################################################################################################

    def handle_subscribe(self, request:'Request', topic_name:'str', endpoint_name:'str', **values) -> 'Response':
        """ Handle subscription operations: subscribe, unsubscribe.
        """
        # POST = subscribe
        if request.method == 'POST':
            result = self.subscribe(topic_name, endpoint_name)
            return Response(
                dumps(asdict(result)),
                status=200,
                content_type='application/json'
            )
            
        # DELETE = unsubscribe
        elif request.method == 'DELETE':
            result = self.unsubscribe(topic_name, endpoint_name)
            return Response(
                dumps(asdict(result)),
                status=200,
                content_type='application/json'
            )
            
        # Other methods not allowed
        return Response(
            dumps({'is_ok': False, 'cid': new_cid(), 'details': 'Method not allowed'}),
            status=405,
            content_type='application/json'
        )

    # ################################################################################################################################

    def wsgi_app(self, environ:'Dict', start_response:'Any') -> 'Any':
        """ WSGI application entry point.
        """
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    # ################################################################################################################################

    def __call__(self, environ:'Dict', start_response:'Any') -> 'Any':
        """ Make the class callable as a WSGI application.
        """
        return self.wsgi_app(environ, start_response)

    # ################################################################################################################################

    def run(self) -> 'None':
        """ Run the server using gevent's WSGIServer.
        """
        server = WSGIServer((self.host, self.port), ProxyFix(self))
        logger.info(f'Starting PubSub REST API server on {self.host}:{self.port}')
        server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

class GunicornApplication(BaseApplication):
    """ Gunicorn application wrapper for the PubSub REST API.
    """
    def __init__(self, app:'PubSubRESTServer', options:'Dict'=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

# ################################################################################################################################
# ################################################################################################################################

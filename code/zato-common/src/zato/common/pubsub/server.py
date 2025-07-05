# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import asdict
from json import dumps
from logging import getLogger

# Zato
from zato.common.typing_ import any_, anydict, dict_, list_, optional, str_

# gevent
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# gunicorn
from gunicorn.app.base import BaseApplication

# Zato
from zato.broker.client import BrokerClient
from zato.common.util.api import new_cid
from zato.common.pubsub.models import PubMessage, PubResponse, Message, SimpleResponse
from zato.common.pubsub.models import Subscription, Topic
from zato.common.pubsub.models import topic_messages, topic_subscriptions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, dictnone

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

def load_users(users_file:'str') -> 'strdict':
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
        self.topics:dict_[str_, Topic] = {}  # topic_name -> Topic
        self.subscriptions:topic_subscriptions = {}  # topic_name -> {endpoint_name -> Subscription}
        self.messages:topic_messages = {}  # topic_name -> {endpoint_name -> [Message]}

        logger.info(f'PubSubRESTServer initialized on {host}:{port} with debug={debug}')

    # ################################################################################################################################

    def authenticate(self, environ:'anydict') -> 'optional[str_]':
        """ Authenticate a request using HTTP Basic Authentication.
        """
        logger.info('Authenticating request')
        auth_header = environ.get('HTTP_AUTHORIZATION')
        if not auth_header:
            logger.warning('No Authorization header present')
            return None

        if not auth_header.startswith('Basic '):
            logger.warning('Authorization header is not Basic')
            return None

        try:
            encoded = auth_header[6:]  # Remove 'Basic ' prefix
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)

            if username in self.users and self.users[username] == password:
                logger.debug(f'Authenticated user: {username}')
                return username

            logger.warning(f'Authentication failed for user: {username}')
            return None
        except Exception as e:
            logger.error(f'Error during authentication: {e}')
            return None

    # ################################################################################################################################

    def publish(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ Publish a message to a topic.
        """
        logger.info('Processing publish request')
        cid = new_cid()
        logger.info(f'[{cid}] Publishing message to topic')

        # Get request data
        request = Request(environ)
        data = request.get_json()

        # Validate request data
        if not data:
            logger.warning(f'[{cid}] Invalid request data')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Invalid request data'}, '400 Bad Request')

        topic_name = data.get('topic_name')
        msg = PubMessage(
            data=data.get('data'),
            priority=data.get('priority', 5),
            expiration=data.get('expiration', 86400),
            correl_id=data.get('correl_id', ''),
            in_reply_to=data.get('in_reply_to', ''),
            ext_client_id=data.get('ext_client_id', '')
        )

        # Authenticate request
        endpoint_name = self.authenticate(environ)
        if not endpoint_name:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Publish message
        result = self.publish_message(topic_name, msg, endpoint_name)
        return self._json_response(start_response, asdict(result))

    # ################################################################################################################################

    def handle_subscribe(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ Handle subscribe request to a topic.
        """
        logger.info('Processing subscribe request')
        cid = new_cid()
        logger.info(f'[{cid}] Handling subscribe request to topic')

        # Get request data
        request = Request(environ)
        data = request.get_json()

        # Validate request data
        if not data:
            logger.warning(f'[{cid}] Invalid request data')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Invalid request data'}, '400 Bad Request')

        topic_name = data.get('topic_name')

        # Authenticate request
        endpoint_name = self.authenticate(environ)
        if not endpoint_name:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Subscribe to topic
        result = self.subscribe(topic_name, endpoint_name)
        return self._json_response(start_response, asdict(result))

    # ################################################################################################################################

    def handle_unsubscribe(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ Handle unsubscribe request from a topic.
        """
        logger.info('Processing unsubscribe request')
        cid = new_cid()
        logger.info(f'[{cid}] Handling unsubscribe request from topic')

        # Get request data
        request = Request(environ)
        data = request.get_json()

        # Validate request data
        if not data:
            logger.warning(f'[{cid}] Invalid request data')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Invalid request data'}, '400 Bad Request')

        topic_name = data.get('topic_name')

        # Authenticate request
        endpoint_name = self.authenticate(environ)
        if not endpoint_name:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Unsubscribe from topic
        result = self.unsubscribe(topic_name, endpoint_name)
        return self._json_response(start_response, asdict(result))

    # ################################################################################################################################

    def health_check(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ Health check endpoint.
        """
        logger.info('Processing health check request')
        return self._json_response(start_response, {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

    # ################################################################################################################################

    def _json_response(self, start_response:'any_', data:'any_', status:'str_'='200 OK') -> 'list_[bytes]':
        """ Return a JSON response.
        """
        logger.debug('Sending JSON response, status: %s', status)
        response = dumps(asdict(data) if hasattr(data, '__dataclass_fields__') else data).encode('utf-8')
        start_response(status, [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response)))
        ])
        return [response]

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

    def subscribe(
        self,
        topic_name:'str',
        endpoint_name:'str'
        ) -> 'SimpleResponse':
        """ Subscribe to a topic.
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
        """ Unsubscribe from a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Unsubscribing {endpoint_name} from topic {topic_name}')

        # Check if subscription exists
        if topic_name in self.subscriptions and endpoint_name in self.subscriptions[topic_name]:

            # Get topic subscriptions
            topic_subscriptions = self.subscriptions[topic_name]

            # Remove the subscription
            _ = topic_subscriptions.pop(endpoint_name)

            # Remove messages if they exist
            if topic_name in self.messages and endpoint_name in self.messages[topic_name]:

                # Get topic messages
                topic_message_map = self.messages[topic_name]

                # Remove endpoint messages
                _ = topic_message_map.pop(endpoint_name)

            logger.info(f'[{cid}] Successfully unsubscribed {endpoint_name} from {topic_name}')
        else:
            logger.info(f'[{cid}] No subscription found for {endpoint_name} to {topic_name}')

        return SimpleResponse(is_ok=True)

    # ################################################################################################################################

    def __call__(self, environ:'anydict', start_response:'any_') -> 'any_':
        """ Handle incoming HTTP requests.
        """
        # Log the incoming request
        logger.info('Handling incoming HTTP request, path: %s, method: %s', environ.get('PATH_INFO'), environ.get('REQUEST_METHOD'))

        # Dispatch to handler
        if environ['PATH_INFO'] == '/pubsub/topic':
            return self.publish(environ, start_response)
        elif environ['PATH_INFO'].startswith('/pubsub/subscribe/topic'):
            # Check the HTTP method to determine if it's a subscribe or unsubscribe request
            if environ['REQUEST_METHOD'] == 'POST':
                return self.handle_subscribe(environ, start_response)
            elif environ['REQUEST_METHOD'] == 'DELETE':
                return self.handle_unsubscribe(environ, start_response)
        elif environ['PATH_INFO'] == '/pubsub/health':
            return self.health_check(environ, start_response)
        else:
            logger.warning('Unknown request path: %s', environ['PATH_INFO'])
            return self._json_response(start_response, {'is_ok': False, 'details': 'Unknown request path'}, '404 Not Found')

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
    def __init__(self, app:'PubSubRESTServer', options:'dictnone'=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        # Apply valid configuration options
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None: # type: ignore
                self.cfg.set(key.lower(), value) # type: ignore

    def load(self):
        return self.application

# ################################################################################################################################
# ################################################################################################################################

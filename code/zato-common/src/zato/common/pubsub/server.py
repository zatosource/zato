# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import uuid
from datetime import datetime, timedelta
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common.typing_ import any_, anydict, dict_, list_, strnone
from zato.common.util.auth import check_basic_auth, extract_basic_auth

# gevent
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# gunicorn
from gunicorn.app.base import BaseApplication

# Zato
from zato.broker.client import BrokerClient
from zato.common.util.api import new_cid
from zato.common.pubsub.models import PubMessage, PubResponse, SimpleResponse
from zato.common.pubsub.models import Subscription, Topic
from zato.common.pubsub.models import topic_subscriptions

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

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

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
            data = f.read()
            users_list = loads(data)

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
        has_debug:'bool'=False
        ) -> 'None':

        # Basic server configuration
        self.host = host
        self.port = port
        self.has_debug = has_debug

        # Initialize broker client
        self.broker_client = BrokerClient()

        # Set up URL routing with direct mapping to handler methods
        self.url_map = Map([
            # Topic operations - publish
            Rule('/pubsub/topic/<topic_name>', endpoint='publish', methods=['POST']),

            # Subscribe and unsubscribe operations - same URL, different HTTP methods
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='handle_subscribe', methods=['POST']),
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='handle_unsubscribe', methods=['DELETE']),

            # Health check
            Rule('/pubsub/health', endpoint='health_check', methods=['GET']),
        ])

        # Load users if a file is provided
        self.users = {}
        if users_file:
            self.users = load_users(users_file)

        # Storage for topics and subscriptions metadata only
        self.topics:'dict_[str, Topic]' = {}           # topic_name -> Topic
        self.subscriptions:'topic_subscriptions' = {}  # topic_name -> {endpoint_name -> Subscription}

        logger.info(f'PubSubRESTServer initialized on {host}:{port} with has_debug={has_debug}')

# ################################################################################################################################

    def authenticate(self, environ:'anydict') -> 'strnone':
        """ Authenticate a request using HTTP Basic Authentication.
        """
        cid = new_cid()
        auth_header = environ.get('HTTP_AUTHORIZATION', '')

        path_info = environ.get('PATH_INFO', 'unknown-path')

        if not auth_header:
            logger.warning(f'No Authorization header present; path_info:`{path_info}`')
            return None

        # First, extract the username and password from the auth header
        result = extract_basic_auth(cid, auth_header, raise_on_error=False)
        username, _ = result

        if not username:
            logger.warning(f'Invalid Authorization header format; path_info:`{path_info}`')
            return None

        if username in self.users:
            if check_basic_auth(cid, auth_header, username, self.users[username]) is True:
                return username
            else:
                logger.warning(f'Invalid password for `{username}`; path_info:`{path_info}`')
        else:
            logger.warning(f'No such user `{username}`; path_info:`{path_info}`')

        return None

# ################################################################################################################################

    def publish(self, environ:'anydict', start_response:'any_', topic_name:'str') -> 'list_[bytes]':
        """ Publish a message to a topic.
        """
        logger.info('Processing publish request')
        cid = new_cid()

        # Get request data
        request = Request(environ)
        data = self._parse_json(request)

        # Validate request data
        if not data:
            logger.warning(f'[{cid}] Invalid request data')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Invalid request data'}, '400 Bad Request')

        # Use the 'data' field from the request as specified in the spec
        msg_data = data.get('data')

        if msg_data is None:
            logger.warning(f'[{cid}] Missing required data field')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Missing required data field'}, '400 Bad Request')

        msg = PubMessage(
            data=msg_data,
            priority=data.get('priority', 5),
            expiration=data.get('expiration', 86400),
            correl_id=data.get('correl_id', ''),
            in_reply_to=data.get('in_reply_to', ''),
            ext_client_id=data.get('ext_client_id', '')
        )

        # Authenticate request
        username = self.authenticate(environ)
        if not username:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Get client id if provided
        ext_client_id = data.get('ext_client_id')

        # Publish message
        result = self.publish_message(topic_name, msg, username, ext_client_id)

        # Create a simple response with only the necessary fields
        return self._json_response(start_response, {'is_ok': result.is_ok, 'cid': cid})

# ################################################################################################################################

    def handle_subscribe(self, environ:'anydict', start_response:'any_', topic_name:'str') -> 'list_[bytes]':
        """ Handle subscription request.
        """
        logger.info('Processing subscribe request')
        cid = new_cid()

        logger.info(f'[{cid}] Processing subscription request for topic {topic_name}')

        # Authenticate request
        endpoint_name = self.authenticate(environ)
        if not endpoint_name:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Subscribe to topic
        result = self.subscribe(topic_name, endpoint_name)
        return self._json_response(start_response, {'is_ok': result.is_ok, 'cid': cid})

# ################################################################################################################################

    def handle_unsubscribe(self, environ:'anydict', start_response:'any_', topic_name:'str') -> 'list_[bytes]':
        """ Handle unsubscribe request.
        """
        logger.info('Processing unsubscribe request')
        cid = new_cid()
        logger.info(f'[{cid}] Processing unsubscription request for topic {topic_name}')

        # Authenticate request
        endpoint_name = self.authenticate(environ)
        if not endpoint_name:
            logger.warning(f'[{cid}] Authentication failed')
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Authentication failed'}, '401 Unauthorized')

        # Unsubscribe from topic
        result = self.unsubscribe(topic_name, endpoint_name)

        if result.is_ok:
            return self._json_response(start_response, {'is_ok': True, 'cid': cid})
        else:
            return self._json_response(start_response, {'is_ok': False, 'cid': cid, 'details': 'Failed to unsubscribe'}, '400 Bad Request')

# ################################################################################################################################

    def health_check(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ Health check endpoint.
        """
        logger.info('Processing health check request')
        return self._json_response(start_response, {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

# ################################################################################################################################

    def _parse_json(self, request:'Request') -> 'dict_':
        """ Parse JSON from request.
        """
        # Initialize raw_data to avoid unbound variable in exception handler
        raw_data = None

        try:
            # Get raw data from environ['wsgi.input']
            raw_data = request.get_data()

            if raw_data:
                # Decode and parse
                text_data = raw_data.decode('utf-8')
                data = loads(text_data)
                return data
            else:
                logger.warning('No request data provided')
                return {}

        except Exception as e:
            logger.error(f'Error parsing JSON: {e}, raw data: {raw_data}')
            # Re-raise so the caller can handle it
            raise

# ################################################################################################################################

    def _json_response(self, start_response:'any_', data:'any_', status:'str'='200 OK') -> 'list_[bytes]':
        """ Return a JSON response.
        """
        # Set response headers
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)

        # Return JSON data
        json_data = dumps(data).encode('utf-8')
        return [json_data]

# ################################################################################################################################

    def publish_message(
        self,
        topic_name:'str',
        msg:'PubMessage',
        username:'str',
        ext_client_id:'strnone'=None
        ) -> 'PubResponse':
        """ Publish a message to a topic using the broker client.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Publishing message to topic {topic_name} from {username}')

        # Create topic if it doesn't exist
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
            self.subscriptions[topic_name] = {}
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
        message = {
            'data': msg.data,
            'topic_name': topic_name,
            'msg_id': msg_id,
            'correl_id': msg.correl_id,
            'in_reply_to': msg.in_reply_to,
            'priority': msg.priority,
            'ext_client_id': msg.ext_client_id,
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': pub_time_iso,  # Same as pub_time for direct API calls
            'expiration': msg.expiration,
            'expiration_time_iso': expiration_time_iso,
            'size': size,
            'delivery_count': 0,
            'publisher': username,
        }

        self.broker_client.publish(message, exchange=ModuleCtx.Exchange_Name, routing_key=topic_name)

        ext_client_part = f' -> {ext_client_id}' if ext_client_id else ''
        logger.info(f'Published message {cid} to topic {topic_name} ({username}{ext_client_part})')

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

        # Register subscription with broker client
        self.broker_client.subscribe(topic_name, endpoint_name, sub_key) # type: ignore
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
            # Get subscription key before removing it
            sub_key = self.subscriptions[topic_name][endpoint_name].sub_key

            # Remove the subscription from our metadata
            _ = self.subscriptions[topic_name].pop(endpoint_name)

            # Unregister subscription with broker client
            self.broker_client.unsubscribe(topic_name, endpoint_name, sub_key) # type: ignore

            logger.info(f'[{cid}] Successfully unsubscribed {endpoint_name} from {topic_name}')
        else:
            logger.info(f'[{cid}] No subscription found for {endpoint_name} to {topic_name}')

        return SimpleResponse(is_ok=True)

# ################################################################################################################################

    def __call__(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ WSGI entry point for the server using dynamic dispatch based on Werkzeug URL routing.
        """
        logger.info('Handling incoming HTTP request, path: %s, method: %s', environ.get('PATH_INFO'), environ.get('REQUEST_METHOD'))

        # Bind the URL map to the current request
        urls = self.url_map.bind_to_environ(environ)

        try:
            # Match the path to a registered endpoint
            endpoint, args = urls.match()

            # Dynamic dispatch - call the method named by the endpoint
            if hasattr(self, endpoint):
                handler = getattr(self, endpoint)
                return handler(environ, start_response, **args)
            else:
                logger.warning(f'No handler for endpoint: {endpoint}')
                return self._json_response(start_response,
                    {'is_ok': False, 'details': 'Endpoint not implemented'},
                    '501 Not Implemented')

        except NotFound:
            logger.warning('No URL match found for path: %s', environ.get('PATH_INFO'))
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

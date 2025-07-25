# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
from dataclasses import asdict
from http.client import OK
from json import dumps, loads
from logging import getLogger

# PyYAML
from yaml import dump as yaml_dump

# requests
import requests
from requests.auth import HTTPBasicAuth

# Zato
from zato.common.typing_ import any_, anydict, dict_, list_, strnone
from zato.common.util.auth import check_basic_auth, extract_basic_auth

# gevent
from gevent.pywsgi import WSGIServer

# gunicorn
from gunicorn.app.base import BaseApplication

# werkzeug
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# Zato
from zato.common.api import PubSub
from zato.common.util.api import new_cid
from zato.common.pubsub.models import PubMessage
from zato.common.pubsub.models import APIResponse, BadRequestResponse, HealthCheckResponse, NotImplementedResponse, \
    UnauthorizedResponse
from zato.common.pubsub.server.base import BaseServer
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration
_max_messages_limit = 1000
_max_len_limit = 5_000_000

# ################################################################################################################################
# ################################################################################################################################

class UnauthorizedException(Exception):
    def __init__(self, cid:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class BadRequestException(Exception):
    def __init__(self, cid:'str', message:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        self.message = message
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServer(BaseServer):
    """ A REST server for pub/sub operations.
    """

    def __init__(self, host:'str', port:'int', yaml_config_file:'any_'=None) -> 'None':
        super().__init__(host, port, yaml_config_file)

        # Initialize broker configuration for reuse
        self._broker_config = get_broker_config()
        self._broker_auth = HTTPBasicAuth(self._broker_config.username, self._broker_config.password)
        self._broker_api_base_url = f'{self._broker_config.protocol}://{self._broker_config.address}:15672/api'

# ################################################################################################################################

    def authenticate(self, cid:'str', environ:'anydict') -> 'strnone':
        """ Authenticate a request using HTTP Basic Authentication.
        """
        path_info = environ['PATH_INFO']
        auth_header = environ.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            logger.warning(f'[{cid}] No Authorization header present; path_info:`{path_info}`')
            return None

        # First, extract the username and password from the auth header
        result = extract_basic_auth(cid, auth_header, raise_on_error=False)
        username, _ = result

        if not username:
            logger.warning(f'[{cid}] Invalid Authorization header format; path_info:`{path_info}`')
            return None

        if username in self.users:
            password = self.users[username]
            if check_basic_auth(cid, auth_header, username, password) is True:
                return username
            else:
                logger.warning(f'[{cid}] Invalid password for `{username}`; path_info:`{path_info}`')
        else:
            logger.warning(f'[{cid}] No such user `{username}`; path_info:`{path_info}`')

        return None

# ################################################################################################################################

    def _ensure_authenticated(self, cid:'str', environ:'anydict') -> 'str':

        # Authenticate request
        username = self.authenticate(cid, environ)

        if not username:
            raise UnauthorizedException(cid)
        else:
            return username

# ################################################################################################################################
# ################################################################################################################################

#
# All the on_* methods are WSGI-level callbacks invoked by __call__
#

# ################################################################################################################################
# ################################################################################################################################

    def on_publish(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Publish a message to a topic.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing publish request')

        # .. make sure the client is allowed to carry out this action ..
        username = self._ensure_authenticated(cid, environ)

        # .. build our representation of the request ..
        request = Request(environ)
        data = self._parse_json(cid, request)

        # .. make sure we actually did receive anything ..
        if not data:
            raise BadRequestException(cid, 'Input data missing')

        # .. now also make sure we did receive the business data ..
        msg_data = data.get('data')

        if msg_data is None:
            raise BadRequestException(cid, 'Message data missing')

        # .. get all the details from the message now that we know we have it ..
        ext_client_id = data.get('ext_client_id', '')
        priority = data.get('priority', _default_priority)
        expiration = data.get('expiration', _default_expiration)
        correl_id = data.get('correl_id', '') or cid
        in_reply_to=data.get('in_reply_to', '')

        # .. build a business message ..
        msg = PubMessage()
        msg.data = msg_data
        msg.priority = priority
        msg.expiration = expiration
        msg.correl_id = correl_id
        msg.ext_client_id = ext_client_id
        msg.in_reply_to = in_reply_to

        # .. let the backend handle it ..
        result = self.backend.publish_impl(cid, topic_name, msg, username, ext_client_id)

        # .. build our response ..
        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        # .. and return it to the caller.
        return response

# ################################################################################################################################

    def on_subscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle subscription request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing subscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self._ensure_authenticated(cid, environ)

        # Subscribe to topic using backend
        result = self.backend.register_subscription(cid, topic_name, username)

        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        return response

# ################################################################################################################################

    def on_unsubscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle unsubscribe request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing unsubscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self._ensure_authenticated(cid, environ)

        # Unsubscribe from topic using backend
        result = self.backend.unregister_subscription(cid, topic_name, username)

        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        return response

# ################################################################################################################################

    def on_health_check(self, environ:'anydict', start_response:'any_') -> 'HealthCheckResponse':
        """ Health check endpoint.
        """
        response = HealthCheckResponse()
        response.is_ok = True
        response.cid = new_cid()

        return response

# ################################################################################################################################

    def on_admin_diagnostics(self, cid:'str', environ:'anydict', start_response:'any_') -> 'APIResponse':
        """ Admin diagnostics endpoint - dumps topics, users, subscriptions, etc. to logs in YAML format.
        """
        # Ensure the request is authenticated
        _ = self._ensure_authenticated(cid, environ)

        # Collect data for diagnostics
        diagnostics = {
            'topics': {},
            'users': self.users,
            'subscriptions': {}
        }

        # Extract topic information
        for topic_name, topic in self.backend.topics.items():
            diagnostics['topics'][topic_name] = {
                'name': topic.name
            }

        # Extract subscription information
        for topic_name, subs_by_username in self.backend.subs_by_topic.items():
            diagnostics['subscriptions'][topic_name] = {}
            for username, subscription in subs_by_username.items():
                diagnostics['subscriptions'][topic_name][username] = {
                    'sub_key': subscription.sub_key
                }

        # Dump to logs in YAML format
        yaml_output = yaml_dump(diagnostics, default_flow_style=False)
        logger.info(f'[{cid}] Admin diagnostics: \n{yaml_output}')

        # Return a simple success response (not exposing the data)
        response = APIResponse()
        response.is_ok = True
        response.cid = cid
        response.details = 'Diagnostics logged successfully'

        return response

# ################################################################################################################################

    def on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> 'APIResponse':
        """ Get messages from the user's queue.
        """
        # Authenticate the user
        username = self._ensure_authenticated(cid, environ)

        # Parse request data
        request = Request(environ)
        data = self._parse_json(cid, request)

        # Extract and validate parameters
        max_len = data.get('max_len', _max_len_limit)
        max_messages = data.get('max_messages', 1)

        # Enforce limits
        max_len = min(max_len, _max_len_limit)
        max_messages = min(max_messages, _max_messages_limit)

        # Find the user's subscription to get their sub_key (queue name)
        sub_key = None
        for subs_by_sec_name in self.subs_by_topic.values():
            if username in subs_by_sec_name:
                subscription = subs_by_sec_name[username]
                sub_key = subscription.sub_key
                break

        if not sub_key:
            logger.warning(f'[{cid}] No subscription found for user `{username}`')
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'No subscription found for user'
            return response

        # Build RabbitMQ API URL
        api_url = f'{self._broker_api_base_url}/queues/{self._broker_config.vhost}/{sub_key}/get'

        # Prepare request payload for RabbitMQ
        rabbitmq_payload = {
            'count': max_messages,
            'ackmode': 'ack_requeue_false',  # Acknowledge and delete messages
            'encoding': 'auto',
            'truncate': max_len
        }

        try:
            # Make request to RabbitMQ
            rabbitmq_response = requests.post(api_url, json=rabbitmq_payload, auth=self._broker_auth)

            if rabbitmq_response.status_code != OK:
                logger.error(f'[{cid}] RabbitMQ API error: {rabbitmq_response.status_code} - {rabbitmq_response.text}')
                response = BadRequestResponse()
                response.cid = cid
                response.details = 'Failed to retrieve messages from queue'
                return response

            # Parse RabbitMQ response
            messages_data = rabbitmq_response.json()

            # Transform messages to our API format
            messages = []
            for msg in messages_data:
                # Extract message properties
                properties = msg.get('properties', {})
                headers = properties.get('headers', {})
                payload_data = msg.get('payload', '')

                # Calculate size
                if isinstance(payload_data, str):
                    size = len(payload_data.encode('utf-8'))
                else:
                    size = len(payload_data)

                # Build our message format according to Zato spec
                message = {
                    'data': payload_data,
                    'msg_id': properties.get('message_id', ''),
                    'correl_id': properties.get('correlation_id', ''),
                    'priority': properties.get('priority', _default_priority),
                    'mime_type': properties.get('content_type', 'application/json'),
                    'pub_time_iso': properties.get('timestamp', ''),
                    'recv_time_iso': properties.get('timestamp', ''),
                    'expiration': properties.get('expiration', _default_expiration),
                    'topic_name': headers.get('topic_name', ''),
                    'ext_client_id': headers.get('ext_client_id', ''),
                    'ext_pub_time_iso': headers.get('ext_pub_time_iso', ''),
                    'in_reply_to': '',
                    'expiration_time_iso': '',
                    'size': size,
                }
                messages.append(message)

            logger.info(f'[{cid}] Retrieved {len(messages)} messages for user `{username}` from queue `{sub_key}`')

            # Build success response
            response = APIResponse()
            response.is_ok = True
            response.cid = cid
            response.data = messages

            return response

        except Exception as e:
            logger.error(f'[{cid}] Error retrieving messages: {e}')
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'Internal error retrieving messages'
            return response

# ################################################################################################################################

    def _parse_json(self, cid:'str', request:'Request') -> 'dict_':
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
                logger.warning('[{cid}] No request data provided')
                return {}

        except Exception as e:
            logger.error(f'[{cid}] Error parsing JSON: {e}, raw data: {raw_data}')
            raise

# ################################################################################################################################

    def _json_response(self, start_response:'any_', data:'APIResponse | HealthCheckResponse') -> 'list_[bytes]':
        """ Return a JSON response.
        """
        response_data = asdict(data)

        if not response_data.get('details'):
            del response_data['details']

        json_data = dumps(response_data).encode('utf-8')

        headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(json_data)))]
        start_response(data.status, headers)

        return [json_data]

# ################################################################################################################################

    def __call__(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ WSGI entry point for the server using dynamic dispatch based on Werkzeug URL routing.
        """
        # We always need our own new Correlation ID ..
        cid = new_cid()

        # .. log what we're doing ..
        logger.info('[%s] Handling request, %s %s', cid, environ.get('REQUEST_METHOD'), environ.get('PATH_INFO'))

        # Bind the URL map to the current request
        urls = self.url_map.bind_to_environ(environ)

        try:
            # Match the path to a registered endpoint
            endpoint, args = urls.match()

            # Dynamic dispatch - call the method named by the endpoint
            if hasattr(self, endpoint):

                # The actual handler will be one of our on_* methods, e.g. on_publish, on_subscribe etc.
                handler = getattr(self, endpoint)
                handler_response = handler(cid, environ, start_response, **args)
                response_bytes = self._json_response(start_response, handler_response)
                return response_bytes
            else:
                logger.warning(f'No handler for endpoint: {endpoint}')
                response = NotImplementedResponse()
                response.cid = cid
                return self._json_response(start_response, response)

        except UnauthorizedException:
            response = UnauthorizedResponse()
            response.cid = cid
            return self._json_response(start_response, response)

        except BadRequestException as e:
            logger.warning(f'[{cid}] {e.message}')
            response = BadRequestResponse()
            response.cid = cid
            return self._json_response(start_response, response)

        except MethodNotAllowed as e:
            logger.warning(f'[{cid}] Method not allowed')
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'Method not allowed'
            return self._json_response(start_response, response)

        except NotFound:
            logger.warning('No URL match found for path: %s', environ.get('PATH_INFO'))
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'URL not found'
            return self._json_response(start_response, response)

# ################################################################################################################################

    def list_connections(self, cid:'str', management_port:'int'=15672) -> 'dict_':

        logger.info(f'[{cid}] Listing RabbitMQ connections via management API')

        # Use instance variables for broker configuration
        host = self._broker_config.address.split(':')[0]

        # Base URL for the management API
        api_base_url = f'http://{host}:{management_port}/api'

        # Get all connections
        connections_url = f'{api_base_url}/connections'
        response = requests.get(connections_url, auth=self._broker_auth)

        if response.status_code != OK:
            logger.error(f'Failed to list connections: {response.status_code}, {response.text}')
            return {'status': 'error', 'error': response.text, 'status_code': response.status_code}

        connections = response.json()
        total_count = len(connections)
        logger.info(f'[{cid}] Found {total_count} RabbitMQ connections')

        # Analyze connections
        connection_types = {}
        user_connections = {}
        client_properties = {}

        for conn in connections:
            # Group by connection type
            conn_type = conn.get('client_properties', {}).get('connection_name', 'Unknown')
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1

            # Group by user
            user = conn.get('user', 'Unknown')
            if user not in user_connections:
                user_connections[user] = []
            user_connections[user].append({
                'client_properties': conn.get('client_properties', {}),
                'connected_at': conn.get('connected_at'),
                'channels': conn.get('channels', 0)
            })

            # Track unique client properties
            for key, value in conn.get('client_properties', {}).items():
                if key not in client_properties:
                    client_properties[key] = set()
                if isinstance(value, (str, int, bool, float)):
                    client_properties[key].add(value)

        # Convert sets to lists for JSON serialization
        for key in client_properties:
            client_properties[key] = list(client_properties[key])

        # Check consumers
        channels_url = f'{api_base_url}/channels'
        response = requests.get(channels_url, auth=self._broker_auth)

        consumers_per_queue = {}
        if response.status_code == OK:
            channels = response.json()
            for channel in channels:
                consumer_details = channel.get('consumer_details', [])
                for consumer in consumer_details:
                    queue = consumer.get('queue', {}).get('name', 'Unknown')
                    if queue not in consumers_per_queue:
                        consumers_per_queue[queue] = 0
                    consumers_per_queue[queue] += 1

        # Check subscription keys in backend
        sub_keys = list(self.backend.consumers.keys()) if hasattr(self.backend, 'consumers') else []

        return {
            'status': 'success',
            'total_connections': total_count,
            'connection_types': connection_types,
            'user_connections': user_connections,
            'client_properties_unique_values': client_properties,
            'consumers_per_queue': consumers_per_queue,
            'backend_sub_keys': sub_keys
        }

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
        self.options.setdefault('post_fork', self.on_post_fork)
        self.application = app
        super().__init__()

    def load_config(self):
        # Apply valid configuration options
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None: # type: ignore
                self.cfg.set(key.lower(), value) # type: ignore

    def load(self):
        return self.application

    def on_post_fork(self, server, worker):
        self.application.setup()

# ################################################################################################################################
# ################################################################################################################################

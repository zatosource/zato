# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import os
from dataclasses import asdict
from http.client import responses as http_responses, OK, METHOD_NOT_ALLOWED
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

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

# werkzeug
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# Zato
from zato.common.api import PubSub
from zato.common.util.api import as_bool, new_cid_pubsub
from zato.common.pubsub.models import APIResponse, BadRequestResponse, HealthCheckResponse, MethodNotAllowedResponse, \
    NotImplementedResponse, UnauthorizedResponse
from zato.common.pubsub.server.base import BaseServer
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_default_priority = PubSub.Message.Priority_Default
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

class BaseRESTServer(BaseServer):

    def __init__(
        self,
        host:'str',
        port:'int',
        should_init_broker_client:'bool'=False,
    ) -> 'None':

        super().__init__(host, port, should_init_broker_client)

        # Initialize broker configuration for reuse
        self._broker_config = get_broker_config()
        self._broker_auth = HTTPBasicAuth(self._broker_config.username, self._broker_config.password)

        # Extract host from address (remove port if present)
        broker_host = self._broker_config.address.split(':')[0]

        http_protocol = 'https' if self._broker_config.protocol == 'amqps' else 'http'
        self._broker_api_base_url = f'{http_protocol}://{broker_host}:15672/api'

# ################################################################################################################################

    def _authenticate(self, cid:'str', environ:'anydict') -> 'strnone':
        """ Authenticate a request using HTTP Basic Authentication.
        """
        path_info = environ['PATH_INFO']
        auth_header = environ.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            logger.warning(f'[{cid}] No Authorization header present; path_info:`{path_info}`')
            return None

        try:

            # First, extract the username and password from the auth header ..
            result = extract_basic_auth(cid, auth_header, raise_on_error=False)

        except Exception as e:

            # .. but if we failed to extract them, turn that into a 401 exception because we cannot log the user in.
            raise UnauthorizedException(e.args[0])

        username, _ = result

        if not username:
            logger.warning(f'[{cid}] Invalid Authorization header format; path_info:`{path_info}`')
            return None

        if username in self.users:
            config = self.users[username]
            password = config['password']
            if check_basic_auth(cid, auth_header, username, password) is True:
                return username
            else:
                logger.warning(f'[{cid}] Invalid password for `{username}`; path_info:`{path_info}`')
        else:
            logger.warning(f'[{cid}] No such user `{username}`; path_info:`{path_info}`')

        return None

# ################################################################################################################################

    def authenticate(self, cid:'str', environ:'anydict') -> 'str':

        # Authenticate request
        username = self._authenticate(cid, environ)

        if not username:
            raise UnauthorizedException(cid)
        else:
            return username

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
                logger.warning(f'[{cid}] No request data provided')
                return {}

        except Exception:
            raise BadRequestException(cid, f'JSON parsing error: `{format_exc()}`')

# ################################################################################################################################

    def _json_response(self, start_response:'any_', data:'APIResponse | HealthCheckResponse') -> 'list_[bytes]':
        """ Return a JSON response.
        """
        # Check if this is a 405 response before status gets modified
        is_method_not_allowed = data.status == METHOD_NOT_ALLOWED

        # Get the textual part of the status code ..
        response_text = http_responses[data.status] # type: ignore

        # .. build a full status field ..
        status = f'{data.status} {response_text}'

        # .. replace the status we were given on input ..
        data.status = status

        # .. now we can serialize it ..
        response_data = asdict(data)

        # .. drop the fields that may be empty ..
        fields_to_check = ['details', 'msg_id', 'data']

        # .. add fields that should only be dropped if None ..
        for field in ['messages', 'message_count', 'meta', 'messages']:
            value = response_data.get(field)
            if value is None:
                fields_to_check.append(field)

        for key in fields_to_check:
            if not response_data.get(key):
                _ = response_data.pop(key, None)

        # .. now we can serialize it ..
        json_data = dumps(response_data).encode('utf-8')

        # .. prepare our headers ..
        headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(json_data)))]

        # .. add Allow header for 405 responses ..
        if is_method_not_allowed:
            headers.append(('Allow', 'POST'))

        # .. call the WSGI handler ..
        start_response(status, headers)

        # .. and return the response to our WSGI caller.
        return [json_data]

# ################################################################################################################################

    def __call__(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ WSGI entry point for the server using dynamic dispatch based on Werkzeug URL routing.
        """
        # We always need our own new Correlation ID ..
        cid = new_cid_pubsub()

        # .. log what we're doing ..
        path_info = environ.get('PATH_INFO', '').encode('latin1').decode('utf-8', errors='replace')
        if _needs_details:
            logger.info('[%s] Handling request, %s %s', cid, environ.get('REQUEST_METHOD'), path_info)

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

        except ValueError as e:
            logger.warning(f'[{cid}] {e}')
            response = BadRequestResponse()
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
            response = MethodNotAllowedResponse()
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

    def on_health_check(self, environ:'anydict', start_response:'any_') -> 'HealthCheckResponse':
        """ Health check endpoint.
        """
        response = HealthCheckResponse()
        response.is_ok = True
        response.cid = new_cid_pubsub()

        return response

# ################################################################################################################################

    def on_admin_diagnostics(self, cid:'str', environ:'anydict', start_response:'any_') -> 'APIResponse':
        """ Admin diagnostics endpoint - dumps topics, users, subscriptions, etc. to logs in YAML format.
        """
        # Ensure the request is authenticated
        _ = self.authenticate(cid, environ)

        # Collect data for diagnostics
        diagnostics = {
            'topics': {},
            'users': self.users,
            'subscriptions': {},
            'pattern_matcher': {}
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

        # Extract pattern matcher information
        diagnostics['pattern_matcher']['clients'] = {}
        for client_id, client_perms in self.backend.pattern_matcher._clients.items():
            diagnostics['pattern_matcher']['clients'][client_id] = {
                'pub_patterns': [item.pattern for item in client_perms.pub_patterns],
                'sub_patterns': [item.pattern for item in client_perms.sub_patterns]
            }
        diagnostics['pattern_matcher']['cache_size'] = len(self.backend.pattern_matcher._pattern_cache)
        diagnostics['pattern_matcher']['client_count'] = len(self.backend.pattern_matcher._clients)

        # Dump to logs in YAML format
        yaml_output = yaml_dump(diagnostics, default_flow_style=False)
        logger.debug(f'[{cid}] Admin diagnostics: \n{yaml_output}')

        # Return diagnostics data in response
        response = APIResponse()
        response.is_ok = True
        response.cid = cid
        response.details = 'Diagnostics retrieved successfully'
        response.data = diagnostics

        return response

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
            logger.warning(f'Failed to list connections: {response.status_code}, {response.text}')
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

# ################################################################################################################################

    def on_subscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle subscription request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing subscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # .. validate topic name ..
        from zato.common.pubsub.util import validate_topic_name
        validate_topic_name(topic_name)

        # .. check if user has permission to subscribe to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'subscribe')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied subscribe access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # Subscribe to topic using backend
        result = self.backend.register_subscription(cid, topic_name, username=username, should_invoke_server=True)

        response = APIResponse()
        response.cid = cid
        response.is_ok = result.is_ok
        response.status = result.status
        return response

# ################################################################################################################################

    def on_unsubscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle unsubscribe request.
        """
        logger.info(f'[{cid}] Processing unsubscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # .. validate topic name ..
        from zato.common.pubsub.util import validate_topic_name
        validate_topic_name(topic_name)

        # .. check if user has permission to subscribe to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'subscribe')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied subscribe access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # Unsubscribe from topic using backend
        result = self.backend.unregister_subscription(cid, topic_name, username=username)

        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        return response

# ################################################################################################################################

    def run(self) -> 'None':
        """ Run the server using gevent's WSGIServer.
        """
        server = WSGIServer((self.host, self.port), ProxyFix(self))
        logger.info(f'Starting PubSub REST API server on {self.host}:{self.port}')
        server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

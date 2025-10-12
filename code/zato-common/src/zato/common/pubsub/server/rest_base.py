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
import gc
import time
import threading
import psutil
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_IMPLEMENTED, OK, \
    responses as http_responses, UNAUTHORIZED

# orjson
import orjson
from logging import getLogger
from traceback import format_exc

# PyYAML
from yaml import dump as yaml_dump

# prometheus
from prometheus_client import Histogram, Gauge, Counter

# requests
import requests
from requests.auth import HTTPBasicAuth

# gevent
import gevent
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.wrappers import Request

# Zato
from zato.common.api import PubSub
from zato.common.util.api import as_bool, new_cid_pubsub
from zato.common.pubsub.models import APIResponse, _base_response, HealthCheckResponse
from zato.common.pubsub.server.base import BaseServer
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_, list_

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

# This is needed to satisfy the type checker
_BAD_REQUEST = int(BAD_REQUEST) # type: ignore

# Metrics
wsgi_call_time = Histogram('zato_pubsub_wsgi_call_seconds', 'WSGI call processing time')
memory_usage = Gauge('zato_pubsub_memory_bytes', 'Process memory usage')
gc_collections = Counter('zato_pubsub_gc_collections_total', 'GC collections', ['generation'])
gc_objects = Gauge('zato_pubsub_gc_objects', 'GC tracked objects')
gc_objects_by_type = Gauge('zato_pubsub_gc_objects_by_type', 'GC objects by type', ['type'])
thread_count = Gauge('zato_pubsub_threads', 'Active thread count')
greenlet_count = Gauge('zato_pubsub_greenlets', 'Active greenlet count')
socket_wait_time = Histogram('zato_pubsub_socket_wait_seconds', 'Socket wait time')
gil_wait_time = Histogram('zato_pubsub_gil_wait_seconds', 'GIL acquisition time')
request_queue_depth = Gauge('zato_pubsub_request_queue_depth', 'Request queue depth')
fd_count = Gauge('zato_pubsub_file_descriptors', 'Open file descriptors')
context_switches = Counter('zato_pubsub_context_switches_total', 'Context switches', ['type'])
tcp_connections = Gauge('zato_pubsub_tcp_connections', 'TCP connections', ['state'])
cpu_percent = Gauge('zato_pubsub_cpu_percent', 'CPU usage percent')
io_counters = Gauge('zato_pubsub_io_bytes', 'IO bytes', ['direction'])
gevent_request_time = Histogram('zato_pubsub_gevent_request_seconds', 'Gevent WSGI request time')
gevent_queue_time = Histogram('zato_pubsub_gevent_queue_seconds', 'Gevent request queue time')
active_greenlets = Gauge('zato_pubsub_active_greenlets', 'Active greenlets in gevent')

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
        try:
            raw_data = request.get_data()

            if raw_data:
                data = orjson.loads(raw_data)
                return data
            else:
                logger.warning(f'[{cid}] No request data provided')
                return {}

        except Exception:
            raise BadRequestException(cid, f'JSON parsing error: `{format_exc()}`')

# ################################################################################################################################

    def _json_response(self, start_response:'any_', data:'_base_response') -> 'list_[bytes]':
        """ Return a JSON response.
        """

        status_value = data.get('status') or OK
        is_method_not_allowed = status_value == METHOD_NOT_ALLOWED # type: ignore

        response_text = http_responses[status_value] # type: ignore

        # .. build a full status field ..
        status = f'{status_value} {response_text}'

        # .. replace the status we were given on input ..
        data['status'] = status

        # .. drop the fields that may be empty ..
        fields_to_check = ['details', 'msg_id', 'data']

        # .. add fields that should only be dropped if None ..
        for field in ['messages', 'message_count', 'meta', 'messages']:
            value = data.get(field)
            if value is None:
                fields_to_check.append(field)

        for key in fields_to_check:
            if not data.get(key):
                _ = data.pop(key, None)

        # .. now we can serialize it ..
        json_data = orjson.dumps(data)

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

    def _call(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ WSGI entry point for the server using dynamic dispatch based on Werkzeug URL routing.
        """

        # We always need our own new Correlation ID ..
        cid = new_cid_pubsub()

        # Declare response variable with union type
        response:'_base_response'

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

                # Special case for metrics endpoint - it handles its own response
                if endpoint == 'on_metrics':
                    return handler_response

                response_bytes = self._json_response(start_response, handler_response)
                return response_bytes
            else:
                logger.warning(f'No handler for endpoint: {endpoint}')
                response = {
                    'is_ok': False,
                    'cid': cid,
                    'details': 'Endpoint not implemented',
                    'status': NOT_IMPLEMENTED
                }
                return self._json_response(start_response, response)

        except ValueError as e:
            logger.warning(f'[{cid}] {e}')
            response = {
                'is_ok': False,
                'cid': cid,
                'details': 'Invalid request data',
                'status': _BAD_REQUEST,
            }
            return self._json_response(start_response, response)

        except UnauthorizedException:
            response = {
                'is_ok': False,
                'cid': cid,
                'details': 'Unathorized',
                'status': UNAUTHORIZED
            }
            return self._json_response(start_response, response)

        except BadRequestException as e:
            logger.warning(f'[{cid}] {e.message}')
            response = {
                'is_ok': False,
                'cid': cid,
                'details': e.message,
                'status': _BAD_REQUEST
            }
            return self._json_response(start_response, response)

        except MethodNotAllowed as e:
            logger.warning(f'[{cid}] Method not allowed')
            response = {
                'is_ok': False,
                'cid': cid,
                'details': 'Method not allowed',
                'status': METHOD_NOT_ALLOWED
            }
            return self._json_response(start_response, response)

        except NotFound:
            logger.warning('No URL match found for path: %s', environ.get('PATH_INFO'))
            response = {
                'is_ok': False,
                'cid': cid,
                'details': 'URL not found',
                'status': _BAD_REQUEST
            }
            return self._json_response(start_response, response)

        except Exception as e:
            logger.error(f'[{cid}] Unhandled exception: {format_exc()}')
            response = {
                'is_ok': False,
                'cid': cid,
                'details': 'Internal server error',
                'status': INTERNAL_SERVER_ERROR
            }
            return self._json_response(start_response, response)

# ################################################################################################################################

    def __call__(self, environ:'anydict', start_response:'any_') -> 'list_[bytes]':
        """ WSGI entry point for the server using dynamic dispatch based on Werkzeug URL routing.
        """
        start_time = time.time()

        # Update system metrics every 10th request to reduce overhead
        if hasattr(self, '_metrics_counter'):
            self._metrics_counter += 1
        else:
            self._metrics_counter = 1

        if self._metrics_counter % 100 == 0:
            try:
                process = psutil.Process()
                memory_usage.set(process.memory_info().rss)
                thread_count.set(threading.active_count())

                # GC object tracking
                all_objects = gc.get_objects()
                gc_objects.set(len(all_objects))

                # Count objects by type
                type_counts = {}
                for obj in all_objects[:1000]:  # Sample first 1000 to avoid overhead
                    obj_type = type(obj).__name__
                    type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

                for obj_type, count in type_counts.items():
                    gc_objects_by_type.labels(type=obj_type).set(count)

                fd_count.set(process.num_fds())
                cpu_percent.set(process.cpu_percent())

                # IO stats
                io_stats = process.io_counters()
                io_counters.labels(direction='read').set(io_stats.read_bytes)
                io_counters.labels(direction='write').set(io_stats.write_bytes)

                # TCP connections
                connections = process.connections() # type: ignore
                conn_states = {}
                for conn in connections:
                    state = conn.status
                    conn_states[state] = conn_states.get(state, 0) + 1

                for state, count in conn_states.items():
                    tcp_connections.labels(state=state).set(count)

                # Track GC collection counts
                gc_stats = gc.get_stats()
                for i, stat in enumerate(gc_stats):
                    gc_collections.labels(generation=str(i))._value._value = stat['collections']

                ctx_switches = process.num_ctx_switches()
                context_switches.labels(type='voluntary')._value._value = ctx_switches.voluntary
                context_switches.labels(type='involuntary')._value._value = ctx_switches.involuntary

            except Exception:
                logger.error(f'Metrics collection error: {format_exc()}')

        with wsgi_call_time.time():
            result = self._call(environ, start_response)

        # Measure total time including metrics overhead
        total_time = time.time() - start_time
        if total_time > 0.001:  # Log if overhead > 1ms
            pass

        return result

# ################################################################################################################################

    def on_status_check(self, cid:'str', environ:'anydict', start_response:'any_') -> 'HealthCheckResponse':
        """ Status check endpoint for load balancer health checks.
        """
        response:'HealthCheckResponse' = {
            'status': OK
        }

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
        response:'APIResponse' = {
            'is_ok': True,
            'cid': cid,
            'data': diagnostics
        }

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
        result = self.backend.register_subscription(cid, topic_name, username=username, should_invoke_server=True, source_server_type=self.server_type)

        response:'APIResponse' = {
            'cid': cid,
            'is_ok': result['is_ok'],  # type: ignore
            'status': result['status']  # type: ignore
        }
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
        result = self.backend.unregister_subscription(cid, topic_name, username=username, source_server_type=self.server_type)

        response:'APIResponse' = {
            'is_ok': result['is_ok'],  # type: ignore
            'cid': cid
        }

        return response

# ################################################################################################################################

    def _wsgi_wrapper(self, environ, start_response):
        """ WSGI wrapper to measure gevent-level timing.
        """
        try:
            # Track active greenlets
            active_greenlets.set(len(gevent._get_hub().loop._callbacks))

            with gevent_request_time.time():
                result = self._call(environ, start_response)

            return result
        except Exception:
            return self._call(environ, start_response)

    def run(self) -> 'None':
        """ Run the server using gevent's WSGIServer.
        """
        def wsgi_wrapper(environ, start_response):
            start_time = time.time()
            try:
                result = self(environ, start_response)
                return result
            finally:
                duration = time.time() - start_time
                gevent_request_time.observe(duration)

        server = WSGIServer((self.host, self.port), wsgi_wrapper)
        logger.info(f'Starting PubSub REST API server on {self.host}:{self.port}')
        server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

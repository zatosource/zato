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
from json import dumps, loads
from logging import getLogger
from yaml import dump as yaml_dump

# Zato
from zato.common.typing_ import any_, anydict, dict_, list_, strnone
from zato.common.util.auth import check_basic_auth, extract_basic_auth

# gevent
from gevent.pywsgi import WSGIServer

# gunicorn
from gunicorn.app.base import BaseApplication

# werkzeug
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import PubSub
from zato.common.util.api import new_cid
from zato.common.pubsub.models import PubMessage
from zato.common.pubsub.models import APIResponse, BadRequestResponse, HealthCheckResponse, NotImplementedResponse, \
    UnauthorizedResponse
from zato.common.pubsub.backend import Backend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, dictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

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
    def __init__(self, host:'str', port:'int', users_file:'any_'=None) -> 'None':
        self.host = host
        self.port = port
        self.users = load_users(users_file) if users_file else {}

        # Initialize the broker client
        self.broker_client = BrokerClient()

        # Initialize the backend
        self.backend = Backend(self.broker_client)

        # Share references for backward compatibility and simpler access
        self.topics = self.backend.topics
        self.subs_by_topic = self.backend.subs_by_topic

        # URL routing configuration
        self.url_map = Map([
            Rule('/pubsub/health', endpoint='on_health_check', methods=['GET']),
            Rule('/pubsub/topic/<topic_name>', endpoint='on_publish', methods=['POST']),
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='on_subscribe', methods=['POST']),
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='on_unsubscribe', methods=['DELETE']),
            Rule('/pubsub/admin/diagnostics', endpoint='on_admin_diagnostics', methods=['GET']),
        ])

        # Set up all the initial objects
        self.setup()

# ################################################################################################################################

    def _load_subscriptions(self) -> 'None':

        service = 'zato.pubsub.subscription.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True
        }

        response = self.backend.invoke_service(service, request)

        for item in response:
            print()
            print(333, item)
            print()

# ################################################################################################################################

    def setup(self) -> 'None':

        # Load up all the initial subscriptions
        self._load_subscriptions()

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
        result = self.backend.subscribe_impl(cid, topic_name, username)

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
        result = self.backend.unsubscribe_impl(cid, topic_name, username)

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

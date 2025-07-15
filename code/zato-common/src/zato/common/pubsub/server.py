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
from traceback import format_exc
from yaml import dump as yaml_dump, safe_load as yaml_load

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

def load_users_json(users_file:'str') -> 'strdict':
    """ Load users from a JSON file.
    """
    logger.info(f'Loading users from JSON file {users_file}')

    try:
        with open(users_file, 'r') as f:
            data = f.read()
            users_list = loads(data)

        # Convert the list of single-pair dicts to a single dict
        users = {}
        for user_dict in users_list:
            for username, password in user_dict.items():
                users[username] = password

        count = len(users)
        if count == 1:
            logger.info('Loaded 1 user')
        else:
            logger.info(f'Loaded {count} users')
        return users

    except Exception as e:
        logger.error(f'Error loading users from JSON: {e}')
        return {}

# ################################################################################################################################
# ################################################################################################################################

def load_yaml_config(yaml_file:'str') -> 'dict_':
    """ Load configuration from a YAML file including users, topics, and subscriptions.
    """
    logger.info(f'Loading configuration from YAML file {yaml_file}')

    try:
        with open(yaml_file, 'r') as f:
            config = yaml_load(f)

        return config

    except Exception as e:
        logger.error(f'Error loading YAML configuration: {e}')
        return {}

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServer:
    """ Main server class for the Pub/Sub REST API.
    """
    def __init__(self, host:'str', port:'int', users_file:'any_'=None, yaml_config_file:'any_'=None) -> 'None':
        self.host = host
        self.port = port

        # Initialize configuration variables
        self.users = {}
        self.yaml_config = None

        # Load users from JSON if provided
        if users_file and users_file.endswith('.json'):
            self.users = load_users_json(users_file)

        # Load configuration from YAML if provided
        if yaml_config_file and yaml_config_file.endswith('.yaml'):
            self.yaml_config = load_yaml_config(yaml_config_file)

            # Extract users from YAML config if present
            if self.yaml_config:
                self.users.update(self.yaml_config['users'])
                logger.info(f'Updated users from YAML config, total users: {len(self.users)}')

        # Initialize the broker client
        self.broker_client = BrokerClient()

        # Initialize the backend
        self.backend = Backend(self, self.broker_client)

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

# ################################################################################################################################

    def _load_users(self, cid:'str') -> 'None':
        """ Load initial users from server.
        """

        # Prepare our input ..
        service = 'zato.security.basic-auth.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True
        }

        # .. invoke the service ..
        response = self.backend.invoke_service(service, request)

        # .. log what we've received ..
        if len_response := len(response):
            logger.info('Loading 1 user')
        else:
            logger.info(f'Loading {len_response} users')

        # .. process each subscription ..
        for item in response:

            # .. extract what we need ..
            username = item['username']
            password = item['password']

            # .. and create a user ..
            self.create_user(cid, username, password)

# ################################################################################################################################

    def _load_subscriptions(self, cid:'str') -> 'None':
        """ Load subscriptions from server and set up the pub/sub structure.
        """

        # Prepare our input ..
        service = 'zato.pubsub.subscription.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True
        }

        # .. invoke the service ..
        response = self.backend.invoke_service(service, request)

        # .. log what we've received ..
        if len_response := len(response):
            logger.info('Loading 1 subscription')
        else:
            logger.info(f'Loading {len_response} subscriptions')

        # .. process each subscription ..
        for item in response:

            try:
                # .. extract what we need ..
                sec_name = item['sec_name']
                username = item['username']
                password = item['password']
                topic_names = item.get('topic_names') or ''
                sub_key = item['sub_key']

                # Add user credentials
                self.create_user(cid, username, password)

                # Handle multiple topics (comma-separated)
                for topic_name in topic_names.split(','):
                    topic_name = topic_name.strip()
                    if not topic_name:
                        continue

                    logger.info(f'[{cid}] Setting up subscription: `{username}` -> `{topic_name}`')

                    # Create the subscription
                    _ = self.backend.subscribe_impl(cid, topic_name, sec_name, sub_key)

            except Exception:
                logger.error(f'[{cid}] Error processing subscription {item}: {format_exc()}')

        logger.info('Finished loading subscriptions')

# ################################################################################################################################

    def _setup_from_yaml_config(self, cid:'str') -> 'None':
        """ Set up users, topics, and subscriptions based on YAML configuration.
        """
        if not self.yaml_config:
            return

        logger.info(f'[{cid}] Setting up from YAML configuration')

        # Process users section
        users_config = self.yaml_config['users']
        for username, password in users_config.items():
            self.create_user(cid, username, password)

        # Process topics section
        topics_config = self.yaml_config['topics']
        for topic_data in topics_config.values():
            topic_name = topic_data['name']
            if topic_name not in self.backend.topics:
                self.backend.create_topic(cid, 'yaml-config', topic_name)
                logger.info(f'[{cid}] Created topic: {topic_name}')

        # Process subscriptions section
        subs_config = self.yaml_config['subscriptions']
        for topic_name, users_data in subs_config.items():

            # Make sure the topic exists
            if topic_name not in self.backend.topics:
                self.backend.create_topic(cid, 'yaml-config-subscription', topic_name)
                logger.info(f'[{cid}] Created topic for subscription: {topic_name}')

            # Process each user subscription for this topic
            for username, sub_data in users_data.items():

                # Get the subscription key
                sub_key = sub_data['sub_key']

                # Create the subscription
                logger.info(f'[{cid}] Setting up subscription from YAML: {username} -> {topic_name} (key={sub_key})')
                _ = self.backend.subscribe_impl(cid, topic_name, username, sub_key)

        logger.info(f'[{cid}] Finished setting up from YAML configuration')

# ################################################################################################################################

    def create_user(self, cid:'str', username:'str', password:'str') -> 'None':
        if username not in self.users:
            logger.info(f'[{cid}] Adding user credentials for `{username}`')
            self.users[username] = password
        else:
            logger.debug(f'[{cid}] User already exists: `{username}`')

# ################################################################################################################################

    def change_username(self, cid:'str', old_username:'str', new_username:'str') -> 'None':

        if old_username not in self.users:
            logger.info(f'[{cid}] User not found: `{old_username}`')
            return

        if new_username in self.users:
            logger.info(f'[{cid}] Cannot change username, target already exists: `{new_username}`')
            return

        # Store the password
        password = self.users[old_username]

        # Create the new user entry
        self.users[new_username] = password

        # Remove the old username
        del self.users[old_username]

        logger.info(f'[{cid}] Changed username from `{old_username}` to `{new_username}`')

# ################################################################################################################################

    def setup(self) -> 'None':

        # Reusable
        cid = new_cid()

        # Start the subscriber for internal commands
        self.backend.start_internal_subscriber()

        # Load test data
        self._setup_from_yaml_config(cid)

        # Load all the initial users
        self._load_users(cid)

        # Load all the initial subscriptions
        self._load_subscriptions(cid)

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

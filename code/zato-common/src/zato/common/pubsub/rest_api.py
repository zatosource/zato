# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import datetime
import json
import logging
import os
from http import HTTPStatus
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import unquote

# gevent
from gevent import spawn
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

# Zato
from zato.common.typing_ import any_, anynone
from zato.common.util.api import new_cid
from zato.common.pubsub.models import MessageData
from zato.common.pubsub.subscription import SubscriptionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TypeAlias
    from werkzeug.routing import Map as WerkzeugMap

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.pubsub.rest')

# ################################################################################################################################
# ################################################################################################################################

class AuthMiddleware:
    """ Middleware for HTTP Basic Authentication.
    """
    
    def __init__(self, users: Dict[str, str], app):
        self.users = users
        self.app = app
        
    def __call__(self, environ, start_response):
        request = Request(environ)
        auth = request.headers.get('Authorization')
        
        if not auth or not auth.startswith('Basic '):
            return self._unauthorized(start_response)
            
        # Decode and validate credentials
        try:
            auth_decoded = base64.b64decode(auth[6:]).decode('utf-8')
            username, password = auth_decoded.split(':', 1)
            
            if username not in self.users or self.users[username] != password:
                return self._unauthorized(start_response)
                
            # Store the authenticated username in the environment
            environ['AUTH_USERNAME'] = username
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return self._unauthorized(start_response)
            
        return self.app(environ, start_response)
        
    def _unauthorized(self, start_response):
        response = Response('Unauthorized', status=401)
        response.headers['WWW-Authenticate'] = 'Basic realm="Zato PubSub"'
        return response(environ={}, start_response=start_response)

# ################################################################################################################################
# ################################################################################################################################

class RESTAPIServer:
    """ REST API server for RabbitMQ pub/sub using gevent and werkzeug.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, 
                 users: Dict[str, str] = None,
                 broker_client=None) -> 'None':
        self.host = host
        self.port = port
        self.users = users or {}
        self.subscription_manager = SubscriptionManager()
        self.broker_client = broker_client  # AMQP broker client for external messaging
        self.server = None
        self.url_map = self._create_url_map()
        
        logger.info(f'REST API server initialized on {host}:{port}')
        
    def _create_url_map(self) -> 'WerkzeugMap':
        """ Creates the URL routing map.
        """
        return Map([
            Rule('/topic/<topic_name>', endpoint='publish_message', methods=['POST']),
            Rule('/topic/<topic_name>', endpoint='retrieve_messages', methods=['PATCH']),
            Rule('/topic/<topic_name>', endpoint='read_messages', methods=['GET']),
            Rule('/subscribe/topic/<topic_name>', endpoint='subscribe_topic', methods=['PUT']),
            Rule('/subscribe/topic/<topic_name>', endpoint='unsubscribe_topic', methods=['DELETE']),
        ])
        
    def _get_endpoint_name(self, environ: Dict) -> str:
        """ Gets the endpoint name from the request environment.
        """
        return environ.get('AUTH_USERNAME', 'unknown')
        
    def _parse_json(self, request: Request) -> Dict:
        """ Parse JSON request body.
        """
        try:
            return json.loads(request.data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            raise BadRequest(f"Invalid JSON: {e}")
            
    def publish_message(self, request: Request, topic_name: str) -> Response:
        """ Publish a message to a topic.
        """
        endpoint_name = self._get_endpoint_name(request.environ)
        data = self._parse_json(request)
        
        if not data:
            raise BadRequest("Message body is required")
            
        # Create a message
        now = datetime.datetime.utcnow()
        now_iso = now.isoformat()
        
        # Get message expiration (in seconds)
        expiration = int(data.get('expiration', 86400))  # Default 24 hours
        expiration_time = now + datetime.timedelta(seconds=expiration)
        expiration_time_iso = expiration_time.isoformat()
        
        # Create the message
        message = MessageData(
            msg_id=new_cid(),
            topic_name=topic_name,
            correl_id=data.get('correl_id'),
            in_reply_to=data.get('in_reply_to'),
            priority=data.get('priority', 5),
            mime_type=data.get('mime_type', 'application/json'),
            ext_client_id=endpoint_name,
            pub_time_iso=now_iso,
            ext_pub_time_iso=data.get('ext_pub_time_iso', now_iso),
            recv_time_iso=now_iso,
            expiration=expiration,
            expiration_time_iso=expiration_time_iso,
            size=len(json.dumps(data.get('data', ''))),
            data=data.get('data')
        )
        
        # Publish the message locally to subscribers
        subscription_ids = self.subscription_manager.publish_message(topic_name, message)
        
        # If we have a broker client, also publish to AMQP
        amqp_published = False
        if self.broker_client:
            try:
                # Convert MessageData to format suitable for BrokerClient
                amqp_msg = {
                    'msg_id': message.msg_id,
                    'topic_name': topic_name,
                    'data': message.data,
                    'mime_type': message.mime_type,
                    'priority': message.priority,
                    'expiration': message.expiration,
                    'correl_id': message.correl_id,
                    'in_reply_to': message.in_reply_to,
                }
                
                # Publish to AMQP
                self.broker_client.publish(amqp_msg)
                logger.info(f'Message {message.msg_id} published to AMQP topic {topic_name}')
                amqp_published = True
                
            except Exception as e:
                logger.error(f'Failed to publish message to AMQP: {e}', exc_info=True)
        
        # Return the result
        return Response(
            json.dumps({
                'msg_id': message.msg_id,
                'status': 'OK',
                'subscriptions_delivered': len(subscription_ids),
                'amqp_published': amqp_published
            }),
            status=201,
            content_type='application/json'
        )
        
    def retrieve_messages(self, request: Request, topic_name: str) -> Response:
        """ Retrieve and remove messages from a topic.
        """
        endpoint_name = self._get_endpoint_name(request.environ)
        
        # Get messages (destructive)
        messages = self.subscription_manager.get_messages(topic_name, endpoint_name, destructive=True)
        
        # Convert to dictionary for JSON
        message_dicts = [msg.to_dict() for msg in messages]
        
        # Return the messages
        return Response(
            json.dumps({
                'messages': message_dicts,
                'message_count': len(messages)
            }),
            content_type='application/json'
        )
        
    def read_messages(self, request: Request, topic_name: str) -> Response:
        """ Read messages non-destructively from a topic.
        """
        endpoint_name = self._get_endpoint_name(request.environ)
        
        # Get messages (non-destructive)
        messages = self.subscription_manager.get_messages(topic_name, endpoint_name, destructive=False)
        
        # Convert to dictionary for JSON
        message_dicts = [msg.to_dict() for msg in messages]
        
        # Return the messages
        return Response(
            json.dumps({
                'messages': message_dicts,
                'message_count': len(messages)
            }),
            content_type='application/json'
        )
        
    def subscribe_topic(self, request: Request, topic_name: str) -> Response:
        """ Subscribe to a topic.
        """
        endpoint_name = self._get_endpoint_name(request.environ)
        
        # Get patterns from request body
        data = {}
        try:
            if request.data:
                data = self._parse_json(request)
        except:
            # Ignore JSON parsing errors for empty bodies
            pass
            
        patterns = data.get('patterns', [topic_name])
        
        # Subscribe
        subscription = self.subscription_manager.subscribe(topic_name, endpoint_name, patterns)
        
        # Return the result
        return Response(
            json.dumps({
                'sub_id': subscription.sub_id,
                'topic_name': subscription.topic_name,
                'patterns': subscription.patterns,
                'status': 'SUBSCRIBED'
            }),
            status=201,
            content_type='application/json'
        )
        
    def unsubscribe_topic(self, request: Request, topic_name: str) -> Response:
        """ Unsubscribe from a topic.
        """
        endpoint_name = self._get_endpoint_name(request.environ)
        
        # Unsubscribe
        success = self.subscription_manager.unsubscribe(topic_name, endpoint_name)
        
        if not success:
            # No subscription found
            return Response(
                json.dumps({
                    'status': 'NOT_FOUND',
                    'message': f'No subscription found for topic {topic_name}'
                }),
                status=404,
                content_type='application/json'
            )
        
        # Return the result
        return Response(
            json.dumps({
                'status': 'UNSUBSCRIBED',
                'topic_name': topic_name
            }),
            content_type='application/json'
        )
        
    def dispatch_request(self, request: Request) -> Response:
        """ Dispatch the request to the correct handler.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)
            return handler(request, **values)
        except NotFound:
            return Response(json.dumps({'error': 'Not Found'}), status=404, content_type='application/json')
        except BadRequest as e:
            return Response(json.dumps({'error': str(e)}), status=400, content_type='application/json')
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return Response(
                json.dumps({'error': 'Internal Server Error'}),
                status=500,
                content_type='application/json'
            )
            
    def wsgi_app(self, environ, start_response):
        """ WSGI application.
        """
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
        
    def __call__(self, environ, start_response):
        """ WSGI entry point.
        """
        return self.wsgi_app(environ, start_response)
        
    def start(self):
        """ Start the server.
        """
        # Create the WSGI server
        app = self.wsgi_app
        
        # Apply authentication if users are provided
        if self.users:
            app = AuthMiddleware(self.users, app)
            
        self.server = WSGIServer((self.host, self.port), app)
        
        # Start the server in a separate greenlet
        spawn(self.server.serve_forever)
        logger.info(f'REST API server started on {self.host}:{self.port}')
        
    def stop(self):
        """ Stop the server.
        """
        if self.server:
            self.server.stop()
            logger.info('REST API server stopped')

# ################################################################################################################################
# ################################################################################################################################

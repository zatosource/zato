# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import spawn
from gevent.lock import RLock
from gevent.pywsgi import WSGIServer

# werkzeug
from werkzeug.exceptions import BadRequest
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

# Zato
from zato.common.test.zato.common.pubsub.models import Message, TestCollector, QueueStats
from zato.common.test.zato.common.pubsub.config import AppConfig
from zato.common.test.zato.common.pubsub.report import generate_html_report

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from typing import Any, Dict, List, Optional
    from werkzeug.wrappers import Request, Response
    
    # Define type aliases
    Any = Any
    Dict = Dict
    Optional = Optional

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestServer:
    """ Test server for PubSub message collection and reporting.
    """
    
    def __init__(self, config:'AppConfig') -> 'None':
        """ Initialize server with configuration.
        """
        self.config = config
        self.lock = RLock()
        self.collector = TestCollector(expected_count=config.collection.expected_message_count)
        self.last_message_time = datetime.utcnow()
        
        # Setup URL routes
        self.url_map = Map([
            Rule('/messages', endpoint='messages'),
            Rule('/report', endpoint='report'),
            Rule('/status', endpoint='status'),
        ])
    
    def on_messages(self, request:'Request') -> 'Response':
        """ Handle incoming message POST requests.
        """
        # Must be POST method
        if request.method != 'POST':
            return Response('Method not allowed, use POST', status=405)
            
        try:
            # Parse the JSON body
            data = loads(request.data)
            
            # Create message object from request
            message = Message(
                message_id=data.get('message_id', ''),
                publication_time=datetime.fromisoformat(data.get('publication_time', '')),
                publisher_name=data.get('publisher_name', ''),
                topic_name=data.get('topic_name', ''),
                queue_name=data.get('queue_name', ''),
                priority=int(data.get('priority', 0)),
                expiration=int(data.get('expiration', 0)),
                content=data.get('content'),
                received_time=datetime.utcnow()
            )
            
            with self.lock:
                # Add message to collector
                added = self.collector.add_message(message)
                self.last_message_time = datetime.utcnow()
                
                # Check if we've reached expected count
                if self.collector.is_complete() and not self.collector.end_time:
                    self.collector.complete_test()
                    logger.info(f'Test complete! Collected {self.collector.received_count} messages')
                
                # Log progress at intervals
                if (self.collector.received_count % self.config.collection.log_interval == 0) and added:
                    self._log_progress()
                    
            # Return response with current count
            response_data = {
                'status': 'ok',
                'received': self.collector.received_count,
                'expected': self.collector.expected_count,
                'complete': self.collector.is_complete(),
            }
            return Response(dumps(response_data), content_type='application/json')
            
        except Exception as e:
            logger.error(f'Error processing message: {e}')
            logger.error(format_exc())
            
            # Increment malformed count
            with self.lock:
                self.collector.increment_malformed()
                
            # Return error response
            return Response(
                dumps({'status': 'error', 'message': str(e)}), 
                content_type='application/json',
                status=400
            )

    def on_report(self, request:'Request') -> 'Response':
        """ Generate and return HTML report.
        """
        with self.lock:
            html_report = generate_html_report(self.collector)
            
        return Response(html_report, content_type='text/html')
    
    def on_status(self, request:'Request') -> 'Response':
        """ Return current test status.
        """
        with self.lock:
            status_data = {
                'received_count': self.collector.received_count,
                'expected_count': self.collector.expected_count,
                'complete': self.collector.is_complete(),
                'duration_seconds': self.collector.get_duration_seconds(),
                'message_rate': self.collector.get_message_rate(),
                'duplicate_count': self.collector.duplicate_count,
                'malformed_count': self.collector.malformed_count,
            }
            
        return Response(dumps(status_data), content_type='application/json')
    
    def dispatch_request(self, request:'Request') -> 'Response':
        """ Dispatch request to appropriate handler.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            if endpoint == 'messages':
                return self.on_messages(request)
            elif endpoint == 'report':
                return self.on_report(request)
            elif endpoint == 'status':
                return self.on_status(request)
            else:
                return Response('Not found', status=404)
                
        except BadRequest as e:
            return Response(str(e), status=400)
            
        except Exception as e:
            logger.error(f'Error handling request: {e}')
            logger.error(format_exc())
            return Response(f'Internal server error: {str(e)}', status=500)
    
    def wsgi_app(self, environ:'dict', start_response:'callable') -> 'list':
        """ WSGI application entry point.
        """
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def __call__(self, environ:'dict', start_response:'callable') -> 'list':
        """ Make the class callable as a WSGI application.
        """
        return self.wsgi_app(environ, start_response)
    
    def _check_timeout(self) -> 'None':
        """ Periodically check if the test has timed out.
        """
        while not self.collector.is_complete():
            # Calculate time since last message
            seconds_since_last = (datetime.utcnow() - self.last_message_time).total_seconds()
            
            # If timeout exceeded, complete the test
            if seconds_since_last >= self.config.collection.timeout_seconds:
                with self.lock:
                    if not self.collector.is_complete() and not self.collector.end_time:
                        logger.warning(f'Test timeout after {seconds_since_last:.1f} seconds of inactivity')
                        self.collector.complete_test()
                        break
            
            # Sleep before checking again
            gevent.sleep(5)
    
    def _log_progress(self) -> 'None':
        """ Log the current progress of message collection.
        """
        count = self.collector.received_count
        total = self.collector.expected_count
        percentage = (count / total) * 100 if total > 0 else 0
        rate = self.collector.get_message_rate()
        
        logger.info(f'Received {count}/{total} messages ({percentage:.1f}%) - Current rate: {rate:.1f} msgs/sec')
    
    def run(self) -> 'None':
        """ Run the test server.
        """
        # Start timeout checker in a separate greenlet
        spawn(self._check_timeout)
        
        # Create and start the WSGI server
        host = self.config.server.host
        port = self.config.server.port
        server = WSGIServer((host, port), self)
        
        logger.info(f'PubSub Test Server starting on {host}:{port}')
        logger.info(f'Expecting {self.collector.expected_count} messages')
        logger.info(f'Report will be available at http://{host}:{port}{self.config.report.url_path}')
        
        server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

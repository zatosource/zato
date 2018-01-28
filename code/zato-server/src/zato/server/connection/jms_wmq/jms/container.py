# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# stdlib
import logging
import sys
from json import loads
from logging import basicConfig, DEBUG, Formatter, getLogger, INFO, StreamHandler
from logging.handlers import RotatingFileHandler
from os import getpid, getppid, path
from thread import start_new_thread
from threading import RLock
from traceback import format_exc
from wsgiref.simple_server import make_server
import httplib

# Bunch
from bunch import Bunch, bunchify

# ThreadPool
from threadpool import ThreadPool, WorkRequest, NoResultsPending

# YAML
import yaml

# Zato
from zato.common.auth_util import parse_basic_auth
from zato.common.broker_message import code_to_name, DEFINITION
from zato.common.zato_keyutils import KeyUtils
from zato.server.connection.jms_wmq.jms import WebSphereMQException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage

# ################################################################################################################################

default_logging_config = {
    'loggers': {
        'zato_websphere_mq': {
            'qualname': 'zato_websphere_mq', 'level': 'INFO', 'propagate': False, 'handlers': ['websphere_mq']}
    },
    'handlers': {
        'websphere_mq': {
            'formatter': 'default', 'backupCount': 10, 'mode': 'a', 'maxBytes': 20000000, 'filename': './logs/websphere-mq.log'
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'}
    }
}

# ################################################################################################################################

_http_200 = b'{} {}'.format(httplib.OK, httplib.responses[httplib.OK])
_http_400 = b'{} {}'.format(httplib.BAD_REQUEST, httplib.responses[httplib.BAD_REQUEST])
_http_403 = b'{} {}'.format(httplib.FORBIDDEN, httplib.responses[httplib.FORBIDDEN])
_http_406 = b'{} {}'.format(httplib.NOT_ACCEPTABLE, httplib.responses[httplib.NOT_ACCEPTABLE])
_http_500 = b'{} {}'.format(httplib.INTERNAL_SERVER_ERROR, httplib.responses[httplib.INTERNAL_SERVER_ERROR])
_http_503 = b'{} {}'.format(httplib.SERVICE_UNAVAILABLE, httplib.responses[httplib.SERVICE_UNAVAILABLE])

_path_api = '/api'
_path_ping = '/ping'

_paths = (_path_api, _path_ping)

# ################################################################################################################################

class Response(object):
    def __init__(self, status=_http_200, data=b'', content_type='text/json'):
        self.status = status
        self.data = data
        self.content_type = content_type

# ################################################################################################################################

class WebSphereMQTask(object):
    """ A process to listen for messages and to send them to WebSphere MQ queue managers.
    """
    def __init__(self, conn, on_message_callback, max_chars_printed):
        self.conn = conn
        self.on_message_callback = on_message_callback
        self.max_chars_printed = max_chars_printed
        self.handlers_pool = ThreadPool(5)
        self.keep_running = True
        self.has_debug = self.logger.isEnabledFor(DEBUG)

# ################################################################################################################################

    def _get_destination_info(self):
        return 'destination:`%s`, %s' % (self.destination, self.conn.get_connection_info())

# ################################################################################################################################

    def send(self, payload, queue_name):
        return self.conn.send(TextMessage(payload), queue_name)

# ################################################################################################################################

    def listen_for_messages(self, queue_name):
        """ Runs a background queue listener in its own  thread.
        """
        def _impl():
            while self.keep_running:
                try:
                    message = self.conn.receive(queue_name, 1000)
                    if self.has_debug:
                        self.logger.debug('Message received `%s`' % str(message).decode('utf-8'))

                    work_request = WorkRequest(self.on_message_callback, [message])
                    self.handlers_pool.putRequest(work_request)

                    try:
                        self.handlers_pool.poll()
                    except NoResultsPending, e:
                        pass

                except NoMessageAvailableException, e:
                    if self.has_debug:
                        self.logger.debug('Consumer did not receive a message. `%s`' % self._get_destination_info())

                except WebSphereMQException, e:
                    self.logger.error('%s in run, completion_code:`%s`, reason_code:`%s`' % (
                        e.__class__.__name__, e.completion_code, e.reason_code))
                    raise

        # Start listener in a thread
        start_new_thread(_impl, ())

# ################################################################################################################################

class ConnectionContainer(object):
    def __init__(self):

        # PyMQI is an optional dependency so let's import it here rather than on module level
        import pymqi
        self.pymqi = pymqi

        self.host = '127.0.0.1'
        self.port = None
        self.username = None
        self.password = None
        self.basic_auth_expected = None
        self.server_pid = None
        self.server_name = None
        self.cluster_name = None

        self.lock = RLock()
        self.logger = None
        self.parent_pid = getppid()
        self.keyutils = KeyUtils('zato-wmq', self.parent_pid)

        self.connections = {}
        self.outconns = {}
        self.channels = {}

        self.outconn_id_to_def_id = {} # Maps outgoing connection IDs to their underlying definition IDs
        self.channel_id_to_def_id = {} # Ditto but for channels

        self.set_config()

    def set_config(self):
        """ Sets self attributes, as configured in keyring by our parent process.
        """
        config = self.keyutils.user_get()
        config = loads(config)
        config = bunchify(config)

        self.username = config.username
        self.password = config.password
        self.server_pid = config.server_pid
        self.server_name = config.server_name
        self.cluster_name = config.cluster_name
        self.base_dir = config.base_dir
        self.port = config.port

        with open(config.logging_conf_path) as f:
            logging_config = yaml.load(f)

        # WebSphere MQ logging configuration is new in Zato 3.0, so it's optional.
        if not 'zato_websphere_mq' in logging_config['loggers']:
            logging_config = default_logging_config

        self.set_up_logging(logging_config)

# ################################################################################################################################

    def set_up_logging(self, config):

        logger_conf = config['loggers']['zato_websphere_mq']
        wmq_handler_conf = config['handlers']['websphere_mq']
        del wmq_handler_conf['formatter']
        del wmq_handler_conf['class']
        formatter_conf = config['formatters']['default']['format']

        self.logger = getLogger(logger_conf['qualname'])
        self.logger.setLevel(getattr(logging, logger_conf['level']))

        formatter = Formatter(formatter_conf)

        wmq_handler_conf['filename'] = path.abspath(path.join(self.base_dir, wmq_handler_conf['filename']))
        wmq_handler = RotatingFileHandler(**wmq_handler_conf)
        wmq_handler.setFormatter(formatter)

        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        self.logger.addHandler(wmq_handler)
        self.logger.addHandler(stdout_handler)

# ################################################################################################################################

    def on_mq_message_received(self, msg):
        self.logger.info('MQ message received %s', msg)

# ################################################################################################################################

    def add_channel(self, config):
        with self.lock:

            task = WebSphereMQTask(conn, self.on_mq_message_received)
            task.listen_for_messages('DEV.QUEUE.1')

            import time
            time.sleep(1)

            for x in range(40):
                task.send('aaa', 'DEV.QUEUE.1')

            time.sleep(2)

            #print(conn.receive('DEV.QUEUE.1', 100))

# ################################################################################################################################

    def _create_definition(self, msg, needs_connect=True):
        """ A low-level method to create connection definitions. Must be called with self.lock held.
        """
        conn_name = msg.pop('name')
        msg.pop('cluster_id', None)
        msg.pop('old_name', None)
        id = msg.pop('id')
        msg['needs_jms'] = msg.pop('use_jms', False)
        max_chars_printed = msg.pop('max_chars_printed')

        # We always create and add a connetion ..
        conn = WebSphereMQConnection(**msg)
        self.connections[id] = conn

        # .. because even if it fails here, it will be eventually established during one of .send or .receive,
        # however, it is possible that our caller already knows that the connection will fail so we need
        # to take it into account too.
        if needs_connect:
            conn.connect()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_CREATE(self, msg):
        """ Creates a new connection to WebSphere MQ.
        """
        with self.lock:
            try:
                self._create_definition(msg)
            except Exception as e:
                self.logger.warn(format_exc())
                return Response(_http_503, str(e.message))
            else:
                return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_EDIT(self, msg):
        """ Updates an existing definition - close the current one, including channels and outconns,
        and creates a new one in its place.
        """
        with self.lock:
            connection = self.connections[msg.id]

            # Edit messages don't carry passwords
            msg.password = connection.password

            # It's possible that we are editing a connection that has no connected yet,
            # e.g. if password was invalid, so this needs to be guarded by an if.
            if connection.is_connected:
                self.connections[msg.id].close()

            # Overwrites the previous connection object
            self._create_definition(msg, connection.is_connected)

            return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_DELETE(self, msg):
        """ Deletes a WebSphere MQ definition along with its associated outconns and channels.
        """
        with self.lock:
            def_id = msg.id

            # Stop all connections ..
            try:
                self.connections[def_id].close()
            except Exception as e:
                self.logger.warn(format_exc())
            finally:
                try:
                    del self.connections[def_id]
                except Exception:
                    self.logger.warn(format_exc())

                # .. continue to delete outconns regardless of errors above ..
                for outconn_id, outconn_def_id in self.outconn_id_to_def_id.items():
                    if outconn_def_id == def_id:
                        del self.outconn_id_to_def_id[outconn_id]
                        del self.outconns[outconn_id]

                # .. delete channels too.
                for channel_id, channel_def_id in self.channel_id_to_def_id.items():
                    if channel_def_id == def_id:
                        del self.channel_id_to_def_id[channel_id]
                        del self.channels[channel_id]

            return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_CHANGE_PASSWORD(self, msg):
        with self.lock:
            try:
                conn = self.connections[msg.id]
                conn.close()
                conn.password = msg.password1
                conn.connect()
            except Exception as e:
                self.logger.warn(format_exc())
                return Response(_http_503, str(e.message), 'text/plain')
            else:
                return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_PING(self, msg):
        """ Pings a remote WebSphere MQ manager.
        """
        try:
            self.connections[msg.id].ping()
        except WebSphereMQException, e:
            return Response(_http_503, str(e.message), 'text/plain')
        else:
            return Response()

# ################################################################################################################################

    def _create_outconn(self, msg):
        """ A low-level method to create an outgoing connection. Must be called with self.lock held.
        """
        # Just to be on the safe side, make sure that our connection exists
        if not msg.def_id in self.connections:
            return Response(_http_503, 'Could not find def_id among {}'.format(self.connections.keys()), 'text/plain')

        # Map outconn to its definition
        self.outconn_id_to_def_id[msg.id] = msg.def_id

        # Create the outconn now
        self.outconns[msg.id] = msg

        # Everything OK
        return Response()

# ################################################################################################################################

    def _delete_outconn(self, msg):
        """ A low-level implementation of outconn deletion. Must be called with self.lock held.
        """
        del self.outconns[msg.id]
        del self.outconn_id_to_def_id[msg.id]

# ################################################################################################################################

    def _on_OUTGOING_WMQ_DELETE(self, msg):
        """ Deletes an existing WebSphere MQ outconn.
        """
        with self.lock:
            self._delete_outconn(msg)
            return Response()

# ################################################################################################################################

    def _on_OUTGOING_WMQ_CREATE(self, msg):
        """ Creates a new WebSphere MQ outgoin connections using an already existing definition.
        """
        with self.lock:
            return self._create_outconn(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_EDIT(self, msg):
        """ Updates and existing outconn by deleting and creating it again with latest configuration.
        """
        with self.lock:
            self._delete_outconn(msg)
            return self._create_outconn(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_SEND(self, msg):
        """ Sends a message to a remote WebSphere MQ queue.
        """
        outconn = self.outconns[msg.id]

        if not outconn.is_active:
            return Response(_http_406, 'Cannot send messages through an inactive connection', 'text/plain')
        else:
            conn_id = self.outconn_id_to_def_id[msg.id]
            try:

                delivery_mode = msg.delivery_mode or outconn.delivery_mode
                priority = msg.priority or outconn.priority
                expiration = msg.expiration or outconn.expiration

                self.connections[conn_id].send(TextMessage(
                    text = msg.data,
                    jms_delivery_mode = delivery_mode,
                    jms_priority = priority,
                    jms_expiration = expiration,
                    jms_correlation_id = msg.correl_id,
                    jms_message_id = msg.msg_id,
                    jms_reply_to = msg.reply_to,
                ), msg.queue_name.encode('utf8'))
            except Exception as e:
                self.logger.warn(format_exc())

                if isinstance(e, self.pymqi.MQMIError):
                    message = e.errorAsString()
                else:
                    message = e.message

                return Response(_http_503, message)
            else:
                return Response()

# ################################################################################################################################

    def handle_http_request(self, path, msg, ok=b'OK'):
        """ Dispatches incoming HTTP requests - either reconfigures the connector or puts messages to queues.
        """
        self.logger.info('MSG received %s %s', path, msg)

        if path == _path_ping:
            return Response()
        else:
            msg = bunchify(loads(msg))

            # Delete what handlers don't need
            msg.pop('msg_type', None) # Optional if message was sent by a server that is starting up vs. API call
            action = msg.pop('action')

            handler = getattr(self, '_on_{}'.format(code_to_name[action]))
            return handler(msg)

# ################################################################################################################################

    def check_credentials(self, auth):
        """ Checks incoming username/password and returns True only if they were valid and as expected.
        """
        username, password = parse_basic_auth(auth)

        if username != self.username:
            self.logger.warn('Invalid username or password')
            return

        elif password != self.password:
            self.logger.warn('Invalid username or password')
            return
        else:
            # All good, we let the request in
            return True

# ################################################################################################################################

    def on_wsgi_request(self, environ, start_response):

        # Default values to use in case of any internal errors
        status = _http_503
        content_type = 'text/plain'

        try:
            content_length = environ['CONTENT_LENGTH']
            if not content_length:
                status = _http_400
                data = 'Missing content'
                content_type = 'text/plain'
            else:
                data = environ['wsgi.input'].read(int(content_length))
                if self.check_credentials(environ.get('HTTP_AUTHORIZATION')):
                    response = self.handle_http_request(environ['PATH_INFO'], data)
                    status = response.status
                    data = response.data
                    content_type = response.content_type
                else:
                    status = _http_403
                    data = 'You are not allowed to access this resource'
                    content_type = 'text/plain'

        except Exception as e:
            self.logger.warn(format_exc())
            content_type = 'text/plain'
            status = _http_500
            data = 'Internal server error'
        finally:
            headers = [('Content-type', content_type)]
            start_response(status, headers)

            return [data]

# ################################################################################################################################

    def run(self):
        server = make_server(self.host, self.port, self.on_wsgi_request)
        server.serve_forever()

# ################################################################################################################################

if __name__ == '__main__':

    container = ConnectionContainer()
    container.run()

# ################################################################################################################################

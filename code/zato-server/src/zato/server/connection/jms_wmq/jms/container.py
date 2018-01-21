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
from logging import basicConfig, DEBUG, getLogger, INFO
from os import getpid
from thread import start_new_thread
from threading import RLock
from wsgiref.simple_server import make_server

# Bunch
from bunch import Bunch

# ThreadPool
from threadpool import ThreadPool, WorkRequest, NoResultsPending

# Zato
from zato.server.connection.jms_wmq.jms import WebSphereMQJMSException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage

# ################################################################################################################################

log_level = INFO
log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
basicConfig(level=INFO, format=log_format)
logger = getLogger(__name__)

# ################################################################################################################################

class WebSphereMQTask(object):
    """ A process to listen for messages and to send them to WebSphere MQ queue managers.
    """
    def __init__(self, conn, on_message_callback):
        self.conn = conn
        self.on_message_callback = on_message_callback
        self.handlers_pool = ThreadPool(5)
        self.keep_running = True
        self.has_debug = logger.isEnabledFor(DEBUG)

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
                        logger.debug('Message received `%s`' % str(message).decode('utf-8'))

                    work_request = WorkRequest(self.on_message_callback, [message])
                    self.handlers_pool.putRequest(work_request)

                    try:
                        self.handlers_pool.poll()
                    except NoResultsPending, e:
                        pass

                except NoMessageAvailableException, e:
                    if self.has_debug:
                        logger.debug('Consumer did not receive a message. `%s`' % self._get_destination_info())

                except WebSphereMQJMSException, e:
                    logger.error('%s in run, completion_code:`%s`, reason_code:`%s`' % (
                        e.__class__.__name__, e.completion_code, e.reason_code))
                    raise

        # Start listener in a thread
        start_new_thread(_impl, ())

# ################################################################################################################################

class ConnectionContainer(object):
    def __init__(self):
        self.lock = RLock()
        self.connections = {}

    def on_mq_message_received(self, msg):
        logger.info('MQ message received %s', msg)

    def add_conn_def(self, config):
        with self.lock:
            conn = WebSphereMQConnection(**config)
            conn.connect()

            self.connections[config.name] = conn

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

    def on_wsgi_request(self, environ, start_response):

        data = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))

        print()
        print(data, type(data))
        print()

        status = '200 OK'  # HTTP Status
        headers = [('Content-type', 'text/plain')]  # HTTP Headers
        start_response(status, headers)

        return ['OK']

# ################################################################################################################################

    def run(self):
        server = make_server('127.0.0.1', 34567, self.on_wsgi_request)
        server.serve_forever()

# ################################################################################################################################

if __name__ == '__main__':

    config = Bunch()
    config.queue_manager = 'QM1'
    config.channel = 'DEV.APP.SVRCONN'
    config.host = 'localhost'
    config.listener_port = 1414
    config.username = 'app'
    config.password = 'abcd1234'
    config.cache_open_send_queues = True
    config.cache_open_receive_queues = True
    config.use_shared_connections = True
    config.dynamic_queue_template = 'SYSTEM.DEFAULT.MODEL.QUEUE'
    config.ssl = False
    config.ssl_cipher_spec = None
    config.ssl_key_repository = None
    config.needs_mcd = True
    config.needs_jms = False

    container = ConnectionContainer()
    container.run()

    from time import sleep
    sleep(3)

# ################################################################################################################################

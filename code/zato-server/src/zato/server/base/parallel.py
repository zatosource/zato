# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import asyncore, json, logging, time
from threading import Thread

# Zope
from zope.server.http.httpserver import HTTPServer
from zope.server.taskthreads import ThreadedTaskDispatcher

# ZeroMQ
import zmq

# Spring Python
from springpython.util import synchronized

# Zato
from zato.common import ZATO_CONFIG_REQUEST, ZATO_JOIN_REQUEST_ACCEPTED, \
     ZATO_PARALLEL_SERVER, ZATO_SINGLETON_SERVER, ZATO_OK
from zato.common.util import TRACE1, zmq_names, ZMQPull, ZMQPush
from zato.common.odb import create_pool
from zato.server.base import BaseServer, IPCMessage


class ZatoHTTPServer(HTTPServer):
    def __init__(self, host, port, task_dispatcher):

        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))
        super(ZatoHTTPServer, self).__init__(host, port, task_dispatcher)

    def executeRequest(self, task):

        # Currently, we always return text/xml.
        task.response_headers["Content-Type"] = "text/xml"

        try:
            # Collect necessary request data.
            request_body = task.request_data.getBodyStream().getvalue()
            headers = task.request_data.headers
            time.sleep(0.2)
            #print(headers.get('X_ZATO_PEERCERT'))

            #print(33, headers)

            # Fetch the response.
            response = '<?xml version="1.0" encoding="utf-8"?><axx />' #self.soap_dispatcher.handle(request_body, headers)

        # Any exception at this point must be our fault.
        except Exception:
            tb = get_last_traceback(e)
            self.logger.error("Exception caught [%s]" % tb)
            response = server_soap_error(tb)

        # Return HTTP response.
        task.response_headers["Content-Length"] = str(len(response))
        task.write(response)


class ParallelServer(object):
    def __init__(self, host=None, port=None, zmq_context=None, crypto_manager=None,
                 odb_manager=None, singleton_server=None):
        self.host = host
        self.port = port
        self.zmq_context = zmq_context or zmq.Context()
        self.crypto_manager = crypto_manager
        self.odb_manager = odb_manager
        self.singleton_server = singleton_server
        
        self.zmq_items = {}
        
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))
        
    def _after_init_common(self, server):

        # All of the ZeroMQ sockets need to be created in the main thread.
        
        if self.singleton_server:

            # Singleton -> Parallel (pull)
            name = zmq_names.inproc.singleton_to_parallel
            pull_sing_to_para = ZMQPull(name, self.zmq_context, self.on_inproc_message_handler)
            pull_sing_to_para.start()
            self.zmq_items[name] = pull_sing_to_para
            
            # Parallel -> Singleton (pull)
            name = zmq_names.inproc.parallel_to_singleton
            pull_para_to_sing = ZMQPull(name, self.zmq_context, self.singleton_server.on_inproc_message_handler)
            pull_para_to_sing.start()
            self.zmq_items[name] = pull_para_to_sing
            
            # So that the .bind call in ZMQPull's above has enough time.
            # TODO: Make it a configurable option.
            time.sleep(0.05)
            
            # Parallel (push) -> Singleton
            name = zmq_names.inproc.parallel_to_singleton
            push_para_to_sing = ZMQPush(name, self.zmq_context)
            self.zmq_items[name] = push_para_to_sing
            
            # Singleton (push) -> Parallel
            name = zmq_names.inproc.singleton_to_parallel
            push_sing_to_para = ZMQPush(name, self.zmq_context)
            self.zmq_items[name] = push_sing_to_para
            
            Thread(target=self.singleton_server.run).start()
    
    def _after_init_accepted(self, server):
        pass
    
    def _after_init_non_accepted(self, server):
        pass    
        
    def after_init(self):
        
        # First try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = self.odb_manager.fetch_server()
        
        if not server:
            raise Exception('Server does not exist in the ODB')
        
        self._after_init_common(server)
        
        # A server which hasn't been approved in the cluster still needs to fetch
        # all the config data but it won't start any MQ/AMQP/ZMQ/etc. listeners
        # except for a ZMQ config subscriber that will listen for an incoming approval.
        
        if server.last_join_status == ZATO_JOIN_REQUEST_ACCEPTED:
            self._after_init_accepted(server)
        else:
            msg = 'Server has not been accepted, last_join_status=[{0}]'
            self.logger.warn(msg.format(server.last_join_status))
            
            self._after_init_non_accepted(server)
        
    def on_inproc_message_handler(self, msg):
        """ Handler for incoming 'inproc' ZMQ messages.
        """
        
    def run_forever(self):
        task_dispatcher = ThreadedTaskDispatcher()
        task_dispatcher.setThreadCount(20)

        self.logger.debug("host=[{0}], port=[{1}]".format(self.host, self.port))

        ZatoHTTPServer(self.host, self.port, task_dispatcher)

        try:
            while True:
                asyncore.poll(5)

        except KeyboardInterrupt:
            self.logger.info("Shutting down.")
            
            # ZeroMQ
            for zmq_item in self.zmq_items.values():
                zmq_item.stop()
                
            self.zmq_context.term()
            
            # Zope
            task_dispatcher.shutdown()

    def send_config_request(self, command, data=None, timeout=None):
        """ Sends a synchronous IPC request to the SingletonServer.
        """
        request = self._create_ipc_config_request(command, data)
        return self._send_config_request(request, self.partner_request_queues.values()[0], timeout)

################################################################################

    def _on_config_sql(self, msg):
        """ A common method for handling all SQL connection pools-related config
        requests. Must always be called from within a concrete, synchronized,
        configuration handler (such as _on_config_EDIT_SQL_CONNECTION_POOL etc.)
        """
        command = msg.command
        params = json.loads(msg.params["data"])

        command_handler = getattr(self.sql_pool, "_on_config_" + command)
        command_handler(params)

        return ZATO_OK, ""

    @synchronized()
    def _on_config_EDIT_SQL_CONNECTION_POOL(self, msg):
        """ Updates all of SQL connection pool's parameters, except for
        the password.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CREATE_SQL_CONNECTION_POOL(self, msg):
        """ Creates a new SQL connection pool with no password set.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_DELETE_SQL_CONNECTION_POOL(self, msg):
        """ Deletes an SQL connection pool.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CHANGE_PASSWORD_SQL_CONNECTION_POOL(self, msg):
        """ Deletes an SQL connection pool.
        """
        return self._on_config_sql(msg)

################################################################################

    @synchronized()
    def _on_config_LOAD_EGG_SERVICES(self, msg):
        """ Loads Zato services from a given .egg distribution and makes them
        available for immediate use.
        """
        egg_path = json.loads(msg.params["data"])
        self.service_store.import_services_from_egg(egg_path, self)

        return ZATO_OK, ""

################################################################################

    @synchronized()
    def _on_config_ADD_TO_WSS_NONCE_CACHE(self, msg):
        wsse_nonce, recycle_time = json.loads(msg.params["data"])

        # Note that the method is already synchronized.
        self.wss_nonce_cache[wsse_nonce] = recycle_time

        return ZATO_OK, ""

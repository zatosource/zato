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
import asyncore, httplib, json, logging, time
from hashlib import sha256
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

class HTTPException(Exception):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason

class ZatoHTTPListener(HTTPServer):
    def __init__(self, server, task_dispatcher):
        self.logger = logging.getLogger("%s.%s" % (__name__, 
                                                   self.__class__.__name__))
        self.server = server
        super(ZatoHTTPListener, self).__init__(self.server.host, self.server.port, 
                                               task_dispatcher)

    def _handle_security_tech_account(self, sec_def, request_data, body, headers):
        """ Handles the 'tech-account' security config type.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                msg = "The header [{0}] doesn't exist or is empty, URI=[{1}]".\
                    format(header, request_data.uri)
                self.logger.error(msg)
                raise HTTPException(httplib.FORBIDDEN, msg)

        # Note that both checks below a different message to the client than
        # what goes into logs. It's to conceal from bad-behaving users what really went
        # wrong (that of course assumes they can't access the logs).

        msg_template = 'The {0} is incorrect, URI=[{1}], X_ZATO_USER=[{2}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            self.logger.error(msg_template.format('username', request_data.uri, 
                              headers['X_ZATO_USER']))
            raise HTTPException(httplib.FORBIDDEN, msg_template.\
                    format('username or password', request_data.uri, 
                           headers['X_ZATO_USER']))
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            self.logger.error(msg_template.format('password', request_data.uri, 
                              headers['X_ZATO_USER']))
            raise HTTPException(httplib.FORBIDDEN, msg_template.\
                    format('username or password', request_data.uri, 
                           headers['X_ZATO_USER']))
        
        
    def handle_security(self, request_data, body, headers):
        """ Handles all security-related aspects of an incoming HTTP message
        handling. Calls other concrete security methods as appropriate.
        """
        
        if request_data.uri in self.server.url_security:
            sec_def_data = self.server.url_security[request_data.uri]
            sec_def, sec_def_type = sec_def_data['sec_def'], sec_def_data['sec_def_type']
            
            handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
            getattr(self, handler_name)(sec_def, request_data, body, headers)
            
        else:
            msg = ("The URL [{0}] doesn't exist or has no security "
                  "configuration assigned").format(request_data.uri)
            self.logger.error(msg)
            raise HTTPException(httplib.NOT_FOUND, msg)
        
    def executeRequest(self, task):

        # Currently, we always return text/xml.
        task.response_headers["Content-Type"] = "text/xml"

        try:
            # Collect necessary request data.
            body = task.request_data.getBodyStream().getvalue()
            headers = task.request_data.headers
            
            self.handle_security(task.request_data, body, headers)

            # Fetch the response.
            response = '<?xml version="1.0" encoding="utf-8"?><axx />' #self.soap_dispatcher.handle(request_body, headers)

        except HTTPException, e:
            task.setResponseStatus(e.status, e.reason)
            response = e.reason
            
        # Any exception at this point must be our fault.
        except Exception:
            tb = get_last_traceback(e)
            self.logger.error("Exception caught [%s]" % tb)
            response = server_soap_error(tb)
            
        # Return the HTTP response.
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
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
        
        # Security configuration of HTTP URLs.
        self.url_security = self.odb_manager.get_url_security(server)
        self.logger.log(logging.DEBUG, 'url_security=[{0}]'.format(self.url_security))
        
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

        ZatoHTTPListener(self, task_dispatcher)

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

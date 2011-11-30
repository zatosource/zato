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
import asyncore, httplib, json, logging, os, socket, sys, time
from copy import deepcopy
from hashlib import sha256
from threading import Thread
from traceback import format_exc

# zope.server
from zope.server.http.httpserver import HTTPServer

# ZeroMQ
import zmq

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import(PORTS, ZATO_CONFIG_REQUEST, ZATO_JOIN_REQUEST_ACCEPTED,
     ZATO_OK, ZATO_URL_TYPE_SOAP)
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.util import new_rid, TRACE1
from zato.server.amqp.outgoing import start_connector as out_start_connector
from zato.server.base import BrokerMessageReceiver
from zato.server.base.worker import _HTTPServerChannel, _HTTPTask, _TaskDispatcher, WorkerStore
from zato.server.channel.soap import server_soap_error

logger = logging.getLogger(__name__)

def wrap_error_message(rid, url_type, msg):
    """ Wraps an error message in a transport-specific envelope.
    """
    if url_type == ZATO_URL_TYPE_SOAP:
        return server_soap_error(rid, msg)
    
    # Let's return the message as-is if we don't have any specific envelope
    # to use.
    return msg

class HTTPException(Exception):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
        
class ZatoHTTPListener(HTTPServer):
    
    channel_class = _HTTPServerChannel
    
    def __init__(self, server, task_dispatcher, broker_client=None):
        self.server = server
        self.broker_client = broker_client
        super(ZatoHTTPListener, self).__init__(self.server.host, self.server.port, 
                                               task_dispatcher)

    def _handle_security_tech_account(self, rid, sec_def, request_data, body, headers):
        """ Handles the 'tech-account' security config type.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                msg = ("[{0}] The header [{1}] doesn't exist or is empty, URI=[{2}, "
                      "headers=[{3}]]").\
                        format(rid, header, request_data.uri, headers)
                logger.error(msg)
                raise HTTPException(httplib.FORBIDDEN, msg)

        # Note that both checks below send a different message to the client 
        # when compared with what goes into logs. It's to conceal from
        # bad-behaving users what really went wrong (that of course assumes 
        # they can't access the logs).

        msg_template = '[{0}] The {1} is incorrect, URI=[{2}], X_ZATO_USER=[{3}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            logger.error(msg_template.format(rid, 'username', 
                        request_data.uri, headers['X_ZATO_USER']))
            raise HTTPException(httplib.FORBIDDEN, msg_template.\
                    format(rid, 'username or password', request_data.uri, 
                           headers['X_ZATO_USER']))
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            logger.error(msg_template.format(rid, 'password', request_data.uri, 
                              headers['X_ZATO_USER']))
            raise HTTPException(httplib.FORBIDDEN, msg_template.\
                    format(rid, 'username or password', request_data.uri, 
                           headers['X_ZATO_USER']))
        
        
    def handle_security(self, rid, url_data, request_data, body, headers):
        """ Handles all security-related aspects of an incoming HTTP message
        handling. Calls other concrete security methods as appropriate.
        """
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(rid, sec_def, request_data, body, headers)
            
    def executeRequest(self, task, thread_ctx):
        """ Handles incoming HTTP requests. Each request is being handled by one
        of the threads created in ParallelServer.run_forever method.
        """
        
        # Initially, we have no clue about the type of the URL being accessed,
        # later on, if we don't stumble upon an exception, we may learn that
        # it is for instance, a SOAP URL.
        url_type = None
        rid = new_rid()
        
        try:
            # Collect necessary request data.
            body = task.request_data.getBodyStream().getvalue()
            headers = task.request_data.headers
            
            url_data = thread_ctx.store.url_sec_get(task.request_data.uri)
            if url_data:
                url_type = url_data['url_type']
                
                self.handle_security(rid, url_data, task.request_data, body, headers)
                
                # TODO: Shadow out any passwords that may be contained in HTTP
                # headers or in the message itself. Of course, that only applies
                # to auth schemes we're aware of (HTTP Basic Auth, WSS etc.)

            else:
                msg = ("The URL [{0}] doesn't exist or has no security "
                      "configuration assigned").format(task.request_data.uri)
                logger.warn(msg, rid)
                raise HTTPException(httplib.NOT_FOUND, msg)

            # Fetch the response.
            response = self.server.soap_handler.handle(rid, body, headers, thread_ctx)

        except HTTPException, e:
            task.setResponseStatus(e.status, e.reason)
            response = wrap_error_message(rid, url_type, e.reason)
            
        # Any exception at this point must be our fault.
        except Exception, e:
            tb = format_exc(e)
            logger.error('[{0}] Exception caught [{1}]'.format(rid, tb))
            response = wrap_error_message(rid, url_type, tb)

        if url_type == ZATO_URL_TYPE_SOAP:
            content_type = 'text/xml'
        else:
            content_type = 'text/plain'
            
        task.response_headers['Content-Type'] = content_type
            
        # Return the HTTP response.
        task.response_headers['Content-Length'] = str(len(response))
        task.write(response)


class ParallelServer(BrokerMessageReceiver):
    def __init__(self, host=None, port=None, zmq_context=None, crypto_manager=None,
                 odb=None, singleton_server=None, worker_config=None, repo_location=None):
        self.host = host
        self.port = port
        self.zmq_context = zmq_context or zmq.Context()
        self.crypto_manager = crypto_manager
        self.odb = odb
        self.singleton_server = singleton_server
        self.worker_config = worker_config
        self.repo_location = repo_location
        
    def _after_init_common(self, server):
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
        
        self.broker_token = server.cluster.broker_token
        self.broker_push_worker_pull = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.BROKER_PUSH_WORKER_THREAD_PULL)
        self.worker_push_broker_pull = self.parallel_push_broker_pull = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.WORKER_THREAD_PUSH_BROKER_PULL)
        self.broker_pub_worker_sub = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.BROKER_PUB_WORKER_THREAD_SUB)
        
        if self.singleton_server:
            
            self.service_store.read_internal_services()
            
            kwargs = {'zmq_context':self.zmq_context,
            'broker_host': server.cluster.broker_host,
            'broker_push_singleton_pull_port': server.cluster.broker_start_port + PORTS.BROKER_PUSH_SINGLETON_PULL,
            'singleton_push_broker_pull_port': server.cluster.broker_start_port + PORTS.SINGLETON_PUSH_BROKER_PULL,
            'broker_token':self.broker_token,
                    }
            Thread(target=self.singleton_server.run, kwargs=kwargs).start()
            
            # Let the scheduler fully initialize
            time.sleep(0.2)
    
    def _after_init_accepted(self, server):
        if self.singleton_server:
            for(_, name, is_active, job_type, start_date, extra, service,\
                _, weeks, days, hours, minutes, seconds, repeats, cron_definition)\
                    in self.odb.get_job_list(server.cluster.id):
                if is_active:
                    job_data = Bunch({'name':name, 'is_active':is_active, 
                        'job_type':job_type, 'start_date':start_date, 
                        'extra':extra, 'service':service,  'weeks':weeks, 
                        'days':days, 'hours':hours, 'minutes':minutes, 
                        'seconds':seconds,  'repeats':repeats, 
                        'cron_definition':cron_definition})
                    self.singleton_server.scheduler.create_edit('create', job_data)
                    
        self.worker_config = Bunch()
        
        # Repo location so that AMQP subprocesses know how where to read
        # the server's configuration from.
        self.worker_config.repo_location = self.repo_location
        
        # The broker client for each of the worker threads.
        self.worker_config.broker_config = Bunch()
        self.worker_config.broker_config.name = 'worker-thread'
        self.worker_config.broker_config.broker_token = self.broker_token
        self.worker_config.broker_config.zmq_context = self.zmq_context
        self.worker_config.broker_config.broker_push_client_pull = self.broker_push_worker_pull
        self.worker_config.broker_config.client_push_broker_pull = self.worker_push_broker_pull
        self.worker_config.broker_config.broker_pub_client_sub = self.broker_pub_worker_sub
        
        # HTTP Basic Auth
        ba_config = Bunch()
        for item in self.odb.get_basic_auth_list(server.cluster.id):
            ba_config[item.name] = Bunch()
            ba_config[item.name].is_active = item.is_active
            ba_config[item.name].username = item.username
            ba_config[item.name].domain = item.domain
            ba_config[item.name].password = item.password
            
        # Technical accounts
        ta_config = Bunch()
        for item in self.odb.get_tech_acc_list(server.cluster.id):
            ta_config[item.name] = Bunch()
            ta_config[item.name].is_active = item.is_active
            ta_config[item.name].name = item.name
            ta_config[item.name].password = item.password
            ta_config[item.name].salt = item.salt
            
        wss_config = Bunch()
        for item in self.odb.get_wss_list(server.cluster.id):
            wss_config[item.name] = Bunch()
            wss_config[item.name].is_active = item.is_active
            wss_config[item.name].username = item.username
            wss_config[item.name].password = item.password
            wss_config[item.name].password_type = item.password_type
            wss_config[item.name].reject_empty_nonce_ts = item.reject_empty_nonce_ts
            wss_config[item.name].reject_stale_username = item.reject_stale_username
            wss_config[item.name].expiry_limit = item.expiry_limit
            wss_config[item.name].nonce_freshness = item.nonce_freshness

        # Security configuration of HTTP URLs.
        url_sec = self.odb.get_url_security(server)
        
        self.worker_config.basic_auth = ba_config
        self.worker_config.tech_acc = ta_config
        self.worker_config.wss = wss_config
        self.worker_config.url_sec = url_sec
        
        self._init_amqp(server)
        
        # The parallel server's broker client. The client's used to notify
        # all the server's AMQP subprocesses that they need to shut down.

        self.broker_client = BrokerClient()
        self.broker_client.name = 'parallel'
        self.broker_client.token = server.cluster.broker_token
        self.broker_client.zmq_context = self.zmq_context
        self.broker_client.client_push_broker_pull = self.parallel_push_broker_pull
        #self.broker_client.broker_push_client_pull = self.broker_push_worker_pull
        
        self.broker_client.init()
        self.broker_client.start()
        
    def _init_amqp(self, server):
        
        for item in self.odb.get_out_amqp_list(server.cluster.id):
            out_start_connector(self.repo_location, item.id, item.def_id)
        
    def _after_init_non_accepted(self, server):
        pass    
        
    def after_init(self):
        
        # First try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = self.odb.fetch_server()
        
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
            logger.warn(msg.format(server.last_join_status))
            
            self._after_init_non_accepted(server)
        
    def on_inproc_message_handler(self, msg):
        """ Handler for incoming 'inproc' ZMQ messages.
        """
        
    def run_forever(self):
        
        task_dispatcher = _TaskDispatcher(self, self.worker_config, self.on_broker_msg, self.zmq_context)
        task_dispatcher.setThreadCount(1)

        logger.debug('host=[{0}], port=[{1}]'.format(self.host, self.port))

        ZatoHTTPListener(self, task_dispatcher)

        try:
            while True:
                asyncore.poll(5)

        except KeyboardInterrupt:
            logger.info("Shutting down.")
            
            # Close all the AMQP subprocesses this server has started.
            msg = {}
            msg['action'] = OUTGOING.AMQP_CLOSE
            msg['odb_token'] = self.odb.odb_data['token']
            self.broker_client.send_json(msg, msg_type=MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB)
            time.sleep(0.1)
            self.broker_client.close()
            
            if self.singleton_server:
                self.singleton_server.broker_client.close()
                
            self.zmq_context.term()
            self.odb.close()
            task_dispatcher.shutdown()

# ##############################################################################


            
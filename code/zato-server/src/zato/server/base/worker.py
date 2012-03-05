# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
import logging, socket
from copy import deepcopy
from thread import start_new_thread
from threading import local, RLock
from traceback import format_exc

# zope.server
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httptask import HTTPTask
from zope.server.serverchannelbase import task_lock
from zope.server.taskthreads import ThreadedTaskDispatcher

# Zato
from zato.server.base import BaseWorker
from zato.server.connection.http_soap import PlainHTTPHandler, RequestHandler, SOAPHandler
from zato.server.connection.http_soap import Security as ConnectionHTTPSOAPSecurity

logger = logging.getLogger(__name__)

class WorkerStore(BaseWorker):
    """ Each worker thread has its own configuration store. The store is assigned
    to the thread's threading.local variable. All the methods assume the data's
    being already validated and sanitized by one of Zato's internal services.
    
    There are exactly two threads willing to access the data at any time
    - the worker thread this store belongs to
    - the background ZeroMQ thread which may wish to update the store's configuration
    hence the need for employing RLocks yet there shouldn't be much contention
    because configuration updates are extremaly rare when compared to regular
    access by worker threads.
    """
    def __init__(self, worker_config):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.worker_config = worker_config
        
        self.basic_auth_lock = RLock()
        self.tech_acc_lock = RLock()
        self.wss_lock = RLock()
        
        self.request_handler = RequestHandler()
        self.request_handler.soap_handler = SOAPHandler(self.worker_config.http_soap, self.worker_config.server)
        self.request_handler.plain_http_handler = PlainHTTPHandler(self.worker_config.http_soap, self.worker_config.server)
        self.request_handler.security = ConnectionHTTPSOAPSecurity(self.worker_config.url_sec, 
                self.worker_config.basic_auth, self.worker_config.tech_acc, self.worker_config.wss)
        
    def filter(self, msg):
        return True
        
# ##############################################################################        
        
    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        self.request_handler.security.basic_auth_get(name)

    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_BASIC_AUTH_CREATE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_BASIC_AUTH_EDIT(msg, *args)
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg, *args)

# ##############################################################################

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        self.request_handler.security.tech_acc_get(msg, *args)

    def on_broker_pull_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_TECH_ACC_CREATE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_TECH_ACC_EDIT(msg, *args)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_TECH_ACC_DELETE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(msg, *args)
            
# ##############################################################################

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        self.request_handler.security.wss_get(msg, *args)

    def on_broker_pull_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_WSS_CREATE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_WSS_EDIT(msg, *args)
        
    def on_broker_pull_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_WSS_DELETE(msg, *args)
        
    def on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        self.request_handler.security.on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(msg, *args)
            
# ##############################################################################

    def _on_message_invoke_service(self, msg, channel, action, args=None):
        """ Triggered by external processes, such as AMQP or the singleton's scheduler,
        creates a new service instance and invokes it.
        """
        service_instance = self.worker_config.server.service_store.new_instance(msg.service)
        service_instance.update(service_instance, self.worker_config.server, self.broker_client, channel, msg.rid)
        
        response = service_instance.handle(payload=msg.get('payload'), raw_request=msg)
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Invoked [{0}], channel [{1}], action [{2}], response [{3}]'.format(
                msg.service, channel, action, repr(response))
            logger.debug(msg)

    def on_broker_pull_msg_SCHEDULER_JOB_EXECUTED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'scheduler', 'SCHEDULER_JOB_EXECUTED', args)

    def on_broker_pull_msg_CHANNEL_AMQP_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'amqp', 'CHANNEL_AMQP_MESSAGE_RECEIVED', args)
    
    def on_broker_pull_msg_CHANNEL_JMS_WMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'jms-wmq', 'CHANNEL_JMS_WMQ_MESSAGE_RECEIVED', args)
    
    def on_broker_pull_msg_CHANNEL_ZMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'zmq', 'CHANNEL_ZMQ_MESSAGE_RECEIVED', args)
            
# ##############################################################################
            
class _TaskDispatcher(ThreadedTaskDispatcher):
    """ A task dispatcher which knows how to pass custom arguments down to
    the worker threads.
    """
    def __init__(self, server, server_config, pull_handler, zmq_context):
        super(_TaskDispatcher, self).__init__()
        self.server = server
        self.server_config = server_config
        self.pull_handler = pull_handler
        self.zmq_context = zmq_context
        
    def setThreadCount(self, count):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """
        mlock = self.thread_mgmt_lock
        mlock.acquire()
        try:
            threads = self.threads
            thread_no = 0
            running = len(threads) - self.stop_count
            while running < count:
                # Start threads.
                while thread_no in threads:
                    thread_no = thread_no + 1
                threads[thread_no] = 1
                running += 1

                # Each thread gets its own copy of the initial configuration ..
                worker_config = self.server_config.copy()
                
                # .. though the ZMQ context is OK to be shared among multiple threads.
                worker_config.zmq_context = self.zmq_context
                
                # .. be careful with this, it's a reference to the main ParallelServer
                # this thread is running on.
                worker_config.server = self.server
                
                start_new_thread(self.handlerThread, (thread_no, worker_config))
                
                thread_no = thread_no + 1
            if running > count:
                # Stop threads.
                to_stop = running - count
                self.stop_count += to_stop
                for n in range(to_stop):
                    self.queue.put(None)
                    running -= 1
        finally:
            mlock.release()
            
    def handlerThread(self, thread_no, worker_config):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """

        # We're in a new thread so we can start new thread-specific clients.
        _local = local()
        _local.store = WorkerStore(worker_config)
        _local.store._init()
        _local.broker_client = _local.store.broker_client
        
        threads = self.threads
        try:
            while threads.get(thread_no):
                task = self.queue.get()
                if task is None:
                    # Special value: kill this thread.
                    break
                try:
                    task.service(_local)
                except Exception, e:
                    logger.error('Exception during task {0}'.format(
                        format_exc(e)))
        finally:
            mlock = self.thread_mgmt_lock
            mlock.acquire()
            try:
                self.stop_count -= 1
                try: del threads[thread_no]
                except KeyError: pass
            finally:
                mlock.release()
                
# ##############################################################################

class _HTTPTask(HTTPTask):
    """ An HTTP task which knows how to use ZMQ sockets.
    """
    def service(self, worker_config):
        try:
            try:
                self.start()
                self.channel.server.executeRequest(self, worker_config)
                self.finish()
            except socket.error:
                self.close_on_finish = 1
                if self.channel.adj.log_socket_errors:
                    raise
        finally:
            if self.close_on_finish:
                self.channel.close_when_done()
                
class _HTTPServerChannel(HTTPServerChannel):
    """ A subclass which uses Zato's own _HTTPTasks.
    """
    task_class = _HTTPTask
    
    def service(self, worker_config):
        """Execute all pending tasks"""
        while True:
            task = None
            task_lock.acquire()
            try:
                if self.tasks:
                    task = self.tasks.pop(0)
                else:
                    # No more tasks
                    self.running_tasks = False
                    self.set_async()
                    break
            finally:
                task_lock.release()
            try:
                task.service(worker_config)
            except:
                # propagate the exception, but keep executing tasks
                self.server.addTask(self)
                raise
            
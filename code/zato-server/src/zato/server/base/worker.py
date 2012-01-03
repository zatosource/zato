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
import errno, logging, multiprocessing, os, socket, sys, time
from copy import deepcopy
from datetime import datetime
from subprocess import Popen
from thread import start_new_thread
from threading import local, RLock, Thread
from traceback import format_exc

# zope.server
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httptask import HTTPTask
from zope.server.serverchannelbase import task_lock
from zope.server.taskthreads import ThreadedTaskDispatcher

# Bunch
from bunch import Bunch

# Zato
from zato.common import ConnectionException
from zato.common.util import TRACE1
from zato.server.base import BaseWorker, BrokerMessageReceiver

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
    def __init__(self, worker_data):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.worker_data = worker_data
        
        self.basic_auth = self.worker_data.basic_auth
        self.tech_acc = self.worker_data.tech_acc
        self.wss = self.worker_data.wss
        self.url_sec = self.worker_data.url_sec
        
        self.basic_auth_lock = RLock()
        self.tech_acc_lock = RLock()
        self.wss_lock = RLock()
        self.url_sec_lock = RLock()
        
    def filter(self, msg):
        return True
        
# ##############################################################################        
        
    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        with self.basic_auth_lock:
            return self.basic_auth.get(Name)

    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        with self.basic_auth_lock:
            self.basic_auth[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            del self.basic_auth[msg.old_name]
            self.basic_auth[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            del self.basic_auth[msg.name]
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            self.basic_auth[msg.name]['password'] = msg.password

# ##############################################################################

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        with self.tech_acc_lock:
            return self.tech_acc.get(name)

    def on_broker_pull_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        with self.tech_acc_lock:
            self.tech_acc[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        with self.tech_acc_lock:
            del self.tech_acc[msg.old_name]
            self.tech_acc[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        with self.tech_acc_lock:
            del self.tech_acc[msg.name]
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        with self.tech_acc_lock:
            # The message's 'password' attribute already takes the salt 
            # into account (pun intended ;-))
            self.tech_acc[msg.name]['password'] = msg.password
            
# ##############################################################################

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        with self.wss_lock:
            return self.wss.get(name)

    def on_broker_pull_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        with self.wss_lock:
            self.wss[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        with self.wss_lock:
            del self.wss[msg.old_name]
            self.wss[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.wss_lock:
            del self.wss[msg.name]
        
    def on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        with self.wss_lock:
            # The message's 'password' attribute already takes the salt 
            # into account.
            self.wss[msg.name]['password'] = msg.password
            
# ##############################################################################

    def url_sec_get(self, url):
        """ Returns the configuration of the given URL
        """
        with self.url_sec_lock:
            return self.url_sec.get(url)

# ##############################################################################

    def _on_message_invoke_service(self, msg, channel, action, args=None):
        """ Triggered by external processes, such as AMQP or the singleton's scheduler,
        creates a new service instance and invokes it.
        """
        service_instance = self.worker_data.server.service_store.new_instance(msg.service)
        service_instance.update(service_instance, self.worker_data.server, self.broker_client, channel, msg.rid)
        
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
    def __init__(self, server, worker_config, pull_handler, zmq_context):
        super(_TaskDispatcher, self).__init__()
        self.server = server
        self.worker_config = worker_config
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
                worker_data = deepcopy(self.worker_config)
                
                # .. though the ZMQ context is OK to be shared among multiple threads.
                worker_data.zmq_context = self.zmq_context
                
                # .. be careful with this, it's a reference to the main ParallelServer
                # this thread is running on.
                worker_data.server = self.server
                
                start_new_thread(self.handlerThread, (thread_no, worker_data))
                
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
            
    def handlerThread(self, thread_no, worker_data):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """

        # We're in a new thread so we can start new thread-specific clients.
        _local = local()
        _local.store = WorkerStore(worker_data)
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
    def service(self, worker_data):
        try:
            try:
                self.start()
                self.channel.server.executeRequest(self, worker_data)
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
    
    def service(self, worker_data):
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
                task.service(worker_data)
            except:
                # propagate the exception, but keep executing tasks
                self.server.addTask(self)
                raise
            
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
import logging, socket, time
from copy import deepcopy
from thread import start_new_thread
from threading import local, RLock, Thread
from traceback import format_exc

# zope.server
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httptask import HTTPTask
from zope.server.serverchannelbase import task_lock
from zope.server.taskthreads import ThreadedTaskDispatcher

# Pika
from pika import BasicProperties
from pika.adapters import SelectConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.server.base import BrokerMessageReceiver

logger = logging.getLogger(__name__)

class _AMQPPublisher(object):
    def __init__(self, conn_params, def_name, out_name):
        self.conn_params = conn_params
        self.def_name = def_name
        self.out_name = out_name
        
    def publish(self, msg, exchange, routing_key):
        self.channel.basic_channel(exchange, routing_key, msg)
        
    def _on_connected(self, conn):
        conn.channel(self._on_channel_open)
        
    def _on_channel_open(self, channel):
        self.channel = channel
        msg = 'Got a channel for {0}:{1}{2} ({3}/{4})'.format(self.conn_params.host, 
            self.conn_params.port, self.conn_params.virtual_host, self.def_name, self.out_name)
        logger.debug(msg)
        
    def _run(self):
        try:
            try:
                self.conn = SelectConnection(self.conn_params, self._on_connected)
                self.conn.ioloop.start()
            except KeyboardInterrupt:
                conn.close()
                conn.ioloop.start()
        except socket.error, e:
            msg = 'Could not establish a connection to {0}:{1}{2} ({3}/{4}), e=[{5}]'.format(
                self.conn_params.host, self.conn_params.port, self.conn_params.virtual_host, 
                self.def_name, self.out_name, format_exc(e))
            logger.error(msg)
            
    def close(self):
        self.conn.close()
        self.conn.ioloop.start()

class WorkerStore(BrokerMessageReceiver):
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
    def __init__(self, thread_data):

        self.thread_data = thread_data
        
        self.basic_auth = self.thread_data.basic_auth
        self.tech_acc = self.thread_data.tech_acc
        self.wss = self.thread_data.wss
        self.url_sec = self.thread_data.url_sec
        self.def_amqp = self.thread_data.def_amqp
        self.out_amqp = self.thread_data.out_amqp
        
        self.basic_auth_lock = RLock()
        self.tech_acc_lock = RLock()
        self.wss_lock = RLock()
        self.url_sec_lock = RLock()
        self.def_amqp_lock = RLock()
        self.out_amqp_lock = RLock()
        
    def _init(self):
        self._setup_amqp()
        self._setup_broker_client()

    def _setup_broker_client(self):
        self.broker_client = BrokerClient()
        self.broker_client.name = 'parallel/thread2'
        self.broker_client.token = self.thread_data.broker_config.broker_token
        self.broker_client.zmq_context = self.thread_data.broker_config.zmq_context
        self.broker_client.push_addr = self.thread_data.broker_config.broker_push_addr
        self.broker_client.pull_addr = self.thread_data.broker_config.broker_pull_addr
        self.broker_client.sub_addr = self.thread_data.broker_config.broker_sub_addr
        self.broker_client.on_pull_handler = self.thread_data.broker_pull_handler
        self.broker_client.on_sub_handler = self.on_broker_msg
        self.broker_client.init()
        self.broker_client.start()
        
    def _setup_amqp(self):
        """ Sets up AMQP channels and outgoing connections on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                for def_name, def_attrs in self.def_amqp.items():
                    for out_name, out_attrs in self.out_amqp.items():
                        if def_name == out_attrs.def_name:
                            
                            credentials = PlainCredentials(def_attrs.username, def_attrs.password)
                            conn_params = ConnectionParameters(def_attrs.host,
                                def_attrs.port, def_attrs.vhost, credentials,
                                frame_max=def_attrs.frame_max, heartbeat=def_attrs.heartbeat)

                            publisher = _AMQPPublisher(conn_params, def_name, out_attrs.name)
                            Thread(target=publisher._run).start()
                            
                            self.out_amqp[out_name].publisher = publisher

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

    def def_amqp_get(self, name):
        """ Returns the configuration of the AMQP definition of the given name.
        """
        #with self.def_amqp_lock:
        #    return self.def_amqp.get(name)

    def on_broker_pull_msg_DEFINITION_AMQP_CREATE(self, msg, *args):
        """ Creates a new AMQP definition.
        """
        #with self.def_amqp_lock:
        #    self.def_amqp[msg.name] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        #with self.def_amqp_lock:
        #    del self.def_amqp[msg.old_name]
        #    self.def_amqp[msg.name] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition.
        """
        #with self.def_amqp_lock:
        #    del self.def_amqp[msg.name]
        
    def on_broker_pull_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition.
        """
        #with self.def_amqp_lock:
        #    self.def_amqp[msg.name]['password'] = msg.password
            
# ##############################################################################

    def out_amqp_get(self, name):
        """ Returns the configuration of an outgoing AMQP connection.
        """
        #with self.out_amqp_lock:
        #    return self.out_amqp.get(name)

    def on_broker_pull_msg_OUTGOING_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection.
        """
        #with self.out_amqp_lock:
        #    self.out_amqp[msg.name] = msg
        
    def on_broker_pull_msg_OUTGOING_AMQP_EDIT(self, msg, *args):
        """ Updates an outgoing AMQP connection.
        """
        #with self.out_amqp_lock:
        #    del self.out_amqp[msg.old_name]
        #    self.out_amqp[msg.name] = msg
        
    def on_broker_pull_msg_OUTGOING_AMQP_DELETE(self, msg, *args):
        """ Deletes an outgoing AMQP connection.
        """
        #with self.out_amqp_lock:
        #    del self.out_amqp[msg.name]
        
# ##############################################################################
            
class _TaskDispatcher(ThreadedTaskDispatcher):
    """ A task dispatcher which knows how to pass custom arguments down to
    the worker threads.
    """
    def __init__(self, worker_config, pull_handler, zmq_context):
        super(_TaskDispatcher, self).__init__()
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
                thread_data = deepcopy(self.worker_config)
                
                # .. though some things are OK to be shared among multiple threads.
                thread_data.zmq_context = self.zmq_context
                thread_data.broker_pull_handler = self.pull_handler
                
                start_new_thread(self.handlerThread, (thread_no, thread_data))
                
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
            
    def handlerThread(self, thread_no, thread_data):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """
        _local = local()
        _local.store = WorkerStore(thread_data)
        
        # We're in a new thread so we can start new thread-specific clients.
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
    def service(self, thread_data):
        try:
            try:
                self.start()
                self.channel.server.executeRequest(self, thread_data)
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
    
    def service(self, thread_data):
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
                task.service(thread_data)
            except:
                # propagate the exception, but keep executing tasks
                self.server.addTask(self)
                raise
            
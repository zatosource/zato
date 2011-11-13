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
import errno, logging, socket, time
from copy import deepcopy
from datetime import datetime
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
from zato.common import ConnectionException
from zato.common.util import TRACE1
from zato.server.base import BrokerMessageReceiver

logger = logging.getLogger(__name__)

class _AMQPPublisher(object):
    def __init__(self, conn_params, def_name, out_name, properties):
        self.conn_params = conn_params
        self.def_name = def_name
        self.out_name = out_name
        self.properties = properties
        self.conn = None
        self.channel = None
        self.connection_attempts = 1
        self.first_connection_attempt_time = None
        self.keep_running = True
        self.reconnect_sleep_time = 5 # Seconds
        self.reconnect_error_numbers = (errno.ENETUNREACH, errno.ENETRESET, errno.ECONNABORTED, 
            errno.ECONNRESET, errno.ETIMEDOUT, errno.ECONNREFUSED, errno.EHOSTUNREACH)

    def _conn_info(self):
        return '{0}:{1}{2} ({3})'.format(self.conn_params.host, 
            self.conn_params.port, self.conn_params.virtual_host, self.out_name)
        
    def publish(self, msg, exchange, routing_key, properties=None, *args, **kwargs):
        if self.channel:
            if self.conn.is_open:
                properties = properties if properties else self.properties
                self.channel.basic_publish(exchange, routing_key, msg, properties, *args, **kwargs)
                if(logger.isEnabledFor(TRACE1)):
                    log_msg = 'AMQP message published [{0}], exchange [{1}], routing key [{2}], publisher ID [{3}]'
                    logger.log(TRACE1, log_msg.format(msg, exchange, routing_key, str(hex(id(self)))))
            else:
                msg = "Can't publish, the connection for {0} is not open".format(self._conn_info())
                logger.error(msg)
                raise ConnectionException(msg)
        else:
            msg = "Can't publish, don't have a channel for {0}".format(self._conn_info())
            logger.error(msg)
            raise ConnectionException(msg)
        
    def _on_connected(self, conn):
        """ Invoked after establishing a successful connection to an AMQP broker.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hasn't been established straightaway.
        """
        
        if self.connection_attempts > 1:
            delta = datetime.now() - self.first_connection_attempt_time
            msg = '(Re-)connected to {0} after {1} attempt(s), time spent {2}'.format(
                self._conn_info(), self.connection_attempts, delta)
            logger.warn(msg)
            
        self.connection_attempts = 1
        conn.channel(self._on_channel_open)
        
    def _on_channel_open(self, channel):
        self.channel = channel
        msg = 'Got a channel for {0}'.format(self._conn_info())
        logger.debug(msg)
        
    def _run(self):
        try:
            self.start()
        except KeyboardInterrupt:
            self.close()
            
    def _start(self):
        self.conn = SelectConnection(self.conn_params, self._on_connected)
        self.conn.ioloop.start()
        
    def start(self):
        
        # Set right after the publisher has been created
        self.first_connection_attempt_time = datetime.now() 
        
        while self.keep_running:
            try:
                
                # Actually try establishing the connection
                self._start()
                
                # Set only if there was an already established connection 
                # and we're now trying to reconnect to the broker.
                self.first_connection_attempt_time = datetime.now()
            except(TypeError, EnvironmentError), e:
                # We need to catch TypeError because pika will sometimes erroneously raise
                # it in self._start's self.conn.ioloop.start()
                if isinstance(e, TypeError) or e.errno in self.reconnect_error_numbers:
                    if isinstance(e, TypeError):
                        err_info = format_exc(e)
                    else:
                        err_info = '{0} {1}'.format(e.errno, e.strerror)
                    msg = 'Caught [{0}] error, will try to (re-)connect to {1} in {2} seconds, {3} attempt(s) so far, time spent {4}'
                    delta = datetime.now() - self.first_connection_attempt_time
                    logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = 'No connection for {0}, e=[{1}]'.format(self._conn_info(), format_exc(e))
                    logger.error(msg)
                    raise
        
    def close(self):
        if(logger.isEnabledFor(TRACE1)):
            msg = 'About to close the publisher for {0}'.format(self._conn_info())
            logger.log(TRACE1, msg)
            
        self.keep_running = False
        if self.conn:
            self.conn.ioloop.stop()
            self.conn.close()
            
        msg = 'Closed the publisher for {0}'.format(self._conn_info())
        logger.debug(msg)

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
        self.broker_client.name = 'parallel/thread'
        self.broker_client.token = self.thread_data.broker_config.broker_token
        self.broker_client.zmq_context = self.thread_data.broker_config.zmq_context
        self.broker_client.push_addr = self.thread_data.broker_config.broker_push_addr
        self.broker_client.pull_addr = self.thread_data.broker_config.broker_pull_addr
        self.broker_client.sub_addr = self.thread_data.broker_config.broker_sub_addr
        self.broker_client.on_pull_handler = self.on_broker_msg
        self.broker_client.on_sub_handler = self.on_broker_msg
        self.broker_client.init()
        self.broker_client.start()
        
    def _setup_amqp(self):
        """ Sets up AMQP channels and outgoing connections on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                for def_id, def_attrs in self.def_amqp.items():
                    for out_name, out_attrs in self.out_amqp.items():
                        if def_id == out_attrs.def_id:
                            self._recreate_amqp_publisher(def_id, out_attrs)
                            
    def _stop_amqp_publisher(self, out_name):
        """ Stops the given outgoing AMQP connection's publisher. The method must 
        be called from a method that holds onto all AMQP-related RLocks.
        """
        if self.out_amqp[out_name].publisher:
            self.out_amqp[out_name].publisher.close()
                            
    def _recreate_amqp_publisher(self, def_id, out_attrs):
        """ (Re-)creates an AMQP publisher and updates the related outgoing
        AMQP connection's attributes so that they point to the newly created
        publisher. The method must be called from a method that holds
        onto all AMQP-related RLocks.
        """
        if out_attrs.name in self.out_amqp:
            self._stop_amqp_publisher(out_attrs.name)
            del self.out_amqp[out_attrs.name]
            
        def_attrs = self.def_amqp[def_id]
        
        vhost = def_attrs.virtual_host if 'virtual_host' in def_attrs else def_attrs.vhost
        if 'credentials' in def_attrs:
            username = def_attrs.credentials.username
            password = def_attrs.credentials.password
        else:
            username = def_attrs.username
            password = def_attrs.password
        
        conn_params = self._amqp_conn_params(def_attrs, vhost, username, password, bool(def_attrs.heartbeat))
        
        # Default properties for published messages
        properties = self._amqp_basic_properties(out_attrs.content_type, 
            out_attrs.content_encoding, out_attrs.delivery_mode, out_attrs.priority, 
            out_attrs.expiration, out_attrs.user_id, out_attrs.app_id)

        # An outgoing AMQP connection's properties
        self.out_amqp[out_attrs.name] = out_attrs
        
        # An actual AMQP publisher
        if out_attrs.is_active:
            publisher = self._amqp_publisher(conn_params, def_id, out_attrs.name, properties)
            self.out_amqp[out_attrs.name].publisher = publisher
        
    def _amqp_conn_params(self, def_attrs, vhost, username, password, heartbeat):
        return ConnectionParameters(def_attrs.host, def_attrs.port, vhost, 
            PlainCredentials(username, password),
            frame_max=def_attrs.frame_max, heartbeat=heartbeat)

    def _amqp_basic_properties(self, content_type, content_encoding, delivery_mode, priority, expiration, user_id, app_id):
        return BasicProperties(content_type=content_type, content_encoding=content_encoding, 
            delivery_mode=delivery_mode, priority=priority, expiration=expiration, 
            user_id=user_id, app_id=app_id)

    def _amqp_basic_properties_from_attrs(self, out_attrs):
        return self._amqp_basic_properties(out_attrs.content_type, out_attrs.content_encoding, 
            out_attrs.delivery_mode, out_attrs.priority, out_attrs.expiration, 
            out_attrs.user_id, out_attrs.app_id)
    
    def _amqp_publisher(self, conn_params, def_id, out_name, properties):
        publisher = _AMQPPublisher(conn_params, def_id, out_name, properties)
        Thread(target=publisher._run).start()
        
        return publisher

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

    def def_amqp_get(self, id):
        """ Returns the configuration of the AMQP definition of the given name.
        """
        with self.def_amqp_lock:
            return self.def_amqp.get(id)
        
    def on_broker_pull_msg_DEFINITION_AMQP_CREATE(self, msg, *args):
        """ Creates a new AMQP definition.
        """
        with self.def_amqp_lock:
            msg.host = str(msg.host)
            self.def_amqp[msg.id] = msg
            
        if logger.isEnabledFor(TRACE1):
            msg = 'self.def_amqp is {0}'.format(self.def_amqp)
            logger.log(TRACE1, msg)
        
    def on_broker_pull_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        with self.def_amqp_lock:
            del self.def_amqp[msg.old_name]
            self.def_amqp[msg.id] = msg
            
        if logger.isEnabledFor(TRACE1):
            msg = 'self.def_amqp is {0}'.format(self.def_amqp)
            logger.log(TRACE1, msg)
        
    def on_broker_pull_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition.
        """
        with self.def_amqp_lock:
            del self.def_amqp[msg.id]
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._stop_amqp_publisher(out_name)
                        del self.out_amqp[out_name]
                        
        if logger.isEnabledFor(TRACE1):
            msg = 'self.def_amqp is {0}'.format(self.def_amqp)
            logger.log(TRACE1, msg)
        
    def on_broker_pull_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition and of any existing publishers
        using this definition.
        """
        with self.def_amqp_lock:
            self.def_amqp[msg.id]['password'] = msg.password
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._recreate_amqp_publisher(out_attrs.def_id, out_attrs)
                        
        if logger.isEnabledFor(TRACE1):
            msg = 'self.def_amqp is {0}'.format(self.def_amqp)
            logger.log(TRACE1, msg)
                
        
    def on_broker_pull_msg_DEFINITION_AMQP_RECONNECT(self, msg, *args):
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._recreate_amqp_publisher(out_attrs.def_id, out_attrs)
        
# ##############################################################################

    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP publisher.
        """ 
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._recreate_amqp_publisher(msg.def_id, msg)

    def out_amqp_get(self, name):
        """ Returns the configuration of an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            item = self.out_amqp.get(name)
            if item and item.is_active:
                return item

    def on_broker_pull_msg_OUTGOING_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'self.def_amqp is {0}'.format(self.def_amqp))
            
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_EDIT(self, msg, *args):
        """ Updates an outgoing AMQP connection.
        """
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'self.def_amqp is {0}'.format(self.def_amqp))
            
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_DELETE(self, msg, *args):
        """ Deletes an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            self._stop_amqp_publisher(msg.name)
            del self.out_amqp[msg.name]
        
# ##############################################################################

    def on_broker_pull_msg_SCHEDULER_JOB_EXECUTED(self, msg, args=None):

        service_info = self.thread_data.server.service_store.services[msg.service]
        class_ = service_info['service_class']
        instance = class_()
        instance.server = self.thread_data.server
        
        response = instance.handle(payload=msg.extra, raw_request=msg, channel='scheduler_job', thread_ctx=self)
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Invoked [{0}], response [{1}]'.format(msg.service, repr(response))
            logger.debug(str(msg))
            
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
                thread_data = deepcopy(self.worker_config)
                
                # .. though the ZMQ context is OK to be shared among multiple threads.
                thread_data.zmq_context = self.zmq_context
                
                # .. be careful with this, it's a reference to the main ParallelServer
                # this thread is running on.
                thread_data.server = self.server
                
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
            
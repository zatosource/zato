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
import logging, os, socket
from copy import deepcopy
from errno import ENOENT
from thread import start_new_thread
from threading import local, RLock
from traceback import format_exc

# Bunch
from bunch import Bunch

# zope.server
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httptask import HTTPTask
from zope.server.serverchannelbase import task_lock
from zope.server.taskthreads import ThreadedTaskDispatcher

# Paste
from paste.util.multidict import MultiDict

# Zato
from zato.common import SIMPLE_IO, ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name
from zato.common.util import new_cid, security_def_type, TRACE1
from zato.server.base import BaseWorker
from zato.server.connection.http_soap import HTTPSOAPWrapper, PlainHTTPHandler, RequestHandler, SOAPHandler
from zato.server.connection.http_soap import Security as ConnectionHTTPSOAPSecurity
from zato.server.connection.sql import PoolStore, SessionWrapper

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
        
        self.update_lock = RLock()
        
        plain_http_config = MultiDict()
        soap_config = MultiDict()
        
        copy = deepcopy(self.worker_config.http_soap)
        for url_path in copy:
            for soap_action in copy[url_path]:
                item = copy[url_path][soap_action]
                if item.connection == 'channel':
                    if item.transport == 'plain_http':
                        config = plain_http_config.setdefault(url_path, Bunch())
                        config[soap_action] = deepcopy(item)
                    else:
                        config = soap_config.setdefault(url_path, Bunch())
                        config[soap_action] = deepcopy(item)
        
        self.request_handler = RequestHandler(simple_io_config=self.worker_config.simple_io)
        self.request_handler.soap_handler = SOAPHandler(soap_config, self.worker_config.server)
        self.request_handler.plain_http_handler = PlainHTTPHandler(plain_http_config, self.worker_config.server)
        
        # ConnectionHTTPSOAPSecurity needs only actual URLs hence it's self.worker_config.url_sec[0]
        # below
        self.request_handler.security = ConnectionHTTPSOAPSecurity(self.worker_config.url_sec[0], 
                self.worker_config.basic_auth, self.worker_config.tech_acc, self.worker_config.wss)
        
        # Create all the expected connections
        self.init_sql()
        self.init_http_soap()
        
    def filter(self, msg):
        return True
    
    def init_sql(self):
        """ Initializes SQL connections, first to ODB and then any user-defined ones.
        """
        # We need a store first
        self.sql_pool_store = PoolStore()
        
        # Connect to ODB
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.worker_config.odb_data
        self.odb = SessionWrapper()
        self.odb.init_session(self.sql_pool_store[ZATO_ODB_POOL_NAME])
        
        # Any user-defined SQL connections left?
        for pool_name in self.worker_config.out_sql:
            config = self.worker_config.out_sql[pool_name]['config']
            self.sql_pool_store[pool_name] = config
            
    def _http_soap_wrapper_from_config(self, config, has_sec_config=True):
        """ Creates a new HTTP/SOAP connection wrapper out of a configuration
        dictionary. 
        """
        security_name = config.get('security_name')
        sec_config = {'security_name':security_name, 'sec_type':None, 'username':None, 
            'password':None, 'password_type':None}
        _sec_config = None

        # This will be set to True only if the method's invoked on a server's starting up
        if has_sec_config:
            # It's possible that there is no security config attached at all
            if security_name:
                _sec_config = config
        else:
            if security_name:
                sec_type = config.sec_type
                meth = getattr(self.request_handler.security, sec_type + '_get')
                _sec_config = meth(security_name).config
                
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'has_sec_config:[{}], security_name:[{}], _sec_config:[{}]'.format(
                has_sec_config, security_name, _sec_config))
                
        if _sec_config:
            sec_config['sec_type'] = _sec_config['sec_type']
            sec_config['username'] = _sec_config['username']
            sec_config['password'] = _sec_config['password']
            sec_config['password_type'] = _sec_config.get('password_type')
            
        wrapper_config = {'id':config.id, 
            'is_active':config.is_active, 'method':config.method, 
            'name':config.name, 'transport':config.transport, 
            'address':config.host + config.url_path, 
            'soap_action':config.soap_action, 'soap_version':config.soap_version}
        wrapper_config.update(sec_config)
        return HTTPSOAPWrapper(wrapper_config)
            
    def init_http_soap(self):
        """ Initializes plain HTTP/SOAP connections.
        """
        for transport in('soap', 'plain_http'):
            config_dict = getattr(self.worker_config, 'out_' + transport)
            for name in config_dict:
                config = config_dict[name].config
                
                wrapper = self._http_soap_wrapper_from_config(config)
                config_dict[name].conn = wrapper
                
                # To make the API consistent with that of SQL connection pools
                config_dict[name].ping = wrapper.ping
            
    def _update_auth(self, msg, action_name, sec_type, visit_wrapper, keys=None):
        """ A common method for updating auth-related configuration.
        """ 
        with self.update_lock:
            # Channels
            handler = getattr(self.request_handler.security, 'on_broker_pull_msg_' + action_name)
            handler(msg)
        
            for transport in('soap', 'plain_http'):
                config_dict = getattr(self.worker_config, 'out_' + transport)
                
                # Wrappers and static configuration for outgoing connections
                for name in config_dict.copy_keys():
                    config = config_dict[name].config
                    wrapper = config_dict[name].conn
                    if config['sec_type'] == sec_type:
                        if keys:
                            visit_wrapper(wrapper, msg, keys)
                        else:
                            visit_wrapper(wrapper, msg)
                        
    def _visit_wrapper_edit(self, wrapper, msg, keys):
        """ Updates a given wrapper's security configuration.
        """
        if wrapper.config['security_name'] == msg['old_name']:
            for key in keys:
                # All's good except for 'name', the msg's 'name' is known
                # as 'security_name' in wrapper's config.
                if key == 'name':
                    key1 = 'security_name'
                    key2 = key
                else:
                    key1, key2 = key, key
                wrapper.config[key1] = msg[key2]
            wrapper.set_auth()
    
    def _visit_wrapper_delete(self, wrapper, msg):
        """ Deletes a wrapper.
        """
        config_dict = getattr(self.worker_config, 'out_' + wrapper.config['transport'])
        if wrapper.config['security_name'] == msg['name']:
            del config_dict[wrapper.config['name']]
            
    def _visit_wrapper_change_password(self, wrapper, msg):
        """ Changes a wrapper's password.
        """
        if wrapper.config['security_name'] == msg['name']:
            wrapper.config['password'] = msg['password']
            wrapper.set_auth()
        
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
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_delete)
                    
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_change_password)

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
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name',
                    'nonce_freshness_time', 'reject_expiry_limit', 'password_type', 
                    'reject_empty_nonce_creat', 'reject_stale_tokens'))
        
    def on_broker_pull_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_delete)
        
    def on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_change_password)
            
# ##############################################################################

    def _on_message_invoke_service(self, msg, channel, action, args=None):
        """ Triggered by external processes, such as AMQP or the singleton's scheduler,
        creates a new service instance and invokes it.
        """
        service_instance = self.worker_config.server.service_store.new_instance(msg.service)
        service_instance.update(service_instance, self.worker_config.server, self.broker_client,
            self, msg.cid, msg.payload, msg.payload, None, self.worker_config.simple_io,
            msg.data_format if hasattr(msg, 'data_format') else None)
        
        service_instance._pre_handle()
        service_instance.handle()
        service_instance._post_handle()
        if not isinstance(service_instance.response.payload, basestring):
            service_instance.response.payload = service_instance.response.payload.getvalue()
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Invoked [{0}], channel [{1}], action [{2}], response [{3}]'.format(
                msg.service, channel, action, repr(service_instance.response.payload))
            logger.debug(msg)
            
# ##############################################################################

    def on_broker_pull_msg_SCHEDULER_JOB_EXECUTED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'scheduler', 'SCHEDULER_JOB_EXECUTED', args)

    def on_broker_pull_msg_CHANNEL_AMQP_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'amqp', 'CHANNEL_AMQP_MESSAGE_RECEIVED', args)
    
    def on_broker_pull_msg_CHANNEL_JMS_WMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'jms-wmq', 'CHANNEL_JMS_WMQ_MESSAGE_RECEIVED', args)
    
    def on_broker_pull_msg_CHANNEL_ZMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, 'zmq', 'CHANNEL_ZMQ_MESSAGE_RECEIVED', args)
    
# ##############################################################################

    def on_broker_pull_msg_OUTGOING_SQL_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an SQL connection, including changing its
        password.
        """
        # Is it a rename? If so, delete the connection first
        if msg.get('old_name') and msg.get('old_name') != msg['name']:
            del self.sql_pool_store[msg['old_name']]
            
        self.sql_pool_store[msg['name']] = msg
        
    def on_broker_pull_msg_OUTGOING_SQL_CHANGE_PASSWORD(self, msg, *args):
        """ Deletes an outgoing SQL connection pool and recreates it using the
        new password.
        """
        self.sql_pool_store.change_password(msg['name'], msg['password'])
        
    def on_broker_pull_msg_OUTGOING_SQL_DELETE(self, msg, *args):
        """ Deletes an outgoing SQL connection pool.
        """
        del self.sql_pool_store[msg['name']]

# ##############################################################################

    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        # Security
        self.request_handler.security.on_broker_pull_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)
        
        # A mapping between a URL and a service
        handler = getattr(self.request_handler, msg.transport + '_handler')
        handler.on_broker_pull_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)
        
    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        # Security
        self.request_handler.security.on_broker_pull_msg_CHANNEL_HTTP_SOAP_DELETE(msg, *args)
        
        # A mapping between a URL and a service
        handler = getattr(self.request_handler, msg.transport + '_handler')
        handler.on_broker_pull_msg_CHANNEL_HTTP_SOAP_DELETE(msg, *args)

# ##############################################################################

    def _delete_outgoing_http_soap(self, name, transport, log_meth):
        """ Actually deletes an outgoing HTTP/SOAP connection.
        """
        # Are we dealing with plain HTTP or SOAP?
        config_dict = getattr(self.worker_config, 'out_' + transport)
        
        # Delete the connection first, if it exists at all ..
        try:
            del config_dict[name]
        except(KeyError, AttributeError), e:
            log_meth('Could not delete an outgoing HTTP/SOAP connection, e:[{}]'.format(format_exc(e)))
        
    def on_broker_pull_msg_OUTGOING_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an outgoing HTTP/SOAP connection.
        """
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_outgoing_http_soap(msg['name'], msg['transport'], logger.debug)
        
        # .. and create a new one
        wrapper = self._http_soap_wrapper_from_config(msg, False)
        config_dict = getattr(self.worker_config, 'out_' + msg['transport'])
        config_dict[msg['name']] = Bunch()
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper
        config_dict[msg['name']].ping = wrapper.ping # (just like in self.init_http)
        
    def on_broker_pull_msg_OUTGOING_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an outgoing HTTP/SOAP connection (actually delegates the
        task to self._delete_outgoing_http_soap.
        """
        self._delete_outgoing_http_soap(msg['name'], msg['transport'], logger.error)
            
# ##############################################################################

    def on_broker_pull_msg_SERVICE_SET_REQUEST_RESPONSE(self, msg, *args):
        new_msg = Bunch()
        new_msg.cid = msg.cid
        new_msg.service = 'zato.server.service.internal.service.SetRequestResponse'
        new_msg.data_format = SIMPLE_IO.FORMAT.JSON
        new_msg.payload = msg
        return self._on_message_invoke_service(new_msg, 'req-resp', 'SERVICE_SET_REQUEST_RESPONSE', args)
    
    def on_broker_pull_msg_SERVICE_DELETE(self, msg, *args):
        """ Deletes the service from the service store and removes it from the filesystem
        if it's not an internal one.
        """
        # Where to delete it from in the second step
        fs_location = self.worker_config.server.service_store.services[msg.impl_name]['deployment_info']['fs_location']
        
        # Delete it from the service store
        del self.worker_config.server.service_store.services[msg.impl_name]
        
        # Delete it from the filesystem, including any bytecode left over. Note that
        # other parallel servers may wish to do exactly the same so we just ignore
        # the error if any files are missing. Also note that internal services won't
        # be ever deleted from the FS.
        if msg.is_internal:
            all_ext = ('py', 'pyc', 'pyo')
            no_ext = '.'.join(fs_location.split('.')[:-1])
            for ext in all_ext:
                path = '{}.{}'.format(no_ext, ext)
                try:
                    os.remove(path)
                except OSError, e:
                    if e.errno != ENOENT:
                        raise
                
    def on_broker_pull_msg_SERVICE_EDIT(self, msg, *args):
        self.worker_config.server.service_store.services[msg.impl_name]['is_active'] = msg.is_active
        
# ##############################################################################

    def on_broker_pull_msg_HOT_DEPLOY_CREATE(self, msg, *args):
        msg.cid = new_cid()
        msg.service = 'zato.server.service.internal.hot_deploy.Create'
        msg.payload = {'package_id': msg.package_id}
        msg.data_format = SIMPLE_IO.FORMAT.JSON
        return self._on_message_invoke_service(msg, 'hot-deploy', 'HOT_DEPLOY_CREATE', args)

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
    def service(self, thread_ctx):
        try:
            try:
                self.start()
                self.channel.server.executeRequest(self, thread_ctx)
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
    
    def service(self, thread_ctx):
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
                task.service(thread_ctx)
            except:
                # propagate the exception, but keep executing tasks
                self.server.addTask(self)
                raise
            
# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, inspect, os, socket, sys, traceback
from copy import deepcopy
from errno import ENOENT
from threading import RLock
from time import sleep
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MINUTELY, rrule

# gunicorn
from gunicorn.workers.ggevent import GeventWorker as GunicornGeventWorker
from gunicorn.workers.sync import SyncWorker as GunicornSyncWorker

# Paste
from paste.util.multidict import MultiDict

# Zato
from zato.common import CHANNEL, SIMPLE_IO, ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name, STATS
from zato.common.util import new_cid, pairwise, security_def_type, TRACE1
from zato.server.base import BrokerMessageReceiver
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.sql import PoolStore, SessionWrapper
from zato.server.stats import MaintenanceTool

logger = logging.getLogger(__name__)

class GeventWorker(GunicornGeventWorker):
    def __init__(self, *args, **kwargs):
        self.deployment_key = uuid4().hex
        super(GunicornGeventWorker, self).__init__(*args, **kwargs)

class SyncWorker(GunicornSyncWorker):
    def __init__(self, *args, **kwargs):
        self.deployment_key = uuid4().hex
        super(GunicornSyncWorker, self).__init__(*args, **kwargs)

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
    def __init__(self, worker_config=None, server=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.worker_config = worker_config
        self.server = server
        self.update_lock = RLock()
        self.kvdb = server.kvdb
        self.broker_client = None
        
    def init(self):
        
        # Statistics maintenance
        self.stats_maint = MaintenanceTool(self.kvdb.conn)

        # Request dispatcher - matches URLs, checks security and dispatches HTTP
        # requests to services.
        self.request_dispatcher = RequestDispatcher(simple_io_config=self.worker_config.simple_io)
        self.request_dispatcher.url_data = URLData(
            deepcopy(self.worker_config.http_soap),
            self.server.odb.get_url_security(self.server.cluster_id, 'channel')[0],
            self.worker_config.basic_auth, self.worker_config.tech_acc, self.worker_config.wss)
        
        self.request_dispatcher.request_handler = RequestHandler(self.server)
        
        # Create all the expected connections
        self.init_sql()
        self.init_ftp()
        self.init_http_soap()
        
    def filter(self, msg):
        # TODO: Fix it, worker doesn't need to accept all the messages
        return True
    
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
                func = getattr(self.request_dispatcher.url_data, sec_type + '_get')
                _sec_config = func(security_name).config
                
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'has_sec_config:[{}], security_name:[{}], _sec_config:[{}]'.format(
                has_sec_config, security_name, _sec_config))
                
        if _sec_config:
            sec_config['sec_type'] = _sec_config['sec_type']
            sec_config['username'] = _sec_config['username']
            sec_config['password'] = _sec_config['password']
            sec_config['password_type'] = _sec_config.get('password_type')
            sec_config['salt'] = _sec_config.get('salt')
            
        wrapper_config = {'id':config.id, 
            'is_active':config.is_active, 'method':config.method, 
            'name':config.name, 'transport':config.transport, 
            'address':config.host + config.url_path, 
            'soap_action':config.soap_action, 'soap_version':config.soap_version,
            'ping_method':config.ping_method, 'pool_size':config.pool_size,}
        wrapper_config.update(sec_config)
        return HTTPSOAPWrapper(wrapper_config)
    
    def init_sql(self):
        """ Initializes SQL connections, first to ODB and then any user-defined ones.
        """
        # We need a store first
        self.sql_pool_store = PoolStore()
        
        # Connect to ODB
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.worker_config.odb_data
        self.odb = SessionWrapper()
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.worker_config.odb_data, self.sql_pool_store[ZATO_ODB_POOL_NAME].pool)
        
        # Any user-defined SQL connections left?
        for pool_name in self.worker_config.out_sql:
            config = self.worker_config.out_sql[pool_name]['config']
            self.sql_pool_store[pool_name] = config
    
    def init_ftp(self):
        """ Initializes FTP connetions. The method replaces whatever value self.out_ftp
        previously had (initially this would be a ConfigDict of connection definitions).
        """
        config_list = self.worker_config.out_ftp.get_config_list()
        self.worker_config.out_ftp = FTPStore()
        self.worker_config.out_ftp.add_params(config_list)
            
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
            handler = getattr(self.request_dispatcher.url_data, 'on_broker_msg_' + action_name)
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
        self.request_dispatcher.url_data.basic_auth_get(name)

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg, *args)
        
    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_delete)
                    
    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.basic_auth,
                self._visit_wrapper_change_password)

# ##############################################################################

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        self.request_dispatcher.url_data.tech_acc_get(name)

    def on_broker_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_TECH_ACC_CREATE(msg, *args)
        
    def on_broker_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_TECH_ACC_EDIT(msg, *args)
        
    def on_broker_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_TECH_ACC_DELETE(msg, *args)
        
    def on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(msg, *args)
            
# ##############################################################################

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        self.request_dispatcher.url_data.wss_get(name)

    def on_broker_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        self.request_dispatcher.url_data.on_broker_msg_SECURITY_WSS_CREATE(msg, *args)
        
    def on_broker_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name',
                    'nonce_freshness_time', 'reject_expiry_limit', 'password_type', 
                    'reject_empty_nonce_creat', 'reject_stale_tokens'))
        
    def on_broker_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_delete)
        
    def on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], security_def_type.wss,
                self._visit_wrapper_change_password)
            
# ##############################################################################

    def _set_service_response_data(self, service, **ignored):
        if not isinstance(service.response.payload, basestring):
            service.response.payload = service.response.payload.getvalue()

    def _on_message_invoke_service(self, msg, channel, action, args=None):
        """ Triggered by external processes, such as AMQP or the singleton's scheduler,
        creates a new service instance and invokes it.
        """
        # WSGI environment is the best place we have to store raw msg in
        wsgi_environ = {'zato.request_ctx.async_msg':msg}
        
        service = self.server.service_store.new_instance_by_name(msg.service)
        service.update_handle(self._set_service_response_data, service, msg.payload,
            channel, msg.get('data_format'), msg.get('transport'), self.server,
            self.broker_client, self, msg.cid, self.worker_config.simple_io,
            job_type=msg.get('job_type'), wsgi_environ=wsgi_environ)

# ##############################################################################

    def on_broker_msg_SCHEDULER_JOB_EXECUTED(self, msg, args=None):
        return self._on_message_invoke_service(msg, CHANNEL.SCHEDULER, 'SCHEDULER_JOB_EXECUTED', args)

    def on_broker_msg_CHANNEL_AMQP_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, CHANNEL.AMQP, 'CHANNEL_AMQP_MESSAGE_RECEIVED', args)
    
    def on_broker_msg_CHANNEL_JMS_WMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, CHANNEL.JMS_WMQ, 'CHANNEL_JMS_WMQ_MESSAGE_RECEIVED', args)
    
    def on_broker_msg_CHANNEL_ZMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self._on_message_invoke_service(msg, CHANNEL.ZMQ, 'CHANNEL_ZMQ_MESSAGE_RECEIVED', args)
    
# ##############################################################################

    def on_broker_msg_OUTGOING_SQL_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an SQL connection, including changing its
        password.
        """
        # Is it a rename? If so, delete the connection first
        if msg.get('old_name') and msg.get('old_name') != msg['name']:
            del self.sql_pool_store[msg['old_name']]
            
        self.sql_pool_store[msg['name']] = msg
        
    def on_broker_msg_OUTGOING_SQL_CHANGE_PASSWORD(self, msg, *args):
        """ Deletes an outgoing SQL connection pool and recreates it using the
        new password.
        """
        self.sql_pool_store.change_password(msg['name'], msg['password'])
        
    def on_broker_msg_OUTGOING_SQL_DELETE(self, msg, *args):
        """ Deletes an outgoing SQL connection pool.
        """
        del self.sql_pool_store[msg['name']]

# ##############################################################################

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)
        
    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(msg, *args)

# ##############################################################################

    def _delete_outgoing_http_soap(self, name, transport, log_func):
        """ Actually deletes an outgoing HTTP/SOAP connection.
        """
        # Are we dealing with plain HTTP or SOAP?
        config_dict = getattr(self.worker_config, 'out_' + transport)
        
        # Delete the connection first, if it exists at all ..
        try:
            try:
                wrapper = config_dict[name].conn
            except (KeyError, AttributeError), e:
                log_func('Could not access a wrapper, e:[{}]'.format(format_exc(e)))
            else:
                try:
                    wrapper.session.close()
                finally:
                    del config_dict[name]
        except Exception, e:
            log_func('Could not delete an outgoing HTTP/SOAP connection, e:[{}]'.format(format_exc(e)))
        
    def on_broker_msg_OUTGOING_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an outgoing HTTP/SOAP connection.
        """
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_outgoing_http_soap(del_name, msg['transport'], logger.debug)
        
        # .. and create a new one
        wrapper = self._http_soap_wrapper_from_config(msg, False)
        config_dict = getattr(self.worker_config, 'out_' + msg['transport'])
        config_dict[msg['name']] = Bunch()
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper
        config_dict[msg['name']].ping = wrapper.ping # (just like in self.init_http)
        
    def on_broker_msg_OUTGOING_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an outgoing HTTP/SOAP connection (actually delegates the
        task to self._delete_outgoing_http_soap.
        """
        self._delete_outgoing_http_soap(msg['name'], msg['transport'], logger.error)
            
# ##############################################################################

    def on_broker_msg_SERVICE_DELETE(self, msg, *args):
        """ Deletes the service from the service store and removes it from the filesystem
        if it's not an internal one.
        """
        # Module this service is in so it can be removed from sys.modules
        mod = inspect.getmodule(self.server.service_store.services[msg.impl_name]['service_class'])

        # Where to delete it from in the second step
        fs_location = self.server.service_store.services[msg.impl_name]['deployment_info']['fs_location']
        
        # Delete it from the service store
        del self.server.service_store.services[msg.impl_name]
        
        # Delete it from the filesystem, including any bytecode left over. Note that
        # other parallel servers may wish to do exactly the same so we just ignore
        # the error if any files are missing. Also note that internal services won't
        # be ever deleted from the FS.
        if not msg.is_internal:
            all_ext = ('py', 'pyc', 'pyo')
            no_ext = '.'.join(fs_location.split('.')[:-1])
            for ext in all_ext:
                path = '{}.{}'.format(no_ext, ext)
                try:
                    os.remove(path)
                except OSError, e:
                    if e.errno != ENOENT:
                        raise
        
        # Makes it actually gets reimported next time it's redeployed
        del sys.modules[mod.__name__]
                
    def on_broker_msg_SERVICE_EDIT(self, msg, *args):
        for name in('is_active', 'slow_threshold'):
            self.server.service_store.services[msg.impl_name][name] = msg[name]

# ##############################################################################

    def on_broker_msg_OUTGOING_FTP_CREATE_EDIT(self, msg, *args):
        self.worker_config.out_ftp.create_edit(msg, msg.get('old_name'))

    def on_broker_msg_OUTGOING_FTP_DELETE(self, msg, *args):
        self.worker_config.out_ftp.delete(msg.name)
    
    def on_broker_msg_OUTGOING_FTP_CHANGE_PASSWORD(self, msg, *args):
        self.worker_config.out_ftp.change_password(msg.name, msg.password)
        
# ##############################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE(self, msg, *args):
        msg.cid = new_cid()
        msg.service = 'zato.hot-deploy.create'
        msg.payload = {'package_id': msg.package_id}
        msg.data_format = SIMPLE_IO.FORMAT.JSON
        return self._on_message_invoke_service(msg, 'hot-deploy', 'HOT_DEPLOY_CREATE', args)
    
# ##############################################################################

    def on_broker_msg_STATS_DELETE(self, msg, *args):
        start = parse(msg.start)
        stop = parse(msg.stop)
        
        # Looks weird but this is so we don't have to create a list instead of a generator
        # (and Python 3 won't leak the last element anymore)
        last_elem = None
        
        # Are the dates are at least a day apart? If so, we'll split the interval
        # into smaller one day-long batches.
        if(stop-start).days:
            for elem1, elem2 in pairwise(elem for elem in rrule(DAILY, dtstart=start, until=stop)):
                self.broker_client.invoke_async({'action':STATS.DELETE_DAY, 'start':elem1.isoformat(), 'stop':elem2.isoformat()})
                   
                # So as not to drown the broker with a sudden surge of messages
                sleep(0.02)
            
                last_elem = elem2
                
            # It's possible we still have something left over. Let's say
            # 
            # start = '2012-07-24T02:02:53'
            # stop = '2012-07-25T02:04:53'
            #
            # The call to rrule(DAILY, ...) will nicely slice the time between
            # start and stop into one day intervals yet the last element of the slice
            # will have the time portion equal to that of start - so in this
            # particular case it would be that last_elem was 2012-07-25T02:02:53
            # which would be still be 2 minutes short of stop. Hence the need for
            # a relativedelta, to tease out the remaining time information.
            delta = relativedelta(stop, last_elem)
            if delta.minutes:
                self.stats_maint.delete(last_elem, stop, MINUTELY)

        # Not a full day apart so we can delete everything ourselves   
        else:
            self.stats_maint.delete(start, stop, MINUTELY)

    def on_broker_msg_STATS_DELETE_DAY(self, msg, *args):
        self.stats_maint.delete(parse(msg.start), parse(msg.stop), MINUTELY)

# ##############################################################################

    def on_broker_msg_SERVICE_PUBLISH(self, msg, args=None):
        return self._on_message_invoke_service(msg, CHANNEL.INVOKE_ASYNC, 'SERVICE_PUBLISH', args)
        
# ##############################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# stdlib
import errno, logging, socket
from threading import RLock

# Pika
from pika.adapters import SelectConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import BasicProperties

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import AMQP_CONNECTOR, DEFINITION
from zato.common import TRACE1
from zato.server.connection import BaseConnection, BaseConnector

logger = logging.getLogger('zato_connector')

def _conn_info(host, port, vhost, item_name):
    return '{0}:{1}{2} ({3})'.format(host, port, vhost, item_name)

class BaseAMQPConnection(BaseConnection):
    """ An object which does an actual job of (re-)connecting to the the AMQP broker.
    Concrete subclasses implement either listening or publishing features.
    """
    def __init__(self, conn_params, item_name, properties=None):
        super(BaseAMQPConnection, self).__init__()
        self.conn_params = conn_params
        self.item_name = item_name
        self.properties = properties
        self.conn = None
        self.channel = None
        self.reconnect_exceptions = (TypeError, EnvironmentError)

    def _start(self):
        self.conn = SelectConnection(self.conn_params, self._on_connected)
        self.conn.ioloop.start()
        
    def _close(self):
        """ Actually close the connection.
        """
        if self.conn:
            try:
                self.conn.close()
            except socket.error, e:
                if e.errno != errno.EBADF:
                    # EBADF meant we actually had a connection but it was unusable (like the credentials were incorrect)
                    raise
            
    def _conn_info(self):
        return _conn_info(self.conn_params.host, self.conn_params.port, self.conn_params.virtual_host, self.item_name)
            
    def _on_channel_open(self, channel):
        self.channel = channel
        if logger.isEnabledFor(logging.DEBUG):
            msg = u'Got a channel for {0}'.format(self._conn_info())
            logger.debug(msg)
        
    def _keep_connecting(self, e):
        # We need to catch TypeError because pika will sometimes erroneously raise
        # it in self._start's self.conn.ioloop.start().
        # Otherwise, it may one of the network errors we are hopefully able to recover from.
        return isinstance(e, TypeError) or (isinstance(e, EnvironmentError) 
                                            and e.errno in self.reconnect_error_numbers)
            
    def _on_connected(self, conn):
        """ Invoked after establishing a successful connection to an AMQP broker.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hasn't been established straightaway.
        """
        self.has_valid_connection = True
        super(BaseAMQPConnection, self)._on_connected()
        conn.channel(self._on_channel_open)
        
class BaseAMQPConnector(BaseConnector):
    """ A base connector for any AMQP-related ones.
    """
    def _init(self):
        self.def_amqp = Bunch()
        self.def_amqp_lock = RLock()
        
        # One of these will be used depending whether the subclass is a channel
        # or an outgoing AMQP connection.
        
        self.out_amqp = Bunch()
        self.channel_amqp = Bunch()
        
        self.out_amqp_lock = RLock()
        self.channel_amqp_lock = RLock()
        
        super(BaseAMQPConnector, self)._init()
        
    def _conn_info(self):
        return _conn_info(self.def_amqp.host, self.def_amqp.port, self.def_amqp.vhost, self.out_amqp.name)
    
    def filter(self, msg):
        """ The base class knows how to manage the AMQP definitions but not channels
        or outgoing connections.
        """
        if msg.action == AMQP_CONNECTOR.CLOSE.value:
            if self.odb.token == msg['token']:
                return True
            
        elif msg.action in(DEFINITION.AMQP_EDIT.value, DEFINITION.AMQP_DELETE.value, DEFINITION.AMQP_CHANGE_PASSWORD.value):
            if self.def_amqp.id == msg.id:
                return True
        
    def on_broker_msg_AMQP_CONNECTOR_CLOSE(self, msg, *args):
        """ Stops the publisher, ODB connection and exits the process.
        """
        self._close()
        
    def on_broker_msg_DEFINITION_AMQP_CREATE(self, msg, *args):
        """ Creates a new AMQP definition.
        """
        with self.def_amqp_lock:
            msg.host = str(msg.host)
            self.def_amqp[msg.id] = msg
        
    def on_broker_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        with self.def_amqp_lock:
            password = self.def_amqp.password
            self.def_amqp = msg
            self.def_amqp.password = password
            self.def_amqp.host = str(self.def_amqp.host)
            self._recreate()
            
    def on_broker_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition and stops the process.
        """
        self._close()
        
    def on_broker_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition and of any existing publishers
        using this definition.
        """
        with self.def_amqp_lock:
            self.def_amqp['password'] = msg.password
            self._recreate()
                    
    def _recreate(self):
        with self.out_amqp_lock:
            with self.channel_amqp_lock:
                recreate_func = '_recreate_sender' if hasattr(self, '_recreate_sender') else '_recreate_consumer'
                getattr(self, recreate_func)()
                if logger.isEnabledFor(TRACE1):
                    log_msg = 'self.def_amqp [{0}]'.format(self.def_amqp)
                    logger.log(TRACE1, log_msg)
                
    def _amqp_conn_params(self):
        
        vhost = self.def_amqp.virtual_host if 'virtual_host' in self.def_amqp else self.def_amqp.vhost
        if 'credentials' in self.def_amqp:
            username = self.def_amqp.credentials.username
            password = self.def_amqp.credentials.password
        else:
            username = self.def_amqp.username
            password = self.def_amqp.password
            
        params = ConnectionParameters(self.def_amqp.host, int(self.def_amqp.port), vhost, 
            PlainCredentials(username, password),
            frame_max=int(self.def_amqp.frame_max))
        
        # heartbeat is an integer but ConnectionParameter.__init__ insists it
        # be a boolean.
        params.heartbeat = float(self.def_amqp.heartbeat)
        
        return params

    def _amqp_basic_properties(self, content_type, content_encoding, delivery_mode, priority, expiration, user_id, app_id):
        return BasicProperties(content_type=content_type, content_encoding=content_encoding, 
            delivery_mode=delivery_mode, priority=priority, expiration=expiration, 
            user_id=user_id, app_id=app_id)

    def _amqp_basic_properties_from_attrs(self, out_attrs):
        return self._amqp_basic_properties(out_attrs.content_type, out_attrs.content_encoding, 
            out_attrs.delivery_mode, out_attrs.priority, out_attrs.expiration, 
            out_attrs.user_id, out_attrs.app_id)
                
    def _stop_amqp_connection(self):
        """ Stops the AMQP connection, a subclass needs to implement it.
        """
        raise NotImplementedError('Must be implemented by a subclass')
                
    def _close(self):
        """ Deletes an outgoing AMQP connection, closes all the other connections
        and stops the process.
        """
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._stop_amqp_connection()
                super(BaseAMQPConnector, self)._close()
                
    def _setup_odb(self):
        super(BaseAMQPConnector, self)._setup_odb()
        
        item = self.odb.get_def_amqp(self.server.cluster.id, self.def_id)
        self.def_amqp = Bunch()
        self.def_amqp.name = item.name
        self.def_amqp.id = item.id
        self.def_amqp.host = str(item.host)
        self.def_amqp.port = item.port
        self.def_amqp.vhost = str(item.vhost)
        self.def_amqp.username = item.username
        self.def_amqp.password = item.password
        self.def_amqp.heartbeat = item.heartbeat
        self.def_amqp.frame_max = item.frame_max

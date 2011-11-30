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

from __future__ import absolute_import, division, print_function

# Setting the custom logger must come first
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

# stdlib
import os, sys
from subprocess import Popen
from threading import RLock

# ZeroMQ
import zmq

# Pika
from pika import BasicProperties
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import BasicProperties

# psutil
import psutil

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ConnectionException, PORTS, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.util import get_app_context, get_config, get_crypto_manager, TRACE1
from zato.server.base import BaseWorker

class BaseConnector(BaseWorker):
    """ A base class for both AMQP channels and outgoing connections.
    """
    def __init__(self, repo_location, def_id):
        self.repo_location = repo_location
        self.def_id = def_id
        self.odb = None
        
    def _init(self):
        """ Initializes all the run-time data structures, fetches configuration,
        connects to the ODB and the AMQP broker.
        """
        
        # Imported here to avoid circular dependencies
        from zato.server.config.app import ZatoContext

        config = get_config(self.repo_location, 'server.conf')
        app_context = get_app_context(config, ZatoContext)
        crypto_manager = get_crypto_manager(self.repo_location, app_context, config)
        
        self.odb = app_context.get_object('odb_manager')
        self.odb.crypto_manager = crypto_manager
        self.odb.odb_data = config['odb']
        
        self.def_amqp = Bunch()
        self.def_amqp_lock = RLock()
        
        # One of these will be used depending whether the subclass is a channel
        # or an outgoing AMQP connection.
        
        self.out_amqp = Bunch()
        self.channel_amqp = Bunch()
        
        self.out_amqp_lock = RLock()
        self.channel_amqp_lock = RLock()
        
        self._setup_odb()
        
        self.worker_data = Bunch()
        self.worker_data.broker_config = Bunch()
        self.worker_data.broker_config.name = 'amqp-connector'
        self.worker_data.broker_config.broker_token = self.server.cluster.broker_token
        self.worker_data.broker_config.zmq_context = zmq.Context()

        broker_push_client_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.BROKER_PUSH_CONNECTOR_AMQP_PULL)
        
        client_push_broker_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.CONNECTOR_AMQP_PUSH_BROKER_PULL)
        
        broker_pub_client_sub = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.BROKER_PUB_CONNECTOR_AMQP_SUB)
        
        self.worker_data.broker_config.broker_push_client_pull = broker_push_client_pull
        self.worker_data.broker_config.client_push_broker_pull = client_push_broker_pull
        self.worker_data.broker_config.broker_pub_client_sub = broker_pub_client_sub

        # Connects to the broker
        super(BaseConnector, self)._init()
        
    def _setup_odb(self):
        
        # First let's see if the server we're running on top of exists in the ODB.
        self.server = self.odb.fetch_server()
        if not self.server:
            raise Exception('Server does not exist in the ODB')

        item = self.odb.get_def_amqp(self.server.cluster.id, self.def_id)
        self.def_amqp = Bunch()
        self.def_amqp.name = item.name
        self.def_amqp.id = item.id
        self.def_amqp.host = str(item.host)
        self.def_amqp.port = item.port
        self.def_amqp.vhost = item.vhost
        self.def_amqp.username = item.username
        self.def_amqp.password = item.password
        self.def_amqp.heartbeat = item.heartbeat
        self.def_amqp.frame_max = item.frame_max
        
        item = self.odb.get_out_amqp(self.server.cluster.id, self.out_id)
        self.out_amqp = Bunch()
        self.out_amqp.id = item.id
        self.out_amqp.name = item.name
        self.out_amqp.is_active = item.is_active
        self.out_amqp.delivery_mode = item.delivery_mode
        self.out_amqp.priority = item.priority
        self.out_amqp.content_type = item.content_type
        self.out_amqp.content_encoding = item.content_encoding
        self.out_amqp.expiration = item.expiration
        self.out_amqp.user_id = item.user_id
        self.out_amqp.app_id = item.app_id
        self.out_amqp.def_name = item.def_name
        self.out_amqp.def_id = item.def_id
        self.out_amqp.publisher = None
        
    def on_broker_pull_msg_DEFINITION_AMQP_CREATE(self, msg, *args):
        """ Creates a new AMQP definition.
        """
        with self.def_amqp_lock:
            msg.host = str(msg.host)
            self.def_amqp[msg.id] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        with self.def_amqp_lock:
            
            password = self.def_amqp.password
            self.def_amqp = msg
            self.def_amqp.password = password
            self.def_amqp.host = str(self.def_amqp.host)
            
            with self.out_amqp_lock:
                with self.channel_amqp_lock:
                    self._recreate_amqp_publisher()
                    if self.logger.isEnabledFor(TRACE1):
                        log_msg = 'self.def_amqp [{0}]'.format(self.def_amqp)
                        self.logger.log(TRACE1, log_msg)
        
    def on_broker_pull_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition and stops the process.
        """
        self._close()
        
    def on_broker_pull_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition and of any existing publishers
        using this definition.
        """
        with self.def_amqp_lock:
            self.def_amqp['password'] = msg.password
            with self.out_amqp_lock:
                self._recreate_amqp_publisher()
                
    def _amqp_conn_params(self, def_attrs, vhost, username, password, heartbeat):
        params = ConnectionParameters(def_attrs.host, def_attrs.port, vhost, 
            PlainCredentials(username, password),
            frame_max=def_attrs.frame_max)
        
        # heartbeat is an integer but ConnectionParameter.__init__ insists it
        # be a boolean.
        params.heartbeat = heartbeat
        
        return params

    def _amqp_basic_properties(self, content_type, content_encoding, delivery_mode, priority, expiration, user_id, app_id):
        return BasicProperties(content_type=content_type, content_encoding=content_encoding, 
            delivery_mode=delivery_mode, priority=priority, expiration=expiration, 
            user_id=user_id, app_id=app_id)

    def _amqp_basic_properties_from_attrs(self, out_attrs):
        return self._amqp_basic_properties(out_attrs.content_type, out_attrs.content_encoding, 
            out_attrs.delivery_mode, out_attrs.priority, out_attrs.expiration, 
            out_attrs.user_id, out_attrs.app_id)
                
    def _stop_amqp_publisher(self):
        """ Stops the publisher, a subclass needs to implement it.
        """
        raise NotImplementedError('Must be implemented by a subclass')
                
    def _close(self):
        """ Deletes an outgoing AMQP connection, closes all the other connections
        and stops the process.
        """
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._stop_amqp_publisher()
                self.odb.close()
                
                p = psutil.Process(os.getpid())
                p.terminate()

def start_connector(repo_location, amqp_file, out_id, def_id):
    """ Starts a new connector process.
    """
    
    # Believe it or not but this is the only sane way to make AMQP subprocesses 
    # work as of now (15 XI 2011).
    
    # Subprocesses spawned in a shell need to use
    # the wrapper which sets up the PYTHONPATH instead of the regular Python
    # executable, because the executable may not have all the dependencies required.
    # Of course, this needs to be squared away before Zato gets into any Linux 
    # distribution but then the situation will be much simpler as we simply won't 
    # have to patch up anything, the distro will take care of any dependencies.
    executable = os.path.join(os.path.dirname(sys.executable), 'py')
    
    if amqp_file[-1] in('c', 'o'): # Need to use the source code file
        amqp_file = amqp_file[:-1]
    
    program = '{0} {1}'.format(executable, amqp_file)
    
    zato_env = {}
    zato_env['ZATO_REPO_LOCATION'] = repo_location
    zato_env['ZATO_CONNECTOR_AMQP_OUT_ID'] = str(out_id)
    zato_env['ZATO_CONNECTOR_AMQP_DEF_ID'] = str(def_id)
    
    _env = os.environ
    _env.update(zato_env)
    
    Popen(program, close_fds=True, shell=True, env=_env)

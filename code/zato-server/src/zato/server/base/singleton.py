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
import logging
from datetime import datetime
from time import sleep

# anyjson
from anyjson import dumps

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ZATO_OK, ZatoException
from zato.common.broker_message import SCHEDULER
from zato.common.util import deployment_info
from zato.server.base import BrokerMessageReceiver

_scheduler_values = SCHEDULER.values()

logger = logging.getLogger(__name__)

class SingletonServer(BrokerMessageReceiver):
    """ A server of which one instance only may be running in a Zato container.
    Holds and processes data which can't be made parallel, such as scheduler,
    hot-deployment or on-disk configuration management.
    """
    
    def __init__(self, parallel_server=None, server_id=None, scheduler=None, 
                 broker_token=None, zmq_context=None, broker_host=None, broker_push_singleton_pull_port=None, 
                 singleton_push_broker_pull_port=None, initial_sleep_time=None,
                 is_connector_server=False):
        self.parallel_server = parallel_server
        self.server_id = server_id
        self.scheduler = scheduler
        self.broker_token = broker_token
        self.broker_host = broker_host
        self.broker_push_singleton_pull_port = broker_push_singleton_pull_port
        self.singleton_push_broker_pull_port = singleton_push_broker_pull_port
        self.zmq_context = zmq_context
        self.initial_sleep_time = initial_sleep_time
        self.is_connector_server = is_connector_server

    def run(self, *ignored_args, **kwargs):
        # So that other moving parts - like connector subprocesses - have time
        # to initialize before the singleton server starts the scheduler.
        logger.debug('Sleeping for {0} s'.format(self.initial_sleep_time))
        sleep(self.initial_sleep_time)

        for name in('broker_token', 'zmq_context', 'broker_host', 'broker_push_singleton_pull_port', 
                    'singleton_push_broker_pull_port'):
            if name in kwargs:
                setattr(self, name, kwargs[name])
                
        self.broker_push_client_pull = 'tcp://{0}:{1}'.format(self.broker_host, self.broker_push_singleton_pull_port)
        self.client_push_broker_pull = 'tcp://{0}:{1}'.format(self.broker_host, self.singleton_push_broker_pull_port)
        
        # Initialize scheduler.
        self.scheduler.singleton = self
        
        self.broker_client = BrokerClient()
        self.broker_client.name = 'singleton'
        self.broker_client.token = self.broker_token
        self.broker_client.zmq_context = self.zmq_context
        self.broker_client.broker_push_client_pull = self.broker_push_client_pull
        self.broker_client.client_push_broker_pull = self.client_push_broker_pull
        self.broker_client.on_pull_handler = self.on_broker_msg
        self.broker_client.init()
        self.broker_client.start()
        
        # Start the hot-reload pickup monitor
        logger.info('Pickup notifier starting')
        self.pickup.watch()

################################################################################        

    def hot_deploy(self, file_name, path):
        """ Hot deploys a file pointed to by the 'path' parameter.
        """
        logger.debug('About to hot-deploy [{}]'.format(path))
        now = datetime.utcnow()
        di = dumps(deployment_info('hot-deploy', file_name, now.isoformat(), path))
        
        # Insert the package into the DB ..
        package_id = self.parallel_server.odb.hot_deploy(now, di, file_name, 
            open(path, 'rb').read(), self.server_id)
        
        # .. and notify all the servers they're to pick up a delivery
        self.parallel_server.notify_new_package(package_id)
        
################################################################################

    def filter(self, msg):
        if msg.action in _scheduler_values:
            return True
        return False

    def on_broker_pull_msg_SCHEDULER_CREATE(self, msg, *ignored_args):
        self.scheduler.create_edit('create', msg)
        
    def on_broker_pull_msg_SCHEDULER_EDIT(self, msg, *ignored_args):
        self.scheduler.create_edit('edit', msg)
        
    def on_broker_pull_msg_SCHEDULER_DELETE(self, msg, *ignored_args):
        self.scheduler.delete(msg)
        
    def on_broker_pull_msg_SCHEDULER_EXECUTE(self, msg, *ignored_args):
        self.scheduler.execute(msg)

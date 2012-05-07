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
from datetime import datetime, timedelta
from time import sleep

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ZATO_OK, ZatoException
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER
from zato.common.util import deployment_info
from zato.server.base import BrokerMessageReceiver

_scheduler_values = SCHEDULER.values()

class SingletonServer(BrokerMessageReceiver):
    """ A server of which one instance only may be running in a Zato container.
    Holds and processes data which can't be made parallel, such as scheduler,
    hot-deployment or on-disk configuration management.
    """
    
    def __init__(self, parallel_server=None, server_id=None, scheduler=None, 
                 broker_token=None, zmq_context=None, broker_host=None, broker_push_singleton_pull_port=None, 
                 singleton_push_broker_pull_port=None, initial_sleep_time=None,
                 is_cluster_wide=False):
        self.parallel_server = parallel_server
        self.server_id = server_id
        self.scheduler = scheduler
        self.broker_token = broker_token
        self.broker_host = broker_host
        self.broker_push_singleton_pull_port = broker_push_singleton_pull_port
        self.singleton_push_broker_pull_port = singleton_push_broker_pull_port
        self.zmq_context = zmq_context
        self.initial_sleep_time = initial_sleep_time
        self.is_cluster_wide = is_cluster_wide
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, *ignored_args, **kwargs):
        # So that other moving parts - like connector subprocesses - have time
        # to initialize before the singleton server starts the scheduler.
        self.logger.debug('Sleeping for {0} s'.format(self.initial_sleep_time))
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
        self.logger.info('Pickup notifier starting')
        self.pickup.watch()

    def hot_deploy(self, file_name, path):
        """ Hot deploys a file pointed to by the 'path' parameter.
        """
        self.logger.debug('About to hot-deploy [{}]'.format(path))
        now = datetime.utcnow()
        di = dumps(deployment_info('hot-deploy', file_name, now.isoformat(), path))
        
        # Insert the package into the DB ..
        package_id = self.parallel_server.odb.hot_deploy(now, di, file_name, 
            open(path, 'rb').read(), self.server_id)
        
        # .. and notify all the servers they're to pick up a delivery
        self.parallel_server.notify_new_package(package_id)
        
    def become_cluster_wide(self, connector_server_keep_alive_job_time, connector_server_grace_time, 
            server_id, cluster_id, starting_up):
        """ Attempts to become a connector server, the one to start the connector
        processes.
        """
        base_job_data = Bunch({
                'weeks': None, 'days': None, 
                'hours': None, 'minutes': None, 
                'seconds': connector_server_keep_alive_job_time, 
                'repeats': None, 
                'extra': 'server_id:{};cluster_id:{}'.format(server_id, cluster_id),
                })
        job_data = None
        
        if self.parallel_server.odb.become_cluster_wide(connector_server_grace_time):
            self.is_cluster_wide = True
            
            # Schedule a job for letting the other servers know we're still alive
            # (not that we're not using .utcnow() for start_date because the
            # scheduler - for better or worse - doesn't use UTC.
            job_data = Bunch(base_job_data.copy())
            job_data.start_date = datetime.now()
            job_data.name = 'zato.ClusterWideSingletonKeepAlive'
            job_data.service = 'zato.server.service.internal.server.ClusterWideSingletonKeepAlive'
            
        else:
            # All other singleton servers that are just starting up get this job
            # for checking whether the connector server is alive or not
            if starting_up:
                job_data = Bunch(base_job_data.copy())
                job_data.start_date = datetime.now() + timedelta(seconds=10) # Let's give the other server some time to warm up
                job_data.name = 'zato.EnsureClusterWideSingleton'
                job_data.service = 'zato.server.service.internal.server.EnsureClusterWideSingleton'

        if job_data:
            self.scheduler.create_interval_based(job_data, MESSAGE_TYPE.TO_PARALLEL_SUB)

        return self.is_cluster_wide
        
################################################################################

    def filter(self, msg):
        """ Filters out messages meant to be received by a singleton server.
        """
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

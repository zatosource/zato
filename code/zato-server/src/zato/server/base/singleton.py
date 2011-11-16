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
import json, logging
from uuid import uuid4
from traceback import format_exc

# lxml
from lxml import etree

# ZeroMQ
import zmq

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ZATO_CONFIG_REQUEST, ZATO_CONFIG_RESPONSE, ZATO_NOT_GIVEN, \
     ZATO_ERROR, ZATO_OK, ZatoException
from zato.common.util import TRACE1
from zato.server.base import BrokerMessageReceiver

class SingletonServer(BrokerMessageReceiver):
    """ A server of which one instance only may be running in a Zato container.
    Holds and processes data which can't be made parallel, such as scheduler,
    hot-deployment or on-disk configuration management.
    """
    
    def __init__(self, parallel_server=None, scheduler=None, broker_token=None, 
                 zmq_context=None, broker_host=None, broker_push_port=None, 
                 broker_pull_port=None):
        self.parallel_server = parallel_server
        self.scheduler = scheduler
        self.broker_token = broker_token
        self.broker_host = broker_host
        self.broker_push_port = broker_push_port
        self.broker_pull_port = broker_pull_port
        self.zmq_context = zmq_context

    def run(self, *ignored_args, **kwargs):
        self.logger = logging.getLogger('{0}.{1}:{2}'.format(__name__, 
                                        self.__class__.__name__, hex(id(self))))

        for name in('broker_token', 'zmq_context', 'broker_host', 'broker_push_port', 
                    'broker_pull_port'):
            if name in kwargs:
                setattr(self, name, kwargs[name])
                
        self.broker_broker_push_client_pull = 'tcp://{0}:{1}'.format(self.broker_host, self.broker_push_port)
        self.broker_client_push_broker_pull = 'tcp://{0}:{1}'.format(self.broker_host, self.broker_pull_port)
        
        # Initialize scheduler.
        self.scheduler.singleton = self
        
        self.broker_client = BrokerClient()
        self.broker_client.name = 'singleton'
        self.broker_client.token = self.broker_token
        self.broker_client.zmq_context = self.zmq_context
        self.broker_client.broker_push_client_pull = self.broker_broker_push_client_pull
        self.broker_client.client_push_broker_pull = self.broker_client_push_broker_pull
        self.broker_client.on_pull_handler = self.on_broker_msg
        self.broker_client.init()
        self.broker_client.start()
        
        '''
        # Start the pickup monitor.
        self.logger.debug("Pickup notifier starting.")
        self.pickup.watch()
        
        '''
        
################################################################################

    def on_broker_pull_msg_SCHEDULER_CREATE(self, msg, *ignored_args):
        self.scheduler.create_edit('create', msg)
        
    def on_broker_pull_msg_SCHEDULER_EDIT(self, msg, *ignored_args):
        self.scheduler.create_edit('edit', msg)
        
    def on_broker_pull_msg_SCHEDULER_DELETE(self, msg, *ignored_args):
        self.scheduler.delete(msg)
        
    def on_broker_pull_msg_SCHEDULER_EXECUTE(self, msg, *ignored_args):
        self.scheduler.execute(msg)

################################################################################

    def load_egg_services(self, egg_path):
        """ Tells each of parallel servers to load Zato services off an .egg
        distribution. The .egg is guaranteed to contain at least one service to
        load.
        """

        # XXX: That loop could be refactored out to some common place.
        for q in self.partner_request_queues.values():
            req = self._create_ipc_config_request("LOAD_EGG_SERVICES", egg_path)
            code, reason = self._send_config_request(req, q, timeout=1.0)

            if code != ZATO_OK:
                # XXX: Add the parallel server's PID/name here.
                msg = "Could not update a parallel server, server may have been left in an unstable state, reason=[%s]" % reason
                self.logger.error(msg)
                raise ZatoException(msg)

        return ZATO_OK, ""

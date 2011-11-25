#!/usr/bin/env python

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
import sys

# anyjson
from anyjson import loads

# Zato
from zato.broker import SocketData
from zato.broker.zato_broker import Broker
from zato.common import PORTS

import logging

logging.basicConfig(level=5)

if __name__ == '__main__':
    config = loads(open(sys.argv[1]).read())
    
    token = config['token']
    log_invalid_tokens = config['log_invalid_tokens']
    host = config['host']
    start_port = config['start_port']
    
    broker_push_worker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_WORKER_THREAD_PULL)
    worker_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.WORKER_THREAD_PUSH_BROKER_PULL)
    
    broker_pub_worker_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_WORKER_THREAD_SUB)
    
    broker_push_singleton_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_SINGLETON_PULL)
    singleton_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.SINGLETON_PUSH_BROKER_PULL)
    
    broker_push_connector_amqp_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_CONNECTOR_AMQP_PULL)
    connector_amqp_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.CONNECTOR_AMQP_PUSH_BROKER_PULL)
    broker_pub_connector_amqp_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_CONNECTOR_AMQP_SUB)
    
    s1 = SocketData('worker-thread/pull-push', broker_push_worker_pull, worker_push_broker_pull)
    s2 = SocketData('worker-thread/sub', None, None, broker_pub_worker_sub)
    s3 = SocketData('singleton', broker_push_singleton_pull, singleton_push_broker_pull)
    s4 = SocketData('amqp-connector/pull-push', broker_push_connector_amqp_pull, connector_amqp_push_broker_pull)
    s5 = SocketData('amqp-connector/sub', None, None, broker_pub_connector_amqp_sub)
    
    Broker(token, log_invalid_tokens, s1, s2, s3, s4, s5).serve_forever()

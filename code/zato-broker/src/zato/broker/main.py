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
    
    broker_push_publishing_connector_amqp_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_AMQP_PULL)
    publishing_connector_amqp_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.PUBLISHING_CONNECTOR_AMQP_PUSH_BROKER_PULL)
    broker_pub_publishing_connector_amqp_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_AMQP_SUB)
    
    broker_push_consuming_connector_amqp_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_AMQP_PULL)
    consuming_connector_amqp_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.CONSUMING_CONNECTOR_AMQP_PUSH_BROKER_PULL)
    broker_pub_consuming_connector_amqp_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_CONSUMING_CONNECTOR_AMQP_SUB)
    
    broker_push_publishing_connector_jms_wmq_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_JMS_WMQ_PULL)
    publishing_connector_jms_wmq_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.PUBLISHING_CONNECTOR_JMS_WMQ_PUSH_BROKER_PULL)
    broker_pub_publishing_connector_jms_wmq_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_JMS_WMQ_SUB)
    
    broker_push_consuming_connector_jms_wmq_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_JMS_WMQ_PULL)
    consuming_connector_jms_wmq_push_broker_pull = 'tcp://{0}:{1}'.format(host, start_port + PORTS.CONSUMING_CONNECTOR_JMS_WMQ_PUSH_BROKER_PULL)
    broker_pub_consuming_connector_jms_wmq_sub = 'tcp://{0}:{1}'.format(host, start_port + PORTS.BROKER_PUB_CONSUMING_CONNECTOR_JMS_WMQ_SUB)
    
    sockets = []
    
    sockets.append(SocketData('worker-thread/pull-push', broker_push_worker_pull, worker_push_broker_pull))
    sockets.append(SocketData('worker-thread/sub', None, None, broker_pub_worker_sub))
    
    sockets.append(SocketData('singleton', broker_push_singleton_pull, singleton_push_broker_pull))
    
    sockets.append(SocketData('amqp-publishing-connector/pull-push', broker_push_publishing_connector_amqp_pull, publishing_connector_amqp_push_broker_pull))
    sockets.append(SocketData('amqp-publishing-connector/sub', None, None, broker_pub_publishing_connector_amqp_sub))
    
    sockets.append(SocketData('amqp-consuming-connector/pull-push', broker_push_consuming_connector_amqp_pull, consuming_connector_amqp_push_broker_pull))
    sockets.append(SocketData('amqp-consuming-connector/sub', None, None, broker_pub_consuming_connector_amqp_sub))
    
    sockets.append(SocketData('jms-wmq-publishing-connector/pull-push', broker_push_publishing_connector_jms_wmq_pull, publishing_connector_jms_wmq_push_broker_pull))
    sockets.append(SocketData('jms-wmq-publishing-connector/sub', None, None, broker_pub_publishing_connector_jms_wmq_sub))
    
    sockets.append(SocketData('jms-wmq-consuming-connector/pull-push', broker_push_consuming_connector_jms_wmq_pull, consuming_connector_jms_wmq_push_broker_pull))
    sockets.append(SocketData('jms-wmq-consuming-connector/sub', None, None, broker_pub_consuming_connector_jms_wmq_sub))
    
    Broker(token, log_invalid_tokens, *sockets).serve_forever()

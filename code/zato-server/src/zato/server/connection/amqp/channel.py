# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# stdlib
import logging, os
from random import getrandbits
from os import getpid
from socket import getfqdn, gethostbyname, gethostname
from threading import Thread

# Bunch
from bunch import Bunch

# Zato
from zato.common import TRACE1
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE, TOPICS
from zato.common.util import new_cid
from zato.server.connection.amqp import BaseAMQPConnection, BaseAMQPConnector
from zato.server.connection import setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_AMQP_CHANNEL_ID'

logger = logging.getLogger('zato_connector')

class ConsumingConnection(BaseAMQPConnection):
    """ A connection for consuming the AMQP messages.
    """
    def __init__(self, conn_params, channel_name, queue, consumer_tag_prefix, callback):
        super(ConsumingConnection, self).__init__(conn_params, channel_name)
        self.queue = queue
        self.consumer_tag_prefix = consumer_tag_prefix
        self.callback = callback

    def _on_channel_open(self, channel):
        """ We've opened a channel to the broker.
        """
        super(ConsumingConnection, self)._on_channel_open(channel)
        self.consume()

    def _on_basic_consume(self, channel, method_frame, header_frame, body):
        """ We've got a message to handle.
        """
        self.callback(method_frame, header_frame, body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def consume(self, queue=None, consumer_tag_prefix=None):
        """ Starts consuming messages from the broker.
        """
        _queue = queue if queue else self.queue
        _consumer_tag_prefix = consumer_tag_prefix if consumer_tag_prefix else self.consumer_tag_prefix

        consumer_tag = '{0}:{1}:{2}:{3}:{4}'.format(
            _consumer_tag_prefix, gethostbyname(gethostname()), getfqdn(),
            getpid(), getrandbits(64)).ljust(72, '0')

        self.channel.basic_consume(self._on_basic_consume, queue=_queue, consumer_tag=consumer_tag)
        logger.info(u'Started an AMQP consumer for [{0}], queue [{1}], tag [{2}]'.format(
            self._conn_info(), _queue, consumer_tag))

class ConsumingConnector(BaseAMQPConnector):
    """ An AMQP consuming connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, def_id=None, channel_id=None, init=True):
        super(ConsumingConnector, self).__init__(repo_location, def_id)
        self.broker_client_id = 'amqp-consuming-connector'
        self.channel_id = channel_id

        self.broker_client_id = 'amqp-consuming-connector'
        self.broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_AMQP_CONSUMING_CONNECTOR_ALL]: self.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL]: self.on_broker_msg
        }
        self.broker_messages = self.broker_callbacks.keys()

        if init:
            self._init()
            self._setup_amqp()

    def _setup_odb(self):
        super(ConsumingConnector, self)._setup_odb()

        item = self.odb.get_channel_amqp(self.server.cluster.id, self.channel_id)
        self.channel_amqp = Bunch()
        self.channel_amqp.id = item.id
        self.channel_amqp.name = item.name
        self.channel_amqp.is_active = item.is_active
        self.channel_amqp.queue = item.queue
        self.channel_amqp.consumer_tag_prefix = item.consumer_tag_prefix
        self.channel_amqp.service = item.service_name
        self.channel_amqp.data_format = item.data_format

    def _setup_amqp(self):
        """ Sets up the AMQP listener on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                self._recreate_consumer()

    def filter(self, msg):
        """ Finds out whether the incoming message actually belongs to the
        listener. All the listeners receive incoming each of the PUB messages
        and filtering out is being performed here, on the client side, not in the broker.
        """
        if super(ConsumingConnector, self).filter(msg):
            return True

        elif msg.action in(CHANNEL.AMQP_EDIT.value, CHANNEL.AMQP_DELETE.value):
            if self.channel_amqp.id == msg.id:
                return True
        else:
            if logger.isEnabledFor(TRACE1):
                logger.log(TRACE1, 'Returning False for msg [{0}]'.format(msg))
            return False

    def _recreate_consumer(self):
        """ (Re-)creates an AMQP consumer and updates the related attributes so
        that they point to the newly created consumer. The method must be called
        from a method that holds onto all AMQP-related RLocks.
        """
        self._stop_amqp_connection()

        # An actual AMQP consumer
        if self.channel_amqp.is_active:
            consumer = self._amqp_consumer()
            self.channel_amqp.consumer = consumer

    def _amqp_consumer(self):
        consumer = ConsumingConnection(self._amqp_conn_params(), self.channel_amqp.name,
            self.channel_amqp.queue, self.channel_amqp.consumer_tag_prefix,
            self._on_message)
        t = Thread(target=consumer._run)
        t.start()

        return consumer

    def _channel_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP consumer.
        """
        with self.def_amqp_lock:
            with self.channel_amqp_lock:
                consumer = self.channel_amqp.get('consumer')
                self.channel_amqp = msg
                self.channel_amqp.consumer = consumer
                self._recreate_consumer()

    def _stop_amqp_connection(self):
        """ Stops the AMQP connection.
        """
        if self.channel_amqp.get('consumer'):
            self.channel_amqp.consumer.close()

    def _get_frame_data(self, frame):
        """ Inspired by pika.amqp_object.AMQPObject.__repr__
        """
        items = {}
        for key, value in frame.__dict__.iteritems():
            if getattr(frame.__class__, key, None) != value:
                items[key] = value

        return items

    def _on_message(self, method_frame, header_frame, body):
        """ A callback to be invoked by ConsumingConnection on each new AMQP message.
        """
        with self.def_amqp_lock:
            with self.channel_amqp_lock:
                params = {}
                params['action'] = CHANNEL.AMQP_MESSAGE_RECEIVED.value
                params['service'] = self.channel_amqp.service
                params['data_format'] = self.channel_amqp.data_format
                params['cid'] = new_cid()
                params['payload'] = body
                params['method_frame'] = self._get_frame_data(method_frame)
                params['header_frame'] = self._get_frame_data(header_frame)

                self.broker_client.invoke_async(params)

    def on_broker_msg_CHANNEL_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._channel_amqp_create_edit(msg, *args)

    def on_broker_msg_CHANNEL_AMQP_EDIT(self, msg, *args):
        """ Updates an AMQP consumer. Note that the implementation
        is the same for both CHANNEL_AMQP_CREATE and CHANNEL_AMQP_EDIT.
        """
        self._channel_amqp_create_edit(msg, *args)

    def on_broker_msg_CHANNEL_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP connection, closes all the other connections
        and stops the process.
        """
        self._close()

    def on_broker_msg_CHANNEL_AMQP_CLOSE(self, msg, *args):
        """ Stops the consumer, ODB connection and exits the process.
        """
        self._close()

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()

    repo_location = os.environ['ZATO_REPO_LOCATION']
    def_id = os.environ['ZATO_CONNECTOR_DEF_ID']
    item_id = os.environ[ENV_ITEM_NAME]

    ConsumingConnector(repo_location, def_id, item_id)

    logger.debug('Starting AMQP consuming connector, repo_location [{0}], item_id [{1}], def_id [{2}]'.format(
        repo_location, item_id, def_id))

def start_connector(repo_location, item_id, def_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, def_id, item_id)

if __name__ == '__main__':
    run_connector()

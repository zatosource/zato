# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The producers and consumers of Azure Service Bus, which an AMQP connector imports when it starts for such a namespace.

# stdlib
from logging import getLogger
from traceback import format_exc

# Azure Service Bus
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# gevent
from gevent import sleep
from gevent.lock import RLock

# Zato
from zato.common.util.api import new_cid_queue_consumer, wait_for_predicate
from zato.server.connection.amqp_ import Message_State_Ack, Message_State_Received, Message_State_Rejected, \
    Message_State_Requeued

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, callable_, stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def check_conn_str(conn_str:'str') -> 'None':
    """ Builds a client of a connection string and closes it at once, which raises if the string is invalid.
    Nothing is sent to the namespace.
    """
    client = ServiceBusClient.from_connection_string(conn_str)
    client.close()

# ################################################################################################################################
# ################################################################################################################################

class AzureServiceBusProducer:
    """ Publishes messages to Azure Service Bus queues through one outgoing connection. The queue a message goes to
    is named by the routing key of each publication, and the client along with a sender per queue are built
    on first use, the way AMQP producers connect when a message is published.
    """
    def __init__(self, config:'Bunch') -> 'None':
        self.config = config
        self.name = config.name
        self.client:'ServiceBusClient | None' = None
        self.senders:'stranydict' = {}
        self.lock = RLock()

    def _get_sender(self, queue:'str') -> 'any_':
        """ Returns the sender for a queue, building the client and the sender when they are needed for the first time.
        """
        with self.lock:

            if self.client is None:
                self.client = ServiceBusClient.from_connection_string(self.config.azure_conn_str)

            if queue not in self.senders:
                self.senders[queue] = self.client.get_queue_sender(queue)

            out = self.senders[queue]

        return out

    def publish(self, msg:'str', queue:'str') -> 'None':
        sender = self._get_sender(queue)
        service_bus_msg = ServiceBusMessage(msg)
        sender.send_messages(service_bus_msg)

    def stop(self) -> 'None':
        with self.lock:
            for sender in self.senders.values():
                sender.close()
            self.senders.clear()

            if self.client is not None:
                self.client.close()
                self.client = None

# ################################################################################################################################
# ################################################################################################################################

class _AzureMessageWrapper:
    """ An Azure Service Bus message under the same ack, reject and requeue interface, and with the same
    delivery state names, as a kombu message, so that a channel's acknowledgment mode applies to both alike.
    """

    def __init__(self, msg:'any_', receiver:'any_') -> 'None':
        self._msg = msg
        self._receiver = receiver
        self._state = Message_State_Received

# ################################################################################################################################

    def ack(self) -> 'None':
        self._receiver.complete_message(self._msg)
        self._state = Message_State_Ack

# ################################################################################################################################

    def reject(self) -> 'None':
        self._receiver.abandon_message(self._msg)
        self._state = Message_State_Rejected

# ################################################################################################################################

    def requeue(self) -> 'None':
        self._receiver.abandon_message(self._msg)
        self._state = Message_State_Requeued

# ################################################################################################################################
# ################################################################################################################################

class AzureServiceBusConsumer:
    def __init__(self, config:'Bunch', on_amqp_message:'callable_') -> 'None':
        self.cid = new_cid_queue_consumer()
        self.config = config
        self.name = config.name
        self.on_amqp_message = on_amqp_message
        self._keep_running = True
        self.is_stopped = True
        self.is_connected = False
        self.start_called = False
        self.client = None
        self.receiver = None

    @property
    def keep_running(self) -> 'bool':
        return self._keep_running

    @keep_running.setter
    def keep_running(self, value:'bool') -> 'None':
        self._keep_running = value

    def start(self) -> 'None':
        self.start_called = True
        self.is_stopped = False

        try:
            self.client = ServiceBusClient.from_connection_string(self.config.azure_conn_str)
            self.receiver = self.client.get_queue_receiver(self.config.queue, max_wait_time=5)
            self.is_connected = True

            while self.keep_running:
                try:
                    for msg in self.receiver:
                        if not self.keep_running:
                            break
                        try:
                            body = str(msg)
                            wrapped_msg = _AzureMessageWrapper(msg, self.receiver)
                            self.on_amqp_message(body, wrapped_msg, self.name, self.config)
                        except Exception:
                            logger.warning(f'[{self.cid}] {format_exc()}')
                except Exception:
                    if self.keep_running:
                        logger.warning(f'[{self.cid}] Azure consumer error: {format_exc()}')
                        sleep(2)

        except Exception:
            logger.warning(f'[{self.cid}] Azure consumer startup error: {format_exc()}')
        finally:
            self.is_stopped = True

    def stop(self) -> 'None':
        self.keep_running = False
        if self.receiver:
            self.receiver.close()
        if self.client:
            self.client.close()
        self.is_stopped = True

    def wait_until_connected(self, timeout:'int'=1) -> 'bool':
        return wait_for_predicate(
            self._is_connected,
            timeout=timeout,
            interval=0.01,
            log_msg_details=f'Azure consumer `{self.name}` to connect',
            needs_log=True,
        )

    def _is_connected(self) -> 'bool':
        return self.is_connected

# ################################################################################################################################
# ################################################################################################################################

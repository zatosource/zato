# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an AMQP connector reaches for when it is exercised offline - producers that remember
# what they were told to publish, an Azure receiver that remembers how each message was settled,
# and the connector built around them.

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.api import AMQP
from zato.common.ext.bunch import Bunch
from zato.server.connection.amqp_ import ConnectorAMQP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

# The names the objects under test go by
Connector_Name = 'test.amqp.connector'
Outconn_Name   = 'test.amqp.outgoing'
Channel_Name   = 'test.amqp.channel'
Service_Name   = 'test.amqp.process-order'

# ################################################################################################################################
# ################################################################################################################################

class KombuProducerRecorder:
    """ Stands in for a kombu producer - it remembers each message it was told to publish.
    """

    def __init__(self) -> 'None':
        self.published:'anylist' = []

    def publish(self, msg:'any_', headers:'any_'=None, **kwargs:'any_') -> 'None':
        self.published.append(msg)

# ################################################################################################################################

class KombuProducerPoolStub:
    """ Stands in for a kombu producer pool - acquiring it hands over the recorder.
    """

    def __init__(self) -> 'None':
        self.producer = KombuProducerRecorder()

    @contextmanager
    def acquire(self, block:'bool', timeout:'any_') -> 'any_':
        yield self.producer

# ################################################################################################################################

class AzureProducerRecorder:
    """ Stands in for an Azure Service Bus sender - it remembers each message it was told to publish.
    """

    def __init__(self) -> 'None':
        self.published:'anylist' = []

    def publish(self, msg:'any_', **kwargs:'any_') -> 'None':
        self.published.append(msg)

# ################################################################################################################################

class AzureReceiverRecorder:
    """ Stands in for an Azure Service Bus receiver - it remembers how each message was settled.
    """

    def __init__(self) -> 'None':
        self.completed:'anylist' = []
        self.abandoned:'anylist' = []

    def complete_message(self, msg:'any_') -> 'None':
        self.completed.append(msg)

    def abandon_message(self, msg:'any_') -> 'None':
        self.abandoned.append(msg)

# ################################################################################################################################
# ################################################################################################################################

def new_outconn_config(*, is_azure:'bool') -> 'Bunch':
    """ The configuration of one outgoing connection, with none of the optional AMQP properties set.
    """
    out = Bunch()
    out.name = Outconn_Name
    out.is_active = True
    out.is_azure = is_azure

    out.app_id = ''
    out.content_encoding = ''
    out.content_type = ''
    out.delivery_mode = ''
    out.expiration = ''
    out.priority = ''
    out.user_id = ''

    return out

# ################################################################################################################################

def new_channel_config(ack_mode:'str'=AMQP.ACK_MODE.ACK.id) -> 'Bunch':
    """ The configuration of one channel, under the given acknowledgment mode.
    """
    out = Bunch()
    out.id = 1
    out.name = Channel_Name
    out.service_name = Service_Name
    out.data_format = 'json'
    out.ack_mode = ack_mode

    return out

# ################################################################################################################################

def new_connector(on_message_callback:'callable_', producer:'any_', *, is_azure:'bool') -> 'ConnectorAMQP':
    """ Builds the connector under test around one stubbed producer, with one outgoing connection named after it.
    """
    config = Bunch()
    config.id = 1
    config.name = Outconn_Name
    config.is_active = True

    outconn_config = new_outconn_config(is_azure=is_azure)
    outconns = {Outconn_Name: outconn_config}

    out = ConnectorAMQP(Connector_Name, 'amqp', config, on_message_callback, outconns=outconns)
    out._producers = {Outconn_Name: producer}

    return out

# ################################################################################################################################
# ################################################################################################################################

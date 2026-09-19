# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the broker backends add to the enmasse configuration of a server.

# PyYAML
from yaml import safe_dump, safe_load

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.outgoing import get_outgoing_topic_name, OutgoingType
from zato.common.test.rabbitmq_ import declare_and_bind

# local
from _helpers import Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.rabbitmq_ import RabbitMQProcess
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The connection whose switch is off has no topic in the broker
_conn_without_queue = 'plain'

Outgoing_AMQP_Name = 'test.queue-delivery.broker'
Exchange_Name = 'zato.out.rest'

# Enmasse runs before the server does, so the channel's service must be one quickstart put in the database
Channel_Service = 'demo.ping'

Broker_Username = 'guest'
Broker_Password = 'guest'

# One consumer with one message in flight keeps the order of a queue
Channel_Pool_Size = 1
Channel_Prefetch_Count = 1

# ################################################################################################################################
# ################################################################################################################################

def get_broker_address(broker:'RabbitMQProcess') -> 'str':
    """ The broker's address without credentials.
    """
    if broker.needs_ssl:
        scheme = 'amqps'
    else:
        scheme = 'amqp'

    out = f'{scheme}://127.0.0.1:{broker.amqp_port}//'
    return out

# ################################################################################################################################

def get_channel_name(topic_name:'str') -> 'str':
    """ The AMQP channel that consumes one topic's queue is named after the topic.
    """
    out = 'channel.' + topic_name
    return out

# ################################################################################################################################

def get_queued_topic_names() -> 'strlist':
    """ The topics of every connection with the queue switch on.
    """
    out = []

    for key, conn_name in Connections.items():

        if key == _conn_without_queue:
            continue

        topic_name = get_outgoing_topic_name(OutgoingType.REST, conn_name)
        out.append(topic_name)

    return out

# ################################################################################################################################

def declare_broker_queues(broker:'RabbitMQProcess') -> 'None':
    """ Declares the exchange and, for each topic, a queue bound to it under the topic's own name as the routing key.
    """
    for topic_name in get_queued_topic_names():
        declare_and_bind(broker.amqp_url, Exchange_Name, topic_name, topic_name)

# ################################################################################################################################

def build_amqp_config(broker:'RabbitMQProcess') -> 'stranydict':
    """ The enmasse definitions that make every connection's topic an AMQP-backed one.
    """
    address = get_broker_address(broker)

    outgoing_amqp = [{
        'name': Outgoing_AMQP_Name,
        'address': address,
        'username': Broker_Username,
        'password': Broker_Password,
    }]

    channel_amqp = []
    pubsub_topic = []

    for topic_name in get_queued_topic_names():

        channel_name = get_channel_name(topic_name)

        channel_amqp.append({
            'name': channel_name,
            'address': address,
            'username': Broker_Username,
            'password': Broker_Password,
            'queue': topic_name,
            'service': Channel_Service,
            'pool_size': Channel_Pool_Size,
            'prefetch_count': Channel_Prefetch_Count,
        })

        pubsub_topic.append({
            'name': topic_name,
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': Outgoing_AMQP_Name,
            'amqp_exchange': Exchange_Name,
            'amqp_routing_key': topic_name,
            'amqp_channel_name': channel_name,
        })

    out = {
        'outgoing_amqp': outgoing_amqp,
        'channel_amqp': channel_amqp,
        'pubsub_topic': pubsub_topic,
    }

    return out

# ################################################################################################################################

def add_amqp_config(rendered_yaml:'str', broker:'RabbitMQProcess') -> 'str':
    """ The rendered enmasse configuration with the broker's definitions added to it.
    """
    config = safe_load(rendered_yaml)

    for section, items in build_amqp_config(broker).items():

        if section in config:
            config[section].extend(items)
        else:
            config[section] = items

    out = safe_dump(config, sort_keys=False)
    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an outgoing AMQP connection publishes when a service hands it its own input -
# the dict of the request's fields for a broker, and the same dict as JSON text for Azure Service Bus.

# stdlib
from json import loads

# Zato
from zato.input_output import ServiceInput

# Test support
from amqp_stub import new_connector, AzureProducerRecorder, KombuProducerPoolStub

# ################################################################################################################################
# ################################################################################################################################

_order_fields = {'customer_id': 'C-1001', 'quantity': 3}

# ################################################################################################################################
# ################################################################################################################################

def _no_message_callback(*args:'object', **kwargs:'object') -> 'None':
    pass

# ################################################################################################################################
# ################################################################################################################################

def test_a_service_input_is_published_to_a_broker_as_a_dict() -> 'None':
    pool = KombuProducerPoolStub()
    connector = new_connector(_no_message_callback, pool, is_azure=False)

    _ = connector.invoke(ServiceInput(_order_fields))

    assert pool.producer.published == [_order_fields]

# ################################################################################################################################

def test_text_is_published_to_a_broker_as_it_is() -> 'None':
    pool = KombuProducerPoolStub()
    connector = new_connector(_no_message_callback, pool, is_azure=False)

    _ = connector.invoke('Order ORD-001 completed')

    assert pool.producer.published == ['Order ORD-001 completed']

# ################################################################################################################################

def test_a_service_input_is_published_to_azure_as_json_text() -> 'None':
    producer = AzureProducerRecorder()
    connector = new_connector(_no_message_callback, producer, is_azure=True)

    _ = connector.invoke(ServiceInput(_order_fields))

    published = producer.published[0]

    assert isinstance(published, str)
    assert loads(published) == _order_fields

# ################################################################################################################################

def test_a_dict_is_published_to_azure_as_json_text() -> 'None':
    producer = AzureProducerRecorder()
    connector = new_connector(_no_message_callback, producer, is_azure=True)

    _ = connector.invoke(_order_fields)

    published = producer.published[0]

    assert isinstance(published, str)
    assert loads(published) == _order_fields

# ################################################################################################################################

def test_text_is_published_to_azure_as_it_is() -> 'None':
    producer = AzureProducerRecorder()
    connector = new_connector(_no_message_callback, producer, is_azure=True)

    _ = connector.invoke('Order ORD-001 completed')

    assert producer.published == ['Order ORD-001 completed']

# ################################################################################################################################
# ################################################################################################################################

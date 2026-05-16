# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock

# Zato
from zato.common.marshal_.api import Model
from zato.common.pubsub.redis_backend import RedisPubSubBackend
from zato.server.base.parallel.delivery import RedisPushDelivery

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CustomerRequest(Model):
    customer_id: str = ''
    name: str = ''

# ################################################################################################################################
# ################################################################################################################################

class TestServicePublishRoundTrip(unittest.TestCase):

    def _publish_and_deliver(self, data:'object') -> 'object':
        """ Publishes data through RedisPubSubBackend with a mock Redis client,
        captures the xadd message, then feeds it into _deliver_to_service
        with a mock server.invoke to return what the subscriber receives.
        """

        # Set up the backend with a mock Redis that captures xadd calls ..
        mock_redis = MagicMock()
        mock_redis.xadd.return_value = b'1234567890-0'

        backend = RedisPubSubBackend(mock_redis)

        # .. publish the data ..
        _ = backend.publish('test.topic', data, publisher='test.publisher')

        # .. extract the message dict that was passed to xadd ..
        xadd_call_args = mock_redis.xadd.call_args
        captured_message = xadd_call_args[0][1]

        # .. now set up the delivery side with a mock server ..
        mock_server = MagicMock()
        delivery = RedisPushDelivery.__new__(RedisPushDelivery)
        delivery.server = mock_server

        sub_config = {'push_service_name': 'subscriber.service'}

        # .. deliver the captured message to the subscriber service ..
        delivery._deliver_to_service(captured_message, sub_config)

        # .. return what the subscriber received as its payload.
        invoke_call_args = mock_server.invoke.call_args[0]
        received_payload = invoke_call_args[1]

        return received_payload

# ################################################################################################################################

    def test_string_round_trip(self) -> 'None':
        """ A plain string payload survives the publish-deliver round-trip unchanged.
        """
        received = self._publish_and_deliver('hello')

        self.assertEqual(received, 'hello')

# ################################################################################################################################

    def test_dict_round_trip(self) -> 'None':
        """ A dict payload is serialized to JSON and deserialized back to a dict.
        """
        payload = {'order_id': 123, 'status': 'pending'}

        received = self._publish_and_deliver(payload)

        self.assertEqual(received, payload)

# ################################################################################################################################

    def test_int_round_trip(self) -> 'None':
        """ An integer payload round-trips through JSON correctly.
        """
        received = self._publish_and_deliver(42)

        self.assertEqual(received, 42)

# ################################################################################################################################

    def test_list_round_trip(self) -> 'None':
        """ A list payload round-trips through JSON correctly.
        """
        payload = [1, 2, 3]

        received = self._publish_and_deliver(payload)

        self.assertEqual(received, payload)

# ################################################################################################################################

    def test_model_round_trip(self) -> 'None':
        """ A Model instance is serialized with its class name and
        reconstructed on the subscriber side as the same Model class.
        """
        request = CustomerRequest()
        request.customer_id = 'CUST-001'
        request.name = 'Test Customer'

        received = self._publish_and_deliver(request)

        self.assertIsInstance(received, CustomerRequest)

        received_model:'CustomerRequest' = received # type: ignore[assignment]
        self.assertEqual(received_model.customer_id, 'CUST-001')
        self.assertEqual(received_model.name, 'Test Customer')

# ################################################################################################################################

    def test_inline_kwargs_round_trip(self) -> 'None':
        """ When inline kwargs are used as payload via Service.publish,
        the resulting dict round-trips through publish-deliver correctly.
        """

        # Service.publish would build this dict from the kwargs
        # before passing it to the backend ..
        payload = {'order_id': 123, 'status': 'pending'}

        received = self._publish_and_deliver(payload)

        self.assertEqual(received, {'order_id': 123, 'status': 'pending'})

# ################################################################################################################################

    def test_inline_kwargs_with_metadata(self) -> 'None':
        """ When metadata kwargs (like priority) are passed alongside
        payload kwargs, only the payload keys reach the subscriber.
        This tests the Service.publish layer that separates them.
        """
        from zato.server.service import Service

        # Build a minimally wired Service instance ..
        service = Service.__new__(Service)

        # .. mock pubsub.publish to capture what it receives ..
        service.pubsub = MagicMock()

        # .. call publish with a mix of payload and metadata kwargs ..
        _ = service.publish('test.topic', order_id=123, priority=5)

        # .. verify pubsub.publish received the payload dict
        # .. with only the non-meta keys ..
        call_args = service.pubsub.publish.call_args
        received_data = call_args[0][1]

        self.assertEqual(received_data, {'order_id': 123})

        # .. and priority was passed as a kwarg to pubsub.publish,
        # .. not included in the payload.
        received_kwargs = call_args[1]
        self.assertEqual(received_kwargs['priority'], 5)

# ################################################################################################################################

    def test_model_data_class_stored_in_message(self) -> 'None':
        """ When a Model is published, the Redis message contains a
        data_class field with the fully-qualified class name.
        """
        mock_redis = MagicMock()
        mock_redis.xadd.return_value = b'1234567890-0'

        backend = RedisPubSubBackend(mock_redis)

        request = CustomerRequest()
        request.customer_id = 'CUST-001'
        request.name = 'Test Customer'

        _ = backend.publish('test.topic', request, publisher='test.publisher')

        xadd_call_args = mock_redis.xadd.call_args
        captured_message = xadd_call_args[0][1]

        expected_class = f'{CustomerRequest.__module__}.{CustomerRequest.__qualname__}'
        self.assertEqual(captured_message['data_class'], expected_class)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################

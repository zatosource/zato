# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
import unittest

# Zato
from zato.common.test.client import AdminClient as ZatoClient

# local
from zato.common.test.config_pubsub_service import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_delivery_poll_timeout  = 5
_delivery_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriberInput(unittest.TestCase):
    """ What a subscribing service finds in self.request.input and self.request.raw
    for each kind of message a publisher sends to it.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = ZatoClient(TestConfig.base_url, TestConfig.password)

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.client.invoke('test.pubsub.clear-input-received')

# ################################################################################################################################

    def _get_received(self) -> 'anydict':
        raw = self.client.invoke('test.pubsub.get-input-received')
        out = json.loads(raw) if isinstance(raw, str) else raw
        return out

# ################################################################################################################################

    def _publish_and_wait(self, kind:'str', data:'object') -> 'anydict':
        """ Publishes one message of the given kind and returns what the receiver stored for it.
        """
        _ = self.client.invoke('test.pubsub.publish-event', {'kind': kind, 'data': data})

        deadline = time.monotonic() + _delivery_poll_timeout

        while time.monotonic() < deadline:
            received = self._get_received()
            if received['count'] >= 1:
                break
            time.sleep(_delivery_poll_interval)
        else:
            received = self._get_received()

        self.assertEqual(received['count'], 1, 'The receiver should have received exactly one message')

        out = received['received'][0]
        return out

# ################################################################################################################################

    def test_dict_event_is_parsed_into_input(self) -> 'None':
        """ A dict published to a service is the subscriber's input, with the stored JSON text in raw.
        """
        event = {'order_id': 'ORD-001', 'status': 'completed'}

        received = self._publish_and_wait('dict', event)

        self.assertEqual(received['input_type'], 'ServiceInput')
        self.assertEqual(received['input'], event)
        self.assertEqual(received['raw_type'], 'str')
        self.assertEqual(json.loads(received['raw']), event)

# ################################################################################################################################

    def test_text_event_is_input_as_it_is(self) -> 'None':
        """ Text published to a service reaches the subscriber's input unchanged, and raw holds the same text.
        """
        text = 'Order ORD-001 completed'

        received = self._publish_and_wait('text', text)

        self.assertEqual(received['input_type'], 'str')
        self.assertEqual(received['input'], text)
        self.assertEqual(received['raw'], text)

# ################################################################################################################################

    def test_model_event_is_input_as_an_instance(self) -> 'None':
        """ A Model published to a service is rebuilt and the instance is the subscriber's input.
        """
        event = {'order_id': 'ORD-001', 'status': 'completed', 'amount': 99.95}

        received = self._publish_and_wait('model', event)

        self.assertEqual(received['input_type'], 'OrderEvent')
        self.assertEqual(received['input'], event)
        self.assertEqual(received['raw_type'], 'OrderEvent')

# ################################################################################################################################
# ################################################################################################################################

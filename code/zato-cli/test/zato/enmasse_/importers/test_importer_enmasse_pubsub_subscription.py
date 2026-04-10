# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubSubscriptionImport(TestCase):

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name or item.get('security') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_pubsub_subscription_count(self) -> 'None':
        sub_list = self.exported['pubsub_subscription']
        self.assertEqual(len(sub_list), 3)

# ################################################################################################################################

    def test_subscription_basic_auth_1(self) -> 'None':
        item = self._find(self.exported['pubsub_subscription'], 'enmasse.basic_auth.1')
        self.assertEqual(item['delivery_type'], 'pull')
        self.assertEqual(item['max_retry_time'], '365d')
        self.assertEqual(sorted(item['topic_list']), ['enmasse.topic.1', 'enmasse.topic.2'])

# ################################################################################################################################

    def test_subscription_basic_auth_2(self) -> 'None':
        item = self._find(self.exported['pubsub_subscription'], 'enmasse.basic_auth.2')
        self.assertEqual(item['delivery_type'], 'push')
        self.assertEqual(item['push_rest_endpoint'], 'enmasse.outgoing.rest.1')
        self.assertEqual(item['max_retry_time'], '48h')
        self.assertEqual(item['topic_list'], ['enmasse.topic.1'])

# ################################################################################################################################

    def test_subscription_basic_auth_3(self) -> 'None':
        item = self._find(self.exported['pubsub_subscription'], 'enmasse.basic_auth.3')
        self.assertEqual(item['delivery_type'], 'push')
        self.assertIsNone(item.get('push_service_name'))
        self.assertEqual(item['max_retry_time'], '30m')
        self.assertEqual(item['topic_list'], ['enmasse.topic.3'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

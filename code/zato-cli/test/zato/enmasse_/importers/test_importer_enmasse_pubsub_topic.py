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

class TestEnmassePubSubTopicImport(TestCase):

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_pubsub_topic_count(self) -> 'None':
        topic_list = self.exported['pubsub_topic']
        self.assertEqual(len(topic_list), 3)

# ################################################################################################################################

    def test_topic_1(self) -> 'None':
        item = self._find(self.exported['pubsub_topic'], 'enmasse.topic.1')
        self.assertEqual(item['description'], 'Optional description for topic 1')

# ################################################################################################################################

    def test_topic_2(self) -> 'None':
        item = self._find(self.exported['pubsub_topic'], 'enmasse.topic.2')
        self.assertEqual(item['name'], 'enmasse.topic.2')

# ################################################################################################################################

    def test_topic_3(self) -> 'None':
        item = self._find(self.exported['pubsub_topic'], 'enmasse.topic.3')
        self.assertEqual(item['name'], 'enmasse.topic.3')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

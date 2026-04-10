# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubPermissionExporter(TestCase):
    """ Tests exporting pub/sub permission definitions via ConfigStore round-trip.
    """

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

    def test_pubsub_permission_count(self) -> 'None':
        perm_list = self.exported['pubsub_permission']
        self.assertEqual(len(perm_list), 3)

# ################################################################################################################################

    def test_pubsub_permission_basic_auth_1(self) -> 'None':
        item = self._find(self.exported['pubsub_permission'], 'enmasse.basic_auth.1')
        self.assertEqual(item['security'], 'enmasse.basic_auth.1')
        self.assertEqual(set(item['pub']), {'enmasse.topic.1', 'enmasse.topic.2'})
        self.assertEqual(set(item['sub']), {'enmasse.topic.2', 'enmasse.topic.3'})

# ################################################################################################################################

    def test_pubsub_permission_basic_auth_2(self) -> 'None':
        item = self._find(self.exported['pubsub_permission'], 'enmasse.basic_auth.2')
        self.assertEqual(item['security'], 'enmasse.basic_auth.2')
        self.assertEqual(item['pub'], ['enmasse.topic.*'])
        self.assertEqual(item['sub'], ['enmasse.#'])

# ################################################################################################################################

    def test_pubsub_permission_basic_auth_3(self) -> 'None':
        item = self._find(self.exported['pubsub_permission'], 'enmasse.basic_auth.3')
        self.assertEqual(item['security'], 'enmasse.basic_auth.3')
        self.assertEqual(item['pub'], [])
        self.assertEqual(item['sub'], ['enmasse.topic.3'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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

class TestEnmasseGroupExporter(TestCase):
    """ Tests exporting group definitions via ConfigStore round-trip.
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

    def test_groups_count(self) -> 'None':
        groups_list = self.exported['groups']
        self.assertEqual(len(groups_list), 2)

# ################################################################################################################################

    def test_group_1(self) -> 'None':
        item = self._find(self.exported['groups'], 'enmasse.group.1')
        self.assertEqual(item['name'], 'enmasse.group.1')
        self.assertEqual(sorted(item['members']), ['enmasse.apikey.1', 'enmasse.basic_auth.1', 'enmasse.basic_auth.2'])

# ################################################################################################################################

    def test_group_2(self) -> 'None':
        item = self._find(self.exported['groups'], 'enmasse.group.2')
        self.assertEqual(item['name'], 'enmasse.group.2')
        self.assertEqual(sorted(item['members']), ['enmasse.apikey.1', 'enmasse.apikey.2', 'enmasse.basic_auth.1'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

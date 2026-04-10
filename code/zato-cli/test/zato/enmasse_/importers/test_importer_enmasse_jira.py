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

class TestEnmasseJiraImport(TestCase):

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

    def test_jira_count(self) -> 'None':
        ldap_list = self.exported['ldap']
        jira_items = [item for item in ldap_list if item.get('type_') == 'cloud-jira']
        self.assertEqual(len(jira_items), 1)

# ################################################################################################################################

    def test_jira_1(self) -> 'None':
        ldap_list = self.exported['ldap']
        jira_items = [item for item in ldap_list if item.get('type_') == 'cloud-jira']
        item = self._find(jira_items, 'enmasse.jira.1')
        self.assertEqual(item['type_'], 'cloud-jira')
        self.assertEqual(item['address'], 'https://example.atlassian.net')
        self.assertEqual(item['username'], 'enmasse@example.com')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

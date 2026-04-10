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

class TestEnmasseMicrosoft365Exporter(TestCase):
    """ Tests exporting Microsoft 365 definitions via ConfigStore round-trip.
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

    def test_microsoft_365_in_ldap(self) -> 'None':
        ldap_list = self.exported['ldap']
        ms365_items = [item for item in ldap_list if item.get('type_') == 'cloud-microsoft-365']
        self.assertEqual(len(ms365_items), 1)

# ################################################################################################################################

    def test_microsoft_365_1(self) -> 'None':
        ldap_list = self.exported['ldap']
        ms365_items = [item for item in ldap_list if item.get('type_') == 'cloud-microsoft-365']
        item = ms365_items[0]
        self.assertEqual(item['name'], 'enmasse.cloud.microsoft365.1')
        self.assertEqual(item['type_'], 'cloud-microsoft-365')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

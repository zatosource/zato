# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMicrosoft365Import(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_microsoft_365_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('microsoft_365', exported)

        m365_list = exported['microsoft_365']
        m365_by_name = {item['name']: item for item in m365_list}
        self.assertIn('enmasse.cloud.microsoft365.1', m365_by_name)

# ################################################################################################################################

    def test_microsoft_365_values(self):

        exported = self.config_manager.export_to_dict()
        m365_list = exported['microsoft_365']
        m365_by_name = {item['name']: item for item in m365_list}

        m1 = m365_by_name['enmasse.cloud.microsoft365.1']
        self.assertEqual(m1['client_id'], '12345678-1234-1234-1234-123456789abc')
        self.assertEqual(m1['tenant_id'], '87654321-4321-4321-4321-cba987654321')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

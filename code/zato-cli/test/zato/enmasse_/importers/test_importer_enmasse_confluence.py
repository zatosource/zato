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

class TestEnmasseConfluenceImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_confluence_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('confluence', exported)

        conn_list = exported['confluence']
        conn_by_name = {item['name']: item for item in conn_list}
        self.assertIn('enmasse.confluence.1', conn_by_name)

# ################################################################################################################################

    def test_confluence_values(self):

        exported = self.config_manager.export_to_dict()
        conn_list = exported['confluence']
        conn_by_name = {item['name']: item for item in conn_list}

        c1 = conn_by_name['enmasse.confluence.1']
        self.assertEqual(c1['address'], 'https://example.atlassian.net')
        self.assertEqual(c1['username'], 'api_user@example.com')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

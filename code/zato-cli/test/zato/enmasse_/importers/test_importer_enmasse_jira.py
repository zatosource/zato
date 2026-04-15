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
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseJiraImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_jira_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('jira', exported)

        jira_list = exported['jira']
        jira_by_name = {item['name']: item for item in jira_list}
        self.assertIn('enmasse.jira.1', jira_by_name)

# ################################################################################################################################

    def test_jira_values(self):

        exported = self.config_store.export_to_dict()
        jira_list = exported['jira']
        jira_by_name = {item['name']: item for item in jira_list}

        j1 = jira_by_name['enmasse.jira.1']
        self.assertEqual(j1['address'], 'https://example.atlassian.net')
        self.assertEqual(j1['username'], 'enmasse@example.com')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

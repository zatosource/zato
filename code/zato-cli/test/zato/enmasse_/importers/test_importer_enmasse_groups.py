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

class TestEnmasseGroupImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_groups_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('groups', exported)

        group_list = exported['groups']
        group_by_name = {item['name']: item for item in group_list}

        self.assertIn('enmasse.group.1', group_by_name)
        self.assertIn('enmasse.group.2', group_by_name)

# ################################################################################################################################

    def test_group_members(self):

        exported = self.config_store.export_to_dict()
        group_list = exported['groups']
        group_by_name = {item['name']: item for item in group_list}

        g1 = group_by_name['enmasse.group.1']
        self.assertIn('members', g1)
        members = g1['members']
        self.assertIn('enmasse.basic_auth.1', members)
        self.assertIn('enmasse.basic_auth.2', members)
        self.assertIn('enmasse.apikey.1', members)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

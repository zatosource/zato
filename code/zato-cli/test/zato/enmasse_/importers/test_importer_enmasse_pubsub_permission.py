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

class TestEnmassePubSubPermissionImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_pubsub_permission_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('pubsub_permission', exported)

        perm_list = exported['pubsub_permission']
        self.assertEqual(len(perm_list), 3)

# ################################################################################################################################

    def test_pubsub_permission_values(self):

        exported = self.config_store.export_to_dict()
        perm_list = exported['pubsub_permission']

        perm_by_security = {item['security']: item for item in perm_list}

        p1 = perm_by_security['enmasse.basic_auth.1']
        self.assertIn('enmasse.topic.1', p1.get('pub', []))
        self.assertIn('enmasse.topic.2', p1.get('pub', []))
        self.assertIn('enmasse.topic.2', p1.get('sub', []))
        self.assertIn('enmasse.topic.3', p1.get('sub', []))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

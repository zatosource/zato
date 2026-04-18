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

class TestEnmassePubSubSubscriptionImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_pubsub_subscription_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('pubsub_subscription', exported)

        sub_list = exported['pubsub_subscription']
        self.assertEqual(len(sub_list), 3)

# ################################################################################################################################

    def test_pubsub_subscription_values(self):

        exported = self.config_store.export_to_dict()
        sub_list = exported['pubsub_subscription']

        sub_by_security = {item['security']: item for item in sub_list}

        s1 = sub_by_security['enmasse.basic_auth.1']
        self.assertEqual(s1['delivery_type'], 'pull')

        s2 = sub_by_security['enmasse.basic_auth.2']
        self.assertEqual(s2['delivery_type'], 'push')
        self.assertEqual(s2['push_rest_endpoint'], 'enmasse.outgoing.rest.1')

        s3 = sub_by_security['enmasse.basic_auth.3']
        self.assertEqual(s3['delivery_type'], 'push')
        self.assertEqual(s3['push_service'], 'demo.input-logger')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

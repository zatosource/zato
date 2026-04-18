# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurityImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_security_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        security_items = template_dict['security']

        preprocessed = SecurityImporter.preprocess(security_items)

        for item in preprocessed:
            self.assertIn('password', item)
            self.assertTrue(item['password'])

            if item['type'] == 'bearer_token':
                self.assertIn('client_id_field', item)
                self.assertIn('client_secret_field', item)
                self.assertIn('grant_type', item)
                self.assertIn('data_format', item)

            if item['type'] == 'apikey':
                self.assertIn('username', item)

# ################################################################################################################################

    def test_security_auth_endpoint_rename(self):

        template_dict = yaml.safe_load(template_complex_01)
        security_items = template_dict['security']

        preprocessed = SecurityImporter.preprocess(security_items)

        for item in preprocessed:
            self.assertNotIn('auth_endpoint', item)
            if item['name'] == 'enmasse.bearer_token.1':
                self.assertEqual(item['auth_server_url'], 'https://example.com')

# ################################################################################################################################

    def test_security_imported_to_config_store(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('security', exported)

        security_list = exported['security']
        security_by_name = {item['name']: item for item in security_list}

        self.assertIn('enmasse.basic_auth.1', security_by_name)
        self.assertIn('enmasse.bearer_token.1', security_by_name)
        self.assertIn('enmasse.ntlm.1', security_by_name)
        self.assertIn('enmasse.apikey.1', security_by_name)

# ################################################################################################################################

    def test_security_types_preserved(self):

        exported = self.config_store.export_to_dict()
        security_list = exported['security']
        security_by_name = {item['name']: item for item in security_list}

        self.assertEqual(security_by_name['enmasse.basic_auth.1']['type'], 'basic_auth')
        self.assertEqual(security_by_name['enmasse.bearer_token.1']['type'], 'bearer_token')
        self.assertEqual(security_by_name['enmasse.ntlm.1']['type'], 'ntlm')
        self.assertEqual(security_by_name['enmasse.apikey.1']['type'], 'apikey')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

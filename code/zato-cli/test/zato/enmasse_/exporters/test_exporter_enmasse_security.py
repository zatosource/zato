# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurityExporter(TestCase):
    """ Tests exporting security definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

# ################################################################################################################################

    def test_security_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('security', exported_data, 'Exporter did not produce a "security" section.')
        all_exported_security_list = exported_data['security']

        # Filter exported security definitions to only include those with names starting with "enmasse"
        exported_security_list = [item for item in all_exported_security_list if item['name'].startswith('enmasse')]

        import yaml
        template_dict = yaml.safe_load(template_complex_01)
        security_list_from_yaml = template_dict.get('security', [])

        self.assertEqual(len(exported_security_list), len(security_list_from_yaml),
            'Number of exported security definitions does not match original YAML.')

        yaml_security_by_name = {item['name']: item for item in security_list_from_yaml}
        exported_security_by_name = {item['name']: item for item in exported_security_list}

        for name, yaml_def in yaml_security_by_name.items():
            self.assertIn(name, exported_security_by_name, f'Security definition "{name}" from YAML not found in export.')
            exported_def = exported_security_by_name[name]

            self.assertEqual(exported_def.get('type'), yaml_def.get('type'), f'Security type mismatch for "{name}"')
            self.assertEqual(exported_def.get('name'), yaml_def.get('name'), f'Security name mismatch for "{name}"')

            if 'username' in yaml_def and yaml_def.get('type') != 'apikey':
                self.assertEqual(exported_def.get('username'), yaml_def.get('username'),
                    f'Username mismatch for security definition "{name}"')

            if yaml_def.get('type') == 'bearer_token':
                for field in ['auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format']:
                    if field in yaml_def:
                        self.assertEqual(exported_def.get(field), yaml_def.get(field),
                            f'Field {field} mismatch for security definition "{name}"')

                if 'extra_fields' in yaml_def:
                    self.assertEqual(exported_def.get('extra_fields'), yaml_def.get('extra_fields'),
                        f'Extra fields mismatch for security definition "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseEmailIMAPExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.config_store.load_yaml_string(template_complex_01)

    def test_email_imap_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('email_imap', exported_data, 'Exporter did not produce an "email_imap" section.')
        exported_list = exported_data['email_imap']

        template_dict = yaml.safe_load(template_complex_01)
        yaml_list = template_dict.get('email_imap', [])

        exported_by_name = {item['name']: item for item in exported_list}

        for yaml_def in yaml_list:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name, f'IMAP "{name}" not found in export')
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def['name'], yaml_def['name'])
            if 'username' in yaml_def:
                self.assertEqual(exported_def.get('username'), yaml_def['username'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingRESTExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

    def test_outgoing_rest_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('outgoing_rest', exported_data, 'Exporter did not produce an "outgoing_rest" section.')
        exported_list = exported_data['outgoing_rest']

        template_dict = yaml.safe_load(template_complex_01)
        yaml_list = template_dict.get('outgoing_rest', [])

        exported_by_name = {item['name']: item for item in exported_list}

        for yaml_def in yaml_list:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name, f'Outgoing REST "{name}" not found in export')
            exported_def = exported_by_name[name]

            self.assertEqual(exported_def['name'], yaml_def['name'])
            self.assertEqual(exported_def['host'], yaml_def['host'])
            self.assertEqual(exported_def['url_path'], yaml_def['url_path'])

            if 'security' in yaml_def:
                self.assertEqual(exported_def.get('security'), yaml_def['security'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

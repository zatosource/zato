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

class TestEnmasseGroupExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

    def test_group_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('groups', exported_data, 'Exporter did not produce a "groups" section.')
        exported_groups = exported_data['groups']

        template_dict = yaml.safe_load(template_complex_01)
        groups_from_yaml = template_dict.get('groups', [])

        self.assertEqual(len(exported_groups), len(groups_from_yaml))

        exported_by_name = {g['name']: g for g in exported_groups}

        for yaml_group in groups_from_yaml:
            name = yaml_group['name']
            self.assertIn(name, exported_by_name, f'Group "{name}" not found in export')
            exported_group = exported_by_name[name]
            self.assertEqual(sorted(exported_group.get('members', [])), sorted(yaml_group.get('members', [])),
                f'Members mismatch for group "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

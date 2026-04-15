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
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerExporter(TestCase):
    """ Tests exporting scheduler job definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.config_store.load_yaml_string(template_complex_01)

# ################################################################################################################################

    def test_scheduler_export(self):

        import yaml
        template_dict = yaml.safe_load(template_complex_01)
        scheduler_list_from_yaml = template_dict.get('scheduler', [])

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('scheduler', exported_data, 'Exporter did not produce a "scheduler" section.')
        exported_scheduler_list = exported_data['scheduler']

        yaml_scheduler_by_name = {item['name']: item for item in scheduler_list_from_yaml}
        exported_scheduler_by_name = {item['name']: item for item in exported_scheduler_list}

        for name in yaml_scheduler_by_name:
            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')

        for name, yaml_def in yaml_scheduler_by_name.items():

            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')
            exported_def = exported_scheduler_by_name[name]

            for field in ['name', 'is_active', 'job_type', 'service']:
                if field in yaml_def:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field),
                        f'Mismatch for "{field}" in scheduler job "{name}"')

            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']:
                if attr in yaml_def and yaml_def[attr] is not None:
                    self.assertEqual(exported_def.get(attr), yaml_def.get(attr),
                        f'Mismatch for interval attribute "{attr}" in scheduler job "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

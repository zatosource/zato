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

class TestEnmasseCacheExporter(TestCase):
    """ Tests exporting caches to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.config_store.load_yaml_string(template_complex_01)

# ################################################################################################################################

    def test_cache_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('cache', exported_data, 'Exporter did not produce a "cache" section.')
        exported_cache_list = exported_data['cache']

        # The template has 1 cache definition (enmasse.cache.builtin.1)
        self.assertEqual(len(exported_cache_list), 1)

        # Create dictionaries keyed by name for easier comparison
        import yaml
        template_dict = yaml.safe_load(template_complex_01)
        yaml_caches_by_name = {item['name']: item for item in template_dict.get('cache', [])}
        exported_caches_by_name = {item['name']: item for item in exported_cache_list}

        for name, yaml_def in yaml_caches_by_name.items():

            self.assertIn(name, exported_caches_by_name, f'Cache "{name}" from YAML not found in export.')
            exported_def = exported_caches_by_name[name]

            exported_name = exported_def.get('name')
            yaml_name = yaml_def.get('name')
            self.assertEqual(exported_name, yaml_name, f'Mismatch for "name" in cache "{name}"')

            exported_extend_on_get = exported_def.get('extend_expiry_on_get')
            yaml_extend_on_get = yaml_def.get('extend_expiry_on_get')
            self.assertEqual(exported_extend_on_get, yaml_extend_on_get, f'Mismatch for "extend_expiry_on_get" in cache "{name}"')

            exported_extend_on_set = exported_def.get('extend_expiry_on_set')
            yaml_extend_on_set = yaml_def.get('extend_expiry_on_set')
            self.assertEqual(exported_extend_on_set, yaml_extend_on_set, f'Mismatch for "extend_expiry_on_set" in cache "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

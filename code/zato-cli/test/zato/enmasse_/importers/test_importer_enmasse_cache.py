# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCacheImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_cache_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        cache_items = template_dict['cache']

        preprocessed = CacheImporter.preprocess(cache_items)

        for item in preprocessed:
            self.assertEqual(item.get('sync_method'), 'in-background')
            self.assertEqual(item.get('persistent_storage'), 'sqlite')
            self.assertEqual(item.get('max_item_size'), 1000000)
            self.assertEqual(item.get('max_size'), 10000)

# ################################################################################################################################

    def test_cache_imported_to_config_store(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('cache', exported)

        cache_list = exported['cache']
        cache_by_name = {item['name']: item for item in cache_list}
        self.assertIn('enmasse.cache.builtin.1', cache_by_name)

# ################################################################################################################################

    def test_cache_values_preserved(self):

        exported = self.config_store.export_to_dict()
        cache_list = exported['cache']
        cache_by_name = {item['name']: item for item in cache_list}

        cache1 = cache_by_name['enmasse.cache.builtin.1']
        self.assertTrue(cache1['extend_expiry_on_get'])
        self.assertFalse(cache1['extend_expiry_on_set'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

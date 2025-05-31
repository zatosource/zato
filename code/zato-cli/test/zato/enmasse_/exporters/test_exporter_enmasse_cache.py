# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCacheExporter(TestCase):
    """ Tests exporting caches to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.cache_importer = CacheImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_cache_export(self):
        self._setup_test_environment()

        # 1. Get cache definitions from the YAML template
        cache_list_from_yaml = self.yaml_config.get('cache', [])

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_caches, _ = self.cache_importer.sync_cache_definitions(cache_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_caches) > 0, 'No caches were created from YAML, cannot test export meaningfully.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('cache', exported_data, 'Exporter did not produce a "cache" section.')
        exported_cache_list = exported_data['cache']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_cache_list), len(cache_list_from_yaml), 'Number of exported caches does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_caches_by_name = {item['name']: item for item in cache_list_from_yaml}
        exported_caches_by_name = {item['name']: item for item in exported_cache_list}

        for name, yaml_def in yaml_caches_by_name.items():

            self.assertIn(name, exported_caches_by_name, f'Cache "{name}" from YAML not found in export.')
            exported_def = exported_caches_by_name[name]

            # Compare only the fields that are expected to be exported by CacheExporter
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

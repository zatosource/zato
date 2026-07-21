# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.quota_tier import QuotaTierImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseQuotaTierExporter(TestCase):
    """ Tests exporting quota tier definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.quota_tier_importer = QuotaTierImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import quota tier definitions
        tiers_from_yaml = self.yaml_config.get('quota_tier', [])
        if tiers_from_yaml:
            _, _ = self.quota_tier_importer.sync_quota_tiers(tiers_from_yaml, self.session)

        self.session.commit()

# ################################################################################################################################

    def test_quota_tier_export(self) -> 'None':
        """ Tests the export of quota tier definitions.
        """
        self._setup_test_environment()

        # Initialize the exporter
        yaml_exporter = EnmasseYAMLExporter()

        # Export the data
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Get the quota tier section
        exported_tiers = exported_data.get('quota_tier', [])

        # Take into account only our own tiers
        exported_tiers = [tier for tier in exported_tiers if tier['name'].startswith('enmasse.')]

        # Get the expected tiers from the imported YAML
        expected_tiers_from_yaml = self.yaml_config.get('quota_tier', [])

        # Assert that the number of exported tiers matches the expected number
        self.assertEqual(len(exported_tiers), len(expected_tiers_from_yaml), \
            f'Expected {len(expected_tiers_from_yaml)} tiers, but got {len(exported_tiers)}')

        # Convert exported tiers to a dictionary keyed by name for easier lookup
        exported_tiers_dict = {item['name']: item for item in exported_tiers}

        # Verify each expected tier
        for expected_tier in expected_tiers_from_yaml:
            expected_name = expected_tier['name']
            self.assertIn(expected_name, exported_tiers_dict, f'Exported tiers missing tier: {expected_name}')

            exported_tier_data = exported_tiers_dict[expected_name]
            self.assertEqual(exported_tier_data['name'], expected_name)
            self.assertEqual(exported_tier_data['description'], expected_tier['description'])
            self.assertEqual(exported_tier_data['rules'], expected_tier['rules'])

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

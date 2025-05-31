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
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, SASession

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGroupExporter(TestCase):
    """ Tests exporting Security Group definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer) # Handles all security definition types
        self.group_importer = GroupImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import security definitions first, as groups depend on them
        security_defs_from_yaml = self.yaml_config.get('security', [])
        if security_defs_from_yaml:
            # SecurityImporter handles all types of security definitions
            _, _ = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)

        # Import group definitions
        groups_from_yaml = self.yaml_config.get('groups', [])
        if groups_from_yaml:
            _, _ = self.group_importer.sync_groups(groups_from_yaml, self.session)

        self.session.commit()

# ################################################################################################################################

    def test_group_export(self) -> 'None':
        """ Tests the export of group definitions.
        """
        self._setup_test_environment()

        # Initialize the exporter
        yaml_exporter = EnmasseYAMLExporter()

        # Export the data
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Get the groups section
        exported_groups = exported_data.get('groups', [])

        # Get the expected groups from the imported YAML
        expected_groups_from_yaml = self.yaml_config.get('groups', [])

        # Assert that the number of exported groups matches the expected number
        self.assertEqual(len(exported_groups), len(expected_groups_from_yaml), \
            f'Expected {len(expected_groups_from_yaml)} groups, but got {len(exported_groups)}')

        # Convert exported groups to a dictionary keyed by name for easier lookup
        exported_groups_dict = {item['name']: item for item in exported_groups}

        # Verify each expected group
        for expected_group in expected_groups_from_yaml:
            expected_name = expected_group['name']
            self.assertIn(expected_name, exported_groups_dict, f'Exported groups missing group: {expected_name}')

            exported_group_data = exported_groups_dict[expected_name]
            self.assertEqual(exported_group_data['name'], expected_name)

            # Compare members as sets to ignore order
            expected_members = set(expected_group.get('members', []))
            exported_members = set(exported_group_data.get('members', []))
            self.assertSetEqual(exported_members, expected_members, \
                f'Member mismatch for group {expected_name}. Expected: {expected_members}, Got: {exported_members}')

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()


# ################################################################################################################################
# ################################################################################################################################

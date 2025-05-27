# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase, main
import uuid

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.typing_ import cast_, any_, stranydict

# Test data
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGroups(TestCase):
    """ Tests for importing security groups from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.group_importer = GroupImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

    def test_groups_yaml_parsing(self):
        """ Test that the groups section in YAML is parsed correctly.
        """
        self._setup_test_environment()

        self.assertIn('groups', self.yaml_config)
        self.assertIsInstance(self.yaml_config['groups'], list)

        # Verify structure of first group
        group = self.yaml_config['groups'][0]
        self.assertIn('name', group)
        self.assertIn('members', group)
        self.assertIsInstance(group['members'], list)

    def test_sync_groups(self):
        """ Test the new sync_groups implementation that deletes and recreates groups.
        """
        self._setup_test_environment()

        # Process security definitions from YAML first
        self.importer.sync_from_yaml(self.yaml_config, self.session)

        # Create a unique group name for this test to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]
        group_defs = [self.yaml_config['groups'][0].copy()]
        group_defs[0]['name'] = f'test_sync_group_{unique_suffix}'

        # First sync - should create the group
        processed_groups, _ = self.group_importer.sync_groups(group_defs, self.session)

        # Verify group was created
        self.assertEqual(len(processed_groups), 1)
        group_name = group_defs[0]['name']
        self.assertEqual(processed_groups[0]['name'], group_name)

        # Verify it's in the database
        db_groups = self.group_importer.get_groups_from_db(self.session)
        self.assertTrue(group_name in db_groups)

        # Second sync - should delete and recreate the group
        # This tests our new implementation
        processed_groups_2, _ = self.group_importer.sync_groups(group_defs, self.session)

        # Verify group was processed and recreated successfully
        self.assertEqual(len(processed_groups_2), 1)
        self.assertEqual(processed_groups_2[0]['name'], group_name)
        self.assertEqual(len(processed_groups_2[0]['members']), len(group_defs[0]['members']))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    # stdlib
    import logging

    # Configure logging for tests
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run tests
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

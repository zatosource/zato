# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGroups(TestCase):
    """ Tests for importing security groups from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
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

    def test_get_groups_from_db(self):
        """ Test retrieving groups from the database.
        """
        self._setup_test_environment()

        # Process security definitions first (needed for member resolution)
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        self.importer.sec_defs = self.security_importer.sec_defs

        # Get just the first group for testing
        group_defs = [self.yaml_config['groups'][0]]

        # First, create a group to retrieve
        created_groups, _ = self.group_importer.sync_groups(group_defs, self.session)
        self.assertEqual(len(created_groups), 1)

        # Now test get_groups_from_db
        db_groups = self.group_importer.get_groups_from_db(self.session)

        # Verify the group exists in the result
        group_name = group_defs[0]['name']
        self.assertIn(group_name, db_groups)

        # Verify the group has the correct structure
        db_group = db_groups[group_name]
        self.assertIn('id', db_group)
        self.assertIn('name', db_group)
        self.assertIn('members', db_group)

    def test_group_creation(self):
        """ Test creating security groups.
        """
        self._setup_test_environment()

        # First process security definitions (groups need them)
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        self.importer.sec_defs = self.security_importer.sec_defs

        # Get just the first group for testing
        group_defs = [self.yaml_config['groups'][0]]

        # Process the group
        created_groups, _ = self.group_importer.sync_groups(group_defs, self.session)

        # Verify group was created
        self.assertEqual(len(created_groups), 1)
        self.assertEqual(created_groups[0]['name'], group_defs[0]['name'])

        # Verify it's in the database
        db_groups = self.group_importer.get_groups_from_db(self.session)
        self.assertIn(group_defs[0]['name'], db_groups)

    def test_member_resolution(self):
        """ Test that member names are correctly resolved to security definition IDs.
        """
        self._setup_test_environment()

        # Create security definitions first
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        self.importer.sec_defs = self.security_importer.sec_defs

        # Get sample members from the YAML
        group = self.yaml_config['groups'][0]
        member_names = group['members'][:2]  # Just use the first two members

        # Test member resolution method directly
        member_ids = self.group_importer._resolve_member_names(member_names)

        # Verify we got the correct number of member IDs
        self.assertEqual(len(member_ids), len(member_names))

        # Check that IDs are in the expected format (should contain a dash)
        for member_id in member_ids:
            self.assertIn('-', member_id)

    def test_group_update(self):
        """ Test updating an existing group's members.
        """
        self._setup_test_environment()

        # Create dependencies first
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        self.importer.sec_defs = self.security_importer.sec_defs

        # Get a sample group
        original_group = self.yaml_config['groups'][0].copy()
        original_members = original_group.get('members', [])[:]  # Make a copy

        # Create the group with original members
        created_groups, _ = self.group_importer.sync_groups([original_group], self.session)
        group_id = created_groups[0]['id']

        # Modify the members list - use the first member only
        modified_group = original_group.copy()
        modified_group['members'] = original_members[:1]
        modified_group['id'] = group_id

        # Update the group
        _, updated_groups = self.group_importer.sync_groups([modified_group], self.session)

        # Verify update was successful
        self.assertEqual(len(updated_groups), 1)

        # Verify the members were updated in the database
        db_groups = self.group_importer.get_groups_from_db(self.session)
        updated_db_members = db_groups[modified_group['name']]['members']
        self.assertEqual(len(updated_db_members), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

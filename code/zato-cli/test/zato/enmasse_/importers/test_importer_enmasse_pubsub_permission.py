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
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.common.api import PubSub
from zato.common.odb.model import PubSubPermission
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubPermissionFromYAML(TestCase):
    """ Tests importing pubsub permission definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains permission definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.pubsub_topic_importer = PubSubTopicImporter(self.importer)
        self.pubsub_permission_importer = PubSubPermissionImporter(self.importer)

        # Parse the YAML file
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def _create_dependencies(self):
        """ Create security definitions and topics that permissions depend on.
        """
        # Create security definitions first
        security_defs = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_defs, self.session)
        self.importer.sec_defs = self.security_importer.sec_defs

        # Create pubsub topics
        topic_defs = self.yaml_config['pubsub_topic']
        _ = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_defs, self.session)
        self.importer.pubsub_topic_defs = self.pubsub_topic_importer.pubsub_topic_defs

# ################################################################################################################################

    def test_pubsub_permission_definition_creation(self):
        """ Test creating pubsub permission definitions from YAML.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        permission_defs = self.yaml_config['pubsub_permission']

        # Process all pubsub permission definitions
        created, updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Should have created permissions for all pub/sub patterns
        # enmasse.basic_auth.1: 2 pub + 2 sub = 4 permissions
        # enmasse.basic_auth.2: 1 pub + 1 sub = 2 permissions
        # enmasse.basic_auth.3: 0 pub + 1 sub = 1 permission
        # Total: 7 permissions
        self.assertEqual(len(created), 7)
        self.assertEqual(len(updated), 0)

        # Verify specific permissions were created correctly
        # Check enmasse.basic_auth.1 publisher permissions
        pub_perms = self.session.query(PubSubPermission).filter_by(
            access_type=PubSub.API_Client.Publisher
        ).all()

        pub_patterns = [perm.pattern for perm in pub_perms]
        self.assertIn('enmasse.topic.1', pub_patterns)
        self.assertIn('enmasse.topic.2', pub_patterns)
        self.assertIn('enmasse.topic.*', pub_patterns)

        # Check subscriber permissions
        sub_perms = self.session.query(PubSubPermission).filter_by(
            access_type=PubSub.API_Client.Subscriber
        ).all()

        sub_patterns = [perm.pattern for perm in sub_perms]
        self.assertIn('enmasse.topic.2', sub_patterns)
        self.assertIn('enmasse.topic.3', sub_patterns)
        self.assertIn('enmasse.#', sub_patterns)

# ################################################################################################################################

    def test_pubsub_permission_update(self):
        """ Test updating existing pubsub permission definitions.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # First, create the permissions
        permission_defs = self.yaml_config['pubsub_permission']
        created, _ = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)
        self.assertEqual(len(created), 7)

        # Run sync again - should result in updates, not new creations
        created2, updated2 = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 7)

        # Verify all permissions still exist
        all_perms = self.session.query(PubSubPermission).all()
        self.assertEqual(len(all_perms), 7)

# ################################################################################################################################

    def test_pubsub_permission_security_mapping(self):
        """ Test that permissions are correctly mapped to security definitions.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        permission_defs = self.yaml_config['pubsub_permission']

        # Process all pubsub permission definitions
        created, _ = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Verify security mappings
        for perm in created:
            self.assertIsNotNone(perm.sec_base_id)
            self.assertIsNotNone(perm.sec_base)
            self.assertIn(perm.sec_base.name, ['enmasse.basic_auth.1', 'enmasse.basic_auth.2', 'enmasse.basic_auth.3'])

        # Check specific security definition mappings
        basic_auth_1_perms = [perm for perm in created if perm.sec_base.name == 'enmasse.basic_auth.1']
        self.assertEqual(len(basic_auth_1_perms), 4)  # 2 pub + 2 sub

        basic_auth_2_perms = [perm for perm in created if perm.sec_base.name == 'enmasse.basic_auth.2']
        self.assertEqual(len(basic_auth_2_perms), 2)  # 1 pub + 1 sub

        basic_auth_3_perms = [perm for perm in created if perm.sec_base.name == 'enmasse.basic_auth.3']
        self.assertEqual(len(basic_auth_3_perms), 1)  # 0 pub + 1 sub

# ################################################################################################################################

    def test_pubsub_permission_patterns(self):
        """ Test that permission patterns are correctly stored.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        permission_defs = self.yaml_config['pubsub_permission']

        # Process all pubsub permission definitions
        created, _ = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Collect all patterns
        patterns = [perm.pattern for perm in created]

        # Verify expected patterns exist
        expected_patterns = [
            'enmasse.topic.1',  # basic_auth.1 pub
            'enmasse.topic.2',  # basic_auth.1 pub and sub
            'enmasse.topic.3',  # basic_auth.1 sub and basic_auth.3 sub
            'enmasse.topic.*',  # basic_auth.2 pub
            'enmasse.#'         # basic_auth.2 sub
        ]

        for expected_pattern in expected_patterns:
            self.assertIn(expected_pattern, patterns)

        # Verify wildcard patterns
        wildcard_patterns = [perm for perm in created if '*' in perm.pattern or '#' in perm.pattern]
        self.assertEqual(len(wildcard_patterns), 2)

# ################################################################################################################################

    def test_complete_pubsub_permission_import_flow(self):
        """ Test the complete flow of importing pubsub permission definitions from a YAML file.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Process all pubsub permission definitions from the YAML
        permission_list = self.yaml_config['pubsub_permission']
        permission_created, permission_updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_list, self.session)

        # Update importer's pubsub permission definitions
        self.importer.pubsub_permission_defs = self.pubsub_permission_importer.pubsub_permission_defs

        # Verify pubsub permission definitions were created
        self.assertEqual(len(permission_created), 7)
        self.assertEqual(len(permission_updated), 0)

        # Verify the pubsub permission definitions dictionary was populated
        self.assertEqual(len(self.pubsub_permission_importer.pubsub_permission_defs), 7)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.pubsub_permission_defs), 7)

        # Verify all permissions are active by default
        for perm in permission_created:
            self.assertTrue(perm.is_active)

        # Verify cluster_id is set correctly
        for perm in permission_created:
            self.assertEqual(perm.cluster_id, self.importer.cluster_id)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

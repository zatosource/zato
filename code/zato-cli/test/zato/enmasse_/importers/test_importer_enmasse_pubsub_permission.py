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
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.common.api import PubSub
from zato.common.odb.model import HTTPBasicAuth, PubSubPermission, SecurityBase
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

        # Initialize PubSubPermission importer
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
            
        # Set cluster_id on importer if not already set
        if not hasattr(self.importer, 'cluster_id') or not self.importer.cluster_id:
            self.importer.cluster_id = 1

# ################################################################################################################################

    def test_pubsub_permission_definition_creation(self):
        """ Test creating pubsub permission definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        permission_defs = self.yaml_config['pubsub_permission']

        # Create security bases from template
        sec_bases = []
        for permission_def in permission_defs:
            sec_base = HTTPBasicAuth(
                name=permission_def['security'],
                is_active=True,
                realm='test'
            )
            sec_base.cluster_id = 1  # Use explicit cluster_id
            self.session.add(sec_base)
            sec_bases.append(sec_base)
        self.session.commit()

        # Process all pubsub permission definitions
        created, updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Should have created 6 permissions (2+2+2+1+1)
        self.assertEqual(len(created), 6)
        self.assertEqual(len(updated), 0)

        # Verify permissions were created correctly
        all_permissions = self.session.query(PubSubPermission).filter_by(cluster_id=1).all()
        self.assertEqual(len(all_permissions), 6)

        # Verify specific permissions
        pub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Publisher]
        sub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Subscriber]

        self.assertEqual(len(pub_permissions), 3)
        self.assertEqual(len(sub_permissions), 3)

# ################################################################################################################################

    def test_pubsub_permission_update(self):
        """ Test updating existing pubsub permission definitions.
        """
        self._setup_test_environment()

        # First, get the pubsub permission definition from YAML and create it
        permission_defs = self.yaml_config['pubsub_permission']
        permission_def = permission_defs[0]

        # Create security base from template
        sec_base = HTTPBasicAuth(
            name=permission_def['security'],
            is_active=True,
            realm='test'
        )
        sec_base.cluster_id = 1  # Use explicit cluster_id
        self.session.add(sec_base)
        self.session.commit()

        # Create the pubsub permission definition using a unique pattern for this test
        test_pattern = 'test.update.pattern'
        definition = {
            'sec_base_id': sec_base.id,
            'pattern': test_pattern,
            'access_type': PubSub.API_Client.Publisher,
            'is_active': True,
            'cluster_id': 1
        }
        instance = self.pubsub_permission_importer.create_pubsub_permission_definition(definition, self.session)
        self.session.commit()
        self.assertTrue(instance.is_active)

        # Now update the permission to be inactive
        definition['id'] = instance.id
        definition['is_active'] = False
        updated_instance = self.pubsub_permission_importer.update_pubsub_permission_definition(definition, self.session)
        self.session.commit()

        # Verify the permission was updated
        self.assertEqual(updated_instance.id, instance.id)
        self.assertFalse(updated_instance.is_active)

# ################################################################################################################################

    def test_full_import_sync(self):
        """ Test full import sync of pubsub permission definitions.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        permission_defs = self.yaml_config['pubsub_permission']

        # Create security bases from template
        sec_bases = []
        for permission_def in permission_defs:
            sec_base = HTTPBasicAuth(
                name=permission_def['security'],
                is_active=True,
                realm='test'
            )
            sec_base.cluster_id = 1  # Use explicit cluster_id
            self.session.add(sec_base)
            sec_bases.append(sec_base)
        self.session.commit()

        # Process all pubsub permission definitions
        created, updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Should have created 6 permissions (2+2+2+1+1)
        self.assertEqual(len(created), 6)
        self.assertEqual(len(updated), 0)

        # Verify permissions were created correctly
        all_permissions = self.session.query(PubSubPermission).filter_by(cluster_id=1).all()
        self.assertEqual(len(all_permissions), 6)

        # Verify specific permissions
        pub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Publisher]
        sub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Subscriber]

        self.assertEqual(len(pub_permissions), 3)
        self.assertEqual(len(sub_permissions), 3)

        # Verify patterns match template data
        pub_patterns = {p.pattern for p in pub_permissions}
        sub_patterns = {p.pattern for p in sub_permissions}

        # Extract expected patterns from YAML
        expected_pub_patterns = set()
        expected_sub_patterns = set()
        for perm_def in permission_defs:
            expected_pub_patterns.update(perm_def.get('pub', []))
            expected_sub_patterns.update(perm_def.get('sub', []))

        self.assertEqual(pub_patterns, expected_pub_patterns)
        self.assertEqual(sub_patterns, expected_sub_patterns)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################

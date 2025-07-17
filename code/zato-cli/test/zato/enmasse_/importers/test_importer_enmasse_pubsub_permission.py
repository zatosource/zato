# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import main

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.common.api import PubSub
from zato.common.odb.model import PubSubPermission, SecurityBase
from zato.common.test import BaseSSOTestCase
from zato.common.test.enmasse_ import _template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class PubSubPermissionImporterTestCase(BaseSSOTestCase):

    def setUp(self):
        super().setUp()

        # Create a temporary YAML file with the complex template
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file.write(_template_complex_01)
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()
        self.importer.cluster_id = self.cluster_id
        self.importer.session = self.session

        # Initialize the pubsub permission importer
        self.pubsub_permission_importer = PubSubPermissionImporter(self.importer)

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        super().tearDown()

# ################################################################################################################################

    def test_create_pubsub_permission_definition(self):

        # Load and parse the YAML configuration
        yaml_config = self.importer.load_yaml_config(self.temp_file.name)

        # Get permission definitions from YAML
        permission_defs = yaml_config['pubsub_permission']
        first_permission = permission_defs[0]

        # Create security base from template
        sec_base = SecurityBase()
        sec_base.name = first_permission['security']
        sec_base.sec_type = 'basic_auth'
        sec_base.cluster_id = self.cluster_id
        sec_base.is_active = True
        self.session.add(sec_base)
        self.session.commit()

        # Create pubsub permission definition using first pub pattern from template
        first_pub_pattern = first_permission['pub'][0]
        definition = {
            'sec_base_id': sec_base.id,
            'pattern': first_pub_pattern,
            'access_type': PubSub.API_Client.Publisher,
            'is_active': True
        }

        # Create the permission
        permission = self.pubsub_permission_importer.create_pubsub_permission_definition(definition, self.session)

        # Verify the permission was created
        self.assertIsNotNone(permission.id)
        self.assertEqual(permission.sec_base_id, sec_base.id)
        self.assertEqual(permission.pattern, first_pub_pattern)
        self.assertEqual(permission.access_type, PubSub.API_Client.Publisher)
        self.assertTrue(permission.is_active)
        self.assertEqual(permission.cluster_id, self.cluster_id)

# ################################################################################################################################

    def test_update_pubsub_permission_definition(self):

        # Load and parse the YAML configuration
        yaml_config = self.importer.load_yaml_config(self.temp_file.name)

        # Get permission definitions from YAML
        permission_defs = yaml_config['pubsub_permission']
        second_permission = permission_defs[1]

        # Create security base from template
        sec_base = SecurityBase()
        sec_base.name = second_permission['security']
        sec_base.sec_type = 'basic_auth'
        sec_base.cluster_id = self.cluster_id
        sec_base.is_active = True
        self.session.add(sec_base)
        self.session.commit()

        # Create initial pubsub permission using template data
        first_pub_pattern = second_permission['pub'][0]
        permission = PubSubPermission()
        permission.cluster_id = self.cluster_id
        permission.sec_base_id = sec_base.id
        permission.pattern = first_pub_pattern
        permission.access_type = PubSub.API_Client.Publisher
        permission.is_active = True
        self.session.add(permission)
        self.session.commit()

        # Update definition
        definition = {
            'id': permission.id,
            'sec_base_id': sec_base.id,
            'pattern': first_pub_pattern,
            'access_type': PubSub.API_Client.Publisher,
            'is_active': False
        }

        # Update the permission
        updated_permission = self.pubsub_permission_importer.update_pubsub_permission_definition(definition, self.session)

        # Verify the permission was updated
        self.assertEqual(updated_permission.id, permission.id)
        self.assertEqual(updated_permission.pattern, first_pub_pattern)
        self.assertEqual(updated_permission.access_type, PubSub.API_Client.Publisher)
        self.assertFalse(updated_permission.is_active)

# ################################################################################################################################

    def test_sync_pubsub_permission_definitions_full_import(self):

        # Load and parse the YAML configuration
        yaml_config = self.importer.load_yaml_config(self.temp_file.name)

        # Get permission definitions from YAML
        permission_defs = yaml_config['pubsub_permission']

        # Create security bases from template
        sec_bases = []
        for permission_def in permission_defs:
            sec_base = SecurityBase()
            sec_base.name = permission_def['security']
            sec_base.sec_type = 'basic_auth'
            sec_base.cluster_id = self.cluster_id
            sec_base.is_active = True
            self.session.add(sec_base)
            sec_bases.append(sec_base)
        self.session.commit()

        # Sync permissions
        created, updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_defs, self.session)

        # Verify results
        self.assertEqual(len(created), 6)  # 2+2+2+1+1 = 6 total permissions
        self.assertEqual(len(updated), 0)

        # Verify permissions in database
        all_permissions = self.session.query(PubSubPermission).filter_by(cluster_id=self.cluster_id).all()
        self.assertEqual(len(all_permissions), 6)

        # Verify specific permissions
        pub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Publisher]
        sub_permissions = [p for p in all_permissions if p.access_type == PubSub.API_Client.Subscriber]

        self.assertEqual(len(pub_permissions), 3)  # 2 + 1 + 0
        self.assertEqual(len(sub_permissions), 3)  # 2 + 1 + 1

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

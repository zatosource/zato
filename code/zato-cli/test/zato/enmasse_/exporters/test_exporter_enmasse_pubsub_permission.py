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
import yaml

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.pubsub_permission import PubSubPermissionExporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import stranydict
    SASession = SASession
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubPermissionExporter(TestCase):
    """ Tests exporting pub/sub permission definitions.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer)
        self.pubsub_topic_importer = PubSubTopicImporter(self.importer)
        self.pubsub_permission_importer = PubSubPermissionImporter(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.pubsub_permission_exporter = PubSubPermissionExporter(self.exporter)

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

        # Import security definitions first, as pubsub permissions depend on them
        security_defs_from_yaml = self.yaml_config['security']
        if security_defs_from_yaml:

            # This method already populates self.importer.sec_defs after commit
            created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
            logger.info('Imported %d security definitions (created=%d, updated=%d)',
                len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

            # Verify that security definitions were populated correctly
            logger.info('Security definitions in importer: %s', list(self.importer.sec_defs.keys()))

        _ = self.session.commit()

        # Import pubsub topics as permissions may reference them
        pubsub_topic_defs_from_yaml = self.yaml_config.get('pubsub_topic', [])
        if pubsub_topic_defs_from_yaml:

            # Import the topics into the database
            created, updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(pubsub_topic_defs_from_yaml, self.session)
            logger.info('Imported %d pubsub topic definitions (created=%d, updated=%d)',
                len(created) + len(updated), len(created), len(updated))

        _ = self.session.commit()

# ################################################################################################################################

    def test_pubsub_permission_export(self) -> 'None':
        """ Tests the export of pub/sub permission definitions.
        """
        self._setup_test_environment()

        # Get permission definitions from YAML
        pubsub_permission_defs_from_yaml = self.yaml_config.get('pubsub_permission', [])
        if pubsub_permission_defs_from_yaml:

            # Import the permissions into the database
            created, updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(pubsub_permission_defs_from_yaml, self.session)
            logger.info('Imported %d pubsub permission definitions (created=%d, updated=%d)',
                len(created) + len(updated), len(created), len(updated))

            _ = self.session.commit()

            # Now test the export functionality
            exported_permissions = self.pubsub_permission_exporter.export(self.session, self.exporter.cluster_id)
            logger.info('Exported %d pubsub permission definitions', len(exported_permissions))

            # Verify that we exported the expected number of permission groups
            # From the template, we expect 3 security definitions with permissions
            expected_security_count = 3
            self.assertEqual(len(exported_permissions), expected_security_count,
                f'Expected {expected_security_count} exported permission groups, got {len(exported_permissions)}')

            # Extract expected permission data directly from the YAML template
            # Parse the template to get the expected values
            template_dict = yaml.safe_load(template_complex_01)

            # Build expected permissions dictionary from the template
            expected_permissions = {}
            for perm_def in template_dict['pubsub_permission']:
                security_name = perm_def['security']
                expected_permissions[security_name] = {
                    'security': security_name,
                }

                # Add pub permissions if present
                if 'pub' in perm_def:
                    expected_permissions[security_name]['pub'] = perm_def['pub']

                # Add sub permissions if present
                if 'sub' in perm_def:
                    expected_permissions[security_name]['sub'] = perm_def['sub']

            # Verify each exported permission group against expected values
            for perm_group in exported_permissions:
                security_name = perm_group['security']
                self.assertIn(security_name, expected_permissions, f'Unexpected security {security_name} in export')
                expected = expected_permissions[security_name]

                # Check security field
                self.assertIn('security', perm_group, f'Required field security missing in permission group {security_name}')
                self.assertEqual(perm_group['security'], expected['security'],
                    f'Field security has incorrect value in permission group {security_name}, expected {expected["security"]}, got {perm_group["security"]}')

                # Check pub permissions if expected
                if 'pub' in expected:
                    self.assertIn('pub', perm_group, f'Expected pub permissions missing in permission group {security_name}')
                    self.assertEqual(set(perm_group['pub']), set(expected['pub']),
                        f'Pub permissions mismatch in permission group {security_name}, expected {expected["pub"]}, got {perm_group["pub"]}')

                # Check sub permissions if expected
                if 'sub' in expected:
                    self.assertIn('sub', perm_group, f'Expected sub permissions missing in permission group {security_name}')
                    self.assertEqual(set(perm_group['sub']), set(expected['sub']),
                        f'Sub permissions mismatch in permission group {security_name}, expected {expected["sub"]}, got {perm_group["sub"]}')

                # Verify no unexpected fields
                allowed_fields = {'security', 'pub', 'sub'}
                for field in perm_group:
                    self.assertIn(field, allowed_fields, f'Unexpected field {field} in permission group {security_name}')

            # Verify specific expected patterns from the template
            exported_by_security = {perm['security']: perm for perm in exported_permissions}

            # Check enmasse.basic_auth.1 permissions
            if 'enmasse.basic_auth.1' in exported_by_security:
                auth1_perms = exported_by_security['enmasse.basic_auth.1']
                self.assertIn('pub', auth1_perms)
                self.assertIn('sub', auth1_perms)
                self.assertEqual(set(auth1_perms['pub']), {'enmasse.topic.1', 'enmasse.topic.2'})
                self.assertEqual(set(auth1_perms['sub']), {'enmasse.topic.2', 'enmasse.topic.3'})

            # Check enmasse.basic_auth.2 permissions
            if 'enmasse.basic_auth.2' in exported_by_security:
                auth2_perms = exported_by_security['enmasse.basic_auth.2']
                self.assertIn('pub', auth2_perms)
                self.assertIn('sub', auth2_perms)
                self.assertEqual(auth2_perms['pub'], ['enmasse.topic.*'])
                self.assertEqual(auth2_perms['sub'], ['enmasse.#'])

            # Check enmasse.basic_auth.3 permissions
            if 'enmasse.basic_auth.3' in exported_by_security:
                auth3_perms = exported_by_security['enmasse.basic_auth.3']
                self.assertNotIn('pub', auth3_perms)  # Should have no pub permissions
                self.assertIn('sub', auth3_perms)
                self.assertEqual(auth3_perms['sub'], ['enmasse.topic.3'])

        else:
            logger.warning('No pubsub permission definitions found in test YAML template')

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

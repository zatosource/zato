# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main
import uuid

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.audit_retention import AuditRetentionImporter
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAuditRetention(TestCase):
    """ Tests for importing audit retention policies from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()
        self.audit_retention_importer = AuditRetentionImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def test_sync_retention_policies(self) -> 'None':
        """ Policies are created on the first sync and updated in place on the second one.
        """
        self._setup_test_environment()

        # Create a unique policy name for this test to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]

        policy_defs = [{
            'name': f'enmasse.test_audit_retention_{unique_suffix}',
            'retention_days': 90,
            'content_retention_days': 14,
            'archive_dir': '/tmp/zato-audit-archive',
        }]

        # First sync - should create the policy
        created, updated = self.audit_retention_importer.sync_retention_policies(policy_defs, self.session)

        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        policy_name = policy_defs[0]['name']
        self.assertIn(policy_name, self.audit_retention_importer.policy_defs)

        policy_id = self.audit_retention_importer.policy_defs[policy_name]['id']

        # Second sync - should update the policy in place, keeping its id stable
        created_2, updated_2 = self.audit_retention_importer.sync_retention_policies(policy_defs, self.session)

        self.assertEqual(len(created_2), 0)
        self.assertEqual(len(updated_2), 1)

        policy_id_2 = self.audit_retention_importer.policy_defs[policy_name]['id']
        self.assertEqual(policy_id, policy_id_2)

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

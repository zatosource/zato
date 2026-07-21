# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import logging
from unittest import TestCase, main
import uuid

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.audit_retention import AuditRetentionImporter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAuditRetentionExporter(TestCase):
    """ Tests exporting audit retention policies to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.audit_retention_importer = AuditRetentionImporter(self.importer)

        self.session = cast_('any_', None)

        # The policy this test creates and expects to see exported back
        unique_suffix = uuid.uuid4().hex[:8]

        self.policy_def = {
            'name': f'enmasse.test_audit_retention_export_{unique_suffix}',
            'retention_days': 60,
            'content_retention_days': 7,
            'archive_dir': '/tmp/zato-audit-archive-export',
        }

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import the retention policy definition
        _, _ = self.audit_retention_importer.sync_retention_policies([self.policy_def], self.session)

        self.session.commit()

# ################################################################################################################################

    def test_audit_retention_export(self) -> 'None':
        """ Tests the export of retention policy definitions - a full round-trip.
        """
        self._setup_test_environment()

        # Initialize the exporter
        yaml_exporter = EnmasseYAMLExporter()

        # Export the data
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Get the retention policy section
        exported_policies = exported_data.get('audit_retention', [])

        # Take into account only the policy this test created
        exported_policies_dict = {item['name']: item for item in exported_policies}

        policy_name = self.policy_def['name']
        self.assertIn(policy_name, exported_policies_dict, f'Exported policies missing policy: {policy_name}')

        exported_policy = exported_policies_dict[policy_name]

        # Every field must round-trip unchanged
        self.assertEqual(exported_policy['retention_days'], self.policy_def['retention_days'])
        self.assertEqual(exported_policy['content_retention_days'], self.policy_def['content_retention_days'])
        self.assertEqual(exported_policy['archive_dir'], self.policy_def['archive_dir'])

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.cli.enmasse.importers.alert_rule import AlertRuleImporter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAlertRuleExporter(TestCase):
    """ Tests exporting alert rule definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.alert_rule_importer = AlertRuleImporter(self.importer)

        self.session = cast_('any_', None)

        # The rule this test creates and expects to see exported back
        unique_suffix = uuid.uuid4().hex[:8]

        self.rule_def = {
            'name': f'enmasse.test_alert_rule_export_{unique_suffix}',
            'kind': 'missing-followup',
            'source': 'hl7',
            'object_name': 'channel.oru.inbound',
            'action': 'teams',
            'action_config': {'webhook_url': 'https://example.webhook.office.com/webhookb2/abc'},
            'config': {'deadline_seconds': 120},
            'dedup_window_seconds': 7200,
            'is_active': True,
        }

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import the alert rule definition
        _, _ = self.alert_rule_importer.sync_alert_rules([self.rule_def], self.session)

        self.session.commit()

# ################################################################################################################################

    def test_alert_rule_export(self) -> 'None':
        """ Tests the export of alert rule definitions - a full round-trip.
        """
        self._setup_test_environment()

        # Initialize the exporter
        yaml_exporter = EnmasseYAMLExporter()

        # Export the data
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Get the alert rule section
        exported_rules = exported_data.get('alert_rule', [])

        # Take into account only the rule this test created
        exported_rules_dict = {item['name']: item for item in exported_rules}

        rule_name = self.rule_def['name']
        self.assertIn(rule_name, exported_rules_dict, f'Exported rules missing rule: {rule_name}')

        exported_rule = exported_rules_dict[rule_name]

        # Every field must round-trip unchanged
        self.assertEqual(exported_rule['kind'], self.rule_def['kind'])
        self.assertEqual(exported_rule['source'], self.rule_def['source'])
        self.assertEqual(exported_rule['object_name'], self.rule_def['object_name'])
        self.assertEqual(exported_rule['action'], self.rule_def['action'])
        self.assertEqual(exported_rule['action_config'], self.rule_def['action_config'])
        self.assertEqual(exported_rule['config'], self.rule_def['config'])
        self.assertEqual(exported_rule['dedup_window_seconds'], self.rule_def['dedup_window_seconds'])
        self.assertEqual(exported_rule['is_active'], self.rule_def['is_active'])

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

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
from zato.cli.enmasse.importers.alert_rule import AlertRuleImporter
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAlertRules(TestCase):
    """ Tests for importing alert rules from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()
        self.alert_rule_importer = AlertRuleImporter(self.importer)

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

    def test_sync_alert_rules(self) -> 'None':
        """ Rules are created on the first sync and updated in place on the second one.
        """
        self._setup_test_environment()

        # Create a unique rule name for this test to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]

        rule_defs = [{
            'name': f'enmasse.test_alert_rule_{unique_suffix}',
            'kind': 'feed-silent',
            'source': 'hl7',
            'object_name': 'channel.adt.inbound',
            'action': 'slack',
            'action_config': {'webhook_url': 'https://hooks.slack.example.com/services/abc'},
            'config': {'silent_after_seconds': 600},
            'dedup_window_seconds': 1800,
        }]

        # First sync - should create the rule
        created, updated = self.alert_rule_importer.sync_alert_rules(rule_defs, self.session)

        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        rule_name = rule_defs[0]['name']
        self.assertIn(rule_name, self.alert_rule_importer.rule_defs)

        rule_id = self.alert_rule_importer.rule_defs[rule_name]['id']

        # Second sync - should update the rule in place, keeping its id stable
        created_2, updated_2 = self.alert_rule_importer.sync_alert_rules(rule_defs, self.session)

        self.assertEqual(len(created_2), 0)
        self.assertEqual(len(updated_2), 1)

        rule_id_2 = self.alert_rule_importer.rule_defs[rule_name]['id']
        self.assertEqual(rule_id, rule_id_2)

# ################################################################################################################################

    def test_defaults_are_applied(self) -> 'None':
        """ A rule carrying only its name and kind receives the documented defaults.
        """
        self._setup_test_environment()

        unique_suffix = uuid.uuid4().hex[:8]

        rule_defs = [{
            'name': f'enmasse.test_alert_rule_min_{unique_suffix}',
            'kind': 'error-rate-above-threshold',
        }]

        created, _ = self.alert_rule_importer.sync_alert_rules(rule_defs, self.session)

        self.assertEqual(len(created), 1)
        self.assertIn(rule_defs[0]['name'], self.alert_rule_importer.rule_defs)

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

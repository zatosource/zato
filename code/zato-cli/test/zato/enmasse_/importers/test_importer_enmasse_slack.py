# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.slack import SlackImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSlackFromYAML(TestCase):
    """ Tests importing Slack definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Slack definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize Slack importer
        self.slack_importer = SlackImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_slack_definition_creation(self):
        """ Test creating Slack definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        slack_defs = self.yaml_config['slack']

        # Process all Slack definitions
        created, updated = self.slack_importer.sync_definitions(slack_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Slack connection was created correctly
        slack = self.session.query(GenericConn).filter_by(
            name='enmasse.chat.slack.1',
            type_=GENERIC.CONNECTION.TYPE.CHAT_SLACK
        ).one()

        self.assertTrue(slack.is_active)
        self.assertTrue(hasattr(slack, 'secret'))

# ################################################################################################################################

    def test_slack_update(self):
        """ Test updating existing Slack definitions.
        """
        self._setup_test_environment()

        # First, get the Slack definition from YAML and create it
        slack_defs = self.yaml_config['slack']
        slack_def = slack_defs[0]

        # Create the Slack definition
        instance = self.slack_importer.create_definition(slack_def, self.session)
        self.session.commit()
        self.assertEqual(instance.name, slack_def['name'])

        # Prepare an update definition based on the existing one, with a new token
        update_def = {
            'name': slack_def['name'],
            'id': instance.id,
            'token': 'xoxb-updated-test-token',
        }

        # Update the Slack definition
        updated_instance = self.slack_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.secret, 'xoxb-updated-test-token')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CHAT_SLACK)

# ################################################################################################################################

    def test_complete_slack_import_flow(self):
        """ Test the complete flow of importing Slack definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Slack definitions from the YAML
        slack_list = self.yaml_config['slack']
        slack_created, slack_updated = self.slack_importer.sync_definitions(slack_list, self.session)

        # Update importer's Slack definitions
        self.importer.slack_defs = self.slack_importer.connection_defs

        # Verify Slack definitions were created
        self.assertEqual(len(slack_created), 1)
        self.assertEqual(len(slack_updated), 0)

        # Verify the Slack definitions dictionary was populated
        self.assertEqual(len(self.slack_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.slack_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        slack_created2, slack_updated2 = self.slack_importer.sync_definitions(slack_list, self.session)
        self.assertEqual(len(slack_created2), 0)
        self.assertEqual(len(slack_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

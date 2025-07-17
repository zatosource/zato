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
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.common.odb.model import PubSubTopic
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubTopicFromYAML(TestCase):
    """ Tests importing pubsub topic definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains topic definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize PubSubTopic importer
        self.pubsub_topic_importer = PubSubTopicImporter(self.importer)

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

    def test_pubsub_topic_definition_creation(self):
        """ Test creating pubsub topic definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        topic_defs = self.yaml_config['pubsub_topic']

        # Process all pubsub topic definitions
        created, updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_defs, self.session)

        # Should have created 3 definitions
        self.assertEqual(len(created), 3)
        self.assertEqual(len(updated), 0)

        # Verify pubsub topics were created correctly
        topic1 = self.session.query(PubSubTopic).filter_by(name='enmasse.topic.1').one()  # type: ignore
        self.assertEqual(topic1.description, 'Optional description for topic 1')
        self.assertTrue(topic1.is_active)

        topic2 = self.session.query(PubSubTopic).filter_by(name='enmasse.topic.2').one()  # type: ignore
        self.assertEqual(topic2.description, 'Optional description for topic 2')
        self.assertTrue(topic2.is_active)

        topic3 = self.session.query(PubSubTopic).filter_by(name='enmasse.topic.3').one()  # type: ignore
        self.assertEqual(topic3.description, 'Optional description for topic 3')
        self.assertTrue(topic3.is_active)

# ################################################################################################################################

    def test_pubsub_topic_update(self):
        """ Test updating existing pubsub topic definitions.
        """
        self._setup_test_environment()

        # First, get the pubsub topic definition from YAML and create it
        topic_defs = self.yaml_config['pubsub_topic']
        topic_def = topic_defs[0]

        # Create the pubsub topic definition
        instance = self.pubsub_topic_importer.create_pubsub_topic_definition(topic_def, self.session)
        self.session.commit()
        original_description = topic_def['description']
        self.assertEqual(instance.description, original_description)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': topic_def['name'],
            'id': instance.id,
            'description': 'Updated description for topic 1',  # Changed description
            'is_active': False  # Changed is_active
        }

        # Update the pubsub topic definition
        updated_instance = self.pubsub_topic_importer.update_pubsub_topic_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.description, 'Updated description for topic 1')
        self.assertFalse(updated_instance.is_active)

        # Make sure name was preserved
        self.assertEqual(updated_instance.name, topic_def['name'])

# ################################################################################################################################

    def test_complete_pubsub_topic_import_flow(self):
        """ Test the complete flow of importing pubsub topic definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all pubsub topic definitions from the YAML
        topic_list = self.yaml_config['pubsub_topic']
        topic_created, topic_updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_list, self.session)

        # Update importer's pubsub topic definitions
        self.importer.pubsub_topic_defs = self.pubsub_topic_importer.pubsub_topic_defs

        # Verify pubsub topic definitions were created
        self.assertEqual(len(topic_created), 3)
        self.assertEqual(len(topic_updated), 0)

        # Verify the pubsub topic definitions dictionary was populated
        self.assertEqual(len(self.pubsub_topic_importer.pubsub_topic_defs), 3)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.pubsub_topic_defs), 3)

        # Try importing the same definitions again - should result in updates, not creations
        topic_created2, topic_updated2 = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_list, self.session)
        self.assertEqual(len(topic_created2), 0)
        self.assertEqual(len(topic_updated2), 3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

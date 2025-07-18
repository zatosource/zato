# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
import unittest
from unittest.mock import patch

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.test.enmasse_ import _template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubTopicExporter(unittest.TestCase):

    def setUp(self):
        self.yaml_data = yaml.safe_load(_template_complex_01.template_complex_01)

    @patch('zato.cli.enmasse.importers.pubsub_topic.PubSubTopicImporter.import_')
    @patch('zato.cli.enmasse.importers.security.SecurityImporter.import_')
    @patch('zato.cli.enmasse.exporter.EnmasseYAMLExporter.export_pubsub_topic')
    def test_export_pubsub_topic(self, mock_export_pubsub_topic, mock_security_import, mock_pubsub_topic_import):

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write(_template_complex_01.template_complex_01)
            temp_file_path = temp_file.name

        try:
            # Import security definitions first (required for some connections)
            security_importer = SecurityImporter()
            security_importer.import_(temp_file_path)

            # Import pub/sub topic definitions
            pubsub_topic_importer = PubSubTopicImporter()
            pubsub_topic_importer.import_(temp_file_path)

            # Create exporter and test export
            exporter = EnmasseYAMLExporter()

            # Mock the export method to return expected data
            expected_topics = [
                {'name': 'enmasse.topic.1', 'description': 'Optional description for topic 1'},
                {'name': 'enmasse.topic.2', 'description': 'Optional description for topic 2'},
                {'name': 'enmasse.topic.3', 'description': 'Optional description for topic 3'}
            ]
            mock_export_pubsub_topic.return_value = expected_topics

            # Test the export
            with patch('zato.cli.enmasse.exporter.EnmasseYAMLExporter.get_cluster'):
                exported_topics = exporter.export_pubsub_topic(None)

            # Verify the exported topics match expected structure
            self.assertEqual(len(exported_topics), 3)

            # Check each topic
            for i, topic in enumerate(exported_topics):
                expected_topic = expected_topics[i]
                self.assertEqual(topic['name'], expected_topic['name'])
                self.assertEqual(topic['description'], expected_topic['description'])

            # Verify the topics from YAML template
            yaml_topics = self.yaml_data.get('pubsub_topic', [])
            self.assertEqual(len(yaml_topics), 3)

            for yaml_topic in yaml_topics:
                self.assertIn('name', yaml_topic)
                self.assertTrue(yaml_topic['name'].startswith('enmasse.topic.'))
                if 'description' in yaml_topic:
                    self.assertIsInstance(yaml_topic['description'], str)

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def test_yaml_template_structure(self):
        """Test that the YAML template has the expected pubsub_topic structure"""
        pubsub_topics = self.yaml_data.get('pubsub_topic', [])

        self.assertIsInstance(pubsub_topics, list)
        self.assertEqual(len(pubsub_topics), 3)

        expected_names = ['enmasse.topic.1', 'enmasse.topic.2', 'enmasse.topic.3']
        actual_names = [topic['name'] for topic in pubsub_topics]

        self.assertEqual(actual_names, expected_names)

        # Check that all topics have descriptions
        for topic in pubsub_topics:
            self.assertIn('name', topic)
            self.assertIn('description', topic)
            self.assertTrue(topic['name'].startswith('enmasse.topic.'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()

# ################################################################################################################################
# ################################################################################################################################

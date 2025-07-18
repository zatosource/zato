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
from zato.cli.enmasse.exporters.pubsub_topic import PubSubTopicExporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
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

class TestEnmassePubSubTopicExporter(TestCase):
    """ Tests exporting pub/sub topic definitions.
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

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.pubsub_topic_exporter = PubSubTopicExporter(self.exporter)

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

        # Import security definitions first, as pubsub topics may depend on them
        security_defs_from_yaml = self.yaml_config['security']
        if security_defs_from_yaml:

            # This method already populates self.importer.sec_defs after commit
            created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
            logger.info('Imported %d security definitions (created=%d, updated=%d)',
                len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

            # Verify that security definitions were populated correctly
            logger.info('Security definitions in importer: %s', list(self.importer.sec_defs.keys()))

        _ = self.session.commit()

# ################################################################################################################################

    def test_pubsub_topic_export(self) -> 'None':
        """ Tests the export of pub/sub topic definitions.
        """
        logger.info('Starting test_pubsub_topic_export')

        # Set up the test environment
        self._setup_test_environment()

        # Import pubsub topic definitions from the YAML template
        pubsub_topic_defs_from_yaml = self.yaml_config['pubsub_topic']

        logger.info('Found %d pubsub topic definitions in YAML template', len(pubsub_topic_defs_from_yaml))

        # Import the topics into the database
        created, updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(pubsub_topic_defs_from_yaml, self.session)
        logger.info('Imported %d pubsub topic definitions (created=%d, updated=%d)',
            len(created) + len(updated), len(created), len(updated))

        _ = self.session.commit()

        # Now test the export functionality
        exported_topics = self.pubsub_topic_exporter.export(self.session, self.exporter.cluster_id)
        logger.info('Exported %d pubsub topic definitions', len(exported_topics))

        # Verify that we exported the expected number of topics
        self.assertEqual(len(exported_topics), len(created) + len(updated),
            f'Expected {len(created) + len(updated)} exported topics, got {len(exported_topics)}')

        # Extract expected topic data directly from the YAML template
        # Parse the template to get the expected values
        template_dict = yaml.safe_load(template_complex_01)

        # Build expected fields dictionary from the template
        required_topic_fields = {}
        for topic_def in template_dict['pubsub_topic']:
            topic_name = topic_def['name']

            # Create a copy of the topic definition for expected fields
            topic_required = {
                'name': topic_name,
            }

            # Add description if present
            if 'description' in topic_def and topic_def['description']:
                topic_required['description'] = topic_def['description']

            # Add this topic's requirements to our dictionary
            required_topic_fields[topic_name] = topic_required

        # Verify each exported topic against required fields
        for topic in exported_topics:
            name = topic['name']
            self.assertIn(name, required_topic_fields, f'Unexpected topic {name} in export')
            expected = required_topic_fields[name]

            # Check all required fields in the topic definition
            # First check basic required fields that must always be present
            self.assertIn('name', topic, f'Required field name missing in topic {name}')
            self.assertEqual(topic['name'], expected['name'],
                f'Field name has incorrect value in topic {name}, expected {expected["name"]}, got {topic["name"]}')

            # Then check optional fields that might be in expected but not always in exported data
            for field, value in expected.items():
                if field != 'name':
                    if field in topic:
                        self.assertEqual(topic[field], value,
                            f'Field {field} has incorrect value in topic {name}, expected {value}, got {topic[field]}')
                    else:
                        logger.info(f'Optional field {field} not found in exported topic {name}, but was in template')
        else:
            logger.warning('No pubsub topic definitions found in test YAML template')

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

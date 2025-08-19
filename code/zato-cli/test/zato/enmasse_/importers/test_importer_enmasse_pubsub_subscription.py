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
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.common.odb.model import PubSubSubscriptionTopic
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubSubscriptionFromYAML(TestCase):
    """ Tests importing pubsub subscription definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':

        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains subscription definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.pubsub_topic_importer = PubSubTopicImporter(self.importer)
        self.pubsub_subscription_importer = PubSubSubscriptionImporter(self.importer)
        self.outgoing_rest_importer = OutgoingRESTImporter(self.importer)

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

    def _create_dependencies(self):
        """ Create security definitions, topics, and outgoing REST connections that subscriptions depend on.
        """
        # Create security definitions first
        security_defs = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_defs, self.session)

        # Create pubsub topics
        topic_defs = self.yaml_config['pubsub_topic']
        _ = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_defs, self.session)
        self.importer.pubsub_topic_defs = self.pubsub_topic_importer.pubsub_topic_defs

        # Create outgoing REST connections
        outgoing_rest_defs = self.yaml_config['outgoing_rest']
        _ = self.outgoing_rest_importer.sync_outgoing_rest(outgoing_rest_defs, self.session)
        self.importer.outgoing_rest_defs = self.outgoing_rest_importer.connection_defs

# ################################################################################################################################

    def test_pubsub_subscription_definition_creation(self):
        """ Test creating pubsub subscription definitions from YAML.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        subscription_defs = self.yaml_config['pubsub_subscription']

        # Process all pubsub subscription definitions
        created, updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_defs, self.session)

        # Should have processed 3 definitions (create or update)
        total_processed = len(created) + len(updated)
        self.assertEqual(total_processed, 3)

        # Get all processed subscriptions
        all_subs = created + updated
        push_rest_sub = cast_('any_', None)
        push_service_sub = cast_('any_', None)

        for sub in all_subs:
            if sub.delivery_type == 'push' and sub.push_type == 'rest':
                push_rest_sub = sub
            elif sub.delivery_type == 'push' and sub.push_type == 'service':
                push_service_sub = sub

        # Verify push REST subscription
        self.assertIsNotNone(push_rest_sub)
        self.assertEqual(push_rest_sub.delivery_type, 'push')
        self.assertEqual(push_rest_sub.push_type, 'rest')
        self.assertIsNotNone(push_rest_sub.rest_push_endpoint_id)

        # Verify push service subscription
        self.assertIsNotNone(push_service_sub)
        self.assertEqual(push_service_sub.delivery_type, 'push')
        self.assertEqual(push_service_sub.push_type, 'service')
        self.assertEqual(push_service_sub.push_service_name, 'demo.input-logger')

# ################################################################################################################################

    def test_pubsub_subscription_update(self):
        """ Test updating existing pubsub subscription definitions.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # First, get the pubsub subscription definition from YAML and create it
        subscription_defs = self.yaml_config['pubsub_subscription']
        subscription_def = subscription_defs[0]  # Pull subscription

        # Get security base ID
        sec_base_id = self.pubsub_subscription_importer.get_security_base_id_by_name(subscription_def['security'], self.session)

        # Get topic IDs
        topic_id_list = []
        for topic_name in subscription_def['topic_list']:
            topic_id = self.pubsub_subscription_importer.get_topic_id_by_name(topic_name, self.session)
            topic_id_list.append(topic_id)

        # Prepare subscription definition
        sub_def = {
            'sec_base_id': sec_base_id,
            'delivery_type': subscription_def['delivery_type'],
            'topic_id_list': topic_id_list,
            'is_active': subscription_def.get('is_active', True),
            'max_retry_time': subscription_def.get('max_retry_time', '365d'),
            'name': subscription_def['security']
        }

        # Create the pubsub subscription definition
        instance = self.pubsub_subscription_importer.create_pubsub_subscription_definition(sub_def, self.session)
        self.session.commit()
        original_delivery_type = sub_def['delivery_type']
        self.assertEqual(instance.delivery_type, original_delivery_type)

        # Prepare an update definition based on the existing one
        update_def = {
            'id': instance.id,
            'sec_base_id': sec_base_id,
            'delivery_type': 'push',  # Changed delivery type
            'push_type': 'service',
            'push_service_name': 'demo.updated-service',
            'topic_id_list': topic_id_list,
            'is_active': False  # Changed is_active
        }

        # Update the pubsub subscription definition
        updated_instance = self.pubsub_subscription_importer.update_pubsub_subscription_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.delivery_type, 'push')
        self.assertEqual(updated_instance.push_type, 'service')
        self.assertEqual(updated_instance.push_service_name, 'demo.updated-service')
        self.assertFalse(updated_instance.is_active)

        # Make sure sub_key was preserved
        self.assertEqual(updated_instance.sub_key, instance.sub_key)

# ################################################################################################################################

    def test_pubsub_subscription_topic_associations(self):
        """ Test that subscription-topic associations are correctly created.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        subscription_defs = self.yaml_config['pubsub_subscription']

        # Process all pubsub subscription definitions
        created, _ = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_defs, self.session)

        # Verify topic associations
        for subscription in created:
            # Get subscription-topic associations
            sub_topics = self.session.query(PubSubSubscriptionTopic).filter_by(subscription_id=subscription.id).all()

            # Find the corresponding YAML definition
            yaml_def = cast_('any_', None)
            for yaml_sub in subscription_defs:
                sec_base_id = self.pubsub_subscription_importer.get_security_base_id_by_name(yaml_sub['security'], self.session)
                if sec_base_id == subscription.sec_base_id and yaml_sub['delivery_type'] == subscription.delivery_type:
                    yaml_def = yaml_sub
                    break

            self.assertIsNotNone(yaml_def)

            # Verify the number of topics matches
            self.assertEqual(len(sub_topics), len(yaml_def['topic_list']))

            # Verify each topic is correctly associated
            for sub_topic in sub_topics:
                topic = self.session.query(PubSubSubscriptionTopic).filter_by(subscription_id=subscription.id, topic_id=sub_topic.topic_id).first()
                self.assertIsNotNone(topic)

# ################################################################################################################################

    def test_pubsub_subscription_delivery_types(self):
        """ Test different delivery types are handled correctly.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Get definitions from YAML
        subscription_defs = self.yaml_config['pubsub_subscription']

        # Process all pubsub subscription definitions
        created, updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_defs, self.session)

        # Count delivery types from all processed subscriptions
        all_subs = created + updated
        pull_count = 0
        push_count = 0

        for subscription in all_subs:
            if subscription.delivery_type == 'pull':
                pull_count += 1
                self.assertIsNone(subscription.push_type)
                self.assertIsNone(subscription.rest_push_endpoint_id)
                self.assertIsNone(subscription.push_service_name)
            elif subscription.delivery_type == 'push':
                push_count += 1
                self.assertIsNotNone(subscription.push_type)
                if subscription.push_type == 'rest':
                    self.assertIsNotNone(subscription.rest_push_endpoint_id)
                    self.assertIsNone(subscription.push_service_name)
                elif subscription.push_type == 'service':
                    self.assertIsNone(subscription.rest_push_endpoint_id)
                    self.assertIsNotNone(subscription.push_service_name)

        # Verify we have the expected counts based on template (database state agnostic)
        total_count = pull_count + push_count
        self.assertEqual(total_count, 3)

# ################################################################################################################################

    def test_complete_pubsub_subscription_import_flow(self):
        """ Test the complete flow of importing pubsub subscription definitions from a YAML file.
        """
        self._setup_test_environment()
        self._create_dependencies()

        # Process all pubsub subscription definitions from the YAML
        subscription_list = self.yaml_config['pubsub_subscription']
        subscription_created, subscription_updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_list, self.session)

        # Update importer's pubsub subscription definitions
        self.importer.pubsub_subscription_defs = self.pubsub_subscription_importer.pubsub_subscription_defs

        # Verify pubsub subscription definitions were processed
        total_processed = len(subscription_created) + len(subscription_updated)
        self.assertEqual(total_processed, 3)

        # Verify the pubsub subscription definitions dictionary was populated
        self.assertEqual(len(self.pubsub_subscription_importer.pubsub_subscription_defs), 3)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.pubsub_subscription_defs), 3)

        # Verify all subscriptions are active by default
        all_subs = subscription_created + subscription_updated
        for sub in all_subs:
            self.assertTrue(sub.is_active)

        # Verify cluster_id is set correctly
        for sub in all_subs:
            self.assertEqual(sub.cluster_id, self.importer.cluster_id)

        # Verify each subscription has a unique sub_key
        sub_keys = [sub.sub_key for sub in all_subs]
        self.assertEqual(len(sub_keys), len(set(sub_keys)))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.cli.enmasse.exporters.pubsub_subscription import PubSubSubscriptionExporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
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

class TestEnmassePubSubSubscriptionExporter(TestCase):
    """ Tests exporting pub/sub subscription definitions.
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
        self.pubsub_subscription_importer = PubSubSubscriptionImporter(self.importer)
        self.outgoing_rest_importer = OutgoingRESTImporter(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.pubsub_subscription_exporter = PubSubSubscriptionExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import security definitions first, as subscriptions depend on them
        security_defs_from_yaml = self.yaml_config['security']
        if security_defs_from_yaml:

            # This method already populates self.importer.sec_defs after commit
            created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
            logger.info('Imported %d security definitions (created=%d, updated=%d)',
                len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

        _ = self.session.commit()

        # Import pubsub topics as subscriptions may reference them
        pubsub_topic_defs_from_yaml = self.yaml_config.get('pubsub_topic', [])
        if pubsub_topic_defs_from_yaml:

            # Import the topics into the database
            created, updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(pubsub_topic_defs_from_yaml, self.session)
            logger.info('Imported %d pubsub topic definitions (created=%d, updated=%d)',
                len(created) + len(updated), len(created), len(updated))

        _ = self.session.commit()

        # Import outgoing REST connections as push subscriptions may reference them
        outgoing_rest_defs_from_yaml = self.yaml_config.get('outgoing_rest', [])
        if outgoing_rest_defs_from_yaml:

            # Import the connections into the database
            created, updated = self.outgoing_rest_importer.sync_outgoing_rest(outgoing_rest_defs_from_yaml, self.session)
            logger.info('Imported %d outgoing REST definitions (created=%d, updated=%d)',
                len(created) + len(updated), len(created), len(updated))

        _ = self.session.commit()

# ################################################################################################################################

    def test_pubsub_subscription_export(self) -> 'None':
        """ Tests the export of pub/sub subscription definitions.
        """
        self._setup_test_environment()

        # Get subscription definitions from YAML
        pubsub_subscription_defs_from_yaml = self.yaml_config.get('pubsub_subscription', [])
        if pubsub_subscription_defs_from_yaml:

            # Import the subscriptions into the database
            created, updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(pubsub_subscription_defs_from_yaml, self.session)

            created_count = len(created)
            updated_count = len(updated)
            total_count = created_count + updated_count

            logger.info('Imported %d pubsub subscription definitions (created=%d, updated=%d)',
                total_count, created_count, updated_count)

            _ = self.session.commit()

            # Now test the export functionality
            exported_subscriptions = self.pubsub_subscription_exporter.export(self.session, self.exporter.cluster_id)

            exported_count = len(exported_subscriptions)
            logger.info('Exported %d pubsub subscription definitions', exported_count)

            # Verify that all expected subscriptions from template are exported
            template_dict = yaml.safe_load(template_complex_01)

            # Build expected subscriptions dictionary from the template
            expected_subscriptions = {}
            for sub_def in template_dict['pubsub_subscription']:
                security_name = sub_def['security']
                expected_subscriptions[security_name] = sub_def

            # Build exported subscriptions dictionary by security name
            exported_by_security = {}
            for subscription in exported_subscriptions:
                security_name = subscription['security'] # type: ignore
                exported_by_security[security_name] = subscription

            # Verify that all expected subscriptions from template are found in export
            expected_security_names = expected_subscriptions.keys()
            for security_name in expected_security_names:
                error_msg = f'Expected security {security_name} from template not found in export'
                self.assertIn(security_name, exported_by_security, error_msg)

            # Verify that all expected subscriptions are present in the export
            for security_name, expected in expected_subscriptions.items():
                subscription = exported_by_security[security_name]

                # Check required fields
                security_missing_msg = f'Required field security missing in subscription {security_name}'
                self.assertIn('security', subscription, security_missing_msg)

                subscription_security = subscription['security'] # type: ignore
                expected_security = expected['security']
                security_incorrect_msg = f'Field security has incorrect value in subscription {security_name}'
                self.assertEqual(subscription_security, expected_security, security_incorrect_msg)

                delivery_type_missing_msg = f'Required field delivery_type missing in subscription {security_name}'
                self.assertIn('delivery_type', subscription, delivery_type_missing_msg)

                subscription_delivery_type = subscription['delivery_type'] # type: ignore
                expected_delivery_type = expected['delivery_type']
                delivery_type_incorrect_msg = f'Field delivery_type has incorrect value in subscription {security_name}'
                self.assertEqual(subscription_delivery_type, expected_delivery_type, delivery_type_incorrect_msg)

                topic_list_missing_msg = f'Required field topic_list missing in subscription {security_name}'
                self.assertIn('topic_list', subscription, topic_list_missing_msg)

                subscription_topic_list = set(subscription['topic_list']) # type: ignore
                expected_topic_list = set(expected['topic_list'])
                topic_list_incorrect_msg = f'Field topic_list has incorrect value in subscription {security_name}'
                self.assertEqual(subscription_topic_list, expected_topic_list, topic_list_incorrect_msg)

                # Check push-specific fields
                expected_delivery_type = expected['delivery_type']
                if expected_delivery_type == 'push':

                    push_rest_endpoint_in_expected = 'push_rest_endpoint' in expected
                    if push_rest_endpoint_in_expected:
                        push_rest_endpoint_missing_msg = f'Expected push_rest_endpoint missing in subscription {security_name}'
                        self.assertIn('push_rest_endpoint', subscription, push_rest_endpoint_missing_msg)

                        subscription_push_rest_endpoint = subscription['push_rest_endpoint'] # type: ignore
                        expected_push_rest_endpoint = expected['push_rest_endpoint']
                        push_rest_endpoint_incorrect_msg = f'Field push_rest_endpoint has incorrect value in subscription {security_name}'
                        self.assertEqual(subscription_push_rest_endpoint, expected_push_rest_endpoint, push_rest_endpoint_incorrect_msg)

                    push_service_in_expected = 'push_service' in expected
                    if push_service_in_expected:
                        push_service_missing_msg = f'Expected push_service missing in subscription {security_name}'
                        self.assertIn('push_service', subscription, push_service_missing_msg)

                        subscription_push_service = subscription['push_service'] # type: ignore
                        expected_push_service = expected['push_service']
                        push_service_incorrect_msg = f'Field push_service has incorrect value in subscription {security_name}'
                        self.assertEqual(subscription_push_service, expected_push_service, push_service_incorrect_msg)

                # Verify no unexpected fields
                allowed_fields = {'security', 'delivery_type', 'topic_list', 'push_rest_endpoint', 'push_service', 'max_retry_time'}
                subscription_fields = subscription
                for field in subscription_fields:
                    unexpected_field_msg = f'Unexpected field {field} in subscription {security_name}'
                    self.assertIn(field, allowed_fields, unexpected_field_msg)

            # Verify specific expected subscriptions from the template
            exported_by_security = {}
            for sub in exported_subscriptions:
                sub_security = sub['security'] # type: ignore
                exported_by_security[sub_security] = sub

            # Check enmasse.basic_auth.1 subscription
            auth1_security_name = 'enmasse.basic_auth.1'
            auth1_in_exported = auth1_security_name in exported_by_security
            if auth1_in_exported:
                auth1_sub = exported_by_security[auth1_security_name]

                auth1_delivery_type = auth1_sub['delivery_type'] # type: ignore
                self.assertEqual(auth1_delivery_type, 'pull')

                auth1_topic_list = set(auth1_sub['topic_list']) # type: ignore
                expected_auth1_topics = {'enmasse.topic.1', 'enmasse.topic.2'}
                self.assertEqual(auth1_topic_list, expected_auth1_topics)

                self.assertNotIn('push_rest_endpoint', auth1_sub)
                self.assertNotIn('push_service', auth1_sub)

            # Check enmasse.basic_auth.2 subscription
            auth2_security_name = 'enmasse.basic_auth.2'
            auth2_in_exported = auth2_security_name in exported_by_security
            if auth2_in_exported:
                auth2_sub = exported_by_security[auth2_security_name]

                auth2_delivery_type = auth2_sub['delivery_type'] # type: ignore
                self.assertEqual(auth2_delivery_type, 'push')

                auth2_topic_list = auth2_sub['topic_list'] # type: ignore
                expected_auth2_topics = ['enmasse.topic.1']
                self.assertEqual(auth2_topic_list, expected_auth2_topics)

                self.assertIn('push_rest_endpoint', auth2_sub)

                auth2_push_rest_endpoint = auth2_sub['push_rest_endpoint'] # type: ignore
                expected_auth2_endpoint = 'enmasse.outgoing.rest.1'
                self.assertEqual(auth2_push_rest_endpoint, expected_auth2_endpoint)

                self.assertNotIn('push_service', auth2_sub)

            # Check enmasse.basic_auth.3 subscription
            auth3_security_name = 'enmasse.basic_auth.3'
            auth3_in_exported = auth3_security_name in exported_by_security
            if auth3_in_exported:
                auth3_sub = exported_by_security[auth3_security_name]

                auth3_delivery_type = auth3_sub['delivery_type'] # type: ignore
                self.assertEqual(auth3_delivery_type, 'push')

                auth3_topic_list = auth3_sub['topic_list'] # type: ignore
                expected_auth3_topics = ['enmasse.topic.3']
                self.assertEqual(auth3_topic_list, expected_auth3_topics)

                self.assertIn('push_service', auth3_sub)

                auth3_push_service = auth3_sub['push_service'] # type: ignore
                expected_auth3_service = 'demo.input-logger'
                self.assertEqual(auth3_push_service, expected_auth3_service)

                self.assertNotIn('push_rest_endpoint', auth3_sub)

        else:
            logger.warning('No pubsub subscription definitions found in test YAML template')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

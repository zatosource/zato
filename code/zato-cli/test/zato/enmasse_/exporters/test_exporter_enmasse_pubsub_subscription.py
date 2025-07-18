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
            created, updated = self.outgoing_rest_importer.sync_outgoing_rest_definitions(outgoing_rest_defs_from_yaml, self.session)
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
            logger.info('Imported %d pubsub subscription definitions (created=%d, updated=%d)',
                len(created) + len(updated), len(created), len(updated))

            _ = self.session.commit()

            # Now test the export functionality
            exported_subscriptions = self.pubsub_subscription_exporter.export(self.session, self.exporter.cluster_id)
            logger.info('Exported %d pubsub subscription definitions', len(exported_subscriptions))

            # Verify that we exported the expected number of subscriptions
            # From the template, we expect 3 subscriptions
            expected_subscription_count = 3
            self.assertEqual(len(exported_subscriptions), expected_subscription_count,
                f'Expected {expected_subscription_count} exported subscriptions, got {len(exported_subscriptions)}')

            # Extract expected subscription data directly from the YAML template
            # Parse the template to get the expected values
            template_dict = yaml.safe_load(template_complex_01)

            # Build expected subscriptions dictionary from the template
            expected_subscriptions = {}
            for sub_def in template_dict['pubsub_subscription']:
                security_name = sub_def['security']
                expected_subscriptions[security_name] = sub_def

            # Verify each exported subscription against expected values
            for subscription in exported_subscriptions:
                security_name = subscription['security']
                self.assertIn(security_name, expected_subscriptions, f'Unexpected security {security_name} in export')
                expected = expected_subscriptions[security_name]

                # Check required fields
                self.assertIn('security', subscription, f'Required field security missing in subscription {security_name}')
                self.assertEqual(subscription['security'], expected['security'],
                    f'Field security has incorrect value in subscription {security_name}')

                self.assertIn('delivery_type', subscription, f'Required field delivery_type missing in subscription {security_name}')
                self.assertEqual(subscription['delivery_type'], expected['delivery_type'],
                    f'Field delivery_type has incorrect value in subscription {security_name}')

                self.assertIn('topic_list', subscription, f'Required field topic_list missing in subscription {security_name}')
                self.assertEqual(set(subscription['topic_list']), set(expected['topic_list']),
                    f'Field topic_list has incorrect value in subscription {security_name}')

                # Check push-specific fields
                if expected['delivery_type'] == 'push':
                    if 'push_rest_endpoint' in expected:
                        self.assertIn('push_rest_endpoint', subscription, f'Expected push_rest_endpoint missing in subscription {security_name}')
                        self.assertEqual(subscription['push_rest_endpoint'], expected['push_rest_endpoint'],
                            f'Field push_rest_endpoint has incorrect value in subscription {security_name}')

                    if 'push_service' in expected:
                        self.assertIn('push_service', subscription, f'Expected push_service missing in subscription {security_name}')
                        self.assertEqual(subscription['push_service'], expected['push_service'],
                            f'Field push_service has incorrect value in subscription {security_name}')

                # Verify no unexpected fields
                allowed_fields = {'security', 'delivery_type', 'topic_list', 'push_rest_endpoint', 'push_service', 'max_retry_time'}
                for field in subscription:
                    self.assertIn(field, allowed_fields, f'Unexpected field {field} in subscription {security_name}')

            # Verify specific expected subscriptions from the template
            exported_by_security = {sub['security']: sub for sub in exported_subscriptions}

            # Check enmasse.basic_auth.1 subscription
            if 'enmasse.basic_auth.1' in exported_by_security:
                auth1_sub = exported_by_security['enmasse.basic_auth.1']
                self.assertEqual(auth1_sub['delivery_type'], 'pull')
                self.assertEqual(set(auth1_sub['topic_list']), {'enmasse.topic.1', 'enmasse.topic.2'})
                self.assertNotIn('push_rest_endpoint', auth1_sub)
                self.assertNotIn('push_service', auth1_sub)

            # Check enmasse.basic_auth.2 subscription
            if 'enmasse.basic_auth.2' in exported_by_security:
                auth2_sub = exported_by_security['enmasse.basic_auth.2']
                self.assertEqual(auth2_sub['delivery_type'], 'push')
                self.assertEqual(auth2_sub['topic_list'], ['enmasse.topic.1'])
                self.assertIn('push_rest_endpoint', auth2_sub)
                self.assertEqual(auth2_sub['push_rest_endpoint'], 'enmasse.outgoing.rest.1')
                self.assertNotIn('push_service', auth2_sub)

            # Check enmasse.basic_auth.3 subscription
            if 'enmasse.basic_auth.3' in exported_by_security:
                auth3_sub = exported_by_security['enmasse.basic_auth.3']
                self.assertEqual(auth3_sub['delivery_type'], 'push')
                self.assertEqual(auth3_sub['topic_list'], ['enmasse.topic.3'])
                self.assertIn('push_service', auth3_sub)
                self.assertEqual(auth3_sub['push_service'], 'demo.input-logger')
                self.assertNotIn('push_rest_endpoint', auth3_sub)

        else:
            logger.warning('No pubsub subscription definitions found in test YAML template')

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

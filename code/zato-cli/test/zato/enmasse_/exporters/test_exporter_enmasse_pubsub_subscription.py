# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubSubscriptionExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.config_manager.load_yaml_string(template_complex_01)

    def test_pubsub_subscription_export(self):

        exporter = EnmasseExporter(self.config_manager)
        exported_data = exporter.export_to_dict()

        self.assertIn('pubsub_subscription', exported_data, 'Exporter did not produce a "pubsub_subscription" section.')
        exported_subscriptions = exported_data['pubsub_subscription']

        template_dict = yaml.safe_load(template_complex_01)

        expected_subscriptions = {}
        for sub_def in template_dict['pubsub_subscription']:
            security_name = sub_def['security']
            expected_subscriptions[security_name] = sub_def

        exported_by_security = {sub['security']: sub for sub in exported_subscriptions}

        for security_name, expected in expected_subscriptions.items():
            self.assertIn(security_name, exported_by_security,
                f'Expected security {security_name} not found in export')
            subscription = exported_by_security[security_name]

            self.assertEqual(subscription['security'], expected['security'])
            self.assertEqual(subscription['delivery_type'], expected['delivery_type'])
            self.assertEqual(set(subscription['topic_list']), set(expected['topic_list']))

            if expected['delivery_type'] == 'push':
                if 'push_rest_endpoint' in expected:
                    self.assertIn('push_rest_endpoint', subscription)
                    self.assertEqual(subscription['push_rest_endpoint'], expected['push_rest_endpoint'])
                if 'push_service' in expected:
                    self.assertIn('push_service', subscription)
                    self.assertEqual(subscription['push_service'], expected['push_service'])

        if 'enmasse.basic_auth.1' in exported_by_security:
            auth1_sub = exported_by_security['enmasse.basic_auth.1']
            self.assertEqual(auth1_sub['delivery_type'], 'pull')
            self.assertEqual(set(auth1_sub['topic_list']), {'enmasse.topic.1', 'enmasse.topic.2'})

        if 'enmasse.basic_auth.2' in exported_by_security:
            auth2_sub = exported_by_security['enmasse.basic_auth.2']
            self.assertEqual(auth2_sub['delivery_type'], 'push')
            self.assertIn('push_rest_endpoint', auth2_sub)
            self.assertEqual(auth2_sub['push_rest_endpoint'], 'enmasse.outgoing.rest.1')

        if 'enmasse.basic_auth.3' in exported_by_security:
            auth3_sub = exported_by_security['enmasse.basic_auth.3']
            self.assertEqual(auth3_sub['delivery_type'], 'push')
            self.assertIn('push_service', auth3_sub)
            self.assertEqual(auth3_sub['push_service'], 'demo.input-logger')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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

class TestEnmassePubSubTopicExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

    def test_pubsub_topic_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('pubsub_topic', exported_data, 'Exporter did not produce a "pubsub_topic" section.')
        all_exported_topics = exported_data['pubsub_topic']

        exported_topics = [t for t in all_exported_topics if t['name'].startswith('enmasse')]

        template_dict = yaml.safe_load(template_complex_01)

        required_topic_fields = {}
        for topic_def in template_dict['pubsub_topic']:
            topic_name = topic_def['name']
            topic_required = {'name': topic_name}
            if 'description' in topic_def and topic_def['description']:
                topic_required['description'] = topic_def['description']
            required_topic_fields[topic_name] = topic_required

        for topic in exported_topics:
            name = topic['name']
            self.assertIn(name, required_topic_fields, f'Unexpected topic {name} in export')
            expected = required_topic_fields[name]

            self.assertEqual(topic['name'], expected['name'])

            for field, value in expected.items():
                if field != 'name':
                    if field in topic:
                        self.assertEqual(topic[field], value,
                            f'Field {field} has incorrect value in topic {name}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

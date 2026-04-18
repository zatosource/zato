# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubTopicImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_pubsub_topic_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('pubsub_topic', exported)

        topic_list = exported['pubsub_topic']
        topic_by_name = {item['name']: item for item in topic_list}

        self.assertIn('enmasse.topic.1', topic_by_name)
        self.assertIn('enmasse.topic.2', topic_by_name)
        self.assertIn('enmasse.topic.3', topic_by_name)

# ################################################################################################################################

    def test_pubsub_topic_values(self):

        exported = self.config_store.export_to_dict()
        topic_list = exported['pubsub_topic']
        topic_by_name = {item['name']: item for item in topic_list}

        t1 = topic_by_name['enmasse.topic.1']
        self.assertEqual(t1['description'], 'Optional description for topic 1')

        t2 = topic_by_name['enmasse.topic.2']
        self.assertEqual(t2['description'], 'Optional description for topic 2')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

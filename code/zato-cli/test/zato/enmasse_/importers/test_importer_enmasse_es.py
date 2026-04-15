# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseElasticSearchImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_es_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        es_items = template_dict['elastic_search']

        preprocessed = ElasticSearchImporter.preprocess(es_items)

        for item in preprocessed:
            self.assertIn('timeout', item)
            self.assertIn('body_as', item)

# ################################################################################################################################

    def test_es_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('elastic_search', exported)

        es_list = exported['elastic_search']
        es_by_name = {item['name']: item for item in es_list}
        self.assertIn('enmasse.elastic.1', es_by_name)

# ################################################################################################################################

    def test_es_values(self):

        exported = self.config_store.export_to_dict()
        es_list = exported['elastic_search']
        es_by_name = {item['name']: item for item in es_list}

        e1 = es_by_name['enmasse.elastic.1']
        self.assertEqual(e1['hosts'], 'http://elasticsearch:9200')
        self.assertEqual(e1['timeout'], 60)
        self.assertEqual(e1['body_as'], 'json')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

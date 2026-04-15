# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSQLImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_sql_preprocessing_engine_mapping(self):

        template_dict = yaml.safe_load(template_complex_01)
        sql_items = template_dict['sql']

        preprocessed = SQLImporter.preprocess(sql_items)

        for item in preprocessed:
            self.assertIn('engine', item)
            self.assertIn('password', item)

        sql1 = [item for item in preprocessed if item['name'] == 'enmasse.sql.1'][0]
        self.assertEqual(sql1['engine'], 'mysql+pymysql')

        sql2 = [item for item in preprocessed if item['name'] == 'enmasse.sql.2'][0]
        self.assertEqual(sql2['engine'], 'oracle')

# ################################################################################################################################

    def test_sql_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('sql', exported)

        sql_list = exported['sql']
        sql_by_name = {item['name']: item for item in sql_list}

        self.assertIn('enmasse.sql.1', sql_by_name)
        self.assertIn('enmasse.sql.2', sql_by_name)

# ################################################################################################################################

    def test_sql_values(self):

        exported = self.config_store.export_to_dict()
        sql_list = exported['sql']
        sql_by_name = {item['name']: item for item in sql_list}

        s1 = sql_by_name['enmasse.sql.1']
        self.assertEqual(s1['host'], '127.0.0.1')
        self.assertEqual(s1['port'], 3306)
        self.assertEqual(s1['db_name'], 'MYDB_01')
        self.assertEqual(s1['username'], 'enmasse.1')

        s2 = sql_by_name['enmasse.sql.2']
        self.assertEqual(s2['host'], '10.152.81.199')
        self.assertEqual(s2['port'], 1521)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

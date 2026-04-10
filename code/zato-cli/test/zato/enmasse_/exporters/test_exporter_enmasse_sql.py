# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSQLExporter(TestCase):
    """ Tests exporting SQL connection definitions via ConfigStore round-trip.
    """

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name or item.get('security') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_sql_count(self) -> 'None':
        sql_list = self.exported['sql']
        self.assertEqual(len(sql_list), 2)

# ################################################################################################################################

    def test_sql_1(self) -> 'None':
        item = self._find(self.exported['sql'], 'enmasse.sql.1')
        self.assertEqual(item['type'], 'mysql')
        self.assertEqual(item['host'], '127.0.0.1')
        self.assertEqual(item['port'], 3306)
        self.assertEqual(item['db_name'], 'MYDB_01')
        self.assertEqual(item['username'], 'enmasse.1')

# ################################################################################################################################

    def test_sql_2(self) -> 'None':
        item = self._find(self.exported['sql'], 'enmasse.sql.2')
        self.assertEqual(item['type'], 'oracle')
        self.assertEqual(item['host'], '10.152.81.199')
        self.assertEqual(item['port'], 1521)
        self.assertEqual(item['db_name'], 'MYDB_01')
        self.assertEqual(item['username'], 'enmasse.2')
        self.assertEqual(item['extra'], 'connect_timeout=10')
        self.assertEqual(item['pool_size'], 10)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerImport(TestCase):

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_scheduler_count(self) -> 'None':
        scheduler_list = self.exported['scheduler']
        self.assertEqual(len(scheduler_list), 4)

# ################################################################################################################################

    def test_scheduler_1(self) -> 'None':
        item = self._find(self.exported['scheduler'], 'enmasse.scheduler.1')
        self.assertEqual(item['job_type'], 'interval_based')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['seconds'], 2)
        self.assertEqual(item['start_date'], '2025-01-11 11:23:52')

# ################################################################################################################################

    def test_scheduler_2(self) -> 'None':
        item = self._find(self.exported['scheduler'], 'enmasse.scheduler.2')
        self.assertEqual(item['job_type'], 'interval_based')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['minutes'], 51)

# ################################################################################################################################

    def test_scheduler_3(self) -> 'None':
        item = self._find(self.exported['scheduler'], 'enmasse.scheduler.3')
        self.assertEqual(item['job_type'], 'interval_based')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['hours'], 3)

# ################################################################################################################################

    def test_scheduler_4(self) -> 'None':
        item = self._find(self.exported['scheduler'], 'enmasse.scheduler.4')
        self.assertEqual(item['job_type'], 'interval_based')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['days'], 10)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_scheduler_preprocessing(self):

        template_dict = yaml.safe_load(template_complex_01)
        scheduler_items = template_dict['scheduler']

        preprocessed = SchedulerImporter.preprocess(scheduler_items)

        for item in preprocessed:
            self.assertIn('start_date', item)
            self.assertIn('job_type', item)

# ################################################################################################################################

    def test_scheduler_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('scheduler', exported)

        scheduler_list = exported['scheduler']
        scheduler_by_name = {item['name']: item for item in scheduler_list}

        self.assertIn('enmasse.scheduler.1', scheduler_by_name)
        self.assertIn('enmasse.scheduler.2', scheduler_by_name)
        self.assertIn('enmasse.scheduler.3', scheduler_by_name)
        self.assertIn('enmasse.scheduler.4', scheduler_by_name)

# ################################################################################################################################

    def test_scheduler_values(self):

        exported = self.config_store.export_to_dict()
        scheduler_list = exported['scheduler']
        scheduler_by_name = {item['name']: item for item in scheduler_list}

        s1 = scheduler_by_name['enmasse.scheduler.1']
        self.assertEqual(s1['service'], 'demo.ping')
        self.assertEqual(s1['job_type'], 'interval_based')
        self.assertEqual(s1['seconds'], 2)

        s2 = scheduler_by_name['enmasse.scheduler.2']
        self.assertEqual(s2['minutes'], 51)

        s3 = scheduler_by_name['enmasse.scheduler.3']
        self.assertEqual(s3['hours'], 3)

        s4 = scheduler_by_name['enmasse.scheduler.4']
        self.assertEqual(s4['days'], 10)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

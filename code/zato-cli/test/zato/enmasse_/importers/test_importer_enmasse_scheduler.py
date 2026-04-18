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
from zato.common.test.enmasse_._template_scheduler_01 import template_scheduler_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
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

class TestEnmasseSchedulerImportExtended(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_scheduler_01)

        exported = self.config_store.export_to_dict()
        self.scheduler_by_name = {item['name']: item for item in exported.get('scheduler', [])}

# ################################################################################################################################

    def test_all_jobs_imported(self):
        expected_names = [
            'enmasse.scheduler.one_time.1',
            'enmasse.scheduler.weeks.1',
            'enmasse.scheduler.repeats.1',
            'enmasse.scheduler.extra_list.1',
            'enmasse.scheduler.extra_string.1',
            'enmasse.scheduler.inactive.1',
            'enmasse.scheduler.future.1',
            'enmasse.scheduler.no_start_date.1',
        ]
        for name in expected_names:
            self.assertIn(name, self.scheduler_by_name, f'Job "{name}" not found after import')

# ################################################################################################################################

    def test_one_time_job_type(self):
        job = self.scheduler_by_name['enmasse.scheduler.one_time.1']
        self.assertEqual(job['job_type'], 'one_time')
        self.assertEqual(job['service'], 'demo.ping')

# ################################################################################################################################

    def test_weeks_interval(self):
        job = self.scheduler_by_name['enmasse.scheduler.weeks.1']
        self.assertEqual(job['job_type'], 'interval_based')
        self.assertEqual(job['weeks'], 2)

# ################################################################################################################################

    def test_repeats_field(self):
        job = self.scheduler_by_name['enmasse.scheduler.repeats.1']
        self.assertEqual(job['minutes'], 30)
        self.assertEqual(job['repeats'], 5)

# ################################################################################################################################

    def test_extra_list_joined(self):
        template_dict = yaml.safe_load(template_scheduler_01)
        scheduler_items = template_dict['scheduler']

        preprocessed = SchedulerImporter.preprocess(scheduler_items)
        extra_list_job = [j for j in preprocessed if j['name'] == 'enmasse.scheduler.extra_list.1'][0]

        self.assertIn('extra', extra_list_job)
        self.assertIsInstance(extra_list_job['extra'], str)
        self.assertIn('key1=value1', extra_list_job['extra'])
        self.assertIn('key2=value2', extra_list_job['extra'])
        self.assertIn('key3=value3', extra_list_job['extra'])

# ################################################################################################################################

    def test_extra_string_preserved(self):
        template_dict = yaml.safe_load(template_scheduler_01)
        scheduler_items = template_dict['scheduler']

        preprocessed = SchedulerImporter.preprocess(scheduler_items)
        extra_str_job = [j for j in preprocessed if j['name'] == 'enmasse.scheduler.extra_string.1'][0]

        self.assertEqual(extra_str_job['extra'], 'single_extra_value')

# ################################################################################################################################

    def test_inactive_job(self):
        job = self.scheduler_by_name['enmasse.scheduler.inactive.1']
        self.assertFalse(job['is_active'])
        self.assertEqual(job['days'], 7)

# ################################################################################################################################

    def test_no_start_date_job(self):
        job = self.scheduler_by_name['enmasse.scheduler.no_start_date.1']
        self.assertEqual(job['hours'], 4)
        self.assertEqual(job['service'], 'demo.ping')

# ################################################################################################################################

    def test_preprocess_does_not_modify_start_date(self):
        template_dict = yaml.safe_load(template_scheduler_01)
        scheduler_items = template_dict['scheduler']

        originals = {}
        for item in scheduler_items:
            originals[item['name']] = item.get('start_date')

        preprocessed = SchedulerImporter.preprocess(scheduler_items)

        for item in preprocessed:
            self.assertEqual(item.get('start_date'), originals[item['name']])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

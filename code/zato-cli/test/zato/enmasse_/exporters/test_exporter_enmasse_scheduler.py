# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import yaml
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.test.enmasse_._template_scheduler_01 import template_scheduler_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerExporter(TestCase):
    """ Tests exporting scheduler job definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

# ################################################################################################################################

    def test_scheduler_export(self):

        template_dict = yaml.safe_load(template_complex_01)
        scheduler_list_from_yaml = template_dict.get('scheduler', [])

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('scheduler', exported_data, 'Exporter did not produce a "scheduler" section.')
        exported_scheduler_list = exported_data['scheduler']

        yaml_scheduler_by_name = {item['name']: item for item in scheduler_list_from_yaml}
        exported_scheduler_by_name = {item['name']: item for item in exported_scheduler_list}

        for name in yaml_scheduler_by_name:
            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')

        for name, yaml_def in yaml_scheduler_by_name.items():

            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')
            exported_def = exported_scheduler_by_name[name]

            for field in ['name', 'is_active', 'job_type', 'service']:
                if field in yaml_def:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field),
                        f'Mismatch for "{field}" in scheduler job "{name}"')

            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']:
                if attr in yaml_def and yaml_def[attr] is not None:
                    self.assertEqual(exported_def.get(attr), yaml_def.get(attr),
                        f'Mismatch for interval attribute "{attr}" in scheduler job "{name}"')

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerExporterExtended(TestCase):
    """ Extended tests for scheduler export using the dedicated scheduler template.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        importer = EnmasseImporter(self.config_store)
        importer.import_(template_scheduler_01)

        self.exporter = EnmasseExporter(self.config_store)
        self.exported = self.exporter.export_to_dict()
        self.scheduler_list = self.exported.get('scheduler', [])
        self.by_name = {item['name']: item for item in self.scheduler_list}

# ################################################################################################################################

    def test_all_jobs_exported(self):
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
            self.assertIn(name, self.by_name, f'Job "{name}" not found in export')

# ################################################################################################################################

    def test_one_time_export(self):
        job = self.by_name['enmasse.scheduler.one_time.1']
        self.assertEqual(job['job_type'], 'one_time')
        self.assertEqual(job['service'], 'demo.ping')
        self.assertTrue(job['is_active'])

# ################################################################################################################################

    def test_weeks_export(self):
        job = self.by_name['enmasse.scheduler.weeks.1']
        self.assertEqual(job['weeks'], 2)

# ################################################################################################################################

    def test_repeats_export(self):
        job = self.by_name['enmasse.scheduler.repeats.1']
        self.assertEqual(job['minutes'], 30)
        self.assertEqual(job['repeats'], 5)

# ################################################################################################################################

    def test_extra_exported(self):
        job = self.by_name['enmasse.scheduler.extra_list.1']
        self.assertIn('extra', job)
        self.assertIn('key1=value1', job['extra'])

# ################################################################################################################################

    def test_extra_string_exported(self):
        job = self.by_name['enmasse.scheduler.extra_string.1']
        self.assertIn('extra', job)
        self.assertEqual(job['extra'], 'single_extra_value')

# ################################################################################################################################

    def test_inactive_exported(self):
        job = self.by_name['enmasse.scheduler.inactive.1']
        self.assertFalse(job['is_active'])

# ################################################################################################################################

    def test_future_start_date_exported(self):
        job = self.by_name['enmasse.scheduler.future.1']
        self.assertIn('start_date', job)
        self.assertIn('2099', job['start_date'])

# ################################################################################################################################

    def test_required_fields_present(self):
        for name, job in self.by_name.items():
            self.assertIn('name', job, f'Missing "name" in job "{name}"')
            self.assertIn('service', job, f'Missing "service" in job "{name}"')
            self.assertIn('job_type', job, f'Missing "job_type" in job "{name}"')
            self.assertIn('is_active', job, f'Missing "is_active" in job "{name}"')

# ################################################################################################################################

    def test_export_count(self):
        template_dict = yaml.safe_load(template_scheduler_01)
        expected_count = len(template_dict['scheduler'])
        self.assertEqual(len(self.scheduler_list), expected_count)

# ################################################################################################################################

    def test_no_start_date_job_exported(self):
        job = self.by_name['enmasse.scheduler.no_start_date.1']
        self.assertEqual(job['hours'], 4)
        self.assertEqual(job['service'], 'demo.ping')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

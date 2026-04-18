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
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerEdgeCasesMissingFields(TestCase):
    """ Verify behaviour when YAML jobs omit optional or required-looking fields.
    """

# ################################################################################################################################

    def test_minimal_job_name_only(self):
        """ Only name is truly required by the Rust model; everything else has serde defaults. """
        yaml_str = """
scheduler:
  - name: edge.minimal.1
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)

        exported = store.export_to_dict()
        by_name = {item['name']: item for item in exported.get('scheduler', [])}

        self.assertIn('edge.minimal.1', by_name)

        job = by_name['edge.minimal.1']
        self.assertEqual(job['service'], '')
        self.assertEqual(job['job_type'], 'interval_based')
        self.assertTrue(job['is_active'])

# ################################################################################################################################

    def test_missing_service_defaults_empty(self):
        yaml_str = """
scheduler:
  - name: edge.no_service.1
    job_type: interval_based
    minutes: 5
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.no_service.1']
        self.assertEqual(job['service'], '')

# ################################################################################################################################

    def test_missing_job_type_defaults_interval_based(self):
        yaml_str = """
scheduler:
  - name: edge.no_job_type.1
    service: demo.ping
    minutes: 10
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.no_job_type.1']
        self.assertEqual(job['job_type'], 'interval_based')

# ################################################################################################################################

    def test_no_interval_fields_all_zero(self):
        yaml_str = """
scheduler:
  - name: edge.no_intervals.1
    service: demo.ping
    job_type: interval_based
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.no_intervals.1']

        for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
            self.assertFalse(job.get(attr), f'{attr} should be zero/absent for a job with no intervals')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerEdgeCasesDuplicateNames(TestCase):
    """ Verify that importing jobs with duplicate names results in the last one winning.
    """

    def test_duplicate_name_last_wins(self):
        yaml_str = """
scheduler:
  - name: edge.dup.1
    service: demo.ping
    job_type: interval_based
    minutes: 5

  - name: edge.dup.1
    service: demo.echo
    job_type: one_time
    hours: 99
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        jobs = [item for item in exported['scheduler'] if item['name'] == 'edge.dup.1']

        self.assertEqual(len(jobs), 1, 'Duplicate name should result in a single stored job')
        self.assertEqual(jobs[0]['service'], 'demo.echo')
        self.assertEqual(jobs[0]['job_type'], 'one_time')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerEdgeCasesInvalidYaml(TestCase):
    """ Verify that malformed YAML or structurally invalid data raises errors.
    """

    def test_extra_as_nested_dict_raises(self):
        yaml_str = """
scheduler:
  - name: edge.bad_extra.1
    service: demo.ping
    job_type: interval_based
    extra:
      nested_key: nested_value
"""
        store = ConfigManager()
        with self.assertRaises(ValueError):
            EnmasseImporter(store).import_(yaml_str)

# ################################################################################################################################

    def test_name_as_integer_converted(self):
        """ YAML will parse an unquoted integer; verify it still stores correctly as a string. """
        yaml_str = """
scheduler:
  - name: 12345
    service: demo.ping
    job_type: interval_based
    seconds: 60
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        names = [item['name'] for item in exported.get('scheduler', [])]
        self.assertIn('12345', names)

# ################################################################################################################################

    def test_empty_scheduler_section_no_error(self):
        """ YAML `scheduler:` with no items parses as None; importer should handle it gracefully. """
        yaml_str = """
scheduler:
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        self.assertEqual(len(exported.get('scheduler', [])), 0)

# ################################################################################################################################

    def test_scheduler_section_empty_list(self):
        yaml_str = """
scheduler: []
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        self.assertEqual(len(exported.get('scheduler', [])), 0)

# ################################################################################################################################

    def test_unknown_job_type_stored_as_is(self):
        """ An unrecognized job_type string should be stored and exported without error. """
        yaml_str = """
scheduler:
  - name: edge.unknown_type.1
    service: demo.ping
    job_type: invalid
    seconds: 30
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)
        exported = store.export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.unknown_type.1']
        self.assertEqual(job['job_type'], 'invalid')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerEdgeCasesPreprocess(TestCase):
    """ Edge cases for SchedulerImporter.preprocess specifically.
    """

    def test_empty_list_returns_empty(self):
        result = SchedulerImporter.preprocess([])
        self.assertEqual(result, [])

# ################################################################################################################################

    def test_extra_empty_list_becomes_empty_string(self):
        items = [{'name': 'x', 'extra': []}]
        result = SchedulerImporter.preprocess(items)
        self.assertEqual(result[0]['extra'], '')

# ################################################################################################################################

    def test_extra_list_with_none_elements_filtered(self):
        items = [{'name': 'x', 'extra': ['a=1', None, 'b=2', None]}]
        result = SchedulerImporter.preprocess(items)
        self.assertEqual(result[0]['extra'], 'a=1\nb=2')

# ################################################################################################################################

    def test_extra_integer_converted_to_string(self):
        items = [{'name': 'x', 'extra': [123, 456]}]
        result = SchedulerImporter.preprocess(items)
        self.assertEqual(result[0]['extra'], '123\n456')

# ################################################################################################################################

    def test_preprocess_preserves_unknown_fields(self):
        items = [{'name': 'x', 'custom_field': 'custom_value'}]
        result = SchedulerImporter.preprocess(items)
        self.assertEqual(result[0]['custom_field'], 'custom_value')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerEdgeCasesExportRoundTrip(TestCase):
    """ Edge cases for the export side of the round trip.
    """

    def test_export_empty_store(self):
        store = ConfigManager()
        exporter = EnmasseExporter(store)
        exported = exporter.export_to_dict()
        self.assertEqual(len(exported.get('scheduler', [])), 0)

# ################################################################################################################################

    def test_many_jobs_all_survive(self):
        jobs = []
        for i in range(50):
            jobs.append({
                'name': f'edge.bulk.{i}',
                'service': 'demo.ping',
                'job_type': 'interval_based',
                'seconds': i + 1,
            })

        yaml_str = yaml.dump({'scheduler': jobs})
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)

        exporter = EnmasseExporter(store)
        exported = exporter.export_to_dict()
        exported_names = {item['name'] for item in exported.get('scheduler', [])}

        for i in range(50):
            self.assertIn(f'edge.bulk.{i}', exported_names)

# ################################################################################################################################

    def test_is_active_false_explicit_survives_export(self):
        yaml_str = """
scheduler:
  - name: edge.inactive_explicit.1
    service: demo.ping
    job_type: interval_based
    is_active: false
    hours: 1
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)

        exported = EnmasseExporter(store).export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.inactive_explicit.1']
        self.assertFalse(job['is_active'])

# ################################################################################################################################

    def test_all_interval_units_together(self):
        yaml_str = """
scheduler:
  - name: edge.all_units.1
    service: demo.ping
    job_type: interval_based
    weeks: 1
    days: 2
    hours: 3
    minutes: 4
    seconds: 5
"""
        store = ConfigManager()
        EnmasseImporter(store).import_(yaml_str)

        exported = EnmasseExporter(store).export_to_dict()
        job = {item['name']: item for item in exported['scheduler']}['edge.all_units.1']
        self.assertEqual(job['weeks'], 1)
        self.assertEqual(job['days'], 2)
        self.assertEqual(job['hours'], 3)
        self.assertEqual(job['minutes'], 4)
        self.assertEqual(job['seconds'], 5)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

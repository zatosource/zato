# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.test.enmasse_._template_scheduler_01 import template_scheduler_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerRoundTripComplex(TestCase):
    """ Import template_complex_01 via enmasse, export back, and verify scheduler fields survive the round trip.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        importer = EnmasseImporter(self.config_store)
        importer.import_(template_complex_01)

        exporter = EnmasseExporter(self.config_store)
        self.exported = exporter.export_to_dict()
        self.exported_by_name = {item['name']: item for item in self.exported.get('scheduler', [])}

        self.input_by_name = {item['name']: item for item in yaml.safe_load(template_complex_01)['scheduler']}

# ################################################################################################################################

    def test_all_input_jobs_present_in_export(self):
        for name in self.input_by_name:
            self.assertIn(name, self.exported_by_name, f'Job "{name}" lost during round trip')

# ################################################################################################################################

    def test_no_extra_jobs_in_export(self):
        self.assertEqual(len(self.input_by_name), len(self.exported_by_name))

# ################################################################################################################################

    def test_core_fields_survive(self):
        for name, inp in self.input_by_name.items():
            out = self.exported_by_name[name]
            self.assertEqual(out['service'], inp['service'], f'{name}: service mismatch')
            self.assertEqual(out['job_type'], inp['job_type'], f'{name}: job_type mismatch')

# ################################################################################################################################

    def test_interval_fields_survive(self):
        for name, inp in self.input_by_name.items():
            out = self.exported_by_name[name]
            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
                if attr in inp and inp[attr]:
                    self.assertEqual(out.get(attr), inp[attr],
                        f'{name}: {attr} mismatch (input={inp[attr]}, export={out.get(attr)})')

# ################################################################################################################################

    def test_is_active_survives(self):
        for name, inp in self.input_by_name.items():
            out = self.exported_by_name[name]
            expected_active = inp.get('is_active', True)
            self.assertEqual(out['is_active'], expected_active, f'{name}: is_active mismatch')

# ################################################################################################################################

    def test_re_import_produces_identical_export(self):
        """ Export -> re-import -> export again; the two exports must match. """
        exporter1 = EnmasseExporter(self.config_store)
        yaml_str = exporter1.export()

        config_store2 = ConfigStore()
        importer2 = EnmasseImporter(config_store2)
        importer2.import_(yaml_str)

        exporter2 = EnmasseExporter(config_store2)
        exported2 = exporter2.export_to_dict()

        by_name_1 = {item['name']: item for item in self.exported.get('scheduler', [])}
        by_name_2 = {item['name']: item for item in exported2.get('scheduler', [])}

        self.assertEqual(set(by_name_1.keys()), set(by_name_2.keys()))

        for name in by_name_1:
            for field in ['service', 'job_type', 'is_active']:
                self.assertEqual(by_name_1[name].get(field), by_name_2[name].get(field),
                    f'Double round-trip mismatch: {name}.{field}')
            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']:
                self.assertEqual(by_name_1[name].get(attr), by_name_2[name].get(attr),
                    f'Double round-trip mismatch: {name}.{attr}')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerRoundTripExtended(TestCase):
    """ Import template_scheduler_01 via enmasse, export back, verify field fidelity.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        importer = EnmasseImporter(self.config_store)
        importer.import_(template_scheduler_01)

        exporter = EnmasseExporter(self.config_store)
        self.exported = exporter.export_to_dict()
        self.exported_by_name = {item['name']: item for item in self.exported.get('scheduler', [])}

        self.input_by_name = {item['name']: item for item in yaml.safe_load(template_scheduler_01)['scheduler']}

# ################################################################################################################################

    def test_count_matches(self):
        self.assertEqual(len(self.input_by_name), len(self.exported_by_name))

# ################################################################################################################################

    def test_one_time_round_trip(self):
        inp = self.input_by_name['enmasse.scheduler.one_time.1']
        out = self.exported_by_name['enmasse.scheduler.one_time.1']
        self.assertEqual(out['job_type'], 'one_time')
        self.assertEqual(out['service'], inp['service'])
        self.assertTrue(out['is_active'])

# ################################################################################################################################

    def test_weeks_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.weeks.1']
        self.assertEqual(out['weeks'], 2)
        self.assertEqual(out['job_type'], 'interval_based')

# ################################################################################################################################

    def test_repeats_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.repeats.1']
        self.assertEqual(out['minutes'], 30)
        self.assertEqual(out['repeats'], 5)

# ################################################################################################################################

    def test_extra_list_becomes_string_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.extra_list.1']
        self.assertIn('extra', out)
        self.assertIsInstance(out['extra'], str)
        self.assertIn('key1=value1', out['extra'])
        self.assertIn('key2=value2', out['extra'])
        self.assertIn('key3=value3', out['extra'])

# ################################################################################################################################

    def test_extra_string_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.extra_string.1']
        self.assertEqual(out['extra'], 'single_extra_value')

# ################################################################################################################################

    def test_inactive_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.inactive.1']
        self.assertFalse(out['is_active'])
        self.assertEqual(out['days'], 7)

# ################################################################################################################################

    def test_future_start_date_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.future.1']
        self.assertIn('2099', out['start_date'])

# ################################################################################################################################

    def test_no_start_date_round_trip(self):
        out = self.exported_by_name['enmasse.scheduler.no_start_date.1']
        self.assertEqual(out['hours'], 4)
        self.assertEqual(out['service'], 'demo.ping')

# ################################################################################################################################

    def test_double_round_trip_stability(self):
        """ Export -> re-import -> export; verify scheduler section is stable. """
        yaml_str = EnmasseExporter(self.config_store).export()

        store2 = ConfigStore()
        EnmasseImporter(store2).import_(yaml_str)

        exported2 = EnmasseExporter(store2).export_to_dict()
        by_name_2 = {item['name']: item for item in exported2.get('scheduler', [])}

        self.assertEqual(set(self.exported_by_name.keys()), set(by_name_2.keys()))

        for name in self.exported_by_name:
            e1 = self.exported_by_name[name]
            e2 = by_name_2[name]

            for field in ['service', 'job_type', 'is_active', 'start_date']:
                self.assertEqual(e1.get(field), e2.get(field),
                    f'Double round-trip diverged: {name}.{field}')

            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'extra']:
                self.assertEqual(e1.get(attr), e2.get(attr),
                    f'Double round-trip diverged: {name}.{attr}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

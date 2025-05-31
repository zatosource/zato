# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerExporter(TestCase):
    """ Tests exporting scheduler job definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.scheduler_importer = SchedulerImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_scheduler_export(self):
        self._setup_test_environment()

        # 1. Get scheduler job definitions from the YAML template
        scheduler_list_from_yaml = self.yaml_config.get('scheduler', [])

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_scheduler_jobs, _ = self.scheduler_importer.sync_job_definitions(scheduler_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_scheduler_jobs) > 0, 'No scheduler jobs were created from YAML.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('scheduler', exported_data, 'Exporter did not produce a "scheduler" section.')
        exported_scheduler_list = exported_data['scheduler']

        # 4. Compare exported data with the original YAML data
        # Create dictionaries keyed by name for easier comparison
        yaml_scheduler_by_name = {item['name']: item for item in scheduler_list_from_yaml}
        exported_scheduler_by_name = {item['name']: item for item in exported_scheduler_list}

        # Check that all jobs from our YAML template were exported (there may be additional jobs in the DB)
        for name in yaml_scheduler_by_name:
            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')

        for name, yaml_def in yaml_scheduler_by_name.items():

            self.assertIn(name, exported_scheduler_by_name, f'Scheduler job "{name}" from YAML not found in export.')
            exported_def = exported_scheduler_by_name[name]

            # Compare fields that are expected to be exported by SchedulerExporter
            for field in ['name', 'is_active', 'job_type', 'service']:
                if field in yaml_def:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field), f'Mismatch for "{field}" in scheduler job "{name}"')

            # Check interval-based attributes
            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']:
                if attr in yaml_def and yaml_def[attr] is not None:
                    self.assertEqual(exported_def.get(attr), yaml_def.get(attr), f'Mismatch for interval attribute "{attr}" in scheduler job "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

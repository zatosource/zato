# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.common.odb.model import IntervalBasedJob, Job
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerFromYAML(TestCase):
    """ Tests importing Scheduler definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.scheduler_importer = self.importer.scheduler_importer

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

    def test_yaml_job_parsing(self):
        """ Test that scheduler job definitions in YAML are parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML contains scheduler job definitions
        self.assertIn('scheduler', self.yaml_config)
        self.assertIsInstance(self.yaml_config['scheduler'], list)
        self.assertEqual(len(self.yaml_config['scheduler']), 4, 'Expected 4 scheduler job definitions in YAML')

    def test_job_definition_creation(self):
        """ Test creating scheduler job definitions from YAML.
        """
        self._setup_test_environment()

        # Get job definitions from YAML
        job_defs = self.yaml_config.get('scheduler', [])
        self.assertTrue(len(job_defs) > 0, 'No scheduler job definitions found in YAML')

        # Process job definitions
        job_created, _ = self.scheduler_importer.sync_job_definitions(job_defs, self.session)

        # Update importer's job definitions for other tests
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Assert the correct number of items were created
        self.assertEqual(len(job_created), len(job_defs), 'Not all scheduler job definitions were created')

        # Verify each definition was created correctly
        for instance in job_created:
            self.assertTrue(instance.name.startswith('enmasse.scheduler.'))
            self.assertEqual(instance.job_type, 'interval_based')
            self.assertTrue(instance.is_active)
            self.assertIsNotNone(instance.service_id)

            # Check if it's an interval based job
            if instance.job_type == 'interval_based':
                self.assertIsNotNone(instance.interval_based)

    def test_job_comparison(self):
        """ Test comparing scheduler job definitions between YAML and database.
        """
        self._setup_test_environment()

        # Get job definitions from YAML
        job_defs = self.yaml_config.get('scheduler', [])
        self.assertTrue(len(job_defs) > 0, 'No scheduler job definitions found in YAML')

        # Get job definitions from database (initially empty)
        db_defs = self.scheduler_importer.get_job_defs_from_db(self.session, self.importer.cluster_id)

        # Compare the definitions
        to_create, to_update = self.scheduler_importer.compare_job_defs(job_defs, db_defs)

        # All should be marked for creation since the database is empty
        self.assertEqual(len(to_create), len(job_defs))
        self.assertEqual(len(to_update), 0)

        # Create the job definitions
        _ = self.scheduler_importer.sync_job_definitions(job_defs, self.session)
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Get job definitions from database again (now should have the created items)
        db_defs = self.scheduler_importer.get_job_defs_from_db(self.session, self.importer.cluster_id)

        # Compare the definitions again
        to_create, to_update = self.scheduler_importer.compare_job_defs(job_defs, db_defs)

        # Now none should be marked for creation, all should be for update
        self.assertEqual(len(to_create), 0)
        self.assertEqual(len(to_update), len(job_defs))

    def test_job_update(self):
        """ Test updating existing scheduler job definitions.
        """
        self._setup_test_environment()

        # Get job definition from YAML
        job_defs = self.yaml_config['scheduler']
        job_def = job_defs[0]

        # Create the job definition
        instance = self.scheduler_importer.create_job_definition(job_def, self.session)
        self.session.commit()
        original_name = job_def['name']
        self.assertEqual(instance.name, original_name)

        # Update the job definition
        update_def = {
            'name': original_name,
            'id': instance.id,
            'minutes': 15,  # Changed from 5 to 15
            'is_active': False  # Changed from True to False
        }

        updated_instance = self.scheduler_importer.update_job_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertFalse(updated_instance.is_active)
        if updated_instance.interval_based:
            self.assertEqual(updated_instance.interval_based.minutes, 15)

    def test_complete_job_import_flow(self):
        """ Test the complete flow of importing scheduler job definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all job definitions from the YAML
        job_list = self.yaml_config.get('scheduler', [])
        job_created, job_updated = self.scheduler_importer.sync_job_definitions(job_list, self.session)

        # Update importer's job definitions
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Verify job definitions were created
        self.assertEqual(len(job_created), len(job_list))
        self.assertEqual(len(job_updated), 0)

        # Verify the job definitions dictionary was populated
        self.assertEqual(len(self.scheduler_importer.job_defs), len(job_list))

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.job_defs), len(job_list))

        # Try importing the same definitions again - should result in updates, not creations
        job_created2, job_updated2 = self.scheduler_importer.sync_job_definitions(job_list, self.session)
        self.assertEqual(len(job_created2), 0)
        self.assertEqual(len(job_updated2), len(job_list))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

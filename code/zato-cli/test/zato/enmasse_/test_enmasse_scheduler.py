# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
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
        """ Clean up test environment.
        """
        # Make sure the session is closed properly
        if self.session:
            try:
                self.session.close()
            except:
                pass

        # Use the global cleanup method
        cleanup_enmasse()
        os.unlink(self.temp_file.name)

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        # Close any existing session first
        if self.session:
            try:
                self.session.close()
            except:
                pass

        # Always create a fresh session
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

        # Check for existing jobs before syncing
        from zato.common.odb.model import Job
        cluster_id = 1  # Default test cluster ID

        # Count existing jobs that match our test patterns
        existing_count = self.session.query(Job).filter(
            Job.name.in_([j['name'] for j in job_defs])
        ).filter(Job.cluster_id==cluster_id).count()

        # Process job definitions
        job_created, job_updated = self.scheduler_importer.sync_job_definitions(job_defs, self.session)

        # Update importer's job definitions for other tests
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Expected: create new ones, update existing ones
        expected_created = len(job_defs) - existing_count
        expected_updated = existing_count

        # Assert the correct number of items were created/updated
        self.assertEqual(len(job_created), expected_created, 'Wrong number of job definitions created')
        self.assertEqual(len(job_updated), expected_updated, 'Wrong number of job definitions updated')

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

        # Database might not be empty from previous tests, so check actual content
        expected_to_create = []
        expected_to_update = []

        for job in job_defs:
            if job['name'] in db_defs:
                expected_to_update.append(job['name'])
            else:
                expected_to_create.append(job['name'])

        self.assertEqual(len(to_create), len(expected_to_create))
        self.assertEqual(len(to_update), len(expected_to_update))

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

        # Get required objects for creating a job
        from zato.common.odb.model import Job, Cluster, Service
        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        service = self.session.query(Service).filter(Service.name==job_def['service']).filter(Service.cluster_id==cluster.id).first()

        # Create a job object directly
        from datetime import datetime
        job = Job()
        job.name = job_def['name']
        job.is_active = True
        job.job_type = 'interval_based'
        job.start_date = datetime.strptime(job_def['start_date'], '%Y-%m-%d %H:%M:%S')
        job.cluster = cluster
        job.service = service

        # Add and commit
        self.session.add(job)
        self.session.commit()

        # Job should now exist with an ID
        self.assertIsNotNone(job.id)

        # Update the job definition
        update_def = {
            'name': job_def['name'],
            'id': job.id,
            'minutes': 15,  # Changed from original value
            'is_active': False  # Changed from original value
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

        # Get job definitions from database first to determine expected behavior
        from zato.common.odb.model import Job
        cluster_id = 1  # Default test cluster ID

        # Count existing jobs that match our test patterns
        existing_count = self.session.query(Job).filter(
            Job.name.in_([item['name'] for item in self.yaml_config.get('scheduler', [])]) # type: ignore
        ).filter(Job.cluster_id==cluster_id).count()

        # Process all job definitions from the YAML
        job_list = self.yaml_config.get('scheduler', [])
        job_created, job_updated = self.scheduler_importer.sync_job_definitions(job_list, self.session)

        # Update importer's job definitions
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Determine expected counts based on existing records
        expected_created = len(job_list) - existing_count
        expected_updated = existing_count

        # Verify job definitions were created/updated appropriately
        self.assertEqual(len(job_created), expected_created)
        self.assertEqual(len(job_updated), expected_updated)

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

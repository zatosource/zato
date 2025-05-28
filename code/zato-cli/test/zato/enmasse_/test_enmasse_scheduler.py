# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
import tempfile
from datetime import datetime
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.common.api import SCHEDULER
from zato.common.odb.model import Cluster, IntervalBasedJob, Job, Service
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerFromYAML(TestCase):
    """ Tests importing Scheduler definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains scheduler job definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize scheduler importer
        self.scheduler_importer = SchedulerImporter(self.importer)

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

    def test_create_job_object(self):
        """ Test the basic creation of a scheduler job object in the database.
        """
        self._setup_test_environment()

        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        service = self.session.query(Service).filter(Service.name=='zato.ping').filter(Service.cluster_id==cluster.id).one()

        job = Job()
        job.cluster = cluster
        job.service = service
        job.name = 'enmasse.job.test.basic'
        job.is_active = True
        job.job_type = SCHEDULER.JOB_TYPE.INTERVAL_BASED
        job.start_date = datetime.utcnow()
        job.extra = ''

        self.session.add(job)
        self.session.flush()

        interval_job = IntervalBasedJob()
        interval_job.job = job
        interval_job.weeks = 0
        interval_job.days = 0
        interval_job.hours = 1
        interval_job.minutes = 0
        interval_job.seconds = 0
        interval_job.repeats = 0

        self.session.add(interval_job)
        self.session.commit()

        # Query to verify it was created
        result = self.session.query(Job).filter_by(name='enmasse.job.test.basic').one()
        self.assertEqual(result.name, 'enmasse.job.test.basic')

        # Verify interval job was created
        interval_result = self.session.query(IntervalBasedJob).filter_by(job_id=result.id).one()
        self.assertEqual(interval_result.hours, 1)

    def test_yaml_job_parsing(self):
        """ Test that scheduler job definitions in YAML are parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML contains scheduler definitions
        self.assertIn('scheduler', self.yaml_config)
        job_defs = self.yaml_config['scheduler']
        self.assertEqual(len(job_defs), 4)  # There are 4 scheduler jobs in the template

        # Check the first definition
        job_def = job_defs[0]
        self.assertEqual(job_def['name'], 'enmasse.scheduler.1')
        self.assertEqual(job_def['service'], 'demo.ping')
        self.assertEqual(job_def['job_type'], 'interval_based')
        self.assertEqual(job_def['seconds'], 2)
        self.assertEqual(job_def['start_date'], '2025-01-11 11:23:52')

        # Check the second definition
        job_def = job_defs[1]
        self.assertEqual(job_def['name'], 'enmasse.scheduler.2')
        self.assertEqual(job_def['service'], 'demo.ping')
        self.assertEqual(job_def['job_type'], 'interval_based')
        self.assertEqual(job_def['minutes'], 51)

    def test_job_definition_creation(self):
        """ Test creating scheduler job definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        job_defs = self.yaml_config['scheduler']

        # Process all scheduler job definitions
        created, updated = self.scheduler_importer.sync_job_definitions(job_defs, self.session)

        # Should have created 4 definitions
        self.assertEqual(len(created), 4)
        self.assertEqual(len(updated), 0)

        # Verify first job was created correctly
        job = self.session.query(Job).filter_by(name='enmasse.scheduler.1').one()
        self.assertEqual(job.job_type, SCHEDULER.JOB_TYPE.INTERVAL_BASED)

        # Verify interval job was created correctly
        interval_job = self.session.query(IntervalBasedJob).filter_by(job_id=job.id).one()
        self.assertEqual(interval_job.seconds, 2)

        # Verify second job was created correctly
        job = self.session.query(Job).filter_by(name='enmasse.scheduler.2').one()
        self.assertEqual(job.job_type, SCHEDULER.JOB_TYPE.INTERVAL_BASED)

        # Verify interval job was created correctly
        interval_job = self.session.query(IntervalBasedJob).filter_by(job_id=job.id).one()
        self.assertEqual(interval_job.minutes, 51)

    def test_job_update(self):
        """ Test updating existing scheduler job definitions.
        """
        self._setup_test_environment()

        # First, get the job definition from YAML and create it
        job_defs = self.yaml_config['scheduler']
        job_def = job_defs[0]  # First job has seconds=2

        # Create the job definition
        instance = self.scheduler_importer.create_job_definition(job_def, self.session)
        self.session.commit()
        original_seconds = 2

        # Verify interval job was created with original seconds
        interval_job = self.session.query(IntervalBasedJob).filter_by(job_id=instance.id).one()
        self.assertEqual(interval_job.seconds, original_seconds)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': job_def['name'],
            'id': instance.id,
            'seconds': 5,  # Changed seconds
            'minutes': 30  # Added minutes
        }

        # Update the job definition
        updated_instance = self.scheduler_importer.update_job_definition(update_def, self.session)
        self.session.commit()

        # Verify the interval job was updated
        updated_interval = self.session.query(IntervalBasedJob).filter_by(job_id=updated_instance.id).one()
        self.assertEqual(updated_interval.seconds, 5)
        self.assertEqual(updated_interval.minutes, 30)

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
        self.assertEqual(len(job_created), 4)
        self.assertEqual(len(job_updated), 0)

        # Verify the job definitions dictionary was populated
        self.assertEqual(len(self.scheduler_importer.job_defs), 4)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.job_defs), 4)

        # Try importing the same definitions again - should result in updates, not creations
        job_created2, job_updated2 = self.scheduler_importer.sync_job_definitions(job_list, self.session)
        self.assertEqual(len(job_created2), 0)
        self.assertEqual(len(job_updated2), 4)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Sample YAML template with scheduler definitions
template_scheduler = """
scheduler:

  - name: enmasse.scheduler.1
    service: zato.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 2
    is_active: true

  - name: enmasse.scheduler.2
    service: zato.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 51

  - name: enmasse.scheduler.3
    service: zato.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 3

  - name: enmasse.scheduler.4
    service: zato.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 10
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSchedulerFromYAML(TestCase):
    """ Tests importing Scheduler definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file with scheduler definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_scheduler.encode('utf-8'))
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

    def test_create_scheduler_job_object(self):
        """ Test the basic creation of a scheduler job object in the database.
        """
        self._setup_test_environment()

        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        cluster.id = 1

        # Create a service for the job
        service = self.session.query(Service).filter(Service.name=='zato.ping').first()
        if not service:
            service = Service()
            service.name = 'zato.ping'
            service.is_active = True
            service.impl_name = 'zato.server.service.internal.Ping'
            service.is_internal = True
            service.cluster = cluster
            self.session.add(service)
            self.session.flush()

        # Create job
        job = Job()
        job.name = 'test.scheduler.basic'
        job.is_active = True
        job.job_type = SCHEDULER.JOB_TYPE.INTERVAL_BASED
        job.start_date = datetime.now()
        job.cluster = cluster
        job.service = service
        job.extra = ''

        self.session.add(job)
        self.session.flush()

        # Create interval-based job
        ib_job = IntervalBasedJob()
        ib_job.job = job
        ib_job.minutes = 5
        
        self.session.add(ib_job)
        self.session.commit()

        # Query to verify it was created
        result = self.session.query(Job).filter_by(name='test.scheduler.basic').one()
        self.assertEqual(result.name, 'test.scheduler.basic')
        self.assertEqual(result.interval_based.minutes, 5)

    def test_yaml_scheduler_parsing(self):
        """ Test that Scheduler definitions in YAML are parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML contains scheduler definitions
        self.assertIn('scheduler', self.yaml_config)
        scheduler_defs = self.yaml_config['scheduler']
        self.assertEqual(len(scheduler_defs), 4)

        # Check the definitions
        seconds_job = scheduler_defs[0]
        self.assertEqual(seconds_job['name'], 'enmasse.scheduler.1')
        self.assertEqual(seconds_job['service'], 'zato.ping')
        self.assertEqual(seconds_job['seconds'], 2)
        
        minutes_job = scheduler_defs[1]
        self.assertEqual(minutes_job['name'], 'enmasse.scheduler.2')
        self.assertEqual(minutes_job['minutes'], 51)
        
        hours_job = scheduler_defs[2]
        self.assertEqual(hours_job['name'], 'enmasse.scheduler.3')
        self.assertEqual(hours_job['hours'], 3)
        
        days_job = scheduler_defs[3]
        self.assertEqual(days_job['name'], 'enmasse.scheduler.4')
        self.assertEqual(days_job['days'], 10)

    def test_scheduler_definition_creation(self):
        """ Test creating Scheduler definitions from YAML.
        """
        self._setup_test_environment()
        
        # Create a service for the job
        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        service = self.session.query(Service).filter(Service.name=='zato.ping').first()
        if not service:
            service = Service()
            service.name = 'zato.ping'
            service.is_active = True
            service.impl_name = 'zato.server.service.internal.Ping'
            service.is_internal = True
            service.cluster = cluster
            self.session.add(service)
            self.session.commit()

        # Get definitions from YAML
        scheduler_defs = self.yaml_config['scheduler']

        # Process all Scheduler definitions
        created, updated = self.scheduler_importer.sync_scheduler_jobs(scheduler_defs, self.session)

        # Should have created 4 definitions
        self.assertEqual(len(created), 4)
        self.assertEqual(len(updated), 0)

        # Verify the seconds-based job was created correctly
        seconds_job = self.session.query(Job).filter_by(name='enmasse.scheduler.1').one()
        self.assertEqual(seconds_job.service.name, 'zato.ping')
        self.assertEqual(seconds_job.interval_based.seconds, 2)
        self.assertEqual(seconds_job.interval_based.minutes, None)
        self.assertEqual(seconds_job.interval_based.hours, None)
        self.assertEqual(seconds_job.interval_based.days, None)
        
        # Verify the minutes-based job was created correctly
        minutes_job = self.session.query(Job).filter_by(name='enmasse.scheduler.2').one()
        self.assertEqual(minutes_job.interval_based.minutes, 51)
        self.assertEqual(minutes_job.interval_based.seconds, None)
        
        # Verify the hours-based job was created correctly
        hours_job = self.session.query(Job).filter_by(name='enmasse.scheduler.3').one()
        self.assertEqual(hours_job.interval_based.hours, 3)
        
        # Verify the days-based job was created correctly
        days_job = self.session.query(Job).filter_by(name='enmasse.scheduler.4').one()
        self.assertEqual(days_job.interval_based.days, 10)

    def test_scheduler_update(self):
        """ Test updating existing Scheduler definitions.
        """
        self._setup_test_environment()

        # Create a service for the job
        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        service = self.session.query(Service).filter(Service.name=='zato.ping').first()
        if not service:
            service = Service()
            service.name = 'zato.ping'
            service.is_active = True
            service.impl_name = 'zato.server.service.internal.Ping'
            service.is_internal = True
            service.cluster = cluster
            self.session.add(service)
            self.session.commit()

        # First, get a scheduler definition from YAML and create it
        scheduler_defs = self.yaml_config['scheduler']
        job_def = scheduler_defs[0]

        # Create the scheduler job
        instance = self.scheduler_importer.create_job_definition(job_def, self.session)
        self.session.commit()
        original_seconds = job_def['seconds']
        self.assertEqual(instance.interval_based.seconds, original_seconds)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': job_def['name'],
            'id': instance.id,
            'seconds': 30,  # Changed seconds
            'is_active': False  # Changed is_active
        }

        # Update the scheduler job
        updated_instance = self.scheduler_importer.update_job_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.interval_based.seconds, 30)
        self.assertEqual(updated_instance.is_active, False)

        # Make sure other fields were preserved from the original YAML definition
        self.assertEqual(updated_instance.service.name, job_def['service'])

    def test_complete_scheduler_import_flow(self):
        """ Test the complete flow of importing Scheduler definitions from a YAML file.
        """
        self._setup_test_environment()

        # Create a service for the job
        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        service = self.session.query(Service).filter(Service.name=='zato.ping').first()
        if not service:
            service = Service()
            service.name = 'zato.ping'
            service.is_active = True
            service.impl_name = 'zato.server.service.internal.Ping'
            service.is_internal = True
            service.cluster = cluster
            self.session.add(service)
            self.session.commit()

        # Process all Scheduler definitions from the YAML
        scheduler_list = self.yaml_config.get('scheduler', [])
        scheduler_created, scheduler_updated = self.scheduler_importer.sync_scheduler_jobs(scheduler_list, self.session)

        # Update importer's Scheduler definitions
        self.importer.job_defs = self.scheduler_importer.job_defs

        # Verify Scheduler definitions were created
        self.assertEqual(len(scheduler_created), 4)
        self.assertEqual(len(scheduler_updated), 0)

        # Verify the Scheduler definitions dictionary was populated
        self.assertEqual(len(self.scheduler_importer.job_defs), 4)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.job_defs), 4)

        # Try importing the same definitions again - should result in updates, not creations
        scheduler_created2, scheduler_updated2 = self.scheduler_importer.sync_scheduler_jobs(scheduler_list, self.session)
        self.assertEqual(len(scheduler_created2), 0)
        self.assertEqual(len(scheduler_updated2), 4)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

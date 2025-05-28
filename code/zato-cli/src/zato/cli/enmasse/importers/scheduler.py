# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
import logging

# ciso8601 or dateutil
from zato.common.util.api import parse_datetime

# Zato
from zato.common.api import SCHEDULER
from zato.common.exception import ServiceMissingException, ZatoException
from zato.common.odb.model import Cluster, Job, IntervalBasedJob, Service, to_json
from zato.common.odb.query import job_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.job_defs = {}

# ################################################################################################################################

    def _process_job_defs(self, query_result:'any_', job_type:'str', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d %s job definitions', len(definitions), job_type)

        for item in definitions:
            name = item['name']
            logger.info('Processing job definition: %s (type=%s, id=%s)', name, job_type, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_job_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving job definitions from database for cluster_id=%s', cluster_id)
        jobs = job_list(session, cluster_id, None, False)

        if jobs:
            self._process_job_defs(jobs, 'scheduler', out)
            logger.info('Total job definitions from DB: %d', len(out))

            for name, details in out.items():
                logger.info('DB job def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_job_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':
        # Find items to create and update
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            name = yaml_def['name']

            # Update existing definition
            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                logger.info('Adding to update: %s', update_def)
                to_update.append(update_def)

            # Create new definition
            else:
                logger.info('Adding to create: %s', yaml_def)
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def create_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':
        """Create a new scheduler job definition in the database.
        """
        # Extract basic information
        def_name = job_def.get('name')
        logger.info('Creating job definition: name=%s', def_name)

        if not def_name:
            logger.error('Job definition missing required name')
            return None
            
        # Get a cluster for this job
        cluster = session.query(Cluster).filter(Cluster.id==self.importer.cluster_id).one()
            
        # Check if a job with this name already exists
        existing_job = session.query(Job).filter(Job.name==def_name).filter(Job.cluster_id==cluster.id).first()
        if existing_job:
            # If it exists, log and return it - don't try to create it again
            logger.info('Job definition %s already exists, will use existing (id=%s)', def_name, existing_job.id)
            # First, check if there's already an interval-based entry for this job
            existing_interval = session.query(JobIntervalBased).filter(JobIntervalBased.job_id==existing_job.id).first()
            if existing_interval:
                # Update the existing interval-based job if needed
                if 'seconds' in job_def:
                    existing_interval.seconds = job_def['seconds']
                if 'minutes' in job_def:
                    existing_interval.minutes = job_def['minutes']
                if 'hours' in job_def:
                    existing_interval.hours = job_def['hours']
                if 'days' in job_def:
                    existing_interval.days = job_def['days']
                if 'weeks' in job_def:
                    existing_interval.weeks = job_def['weeks']
                if 'repeats' in job_def:
                    existing_interval.repeats = job_def['repeats']
                
                logger.info('Updated interval-based job for %s', def_name)
            return existing_job

        # Get the service for this job
        service_name = job_def.get('service')
        if not service_name:
            msg = f'Job definition {def_name} missing required service name'
            logger.error(msg)
            raise ZatoException(None, msg)

        service = session.query(Service).filter(Service.name==service_name).filter(Service.cluster_id==cluster.id).first()
        if not service:
            msg = f'Service {service_name} not found for job {def_name}'
            logger.error(msg)
            raise ServiceMissingException(None, msg)

        # Determine job type
        job_type = job_def.get('job_type', SCHEDULER.JOB_TYPE.INTERVAL_BASED)

        # Parse start date
        start_date_str = job_def.get('start_date')
        if not start_date_str:
            start_date = datetime.datetime.now()
        else:
            start_date = parse_datetime(start_date_str)

        # Extract extra data
        extra = (job_def.get('extra') or '').encode('utf-8')

        # Create the job object
        # Handle is_active - if it's a string that could be an environment variable reference, treat as True
        is_active = job_def.get('is_active', True)
        if isinstance(is_active, str) and is_active.startswith('Zato_Enmasse_Env.'):
            is_active = True

        # First check if job exists - this approach avoids database locking issues
        existing_job = session.query(Job).filter(Job.name==def_name).filter(Job.cluster_id==cluster.id).first()
        if existing_job:
            logger.info('Job %s already exists, using existing (id=%s)', def_name, existing_job.id)
            return existing_job
            
        # Create the job definition
        job = Job(
            name=def_name,
            is_active=is_active,
            start_date=start_date,
            cluster=cluster,
            service=service,
            extra=extra,
            job_type=job_type
        )
        
        session.add(job)
        session.flush()

        # Set opaque attributes
        set_instance_opaque_attrs(job, job_def)

        # If it's an interval-based job, create the interval definition
        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            # Check if an interval record already exists for this job
            existing_interval = session.query(IntervalBasedJob).filter(IntervalBasedJob.job_id==job.id).first()
            
            if existing_interval:
                # Update existing interval record
                for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                    value = job_def.get(param)
                    if value is not None:
                        setattr(existing_interval, param, int(value))
                logger.info('Updated existing interval record for job %s', def_name)
            else:
                # Create a new interval record
                ib_job = IntervalBasedJob()
                ib_job.job = job

                # Set interval attributes from job definition
                for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                    value = job_def.get(param)
                    if value is not None:
                        setattr(ib_job, param, int(value))

                # Add interval job to session
                session.add(ib_job)
                
            # Flush to ensure everything is saved
            session.flush()

        return job

# ################################################################################################################################

    def update_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':
        job_id = job_def['id']
        def_name = job_def['name']

        logger.info('Updating job definition: name=%s id=%s', def_name, job_id)

        # Get the job object
        job = session.query(Job).filter_by(id=job_id).one()

        # Update job attributes
        if 'is_active' in job_def:
            is_active = job_def['is_active']
            # Handle environment variable references
            if isinstance(is_active, str) and is_active.startswith('Zato_Enmasse_Env.'):
                is_active = True
            job.is_active = is_active

        if 'name' in job_def:
            job.name = job_def['name']

        if 'start_date' in job_def:
            job.start_date = parse_datetime(job_def['start_date'])

        if 'extra' in job_def:
            job.extra = (job_def['extra'] or '').encode('utf-8')

        # Update service if specified
        if 'service' in job_def:
            service_name = job_def['service']
            service = session.query(Service).filter(Service.name==service_name).filter(Service.cluster_id==job.cluster_id).first()
            if service:
                job.service = service
            else:
                msg = f'Service {service_name} not found for job {def_name}'
                logger.error(msg)
                raise ServiceMissingException(None, msg)

        # Set opaque attributes
        set_instance_opaque_attrs(job, job_def)

        # Update interval-based job properties if this is an interval job
        if job.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED and job.interval_based:
            ib_job = job.interval_based

            # Update interval attributes
            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                if param in job_def:
                    value = job_def[param]
                    if value is not None:
                        setattr(ib_job, param, int(value))

            session.add(ib_job)

        session.add(job)
        return job

# ################################################################################################################################

    def sync_job_definitions(self, job_defs:'anylist', session:'SASession') -> 'tuple_[anylist, anylist]':
        """Process scheduler job definitions - create new ones and update existing ones.
        Returns a tuple of (created_job_defs, updated_job_defs)
        """
        logger.info('Processing %s job definitions from YAML', len(job_defs))

        # Get existing job definitions from database for comparison
        db_defs = self.get_job_defs_from_db(session, self.importer.cluster_id)

        # Determine which definitions need to be created and which need to be updated
        to_create, to_update = self.compare_job_defs(job_defs, db_defs)

        # Create new job definitions
        job_created = []
        if to_create:
            logger.info('Creating %s new job definitions', len(to_create))
            
            for item in to_create:
                try:
                    instance = self.create_job_definition(item, session)
                    if instance:
                        job_created.append(instance)
                        # Add to job_defs dictionary for external access
                        self.job_defs[instance.name] = instance
                except Exception as e:
                    # If an error occurs, roll back and continue
                    logger.error('Error creating job definition: %s, error: %s', item.get('name'), str(e))
                    session.rollback()

        # Update existing job definitions
        job_updated = []
        if to_update:
            logger.info('Updating %s existing job definitions', len(to_update))

            for item in to_update:
                try:
                    instance = self.update_job_definition(item, session)
                    if instance:
                        job_updated.append(instance)
                        # Update job_defs dictionary for external access
                        self.job_defs[instance.name] = instance
                except Exception as e:
                    # If an error occurs, roll back and continue
                    logger.error('Error updating job definition: %s, error: %s', item.get('name'), str(e))
                    session.rollback()

        # Commit changes
        try:
            logger.info('Committing changes: created=%s updated=%s', len(job_created), len(job_updated))
            session.commit()
            logger.info('Successfully committed all changes')
        except Exception as e:
            logger.error('Error committing changes: %s', str(e))
            session.rollback()
            raise

        return job_created, job_updated

# ################################################################################################################################
# ################################################################################################################################

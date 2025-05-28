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
        def_name = job_def.get('name', 'unnamed')
        logger.info('Creating job definition: name=%s', def_name)

        # Get a cluster for this job
        cluster = session.query(Cluster).filter(Cluster.id==self.importer.cluster_id).one()

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
        job = Job()
        job.name = def_name
        
        # Handle is_active - if it's a string that could be an environment variable reference, treat as True
        is_active = job_def.get('is_active', True)
        if isinstance(is_active, str) and is_active.startswith('Zato_Enmasse_Env.'):
            is_active = True
            
        job.is_active = is_active
        job.job_type = job_type
        job.start_date = start_date
        job.extra = extra
        job.cluster = cluster
        job.service = service

        # Set opaque attributes
        set_instance_opaque_attrs(job, job_def)

        # Add job to session and flush to get ID
        session.add(job)
        session.flush()

        # If it's an interval-based job, create the interval definition
        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            ib_job = IntervalBasedJob()
            ib_job.job = job

            # Set interval attributes from job definition
            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                value = job_def.get(param)
                if value is not None:
                    setattr(ib_job, param, int(value))

            # Add interval job to session
            session.add(ib_job)
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

    def sync_job_definitions(self, job_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d job definitions from YAML', len(job_list))

        db_defs = self.get_job_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_job_defs(job_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new job definitions', len(to_create))
            for item in to_create:
                # Check if a job with this name already exists
                existing_job = session.query(Job).filter(Job.name == item.get('name')).filter(Job.cluster_id == self.importer.cluster_id).first()
                if existing_job:
                    logger.info('Job with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_job_definition(item, session)
                if instance:
                    logger.info('Created job definition: name=%s id=%s', instance.name, instance.id)
                    out_created.append(instance)

                    # Store the mapping for future reference
                    self.job_defs[instance.name] = {
                        'id': instance.id,
                        'name': instance.name,
                        'job_type': instance.job_type
                    }

            logger.info('Updating %d existing job definitions', len(to_update))
            for item in to_update:
                instance = self.update_job_definition(item, session)
                logger.info('Updated job definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing job definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

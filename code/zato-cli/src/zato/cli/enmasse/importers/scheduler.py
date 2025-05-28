# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.api import SCHEDULER, ZATO_NONE
from zato.common.odb.model import Cluster, Job, IntervalBasedJob, Service as ODBService
from zato.common.odb.query import job_by_name, job_list
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
        self._id_counter = 1

# ################################################################################################################################

    def _process_job_defs(self, query_result:'any_', out:'dict') -> 'None':
        logger.info('Processing %d scheduler job definitions', len(query_result))

        for item in query_result:
            name = item.name
            logger.info('Processing scheduler job definition: %s (id=%s)', name, item.id)
            out[name] = {
                'id': item.id,
                'name': name,
                'is_active': item.is_active,
                'job_type': item.job_type,
                'service_name': item.service.name,
                'start_date': item.start_date.isoformat() if item.start_date else None,
                'extra': item.extra
            }

            # Add interval-based parameters if this is an interval-based job
            if item.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED and item.interval_based:
                ib = item.interval_based
                out[name].update({
                    'weeks': ib.weeks,
                    'days': ib.days,
                    'hours': ib.hours,
                    'minutes': ib.minutes,
                    'seconds': ib.seconds,
                    'repeats': ib.repeats
                })

# ################################################################################################################################

    def get_job_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving scheduler job definitions from database for cluster_id=%s', cluster_id)
        jobs = job_list(session, cluster_id)

        self._process_job_defs(jobs, out)
        logger.info('Total scheduler job definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB scheduler job def: name=%s', name)

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
        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Check job type
        job_type = job_def.get('job_type')
        if job_type not in (SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED):
            msg = f'Unrecognized job type [{job_type}]'
            logger.error(msg)
            raise ValueError(msg)

        # Is the service's name correct?
        service_name = job_def.get('service')
        service = session.query(ODBService)\
            .filter(Cluster.id==cluster.id)\
            .filter(ODBService.cluster_id==Cluster.id)\
            .filter(ODBService.name==service_name)\
            .first()

        if not service:
            msg = f'ODBService `{service_name}` does not exist in this cluster'
            logger.info(msg)
            raise ValueError(msg)

        # Parse required parameters
        name = job_def.get('name')
        is_active = job_def.get('is_active', True)
        
        # Parse start_date
        start_date = None
        if 'start_date' in job_def and job_def['start_date']:
            try:
                from zato.common.util.api import parse_datetime
            except ImportError:
                from dateutil.parser import parse as parse_datetime
            
            start_date = parse_datetime(job_def['start_date'])

        # Get extra data
        extra = job_def.get('extra', '')

        # Create base Job object
        job = Job(None, name, is_active, job_type, start_date, extra, cluster=cluster, service=service)

        # Add but don't commit yet
        session.add(job)

        # If job type is interval-based, create an IntervalBasedJob too
        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            ib_job = IntervalBasedJob(None, job)

            # Set interval parameters
            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                value = job_def.get(param)
                if value is not None and value != ZATO_NONE:
                    setattr(ib_job, param, value)

            session.add(ib_job)

        # Flush to get the ID but don't commit yet
        session.flush()

        return job

# ################################################################################################################################

    def update_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':
        job_id = job_def['id']
        def_name = job_def['name']

        logger.info('Updating scheduler job definition: name=%s id=%s', def_name, job_id)

        # Get the existing job
        job = session.query(Job).filter_by(id=job_id).one()

        # Update basic job properties
        for key in ('name', 'is_active'):
            if key in job_def:
                setattr(job, key, job_def[key])

        # Update service if provided
        if 'service' in job_def:
            service_name = job_def['service']
            service = session.query(ODBService)\
                .filter(Cluster.id==job.cluster_id)\
                .filter(ODBService.cluster_id==Cluster.id)\
                .filter(ODBService.name==service_name)\
                .first()
            
            if not service:
                msg = f'ODBService `{service_name}` does not exist in this cluster'
                logger.info(msg)
                raise ValueError(msg)
            
            job.service = service

        # Update start_date if provided
        if 'start_date' in job_def and job_def['start_date']:
            try:
                from zato.common.util.api import parse_datetime
            except ImportError:
                from dateutil.parser import parse as parse_datetime
            
            job.start_date = parse_datetime(job_def['start_date'])

        # Update extra if provided
        if 'extra' in job_def:
            job.extra = job_def.get('extra', '')

        # Update interval-based parameters if applicable
        if job.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED and job.interval_based:
            ib_job = job.interval_based

            # Update interval parameters if provided
            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                if param in job_def and job_def[param] is not None and job_def[param] != ZATO_NONE:
                    setattr(ib_job, param, job_def[param])

            session.add(ib_job)

        # Add the updated job
        session.add(job)

        return job

# ################################################################################################################################

    def sync_scheduler_jobs(self, job_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d scheduler job definitions from YAML', len(job_list))

        db_defs = self.get_job_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_job_defs(job_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new scheduler job definitions', len(to_create))
            for item in to_create:

                # Check if job already exists by name
                existing_job = job_by_name(session, self.importer.cluster_id, item.get('name'))
                if existing_job:
                    logger.info('Scheduler job with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_job_definition(item, session)
                logger.info('Created scheduler job definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.job_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing scheduler job definitions', len(to_update))
            for item in to_update:
                instance = self.update_job_definition(item, session)
                logger.info('Updated scheduler job definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing scheduler job definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

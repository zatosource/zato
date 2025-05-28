# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.odb.model import Job, IntervalBasedJob, Cluster, Service, to_json
from zato.common.odb.query import job_list
from zato.common.util.sql import set_instance_opaque_attrs
from zato.common.api import SCHEDULER

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
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d scheduler job definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing scheduler job definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_job_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving scheduler job definitions from database for cluster_id=%s', cluster_id)
        job_definitions = job_list(session, cluster_id)

        self._process_job_defs(job_definitions, out)
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

        # Get the service instance
        service_name = job_def['service']
        service = session.query(Service).filter(Service.name==service_name).filter(Service.cluster_id==cluster.id).one()

        # Create a new job instance
        job = Job(None, job_def['name'], job_def['is_active'], job_def['job_type'], 
                job_def['start_date'], job_def.get('extra', ''), cluster=cluster, service=service)

        # Add to session and flush to get ID
        session.add(job)
        session.flush()

        # If it's an interval-based job, create the associated IntervalBasedJob
        if job.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            interval_job = IntervalBasedJob(None, job)
            
            # Set interval attributes
            for attr in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                if attr in job_def:
                    setattr(interval_job, attr, job_def[attr])

            # Handle definition_text if provided
            if 'cron_definition' in job_def:
                interval_job.definition_text = job_def['cron_definition']

            # Add the interval job to the session
            session.add(interval_job)
            session.flush()

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(job, job_def)

        return job

# ################################################################################################################################

    def update_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':

        job_id = job_def['id']
        def_name = job_def['name']

        logger.info('Updating scheduler job definition: name=%s id=%s', def_name, job_id)

        # Get the job instance
        job = session.query(Job).filter_by(id=job_id).one()

        # Update all attributes provided in YAML
        for key, value in job_def.items():
            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition']:
                setattr(job, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(job, job_def)

        # If it's an interval-based job, update the associated IntervalBasedJob
        if job.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            interval_job = session.query(IntervalBasedJob).filter_by(job_id=job.id).one()
            
            # Update interval attributes
            for attr in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                if attr in job_def:
                    setattr(interval_job, attr, job_def[attr])

            # Handle definition_text if provided
            if 'cron_definition' in job_def:
                interval_job.definition_text = job_def['cron_definition']

            # Add the updated interval job to the session
            session.add(interval_job)

        session.add(job)
        return job

# ################################################################################################################################

    def sync_job_definitions(self, job_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d scheduler job definitions from YAML', len(job_list))

        db_defs = self.get_job_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_job_defs(job_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new scheduler job definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_job = session.query(Job).filter(Job.name == item.get('name')).first()
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
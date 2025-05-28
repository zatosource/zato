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
from zato.common.odb.model import Cluster, Job, IntervalBasedJob, Service, to_json
from zato.common.odb.query import job_by_name, job_list

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

        processed_query_result = to_json(query_result)

        for item_dict in processed_query_result:

            name = item_dict['name']
            item_id = item_dict['id']
            logger.info('Processing scheduler job definition: %s (id=%s)', name, item_id)
            out[name] = {
                'id': item_id,
                'name': name,
                'is_active': item_dict['is_active'],
                'job_type': item_dict['job_type'],
                'service_name': item_dict.get('service_name') or item_dict.get('service', {}).get('name'),
                'start_date': item_dict['start_date'],
                'extra': item_dict['extra']
            }

            if item_dict['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
                out[name].update({
                    'weeks': item_dict.get('weeks'),
                    'days': item_dict.get('days'),
                    'hours': item_dict.get('hours'),
                    'minutes': item_dict.get('minutes'),
                    'seconds': item_dict.get('seconds'),
                    'repeats': item_dict.get('repeats')
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
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            name = yaml_def['name']

            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                logger.info('Adding to update: %s', update_def)
                to_update.append(update_def)

            else:
                logger.info('Adding to create: %s', yaml_def)
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def create_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':
        cluster = self.importer.get_cluster(session)

        job_type = job_def.get('job_type')

        service_name = job_def.get('service')
        service = session.query(Service).filter(Cluster.id==cluster.id).filter(Service.cluster_id==Cluster.id).filter(Service.name==service_name).first()

        if not service:
            msg = f'Service `{service_name}` does not exist in this cluster'
            logger.info(msg)
            raise ValueError(msg)

        name = job_def.get('name')
        is_active = job_def.get('is_active', True)

        start_date = None
        if 'start_date' in job_def and job_def['start_date']:
            try:
                from zato.common.util.api import parse_datetime
            except ImportError:
                from dateutil.parser import parse as parse_datetime

            start_date = parse_datetime(job_def['start_date'])

        # Ensure 'extra' is bytes
        extra_val = job_def.get('extra')
        if isinstance(extra_val, str):
            extra_bytes = extra_val.encode('utf-8')
        elif isinstance(extra_val, bytes):
            extra_bytes = extra_val
        else:
            extra_bytes = b''

        job = Job(None, name, is_active, job_type, start_date, extra_bytes, cluster=cluster, service=service)

        session.add(job)

        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            ib_job = IntervalBasedJob(None, job)

            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                value = job_def.get(param)
                if value is not None and value != ZATO_NONE:
                    setattr(ib_job, param, value)

            session.add(ib_job)

        session.flush()

        return job

# ################################################################################################################################

    def update_job_definition(self, job_def:'anydict', session:'SASession') -> 'any_':
        job_id = job_def['id']
        def_name = job_def['name']

        logger.info('Updating scheduler job definition: name=%s id=%s', def_name, job_id)

        job = session.query(Job).filter_by(id=job_id).one()

        for key in ('name', 'is_active'):
            if key in job_def:
                setattr(job, key, job_def[key])

        if 'service' in job_def:
            service_name = job_def['service']
            service = session.query(Service)\
                .filter(Cluster.id==job.cluster_id)\
                .filter(Service.cluster_id==Cluster.id)\
                .filter(Service.name==service_name)\
                .first()

            if not service:
                msg = f'Service `{service_name}` does not exist in this cluster'
                logger.info(msg)
                raise ValueError(msg)

            job.service = service

        if 'start_date' in job_def and job_def['start_date']:
            try:
                from zato.common.util.api import parse_datetime
            except ImportError:
                from dateutil.parser import parse as parse_datetime

            job.start_date = parse_datetime(job_def['start_date'])

        if 'extra' in job_def:
            extra_val = job_def.get('extra')
            if isinstance(extra_val, str):
                job.extra = extra_val.encode('utf-8')
            elif isinstance(extra_val, bytes):
                job.extra = extra_val
            else:
                job.extra = b''
        elif 'extra' not in job_def and hasattr(job, 'extra'): # Ensure it's bytes even if not in job_def (e.g. clearing it)
             pass # If not in job_def, existing job.extra (which should be bytes) is kept or handled by ORM defaults if nullable.
                  # If we wanted to explicitly clear it to b'' if not provided: job.extra = b''

        if job.job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED and job.interval_based:
            ib_job = job.interval_based

            for param in ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'):
                if param in job_def and job_def[param] is not None and job_def[param] != ZATO_NONE:
                    setattr(ib_job, param, job_def[param])

            session.add(ib_job)

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

                existing_job = job_by_name(session, self.importer.cluster_id, item.get('name'))
                if existing_job:
                    logger.info('Scheduler job with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_job_definition(item, session)
                logger.info('Created scheduler job definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

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

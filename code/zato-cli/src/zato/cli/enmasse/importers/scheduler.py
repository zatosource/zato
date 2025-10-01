# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timedelta, timezone

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.odb.model import Job, IntervalBasedJob, Service, to_json
from zato.common.odb.query import job_list
from zato.common.util.api import parse_datetime
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

_interval_based_job_attrs = {'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'}

# ################################################################################################################################
# ################################################################################################################################

def compute_next_start_date(start_date, job_def):
    """ Compute the next run time for a job based on its start date and interval settings.
    """

    # All start dates are in UTC
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    # If the start date is in the future, respect it and return as is
    if start_date > current_time:
        return start_date

    seconds = job_def.get('seconds', 0)
    minutes = job_def.get('minutes', 0)
    hours = job_def.get('hours', 0)
    days = job_def.get('days', 0)

    # Calculate the total seconds in the interval
    interval_seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 86400)

    # Safety check - don't allow zero interval
    if interval_seconds == 0:
        return start_date

    # Calculate time elapsed since start_date
    time_elapsed = (current_time - start_date).total_seconds()

    # Calculate how many intervals have passed (must be non-negative)
    intervals_passed = max(0, int(time_elapsed / interval_seconds))

    # Calculate the next start date
    next_start = start_date + timedelta(seconds=intervals_passed * interval_seconds)

    # If the calculated next start is in the past, add one more interval
    if next_start <= current_time:
        next_start += timedelta(seconds=interval_seconds)

    return next_start

# ################################################################################################################################
# ################################################################################################################################

class SchedulerImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.job_defs = {}

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
            yaml_def = preprocess_item(yaml_def)
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
        service = session.query(Service).filter(Service.name==service_name).filter(Service.cluster_id==cluster.id).one() # type: ignore

        # Parse the start_date from string to datetime object
        original_start_date = parse_datetime(job_def['start_date'])

        # Compute the next start date based on current time
        start_date = compute_next_start_date(original_start_date, job_def)

        # Prepare job parameters
        job_id = None
        job_name = job_def['name']
        job_is_active = job_def.get('is_active', True) or True
        job_type = job_def['job_type']
        job_extra = job_def.get('extra', '')

        # Create a new job instance
        job = Job(job_id, job_name, job_is_active, job_type, start_date, job_extra, cluster=cluster, service=service)

        # Add to session and flush to get ID
        session.add(job)
        session.flush()

        # Create the associated IntervalBasedJob
        interval_job = IntervalBasedJob(None, job)

        # Set interval attributes
        for attr in _interval_based_job_attrs:
            if attr in job_def:
                setattr(interval_job, attr, job_def[attr])

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

            # Handle start_date conversion from string to datetime if present
            if key == 'start_date' and value:

                original_start_date = parse_datetime(value)
                next_start_date = compute_next_start_date(original_start_date, job_def)

                setattr(job, key, next_start_date)

            # Handle service specially - it's a relationship, not a string
            elif key == 'service':
                service_name = value
                service = session.query(Service).filter_by(name=service_name).first()
                if not service:
                    raise Exception(f'Service {service_name} not found')
                job.service = service

            # Set all other fields directly, except interval attributes and id
            elif key not in _interval_based_job_attrs:
                setattr(job, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(job, job_def)

        # Get the associated IntervalBasedJob
        interval_job = session.query(IntervalBasedJob).filter_by(job_id=job.id).one()

        # Update interval attributes
        for attr in _interval_based_job_attrs:
            if attr in job_def:
                setattr(interval_job, attr, job_def[attr])

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
            logger.info('Creating new scheduler job definitions: %s', to_create)

            for item in to_create:
                instance = self.create_job_definition(item, session)
                logger.info('Created scheduler job definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.job_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating existing scheduler job definitions: %s', to_update)

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

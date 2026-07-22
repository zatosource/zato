# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.odb.model import GenericConn, IntervalBasedJob, Job, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.file_transfer_scheduler import build_job_extra, get_job_name, schedule_from_yaml
from zato.common.util.imap_scheduler import interval_from_unit
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

class GenericConnectionImporter:

    connection_type = None
    connection_defaults = {}
    connection_extra_field_defaults = {}
    connection_secret_keys = ['password', 'secret', 'api_token']
    connection_required_attrs = ['name', 'address', 'username']

    # File transfer connections carry a list of schedules, each with a linked scheduler job
    supports_schedules = False

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.connection_defs = {}

# ################################################################################################################################

    def _process_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d connection definitions (%s)', len(definitions), self.connection_type)

        for item in definitions:
            name = item['name']
            logger.info('Processing connection definition: %s (id=%s) (%s)', name, item.get('id'), self.connection_type)
            out[name] = item

# ################################################################################################################################

    def get_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving connection definitions from database (%s)', self.connection_type)
        connections = connection_list(session, cluster_id, self.connection_type, False)

        self._process_defs(connections, out)
        logger.info('Total connection definitions from DB: %d (%s)', len(out), self.connection_type)

        for name in out:
            logger.info('DB connection def: name=%s (%s)', name, self.connection_type)

        return out

# ################################################################################################################################

    def compare_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Take the schedules out of the definition first - they are synchronized separately
        # after the connection exists, so they must not land in the opaque attributes as-is.
        schedules = connection_def.pop('schedules', None) if self.supports_schedules else None

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new generic connection
        connection = GenericConn()
        connection.cluster = cluster

        # Apply defaults unless overridden in YAML
        for key, default_value in self.connection_defaults.items():
            value = connection_def.get(key, default_value)
            setattr(connection, key, value)

        # Set required fields - they will always exist
        for attr in self.connection_required_attrs:
            setattr(connection, attr, connection_def[attr])

        # Set secret using a list of possible keys with priority order
        for key in self.connection_secret_keys:
            if key in connection_def and connection_def[key]:
                connection.secret = connection_def[key]
                break

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in self.connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            # Include all values, even None, as None is a valid value for some fields
            extra_fields[field] = value

        # Merge extra_fields with connection_def to ensure defaults are included
        merged_def = connection_def.copy()
        merged_def.update(extra_fields)

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(connection, merged_def)

        # Add to session and flush to get ID
        session.add(connection)
        session.flush()

        # Now that the connection has an ID, its schedules and their jobs can be built
        if schedules is not None:
            self._sync_schedules(schedules, connection, session)

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Take the schedules out of the definition first - they are synchronized separately
        # and must not land in the opaque attributes as-is.
        schedules = connection_def.pop('schedules', None) if self.supports_schedules else None

        connection_id = connection_def['id']
        def_name = connection_def['name']

        logger.info('Updating connection definition (%s): name=%s id=%s', self.connection_type, def_name, connection_id)

        connection = session.query(GenericConn).filter_by(id=connection_id).one()

        # Set required fields using global list of required attributes
        for attr in self.connection_required_attrs:
            setattr(connection, attr, connection_def[attr])

        # Set secret - using global list of possible keys with priority order
        for key in self.connection_secret_keys:
            if key in connection_def and connection_def[key]:
                connection.secret = connection_def[key]
                break

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in self.connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            extra_fields[field] = value

        # Merge extra_fields with connection_def to ensure defaults are included
        merged_def = connection_def.copy()
        merged_def.update(extra_fields)

        set_instance_opaque_attrs(connection, merged_def)

        session.add(connection)

        # An explicit schedules key in YAML - even an empty list - means the YAML
        # is the source of truth for this connection's schedules.
        if schedules is not None:
            self._sync_schedules(schedules, connection, session)

        return connection

# ################################################################################################################################

    def _sync_schedules(self, schedules:'anylist', connection:'any_', session:'SASession') -> 'None':
        """ Creates or updates the scheduler job of each file transfer schedule from YAML,
        deletes the jobs of schedules that the YAML no longer contains and stores
        the full list with the connection.
        """
        _scheduler = FileTransfer.Scheduler

        # The full entries to store with the connection, and the job names the YAML wants to exist
        entries = []
        wanted_job_names = set()

        for schedule_def in schedules:

            # Turn the YAML shape into a full entry with all the defaults filled in
            entry = schedule_from_yaml(schedule_def)

            # The job invokes the internal dispatch service and its extra data carries
            # the connection's identity along with the schedule itself.
            job_name = get_job_name(connection.type_, connection.name, entry['name'])
            extra = build_job_extra(connection.id, connection.name, connection.type_, entry)

            job_def = {
                'name': job_name,
                'service': _scheduler.Dispatch_Service[connection.type_],
                'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
                'is_active': entry['is_active'],
                'extra': extra,

                # The link lets the scheduler screens sync edits and deletions back to this connection
                SchedulerLink.Conn_ID: connection.id,
                SchedulerLink.Conn_Type: connection.type_,
                SchedulerLink.Kind: entry['id'],
            }

            interval = interval_from_unit(int(entry['run_every']), entry['run_unit'])
            job_def.update(interval)

            if entry['start_date']:
                job_def['start_date'] = entry['start_date']

            # The job may already exist from a previous import, in which case it is updated in place
            existing_job = session.query(Job).filter_by(name=job_name, cluster_id=self.importer.cluster_id).first()

            if existing_job:
                job_def['id'] = existing_job.id
                job = self.importer.scheduler_importer.update_job_definition(job_def, session)
            else:
                job = self.importer.scheduler_importer.create_job_definition(job_def, session)

            # The entry stores the resolved start date of its job so both always describe the same moment
            entry['job_id'] = job.id
            entry['start_date'] = job.start_date.isoformat()

            entries.append(entry)
            wanted_job_names.add(job_name)

        # Delete the jobs of schedules that the YAML no longer contains - they are recognized
        # by the naming convention that ties a job to its connection.
        prefix = get_job_name(connection.type_, connection.name, '')
        job_query = session.query(Job).filter(Job.name.startswith(prefix)) # type: ignore
        existing_jobs = job_query.filter(Job.cluster_id==self.importer.cluster_id).all() # type: ignore

        for job in existing_jobs:
            if job.name not in wanted_job_names:
                logger.info('Deleting schedule job no longer in YAML: %s', job.name)
                _ = session.query(IntervalBasedJob).filter_by(job_id=job.id).delete()
                session.delete(job)

        # Store the full list with the connection
        set_instance_opaque_attrs(connection, {_scheduler.Schedules_Field: entries})

# ################################################################################################################################

    def sync_definitions(self, conn_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d connection definitions from YAML (%s)', len(conn_list), self.connection_type)

        db_defs = self.get_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_defs(conn_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new connection definitions (%s)', len(to_create), self.connection_type)
            for item in to_create:

                # Keep track of things that already exist
                existing_conn = session.query(GenericConn).filter(
                    GenericConn.name==item.get('name'),
                    GenericConn.type_==self.connection_type
                ).first()  # type: ignore

                if existing_conn:
                    logger.info('Connection with name %s already exists, skipping (%s)', item.get('name'), self.connection_type)
                    continue

                instance = self.create_definition(item, session)
                logger.info('Created connection definition: name=%s id=%s (%s)', instance.name, instance.id, self.connection_type)
                out_created.append(instance)

                # Store the mapping for future reference
                self.connection_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing connection definitions (%s)', len(to_update), self.connection_type)
            for item in to_update:
                instance = self.update_definition(item, session)
                logger.info('Updated connection definition: name=%s id=%s (%s)', instance.name, instance.id, self.connection_type)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing connection definitions: %s (%s)', e, self.connection_type)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

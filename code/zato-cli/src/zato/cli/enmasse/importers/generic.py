# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.cli.enmasse.util.alerts import flatten_alerts
from zato.cli.enmasse.util.invocation import sync_health_check_job
from zato.cli.enmasse.util.secrets import Common_Secret_Keys, encrypt_opaque_secrets, encrypt_secret, ensure_encrypted, \
    is_secret_to_write, load_opaque, redact_secrets
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.odb.model import GenericConn, Job, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.file_transfer_scheduler import build_job_extra, get_job_name, new_schedule_id, schedule_from_yaml
from zato.common.util.interval import interval_from_unit
from zato.common.util.sql import parse_instance_opaque_attr, set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple, strlist, strnone, strtuple

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

    # The secrets a wrapper of this type reads from the opaque attributes rather than from the secret column -
    # they are stored encrypted in the opaque attributes and never in the column.
    opaque_secret_keys:'strtuple' = ()

    # File transfer connections carry a list of schedules, each with a linked scheduler job
    supports_schedules = False

    # Connections with alert settings of their own name the alert type the settings follow
    alert_type = None

    # Connections with a health check of their own name the connection type its job links back to
    health_check_conn_type = None

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

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ May be overridden by subclasses to reject a YAML definition before anything is written.
        """

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ May be overridden by subclasses to turn the names a YAML definition refers other objects
        by into the ids that are stored. Runs before validation, so what validation sees is what
        will be written.
        """

# ################################################################################################################################

    def compare_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

        # Find items to create and update
        to_create = []
        to_update = []

        for yaml_def in yaml_defs:
            yaml_def = preprocess_item(yaml_def)
            self.resolve_references(yaml_def)
            self.validate_definition(yaml_def)
            name = yaml_def['name']

            # Update existing definition
            if name in db_defs:
                update_def = yaml_def.copy()
                update_def['id'] = db_defs[name]['id']
                logger.info('Adding to update: %s', self._redact(update_def))
                to_update.append(update_def)

            # Create new definition
            else:
                logger.info('Adding to create: %s', self._redact(yaml_def))
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def _redact(self, definition:'anydict') -> 'anydict':
        """ Returns a copy of the definition fit for a log line - every secret this type knows of is replaced by a marker.
        """
        keys = tuple(self.connection_secret_keys) + self.opaque_secret_keys
        out = redact_secrets(definition, keys)
        return out

# ################################################################################################################################

    def _get_secret_from_def(self, connection_def:'anydict', is_create:'bool') -> 'strnone':
        """ Returns the first secret the definition carries under one of this type's secret keys, or None.
        """
        for key in self.connection_secret_keys:
            value = connection_def.get(key)
            if is_secret_to_write(value, is_create):
                return value

        return None

# ################################################################################################################################

    def _set_secret_column(self, connection:'any_', connection_def:'anydict', session:'SASession', is_create:'bool') -> 'None':
        """ Writes the secret the definition gives to the secret column, encrypted. When the definition gives none,
        the stored one is kept and encrypted in place if it is still in clear text. The column is nullable.
        """
        secret = self._get_secret_from_def(connection_def, is_create)

        if secret is not None:
            connection.secret = encrypt_secret(session, secret)
        elif connection.secret is not None:
            connection.secret = ensure_encrypted(session, connection.secret)

# ################################################################################################################################

    def _prepare_opaque_secrets(
        self,
        connection:'any_',
        merged_def:'anydict',
        session:'SASession',
        is_create:'bool',
    ) -> 'None':
        """ Makes the definition about to land in the opaque attributes hold each secret in exactly one place.
        A secret a wrapper of this type reads from the opaque attributes is encrypted there, and one the definition
        does not give in a usable form is dropped so the stored value stays, encrypted in place if it is in clear text.
        Every other secret key leaves the definition - its value lives in the secret column and nowhere else.
        """
        stored = load_opaque(connection.opaque1)
        opaque_secret_keys = self.get_opaque_secret_keys(session)
        encrypt_opaque_secrets(merged_def, stored, opaque_secret_keys, session, is_create)

        # A None is not a secret and a wrapper's fallback read expects the key to exist, so only actual values leave
        for name in self._get_column_secret_keys(opaque_secret_keys):
            if name in merged_def:
                if merged_def[name] is not None:
                    del merged_def[name]

# ################################################################################################################################

    def get_opaque_secret_keys(self, session:'SASession') -> 'strtuple':
        """ Returns the names of the secrets this type keeps in the opaque attributes.
        May be overridden by subclasses whose secret names are not known until runtime.
        """
        return self.opaque_secret_keys

# ################################################################################################################################

    def _get_column_secret_keys(self, opaque_secret_keys:'strtuple') -> 'strtuple':
        """ Returns the names whose value belongs in the secret column and must therefore never reach the opaque attributes.
        """
        out:'strlist' = []

        for name in tuple(self.connection_secret_keys) + Common_Secret_Keys:
            if name in opaque_secret_keys:
                continue
            if name in out:
                continue
            out.append(name)

        return tuple(out)

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # The alerts mapping becomes flat alert_ attributes, over the defaults,
        # which is the shape the opaque attributes store them in.
        if self.alert_type:
            flatten_alerts(connection_def, self.alert_type, self.connection_type, session)

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

        # The secret column holds the first usable secret the definition gives, encrypted
        self._set_secret_column(connection, connection_def, session, is_create=True)

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in self.connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            # Include all values, even None, as None is a valid value for some fields
            extra_fields[field] = value

        # Merge extra_fields with connection_def to ensure defaults are included
        merged_def = connection_def.copy()
        merged_def.update(extra_fields)

        # Each secret lands in one place only - encrypted in the opaque attributes if a wrapper reads it there,
        # otherwise nowhere but the secret column
        self._prepare_opaque_secrets(connection, merged_def, session, is_create=True)

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(connection, merged_def)

        # Add to session and flush to get ID
        session.add(connection)
        session.flush()

        # Now that the connection has an ID, its schedules and their jobs can be built
        if schedules is not None:
            self._sync_schedules(schedules, connection, session)

        # .. and so can its health check job, whose ID is then stored with the connection
        if self.health_check_conn_type:
            sync_health_check_job(self.importer, session, merged_def, connection, self.health_check_conn_type)
            set_instance_opaque_attrs(connection, merged_def)

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # The alerts mapping becomes flat alert_ attributes, over the defaults, the same way
        # a new connection gets them, so that the YAML is the source of truth on every run.
        if self.alert_type:
            flatten_alerts(connection_def, self.alert_type, self.connection_type, session)

        # Take the schedules out of the definition first - they are synchronized separately
        # and must not land in the opaque attributes as-is.
        schedules = connection_def.pop('schedules', None) if self.supports_schedules else None

        connection_id = connection_def['id']
        def_name = connection_def['name']

        logger.info('Updating connection definition (%s): name=%s id=%s', self.connection_type, def_name, connection_id)

        connection = session.query(GenericConn).filter_by(id=connection_id).one()

        # Apply defaults unless overridden in YAML - the same way a new connection gets them,
        # so that a field such as is_active means what the YAML says on every run, not only the first
        for key, default_value in self.connection_defaults.items():
            value = connection_def.get(key, default_value)
            setattr(connection, key, value)

        # Set required fields using global list of required attributes
        for attr in self.connection_required_attrs:
            setattr(connection, attr, connection_def[attr])

        # The secret column holds the first usable secret the definition gives, encrypted,
        # or keeps the stored one when the definition gives none
        self._set_secret_column(connection, connection_def, session, is_create=False)

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in self.connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            extra_fields[field] = value

        # Merge extra_fields with connection_def to ensure defaults are included
        merged_def = connection_def.copy()
        merged_def.update(extra_fields)

        # The connection exists already so its health check job can be created or updated right away,
        # its ID landing in the opaque attributes with everything else
        if self.health_check_conn_type:
            sync_health_check_job(self.importer, session, merged_def, connection, self.health_check_conn_type)

        # Each secret lands in one place only - encrypted in the opaque attributes if a wrapper reads it there,
        # otherwise nowhere but the secret column
        self._prepare_opaque_secrets(connection, merged_def, session, is_create=False)

        set_instance_opaque_attrs(connection, merged_def)

        session.add(connection)

        # An explicit schedules key in YAML - even an empty list - means the YAML
        # is the source of truth for this connection's schedules.
        if schedules is not None:
            self._sync_schedules(schedules, connection, session)

        return connection

# ################################################################################################################################

    def _get_schedule_ids_by_name(self, connection:'any_') -> 'anydict':
        """ Returns the id of each schedule the connection already carries, keyed by its name -
        the name is what YAML and a stored entry have in common, since the id never travels in YAML.
        """
        out:'anydict' = {}

        # A connection being created for the first time carries nothing yet
        if not connection.id:
            return out

        opaque = parse_instance_opaque_attr(connection)
        schedules = opaque.get(FileTransfer.Scheduler.Schedules_Field) or []

        for schedule in schedules:
            out[schedule['name']] = schedule['id']

        return out

# ################################################################################################################################

    def _sync_schedules(self, schedules:'anylist', connection:'any_', session:'SASession') -> 'None':
        """ Creates or updates the scheduler job of each file transfer schedule from YAML,
        deletes the jobs of schedules that the YAML no longer contains and stores
        the full list with the connection.
        """
        _scheduler = FileTransfer.Scheduler

        # A schedule this connection already has keeps the id it was created with, so the link
        # its job carries stays valid across re-imports. Anything the YAML has not been seen with
        # before is new and is given an id of its own.
        existing_ids = self._get_schedule_ids_by_name(connection)

        # The full entries to store with the connection, and the job names the YAML wants to exist
        entries = []
        wanted_job_names = set()

        for schedule_def in schedules:

            name = schedule_def['name']
            schedule_id = existing_ids.get(name)

            if schedule_id is None:
                schedule_id = new_schedule_id()

            # Turn the YAML shape into a full entry with all the defaults filled in
            entry = schedule_from_yaml(schedule_def, schedule_id)

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

                # Deleting the job cascades to its interval row through the ORM relationship
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

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps
from uuid import uuid4

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import EMAIL as EMail_Common, SCHEDULER
from zato.common.odb.model import IMAP, Job, to_json
from zato.common.odb.query import email_imap_list
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

_scheduler_common = EMail_Common.IMAP.Scheduler

# ################################################################################################################################
# ################################################################################################################################

class IMAPImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.imap_defs = {}

# ################################################################################################################################

    def _process_imap_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d IMAP connection definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing IMAP connection definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_imap_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving IMAP connection definitions from database for cluster_id=%s', cluster_id)
        imap_connections = email_imap_list(session, cluster_id)

        self._process_imap_defs(imap_connections, out)
        logger.info('Total IMAP connection definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB IMAP connection def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_imap_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def _sync_linked_job(self, imap_def:'anydict', imap_conn:'any_', session:'SASession') -> 'any_':
        """ Creates or updates the scheduler job that runs the service configured for an IMAP connection.
        """
        run_every = int(imap_def['scheduler_run_every'])
        run_unit = imap_def.get('scheduler_run_unit', _scheduler_common.Unit.Minutes)
        invoke_with = imap_def.get('scheduler_invoke_with', _scheduler_common.InvokeWith.Message)

        # Store the resolved mode back so the connection's opaque attributes always describe it explicitly
        imap_def['scheduler_invoke_with'] = invoke_with

        # The job invokes the internal dispatch service and its extra data carries the connection's identity
        # along with the user's service, which the dispatch service invokes either once per each message received
        # or once per each of a message's attachments, depending on the invoke-with mode.
        extra = dumps({
            _scheduler_common.Extra_Conn_ID: imap_conn.id,
            _scheduler_common.Extra_Conn_Name: imap_conn.name,
            _scheduler_common.Extra_Service: imap_def['scheduler_service'],
            _scheduler_common.Extra_Invoke_With: invoke_with,
        })

        # Build a regular scheduler job definition out of the connection's scheduler fields
        job_def = {
            'name': _scheduler_common.Job_Prefix + imap_conn.name,
            'service': _scheduler_common.Dispatch_Service,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'is_active': imap_def.get('is_active', True),
            'extra': extra,
            _scheduler_common.Conn_ID_Attr: imap_conn.id,
        }

        interval = interval_from_unit(run_every, run_unit)
        job_def.update(interval)

        if start_date := imap_def.get('scheduler_start_date'):
            job_def['start_date'] = start_date

        # The job may already exist from a previous import, in which case it is updated in place
        existing_job = session.query(Job).filter_by(name=job_def['name'], cluster_id=self.importer.cluster_id).first()

        if existing_job:
            job_def['id'] = existing_job.id
            out = self.importer.scheduler_importer.update_job_definition(job_def, session)
        else:
            out = self.importer.scheduler_importer.create_job_definition(job_def, session)

        return out

# ################################################################################################################################

    def create_imap_definition(self, imap_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new IMAP connection instance
        imap_conn = IMAP()
        imap_conn.cluster_id = cluster.id

        name = imap_def.get('name', '')
        is_active = imap_def.get('is_active', True)
        host = imap_def.get('host', '')
        port = imap_def.get('port', 143)
        timeout = imap_def.get('timeout', 30)
        debug_level = imap_def.get('debug_level', 0)
        username = imap_def.get('username', '')
        mode = imap_def.get('mode', 'plain')
        get_criteria = imap_def.get('get_criteria', '{}')
        filter_criteria = imap_def.get('filter_criteria', 'isRead ne true')

        imap_conn.name = name
        imap_conn.is_active = is_active
        imap_conn.host = host
        imap_conn.port = port
        imap_conn.timeout = timeout
        imap_conn.debug_level = debug_level
        imap_conn.username = username
        imap_conn.mode = mode
        imap_conn.get_criteria = get_criteria
        imap_conn.filter_criteria = filter_criteria

        # Remap IMAP server type
        if 'type' in imap_def:
            if imap_def['type'] == 'microsoft-365':
                imap_def['server_type'] = EMail_Common.IMAP.ServerType.Microsoft365
            else:
                imap_def['server_type'] = imap_def['type']
        else:
            imap_def['server_type'] = EMail_Common.IMAP.ServerType.Generic

        # Set password if provided, otherwise generate one
        if 'password' in imap_def:
            imap_conn.password = imap_def['password']
        else:
            imap_conn.password = uuid4().hex

        # Add to session and flush to get ID
        session.add(imap_conn)
        session.flush()

        # Create the scheduler job that this connection is linked to, if one was configured
        if imap_def.get('scheduler_service'):
            job = self._sync_linked_job(imap_def, imap_conn, session)
            imap_def['scheduler_job_id'] = job.id

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(imap_conn, imap_def)

        return imap_conn

# ################################################################################################################################

    def update_imap_definition(self, imap_def:'anydict', session:'SASession') -> 'any_':

        imap_id = imap_def['id']
        def_name = imap_def['name']

        # Set default filter_criteria if not provided
        if 'filter_criteria' not in imap_def:
            imap_def['filter_criteria'] = 'isRead ne true'

        logger.info('Updating IMAP connection definition: name=%s id=%s', def_name, imap_id)

        imap_conn = session.query(IMAP).filter_by(id=imap_id).one()

        # Update all attributes provided in YAML
        for key, value in imap_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type']:

                # Special handling for password - only update if provided
                if key == 'password' and not value:
                    continue

                # Set the attribute on the IMAP connection object
                setattr(imap_conn, key, value)

        # Create or update the scheduler job that this connection is linked to, if one was configured
        if imap_def.get('scheduler_service'):
            job = self._sync_linked_job(imap_def, imap_conn, session)
            imap_def['scheduler_job_id'] = job.id

        # Set any opaque attributes
        set_instance_opaque_attrs(imap_conn, imap_def)

        session.add(imap_conn)
        return imap_conn

# ################################################################################################################################

    def sync_imap_definitions(self, imap_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d IMAP connection definitions from YAML', len(imap_list))

        db_defs = self.get_imap_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_imap_defs(imap_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new IMAP connection definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_imap = session.query(IMAP).filter(IMAP.name == item.get('name')).first() # type: ignore
                if existing_imap:
                    logger.info('IMAP connection with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_imap_definition(item, session)
                logger.info('Created IMAP connection definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.imap_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing IMAP connection definitions', len(to_update))
            for item in to_update:
                instance = self.update_imap_definition(item, session)
                logger.info('Updated IMAP connection definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing IMAP connection definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

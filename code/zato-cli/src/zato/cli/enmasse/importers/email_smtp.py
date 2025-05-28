# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.odb.model import SMTP, Cluster, to_json
from zato.common.odb.query import email_smtp_list
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

class SMTPImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.smtp_defs = {}

# ################################################################################################################################

    def _process_smtp_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d SMTP connection definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing SMTP connection definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_smtp_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving SMTP connection definitions from database for cluster_id=%s', cluster_id)
        smtp_connections = email_smtp_list(session, cluster_id)

        self._process_smtp_defs(smtp_connections, out)
        logger.info('Total SMTP connection definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB SMTP connection def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_smtp_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_smtp_definition(self, smtp_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new SMTP connection instance
        smtp_conn = SMTP(cluster)

        # Define attribute values
        name = smtp_def['name']
        is_active = smtp_def.get('is_active', True)
        host = smtp_def['host']
        port = smtp_def['port']
        timeout = smtp_def.get('timeout', 60)
        is_debug = smtp_def.get('is_debug', False)
        mode = smtp_def.get('mode', 'plain')
        ping_address = smtp_def.get('ping_address', '')
        
        # Set attributes
        smtp_conn.name = name
        smtp_conn.is_active = is_active
        smtp_conn.host = host
        smtp_conn.port = port
        smtp_conn.timeout = timeout
        smtp_conn.is_debug = is_debug
        smtp_conn.mode = mode
        smtp_conn.ping_address = ping_address

        # Optional username - empty string if not provided
        smtp_conn.username = smtp_def.get('username', '') or ''

        # Set password if provided, otherwise generate one
        if 'password' in smtp_def:
            smtp_conn.password = smtp_def['password']
        else:
            smtp_conn.password = uuid4().hex

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(smtp_conn, smtp_def)

        # Add to session and flush to get ID
        session.add(smtp_conn)
        session.flush()

        return smtp_conn

# ################################################################################################################################

    def update_smtp_definition(self, smtp_def:'anydict', session:'SASession') -> 'any_':

        smtp_id = smtp_def['id']
        def_name = smtp_def['name']

        logger.info('Updating SMTP connection definition: name=%s id=%s', def_name, smtp_id)

        smtp_conn = session.query(SMTP).filter_by(id=smtp_id).one()

        # Update all attributes provided in YAML
        for key, value in smtp_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type']:

                # Special handling for password - only update if provided
                if key == 'password' and not value:
                    continue

                # Special handling for username - must be empty string not None
                if key == 'username' and value is None:
                    value = ''

                # Set the attribute on the SMTP connection object
                setattr(smtp_conn, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(smtp_conn, smtp_def)

        session.add(smtp_conn)
        return smtp_conn

# ################################################################################################################################

    def sync_smtp_definitions(self, smtp_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d SMTP connection definitions from YAML', len(smtp_list))

        db_defs = self.get_smtp_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_smtp_defs(smtp_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new SMTP connection definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_smtp = session.query(SMTP).filter(SMTP.name == item.get('name')).first()
                if existing_smtp:
                    logger.info('SMTP connection with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_smtp_definition(item, session)
                logger.info('Created SMTP connection definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.smtp_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing SMTP connection definitions', len(to_update))
            for item in to_update:
                instance = self.update_smtp_definition(item, session)
                logger.info('Updated SMTP connection definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing SMTP connection definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

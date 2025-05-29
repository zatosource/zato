# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn, to_json
from zato.common.odb.query.generic import connection_list
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

connection_type = GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE

connection_defaults = {
    'is_active': True,
    'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
    'is_internal': False,
    'is_channel': False,
    'is_outconn': False,
    'is_outgoing': True,
    'pool_size': 20,
    'timeout': 250,
}

connection_extra_field_defaults = {
    'site_url': None,
    'auth_token': None,
    'is_cloud': True,
    'api_version': 'v1',
}

connection_secret_keys = ['password', 'secret', 'api_token']
connection_required_attrs = ['name', 'address', 'username']

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.confluence_defs = {}

# ################################################################################################################################

    def _process_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d connection definitions (%s)', len(definitions), connection_type)

        for item in definitions:
            name = item['name']
            logger.info('Processing connection definition: %s (id=%s) (%s)', name, item.get('id'), connection_type)
            out[name] = item

# ################################################################################################################################

    def get_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving connection definitions from database (%s)', connection_type)
        connections = connection_list(session, cluster_id, connection_type, False)

        self._process_defs(connections, out)
        logger.info('Total connection definitions from DB: %d (%s)', len(out), connection_type)

        for name in out:
            logger.info('DB connection def: name=%s (%s)', name, connection_type)

        return out

# ################################################################################################################################

    def compare_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new generic connection
        connection = GenericConn()
        connection.cluster = cluster

        # Apply defaults unless overridden in YAML
        for key, default_value in connection_defaults.items():
            value = connection_def.get(key, default_value)
            setattr(connection, key, value)

        # Set required fields - they will always exist
        for attr in connection_required_attrs:
            setattr(connection, attr, connection_def[attr])

        for key in connection_secret_keys:
            if key in connection_def and connection_def[key]:
                connection.secret = connection_def[key]
                break

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            if value is not None:
                extra_fields[field] = value

        # Filter out None values
        extra_fields = {key: value for key, value in extra_fields.items() if value is not None}

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(connection, connection_def, extra_fields)

        # Add to session and flush to get ID
        session.add(connection)
        session.flush()

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        connection_id = connection_def['id']
        def_name = connection_def['name']

        logger.info('Updating connection definition (%s): name=%s id=%s', connection_type, def_name, connection_id)

        connection = session.query(GenericConn).filter_by(id=connection_id).one()

        for attr in connection_required_attrs:
            setattr(connection, attr, connection_def[attr])

        for key in connection_secret_keys:
            if key in connection_def and connection_def[key]:
                connection.secret = connection_def[key]
                break

        # Build extra_fields using the defaults
        extra_fields = {}
        for field, default in connection_extra_field_defaults.items():
            value = connection_def.get(field, default)
            if value is not None:
                extra_fields[field] = value

        set_instance_opaque_attrs(connection, connection_def, extra_fields)

        session.add(connection)
        return connection

# ################################################################################################################################

    def sync_definitions(self, conn_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d connection definitions from YAML (%s)', len(conn_list), connection_type)

        db_defs = self.get_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_defs(conn_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new connection definitions (%s)', len(to_create), connection_type)
            for item in to_create:

                # Keep track of things that already exist
                existing_conn = session.query(GenericConn).filter(GenericConn.name==item.get('name'), GenericConn.type_==connection_type).first() # type: ignore

                if existing_conn:
                    logger.info('Connection with name %s already exists, skipping (%s)', item.get('name'), connection_type)
                    continue

                instance = self.create_definition(item, session)
                logger.info('Created connection definition: name=%s id=%s (%s)', instance.name, instance.id, connection_type)
                out_created.append(instance)

                # Store the mapping for future reference
                self.confluence_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing connection definitions (%s)', len(to_update), connection_type)
            for item in to_update:
                instance = self.update_definition(item, session)
                logger.info('Updated connection definition: name=%s id=%s (%s)', instance.name, instance.id, connection_type)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing connection definitions: %s (%s)', e, connection_type)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

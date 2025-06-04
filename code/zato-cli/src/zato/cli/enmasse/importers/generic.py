# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
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

class GenericConnectionImporter:

    connection_type = None
    connection_defaults = {}
    connection_extra_field_defaults = {}
    connection_secret_keys = ['password', 'secret', 'api_token']
    connection_required_attrs = ['name', 'address', 'username']

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

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
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
        return connection

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

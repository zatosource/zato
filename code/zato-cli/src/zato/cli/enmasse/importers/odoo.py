# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.odb.model import OutgoingOdoo, to_json
from zato.common.odb.query import out_odoo_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OdooImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.odoo_defs = {}

# ################################################################################################################################

    def _process_odoo_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d odoo connection definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing odoo connection definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_odoo_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving odoo connection definitions from database for cluster_id=%s', cluster_id)
        odoo_connections = out_odoo_list(session, cluster_id)

        self._process_odoo_defs(odoo_connections, out)
        logger.info('Total odoo connection definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB odoo connection def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_odoo_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_odoo_definition(self, odoo_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new odoo connection instance
        odoo_conn = OutgoingOdoo(cluster)

        # Set default values
        defaults = {
            'is_active': True,
            'protocol': 'jsonrpc',
            'port': 8069,
            'pool_size': 10,
        }

        # Apply defaults unless overridden in YAML
        for key, default_value in defaults.items():
            value = odoo_def.get(key, default_value)
            setattr(odoo_conn, key, value)

        # Required fields
        required_fields = ['name', 'host', 'user', 'database']
        for field in required_fields:
            if field in odoo_def:
                setattr(odoo_conn, field, odoo_def[field])
            else:
                logger.error('Missing required field %s for odoo connection %s', field, odoo_def.get('name', 'unknown'))
                raise ValueError(f'Missing required field {field} for odoo connection')

        # Set password if provided, otherwise generate one
        if 'password' in odoo_def:
            odoo_conn.password = odoo_def['password']
        else:
            odoo_conn.password = uuid4().hex

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(odoo_conn, odoo_def)

        # Add to session and flush to get ID
        session.add(odoo_conn)
        session.flush()

        return odoo_conn

# ################################################################################################################################

    def update_odoo_definition(self, odoo_def:'anydict', session:'SASession') -> 'any_':

        odoo_id = odoo_def['id']
        def_name = odoo_def['name']

        logger.info('Updating odoo connection definition: name=%s id=%s', def_name, odoo_id)

        odoo_conn = session.query(OutgoingOdoo).filter_by(id=odoo_id).one()

        # Update all attributes provided in YAML
        for key, value in odoo_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type']:

                # Special handling for password - only update if provided
                if key == 'password' and not value:
                    continue

                # Set the attribute on the odoo connection object
                setattr(odoo_conn, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(odoo_conn, odoo_def)

        session.add(odoo_conn)
        return odoo_conn

# ################################################################################################################################

    def sync_odoo_definitions(self, odoo_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d odoo connection definitions from YAML', len(odoo_list))

        db_defs = self.get_odoo_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_odoo_defs(odoo_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new odoo connection definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_odoo = session.query(OutgoingOdoo).filter(OutgoingOdoo.name == item.get('name')).first()
                if existing_odoo:
                    logger.info('Odoo connection with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_odoo_definition(item, session)
                logger.info('Created odoo connection definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.odoo_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing odoo connection definitions', len(to_update))
            for item in to_update:
                instance = self.update_odoo_definition(item, session)
                logger.info('Updated odoo connection definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing odoo connection definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

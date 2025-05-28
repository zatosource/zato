# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.odb.model import SQLConnectionPool, Cluster, to_json
from zato.common.odb.query import out_sql_list
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

class SQLImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.sql_defs = {}

# ################################################################################################################################

    def _process_sql_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d SQL connection pool definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing SQL connection pool definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_sql_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving SQL connection pool definitions from database for cluster_id=%s', cluster_id)
        sql_connections = out_sql_list(session, cluster_id)

        self._process_sql_defs(sql_connections, out)
        logger.info('Total SQL connection pool definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB SQL connection pool def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_sql_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_sql_definition(self, sql_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new SQL connection pool instance
        sql_conn = SQLConnectionPool(cluster)

        # Set the basic attributes
        name = sql_def['name']
        is_active = sql_def.get('is_active', True)
        
        # Accept either 'type' or 'engine' field
        engine = sql_def['type'] if 'type' in sql_def else sql_def['engine']
        host = sql_def['host']
        port = sql_def['port']
        db_name = sql_def['db_name']
        username = sql_def['username']
        pool_size = sql_def.get('pool_size', 5)
        
        sql_conn.name = name
        sql_conn.is_active = is_active
        sql_conn.engine = engine
        sql_conn.host = host
        sql_conn.port = port
        sql_conn.db_name = db_name
        sql_conn.username = username
        sql_conn.pool_size = pool_size

        # Convert extra to bytes if provided
        if 'extra' in sql_def:
            sql_conn.extra = sql_def['extra'].encode('utf8') if sql_def['extra'] else b''
        else:
            sql_conn.extra = b''

        # Set password if provided, otherwise generate one
        if 'password' in sql_def:
            sql_conn.password = sql_def['password']
        else:
            sql_conn.password = uuid4().hex

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(sql_conn, sql_def)

        # Add to session and flush to get ID
        session.add(sql_conn)
        session.flush()

        return sql_conn

# ################################################################################################################################

    def update_sql_definition(self, sql_def:'anydict', session:'SASession') -> 'any_':

        sql_id = sql_def['id']
        def_name = sql_def['name']

        logger.info('Updating SQL connection pool definition: name=%s id=%s', def_name, sql_id)

        sql_conn = session.query(SQLConnectionPool).filter_by(id=sql_id).one()

        # Update all attributes provided in YAML
        for key, value in sql_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type']:

                # Special handling for password - only update if provided
                if key == 'password' and not value:
                    continue

                # Special handling for extra field
                if key == 'extra':
                    value = value.encode('utf8') if value else b''

                # Set the attribute on the SQL connection object
                setattr(sql_conn, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(sql_conn, sql_def)

        session.add(sql_conn)
        return sql_conn

# ################################################################################################################################

    def sync_sql_definitions(self, sql_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d SQL connection pool definitions from YAML', len(sql_list))

        db_defs = self.get_sql_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_sql_defs(sql_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new SQL connection pool definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_sql = session.query(SQLConnectionPool).filter(SQLConnectionPool.name == item.get('name')).first()
                if existing_sql:
                    logger.info('SQL connection pool with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_sql_definition(item, session)
                logger.info('Created SQL connection pool definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.sql_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing SQL connection pool definitions', len(to_update))
            for item in to_update:
                instance = self.update_sql_definition(item, session)
                logger.info('Updated SQL connection pool definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing SQL connection pool definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import get_engine_from_type, preprocess_item, SQL_Default_Pool_Size
from zato.common.crypto.api import CryptoManager
from zato.common.odb.model import SQLConnectionPool, to_json
from zato.common.odb.query import out_sql_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple

    # Add dummy assignments to satisfy type checkers
    SASession = SASession
    EnmasseYAMLImporter = EnmasseYAMLImporter
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What a new connection is unless its definition says otherwise.
_default_is_active = True

# What the extra column stores when a definition carries no extra options.
_empty_extra = b''

# ################################################################################################################################
# ################################################################################################################################

class SQLImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.sql_definitions:'anydict' = {}

# ################################################################################################################################

    def _process_sql_defs(self, query_result:'any_', definitions_by_name:'anydict') -> 'None':

        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d SQL connection pool definition(s)', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing SQL connection pool definition: %s (id=%s)', name, item['id'])
            definitions_by_name[name] = item

# ################################################################################################################################

    def get_sql_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':

        # Our response to produce
        out:'anydict' = {}

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

    def create_sql_definition(self, sql_definition:'anydict', session:'SASession') -> 'SQLConnectionPool':

        # The connection belongs to the one cluster there is ..
        cluster = self.importer.get_cluster(session)

        out = SQLConnectionPool()
        out.cluster = cluster

        # .. the user-friendly type maps to the engine name the column stores ..
        connection_type = sql_definition['type']
        engine = get_engine_from_type(connection_type)

        # .. the basic fields every definition carries ..
        out.name      = sql_definition['name']
        out.is_active = sql_definition.get('is_active', _default_is_active)
        out.engine    = engine
        out.host      = sql_definition['host']
        out.port      = sql_definition['port']
        out.db_name   = sql_definition['db_name']
        out.username  = sql_definition['username']
        out.pool_size = sql_definition.get('pool_size', SQL_Default_Pool_Size)

        # .. the 'extra' options are a YAML list, joined into the newline-separated string the column stores ..
        if extra := sql_definition.get('extra'):
            extra = '\n'.join(extra)
            out.extra = extra.encode('utf8')
        else:
            out.extra = _empty_extra

        # .. a definition without a password gets a generated one ..
        if password := sql_definition.get('password'):
            out.password = password
        else:
            out.password = CryptoManager.generate_password(to_str=True)

        # .. whatever else the definition carries goes to the opaque attributes ..
        set_instance_opaque_attrs(out, sql_definition)

        # .. and the flush gives the new connection its ID.
        session.add(out)
        session.flush()

        return out

# ################################################################################################################################

    def update_sql_definition(self, sql_definition:'anydict', session:'SASession') -> 'SQLConnectionPool':

        sql_id = sql_definition['id']
        name = sql_definition['name']

        logger.info('Updating SQL connection pool definition: name=%s id=%s', name, sql_id)

        query = session.query(SQLConnectionPool)
        query = query.filter_by(id=sql_id)
        out = query.one()

        # The plain columns are assigned directly, one by one, if the definition carries them ..
        if 'name' in sql_definition:
            out.name = sql_definition['name']

        if 'is_active' in sql_definition:
            out.is_active = sql_definition['is_active']

        if 'host' in sql_definition:
            out.host = sql_definition['host']

        if 'port' in sql_definition:
            out.port = sql_definition['port']

        if 'db_name' in sql_definition:
            out.db_name = sql_definition['db_name']

        if 'username' in sql_definition:
            out.username = sql_definition['username']

        if 'pool_size' in sql_definition:
            out.pool_size = sql_definition['pool_size']

        # .. the user-friendly type maps to the engine name the column stores ..
        if 'type' in sql_definition:
            connection_type = sql_definition['type']
            out.engine = get_engine_from_type(connection_type)

        # .. a password is updated only if one was actually given ..
        if password := sql_definition.get('password'):
            out.password = password

        # .. the 'extra' options are a YAML list, joined into the newline-separated string the column stores ..
        if 'extra' in sql_definition:
            extra = '\n'.join(sql_definition['extra'])
            out.extra = extra.encode('utf8')

        # .. and whatever else the definition carries goes to the opaque attributes.
        set_instance_opaque_attrs(out, sql_definition)

        session.add(out)

        return out

# ################################################################################################################################

    def sync_sql_definitions(self, sql_list:'anylist', session:'SASession') -> 'listtuple':

        logger.info('Processing %d SQL connection pool definition(s) from YAML', len(sql_list))

        db_defs = self.get_sql_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_sql_defs(sql_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new SQL connection pool definition(s)', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                name = item['name']
                existing_sql = session.query(SQLConnectionPool).filter(SQLConnectionPool.name == name).first()
                if existing_sql:
                    logger.info('SQL connection pool with name %s already exists, skipping', name)
                    continue

                instance = self.create_sql_definition(item, session)
                logger.info('Created SQL connection pool definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.sql_definitions[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing SQL connection pool definition(s)', len(to_update))
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

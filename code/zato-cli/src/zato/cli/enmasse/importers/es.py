# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.common.odb.model import ElasticSearch, to_json
from zato.common.odb.query import search_es_list
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

class ESImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.es_defs = {}

# ################################################################################################################################

    def _process_es_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d ElasticSearch connection definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing ElasticSearch connection definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_es_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving ElasticSearch connection definitions from database for cluster_id=%s', cluster_id)
        es_connections = search_es_list(session, cluster_id)

        self._process_es_defs(es_connections, out)
        logger.info('Total ElasticSearch connection definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB ElasticSearch connection def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_es_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_es_definition(self, es_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new ElasticSearch connection instance
        es_conn = ElasticSearch()
        es_conn.cluster_id = cluster.id

        name = es_def.get('name', '')
        logger.info('Creating ElasticSearch connection definition: %s', name)

        es_conn.name = name
        es_conn.is_active = es_def.get('is_active', True)
        es_conn.hosts = es_def.get('hosts', '')
        es_conn.timeout = es_def.get('timeout', 90)
        es_conn.body_as = es_def.get('body_as', 'json')

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(es_conn, es_def)

        # Add to session and flush to get ID
        session.add(es_conn)
        session.flush()

        return es_conn

# ################################################################################################################################

    def update_es_definition(self, es_def:'anydict', session:'SASession') -> 'any_':

        es_id = es_def['id']
        def_name = es_def['name']

        logger.info('Updating ElasticSearch connection definition: name=%s id=%s', def_name, es_id)

        es_conn = session.query(ElasticSearch).filter_by(id=es_id).one()

        # Update all attributes provided in YAML
        for key, value in es_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'type']:
                # Set the attribute on the ES connection object
                setattr(es_conn, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(es_conn, es_def)

        session.add(es_conn)
        return es_conn

# ################################################################################################################################

    def sync_es_definitions(self, es_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d ElasticSearch connection definitions from YAML', len(es_list))

        db_defs = self.get_es_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_es_defs(es_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new ElasticSearch connection definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_es = session.query(ElasticSearch).filter(ElasticSearch.name == item.get('name')).first() # type: ignore
                if existing_es:
                    logger.info('ElasticSearch connection with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_es_definition(item, session)
                logger.info('Created ElasticSearch connection definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.es_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing ElasticSearch connection definitions', len(to_update))
            for item in to_update:
                instance = self.update_es_definition(item, session)
                logger.info('Updated ElasticSearch connection definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing ElasticSearch connection definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

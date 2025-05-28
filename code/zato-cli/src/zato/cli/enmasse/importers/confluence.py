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

class ConfluenceImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.confluence_defs = {}

# ################################################################################################################################

    def _process_confluence_defs(self, query_result:'any_', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d confluence connection definitions', len(definitions))

        for item in definitions:
            name = item['name']
            logger.info('Processing confluence connection definition: %s (id=%s)', name, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_confluence_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving confluence connection definitions from database for cluster_id=%s', cluster_id)
        confluence_connections = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE, False)

        self._process_confluence_defs(confluence_connections, out)
        logger.info('Total confluence connection definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB confluence connection def: name=%s', name)

        return out

# ################################################################################################################################

    def compare_confluence_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple':

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

    def create_confluence_definition(self, confluence_def:'anydict', session:'SASession') -> 'any_':

        # Get the cluster instance from the importer
        cluster = self.importer.get_cluster(session)

        # Create a new confluence connection instance (using GenericConn)
        confluence_conn = GenericConn(cluster=cluster)

        # Set default values for Confluence connections
        defaults = {
            'is_active': True,
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
            'is_internal': False,
            'is_channel': False,
            'is_outconn': False,
            'is_outgoing': True,
            'pool_size': 20,
            'timeout': 250,
        }

        # Apply defaults unless overridden in YAML
        for key, default_value in defaults.items():
            value = confluence_def.get(key, default_value)
            setattr(confluence_conn, key, value)

        # Set required fields - they will always exist
        confluence_conn.name = confluence_def['name']
        confluence_conn.address = confluence_def['address']
        confluence_conn.username = confluence_def['username']

        # Set secret - will always exist
        confluence_conn.secret = confluence_def.get('password') or confluence_def.get('secret')

        # Additional Confluence-specific fields for opaque attributes
        extra_fields = {
            'site_url': confluence_def.get('site_url'),
            'auth_token': confluence_def.get('auth_token'),
            'is_cloud': confluence_def.get('is_cloud', True),
            'api_version': confluence_def.get('api_version', 'v1'),
        }

        # Filter out None values
        extra_fields = {key: value for key, value in extra_fields.items() if value is not None}

        # Set any opaque attributes from the configuration
        set_instance_opaque_attrs(confluence_conn, confluence_def, extra_fields)

        # Add to session and flush to get ID
        session.add(confluence_conn)
        session.flush()

        return confluence_conn

# ################################################################################################################################

    def update_confluence_definition(self, confluence_def:'anydict', session:'SASession') -> 'any_':

        confluence_id = confluence_def['id']
        def_name = confluence_def['name']

        logger.info('Updating confluence connection definition: name=%s id=%s', def_name, confluence_id)

        confluence_conn = session.query(GenericConn).filter_by(id=confluence_id).one()

        confluence_conn.name = confluence_def['name']
        confluence_conn.address = confluence_def['address']
        confluence_conn.username = confluence_def['username']

        # Set secret - will always exist
        confluence_conn.secret = confluence_def.get('password') or confluence_def.get('secret')

        # Set opaque attributes
        extra_fields = {
            'site_url': confluence_def.get('site_url'),
            'auth_token': confluence_def.get('auth_token'),
            'is_cloud': confluence_def.get('is_cloud', True),
            'api_version': confluence_def.get('api_version', 'v1'),
        }

        # Filter out None values
        extra_fields = {k: v for k, v in extra_fields.items() if v is not None}

        set_instance_opaque_attrs(confluence_conn, confluence_def, extra_fields)

        session.add(confluence_conn)
        return confluence_conn

# ################################################################################################################################

    def sync_confluence_definitions(self, confluence_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d confluence connection definitions from YAML', len(confluence_list))

        db_defs = self.get_confluence_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_confluence_defs(confluence_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new confluence connection definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_confluence = session.query(GenericConn).filter(GenericConn.name == item.get('name'), GenericConn.type_ == GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE).first() # type: ignore

                if existing_confluence:
                    logger.info('Confluence connection with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_confluence_definition(item, session)
                logger.info('Created confluence connection definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.confluence_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                }

            logger.info('Updating %d existing confluence connection definitions', len(to_update))
            for item in to_update:
                instance = self.update_confluence_definition(item, session)
                logger.info('Updated confluence connection definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing confluence connection definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

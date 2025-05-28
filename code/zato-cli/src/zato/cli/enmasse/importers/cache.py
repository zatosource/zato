# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import CacheBuiltin, to_json
from zato.common.odb.query import cache_builtin_list
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

class CacheImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':

        self.importer = importer
        self.cache_defs = {}
        self._id_counter = 1

# ################################################################################################################################

    def _process_cache_defs(self, query_result:'any_', cache_type:'str', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d %s cache definitions', len(definitions), cache_type)

        for item in definitions:
            item['type'] = cache_type
            name = item['name']
            logger.info('Processing cache definition: %s (type=%s, id=%s)', name, cache_type, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_cache_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving cache definitions from database for cluster_id=%s', cluster_id)
        builtin_cache = cache_builtin_list(session, cluster_id)

        self._process_cache_defs(builtin_cache, 'builtin', out)
        logger.info('Total cache definitions from DB: %d', len(out))

        for name, details in out.items():
            logger.info('DB cache def: name=%s type=%s', name, details.get('type'))

        return out

# ################################################################################################################################

    def compare_cache_defs(self, yaml_defs:'anylist', db_defs:'anylist') -> 'tuple':

        # Build dictionaries for easier lookup
        yaml_dict = {}
        for d in yaml_defs:
            yaml_dict[d['name']] = d

        db_dict = {}
        for d in db_defs:
            db_dict[d['name']] = d

        # Find items to create and update
        to_create = []
        to_update = []

        for name, yaml_def in yaml_dict.items():
            if name in db_dict:
                # Update existing definition
                update_def = yaml_def.copy()
                update_def['id'] = db_dict[name]['id']
                logger.info('Adding to update: %s', update_def)
                to_update.append(update_def)
            else:
                # Create new definition
                logger.info('Adding to create: %s', yaml_def)
                to_create.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def _create_builtin_cache(self, cache_def:'anydict', cluster:'any_') -> 'any_':

        cache = CacheBuiltin(cluster)
        cache.cache_type = 'builtin'

        # Set default values
        defaults = {
            'is_active': True,
            'is_default': False,
            'max_size': 10000,
            'max_item_size': 1000000,
            'extend_expiry_on_get': True,
            'extend_expiry_on_set': False,
            'sync_method': 'in-background',
            'persistent_storage': 'sqlite'
        }

        for key, default_value in defaults.items():

            value = cache_def.get(key, default_value)
            setattr(cache, key, value)

        # Ensure name is set (required)
        cache.name = cache_def['name']

        # Set any opaque attributes
        set_instance_opaque_attrs(cache, cache_def)

        return cache

# ################################################################################################################################

    def create_cache_definition(self, cache_def:'anydict', session:'SASession') -> 'any_':
        def_name = cache_def.get('name', 'unnamed')
        logger.info('Creating cache definition: name=%s', def_name)

        # Create builtin cache directly
        cache = CacheBuiltin()

        # Set required attributes
        cache.cluster_id = int(self.importer.cluster_id)
        cache.name = def_name
        cache.cache_type = 'builtin'
        cache.is_active = cache_def.get('is_active', True)
        cache.is_default = cache_def.get('is_default', False)

        # Set CacheBuiltin-specific attributes
        cache.max_size = cache_def.get('max_size', 10000)
        cache.max_item_size = cache_def.get('max_item_size', 1000000)
        cache.extend_expiry_on_get = cache_def.get('extend_expiry_on_get', True)
        cache.extend_expiry_on_set = cache_def.get('extend_expiry_on_set', False)

        # Set additional attributes
        cache.sync_method = cache_def.get('sync_method', 'in-background')
        cache.persistent_storage = cache_def.get('persistent_storage', 'sqlite')

        # Set opaque attributes from the configuration
        set_instance_opaque_attrs(cache, cache_def)

        # Add to session and flush to get ID
        session.add(cache)
        session.flush()

        # Only add to session once
        return cache

# ################################################################################################################################

    def update_cache_definition(self, cache_def:'anydict', session:'SASession') -> 'any_':

        cache_id = cache_def['id']
        def_name = cache_def['name']

        logger.info('Updating cache definition: name=%s id=%s', def_name, cache_id)

        cache = session.query(CacheBuiltin).filter_by(id=cache_id).one()

        # Update all attributes provided in YAML
        for key, value in cache_def.items():

            # Skip special fields that shouldn't be directly updated
            if key not in ['id', 'cache_id']:

                # Set the attribute on the cache object
                setattr(cache, key, value)

        # Set any opaque attributes
        set_instance_opaque_attrs(cache, cache_def)

        session.add(cache)
        return cache

# ################################################################################################################################

    def sync_cache_definitions(self, cache_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d cache definitions from YAML', len(cache_list))

        db_defs = self.get_cache_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_cache_defs(cache_list, db_defs)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new cache definitions', len(to_create))
            for item in to_create:

                # Keep track of things that already exist
                existing_cache = session.query(Cache).filter(Cache.name == item.get('name')).first()
                if existing_cache:
                    logger.info('Cache with name %s already exists, skipping', item.get('name'))
                    continue

                instance = self.create_cache_definition(item, session)
                logger.info('Created cache definition: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

                # Store the mapping for future reference
                self.cache_defs[instance.name] = {
                    'id': instance.id,
                    'name': instance.name,
                    'type': instance.cache_type
                }

            logger.info('Updating %d existing cache definitions', len(to_update))
            for item in to_update:
                instance = self.update_cache_definition(item, session)
                logger.info('Updated cache definition: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing cache definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################

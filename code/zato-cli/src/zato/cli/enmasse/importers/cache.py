# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import Cache, CacheBuiltin, to_json
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

    def compare_cache_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML defs with %d DB defs', len(yaml_defs), len(db_defs))
        logger.info('DB definition keys: %s', list(db_defs.keys()))

        for item in yaml_defs:
            name = item['name']

            logger.info('Checking YAML def: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Definition %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Definition %s exists in DB with id=%s type=%s', name, db_def.get('id'), db_def.get('type'))

                needs_update = False
                for key, value in item.items():
                    if key in ('type', 'name'):
                        continue

                    if key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                if needs_update:
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
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
        cluster = self.importer.get_cluster(session)

        cache = self._create_builtin_cache(cache_def, cluster)
        session.add(cache)
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
                logger.info('Creating cache definition: name=%s', item.get('name'))
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
                logger.info('Updating cache definition: name=%s id=%s', item.get('name'), item.get('id'))
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

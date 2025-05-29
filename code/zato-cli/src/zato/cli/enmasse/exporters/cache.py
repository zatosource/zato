# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import CacheBuiltin
from zato.common.odb.query import cache_builtin_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CacheExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_cache_definitions(self, session:'SASession') -> 'list':
        """ Export cache definitions from the database.
        """
        logger.info('Exporting cache definitions from cluster_id=%s', self.exporter.cluster_id)
        
        # Get cache definitions from the database
        cache_items = cache_builtin_list(session, self.exporter.cluster_id)
        
        cache_defs = []
        
        for cache in cache_items:
            logger.info('Processing cache: %s', cache.name)
            
            # Create a dictionary representation of the cache definition
            cache_def = {
                'name': cache.name,
                'is_active': cache.is_active,
                'is_default': cache.is_default,
                'max_size': cache.max_size,
                'max_item_size': cache.max_item_size,
                'extend_expiry_on_get': cache.extend_expiry_on_get,
                'extend_expiry_on_set': cache.extend_expiry_on_set,
                'sync_method': cache.sync_method,
                'persistent_storage': cache.persistent_storage
            }
            
            # Store in exporter's cache definitions
            self.exporter.cache_defs[cache.name] = {
                'id': cache.id,
                'name': cache.name
            }
            
            # Add to results
            cache_defs.append(cache_def)
            
        logger.info('Exported %d cache definitions', len(cache_defs))
        return cache_defs

# ################################################################################################################################
# ################################################################################################################################

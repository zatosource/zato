# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.query import cache_builtin_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession

    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.odb.model import CacheBuiltin
    from zato.common.typing_ import anydict, list_

    # Define collection types for type hinting
    cache_def_list = list_[anydict]
    db_cache_list = list_[CacheBuiltin]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CacheExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'cache_def_list':
        """ Exports cache definitions.
        """
        logger.info('Exporting cache definitions')

        # Names to exclude completely
        excluded_names = {'default', 'zato.bearer.token'}

        db_caches:'db_cache_list' = cache_builtin_list(session, cluster_id, False)

        if not db_caches:
            logger.info('No cache definitions found in DB')
            return []

        exported_caches:'cache_def_list' = []

        for cache_item in db_caches.result:

            # Skip excluded cache definitions
            if cache_item.name in excluded_names:
                continue

            item = {
                'name': cache_item.name,
                'extend_expiry_on_get': cache_item.extend_expiry_on_get,
                'extend_expiry_on_set': cache_item.extend_expiry_on_set,
            }

            exported_caches.append(item)

        logger.info('Successfully prepared %d cache definitions for export', len(exported_caches))

        return exported_caches

# ################################################################################################################################
# ################################################################################################################################

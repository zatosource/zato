# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    cache_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CacheExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'cache_def_list':
        """ Exports cache definitions.
        """
        logger.info('Exporting cache definitions')

        # Names to exclude completely
        excluded_names = {'default', 'zato.bearer.token'}

        if not items:
            logger.info('No cache definitions found')
            return []

        exported_caches = []

        for cache_item in items:

            # Skip excluded cache definitions
            if cache_item['name'] in excluded_names:
                continue

            item = {
                'name': cache_item['name'],
                'extend_expiry_on_get': cache_item['extend_expiry_on_get'],
                'extend_expiry_on_set': cache_item['extend_expiry_on_set'],
            }

            exported_caches.append(item)

        logger.info('Successfully prepared %d cache definitions for export', len(exported_caches))

        return exported_caches

# ################################################################################################################################
# ################################################################################################################################

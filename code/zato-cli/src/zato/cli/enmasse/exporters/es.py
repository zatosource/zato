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
    from zato.common.typing_ import list_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ElasticSearchExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, items) -> 'list_':
        """ Exports all ElasticSearch connection definitions.
        """
        logger.info('Exporting ElasticSearch connection definitions')

        if not items:
            logger.info('No ElasticSearch connection definitions found')
            return []

        logger.debug('Processing %d ElasticSearch connection definitions', len(items))

        out = []

        for es_item in items:

            item = {
                'name': es_item['name'],
                'hosts': es_item.get('hosts', ''),
                'is_active': es_item.get('is_active', True),
                'body_as': es_item.get('body_as', ''),
            }

            if (timeout := es_item.get('timeout')) and timeout != 90:
                item['timeout'] = timeout

            out.append(item)

        logger.info('Successfully prepared %d ElasticSearch connection definitions for export', len(out))

        return out

# ################################################################################################################################
# ################################################################################################################################

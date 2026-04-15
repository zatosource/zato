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
    pubsub_permission_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubPermissionExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'pubsub_permission_def_list':
        """ Exports pub/sub permission definitions.
        """
        logger.info('Exporting pub/sub permission definitions')

        exported_permissions = []

        for item in items:

            exported_permission = {
                'security': item['security'],
            }

            pub_topics = item.get('pub_topics') or item.get('pub') or []
            sub_topics = item.get('sub_topics') or item.get('sub') or []

            if pub_topics:
                exported_permission['pub'] = pub_topics

            if sub_topics:
                exported_permission['sub'] = sub_topics

            if 'pub' in exported_permission or 'sub' in exported_permission:
                exported_permissions.append(exported_permission)

        logger.info('Successfully prepared %d pub/sub permission definitions for export', len(exported_permissions))
        return exported_permissions

# ################################################################################################################################
# ################################################################################################################################

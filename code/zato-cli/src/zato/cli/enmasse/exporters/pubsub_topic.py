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
    pubsub_topic_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTopicExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'pubsub_topic_def_list':
        """ Exports pub/sub topic definitions.
        """
        logger.info('Exporting pub/sub topic definitions')

        exported_topics = []

        for item in items:

            exported_topic = {
                'name': item['name'],
            }

            if item.get('description'):
                exported_topic['description'] = item['description']

            exported_topics.append(exported_topic)

        logger.info('Successfully prepared %d pub/sub topic definitions for export', len(exported_topics))
        return exported_topics

# ################################################################################################################################
# ################################################################################################################################

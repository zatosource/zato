# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.query import pubsub_topic_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    pubsub_topic_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTopicExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'pubsub_topic_def_list':
        """ Exports pub/sub topic definitions.
        """
        logger.info('Exporting pub/sub topic definitions')

        exported_topics: 'pubsub_topic_def_list' = []

        # Get pub/sub topics from database
        query_result = pubsub_topic_list(session, cluster_id, needs_columns=False)

        search_results = query_result[0]
        items = search_results.result

        for item in items:

            item = item._asdict()
            item = item['PubSubTopic']

            # Create basic topic definition with required fields
            exported_topic: 'anydict' = {
                'name': item.name,
            }

            # Add description if present
            if item.description:
                exported_topic['description'] = item.description

            exported_topics.append(exported_topic)

        logger.info('Successfully prepared %d pub/sub topic definitions for export', len(exported_topics))
        return exported_topics

# ################################################################################################################################
# ################################################################################################################################

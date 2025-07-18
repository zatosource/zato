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

        # Get pub/sub topics from database
        db_topics = pubsub_topic_list(session, cluster_id, needs_columns=False)

        if not db_topics:
            logger.info('No pub/sub topic definitions found in DB')
            return []

        exported_topics: 'pubsub_topic_def_list' = []

        for topic_row in db_topics:
            topic_dict = topic_row.asdict()

            if not topic_dict['name'].startswith('enmasse'):
                continue

            # Create basic topic definition with required fields
            exported_topic: 'anydict' = {
                'name': topic_dict['name'],
            }

            # Add description if present
            if description := topic_dict.get('description'):
                exported_topic['description'] = description

            exported_topics.append(exported_topic)

        logger.info('Successfully prepared %d pub/sub topic definitions for export', len(exported_topics))
        return exported_topics

# ################################################################################################################################
# ################################################################################################################################

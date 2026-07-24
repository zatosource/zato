# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    slack_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SlackExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'slack_def_list':
        """ Exports Slack connection definitions.
        """
        logger.info('Exporting Slack connection definitions')

        # Get Slack connections from database using the generic connection query
        db_slack = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHAT_SLACK)

        if not db_slack:
            logger.info('No Slack connection definitions found in DB')
            return []

        slack_connections = to_json(db_slack, return_as_dict=True)
        logger.debug('Processing %d Slack connection definitions', len(slack_connections))

        exported_slack = []

        for row in slack_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
                'is_active': row['is_active']
            }

            exported_slack.append(item)

        logger.info('Successfully prepared %d Slack connection definitions for export', len(exported_slack))
        return exported_slack

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    jira_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class JiraExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'jira_def_list':
        """ Exports JIRA connection definitions.
        """
        logger.info('Exporting JIRA connection definitions')

        # Get JIRA connections from database using the generic connection query
        db_jira = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_JIRA)

        if not db_jira:
            logger.info('No JIRA connection definitions found in DB')
            return []

        jira_connections = to_json(db_jira, return_as_dict=True)
        logger.info('Processing %d JIRA connection definitions', len(jira_connections))

        exported_jira = []

        for row in jira_connections:
            # Get the base connection details
            item = {
                'name': row['name'],
                'is_active': row['is_active'],
                'address': row['address'],
                'username': row['username'],
            }

            # Add optional fields if present
            for field in ['timeout', 'is_cloud', 'api_version']:
                if field in row and row[field] is not None:
                    item[field] = row[field]

            # Process any opaque attributes
            if 'opaque_attr' in row and row['opaque_attr']:
                opaque = parse_instance_opaque_attr(row)
                item.update(opaque)

            exported_jira.append(item)

        logger.info('Successfully prepared %d JIRA connection definitions for export', len(exported_jira))
        return exported_jira

# ################################################################################################################################
# ################################################################################################################################

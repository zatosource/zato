# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import GenericConn
from zato.common.odb.query import generic_connection_list

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

class JiraExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_jira_definitions(self, session:'SASession') -> 'list':
        """ Export Jira connection definitions from the database.
        """
        logger.info('Exporting Jira connections from cluster_id=%s', self.exporter.cluster_id)

        # Get Jira connections from the database
        jira_connections = generic_connection_list(session, self.exporter.cluster_id, 'cloud-jira')

        jira_defs = []

        for conn in jira_connections:
            logger.info('Processing Jira connection: %s', conn.name)

            # Create a dictionary representation of the Jira connection
            jira_def = {
                'name': conn.name,
                'is_active': conn.is_active,
                'address': conn.address,
                'username': conn.username
            }

            # Add api_version if not default
            if conn.api_version != 'v2':
                jira_def['api_version'] = conn.api_version

            # Add is_cloud if not default
            if not conn.is_cloud:
                jira_def['is_cloud'] = False

            # Store in exporter's Jira definitions
            self.exporter.jira_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            jira_defs.append(jira_def)

        logger.info('Exported %d Jira connections', len(jira_defs))
        return jira_defs

# ################################################################################################################################
# ################################################################################################################################

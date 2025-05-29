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

class ConfluenceExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_confluence_definitions(self, session:'SASession') -> 'list':
        """ Export Confluence connection definitions from the database.
        """
        logger.info('Exporting Confluence connections from cluster_id=%s', self.exporter.cluster_id)

        # Get Confluence connections from the database
        confluence_connections = generic_connection_list(session, self.exporter.cluster_id, 'cloud-confluence')

        confluence_defs = []

        for conn in confluence_connections:
            logger.info('Processing Confluence connection: %s', conn.name)

            # Create a dictionary representation of the Confluence connection
            confluence_def = {
                'name': conn.name,
                'is_active': conn.is_active,
                'address': conn.address,
                'username': conn.username
            }

            # Add api_version if not default
            if conn.api_version != 'v1':
                confluence_def['api_version'] = conn.api_version

            # Add is_cloud if not default
            if not conn.is_cloud:
                confluence_def['is_cloud'] = False

            # Store in exporter's Confluence definitions
            self.exporter.confluence_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            confluence_defs.append(confluence_def)

        logger.info('Exported %d Confluence connections', len(confluence_defs))
        return confluence_defs

# ################################################################################################################################
# ################################################################################################################################

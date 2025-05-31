# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    confluence_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Direct fields from the GenericConn model
DIRECT_FIELDS = [
    'name', 'is_active', 'timeout', 'pool_size', 'address', 'username'
]

# Fields that are stored in opaque1 JSON attribute
OPAQUE_FIELDS = [
    'site_url', 'auth_token', 'is_cloud', 'api_version', 'api_token'
]

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'confluence_def_list':
        """ Exports Confluence connection definitions.
        """
        logger.info('Exporting Confluence connection definitions')

        # Get Confluence connections from database using the generic connection query
        db_confluence = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE)

        if not db_confluence:
            logger.info('No Confluence connection definitions found in DB')
            return []

        confluence_connections = to_json(db_confluence, return_as_dict=True)
        logger.info('Processing %d Confluence connection definitions', len(confluence_connections))

        exported_confluence = []

        for row in confluence_connections:
            # Get all direct fields from the connection definition
            item = {}

            # Extract all direct fields that exist in the database model
            for field in DIRECT_FIELDS:
                if (value := row.get(field)) is not None:
                    item[field] = value

            # Process any opaque attributes using walrus operator
            # When working with a dictionary, we need to extract opaque fields directly
            if (opaque_json := row.get('opaque1')):
                try:
                    opaque = loads(opaque_json)
                    # Add relevant fields from opaque data
                    for field in OPAQUE_FIELDS:
                        if (value := opaque.get(field)) is not None:
                            item[field] = value
                except Exception as e:
                    logger.warning('Error processing opaque attributes: %s', e)

            exported_confluence.append(item)

        logger.info('Successfully prepared %d Confluence connection definitions for export', len(exported_confluence))
        return exported_confluence

# ################################################################################################################################
# ################################################################################################################################

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
        logger.debug('Processing %d Confluence connection definitions', len(confluence_connections))

        exported_confluence = []

        for row in confluence_connections:
            # Process opaque attributes first
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
                'username': row['username'],
                'address': row['address'],
                'api_version': row['api_version'],
                'is_active': row['is_active']
            }

            if site_url := row.get('site_url'):
                item['site_url'] = site_url

            if row.get('is_cloud') is True:
                item['is_cloud'] = True

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            exported_confluence.append(item)

        logger.info('Successfully prepared %d Confluence connection definitions for export', len(exported_confluence))
        return exported_confluence

# ################################################################################################################################
# ################################################################################################################################

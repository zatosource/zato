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
from zato.common.util.sql import parse_instance_opaque_attr

# Create logger for this module
logger = logging.getLogger(__name__)

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    microsoft_365_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from connection definitions
OPTIONAL_FIELDS = [
    'timeout', 'pool_size', 'recv_timeout', 'is_active'
]

# Fields to extract from opaque attributes
OPAQUE_FIELDS = [
    'tenant_id', 'client_id', 'scopes', 'secret_value'
]

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Exporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'microsoft_365_def_list':
        """ Exports Microsoft 365 connection definitions.
        """
        logger.info('Exporting Microsoft 365 connection definitions')

        # Get Microsoft 365 connections from database using the generic connection query
        db_microsoft_365 = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365)

        if not db_microsoft_365:
            logger.info('No Microsoft 365 connection definitions found in DB')
            return []

        microsoft_365_connections = to_json(db_microsoft_365, return_as_dict=True)
        logger.debug('Processing %d Microsoft 365 connection definitions', len(microsoft_365_connections))

        exported_microsoft_365 = []

        for row in microsoft_365_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name']
            }

            if client_id := row.get('client_id'):
                item['client_id'] = client_id

            if tenant_id := row.get('tenant_id'):
                item['tenant_id'] = tenant_id

            if scopes := row.get('scopes'):
                lines = scopes.splitlines()
                clean_scopes = [line.strip() for line in lines if line.strip()]

                if clean_scopes:
                    item['scopes'] = clean_scopes

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            if recv_timeout := row.get('recv_timeout'):
                item['recv_timeout'] = recv_timeout

            exported_microsoft_365.append(item)

        logger.info('Successfully prepared %d Microsoft 365 connection definitions for export', len(exported_microsoft_365))
        return exported_microsoft_365

# ################################################################################################################################
# ################################################################################################################################

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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    microsoft_fabric_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'microsoft_fabric_def_list':
        """ Exports Microsoft Fabric connection definitions.
        """
        logger.info('Exporting Microsoft Fabric connection definitions')

        # Get Microsoft Fabric connections from database using the generic connection query
        db_connections = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC)

        if not db_connections:
            logger.info('No Microsoft Fabric connection definitions found in DB')
            return []

        connections = to_json(db_connections, return_as_dict=True)
        logger.debug('Processing %d Microsoft Fabric connection definitions', len(connections))

        exported_connections = []

        for row in connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
                'is_active': row['is_active']
            }

            if address := row.get('address'):
                item['address'] = address

            if client_id := row.get('client_id'):
                item['client_id'] = client_id

            if tenant_id := row.get('tenant_id'):
                item['tenant_id'] = tenant_id

            if token_url := row.get('token_url'):
                item['token_url'] = token_url

            if onelake_address := row.get('onelake_address'):
                item['onelake_address'] = onelake_address

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            if recv_timeout := row.get('recv_timeout'):
                item['recv_timeout'] = recv_timeout

            exported_connections.append(item)

        count = len(exported_connections)
        suffix = 'definition' if count == 1 else 'definitions'
        logger.info('Successfully prepared %d Microsoft Fabric connection %s for export', count, suffix)

        return exported_connections

# ################################################################################################################################
# ################################################################################################################################

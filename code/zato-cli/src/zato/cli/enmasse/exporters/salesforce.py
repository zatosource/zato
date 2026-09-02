# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, SALESFORCE
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    salesforce_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SalesforceExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'salesforce_def_list':
        """ Exports Salesforce connection definitions.
        """
        logger.info('Exporting Salesforce connection definitions')

        # Get Salesforce connections from database using the generic connection query
        db_salesforce = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE)

        if not db_salesforce:
            logger.info('No Salesforce connection definitions found in DB')
            return []

        salesforce_connections = to_json(db_salesforce, return_as_dict=True)

        connection_count = len(salesforce_connections)
        connection_noun = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d Salesforce connection %s', connection_count, connection_noun)

        out = []

        for row in salesforce_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create connection entry with proper field order
            item = {
                'name': row['name'],
                'address': row['address'],
                'username': row['username'],
            }

            # The API version is exported only when it differs from the default
            api_version = row['api_version']
            if api_version != SALESFORCE.Default.API_Version:
                item['api_version'] = api_version

            out.append(item)

        exported_count = len(out)
        exported_noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d Salesforce connection %s for export', exported_count, exported_noun)

        return out

# ################################################################################################################################
# ################################################################################################################################

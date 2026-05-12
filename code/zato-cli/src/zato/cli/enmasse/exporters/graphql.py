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

    graphql_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

OUTGOING_OPTIONAL_FIELDS = [
    'default_query_timeout',
    'extra',
    'security_name',
]

# ################################################################################################################################
# ################################################################################################################################

class OutgoingGraphQLExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'graphql_def_list':
        """ Exports GraphQL outgoing definitions.
        """
        logger.info('Exporting GraphQL outgoing definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL)

        if not db_items:
            logger.info('No GraphQL outgoing definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d GraphQL outgoing definitions', len(connections))

        exported = []

        for row in connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
            }

            if address := row.get('address'):
                item['address'] = address

            for field in OUTGOING_OPTIONAL_FIELDS:
                if value := row.get(field):
                    item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d GraphQL outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################

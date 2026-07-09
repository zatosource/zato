# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, ODATA
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    odata_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The optional fields exported only when they hold non-default values.
Optional_Fields = ['username', 'token_url', 'tenant_id', 'client_id', 'scopes', 'needs_csrf_token', 'page_size',
    'timeout', 'pool_size']

# What each optional field defaults to - values equal to these are not exported.
Field_Defaults = {
    'username': '',
    'token_url': '',
    'tenant_id': '',
    'client_id': '',
    'scopes': '',
    'needs_csrf_token': False,
    'page_size': ODATA.DEFAULT.PAGE_SIZE,
    'timeout': ODATA.DEFAULT.TIMEOUT,
    'pool_size': ODATA.DEFAULT.POOL_SIZE,
}

# ################################################################################################################################
# ################################################################################################################################

class ODataExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'odata_def_list':
        """ Exports OData connection definitions.
        """
        logger.info('Exporting OData connection definitions')

        # Get OData connections from database using the generic connection query
        db_odata = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_ODATA)

        if not db_odata:
            logger.info('No OData connection definitions found in DB')
            return []

        odata_connections = to_json(db_odata, return_as_dict=True)
        logger.debug('Processing %d OData connection definitions', len(odata_connections))

        exported_odata = []

        for row in odata_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base OData connection entry with fields in import order
            item = {
                'name': row['name'],
                'address': row['address'],
            }

            if odata_version := row.get('odata_version'):
                item['odata_version'] = odata_version

            if auth_type := row.get('auth_type'):
                item['auth_type'] = auth_type

            # Only add fields that do not hold default values
            for field in Optional_Fields:
                value = row.get(field)
                if value:
                    default = Field_Defaults[field]
                    if value != default:
                        item[field] = value

            exported_odata.append(item)

        logger.info('Successfully prepared %d OData connection definitions for export', len(exported_odata))
        return exported_odata

# ################################################################################################################################
# ################################################################################################################################

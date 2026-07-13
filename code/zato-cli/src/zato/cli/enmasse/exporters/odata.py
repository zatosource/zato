# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, ODATA, ODATA_Subtype
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
    """ One exporter serves every subtype of the OData implementation - the exporter is registered
    once per subtype, e.g. under the odata key and under the sap key.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter', subtype:'str') -> 'None':
        self.exporter = exporter
        self.subtype = ODATA_Subtype[subtype]

        # Values equal to the subtype defaults are not exported.
        self.field_defaults = dict(Field_Defaults)
        self.field_defaults['needs_csrf_token'] = self.subtype['needs_csrf_token']

    def export(self, session: 'SASession', cluster_id: 'int') -> 'odata_def_list':
        """ Exports connection definitions of this exporter's subtype.
        """
        label = self.subtype['label']
        logger.info('Exporting %s connection definitions', label)

        # Get the connections from database using the generic connection query
        db_odata = connection_list(session, cluster_id, self.subtype['type_'])

        if not db_odata:
            logger.info('No %s connection definitions found in DB', label)
            return []

        odata_connections = to_json(db_odata, return_as_dict=True)
        logger.debug('Processing %d %s connection definitions', len(odata_connections), label)

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
                    default = self.field_defaults[field]
                    if value != default:
                        item[field] = value

            exported_odata.append(item)

        logger.info('Successfully prepared %d %s connection definitions for export', len(exported_odata), label)
        return exported_odata

# ################################################################################################################################
# ################################################################################################################################

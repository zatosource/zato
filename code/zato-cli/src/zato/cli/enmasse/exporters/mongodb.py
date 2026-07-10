# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, MongoDB
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    mongodb_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from opaque attributes, in the order they are exported
OPTIONAL_FIELDS = [
    'auth_source',
    'replica_set',
    'app_name',
    'pool_size_max',
    'connect_timeout',
    'server_select_timeout',
    'is_tls_enabled',
    'tls_ca_certs_file',
    'tls_cert_key_file',
    'is_tls_validation_enabled',
]

# Values that are not exported because they match the defaults
_field_defaults = {
    'auth_source': MongoDB.Default.Auth_Source,
    'replica_set': '',
    'app_name': MongoDB.Default.App_Name,
    'pool_size_max': MongoDB.Default.Pool_Size_Max,
    'connect_timeout': MongoDB.Default.Connect_Timeout,
    'server_select_timeout': MongoDB.Default.Server_Select_Timeout,
    'is_tls_enabled': False,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
    'is_tls_validation_enabled': True,
}

# ################################################################################################################################
# ################################################################################################################################

class MongoDBExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'mongodb_def_list':
        """ Exports MongoDB connection definitions.
        """
        logger.info('Exporting MongoDB connection definitions')

        # Get MongoDB connections from database using the generic connection query
        db_mongodb = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB)

        if not db_mongodb:
            logger.info('No MongoDB connection definitions found in DB')
            return []

        mongodb_connections = to_json(db_mongodb, return_as_dict=True)
        logger.debug('Processing %d MongoDB connection definitions', len(mongodb_connections))

        exported_mongodb = []

        for row in mongodb_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base MongoDB connection entry with fields in import order
            item = {
                'name': row['name'],
            }

            if server_list := row.get('server_list'):
                item['server_list'] = server_list

            if username := row.get('username'):
                item['username'] = username

            # Only add optional fields that do not match the defaults - note that the password
            # is never exported because secrets do not leave the database in plain text.
            for field in OPTIONAL_FIELDS:
                value = row.get(field)
                if value is None:
                    continue
                default = _field_defaults[field]
                if value != default:
                    item[field] = value

            exported_mongodb.append(item)

        logger.info('Successfully prepared %d MongoDB connection definitions for export', len(exported_mongodb))
        return exported_mongodb

# ################################################################################################################################
# ################################################################################################################################

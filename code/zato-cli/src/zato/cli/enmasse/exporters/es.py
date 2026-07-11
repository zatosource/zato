# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import ES, GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    es_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from opaque attributes, in the order they are exported
OPTIONAL_FIELDS = [
    'timeout',
    'is_tls_validation_enabled',
    'tls_ca_certs_file',
    'tls_cert_key_file',
]

# Values that are not exported because they match the defaults
_field_defaults = {
    'timeout': ES.Default.Timeout,
    'is_tls_validation_enabled': True,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
}

# ################################################################################################################################
# ################################################################################################################################

class ElasticSearchExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'es_def_list':
        """ Exports Elasticsearch connection definitions.
        """
        logger.info('Exporting Elasticsearch connection definitions')

        # Get Elasticsearch connections from database using the generic connection query
        db_es = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_ES)

        if not db_es:
            logger.info('No Elasticsearch connection definitions found in DB')
            return []

        es_connections = to_json(db_es, return_as_dict=True)
        logger.debug('Processing %d Elasticsearch connection definitions', len(es_connections))

        exported_es = []

        for row in es_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base Elasticsearch connection entry with fields in import order
            item = {
                'name': row['name'],
            }

            if address_list := row.get('address_list'):
                item['address_list'] = address_list

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

            exported_es.append(item)

        logger.info('Successfully prepared %d Elasticsearch connection definitions for export', len(exported_es))
        return exported_es

# ################################################################################################################################
# ################################################################################################################################

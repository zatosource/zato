# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    outgoing_rest_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingRESTExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'outgoing_rest_def_list':
        """ Exports outgoing REST connection definitions.
        """
        logger.info('Exporting outgoing REST connection definitions')

        # Get outgoing REST connections from database
        db_outgoing = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.PLAIN_HTTP,
            return_internal=False,
        )
        db_outgoing = to_json(db_outgoing)

        if not db_outgoing:
            logger.info('No outgoing REST connection definitions found in DB')
            return []

        exported_outgoing: 'outgoing_rest_def_list' = []
        logger.info('Processing %d outgoing REST connection definitions', len(db_outgoing))

        for outgoing_row in db_outgoing:
            
            # Handle both object and dictionary types
            if hasattr(outgoing_row, 'toDict'):
                logger.info('Processing outgoing REST connection row %s', outgoing_row.toDict())
                row_data = outgoing_row
            else:
                logger.info('Processing outgoing REST connection row %s', outgoing_row)
                row_data = outgoing_row

            exported_conn: 'anydict' = {
                'name': row_data['name'] if isinstance(row_data, dict) else row_data.name,
                'host': row_data['host'] if isinstance(row_data, dict) else row_data.host,
                'url_path': row_data['url_path'] if isinstance(row_data, dict) else row_data.url_path,
            }

            # Check for security_name in either dict or object
            security_name = row_data.get('security_name') if isinstance(row_data, dict) else getattr(row_data, 'security_name', None)
            if security_name:
                exported_conn['security'] = security_name

            # Handle optional fields for both dictionary and object types
            optional_fields_from_row = {}
            optional_field_names = ['data_format', 'is_active', 'timeout', 'method', 'content_type', 
                                  'content_encoding', 'pool_size', 'ping_method', 'tls_verify']
            
            for field in optional_field_names:
                if isinstance(row_data, dict):
                    if field in row_data:
                        optional_fields_from_row[field] = row_data[field]
                else:
                    value = getattr(row_data, field, None)
                    if value is not None:
                        optional_fields_from_row[field] = value

            for field_name, field_value in optional_fields_from_row.items():
                if field_value is not None:
                    exported_conn[field_name] = field_value

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing REST connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################

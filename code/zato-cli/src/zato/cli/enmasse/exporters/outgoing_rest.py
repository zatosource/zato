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
        logger.debug('Processing %d outgoing REST connection definitions', len(db_outgoing))

        for outgoing_row in db_outgoing:

            # Handle both object and dictionary types
            if hasattr(outgoing_row, 'toDict'):
                logger.debug('Processing outgoing REST connection row %s', outgoing_row.toDict())
                row_data = outgoing_row
            else:
                logger.debug('Processing outgoing REST connection row %s', outgoing_row)
                row_data = outgoing_row

            # Create basic connection definition with required fields
            exported_conn: 'anydict' = {
                'name': row_data['name'] if isinstance(row_data, dict) else row_data.name,
                'host': row_data['host'] if isinstance(row_data, dict) else row_data.host,
                'url_path': row_data['url_path'] if isinstance(row_data, dict) else row_data.url_path,
            }

            # Add security if present
            security_name = row_data.get('security_name') if isinstance(row_data, dict) else getattr(row_data, 'security_name', None)
            if security_name:
                exported_conn['security'] = security_name

            # Add data_format if present
            data_format = row_data.get('data_format') if isinstance(row_data, dict) else getattr(row_data, 'data_format', None)
            if data_format:
                exported_conn['data_format'] = data_format

            # Add timeout if not default (60)
            timeout = row_data.get('timeout') if isinstance(row_data, dict) else getattr(row_data, 'timeout', None)
            if timeout is not None and timeout != 60:
                exported_conn['timeout'] = timeout

            # Add ping_method only if not the default (GET)
            ping_method = row_data.get('ping_method') if isinstance(row_data, dict) else getattr(row_data, 'ping_method', None)
            if ping_method and ping_method != 'GET':
                exported_conn['ping_method'] = ping_method

            # Add tls_verify only if False (default is True)
            tls_verify = row_data.get('tls_verify') if isinstance(row_data, dict) else getattr(row_data, 'tls_verify', None)
            if tls_verify is False:  # Only include if explicitly False
                exported_conn['tls_verify'] = False

            # Add content type and encoding if present
            for field in ['content_type', 'content_encoding']:
                value = row_data.get(field) if isinstance(row_data, dict) else getattr(row_data, field, None)
                if value:
                    exported_conn[field] = value

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing REST connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################

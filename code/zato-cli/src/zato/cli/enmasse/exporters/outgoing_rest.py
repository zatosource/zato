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

        for outgoing_row in db_outgoing:

            # Create basic connection definition with required fields
            exported_conn: 'anydict' = {
                'name': outgoing_row['name'],
                'host': outgoing_row['host'],
                'url_path': outgoing_row['url_path'],
            }

            # Add security if present
            if security_name := outgoing_row.get('security_name'):
                exported_conn['security'] = security_name

            if data_format := outgoing_row.get('data_format'):
                exported_conn['data_format'] = data_format

            if (timeout := outgoing_row.get('timeout')) is not None and timeout != 60:
                exported_conn['timeout'] = timeout

            if (ping_method := outgoing_row.get('ping_method')) and ping_method != 'GET':
                exported_conn['ping_method'] = ping_method

            if outgoing_row.get('tls_verify') is False:
                exported_conn['tls_verify'] = False

            # Add content type and encoding if present
            for field in ['content_type', 'content_encoding']:
                if outgoing_row.get(field):
                    exported_conn[field] = outgoing_row[field]

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing REST connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################

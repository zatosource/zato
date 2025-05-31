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

    outgoing_soap_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSOAPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'outgoing_soap_def_list':
        """ Exports outgoing SOAP connection definitions.
        """
        logger.info('Exporting outgoing SOAP connection definitions')

        # Get outgoing SOAP connections from database
        db_outgoing = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.SOAP,
            return_internal=False,
        )
        db_outgoing = to_json(db_outgoing)

        if not db_outgoing:
            logger.info('No outgoing SOAP connection definitions found in DB')
            return []

        exported_outgoing: 'outgoing_soap_def_list' = []
        logger.info('Processing %d outgoing SOAP connection definitions', len(db_outgoing))

        for outgoing_row in db_outgoing:
            
            logger.info('Processing outgoing SOAP connection row %s', outgoing_row.toDict())

            exported_conn: 'anydict' = {
                'name': outgoing_row.name,
                'host': outgoing_row.host,
                'url_path': outgoing_row.url_path,
            }

            if outgoing_row.security_name:
                exported_conn['security'] = outgoing_row.security_name

            # Add SOAP-specific fields
            if outgoing_row.soap_action:
                exported_conn['soap_action'] = outgoing_row.soap_action
            
            if outgoing_row.soap_version:
                exported_conn['soap_version'] = outgoing_row.soap_version

            optional_fields_from_row = {
                'data_format': outgoing_row.data_format,
                'is_active': outgoing_row.is_active,
                'timeout': outgoing_row.timeout,
                'content_type': outgoing_row.content_type,
                'content_encoding': outgoing_row.content_encoding,
                'pool_size': outgoing_row.pool_size,
                'ping_method': outgoing_row.ping_method,
                'tls_verify': outgoing_row.tls_verify,
            }

            for field_name, field_value in optional_fields_from_row.items():
                if field_value is not None:
                    exported_conn[field_name] = field_value

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing SOAP connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################

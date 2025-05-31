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
            # Handle both dict and object types safely
            if hasattr(outgoing_row, 'toDict'):
                logger.info('Processing outgoing SOAP connection row %s', outgoing_row.toDict())
            else:
                logger.info('Processing outgoing SOAP connection row %s', outgoing_row)
            
            # Get fields safely from either object or dict
            def get_value(obj, field):
                if isinstance(obj, dict):
                    return obj.get(field)
                else:
                    return getattr(obj, field, None)
            
            exported_conn: 'anydict' = {
                'name': get_value(outgoing_row, 'name'),
                'host': get_value(outgoing_row, 'host'),
                'url_path': get_value(outgoing_row, 'url_path'),
            }

            # Add security if present
            security_name = get_value(outgoing_row, 'security_name')
            if security_name:
                exported_conn['security'] = security_name

            # Add SOAP-specific fields
            soap_action = get_value(outgoing_row, 'soap_action')
            if soap_action:
                exported_conn['soap_action'] = soap_action
            
            soap_version = get_value(outgoing_row, 'soap_version')
            if soap_version:
                exported_conn['soap_version'] = soap_version

            # Handle optional fields
            optional_fields = ['data_format', 'is_active', 'timeout', 'content_type', 
                             'content_encoding', 'pool_size', 'ping_method', 'tls_verify']
            
            for field in optional_fields:
                value = get_value(outgoing_row, field)
                if value is not None:
                    exported_conn[field] = value

            # Optional fields are already processed above

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing SOAP connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################

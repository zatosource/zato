# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSOAPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_outgoing_soap_definitions(self, session:'SASession') -> 'list':
        """ Export outgoing SOAP connection definitions from the database.
        """
        logger.info('Exporting outgoing SOAP connections from cluster_id=%s', self.exporter.cluster_id)

        # Get outgoing SOAP connections from the database
        outgoing_soap = http_soap_list(session, self.exporter.cluster_id, 'outgoing', 'soap')

        outgoing_soap_defs = []

        for conn in outgoing_soap:
            logger.info('Processing outgoing SOAP connection: %s', conn.name)

            # Create a dictionary representation of the outgoing SOAP connection
            soap_def = {
                'name': conn.name,
                'host': conn.host,
                'url_path': conn.url_path,
                'is_active': conn.is_active
            }

            # Add security if present
            if conn.security_id:
                for sec_name, sec_def in self.exporter.sec_defs.items():
                    if sec_def.get('id') == conn.security_id:
                        soap_def['security'] = sec_name
                        break

            # Add SOAP action if present
            if conn.soap_action:
                soap_def['soap_action'] = conn.soap_action

            # Add SOAP version if not default
            if conn.soap_version and conn.soap_version != '1.1':
                soap_def['soap_version'] = conn.soap_version

            # Add timeout if not default
            if conn.timeout:
                soap_def['timeout'] = conn.timeout

            # Add TLS verify setting if not default (True)
            if conn.has_tls and not conn.tls_verify:
                soap_def['tls_verify'] = False

            # Store in exporter's outgoing SOAP definitions
            self.exporter.outgoing_soap_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            outgoing_soap_defs.append(soap_def)

        logger.info('Exported %d outgoing SOAP connections', len(outgoing_soap_defs))
        return outgoing_soap_defs

# ################################################################################################################################
# ################################################################################################################################

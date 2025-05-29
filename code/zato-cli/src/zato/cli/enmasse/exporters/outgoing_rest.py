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

class OutgoingRESTExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_outgoing_rest_definitions(self, session:'SASession') -> 'list':
        """ Export outgoing REST connection definitions from the database.
        """
        logger.info('Exporting outgoing REST connections from cluster_id=%s', self.exporter.cluster_id)
        
        # Get outgoing REST connections from the database
        outgoing_rest = http_soap_list(session, self.exporter.cluster_id, 'outgoing', 'plain_http')
        
        outgoing_rest_defs = []
        
        for conn in outgoing_rest:
            logger.info('Processing outgoing REST connection: %s', conn.name)
            
            # Create a dictionary representation of the outgoing REST connection
            rest_def = {
                'name': conn.name,
                'host': conn.host,
                'url_path': conn.url_path,
                'is_active': conn.is_active
            }
            
            # Add security if present
            if conn.security_id:
                for sec_name, sec_def in self.exporter.sec_defs.items():
                    if sec_def.get('id') == conn.security_id:
                        rest_def['security'] = sec_name
                        break
            
            # Add data format if not default
            if conn.data_format and conn.data_format != 'json':
                rest_def['data_format'] = conn.data_format
            
            # Add method if not default
            if conn.method and conn.method != 'POST':
                rest_def['method'] = conn.method
            
            # Add ping method if set
            if conn.ping_method:
                rest_def['ping_method'] = conn.ping_method
            
            # Add timeout if not default
            if conn.timeout:
                rest_def['timeout'] = conn.timeout
            
            # Add TLS verify setting if not default (True)
            if conn.has_tls and not conn.tls_verify:
                rest_def['tls_verify'] = False
            
            # Store in exporter's outgoing REST definitions
            self.exporter.outgoing_rest_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }
            
            # Add to results
            outgoing_rest_defs.append(rest_def)
            
        logger.info('Exported %d outgoing REST connections', len(outgoing_rest_defs))
        return outgoing_rest_defs

# ################################################################################################################################
# ################################################################################################################################

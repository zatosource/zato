# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import GenericConn
from zato.common.odb.query import generic_connection_list

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

class Microsoft365Exporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_microsoft_365_definitions(self, session:'SASession') -> 'list':
        """ Export Microsoft 365 connection definitions from the database.
        """
        logger.info('Exporting Microsoft 365 connections from cluster_id=%s', self.exporter.cluster_id)
        
        # Get Microsoft 365 connections from the database
        # Try both possible connection types from the alias mapping
        m365_connections = []
        conn_types = ['cloud-microsoft-365', 'zato_generic_connection:cloud-microsoft-365']
        
        for conn_type in conn_types:
            connections = generic_connection_list(session, self.exporter.cluster_id, conn_type)
            if connections:
                m365_connections.extend(connections)
        
        m365_defs = []
        
        for conn in m365_connections:
            logger.info('Processing Microsoft 365 connection: %s', conn.name)
            
            # Create a dictionary representation of the Microsoft 365 connection
            m365_def = {
                'name': conn.name,
                'is_active': conn.is_active,
                'client_id': conn.client_id,
                'tenant_id': conn.tenant_id
            }
            
            # Add scopes if present
            if conn.scopes:
                m365_def['scopes'] = conn.scopes
            
            # Store in exporter's Microsoft 365 definitions
            self.exporter.microsoft_365_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }
            
            # Add to results
            m365_defs.append(m365_def)
            
        logger.info('Exported %d Microsoft 365 connections', len(m365_defs))
        return m365_defs

# ################################################################################################################################
# ################################################################################################################################

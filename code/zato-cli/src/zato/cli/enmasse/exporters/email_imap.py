# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import IMAP
from zato.common.odb.query import imap_connection_list

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

class IMAPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_imap_definitions(self, session:'SASession') -> 'list':
        """ Export IMAP connection definitions from the database.
        """
        logger.info('Exporting IMAP connections from cluster_id=%s', self.exporter.cluster_id)
        
        # Get IMAP connections from the database
        imap_connections = imap_connection_list(session, self.exporter.cluster_id)
        
        imap_defs = []
        
        for conn in imap_connections:
            logger.info('Processing IMAP connection: %s', conn.name)
            
            # Create a dictionary representation of the IMAP connection
            imap_def = {
                'name': conn.name,
                'host': conn.host,
                'port': conn.port,
                'username': conn.username,
                'is_active': conn.is_active
            }
            
            # Add timeout if not default
            if conn.timeout != 30:
                imap_def['timeout'] = conn.timeout
                
            # Add debug level if not default
            if conn.debug_level != 0:
                imap_def['debug_level'] = conn.debug_level
                
            # Add mode if not default
            if conn.mode != 'ssl':
                imap_def['mode'] = conn.mode
                
            # Add get criteria if not default
            if conn.get_criteria != 'ALL':
                imap_def['get_criteria'] = conn.get_criteria
            
            # Store in exporter's IMAP definitions
            self.exporter.imap_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }
            
            # Add to results
            imap_defs.append(imap_def)
            
        logger.info('Exported %d IMAP connections', len(imap_defs))
        return imap_defs

# ################################################################################################################################
# ################################################################################################################################

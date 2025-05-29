# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import ElasticSearch
from zato.common.odb.query import es_list

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

class ElasticSearchExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_es_definitions(self, session:'SASession') -> 'list':
        """ Export ElasticSearch connection definitions from the database.
        """
        logger.info('Exporting ElasticSearch connections from cluster_id=%s', self.exporter.cluster_id)
        
        # Get ElasticSearch connections from the database
        es_connections = es_list(session, self.exporter.cluster_id)
        
        es_defs = []
        
        for conn in es_connections:
            logger.info('Processing ElasticSearch connection: %s', conn.name)
            
            # Create a dictionary representation of the ElasticSearch connection
            es_def = {
                'name': conn.name,
                'is_active': conn.is_active,
                'hosts': conn.hosts,
                'timeout': conn.timeout,
                'body_as': conn.body_as
            }
            
            # Store in exporter's ES definitions
            self.exporter.es_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }
            
            # Add to results
            es_defs.append(es_def)
            
        logger.info('Exported %d ElasticSearch connections', len(es_defs))
        return es_defs

# ################################################################################################################################
# ################################################################################################################################

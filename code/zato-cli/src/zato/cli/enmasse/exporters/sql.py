# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import SQLConnectionPool
from zato.common.odb.query import sql_connection_pool_list

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

class SQLExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_sql_definitions(self, session:'SASession') -> 'list':
        """ Export SQL connection pool definitions from the database.
        """
        logger.info('Exporting SQL connection pools from cluster_id=%s', self.exporter.cluster_id)

        # Get SQL connection pools from the database
        sql_pools = sql_connection_pool_list(session, self.exporter.cluster_id)

        sql_defs = []

        for pool in sql_pools:
            logger.info('Processing SQL connection pool: %s', pool.name)

            # Create a dictionary representation of the SQL connection pool
            sql_def = {
                'name': pool.name,
                'type': pool.engine,  # Map to 'type' in YAML
                'host': pool.host,
                'port': pool.port,
                'db_name': pool.db_name,
                'username': pool.username,
                'is_active': pool.is_active
            }

            # Add pool_size if not default
            if pool.pool_size != 5:  # Assuming 5 is the default
                sql_def['pool_size'] = pool.pool_size

            # Add extra connection parameters if present
            if pool.extra:
                sql_def['extra'] = pool.extra

            # Store in exporter's SQL definitions
            self.exporter.sql_defs[pool.name] = {
                'id': pool.id,
                'name': pool.name
            }

            # Add to results
            sql_defs.append(sql_def)

        logger.info('Exported %d SQL connection pools', len(sql_defs))
        return sql_defs

# ################################################################################################################################
# ################################################################################################################################

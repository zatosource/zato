# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import OutgoingOdoo
from zato.common.odb.query import out_odoo_list

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

class OdooExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_odoo_definitions(self, session:'SASession') -> 'list':
        """ Export Odoo connection definitions from the database.
        """
        logger.info('Exporting Odoo connections from cluster_id=%s', self.exporter.cluster_id)

        # Get Odoo connections from the database
        odoo_connections = out_odoo_list(session, self.exporter.cluster_id)

        odoo_defs = []

        for conn in odoo_connections:
            logger.info('Processing Odoo connection: %s', conn.name)

            # Create a dictionary representation of the Odoo connection
            odoo_def = {
                'name': conn.name,
                'is_active': conn.is_active,
                'host': conn.host,
                'port': conn.port,
                'user': conn.user,
                'database': conn.database
            }

            # Add protocol if not default
            if conn.protocol != 'jsonrpc':
                odoo_def['protocol'] = conn.protocol

            # Add pool_size if not default
            if conn.pool_size != 10:
                odoo_def['pool_size'] = conn.pool_size

            # Store in exporter's Odoo definitions
            self.exporter.odoo_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            odoo_defs.append(odoo_def)

        logger.info('Exported %d Odoo connections', len(odoo_defs))
        return odoo_defs

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import to_json
from zato.common.odb.query import out_odoo_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession

    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.odb.model import OutgoingOdoo
    from zato.common.typing_ import anydict, list_

    odoo_def_list = list_[anydict]
    db_odoo_list = list_[OutgoingOdoo]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OdooExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'odoo_def_list':
        """ Exports Odoo connection definitions.
        """
        logger.info('Exporting Odoo connection definitions')

        db_odoo_connections = out_odoo_list(session, cluster_id)

        if not db_odoo_connections:
            logger.info('No Odoo connection definitions found in DB')
            return []

        odoo_connections = to_json(db_odoo_connections, return_as_dict=True)
        logger.info('Processing %d Odoo connection definitions', len(odoo_connections))

        exported_odoo_connections = []

        for row in odoo_connections:
            item = {
                'name': row['name'],
                'host': row['host'],
                'port': row['port'],
                'user': row['user'],
                'database': row['database']
            }

            for field in ['is_active', 'protocol', 'pool_size', 'timeout', 'api_client']:
                if field in row:
                    item[field] = row[field]

            if 'opaque_attr' in row and row['opaque_attr']:
                opaque = parse_instance_opaque_attr(row)
                item.update(opaque)

            exported_odoo_connections.append(item)

        logger.info('Successfully prepared %d Odoo connection definitions for export', len(exported_odoo_connections))

        return exported_odoo_connections

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    ldap_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LDAPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'ldap_def_list':
        """ Exports LDAP connection definitions.
        """
        logger.info('Exporting LDAP connection definitions')

        # Get LDAP connections from database using the generic connection query
        db_ldap = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_LDAP)

        if not db_ldap:
            logger.info('No LDAP connection definitions found in DB')
            return []

        ldap_connections = to_json(db_ldap, return_as_dict=True)
        logger.info('Processing %d LDAP connection definitions', len(ldap_connections))

        exported_ldap = []

        for row in ldap_connections:
            # Get the base connection details
            item = {
                'name': row['name'],
                'is_active': row['is_active'],
                'username': row['username'],
                'server_list': row['server_list']
            }

            # Add optional fields if present
            for field in ['connect_timeout', 'pool_size', 'ip_mode', 'get_info', 'auto_bind', 
                          'pool_exhaust_timeout', 'pool_keep_alive', 'pool_max_cycles', 
                          'pool_lifetime', 'pool_ha_strategy', 'use_auto_range', 
                          'should_return_empty_attrs']:
                if field in row and row[field] is not None:
                    item[field] = row[field]

            # Process any opaque attributes
            if 'opaque_attr' in row and row['opaque_attr']:
                opaque = parse_instance_opaque_attr(row)
                item.update(opaque)

            exported_ldap.append(item)

        logger.info('Successfully prepared %d LDAP connection definitions for export', len(exported_ldap))
        return exported_ldap

# ################################################################################################################################
# ################################################################################################################################

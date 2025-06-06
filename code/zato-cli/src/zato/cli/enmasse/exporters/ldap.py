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

# Fields to extract from connection definitions
OPTIONAL_FIELDS = [
    'connect_timeout', 'pool_size', 'ip_mode', 'get_info', 'auto_bind',
    'pool_exhaust_timeout', 'pool_keep_alive', 'pool_max_cycles',
    'pool_lifetime', 'pool_ha_strategy', 'use_auto_range',
    'should_return_empty_attrs'
]

# Fields to extract from opaque attributes
OPAQUE_FIELDS = [
    'server_list', 'auth_type', 'pool_exhaust_timeout', 'pool_keep_alive',
    'pool_max_cycles', 'pool_lifetime', 'pool_ha_strategy', 'use_auto_range',
    'should_return_empty_attrs', 'ip_mode', 'get_info', 'auto_bind'
]

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
        logger.debug('Processing %d LDAP connection definitions', len(ldap_connections))

        exported_ldap = []

        for row in ldap_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base LDAP connection entry with fields in import order
            item = {
                'name': row['name'],
            }

            if username := row.get('username'):
                item['username'] = username

            if auth_type := row.get('auth_type'):
                item['auth_type'] = auth_type

            if (address := row.get('address')) and address.strip():
                item['server_list'] = address

            elif server_list := row.get('server_list'):
                item['server_list'] = server_list

            if (pool_size := row.get('pool_size')) and pool_size != 1:
                item['pool_size'] = pool_size

            # Add other optional fields only if they have non-default values
            defaults = {
                'connect_timeout': 10,
                'pool_exhaust_timeout': 5,
                'pool_keep_alive': 30,
                'pool_max_cycles': 1,
                'pool_lifetime': 3600,
                'pool_ha_strategy': 'ROUND_ROBIN',
                'use_auto_range': True,
                'should_return_empty_attrs': True,
                'auto_bind': 'DEFAULT',
                'get_info': 'SCHEMA',
                'ip_mode': 'IP_SYSTEM_DEFAULT'
            }

            # Only add fields that aren't default values
            for field in OPTIONAL_FIELDS:
                if value := row.get(field):
                    default = defaults.get(field)
                    if default is None or value != default:
                        item[field] = value

            exported_ldap.append(item)

        logger.info('Successfully prepared %d LDAP connection definitions for export', len(exported_ldap))
        return exported_ldap

# ################################################################################################################################
# ################################################################################################################################

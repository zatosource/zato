# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    ldap_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to check for non-default values
OPTIONAL_FIELDS = [
    'connect_timeout', 'pool_size', 'ip_mode', 'get_info', 'auto_bind',
    'pool_exhaust_timeout', 'pool_keep_alive', 'pool_max_cycles',
    'pool_lifetime', 'pool_ha_strategy', 'use_auto_range',
    'should_return_empty_attrs'
]

# ################################################################################################################################
# ################################################################################################################################

class LDAPExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'ldap_def_list':
        """ Exports LDAP connection definitions.
        """
        logger.info('Exporting LDAP connection definitions')

        if not items:
            logger.info('No LDAP connection definitions found')
            return []

        logger.debug('Processing %d LDAP connection definitions', len(items))

        exported_ldap = []

        for row in items:

            item = {
                'name': row['name'],
            }

            if username := row.get('username'):
                item['username'] = username

            if auth_type := row.get('auth_type'):
                item['auth_type'] = auth_type

            if (address := row.get('address')) and str(address).strip():
                item['server_list'] = address
            elif server_list := row.get('server_list'):
                item['server_list'] = server_list

            if (pool_size := row.get('pool_size')) and pool_size != 1:
                item['pool_size'] = pool_size

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

# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, LDAP
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

class LDAPImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_LDAP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LDAP,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': LDAP.DEFAULT.POOL_SIZE,
        'connect_timeout': LDAP.DEFAULT.CONNECT_TIMEOUT,
    }

    connection_extra_field_defaults = {
        'ip_mode': LDAP.IP_MODE.IP_SYSTEM_DEFAULT.id,
        'get_info': LDAP.GET_INFO.SCHEMA.id,
        'auto_bind': LDAP.AUTO_BIND.DEFAULT,
        'server_list': LDAP.DEFAULT.Server_List,
        'pool_exhaust_timeout': LDAP.DEFAULT.POOL_EXHAUST_TIMEOUT,
        'pool_keep_alive': LDAP.DEFAULT.POOL_KEEP_ALIVE,
        'pool_max_cycles': LDAP.DEFAULT.POOL_MAX_CYCLES,
        'pool_lifetime': LDAP.DEFAULT.POOL_LIFETIME,
        'pool_ha_strategy': LDAP.POOL_HA_STRATEGY.ROUND_ROBIN.id,
        'use_auto_range': True,
        'should_return_empty_attrs': True,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'username', 'server_list']

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.server.generic.api.outconn_ldap import LDAPClient

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Service_File_Path = 'Zato_Test_Google_Service_File_Path'
    Env_Key_User = 'Zato_Test_Google_User'

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPTestCase(TestCase):

    def get_config(self, conn_name:'str') -> 'Bunch':

        config = bunchify({
            'name': conn_name,
            'is_active': True,
            'server_list': ['localhost:1389'],
            'username': None,
            'secret': None,
            'is_tls_enabled': False,
            'get_info': None,
            'connect_timeout': 5,
            'ip_mode': 'IP_SYSTEM_DEFAULT',
            'tls': None,
            'sasl_mechanism': None,
            'pool_name': None,
            'pool_ha_strategy': 'ROUND_ROBIN',
            'pool_max_cycles': None,
            'pool_exhaust_timeout': None,
            'auto_bind': None,
            'use_auto_range': None,
            'should_check_names': None,
            'is_stats_enabled': None,
            'is_read_only': None,
            'pool_lifetime': None,
            'should_return_empty_attrs': None,
            'pool_keep_alive': None,
        })

        return config

# ################################################################################################################################

    def test_ping(self):
        if not os.environ.get('Zato_Test_LDAP'):
            return

        conn_name = 'OutconnLDAPTestCase.test_connect'
        config = self.get_config(conn_name)

        client = LDAPClient(config)
        client.ping()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

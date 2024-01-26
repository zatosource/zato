# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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

if 0:
    from bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_LDAP'

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPTestCase(TestCase):

    def get_config(self, conn_name:'str') -> 'Bunch':

        config = bunchify({
            'name': conn_name,
            'is_active': True,
            'server_list': ['localhost:1389'],
            'username': 'cn=admin,dc=example,dc=org',
            'secret': 'adminpassword',
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
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'OutconnLDAPTestCase.test_ping'
        config = self.get_config(conn_name)

        client = LDAPClient(config)
        client.ping()

# ################################################################################################################################

    def test_query(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'OutconnLDAPTestCase.test_ping'
        config = self.get_config(conn_name)
        client = LDAPClient(config)

        # Where in the directory we expect to find the user
        search_base = 'dc=example, dc=org'

        # Look up users up by either username or email
        # search_filter = '(uid=*)'
        search_filter = '(&(|(uid={user_info})(mail={user_info})))'
        user_filter = search_filter.format(user_info='user01')

        # We are looking up these attributes
        query_attributes = ['uid', 'givenName', 'sn', 'mail']

        with client.get() as conn:

            has_result = conn.search(search_base, user_filter, attributes=query_attributes)
            if not has_result:
                self.fail('Expected for results to be available')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

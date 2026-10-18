# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.api import GENERIC
from zato.common.test.ldap_ import LDAPTestServer
from zato.common.typing_ import cast_
from zato.server.base.config_manager.generic import Generic
from zato.server.generic.api.outconn_ldap import LDAPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_LDAP'

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPTestCase(TestCase):

    server: 'LDAPTestServer'

# ################################################################################################################################

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.server = LDAPTestServer()
        class_.server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.server.stop()

# ################################################################################################################################

    def get_config(self, conn_name:'str') -> 'Bunch':

        server = self.__class__.server

        config = bunchify({
            'name': conn_name,
            'is_active': True,
            'server_list': [f'{server.host}:{server.port}'],
            'username': server.admin_dn,
            'secret': server.admin_password,
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
        config = cast_('Bunch', config)

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

        conn_name = 'OutconnLDAPTestCase.test_query'
        config = self.get_config(conn_name)
        client = LDAPClient(config)

        # Where in the directory we expect to find the user
        search_base = self.__class__.server.root_dn

        # Look up users up by either username or email
        # search_filter = '(uid=*)'
        search_filter = '(&(|(uid={user_info})(mail={user_info})))'
        user_filter = search_filter.format(user_info=self.__class__.server.username)

        # We are looking up these attributes
        query_attributes = ['uid', 'givenName', 'sn', 'mail']

        with client.get() as conn:

            has_result = conn.search(search_base, user_filter, attributes=query_attributes)
            if not has_result:
                self.fail('Expected for results to be available')

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPConfigTestCase(TestCase):
    """ Tests for the configuration of an LDAP connection created with the required fields only.
    """

    def test_conn_config_is_built_from_required_fields(self) -> 'None':

        # The fields of a connection created through zato.generic.connection.create with no optional ones ..
        config = bunchify({
            'id': 1,
            'name': 'test.ldap.required-fields',
            'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LDAP,
            'is_active': True,
            'username': 'cn=admin,dc=example,dc=com',
            'secret': 'test.password',
            'pool_size': 1,
            'pool_max_cycles': 1,
            'pool_keep_alive': 30,
            'use_auto_range': True,
            'use_tls': False,
            'sasl_mechanism': '',
            'server_list': 'ldap://localhost:389',
        })
        config = cast_('Bunch', config)

        # .. the config manager fills in the remaining ones ..
        manager = Generic.__new__(Generic)
        manager._generic_normalize_config_outconn_ldap(config)

        # .. and the client builds its connection configuration from the result.
        client = LDAPClient.__new__(LDAPClient)
        client.config = config

        conn_config = client.get_conn_config()

        self.assertFalse(config.is_tls_enabled)
        self.assertEqual(conn_config['user'], 'cn=admin,dc=example,dc=com')
        self.assertEqual(conn_config['password'], 'test.password')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

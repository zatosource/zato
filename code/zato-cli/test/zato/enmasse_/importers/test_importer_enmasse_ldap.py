# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseLDAPImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_ldap_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('ldap', exported)

        ldap_list = exported['ldap']
        ldap_by_name = {item['name']: item for item in ldap_list}
        self.assertIn('enmasse.ldap.1', ldap_by_name)

# ################################################################################################################################

    def test_ldap_values(self):

        exported = self.config_manager.export_to_dict()
        ldap_list = exported['ldap']
        ldap_by_name = {item['name']: item for item in ldap_list}

        l1 = ldap_by_name['enmasse.ldap.1']
        self.assertEqual(l1['username'], 'CN=enmasse,OU=testing,OU=Servers,DC=enmasse')
        self.assertEqual(l1['auth_type'], 'NTLM')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

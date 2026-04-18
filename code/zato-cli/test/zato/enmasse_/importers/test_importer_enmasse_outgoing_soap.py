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

class TestEnmasseOutgoingSOAPImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_outgoing_soap_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('outgoing_soap', exported)

        soap_list = exported['outgoing_soap']
        soap_by_name = {item['name']: item for item in soap_list}
        self.assertIn('enmasse.outgoing.soap.1', soap_by_name)

# ################################################################################################################################

    def test_outgoing_soap_values(self):

        exported = self.config_store.export_to_dict()
        soap_list = exported['outgoing_soap']
        soap_by_name = {item['name']: item for item in soap_list}

        s1 = soap_by_name['enmasse.outgoing.soap.1']
        self.assertEqual(s1['host'], 'https://example.com')
        self.assertEqual(s1['url_path'], '/SOAP')
        self.assertEqual(s1['soap_version'], '1.1')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

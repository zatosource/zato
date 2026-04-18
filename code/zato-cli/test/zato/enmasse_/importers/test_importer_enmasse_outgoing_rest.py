# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingRESTImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_outgoing_rest_preprocessing_tls_rename(self):

        template_dict = yaml.safe_load(template_complex_01)
        outgoing_items = template_dict['outgoing_rest']

        preprocessed = OutgoingRESTImporter.preprocess(outgoing_items)

        for item in preprocessed:
            self.assertNotIn('tls_verify', item)

# ################################################################################################################################

    def test_outgoing_rest_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('outgoing_rest', exported)

        outgoing_list = exported['outgoing_rest']
        outgoing_by_name = {item['name']: item for item in outgoing_list}

        self.assertIn('enmasse.outgoing.rest.1', outgoing_by_name)
        self.assertIn('enmasse.outgoing.rest.2', outgoing_by_name)

# ################################################################################################################################

    def test_outgoing_rest_values(self):

        exported = self.config_manager.export_to_dict()
        outgoing_list = exported['outgoing_rest']
        outgoing_by_name = {item['name']: item for item in outgoing_list}

        o1 = outgoing_by_name['enmasse.outgoing.rest.1']
        self.assertEqual(o1['host'], 'https://example.com:443')
        self.assertEqual(o1['timeout'], 60)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

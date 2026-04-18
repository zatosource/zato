# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseIMAPImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_imap_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        imap_items = template_dict['email_imap']

        preprocessed = IMAPImporter.preprocess(imap_items)

        for item in preprocessed:
            self.assertIn('server_type', item)
            self.assertIn('password', item)
            self.assertEqual(item.get('timeout'), 30)

# ################################################################################################################################

    def test_imap_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('email_imap', exported)

        imap_list = exported['email_imap']
        imap_by_name = {item['name']: item for item in imap_list}
        self.assertIn('enmasse.email.imap.1', imap_by_name)

# ################################################################################################################################

    def test_imap_values(self):

        exported = self.config_store.export_to_dict()
        imap_list = exported['email_imap']
        imap_by_name = {item['name']: item for item in imap_list}

        i1 = imap_by_name['enmasse.email.imap.1']
        self.assertEqual(i1['host'], 'imap.example.com')
        self.assertEqual(i1['port'], 993)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

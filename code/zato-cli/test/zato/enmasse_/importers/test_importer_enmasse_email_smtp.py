# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSMTPImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_smtp_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        smtp_items = template_dict['email_smtp']

        preprocessed = SMTPImporter.preprocess(smtp_items)

        for item in preprocessed:
            self.assertIn('password', item)
            self.assertEqual(item.get('timeout'), 60)
            self.assertEqual(item.get('mode'), 'plain')

# ################################################################################################################################

    def test_smtp_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('email_smtp', exported)

        smtp_list = exported['email_smtp']
        smtp_by_name = {item['name']: item for item in smtp_list}
        self.assertIn('enmasse.email.smtp.1', smtp_by_name)

# ################################################################################################################################

    def test_smtp_values(self):

        exported = self.config_manager.export_to_dict()
        smtp_list = exported['email_smtp']
        smtp_by_name = {item['name']: item for item in smtp_list}

        s1 = smtp_by_name['enmasse.email.smtp.1']
        self.assertEqual(s1['host'], 'smtp.example.com')
        self.assertEqual(s1['port'], 587)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

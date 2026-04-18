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

class TestEnmasseChannelOpenAPIImport(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.importer = EnmasseImporter(self.config_store)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_channel_openapi_imported(self):

        exported = self.config_store.export_to_dict()
        self.assertIn('channel_openapi', exported)

        channel_list = exported['channel_openapi']
        channel_by_name = {item['name']: item for item in channel_list}

        self.assertIn('enmasse.channel.openapi.1', channel_by_name)
        self.assertIn('enmasse.channel.openapi.2', channel_by_name)

# ################################################################################################################################

    def test_channel_openapi_values(self):

        exported = self.config_store.export_to_dict()
        channel_list = exported['channel_openapi']
        channel_by_name = {item['name']: item for item in channel_list}

        ch1 = channel_by_name['enmasse.channel.openapi.1']
        self.assertEqual(ch1['url_path'], '/openapi/enmasse-1')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

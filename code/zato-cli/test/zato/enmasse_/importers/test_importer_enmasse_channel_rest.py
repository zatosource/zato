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

class TestEnmasseChannelRESTImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_channel_rest_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('channel_rest', exported)

        channel_list = exported['channel_rest']
        channel_by_name = {item['name']: item for item in channel_list}

        self.assertIn('enmasse.channel.rest.1', channel_by_name)
        self.assertIn('enmasse.channel.rest.2', channel_by_name)
        self.assertIn('enmasse.channel.rest.3', channel_by_name)
        self.assertIn('enmasse.channel.rest.4', channel_by_name)

# ################################################################################################################################

    def test_channel_rest_values(self):

        exported = self.config_manager.export_to_dict()
        channel_list = exported['channel_rest']
        channel_by_name = {item['name']: item for item in channel_list}

        ch1 = channel_by_name['enmasse.channel.rest.1']
        self.assertEqual(ch1['service'], 'demo.ping')
        self.assertEqual(ch1['url_path'], '/enmasse.rest.1')

        ch2 = channel_by_name['enmasse.channel.rest.2']
        self.assertEqual(ch2['data_format'], 'json')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

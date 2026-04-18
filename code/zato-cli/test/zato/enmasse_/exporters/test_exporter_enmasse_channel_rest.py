# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

    def test_rest_channel_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('channel_rest', exported_data, 'Exporter did not produce a "channel_rest" section.')
        all_exported_channels = exported_data['channel_rest']

        exported_channels = [ch for ch in all_exported_channels if ch['name'].startswith('enmasse')]

        template_dict = yaml.safe_load(template_complex_01)

        required_channel_fields = {}
        for channel_def in template_dict.get('channel_rest', []):

            channel_name = channel_def['name']

            channel_required = {
                'name': channel_name,
                'url_path': channel_def.get('url_path'),
                'service': channel_def.get('service'),
            }

            if 'data_format' in channel_def and channel_def.get('data_format') != 'json':
                channel_required['data_format'] = channel_def.get('data_format')

            if 'groups' in channel_def and channel_def['groups']:
                channel_required['groups'] = channel_def['groups']

            required_channel_fields[channel_name] = channel_required

        for channel in exported_channels:
            name = channel['name']
            self.assertIn(name, required_channel_fields, f'Unexpected channel {name} in export')
            expected = required_channel_fields[name]

            for field, value in expected.items():
                self.assertIn(field, channel, f'Field {field} missing in channel {name}')

                if isinstance(value, list):
                    self.assertIsInstance(channel[field], list, f'Field {field} should be a list in channel {name}')
                    for item in value:
                        self.assertIn(item, channel[field], f'Expected {item} in {field} list for channel {name}')
                else:
                    self.assertEqual(channel[field], value,
                        f'Field {field} has incorrect value in channel {name}, expected {value}, got {channel[field]}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

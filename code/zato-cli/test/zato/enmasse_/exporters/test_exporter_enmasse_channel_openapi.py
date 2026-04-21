# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_openapi import ChannelOpenAPIImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.common.test.config import TestConfig
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelOpenAPIExport(TestCase):

    def setUp(self) -> 'None':
        self.server_path = TestConfig.server_location

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        self.security_importer = SecurityImporter(self.importer)
        self.group_importer = GroupImporter(self.importer)
        self.channel_rest_importer = ChannelImporter(self.importer)
        self.channel_openapi_importer = ChannelOpenAPIImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _find_item_by_name(self, items, name):
        for item in items:
            if item['name'] == name:
                return item
        return None

    def _verify_fields(self, exported_item, original_item, field_list):
        for field in field_list:
            if field in original_item:
                self.assertEqual(exported_item.get(field), original_item.get(field))

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        security_list = self.yaml_config.get('security', [])
        if security_list:
            _, _ = self.security_importer.sync_security_definitions(security_list, self.session)

        group_list = self.yaml_config.get('groups', [])
        if group_list:
            _, _ = self.group_importer.sync_groups(group_list, self.session)
            self.importer.group_defs = self.group_importer.group_defs

# ################################################################################################################################

    def test_channel_openapi_export(self):
        self._setup_test_environment()

        channel_rest_list = self.yaml_config.get('channel_rest', [])
        if channel_rest_list:
            _, _ = self.channel_rest_importer.sync_channel_rest(channel_rest_list, self.session)

        channel_openapi_list = self.yaml_config.get('channel_openapi', [])

        if not channel_openapi_list:
            self.skipTest('No OpenAPI channel definitions found in YAML template')

        created, _ = self.channel_openapi_importer.sync_channel_openapi(channel_openapi_list, self.session)
        self.assertEqual(len(created), len(channel_openapi_list))

        exported_list = self.exporter.export_channel_openapi(self.session)
        self.assertIsNotNone(exported_list)
        self.assertGreaterEqual(len(exported_list), len(channel_openapi_list))

        yaml_item = channel_openapi_list[0]
        yaml_name = yaml_item['name']

        exported_item = self._find_item_by_name(exported_list, yaml_name)
        self.assertIsNotNone(exported_item, f'Could not find exported OpenAPI channel definition for "{yaml_name}"')

        self.assertEqual(exported_item['name'], yaml_item['name'])
        self.assertEqual(exported_item.get('is_active'), yaml_item.get('is_active', True))

        field_list = ['url_path']
        self._verify_fields(exported_item, yaml_item, field_list)

# ################################################################################################################################

    def test_channel_openapi_full_export(self):
        self._setup_test_environment()

        channel_rest_list = self.yaml_config.get('channel_rest', [])
        if channel_rest_list:
            _, _ = self.channel_rest_importer.sync_channel_rest(channel_rest_list, self.session)

        channel_openapi_list = self.yaml_config.get('channel_openapi', [])

        if not channel_openapi_list:
            self.skipTest('No OpenAPI channel definitions found in YAML template')

        _ = self.channel_openapi_importer.sync_channel_openapi(channel_openapi_list, self.session)

        exported_dict = self.exporter.export_to_dict(self.session)

        self.assertIn('channel_openapi', exported_dict)
        self.assertTrue(len(exported_dict['channel_openapi']) > 0)

        imported_def = channel_openapi_list[0]
        imported_name = imported_def['name']

        exported_def = self._find_item_by_name(exported_dict['channel_openapi'], imported_name)
        self.assertIsNotNone(exported_def, f'Could not find exported OpenAPI channel definition for "{imported_name}"')

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def.get('is_active'), imported_def.get('is_active', True))

        field_list = ['url_path']
        self._verify_fields(exported_def, imported_def, field_list)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging
    from unittest import main

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

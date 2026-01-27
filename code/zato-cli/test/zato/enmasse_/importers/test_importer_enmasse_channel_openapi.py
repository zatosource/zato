# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_openapi import ChannelOpenAPIImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
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

class TestEnmasseChannelOpenAPIFromYAML(TestCase):

    def setUp(self) -> 'None':
        self.server_path = TestConfig.server_location

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()

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

        channel_rest_list = self.yaml_config.get('channel_rest', [])
        if channel_rest_list:
            _, _ = self.channel_rest_importer.sync_channel_rest(channel_rest_list, self.session)

# ################################################################################################################################

    def test_channel_openapi_definition_creation(self):
        self._setup_test_environment()

        channel_openapi_defs = self.yaml_config.get('channel_openapi', [])

        if not channel_openapi_defs:
            self.skipTest('No OpenAPI channel definitions found in YAML template')

        created, updated = self.channel_openapi_importer.sync_channel_openapi(channel_openapi_defs, self.session)

        self.assertEqual(len(created), len(channel_openapi_defs))
        self.assertEqual(len(updated), 0)

        channel = self.session.query(GenericConn).filter_by(
            name='enmasse.channel.openapi.1',
            type_=GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI
        ).one()
        self.assertTrue(channel.is_active)

# ################################################################################################################################

    def test_channel_openapi_update(self):
        self._setup_test_environment()

        channel_openapi_defs = self.yaml_config.get('channel_openapi', [])

        if not channel_openapi_defs:
            self.skipTest('No OpenAPI channel definitions found in YAML template')

        channel_def = channel_openapi_defs[0]

        rest_channels_map = self.channel_openapi_importer._get_rest_channels_map(self.session, self.importer.cluster_id)
        instance = self.channel_openapi_importer.create_definition(channel_def, self.session, rest_channels_map)
        self.session.commit()

        self.assertEqual(instance.name, channel_def['name'])

        update_def = {
            'name': channel_def['name'],
            'id': instance.id,
            'is_active': False,
            'url_path': '/openapi/updated-path',
        }

        updated_instance = self.channel_openapi_importer.update_definition(update_def, self.session, rest_channels_map)
        self.session.commit()

        self.assertFalse(updated_instance.is_active)
        self.assertEqual(updated_instance.name, channel_def['name'])

# ################################################################################################################################

    def test_complete_channel_openapi_import_flow(self):
        self._setup_test_environment()

        channel_openapi_list = self.yaml_config.get('channel_openapi', [])

        if not channel_openapi_list:
            self.skipTest('No OpenAPI channel definitions found in YAML template')

        created, updated = self.channel_openapi_importer.sync_channel_openapi(channel_openapi_list, self.session)

        self.assertEqual(len(created), len(channel_openapi_list))
        self.assertEqual(len(updated), 0)

        self.assertEqual(len(self.channel_openapi_importer.channel_openapi_defs), len(channel_openapi_list))

        created2, updated2 = self.channel_openapi_importer.sync_channel_openapi(channel_openapi_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), len(channel_openapi_list))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

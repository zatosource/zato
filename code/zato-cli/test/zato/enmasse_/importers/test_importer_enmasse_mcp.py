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
from zato.cli.enmasse.importers.mcp import ChannelMCPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelMCPFromYAML(TestCase):
    """ Tests importing MCP gateway definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer)
        self.mcp_importer = ChannelMCPImporter(self.importer)

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

        # Process security definitions and groups first - MCP gateways reference security groups
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

# ################################################################################################################################

    def test_mcp_gateway_creation(self):
        self._setup_test_environment()

        mcp_defs = self.yaml_config['mcp_gateway']
        created, updated = self.mcp_importer.sync_definitions(mcp_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name='enmasse.mcp.channel.1',
            type_=GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
        ).one()
        self.assertTrue(conn.is_active)

# ################################################################################################################################

    def test_mcp_gateway_update(self):
        self._setup_test_environment()

        mcp_defs = self.yaml_config['mcp_gateway']
        mcp_def = mcp_defs[0]

        instance = self.mcp_importer.create_definition(mcp_def, self.session)
        self.session.commit()

        update_def = {
            'name': mcp_def['name'],
            'id': instance.id,
            'url_path': '/mcp/updated',
        }

        updated_instance = self.mcp_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.name, mcp_def['name'])

# ################################################################################################################################

    def test_complete_mcp_gateway_import_flow(self):
        self._setup_test_environment()

        mcp_list = self.yaml_config['mcp_gateway']
        created, updated = self.mcp_importer.sync_definitions(mcp_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.mcp_importer.sync_definitions(mcp_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

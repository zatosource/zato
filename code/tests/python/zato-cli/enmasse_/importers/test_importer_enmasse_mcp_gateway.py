# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MCP gateway importer's handling of the connection allow lists and security groups.

# stdlib
import json
import os
from tempfile import gettempdir
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.common.api import CONNECTION, MCP
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import default_server_base_dir
from zato.common.odb.model import HTTPSOAP
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# One gateway carrying two allow lists and one carrying none.
template_mcp_gateway = """
mcp_gateway:

  - name: enmasse.mcp.import.1
    url_path: /mcp/enmasse-import-1
    rest_connections:
      - billing.backend
      - crm.backend
    odoo_connections:
      - erp.backend

  - name: enmasse.mcp.import.2
    url_path: /mcp/enmasse-import-2
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMCPGatewayImporter(TestCase):
    """ Importing MCP gateways with connection allow lists and security groups.
    """

    def setUp(self:'any_') -> 'None':

        # Server path for the database connection ..
        self.server_path = default_server_base_dir

        # .. the YAML template goes to a file of its own ..
        file_name = 'enmasse.mcp.gateway.' + CryptoManager.generate_hex_string() + '.yaml'
        self.temp_file_path = os.path.join(gettempdir(), file_name)

        with open(self.temp_file_path, 'w') as temp_file:
            _ = temp_file.write(template_mcp_gateway)

        # .. and the importers that will read it back.
        self.importer = EnmasseYAMLImporter()
        self.gateway_importer = GatewayMCPImporter(self.importer)
        self.group_importer = GroupImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        if self.session:
            self.session.close()
        os.remove(self.temp_file_path)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self:'any_') -> 'None':

        # Open a session to the server's own database ..
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        # .. and parse the YAML file.
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file_path)

# ################################################################################################################################

    def _get_gateways_by_name(self:'any_', gateways:'any_') -> 'stranydict':
        out = {}

        for gateway in gateways:
            out[gateway.name] = gateway

        return out

# ################################################################################################################################

    def test_the_allow_lists_land_in_the_opaque_attributes(self:'any_') -> 'None':

        self._setup_test_environment()

        # Import the definitions ..
        gateway_definitions = self.yaml_config['mcp_gateway']
        created, _ = self.gateway_importer.sync_definitions(gateway_definitions, self.session)

        gateways_by_name = self._get_gateways_by_name(created)

        # .. the gateway that names its allow lists holds them intact ..
        gateway = gateways_by_name['enmasse.mcp.import.1']
        opaque = json.loads(gateway.opaque1)

        self.assertEqual(opaque['rest_connections'], ['billing.backend', 'crm.backend'])
        self.assertEqual(opaque['odoo_connections'], ['erp.backend'])

        # .. and the ones it does not name default to empty lists.
        self.assertEqual(opaque['sql_connections'], [])

# ################################################################################################################################

    def test_a_gateway_without_allow_lists_defaults_them_all(self:'any_') -> 'None':

        self._setup_test_environment()

        # Import the definitions ..
        gateway_definitions = self.yaml_config['mcp_gateway']
        created, _ = self.gateway_importer.sync_definitions(gateway_definitions, self.session)

        gateways_by_name = self._get_gateways_by_name(created)

        # .. the gateway that names no allow lists holds an empty one under every key.
        gateway = gateways_by_name['enmasse.mcp.import.2']
        opaque = json.loads(gateway.opaque1)

        for key in MCP.Connection_List_Keys:
            self.assertEqual(opaque[key], [], f'`{key}` did not default to an empty list')

# ################################################################################################################################

    def test_a_security_group_existing_only_in_the_database_resolves(self:'any_') -> 'None':

        self._setup_test_environment()

        # The group goes into the database directly, without ever entering
        # the importer's own group definitions, the way a group that was
        # imported on an earlier run exists when a gateway travels alone.
        group_name = 'enmasse.mcp.import.group.db'
        _ = self.group_importer.sync_groups([{'name': group_name, 'members': []}], self.session)

        self.assertNotIn(group_name, self.importer.group_defs)

        gateway_name = 'enmasse.mcp.import.group.gateway'

        gateway_definitions = [{
            'name': gateway_name,
            'url_path': '/mcp/enmasse-import-group',
            'security_groups': [group_name],
        }]

        _ = self.gateway_importer.sync_definitions(gateway_definitions, self.session)

        # The REST channel of the gateway carries the group's ID.
        channel = self.session.query(HTTPSOAP).filter(
            HTTPSOAP.name == gateway_name,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
            HTTPSOAP.cluster_id == self.importer.cluster_id,
        ).one()

        opaque = parse_instance_opaque_attr(channel)
        expected_group_id = self.gateway_importer._get_group_id_from_db(group_name, self.session)

        self.assertEqual(opaque['security_groups'], [expected_group_id])

# ################################################################################################################################

    def test_a_security_group_existing_nowhere_is_rejected(self:'any_') -> 'None':

        self._setup_test_environment()

        gateway_definitions = [{
            'name': 'enmasse.mcp.import.group.unknown',
            'url_path': '/mcp/enmasse-import-group-unknown',
            'security_groups': ['enmasse.no.such.group'],
        }]

        with self.assertRaises(Exception):
            _ = self.gateway_importer.sync_definitions(gateway_definitions, self.session)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

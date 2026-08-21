# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connection allow lists of an MCP gateway - the catalogs that carry them
# and the writer that puts them into enmasse files.

# stdlib
import os
from tempfile import gettempdir
from unittest import TestCase, main

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.exporters.mcp import GATEWAY_OPTIONAL_FIELDS
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.util import FileWriter, get_object_order
from zato.common.api import MCP
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionListCatalogs(TestCase):
    """ Every connection allow-list key travels through the importer's defaults,
    the exporter's field list and the writer's field order.
    """

    def test_every_key_has_an_importer_default(self:'any_') -> 'None':

        defaults = GatewayMCPImporter.connection_extra_field_defaults

        for key in MCP.Connection_List_Keys:
            self.assertIn(key, defaults, f'`{key}` not in the importer defaults')
            self.assertEqual(defaults[key], [], f'`{key}` does not default to an empty list')

# ################################################################################################################################

    def test_every_key_is_an_exporter_field(self:'any_') -> 'None':

        for key in MCP.Connection_List_Keys:
            self.assertIn(key, GATEWAY_OPTIONAL_FIELDS, f'`{key}` not in the exporter fields')

# ################################################################################################################################

    def test_every_key_is_in_the_writer_order_as_a_list(self:'any_') -> 'None':

        fields = get_object_order('mcp_gateway')

        for key in MCP.Connection_List_Keys:
            self.assertIn(f'{key}:list', fields, f'`{key}:list` not in the mcp_gateway order')

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionListWriter(TestCase):
    """ Writing a gateway's allow lists to an enmasse file and reading them back.
    """

    def setUp(self:'any_') -> 'None':
        file_name = 'enmasse.' + CryptoManager.generate_hex_string() + '.yaml'
        self.path = os.path.join(gettempdir(), file_name)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        os.remove(self.path)

# ################################################################################################################################

    def _write_and_read_back(self:'any_', data:'stranydict') -> 'stranydict':

        # Write the data out ..
        writer = FileWriter(self.path)
        writer.write(data)

        # .. and read it back.
        with open(self.path) as yaml_file:
            out = yaml.safe_load(yaml_file)

        return out

# ################################################################################################################################

    def test_the_allow_lists_round_trip(self:'any_') -> 'None':

        # A gateway carrying two allow lists ..
        gateway = {
            'name': 'enmasse.mcp.writer.1',
            'url_path': '/mcp/enmasse-writer',
            'rest_connections': ['billing.backend', 'crm.backend'],
            'sql_connections': ['reporting.db'],
        }

        # .. keeps both as the lists they went in as ..
        parsed = self._write_and_read_back({'mcp_gateway': [gateway]})
        written = parsed['mcp_gateway'][0]

        self.assertEqual(written['name'], gateway['name'])
        self.assertEqual(written['url_path'], gateway['url_path'])
        self.assertEqual(written['rest_connections'], gateway['rest_connections'])
        self.assertEqual(written['sql_connections'], gateway['sql_connections'])

        # .. while a list the gateway does not carry stays out of the file.
        self.assertNotIn('odoo_connections', written)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

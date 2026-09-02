# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MCP gateway exporter's handling of the connection allow lists.

# stdlib
import os
from tempfile import gettempdir
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.mcp import GatewayMCPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.common.api import MCP
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import default_server_base_dir
from zato.common.typing_ import cast_

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

  - name: enmasse.mcp.export.1
    url_path: /mcp/enmasse-export-1
    rest_connections:
      - billing.backend
      - crm.backend
    es_connections:
      - search.backend

  - name: enmasse.mcp.export.2
    url_path: /mcp/enmasse-export-2
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMCPGatewayExporter(TestCase):
    """ Exporting MCP gateways with connection allow lists.
    """

    def setUp(self:'any_') -> 'None':

        # Server path for the database connection ..
        self.server_path = default_server_base_dir

        # .. the YAML template goes to a file of its own ..
        file_name = 'enmasse.mcp.gateway.export.' + CryptoManager.generate_hex_string() + '.yaml'
        self.temp_file_path = os.path.join(gettempdir(), file_name)

        with open(self.temp_file_path, 'w') as temp_file:
            _ = temp_file.write(template_mcp_gateway)

        # The importer sets up the database state for the export tests ..
        self.importer = EnmasseYAMLImporter()
        self.gateway_importer = GatewayMCPImporter(self.importer)

        # .. and the exporter under test reads it back.
        self.exporter = EnmasseYAMLExporter()
        self.gateway_exporter = GatewayMCPExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        if self.session:
            self.session.close()
        os.remove(self.temp_file_path)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _import_and_export(self:'any_') -> 'stranydict':
        """ Imports what the file declares and answers with the export, keyed by gateway name.
        """

        # Open a session to the server's own database ..
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        # .. parse the YAML file ..
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file_path)

        _ = self.importer.get_cluster(self.session)

        # .. import the gateways ..
        gateway_definitions = self.yaml_config['mcp_gateway']
        _, _ = self.gateway_importer.sync_definitions(gateway_definitions, self.session)

        # .. and export them back.
        all_exported = self.gateway_exporter.export(self.session, self.importer.cluster_id)

        out = {}

        for item in all_exported:
            if item['name'].startswith('enmasse.mcp.export.'):
                out[item['name']] = item

        return out

# ################################################################################################################################

    def test_the_allow_lists_are_exported_verbatim(self:'any_') -> 'None':

        exported_by_name = self._import_and_export()

        exported_count = len(exported_by_name)
        self.assertEqual(exported_count, 2)

        # The gateway that names its allow lists exports them as they were given ..
        item = exported_by_name['enmasse.mcp.export.1']

        self.assertEqual(item['rest_connections'], ['billing.backend', 'crm.backend'])
        self.assertEqual(item['es_connections'], ['search.backend'])

        # .. and the lists it left empty stay out of the export.
        self.assertNotIn('sql_connections', item)
        self.assertNotIn('odoo_connections', item)

# ################################################################################################################################

    def test_a_gateway_without_allow_lists_exports_none(self:'any_') -> 'None':

        exported_by_name = self._import_and_export()

        # A gateway with every allow list at its default exports none of them.
        item = exported_by_name['enmasse.mcp.export.2']

        for key in MCP.Connection_List_Keys:
            self.assertNotIn(key, item, f'`{key}` should not be in the export')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

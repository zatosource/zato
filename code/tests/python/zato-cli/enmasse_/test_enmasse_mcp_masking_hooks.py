# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The enmasse round trip of the data masking keys and the hook services of MCP gateways.

# stdlib
import json
import os
from tempfile import gettempdir
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.mcp import GatewayMCPExporter, Gateway_Optional_Fields
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.util.orders import _object_order
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

# One gateway stating every data masking key and both hook services, the custom switch off,
# and one stating none of them.
template_mcp_gateway = """
mcp_gateway:

  - name: enmasse.mcp.masking.1
    url_path: /mcp/enmasse-masking-1
    safeguards_masking_sets:
      - banking
      - healthcare
    safeguards_masking_excluded:
      - iban
    safeguards_masking_custom_fields:
      - customer.loyalty_id
      - Internal_Code
    safeguards_masking_custom_enabled: false
    request_hook_service: enmasse.mcp.request-hook
    response_hook_service: enmasse.mcp.response-hook

  - name: enmasse.mcp.masking.2
    url_path: /mcp/enmasse-masking-2
"""

# What the first gateway states, key by key.
_expected_values = {
    'safeguards_masking_sets': ['banking', 'healthcare'],
    'safeguards_masking_excluded': ['iban'],
    'safeguards_masking_custom_fields': ['customer.loyalty_id', 'Internal_Code'],
    'safeguards_masking_custom_enabled': False,
    'request_hook_service': 'enmasse.mcp.request-hook',
    'response_hook_service': 'enmasse.mcp.response-hook',
}

# The keys the writer emits as YAML lists.
_list_keys = ['safeguards_masking_sets', 'safeguards_masking_excluded', 'safeguards_masking_custom_fields']

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingAndHookCatalogs(TestCase):
    """ Every catalog of the enmasse gateway support lists the six keys.
    """

    def test_every_key_has_an_importer_default(self:'any_') -> 'None':
        defaults = GatewayMCPImporter.connection_extra_field_defaults

        for key in _expected_values:
            self.assertIn(key, defaults, f'`{key}` has no importer default')

    def test_every_key_is_an_exporter_field(self:'any_') -> 'None':
        for key in _expected_values:
            self.assertIn(key, Gateway_Optional_Fields, f'`{key}` not in the exporter fields')

    def test_every_key_is_in_the_writer_order(self:'any_') -> 'None':
        order = _object_order['mcp_gateway']

        for key in _expected_values:

            if key in _list_keys:
                expected = f'{key}:list'
            else:
                expected = key

            self.assertIn(expected, order, f'`{expected}` not in the writer order')

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingAndHookRoundTrip(TestCase):
    """ Importing a gateway with data masking and hook services and exporting it back.
    """

    def setUp(self:'any_') -> 'None':

        # Server path for the database connection ..
        self.server_path = default_server_base_dir

        # .. the YAML template goes to a file of its own ..
        file_name = 'enmasse.mcp.masking.' + CryptoManager.generate_hex_string() + '.yaml'
        self.temp_file_path = os.path.join(gettempdir(), file_name)

        with open(self.temp_file_path, 'w') as temp_file:
            _ = temp_file.write(template_mcp_gateway)

        # .. the importer sets up the database state ..
        self.importer = EnmasseYAMLImporter()
        self.gateway_importer = GatewayMCPImporter(self.importer)

        # .. and the exporter reads it back.
        self.exporter = EnmasseYAMLExporter()
        self.gateway_exporter = GatewayMCPExporter(self.exporter)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        if self.session:
            self.session.close()
        os.remove(self.temp_file_path)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _import(self:'any_') -> 'stranydict':
        """ Imports what the file declares and answers with the stored opaque attributes, keyed by gateway name.
        """
        self.session = get_session_from_server_dir(self.server_path)

        yaml_config = self.importer.from_path(self.temp_file_path)
        created, _ = self.gateway_importer.sync_definitions(yaml_config['mcp_gateway'], self.session)

        out = {}

        for gateway in created:
            out[gateway.name] = json.loads(gateway.opaque1)

        return out

# ################################################################################################################################

    def _export(self:'any_') -> 'stranydict':
        """ Answers with the export of the imported gateways, keyed by gateway name.
        """
        out = {}

        for item in self.gateway_exporter.export(self.session):
            if item['name'].startswith('enmasse.mcp.masking.'):
                out[item['name']] = item

        return out

# ################################################################################################################################

    def test_the_keys_are_stored_verbatim(self:'any_') -> 'None':

        opaque_by_name = self._import()
        opaque = opaque_by_name['enmasse.mcp.masking.1']

        for key, expected in _expected_values.items():
            self.assertEqual(opaque[key], expected, f'`{key}` stored as {opaque[key]!r}')

# ################################################################################################################################

    def test_the_keys_are_exported_verbatim(self:'any_') -> 'None':

        _ = self._import()
        exported_by_name = self._export()

        item = exported_by_name['enmasse.mcp.masking.1']

        for key, expected in _expected_values.items():
            self.assertEqual(item[key], expected, f'`{key}` exported as {item.get(key)!r}')

# ################################################################################################################################

    def test_the_defaults_are_omitted_from_the_export(self:'any_') -> 'None':

        _ = self._import()
        exported_by_name = self._export()

        item = exported_by_name['enmasse.mcp.masking.2']

        for key in _expected_values:
            self.assertNotIn(key, item, f'`{key}` should not be in the export')

# ################################################################################################################################

    def test_the_export_imports_back_to_the_same_values(self:'any_') -> 'None':

        _ = self._import()
        exported_by_name = self._export()

        # The export of the first gateway becomes the input of a second import ..
        item = dict(exported_by_name['enmasse.mcp.masking.1'])
        item['name'] = 'enmasse.mcp.masking.reimported'
        item['url_path'] = '/mcp/enmasse-masking-reimported'

        created, _ = self.gateway_importer.sync_definitions([item], self.session)
        opaque = json.loads(created[0].opaque1)

        # .. and stores what the first import stored.
        for key, expected in _expected_values.items():
            self.assertEqual(opaque[key], expected, f'`{key}` stored as {opaque[key]!r} after a re-import')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

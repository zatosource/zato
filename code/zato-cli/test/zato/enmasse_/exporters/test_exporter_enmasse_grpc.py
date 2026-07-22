# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.grpc import OutgoingGRPCImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingGRPCExport(TestCase):
    """ Tests exporting gRPC outgoing definitions to YAML format.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()
        self.grpc_importer = OutgoingGRPCImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_outgoing_grpc_export(self):
        self._setup_test_environment()

        grpc_list_from_yaml = self.yaml_config['outgoing_grpc']

        created, _ = self.grpc_importer.sync_definitions(grpc_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('outgoing_grpc', exported_data)

        # Filter to test-created items only, ignoring pre-existing DB entries
        exported_grpc_list = []

        for item in exported_data['outgoing_grpc']:
            if item['name'].startswith('enmasse.'):
                exported_grpc_list.append(item)

        self.assertEqual(len(exported_grpc_list), 2)

        exported_by_name = {}
        for item in exported_grpc_list:
            exported_by_name[item['name']] = item

        for yaml_def in grpc_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def['name'], yaml_def['name'])
            if 'address' in yaml_def:
                self.assertEqual(exported_def['address'], yaml_def['address'])

        # Values that differ from the defaults round-trip through the export
        billing = exported_by_name['enmasse.grpc.outgoing.1']
        self.assertEqual(billing['proto_path'], '/opt/zato/proto/billing.proto')
        self.assertEqual(billing['ping_timeout'], 20)
        self.assertNotIn('is_tls', billing)

        inventory = exported_by_name['enmasse.grpc.outgoing.2']
        self.assertEqual(inventory['stub_module'], 'inventory_pb2_grpc')
        self.assertEqual(inventory['stub_class'], 'InventoryServiceStub')
        self.assertIs(inventory['is_tls'], False)

# ################################################################################################################################

    def test_outgoing_grpc_export_round_trip(self):
        self._setup_test_environment()

        grpc_list_from_yaml = self.yaml_config['outgoing_grpc']

        created, _ = self.grpc_importer.sync_definitions(grpc_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        # Filter to test-created items only, ignoring pre-existing DB entries
        exported_names = set()

        for item in exported_data['outgoing_grpc']:
            if item['name'].startswith('enmasse.'):
                exported_names.add(item['name'])

        yaml_names = set()

        for item in grpc_list_from_yaml:
            yaml_names.add(item['name'])

        self.assertEqual(exported_names, yaml_names)

# ################################################################################################################################

    def test_outgoing_grpc_export_empty(self):
        self._setup_test_environment()

        exported_data = self.exporter.export_to_dict(self.session)

        # Verify no test-created items exist, ignoring pre-existing DB entries
        if 'outgoing_grpc' in exported_data:

            test_items = []

            for item in exported_data['outgoing_grpc']:
                if item['name'].startswith('enmasse.'):
                    test_items.append(item)

            self.assertEqual(len(test_items), 0)

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

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.grpc import OutgoingGRPCImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingGRPCFromYAML(TestCase):
    """ Tests importing gRPC outgoing definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
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

    def test_outgoing_grpc_creation(self):
        self._setup_test_environment()

        grpc_defs = self.yaml_config['outgoing_grpc']
        created, updated = self.grpc_importer.sync_definitions(grpc_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        connection = self.session.query(GenericConn).filter_by(
            name='enmasse.grpc.outgoing.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_GRPC,
        ).one()
        self.assertEqual(connection.address, 'billing.example.com:50051')
        self.assertTrue(connection.is_active)

        # The connection-specific fields travel through opaque attributes
        opaque = parse_instance_opaque_attr(connection)
        self.assertEqual(opaque['proto_path'], '/opt/zato/proto/billing.proto')
        self.assertEqual(opaque['ping_timeout'], 20)
        self.assertTrue(opaque['is_tls'])

# ################################################################################################################################

    def test_outgoing_grpc_stub_module(self):
        self._setup_test_environment()

        grpc_defs = self.yaml_config['outgoing_grpc']
        _, _ = self.grpc_importer.sync_definitions(grpc_defs, self.session)

        connection = self.session.query(GenericConn).filter_by(
            name='enmasse.grpc.outgoing.2',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_GRPC,
        ).one()

        opaque = parse_instance_opaque_attr(connection)
        self.assertEqual(opaque['stub_module'], 'inventory_pb2_grpc')
        self.assertEqual(opaque['stub_class'], 'InventoryServiceStub')
        self.assertFalse(opaque['is_tls'])

# ################################################################################################################################

    def test_outgoing_grpc_update(self):
        self._setup_test_environment()

        grpc_defs = self.yaml_config['outgoing_grpc']
        grpc_def = grpc_defs[0]

        instance = self.grpc_importer.create_definition(grpc_def, self.session)
        self.session.commit()
        self.assertEqual(instance.address, 'billing.example.com:50051')

        update_def = {
            'name': grpc_def['name'],
            'id': instance.id,
            'address': 'billing-updated.example.com:50051',
        }

        updated_instance = self.grpc_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.address, 'billing-updated.example.com:50051')
        self.assertEqual(updated_instance.name, grpc_def['name'])

# ################################################################################################################################

    def test_sync_idempotent(self):
        self._setup_test_environment()

        grpc_list = self.yaml_config['outgoing_grpc']

        created1, updated1 = self.grpc_importer.sync_definitions(grpc_list, self.session)
        self.assertEqual(len(created1), 2)
        self.assertEqual(len(updated1), 0)

        created2, updated2 = self.grpc_importer.sync_definitions(grpc_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

        created3, updated3 = self.grpc_importer.sync_definitions(grpc_list, self.session)
        self.assertEqual(len(created3), 0)
        self.assertEqual(len(updated3), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

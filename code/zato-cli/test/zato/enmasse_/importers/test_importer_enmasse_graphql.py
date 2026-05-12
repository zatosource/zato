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
from zato.cli.enmasse.importers.graphql import OutgoingGraphQLImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingGraphQLFromYAML(TestCase):
    """ Tests importing GraphQL outgoing definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.graphql_importer = OutgoingGraphQLImporter(self.importer)

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

# ################################################################################################################################

    def test_outgoing_graphql_creation(self):
        self._setup_test_environment()

        graphql_defs = self.yaml_config['outgoing_graphql']
        created, updated = self.graphql_importer.sync_definitions(graphql_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        connection = self.session.query(GenericConn).filter_by(
            name='enmasse.graphql.outgoing.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL,
        ).one()
        self.assertEqual(connection.address, 'https://graph.microsoft.com/v1.0')
        self.assertTrue(connection.is_active)

# ################################################################################################################################

    def test_outgoing_graphql_update(self):
        self._setup_test_environment()

        graphql_defs = self.yaml_config['outgoing_graphql']
        graphql_def = graphql_defs[0]

        instance = self.graphql_importer.create_definition(graphql_def, self.session)
        self.session.commit()
        self.assertEqual(instance.address, 'https://graph.microsoft.com/v1.0')

        update_def = {
            'name': graphql_def['name'],
            'id': instance.id,
            'address': 'https://graphql-updated.example.com/api',
        }

        updated_instance = self.graphql_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.address, 'https://graphql-updated.example.com/api')
        self.assertEqual(updated_instance.name, graphql_def['name'])

# ################################################################################################################################

    def test_complete_outgoing_graphql_import_flow(self):
        self._setup_test_environment()

        graphql_list = self.yaml_config['outgoing_graphql']
        created, updated = self.graphql_importer.sync_definitions(graphql_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.graphql_importer.sync_definitions(graphql_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################

    def test_sync_idempotent(self):
        self._setup_test_environment()

        graphql_list = self.yaml_config['outgoing_graphql']

        created1, updated1 = self.graphql_importer.sync_definitions(graphql_list, self.session)
        self.assertEqual(len(created1), 2)
        self.assertEqual(len(updated1), 0)

        created2, updated2 = self.graphql_importer.sync_definitions(graphql_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

        created3, updated3 = self.graphql_importer.sync_definitions(graphql_list, self.session)
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

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
from zato.cli.enmasse.importers.graphql import OutgoingGraphQLImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingGraphQLExport(TestCase):
    """ Tests exporting GraphQL outgoing definitions to YAML format.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()
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

    def test_outgoing_graphql_export(self):
        self._setup_test_environment()

        graphql_list_from_yaml = self.yaml_config['outgoing_graphql']

        created, _ = self.graphql_importer.sync_definitions(graphql_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('outgoing_graphql', exported_data)
        exported_graphql_list = exported_data['outgoing_graphql']
        self.assertEqual(len(exported_graphql_list), 2)

        exported_by_name = {item['name']: item for item in exported_graphql_list}

        for yaml_def in graphql_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def['name'], yaml_def['name'])
            if 'address' in yaml_def:
                self.assertEqual(exported_def['address'], yaml_def['address'])

# ################################################################################################################################

    def test_outgoing_graphql_export_round_trip(self):
        self._setup_test_environment()

        graphql_list_from_yaml = self.yaml_config['outgoing_graphql']

        created, _ = self.graphql_importer.sync_definitions(graphql_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)
        exported_graphql_list = exported_data['outgoing_graphql']

        exported_names = set()

        for item in exported_graphql_list:
            exported_names.add(item['name'])

        yaml_names = set()

        for item in graphql_list_from_yaml:
            yaml_names.add(item['name'])

        self.assertEqual(exported_names, yaml_names)

# ################################################################################################################################

    def test_outgoing_graphql_export_empty(self):
        self._setup_test_environment()

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertNotIn('outgoing_graphql', exported_data)

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

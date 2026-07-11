# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from unittest import TestCase, main

# The directory with the shared Elasticsearch server helpers used by the live server tests
_es_tests_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'tests', 'python', 'zato-server', 'es'))
sys.path.insert(0, _es_tests_dir)

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import create_environment, delete_environment
from es_server import start_es, stop_es
from zato.cli.enmasse.client import get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from env_helper import TestEnvironment
    from es_server import ESServer
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict
    ESServer = ESServer
    TestEnvironment = TestEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_ElasticSearch_Dir'
    Conn_Name = 'enmasse.es.1'
    Second_Conn_Name = 'enmasse.es.2'

    # The port the instance the tests below start listens on
    Port = 9264

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseElasticSearchExporter(TestCase):
    """ Tests exporting Elasticsearch connection definitions to YAML-compatible dicts using enmasse,
    with the connections themselves pointing to a dynamically started Elasticsearch server.
    """

    es_server: 'ESServer'
    environment: 'TestEnvironment'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # A throwaway environment with its own ODB so the tests never touch any pre-existing one
        class_.environment = create_environment('zato-enmasse-es-exporter-')

        class_.es_server = start_es(
            port=ModuleCtx.Port,
            needs_tls=False,
        )

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        stop_es(class_.es_server)
        delete_environment(class_.environment)

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_ElasticSearch_Dir is not set')

        self.server_path = self.environment.server_dir

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.es_importer = ElasticSearchImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def get_address_list(self) -> 'str':
        out = f'{self.es_server.scheme}://{self.es_server.host}:{self.es_server.port}'
        return out

# ################################################################################################################################

    def get_definitions(self) -> 'list':

        first = {
            'name': ModuleCtx.Conn_Name,
            'address_list': self.get_address_list(),
            'username': 'enmasse-username',
            'password': 'enmasse-password',
        }

        second = {
            'name': ModuleCtx.Second_Conn_Name,
            'address_list': self.get_address_list(),
            'username': 'enmasse-username',
            'password': 'enmasse-password',
        }

        out = [first, second]

        return out

# ################################################################################################################################

    def test_es_export(self):
        self._setup_test_environment()

        # 1. Build the Elasticsearch connection definitions to be imported
        es_list_from_yaml = self.get_definitions()

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_es_connections, _ = self.es_importer.sync_definitions(es_list_from_yaml, self.session)

        self.assertEqual(len(created_es_connections), 2, 'Not all Elasticsearch connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('elastic_search', exported_data, 'Exporter did not produce an "elastic_search" section.')
        exported_es_list = exported_data['elastic_search']

        # 4. Compare exported data with the original definitions - note that the database may contain
        # other Elasticsearch connections too, which is why only the ones created by this test are compared.
        yaml_es_by_name = {}
        for item in es_list_from_yaml:
            yaml_es_by_name[item['name']] = item

        exported_es_by_name = {}
        for item in exported_es_list:
            if item['name'] in yaml_es_by_name:
                exported_es_by_name[item['name']] = item

        self.assertEqual(len(exported_es_by_name), len(yaml_es_by_name),
                         'Number of exported Elasticsearch connections does not match original YAML.')

        for name, yaml_def in yaml_es_by_name.items():

            self.assertIn(name, exported_es_by_name, f'Elasticsearch connection "{name}" from YAML not found in export.')
            exported_def = exported_es_by_name[name]

            # Compare all the options that were given on input - they must round trip unchanged
            for field in ['name', 'address_list', 'username']:
                self.assertEqual(exported_def.get(field), yaml_def.get(field),
                                 f'Mismatch for "{field}" in Elasticsearch connection "{name}"')

        # 5. The password must never appear in the exported data in plain text
        for item in exported_es_list:
            self.assertNotIn('password', item, 'Password must not be exported')
            self.assertNotIn('secret', item, 'Secret must not be exported')

            for value in item.values():
                if isinstance(value, str):
                    self.assertNotIn('enmasse-password', value, 'Password must not appear in exported values')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

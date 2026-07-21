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

# The directory with the shared MongoDB container helpers used by the live server tests
_mongodb_tests_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'tests', 'python', 'zato-server', 'mongodb'))
sys.path.insert(0, _mongodb_tests_dir)

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from containers import start_mongodb, stop_container
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mongodb import MongoDBImporter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import MongoDBServer
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict
    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_MongoDB'
    Conn_Name = 'enmasse.mongodb.1'
    Second_Conn_Name = 'enmasse.mongodb.2'

    # Details of the container the tests below start
    Container_Name = 'zato-enmasse-test-mongodb-export'
    Port = 27120
    Username = 'zato_enmasse_mongodb'
    Password = 'test-enmasse-mongodb-password'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMongoDBExporter(TestCase):
    """ Tests exporting MongoDB connection definitions to YAML-compatible dicts using enmasse,
    with the connections themselves pointing to a dynamically started MongoDB server.
    """

    mongodb_server: 'MongoDBServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.mongodb_server = start_mongodb(
            container_name=ModuleCtx.Container_Name,
            port=ModuleCtx.Port,
            username=ModuleCtx.Username,
            password=ModuleCtx.Password,
            needs_tls=False,
        )

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        stop_container(class_.mongodb_server.container_name)

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_MongoDB is not set')

        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.mongodb_importer = MongoDBImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def get_server_list(self) -> 'str':
        out = f'{self.mongodb_server.host}:{self.mongodb_server.port}'
        return out

# ################################################################################################################################

    def get_definitions(self) -> 'list':

        first = {
            'name': ModuleCtx.Conn_Name,
            'server_list': self.get_server_list(),
            'username': self.mongodb_server.username,
            'password': self.mongodb_server.password,
        }

        second = {
            'name': ModuleCtx.Second_Conn_Name,
            'server_list': self.get_server_list(),
            'username': self.mongodb_server.username,
            'password': self.mongodb_server.password,
        }

        out = [first, second]

        return out

# ################################################################################################################################

    def test_mongodb_export(self):
        self._setup_test_environment()

        # 1. Build the MongoDB connection definitions to be imported
        mongodb_list_from_yaml = self.get_definitions()

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_mongodb_connections, _ = self.mongodb_importer.sync_definitions(mongodb_list_from_yaml, self.session)

        self.assertEqual(len(created_mongodb_connections), 2, 'Not all MongoDB connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('mongodb', exported_data, 'Exporter did not produce a "mongodb" section.')
        exported_mongodb_list = exported_data['mongodb']

        # 4. Compare exported data with the original definitions - note that the database may contain
        # other MongoDB connections too, which is why only the ones created by this test are compared.
        yaml_mongodb_by_name = {}
        for item in mongodb_list_from_yaml:
            yaml_mongodb_by_name[item['name']] = item

        exported_mongodb_by_name = {}
        for item in exported_mongodb_list:
            if item['name'] in yaml_mongodb_by_name:
                exported_mongodb_by_name[item['name']] = item

        self.assertEqual(len(exported_mongodb_by_name), len(yaml_mongodb_by_name),
                         'Number of exported MongoDB connections does not match original YAML.')

        for name, yaml_def in yaml_mongodb_by_name.items():

            self.assertIn(name, exported_mongodb_by_name, f'MongoDB connection "{name}" from YAML not found in export.')
            exported_def = exported_mongodb_by_name[name]

            # Compare all the options that were given on input - they must round trip unchanged
            for field in ['name', 'server_list', 'username']:
                self.assertEqual(exported_def.get(field), yaml_def.get(field),
                                 f'Mismatch for "{field}" in MongoDB connection "{name}"')

        # 5. The password must never appear in the exported data in plain text
        for item in exported_mongodb_list:
            self.assertNotIn('password', item, 'Password must not be exported')
            self.assertNotIn('secret', item, 'Secret must not be exported')

            for value in item.values():
                if isinstance(value, str):
                    self.assertNotIn(self.mongodb_server.password, value, 'Password must not appear in exported values')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

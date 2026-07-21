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

# The directory with the shared MongoDB container helpers used by the live server tests
_mongodb_tests_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'tests', 'python', 'zato-server', 'mongodb'))
sys.path.insert(0, _mongodb_tests_dir)

# PyYAML
import yaml

# Bunch
from zato.common.ext.bunch import bunchify

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from containers import start_mongodb, stop_container
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mongodb import MongoDBImporter
from zato.common.api import GENERIC, MongoDB
from zato.common.odb.model import GenericConn
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.generic.api.outconn_mongodb import OutconnMongoDBWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import MongoDBServer
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict
    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

# Letters from three alphabets - one of the connections below uses them all in its name
# to prove the round trip through YAML and the ODB does not corrupt Unicode.
Dutch_Letters = 'ÁÉÍÓÚË'
Greek_Letters = 'ΑΒΓΔΕΖ'
Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_MongoDB'
    Conn_Name = 'enmasse.mongodb.1'
    Unicode_Conn_Name = 'enmasse.mongodb.' + Dutch_Letters + '.' + Greek_Letters + '.' + Korean_Letters + '.1'

    # Details of the container the tests below start
    Container_Name = 'zato-enmasse-test-mongodb'
    Port = 27119
    Username = 'zato_enmasse_mongodb'
    Password = 'test-enmasse-mongodb-password'

# ################################################################################################################################
# ################################################################################################################################

class _TestServer:
    """ A minimal stand-in for ParallelServer - the wrapper only needs the decrypt method
    and the test passwords are never encrypted, which is why they are returned as they are.
    """
    def decrypt(self, value:'str') -> 'str':
        return value

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMongoDBFromYAML(TestCase):
    """ Tests importing MongoDB connection definitions from YAML files using enmasse,
    against a dynamically started MongoDB server.
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

        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # The YAML configuration with two connections - one with an ASCII name and one with a Unicode one
        yaml_data = yaml.safe_dump(self.get_yaml_dict(), allow_unicode=True)

        # Create a temporary file with the configuration
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(yaml_data.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize MongoDB importer
        self.mongodb_importer = MongoDBImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def get_server_list(self) -> 'str':
        out = f'{self.mongodb_server.host}:{self.mongodb_server.port}'
        return out

# ################################################################################################################################

    def get_yaml_dict(self) -> 'stranydict':

        # A connection with a plain ASCII name ..
        ascii_named = {
            'name': ModuleCtx.Conn_Name,
            'server_list': self.get_server_list(),
            'username': self.mongodb_server.username,
            'password': self.mongodb_server.password,
        }

        # .. and one whose name contains Dutch, Greek and Korean letters.
        unicode_named = {
            'name': ModuleCtx.Unicode_Conn_Name,
            'server_list': self.get_server_list(),
            'username': self.mongodb_server.username,
            'password': self.mongodb_server.password,
        }

        out = {'mongodb': [ascii_named, unicode_named]}

        return out

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def _build_wrapper_from_instance(self, instance:'any_') -> 'OutconnMongoDBWrapper':
        """ Builds a connection wrapper out of what was actually stored in the database for the input connection.
        """

        # The server list lives in the instance's opaque attributes
        opaque = parse_instance_opaque_attr(instance)

        config = bunchify({
            'id': instance.id,
            'name': instance.name,
            'is_active': True,
            'server_list': opaque.server_list,
            'username': instance.username,
            'secret': instance.secret,
            'auth_source': opaque.auth_source,
            'replica_set': '',
            'app_name': opaque.app_name,
            'pool_size_max': opaque.pool_size_max,
            'connect_timeout': opaque.connect_timeout,
            'server_select_timeout': opaque.server_select_timeout,
            'is_tls_enabled': False,
            'tls_ca_certs_file': '',
            'tls_cert_key_file': '',
            'is_tls_validation_enabled': True,
        })

        wrapper = OutconnMongoDBWrapper(config, cast_('any_', _TestServer()))

        return wrapper

# ################################################################################################################################

    def test_mongodb_definition_creation(self):
        """ Test creating MongoDB connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        mongodb_defs = self.yaml_config['mongodb']

        # Process all MongoDB definitions
        created, updated = self.mongodb_importer.sync_definitions(mongodb_defs, self.session)

        # Should have created both definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify each connection was created correctly, the Unicode name included
        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB
            ).one()

            opaque = parse_instance_opaque_attr(instance)

            self.assertEqual(opaque.server_list, self.get_server_list())
            self.assertEqual(opaque.auth_source, MongoDB.Default.Auth_Source)
            self.assertEqual(instance.username, self.mongodb_server.username)
            self.assertEqual(instance.secret, self.mongodb_server.password)

# ################################################################################################################################

    def test_mongodb_live_ping_after_import(self):
        """ Test that both imported connections actually work against the live MongoDB server.
        """
        self._setup_test_environment()

        # Import both definitions first
        mongodb_defs = self.yaml_config['mongodb']
        created, _ = self.mongodb_importer.sync_definitions(mongodb_defs, self.session)
        self.assertEqual(len(created), 2)

        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB
            ).one()

            # Build a wrapper out of the imported connection ..
            wrapper = self._build_wrapper_from_instance(instance)
            wrapper.build_wrapper(False)

            # .. and a live ping must succeed.
            wrapper.ping()

# ################################################################################################################################

    def test_mongodb_update(self):
        """ Test updating existing MongoDB connection definitions.
        """
        self._setup_test_environment()

        # First, get the MongoDB definition from YAML and create it
        mongodb_defs = self.yaml_config['mongodb']
        mongodb_def = mongodb_defs[0]

        # Create the MongoDB definition
        instance = self.mongodb_importer.create_definition(mongodb_def, self.session)
        self.session.commit()

        opaque = parse_instance_opaque_attr(instance)
        self.assertEqual(opaque.server_list, self.get_server_list())

        # Prepare an update definition based on the existing one
        update_def = {
            'name': mongodb_def['name'],
            'id': instance.id,
            'server_list': 'mongodb.updated.example.com:27017',
            'username': 'updated-username',
        }

        # Update the MongoDB definition
        updated_instance = self.mongodb_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(opaque.server_list, 'mongodb.updated.example.com:27017')
        self.assertEqual(updated_instance.username, 'updated-username')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB)

# ################################################################################################################################

    def test_complete_mongodb_import_flow(self):
        """ Test the complete flow of importing MongoDB connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all MongoDB definitions from the YAML
        mongodb_list = self.yaml_config['mongodb']
        mongodb_created, mongodb_updated = self.mongodb_importer.sync_definitions(mongodb_list, self.session)

        # Update importer's MongoDB definitions
        self.importer.mongodb_defs = self.mongodb_importer.connection_defs

        # Verify MongoDB definitions were created
        self.assertEqual(len(mongodb_created), 2)
        self.assertEqual(len(mongodb_updated), 0)

        # Verify the MongoDB definitions dictionary was populated
        self.assertEqual(len(self.mongodb_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.mongodb_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        mongodb_created2, mongodb_updated2 = self.mongodb_importer.sync_definitions(mongodb_list, self.session)
        self.assertEqual(len(mongodb_created2), 0)
        self.assertEqual(len(mongodb_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

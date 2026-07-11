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

# The directory with the shared Elasticsearch server helpers used by the live server tests
_es_tests_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'tests', 'python', 'zato-server', 'es'))
sys.path.insert(0, _es_tests_dir)

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# PyYAML
import yaml

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from env_helper import create_environment, delete_environment
from es_server import start_es, stop_es
from zato.cli.enmasse.client import get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.common.api import ES, GENERIC
from zato.common.odb.model import GenericConn
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.generic.api.outconn_es import OutconnESWrapper

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

# Letters from three alphabets - one of the connections below uses them all in its name
# to prove the round trip through YAML and the ODB does not corrupt Unicode.
Dutch_Letters = 'ÁÉÍÓÚË'
Greek_Letters = 'ΑΒΓΔΕΖ'
Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_ElasticSearch_Dir'
    Conn_Name = 'enmasse.es.1'
    Unicode_Conn_Name = 'enmasse.es.' + Dutch_Letters + '.' + Greek_Letters + '.' + Korean_Letters + '.1'

    # The port the instance the tests below start listens on
    Port = 9263

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

class TestEnmasseElasticSearchFromYAML(TestCase):
    """ Tests importing Elasticsearch connection definitions from YAML files using enmasse,
    against a dynamically started Elasticsearch server.
    """

    es_server: 'ESServer'
    environment: 'TestEnvironment'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # A throwaway environment with its own ODB so the tests never touch any pre-existing one
        class_.environment = create_environment('zato-enmasse-es-importer-')

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

        # Server path for database connection
        self.server_path = self.environment.server_dir

        # The YAML configuration with two connections - one with an ASCII name and one with a Unicode one
        yaml_data = yaml.safe_dump(self.get_yaml_dict(), allow_unicode=True)

        # Create a temporary file with the configuration
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(yaml_data.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize Elasticsearch importer
        self.es_importer = ElasticSearchImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:

            # Remove the connections created by the test so each test starts from a clean slate
            _ = self.session.query(GenericConn).filter(GenericConn.name.like('enmasse.es.%')).delete(
                synchronize_session=False)
            self.session.commit()

            self.session.close()
        os.unlink(self.temp_file.name)

# ################################################################################################################################

    def get_address_list(self) -> 'str':
        out = f'{self.es_server.scheme}://{self.es_server.host}:{self.es_server.port}'
        return out

# ################################################################################################################################

    def get_yaml_dict(self) -> 'stranydict':

        # A connection with a plain ASCII name ..
        ascii_named = {
            'name': ModuleCtx.Conn_Name,
            'address_list': self.get_address_list(),
        }

        # .. and one whose name contains Dutch, Greek and Korean letters.
        unicode_named = {
            'name': ModuleCtx.Unicode_Conn_Name,
            'address_list': self.get_address_list(),
        }

        out = {'elastic_search': [ascii_named, unicode_named]}

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

    def _build_wrapper_from_instance(self, instance:'any_') -> 'OutconnESWrapper':
        """ Builds a connection wrapper out of what was actually stored in the database for the input connection.
        """

        # The address list lives in the instance's opaque attributes
        opaque = parse_instance_opaque_attr(instance)

        config = bunchify({
            'id': instance.id,
            'name': instance.name,
            'is_active': True,
            'address_list': opaque.address_list,
            'username': instance.username,
            'secret': instance.secret,
            'timeout': instance.timeout,
            'is_tls_validation_enabled': True,
            'tls_ca_certs_file': '',
            'tls_cert_key_file': '',
        })

        wrapper = OutconnESWrapper(config, cast_('any_', _TestServer()))

        return wrapper

# ################################################################################################################################

    def test_es_definition_creation(self):
        """ Test creating Elasticsearch connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        es_defs = self.yaml_config['elastic_search']

        # Process all Elasticsearch definitions
        created, updated = self.es_importer.sync_definitions(es_defs, self.session)

        # Should have created both definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify each connection was created correctly, the Unicode name included
        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_ES
            ).one()

            opaque = parse_instance_opaque_attr(instance)

            self.assertEqual(opaque.address_list, self.get_address_list())
            self.assertEqual(instance.timeout, ES.Default.Timeout)
            self.assertEqual(instance.username, '')

# ################################################################################################################################

    def test_es_live_ping_after_import(self):
        """ Test that both imported connections actually work against the live Elasticsearch server.
        """
        self._setup_test_environment()

        # Import both definitions first
        es_defs = self.yaml_config['elastic_search']
        created, _ = self.es_importer.sync_definitions(es_defs, self.session)
        self.assertEqual(len(created), 2)

        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_ES
            ).one()

            # Build a wrapper out of the imported connection ..
            wrapper = self._build_wrapper_from_instance(instance)
            wrapper.build_wrapper(False)

            # .. and a live ping must succeed.
            wrapper.ping()

# ################################################################################################################################

    def test_es_update(self):
        """ Test updating existing Elasticsearch connection definitions.
        """
        self._setup_test_environment()

        # First, get the Elasticsearch definition from YAML and create it
        es_defs = self.yaml_config['elastic_search']
        es_def = es_defs[0]

        # Create the Elasticsearch definition
        instance = self.es_importer.create_definition(es_def, self.session)
        self.session.commit()

        opaque = parse_instance_opaque_attr(instance)
        self.assertEqual(opaque.address_list, self.get_address_list())

        # Prepare an update definition based on the existing one
        update_def = {
            'name': es_def['name'],
            'id': instance.id,
            'address_list': 'https://es.updated.example.com:9200',
            'username': 'updated-username',
            'timeout': 33,
        }

        # Update the Elasticsearch definition
        updated_instance = self.es_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(opaque.address_list, 'https://es.updated.example.com:9200')
        self.assertEqual(updated_instance.timeout, 33)
        self.assertEqual(updated_instance.username, 'updated-username')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_ES)

# ################################################################################################################################

    def test_complete_es_import_flow(self):
        """ Test the complete flow of importing Elasticsearch connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Elasticsearch definitions from the YAML
        es_list = self.yaml_config['elastic_search']
        es_created, es_updated = self.es_importer.sync_definitions(es_list, self.session)

        # Update importer's Elasticsearch definitions
        self.importer.es_defs = self.es_importer.connection_defs

        # Verify Elasticsearch definitions were created
        self.assertEqual(len(es_created), 2)
        self.assertEqual(len(es_updated), 0)

        # Verify the Elasticsearch definitions dictionary was populated
        self.assertEqual(len(self.es_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.es_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        es_created2, es_updated2 = self.es_importer.sync_definitions(es_list, self.session)
        self.assertEqual(len(es_created2), 0)
        self.assertEqual(len(es_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

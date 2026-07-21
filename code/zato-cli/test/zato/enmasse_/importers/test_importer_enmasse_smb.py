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

# PyYAML
import yaml

# Bunch
from zato.common.ext.bunch import bunchify

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.smb import SMBImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.smb_ import SMBTestServer
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.generic.api.outconn_smb import SMBClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

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
    Env_Key_Should_Test = 'Zato_Test_SMB'
    Conn_Name = 'enmasse.smb.1'
    Unicode_Conn_Name = 'enmasse.smb.' + Dutch_Letters + '.' + Greek_Letters + '.' + Korean_Letters + '.1'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSMBFromYAML(TestCase):
    """ Tests importing SMB connection definitions from YAML files using enmasse,
    against a dynamically started SMB server.
    """

    smb_server: 'SMBTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.smb_server = SMBTestServer()
        class_.smb_server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.smb_server.stop()

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_SMB is not set')

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

        # Initialize SMB importer
        self.smb_importer = SMBImporter(self.importer)

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

    def get_yaml_dict(self) -> 'stranydict':

        # A connection with a plain ASCII name ..
        ascii_named = {
            'name': ModuleCtx.Conn_Name,
            'host': self.smb_server.host,
            'port': self.smb_server.port,
            'username': self.smb_server.username,
            'password': self.smb_server.password,
        }

        # .. and one whose name contains Dutch, Greek and Korean letters.
        unicode_named = {
            'name': ModuleCtx.Unicode_Conn_Name,
            'host': self.smb_server.host,
            'port': self.smb_server.port,
            'username': self.smb_server.username,
            'password': self.smb_server.password,
        }

        out = {'smb': [ascii_named, unicode_named]}

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

    def _build_client_from_instance(self, instance:'any_') -> 'SMBClient':
        """ Builds an SMBClient out of what was actually stored in the database for the input connection.
        """

        # The host lives in the instance's opaque attributes
        opaque = parse_instance_opaque_attr(instance)

        config = bunchify({
            'id': instance.id,
            'name': instance.name,
            'is_active': True,
            'host': opaque.host,
            'port': instance.port,
            'username': instance.username,
            'secret': instance.secret,
        })

        client = SMBClient(config, cast_('any_', None))

        return client

# ################################################################################################################################

    def test_smb_definition_creation(self):
        """ Test creating SMB connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        smb_defs = self.yaml_config['smb']

        # Process all SMB definitions
        created, updated = self.smb_importer.sync_definitions(smb_defs, self.session)

        # Should have created both definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify each connection was created correctly, the Unicode name included
        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_SMB
            ).one()

            opaque = parse_instance_opaque_attr(instance)

            self.assertEqual(opaque.host, self.smb_server.host)
            self.assertEqual(instance.port, self.smb_server.port)
            self.assertEqual(instance.username, self.smb_server.username)
            self.assertEqual(instance.secret, self.smb_server.password)

# ################################################################################################################################

    def test_smb_live_ping_after_import(self):
        """ Test that both imported connections actually work against the live SMB server.
        """
        self._setup_test_environment()

        # Import both definitions first
        smb_defs = self.yaml_config['smb']
        created, _ = self.smb_importer.sync_definitions(smb_defs, self.session)
        self.assertEqual(len(created), 2)

        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_SMB
            ).one()

            # Build a client out of the imported connection ..
            client = self._build_client_from_instance(instance)

            # .. and a live ping must succeed.
            client.ping()

# ################################################################################################################################

    def test_smb_update(self):
        """ Test updating existing SMB connection definitions.
        """
        self._setup_test_environment()

        # First, get the SMB definition from YAML and create it
        smb_defs = self.yaml_config['smb']
        smb_def = smb_defs[0]

        # Create the SMB definition
        instance = self.smb_importer.create_definition(smb_def, self.session)
        self.session.commit()

        opaque = parse_instance_opaque_attr(instance)
        self.assertEqual(opaque.host, self.smb_server.host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': smb_def['name'],
            'id': instance.id,
            'host': 'smb.updated.example.com',
            'username': 'updated-username',
        }

        # Update the SMB definition
        updated_instance = self.smb_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(opaque.host, 'smb.updated.example.com')
        self.assertEqual(updated_instance.username, 'updated-username')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_SMB)

# ################################################################################################################################

    def test_complete_smb_import_flow(self):
        """ Test the complete flow of importing SMB connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all SMB definitions from the YAML
        smb_list = self.yaml_config['smb']
        smb_created, smb_updated = self.smb_importer.sync_definitions(smb_list, self.session)

        # Update importer's SMB definitions
        self.importer.smb_defs = self.smb_importer.connection_defs

        # Verify SMB definitions were created
        self.assertEqual(len(smb_created), 2)
        self.assertEqual(len(smb_updated), 0)

        # Verify the SMB definitions dictionary was populated
        self.assertEqual(len(self.smb_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.smb_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        smb_created2, smb_updated2 = self.smb_importer.sync_definitions(smb_list, self.session)
        self.assertEqual(len(smb_created2), 0)
        self.assertEqual(len(smb_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

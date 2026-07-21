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
from zato.cli.enmasse.importers.sftp import SFTPImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.sftp_ import SFTPTestServer
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.generic.api.outconn_sftp import SFTPClient

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
    Env_Key_Should_Test = 'Zato_Test_SFTP'
    Key_Conn_Name = 'enmasse.sftp.key.1'
    Password_Conn_Name = 'enmasse.sftp.password.' + Dutch_Letters + '.' + Greek_Letters + '.' + Korean_Letters + '.1'

    # Names of environment variables that point to private key files on disk -
    # the YAML definitions below carry these names, not the paths themselves.
    Env_Key_Private_Key = 'Zato_Test_Enmasse_SFTP_Key'
    Env_Key_Private_Key_Encrypted = 'Zato_Test_Enmasse_SFTP_Key_Encrypted'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSFTPFromYAML(TestCase):
    """ Tests importing SFTP connection definitions from YAML files using enmasse,
    against a dynamically started SSH server.
    """

    sftp_server: 'SFTPTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.sftp_server = SFTPTestServer()
        class_.sftp_server.start()

        # Export the variables that the YAML definitions refer to by name
        os.environ[ModuleCtx.Env_Key_Private_Key] = class_.sftp_server.client_key_path
        os.environ[ModuleCtx.Env_Key_Private_Key_Encrypted] = class_.sftp_server.client_key_encrypted_path

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.sftp_server.stop()

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_SFTP is not set')

        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # The YAML configuration with two connections - one key-based and one password-based
        yaml_data = yaml.safe_dump(self.get_yaml_dict(), allow_unicode=True)

        # Create a temporary file with the configuration
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(yaml_data.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize SFTP importer
        self.sftp_importer = SFTPImporter(self.importer)

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

    def get_address(self) -> 'str':

        out = '{}:{}'.format(self.sftp_server.host, self.sftp_server.port)

        return out

# ################################################################################################################################

    def get_yaml_dict(self) -> 'stranydict':

        # A connection that authenticates with a plain key ..
        key_based = {
            'name': ModuleCtx.Key_Conn_Name,
            'address': self.get_address(),
            'username': self.sftp_server.username,
            'private_key': ModuleCtx.Env_Key_Private_Key,

            # The test server's host key is freshly generated, which means it cannot be in known_hosts yet
            'strict_host_key_checking': False,
        }

        # .. and one, with a Unicode name, that authenticates with an encrypted key
        # .. whose passphrase is the connection's password, which exercises the askpass path.
        password_based = {
            'name': ModuleCtx.Password_Conn_Name,
            'address': self.get_address(),
            'username': self.sftp_server.username,
            'private_key': ModuleCtx.Env_Key_Private_Key_Encrypted,
            'password': self.sftp_server.password,
            'strict_host_key_checking': False,
        }

        out = {'sftp': [key_based, password_based]}

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

    def _build_client_from_instance(self, instance:'any_') -> 'SFTPClient':
        """ Builds an SFTPClient out of what was actually stored in the database for the input connection.
        """

        # The private key and host key checking mode live in the instance's opaque attributes
        opaque = parse_instance_opaque_attr(instance)

        config = bunchify({
            'id': instance.id,
            'name': instance.name,
            'is_active': True,
            'address': instance.address,
            'username': instance.username,
            'secret': instance.secret,
            'private_key': opaque.private_key,
            'strict_host_key_checking': opaque.strict_host_key_checking,
        })

        client = SFTPClient(config, cast_('any_', None))

        # Keep the throwaway host keys of test servers out of the user's known_hosts file
        client.base_args.append('-o')
        client.base_args.append('UserKnownHostsFile=/dev/null')

        return client

# ################################################################################################################################

    def test_sftp_definition_creation(self):
        """ Test creating SFTP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        sftp_defs = self.yaml_config['sftp']

        # Process all SFTP definitions
        created, updated = self.sftp_importer.sync_definitions(sftp_defs, self.session)

        # Should have created both definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify the key-based connection was created correctly
        key_based = self.session.query(GenericConn).filter_by(
            name=ModuleCtx.Key_Conn_Name,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        ).one()

        opaque = parse_instance_opaque_attr(key_based)

        self.assertEqual(key_based.address, self.get_address())
        self.assertEqual(key_based.username, self.sftp_server.username)
        self.assertEqual(opaque.private_key, ModuleCtx.Env_Key_Private_Key)
        self.assertFalse(opaque.strict_host_key_checking)

        # Verify the password-based connection, the Unicode name included,
        # stored its password as the secret.
        password_based = self.session.query(GenericConn).filter_by(
            name=ModuleCtx.Password_Conn_Name,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        ).one()

        self.assertEqual(password_based.secret, self.sftp_server.password)

# ################################################################################################################################

    def test_sftp_live_ping_after_import(self):
        """ Test that both imported connections actually work against the live SSH server,
        proving the key path and the askpass password path both work end to end.
        """
        self._setup_test_environment()

        # Import both definitions first
        sftp_defs = self.yaml_config['sftp']
        created, _ = self.sftp_importer.sync_definitions(sftp_defs, self.session)
        self.assertEqual(len(created), 2)

        for name in [ModuleCtx.Key_Conn_Name, ModuleCtx.Password_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
            ).one()

            # Build a client out of the imported connection ..
            client = self._build_client_from_instance(instance)

            # .. a live ping must succeed ..
            ping_result = client.ping()
            self.assertTrue(ping_result.is_ok, 'Ping failed for `{}` -> {}'.format(name, ping_result.stderr))

            # .. and so must a live ls command.
            ls_result = client.execute('test-cid-{}'.format(name), 'ls {}'.format(self.sftp_server.files_dir))
            self.assertTrue(ls_result.is_ok, 'ls failed for `{}` -> {}'.format(name, ls_result.stderr))

# ################################################################################################################################

    def test_sftp_update(self):
        """ Test updating existing SFTP connection definitions.
        """
        self._setup_test_environment()

        # First, get the SFTP definition from YAML and create it
        sftp_defs = self.yaml_config['sftp']
        sftp_def = sftp_defs[0]

        # Create the SFTP definition
        instance = self.sftp_importer.create_definition(sftp_def, self.session)
        self.session.commit()

        self.assertEqual(instance.address, self.get_address())

        # Prepare an update definition based on the existing one
        update_def = {
            'name': sftp_def['name'],
            'id': instance.id,
            'address': 'sftp.updated.example.com:22022',
            'username': 'updated-username',
        }

        # Update the SFTP definition
        updated_instance = self.sftp_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'sftp.updated.example.com:22022')
        self.assertEqual(updated_instance.username, 'updated-username')

        # The update did not mention host key checking, which means the default of True was applied
        opaque = parse_instance_opaque_attr(updated_instance)
        self.assertTrue(opaque.strict_host_key_checking)

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP)

# ################################################################################################################################

    def test_complete_sftp_import_flow(self):
        """ Test the complete flow of importing SFTP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all SFTP definitions from the YAML
        sftp_list = self.yaml_config['sftp']
        sftp_created, sftp_updated = self.sftp_importer.sync_definitions(sftp_list, self.session)

        # Update importer's SFTP definitions
        self.importer.sftp_defs = self.sftp_importer.connection_defs

        # Verify SFTP definitions were created
        self.assertEqual(len(sftp_created), 2)
        self.assertEqual(len(sftp_updated), 0)

        # Verify the SFTP definitions dictionary was populated
        self.assertEqual(len(self.sftp_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.sftp_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        sftp_created2, sftp_updated2 = self.sftp_importer.sync_definitions(sftp_list, self.session)
        self.assertEqual(len(sftp_created2), 0)
        self.assertEqual(len(sftp_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

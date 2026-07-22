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

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sftp import SFTPImporter
from zato.common.test.sftp_ import SFTPTestServer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_SFTP'
    Conn_Name = 'enmasse.sftp.1'
    Second_Conn_Name = 'enmasse.sftp.2'

    # Names of environment variables that point to private key files on disk -
    # the YAML definitions below carry these names, not the paths themselves.
    Env_Key_Private_Key = 'Zato_Test_Enmasse_SFTP_Key'
    Env_Key_Private_Key_Encrypted = 'Zato_Test_Enmasse_SFTP_Key_Encrypted'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSFTPExporter(TestCase):
    """ Tests exporting SFTP connection definitions to YAML-compatible dicts using enmasse,
    with the connections themselves pointing to a dynamically started SSH server.
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

        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.sftp_importer = SFTPImporter(self.importer)

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

    def get_address(self) -> 'str':

        out = '{}:{}'.format(self.sftp_server.host, self.sftp_server.port)

        return out

# ################################################################################################################################

    def get_definitions(self) -> 'list':

        # The first connection authenticates with an encrypted key whose passphrase is the password,
        # with host key checking turned off because the test server's key is freshly generated.
        first = {
            'name': ModuleCtx.Conn_Name,
            'address': self.get_address(),
            'username': self.sftp_server.username,
            'password': self.sftp_server.password,
            'private_key': ModuleCtx.Env_Key_Private_Key_Encrypted,
            'strict_host_key_checking': False,
        }

        # The second one uses a plain key and leaves host key checking at its default of True
        second = {
            'name': ModuleCtx.Second_Conn_Name,
            'address': self.get_address(),
            'username': self.sftp_server.username,
            'private_key': ModuleCtx.Env_Key_Private_Key,
        }

        out = [first, second]

        return out

# ################################################################################################################################

    def test_sftp_export(self):
        self._setup_test_environment()

        # 1. Build the SFTP connection definitions to be imported
        sftp_list_from_yaml = self.get_definitions()

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_sftp_connections, _ = self.sftp_importer.sync_definitions(sftp_list_from_yaml, self.session)

        self.assertEqual(len(created_sftp_connections), 2, 'Not all SFTP connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('sftp', exported_data, 'Exporter did not produce a "sftp" section.')
        exported_sftp_list = exported_data['sftp']

        # 4. Compare exported data with the original definitions - note that the database may contain
        # other SFTP connections too, which is why only the ones created by this test are compared.
        yaml_sftp_by_name = {}
        for item in sftp_list_from_yaml:
            yaml_sftp_by_name[item['name']] = item

        exported_sftp_by_name = {}
        for item in exported_sftp_list:
            if item['name'] in yaml_sftp_by_name:
                exported_sftp_by_name[item['name']] = item

        self.assertEqual(len(exported_sftp_by_name), len(yaml_sftp_by_name),
                         'Number of exported SFTP connections does not match original YAML.')

        for name, yaml_def in yaml_sftp_by_name.items():

            self.assertIn(name, exported_sftp_by_name, f'SFTP connection "{name}" from YAML not found in export.')
            exported_def = exported_sftp_by_name[name]

            # Compare all the options that were given on input - they must round trip unchanged
            for field in ['name', 'address', 'username', 'private_key']:
                self.assertEqual(exported_def.get(field), yaml_def.get(field),
                                 f'Mismatch for "{field}" in SFTP connection "{name}"')

        # 5. Host key checking is only exported when it differs from the default of True
        first_exported = exported_sftp_by_name[ModuleCtx.Conn_Name]
        second_exported = exported_sftp_by_name[ModuleCtx.Second_Conn_Name]

        self.assertFalse(first_exported['strict_host_key_checking'])
        self.assertNotIn('strict_host_key_checking', second_exported)

        # 6. The password must never appear in the exported data in plain text
        for item in exported_sftp_list:
            self.assertNotIn('password', item, 'Password must not be exported')
            self.assertNotIn('secret', item, 'Secret must not be exported')

            for value in item.values():
                if isinstance(value, str):
                    self.assertNotIn(self.sftp_server.password, value, 'Password must not appear in exported values')

# ################################################################################################################################

    def test_sftp_schedules_export(self):
        """ Test that a connection's schedules round trip through import and export in their portable shape -
        without database-specific fields and without options that match the defaults.
        """
        self._setup_test_environment()

        # A connection with one schedule that overrides some options and leaves the rest at their defaults
        conn_def = {
            'name': ModuleCtx.Conn_Name,
            'address': self.get_address(),
            'username': self.sftp_server.username,
            'private_key': ModuleCtx.Env_Key_Private_Key,
            'schedules': [
                {
                    'name': 'invoices.hourly',
                    'directory': '/incoming/invoices',
                    'service': 'demo.ping',
                    'run_every': 30,
                    'run_unit': 'minutes',
                    'pattern': '*.csv',
                    'should_claim': True,
                },
            ],
        }

        # Import the connection along with its schedule ..
        _ = self.importer.get_cluster(self.session)
        created, _ = self.sftp_importer.sync_definitions([conn_def], self.session)
        self.assertEqual(len(created), 1)

        # .. and export everything back.
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        exported_def = None
        for item in exported_data['sftp']:
            if item['name'] == ModuleCtx.Conn_Name:
                exported_def = item
                break

        self.assertIsNotNone(exported_def)

        # The schedule travels in its portable shape ..
        schedules = exported_def['schedules']
        self.assertEqual(len(schedules), 1)

        schedule = schedules[0]

        # .. with what was given on input ..
        self.assertEqual(schedule['name'], 'invoices.hourly')
        self.assertEqual(schedule['directory'], '/incoming/invoices')
        self.assertEqual(schedule['service'], 'demo.ping')
        self.assertEqual(schedule['run_every'], 30)
        self.assertEqual(schedule['run_unit'], 'minutes')
        self.assertEqual(schedule['pattern'], '*.csv')
        self.assertTrue(schedule['should_claim'])

        # .. without database-specific fields ..
        self.assertNotIn('id', schedule)
        self.assertNotIn('job_id', schedule)

        # .. and without options left at their defaults.
        self.assertNotIn('is_active', schedule)
        self.assertNotIn('ready_how', schedule)
        self.assertNotIn('stability_delay', schedule)
        self.assertNotIn('marker_suffix', schedule)
        self.assertNotIn('on_success', schedule)
        self.assertNotIn('move_directory', schedule)

        # The linked job must not be exported as a standalone scheduler job -
        # it always travels as part of its connection.
        job_name = 'sftp.{}.invoices.hourly'.format(ModuleCtx.Conn_Name)

        for item in exported_data.get('scheduler', []):
            self.assertNotEqual(item['name'], job_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.cli.enmasse.importers.ftp import FTPImporter
from zato.common.test.ftp_ import FTPTestServer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, stranydict
    any_, dictlist, stranydict = any_, dictlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_FTP'
    Conn_Name           = 'enmasse.ftp.1'
    Second_Conn_Name    = 'enmasse.ftp.2'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseFTPExporter(TestCase):
    """ Tests exporting FTP connection definitions to YAML-compatible dicts using enmasse,
    with the connections themselves pointing to a dynamically started FTP server.
    """

    ftp_server: 'FTPTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.ftp_server = FTPTestServer()
        class_.ftp_server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.ftp_server.stop()

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_FTP is not set')

        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Build the importers that populate the database.
        self.importer = EnmasseYAMLImporter()
        self.ftp_importer = FTPImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def get_definitions(self) -> 'dictlist':

        # The first connection speaks FTPS and also keeps the bytes of the files it moves.
        first = {
            'name': ModuleCtx.Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
            'use_ssl': True,
            'should_store_content': True,
        }

        second = {
            'name': ModuleCtx.Second_Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
        }

        out = [first, second]

        return out

# ################################################################################################################################

    def test_ftp_export(self) -> 'None':
        self._setup_test_environment()

        # Build the FTP connection definitions to be imported.
        ftp_list_from_yaml = self.get_definitions()

        # Import these definitions into the database to have something to export.
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context.
        created_ftp_connections, _ = self.ftp_importer.sync_definitions(ftp_list_from_yaml, self.session)

        self.assertEqual(len(created_ftp_connections), 2, 'Not all FTP connections were created.')

        # Initialize the exporter and export the data.
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('ftp', exported_data, 'Exporter did not produce a "ftp" section.')
        exported_ftp_list = exported_data['ftp']

        # Only the connections created by this test are compared.
        yaml_ftp_by_name = {}
        for item in ftp_list_from_yaml:
            yaml_ftp_by_name[item['name']] = item

        exported_ftp_by_name = {}
        for item in exported_ftp_list:
            if item['name'] in yaml_ftp_by_name:
                exported_ftp_by_name[item['name']] = item

        self.assertEqual(len(exported_ftp_by_name), len(yaml_ftp_by_name),
                         'Number of exported FTP connections does not match original YAML.')

        for name, yaml_def in yaml_ftp_by_name.items():

            self.assertIn(name, exported_ftp_by_name, f'FTP connection "{name}" from YAML not found in export.')
            exported_def = exported_ftp_by_name[name]

            # Compare all the options that were given on input - they must round trip unchanged.
            for field in ['name', 'host', 'port', 'username']:
                self.assertEqual(exported_def[field], yaml_def[field],
                                 f'Mismatch for "{field}" in FTP connection "{name}"')

            # The SSL flag is exported only when it differs from the default of off.
            if yaml_def.get('use_ssl') is True:
                self.assertIs(exported_def['use_ssl'], True,
                              f'use_ssl not exported for "{name}"')
            else:
                self.assertNotIn('use_ssl', exported_def,
                                 f'use_ssl was exported for "{name}"')

            # The content storage flag is exported only when it differs from the default of off.
            if yaml_def.get('should_store_content') is True:
                self.assertIs(exported_def['should_store_content'], True,
                              f'should_store_content not exported for "{name}"')
            else:
                self.assertNotIn('should_store_content', exported_def,
                                 f'should_store_content was exported for "{name}"')

        # The password must never appear in the exported data in plain text.
        for item in exported_ftp_list:
            self.assertNotIn('password', item, 'Password must not be exported')
            self.assertNotIn('secret', item, 'Secret must not be exported')

            for value in item.values():
                if isinstance(value, str):
                    self.assertNotIn(self.ftp_server.password, value, 'Password must not appear in exported values')

# ################################################################################################################################

    def test_ftp_schedules_export(self) -> 'None':
        """ Test that a connection's schedules round trip through import and export in their portable shape.
        """
        self._setup_test_environment()

        conn_def = {
            'name': ModuleCtx.Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
            'schedules': [
                {
                    'name': 'invoices.hourly',
                    'directory': 'incoming/invoices',
                    'service': 'demo.ping',
                    'run_every': 30,
                    'run_unit': 'minutes',
                },
            ],
        }

        # Import the connection along with its schedule ..
        _ = self.importer.get_cluster(self.session)
        created, _ = self.ftp_importer.sync_definitions([conn_def], self.session)
        self.assertEqual(len(created), 1)

        # .. and export everything back.
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        for item in exported_data['ftp']:
            if item['name'] == ModuleCtx.Conn_Name:
                exported_def = item
                break
        else:
            raise Exception(f'Definition {ModuleCtx.Conn_Name} not found in the export')

        # The schedule travels in its portable shape - what was given on input,
        # without database-specific fields or options left at their defaults.
        schedules = exported_def['schedules']
        self.assertEqual(len(schedules), 1)

        schedule = schedules[0]

        self.assertEqual(schedule['name'], 'invoices.hourly')
        self.assertEqual(schedule['directory'], 'incoming/invoices')
        self.assertEqual(schedule['service'], 'demo.ping')
        self.assertEqual(schedule['run_every'], 30)
        self.assertEqual(schedule['run_unit'], 'minutes')

        self.assertNotIn('id', schedule)
        self.assertNotIn('job_id', schedule)
        self.assertNotIn('pattern', schedule)
        self.assertNotIn('ready_how', schedule)

        # The linked job must not be exported as a standalone scheduler job -
        # it always travels as part of its connection.
        job_name = f'ftp.{ModuleCtx.Conn_Name}.invoices.hourly'

        for item in exported_data.get('scheduler', []):
            self.assertNotEqual(item['name'], job_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

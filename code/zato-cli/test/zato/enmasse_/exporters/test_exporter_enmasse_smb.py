# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.smb import SMBImporter
from zato.common.defaults import default_server_base_dir
from zato.common.test.smb_ import SMBTestServer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_SMB'
    Conn_Name = 'enmasse.smb.1'
    Second_Conn_Name = 'enmasse.smb.2'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSMBExporter(TestCase):
    """ Tests exporting SMB connection definitions to YAML-compatible dicts using enmasse,
    with the connections themselves pointing to a dynamically started SMB server.
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

        self.server_path = default_server_base_dir

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.smb_importer = SMBImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def get_definitions(self) -> 'list':

        first = {
            'name': ModuleCtx.Conn_Name,
            'host': self.smb_server.host,
            'port': self.smb_server.port,
            'username': self.smb_server.username,
            'password': self.smb_server.password,
        }

        second = {
            'name': ModuleCtx.Second_Conn_Name,
            'host': self.smb_server.host,
            'port': self.smb_server.port,
            'username': self.smb_server.username,
            'password': self.smb_server.password,
        }

        out = [first, second]

        return out

# ################################################################################################################################

    def test_smb_export(self):
        self._setup_test_environment()

        # 1. Build the SMB connection definitions to be imported
        smb_list_from_yaml = self.get_definitions()

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_smb_connections, _ = self.smb_importer.sync_definitions(smb_list_from_yaml, self.session)

        self.assertEqual(len(created_smb_connections), 2, 'Not all SMB connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('smb', exported_data, 'Exporter did not produce a "smb" section.')
        exported_smb_list = exported_data['smb']

        # 4. Compare exported data with the original definitions - note that the database may contain
        # other SMB connections too, which is why only the ones created by this test are compared.
        yaml_smb_by_name = {}
        for item in smb_list_from_yaml:
            yaml_smb_by_name[item['name']] = item

        exported_smb_by_name = {}
        for item in exported_smb_list:
            if item['name'] in yaml_smb_by_name:
                exported_smb_by_name[item['name']] = item

        self.assertEqual(len(exported_smb_by_name), len(yaml_smb_by_name),
                         'Number of exported SMB connections does not match original YAML.')

        for name, yaml_def in yaml_smb_by_name.items():

            self.assertIn(name, exported_smb_by_name, f'SMB connection "{name}" from YAML not found in export.')
            exported_def = exported_smb_by_name[name]

            # Compare all the options that were given on input - they must round trip unchanged
            for field in ['name', 'host', 'port', 'username']:
                self.assertEqual(exported_def.get(field), yaml_def.get(field),
                                 f'Mismatch for "{field}" in SMB connection "{name}"')

        # 5. The password must never appear in the exported data in plain text
        for item in exported_smb_list:
            self.assertNotIn('password', item, 'Password must not be exported')
            self.assertNotIn('secret', item, 'Secret must not be exported')

            for value in item.values():
                if isinstance(value, str):
                    self.assertNotIn(self.smb_server.password, value, 'Password must not appear in exported values')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

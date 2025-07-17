# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurity(TestCase):
    """ Tests for security definitions imported from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)

        # Parse the YAML file
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_basic_auth_creation(self):
        """ Test the creation of basic_auth security definitions.
        """
        self._setup_test_environment()

        # Filter only basic_auth security definitions
        basic_auth_defs = [item for item in self.yaml_config['security'] if item.get('type') == 'basic_auth']
        self.assertTrue(len(basic_auth_defs) > 0, 'No basic_auth definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(basic_auth_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(basic_auth_defs), 'Not all basic_auth definitions were created')

        # Verify each definition was created correctly
        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            self.assertIn(instance.username, {'enmasse.1', 'enmasse.2', 'enmasse.3'})
            self.assertIsNotNone(instance.password)

# ################################################################################################################################

    def test_bearer_token_creation(self):
        """ Test the creation of bearer_token security definitions.
        """
        self._setup_test_environment()

        # Filter only bearer_token security definitions
        bearer_token_defs = [item for item in self.yaml_config['security'] if item.get('type') == 'bearer_token']
        self.assertTrue(len(bearer_token_defs) > 0, 'No bearer_token definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(bearer_token_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(bearer_token_defs), 'Not all bearer_token definitions were created')

        # Verify each definition was created correctly
        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            self.assertTrue(instance.name.startswith('enmasse.bearer_token.'))
            self.assertIsNotNone(instance.username)
            self.assertIsNotNone(instance.password)

# ################################################################################################################################

    def test_ntlm_creation(self):
        """ Test the creation of NTLM security definitions.
        """
        self._setup_test_environment()

        # Filter only NTLM security definitions
        ntlm_defs = [item for item in self.yaml_config['security'] if item.get('type') == 'ntlm']
        self.assertTrue(len(ntlm_defs) > 0, 'No NTLM definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(ntlm_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(ntlm_defs), 'Not all NTLM definitions were created')

        # Verify each definition was created correctly
        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            self.assertEqual(instance.name, 'enmasse.ntlm.1')
            self.assertTrue('\\' in instance.username)  # Check for backslash in username

# ################################################################################################################################

    def test_apikey_creation(self):
        """ Test the creation of API key security definitions.
        """
        self._setup_test_environment()

        # Filter only API key security definitions
        apikey_defs = [item for item in self.yaml_config['security'] if item.get('type') == 'apikey']
        self.assertTrue(len(apikey_defs) > 0, 'No API key definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(apikey_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(apikey_defs), 'Not all API key definitions were created')

        # Verify each definition was created correctly
        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            self.assertIn(instance.name, {'enmasse.apikey.1', 'enmasse.apikey.2'})
            self.assertIn(instance.username, {'enmasse.1', 'enmasse.2', 'enmasse.3'})
            self.assertIsNotNone(instance.password)

# ################################################################################################################################

    def test_all_security_definitions(self):
        """ Test all security definitions from the YAML file are properly imported.
        """
        self._setup_test_environment()

        # Process all security definitions
        security_list = self.yaml_config.get('security', [])
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

        # Verify security definitions were created
        self.assertTrue(len(self.importer.sec_defs) >= 5, 'Not all security definitions were created')

        # Check each security definition type exists
        security_types = [def_info['type'] for def_info in self.importer.sec_defs.values()]
        self.assertIn('basic_auth', security_types)
        self.assertIn('bearer_token', security_types)
        self.assertIn('ntlm', security_types)
        self.assertIn('apikey', security_types)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseFromYAML(TestCase):
    """ Tests importing configurations from YAML files using enmasse.
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

    def tearDown(self) -> 'None':
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def test_import_from_yaml_file(self) -> 'None':
        """ Test importing configuration from a YAML file.
        """
        # Get a database session
        session = get_session_from_server_dir(self.server_path)

        try:
            # Parse the YAML file
            yaml_config = self.importer.from_path(self.temp_file.name)

            # Verify the YAML was parsed correctly
            self.assertIn('security', yaml_config)
            self.assertIsInstance(yaml_config['security'], list)

            # Get security definitions from the YAML
            security_list = yaml_config.get('security', [])

            # Sync definitions with the database
            created, _ = self.importer.sync_security_definitions(security_list, session)

            self.assertTrue(len(created) > 0, 'No security definitions were created')

            # Verify the definitions were stored in the in-memory representation
            for instance in created:
                self.assertIn(instance.name, self.importer.sec_defs)

        finally:
            # Clean up
            session.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

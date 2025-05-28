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
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.common.odb.model import SMTP
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSMTPFromYAML(TestCase):
    """ Tests importing SMTP connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains SMTP definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize SMTP importer
        self.smtp_importer = SMTPImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

    def test_smtp_definition_creation(self):
        """ Test creating SMTP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        smtp_defs = self.yaml_config['email_smtp']
        smtp_def = smtp_defs[0]

        # Process the SMTP definition
        instance = self.smtp_importer.create_smtp_definition(smtp_def, self.session)
        self.session.commit()

        # Verify SMTP connection was created correctly
        smtp = self.session.query(SMTP).filter_by(name='enmasse.email.smtp.1').one()
        self.assertEqual(smtp.host, 'smtp.example.com')
        self.assertEqual(smtp.port, 587)
        self.assertEqual(smtp.username, 'enmasse@example.com')
        # We don't check the password value since it can be environment-dependent
        self.assertTrue(smtp.password)

    def test_smtp_update(self):
        """ Test updating existing SMTP connection definitions.
        """
        self._setup_test_environment()

        # First, get the SMTP definition from YAML
        smtp_defs = self.yaml_config['email_smtp']
        smtp_def = smtp_defs[0]

        # Create the SMTP definition
        instance = self.smtp_importer.create_smtp_definition(smtp_def, self.session)
        self.session.commit()
        original_host = smtp_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': smtp_def['name'],
            'id': instance.id,
            'host': 'smtp-updated.example.com',  # Changed host
            'port': 465,  # Changed port
            'mode': 'ssl'  # Changed mode
        }

        # Update the SMTP definition
        updated_instance = self.smtp_importer.update_smtp_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'smtp-updated.example.com')
        self.assertEqual(updated_instance.port, 465)
        self.assertEqual(updated_instance.mode, 'ssl')

        # Make sure other fields were preserved from the original definition
        self.assertEqual(updated_instance.username, smtp_def['username'])
        # We don't test password directly since it can contain environment variables

    def test_complete_smtp_import_flow(self):
        """ Test the complete flow of importing SMTP definitions using sync_smtp_definitions.
        """
        self._setup_test_environment()

        # Get SMTP definitions from YAML
        smtp_list = self.yaml_config['email_smtp']

        # Process all SMTP definitions
        smtp_created, smtp_updated = self.smtp_importer.sync_smtp_definitions(smtp_list, self.session)

        # Update importer's SMTP definitions
        self.importer.smtp_defs = self.smtp_importer.smtp_defs

        # Verify SMTP definitions were created
        self.assertEqual(len(smtp_created), 1)
        self.assertEqual(len(smtp_updated), 0)

        # Verify the SMTP definitions dictionary was populated
        self.assertEqual(len(self.smtp_importer.smtp_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.smtp_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        smtp_created2, smtp_updated2 = self.smtp_importer.sync_smtp_definitions(smtp_list, self.session)
        self.assertEqual(len(smtp_created2), 0)
        self.assertEqual(len(smtp_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

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
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingSOAPFromYAML(TestCase):
    """ Tests importing outgoing SOAP connections from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains outgoing SOAP connections
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize security importer (needed for outgoing connections with security)
        self.security_importer = SecurityImporter(self.importer)
        self.importer.sec_defs = {} # Initialize sec_defs

        # Initialize outgoing SOAP importer
        self.outgoing_soap_importer = OutgoingSOAPImporter(self.importer)

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

        # Get the cluster instance from the database
        self.importer.cluster = self.importer.get_cluster(self.session)

        # Create security definitions first since outgoing SOAP connections may use them
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def test_outgoing_soap_creation(self):
        """ Test creating outgoing SOAP connections from YAML.
        """
        self._setup_test_environment()

        # Get outgoing SOAP definitions from YAML
        outgoing_soap_defs = self.yaml_config['outgoing_soap']

        # Process all outgoing SOAP definitions
        created, updated = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_defs, self.session)

        # Should have created all connections from the template
        self.assertEqual(len(created), 1)  # There's 1 SOAP connection in template_complex_01
        self.assertEqual(len(updated), 0)

        # Verify the outgoing SOAP connection was created correctly
        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.soap.1',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.SOAP
        ).one()

        self.assertEqual(outgoing.host, 'https://example.com')
        self.assertEqual(outgoing.url_path, '/SOAP')
        self.assertEqual(outgoing.soap_action, 'urn:microsoft-dynamics-schemas/page/example:Create')
        self.assertEqual(outgoing.soap_version, '1.1')
        self.assertEqual(outgoing.timeout, 20)
        self.assertFalse(outgoing.tls_verify)

# ################################################################################################################################

    def test_outgoing_soap_update(self):
        """ Test updating existing outgoing SOAP connections.
        """
        self._setup_test_environment()

        # First, get an outgoing SOAP definition from YAML and create it
        outgoing_soap_defs = self.yaml_config['outgoing_soap']
        outgoing_def = outgoing_soap_defs[0]  # Use the first definition

        # Create the outgoing SOAP connection
        instance = self.outgoing_soap_importer.create_outgoing_soap(outgoing_def, self.session)
        self.session.commit()
        original_host = outgoing_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': outgoing_def['name'],
            'id': instance.id,
            'host': 'https://updated-example.com',  # Changed host
            'url_path': '/updated/SOAP',  # Changed path
            'soap_action': 'urn:updated-action',  # Changed SOAP action
            'soap_version': '1.2',  # Changed SOAP version
            'timeout': 30  # Changed timeout
        }

        # Update the outgoing SOAP connection
        updated_instance = self.outgoing_soap_importer.update_outgoing_soap(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'https://updated-example.com')
        self.assertEqual(updated_instance.url_path, '/updated/SOAP')
        self.assertEqual(updated_instance.soap_action, 'urn:updated-action')
        self.assertEqual(updated_instance.soap_version, '1.2')
        self.assertEqual(updated_instance.timeout, 30)

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.connection, CONNECTION.OUTGOING)
        self.assertEqual(updated_instance.transport, URL_TYPE.SOAP)

# ################################################################################################################################

    def test_complete_outgoing_soap_import_flow(self):
        """ Test the complete flow of importing outgoing SOAP connections from a YAML file.
        """
        self._setup_test_environment()

        # Process all outgoing SOAP definitions from the YAML
        outgoing_soap_list = self.yaml_config['outgoing_soap']
        outgoing_created, outgoing_updated = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_list, self.session)

        # Update main importer's outgoing SOAP definitions
        self.importer.outgoing_soap_defs = self.outgoing_soap_importer.connection_defs

        # Verify outgoing SOAP connections were created
        count = len(outgoing_soap_list)
        self.assertEqual(len(outgoing_created), count)
        self.assertEqual(len(outgoing_updated), 0)

        # Verify the outgoing SOAP connections dictionary was populated
        self.assertEqual(len(self.outgoing_soap_importer.connection_defs), count)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.outgoing_soap_defs), count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

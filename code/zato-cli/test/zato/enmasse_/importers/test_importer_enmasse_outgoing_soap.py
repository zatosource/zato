# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from json import loads
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
from zato.common.defaults import default_server_base_dir

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
        self.server_path = default_server_base_dir

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
        self.assertEqual(len(created), 2)  # There are 2 SOAP connections in template_complex_01
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

    def test_outgoing_soap_creation_with_opaque_fields(self):
        """ Test that addressing, MTOM, client-certificate and body-credential fields
        end up in the opaque attributes of a newly created connection.
        """
        self._setup_test_environment()

        outgoing_soap_defs = self.yaml_config['outgoing_soap']
        _ = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_defs, self.session)

        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.soap.2',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.SOAP
        ).one()

        # The column-level fields first ..
        self.assertEqual(outgoing.host, 'https://registry.example.com')
        self.assertEqual(outgoing.url_path, '/iisb/services')
        self.assertEqual(outgoing.soap_action, 'urn:cdc:iisb:2014:submitSingleMessage')
        self.assertEqual(outgoing.soap_version, '1.2')
        self.assertEqual(outgoing.timeout, 30)

        # .. and the new fields carried in the opaque attributes.
        opaque = loads(outgoing.opaque1)

        self.assertTrue(opaque['use_ws_addressing'])
        self.assertTrue(opaque['use_mtom'])
        self.assertEqual(opaque['tls_client_cert'], '/opt/zato/certs/client-cert.pem')
        self.assertEqual(opaque['tls_client_key'], '/opt/zato/certs/client-key.pem')

        # Body-credential mappings are stored the way the Dashboard stores them - as a JSON string.
        body_credentials = loads(opaque['body_credentials'])
        self.assertEqual(body_credentials, [{'name': 'username'}, {'name': 'password', 'position': 2}])

# ################################################################################################################################

    def test_outgoing_soap_reimport_detects_no_changes(self):
        """ Test that importing the same YAML twice detects no changes the second time,
        including for the fields kept in the opaque attributes.
        """
        self._setup_test_environment()

        outgoing_soap_defs = self.yaml_config['outgoing_soap']

        created, updated = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_defs, self.session)
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # The second, identical import must be a no-op.
        created, updated = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_defs, self.session)
        self.assertEqual(len(created), 0)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def test_outgoing_soap_update_opaque_fields(self):
        """ Test that updates to the opaque fields persist and that untouched opaque fields survive an update.
        """
        self._setup_test_environment()

        outgoing_soap_defs = self.yaml_config['outgoing_soap']
        _ = self.outgoing_soap_importer.sync_outgoing_soap(outgoing_soap_defs, self.session)

        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.soap.2',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.SOAP
        ).one()

        # Change some of the opaque fields, leave others out of the update entirely.
        update_def = {
            'name': 'enmasse.outgoing.soap.2',
            'id': outgoing.id,
            'use_mtom': False,
            'tls_client_cert': '/opt/zato/certs/rotated-cert.pem',
            'body_credentials': [{'name': 'accessToken'}],
        }

        _ = self.outgoing_soap_importer.update_outgoing_soap(update_def, self.session)
        self.session.commit()

        self.session.expire_all()
        outgoing = self.session.query(HTTPSOAP).filter_by(id=outgoing.id).one()
        opaque = loads(outgoing.opaque1)

        # The updated fields carry their new values ..
        self.assertFalse(opaque['use_mtom'])
        self.assertEqual(opaque['tls_client_cert'], '/opt/zato/certs/rotated-cert.pem')

        body_credentials = loads(opaque['body_credentials'])
        self.assertEqual(body_credentials, [{'name': 'accessToken'}])

        # .. while the fields the update did not mention are preserved.
        self.assertTrue(opaque['use_ws_addressing'])
        self.assertEqual(opaque['tls_client_key'], '/opt/zato/certs/client-key.pem')

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

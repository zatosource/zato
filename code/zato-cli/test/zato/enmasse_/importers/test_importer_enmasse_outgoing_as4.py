# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from json import loads
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_as4 import OutgoingAS4Importer
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

class TestEnmasseOutgoingAS4FromYAML(TestCase):
    """ Tests importing outgoing AS4 connections from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains outgoing AS4 connections
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize outgoing AS4 importer
        self.outgoing_as4_importer = OutgoingAS4Importer(self.importer)

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

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Get the cluster instance from the database
        self.importer.cluster = self.importer.get_cluster(self.session)

# ################################################################################################################################

    def test_outgoing_as4_creation(self):
        """ Test creating outgoing AS4 connections from YAML.
        """
        self._setup_test_environment()

        # Get outgoing AS4 definitions from YAML
        outgoing_as4_defs = self.yaml_config['outgoing_as4']

        # Process all outgoing AS4 definitions
        created, updated = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_defs, self.session)

        # Should have created all connections from the template
        self.assertEqual(len(created), 2)  # There are 2 AS4 connections in template_complex_01
        self.assertEqual(len(updated), 0)

        # Verify the discovery-driven Peppol connection was created correctly
        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.as4.1',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.AS4
        ).one()

        self.assertEqual(outgoing.host, 'https://ap.example.com')
        self.assertEqual(outgoing.url_path, '/as4')
        self.assertEqual(outgoing.timeout, 20)

        # The AS4 fields travel in the opaque attributes
        opaque = loads(outgoing.opaque1)
        self.assertEqual(opaque['as4_profile'], 'peppol')
        self.assertEqual(opaque['as4_from_party'], 'enmasse-ap')
        self.assertEqual(opaque['as4_original_sender'], '0192:991825827')
        self.assertTrue(opaque['as4_use_discovery'])
        self.assertEqual(opaque['as4_sml_domain'], 'acc.edelivery.tech.ec.europa.eu')

        # A TLS validation toggle that is absent in YAML means TLS is validated
        self.assertTrue(opaque['validate_tls'])

# ################################################################################################################################

    def test_outgoing_as4_creation_with_static_endpoint(self):
        """ Test that a statically addressed ICS2-style connection keeps its fields in the opaque attributes.
        """
        self._setup_test_environment()

        outgoing_as4_defs = self.yaml_config['outgoing_as4']
        _ = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_defs, self.session)

        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.as4.2',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.AS4
        ).one()

        # The column-level fields first ..
        self.assertEqual(outgoing.host, 'https://customs.example.com')
        self.assertEqual(outgoing.url_path, '/domibus/services/msh')
        self.assertEqual(outgoing.timeout, 30)

        # .. and the AS4 fields carried in the opaque attributes.
        opaque = loads(outgoing.opaque1)

        self.assertFalse(opaque['validate_tls'])
        self.assertEqual(opaque['as4_profile'], 'ics2')
        self.assertEqual(opaque['as4_from_party'], 'enmasse-eori')
        self.assertEqual(opaque['as4_to_party'], 'sti-taxud')
        self.assertEqual(opaque['as4_service'], 'eu.customs.ics2')
        self.assertEqual(opaque['as4_action'], 'IE3F26')
        self.assertEqual(opaque['as4_mpc'], 'urn:fdc:ec.europa.eu:2019:mpc')

# ################################################################################################################################

    def test_outgoing_as4_reimport_detects_no_changes(self):
        """ Test that importing the same YAML twice detects no changes the second time,
        including for the AS4 fields kept in the opaque attributes.
        """
        self._setup_test_environment()

        outgoing_as4_defs = self.yaml_config['outgoing_as4']

        created, updated = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_defs, self.session)
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # The second, identical import must be a no-op.
        created, updated = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_defs, self.session)
        self.assertEqual(len(created), 0)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def test_outgoing_as4_update_opaque_fields(self):
        """ Test that updates to the AS4 fields persist and that untouched opaque fields survive an update.
        """
        self._setup_test_environment()

        outgoing_as4_defs = self.yaml_config['outgoing_as4']
        _ = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_defs, self.session)

        outgoing = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.outgoing.as4.2',
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.AS4
        ).one()

        # Change some of the AS4 fields, leave others out of the update entirely.
        update_def = {
            'name': 'enmasse.outgoing.as4.2',
            'id': outgoing.id,
            'as4_action': 'IE3F32',
            'as4_signing_key': '-----BEGIN PRIVATE KEY-----\nrotated\n-----END PRIVATE KEY-----',
        }

        _ = self.outgoing_as4_importer.update_outgoing_as4(update_def, self.session)
        self.session.commit()

        self.session.expire_all()
        outgoing = self.session.query(HTTPSOAP).filter_by(id=outgoing.id).one()
        opaque = loads(outgoing.opaque1)

        # The updated fields carry their new values ..
        self.assertEqual(opaque['as4_action'], 'IE3F32')
        self.assertEqual(opaque['as4_signing_key'], '-----BEGIN PRIVATE KEY-----\nrotated\n-----END PRIVATE KEY-----')

        # .. while the fields the update did not mention are preserved.
        self.assertEqual(opaque['as4_profile'], 'ics2')
        self.assertEqual(opaque['as4_mpc'], 'urn:fdc:ec.europa.eu:2019:mpc')

# ################################################################################################################################

    def test_outgoing_as4_update(self):
        """ Test updating existing outgoing AS4 connections.
        """
        self._setup_test_environment()

        # First, get an outgoing AS4 definition from YAML and create it
        outgoing_as4_defs = self.yaml_config['outgoing_as4']
        outgoing_def = outgoing_as4_defs[0]  # Use the first definition

        # Create the outgoing AS4 connection
        instance = self.outgoing_as4_importer.create_outgoing_as4(outgoing_def, self.session)
        self.session.commit()
        original_host = outgoing_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': outgoing_def['name'],
            'id': instance.id,
            'host': 'https://updated-ap.example.com',  # Changed host
            'url_path': '/updated/as4',  # Changed path
            'timeout': 45  # Changed timeout
        }

        # Update the outgoing AS4 connection
        updated_instance = self.outgoing_as4_importer.update_outgoing_as4(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'https://updated-ap.example.com')
        self.assertEqual(updated_instance.url_path, '/updated/as4')
        self.assertEqual(updated_instance.timeout, 45)

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.connection, CONNECTION.OUTGOING)
        self.assertEqual(updated_instance.transport, URL_TYPE.AS4)

# ################################################################################################################################

    def test_complete_outgoing_as4_import_flow(self):
        """ Test the complete flow of importing outgoing AS4 connections from a YAML file.
        """
        self._setup_test_environment()

        # Process all outgoing AS4 definitions from the YAML
        outgoing_as4_list = self.yaml_config['outgoing_as4']
        outgoing_created, outgoing_updated = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_list, self.session)

        # Update main importer's outgoing AS4 definitions
        self.importer.outgoing_as4_defs = self.outgoing_as4_importer.connection_defs

        # Verify outgoing AS4 connections were created
        count = len(outgoing_as4_list)
        self.assertEqual(len(outgoing_created), count)
        self.assertEqual(len(outgoing_updated), 0)

        # Verify the outgoing AS4 connections dictionary was populated
        self.assertEqual(len(self.outgoing_as4_importer.connection_defs), count)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.outgoing_as4_defs), count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

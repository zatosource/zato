# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.importers.as2 import AS2Importer
from zato.common.api import AS2, GENERIC
from zato.common.odb.model import GenericConn
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

class TestEnmasseOutgoingAS2FromYAML(TestCase):
    """ Tests importing outgoing AS2 connections from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains outgoing AS2 connections
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize outgoing AS2 importer
        self.as2_importer = AS2Importer(self.importer)

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

# ################################################################################################################################

    def test_outgoing_as2_creation(self):
        """ Test creating outgoing AS2 connections from YAML.
        """
        self._setup_test_environment()

        # Get outgoing AS2 definitions from YAML
        outgoing_as2_defs = self.yaml_config['outgoing_as2']

        # Process all outgoing AS2 definitions
        created, updated = self.as2_importer.sync_definitions(outgoing_as2_defs, self.session)

        # Should have created all connections from the template
        self.assertEqual(len(created), 2)  # There are 2 AS2 connections in template_complex_01
        self.assertEqual(len(updated), 0)

        # Verify the fully specified connection was created correctly
        outgoing = self.session.query(GenericConn).filter_by(
            name='enmasse.outgoing.as2.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_AS2
        ).one()

        # The column-level fields first ..
        self.assertTrue(outgoing.is_active)
        self.assertFalse(outgoing.is_channel)
        self.assertTrue(outgoing.is_outconn)
        self.assertEqual(outgoing.pool_size, AS2.Default.Pool_Size)

        # .. and the AS2 fields carried in the opaque attributes.
        opaque = loads(outgoing.opaque1)

        self.assertEqual(opaque['as2_from'], 'EnmasseRetail')
        self.assertEqual(opaque['as2_to'], 'PartnerCorp')
        self.assertEqual(opaque['endpoint_url'], 'https://as2.partnercorp.example.com/as2')
        self.assertEqual(opaque['isa_qualifier'], 'ZZ')
        self.assertEqual(opaque['isa_id'], 'PARTNERCORP')
        self.assertEqual(opaque['gs_id'], 'PARTNERCORP')
        self.assertEqual(opaque['sign_algorithm'], 'sha-256')
        self.assertEqual(opaque['encryption_algorithm'], 'aes-128-cbc')
        self.assertEqual(opaque['mdn_mode'], 'sync')
        self.assertEqual(opaque['subject'], 'Enmasse AS2 message')
        self.assertEqual(opaque['http_timeout_seconds'], 30)
        self.assertTrue(opaque['compress'])

        # A security toggle that is absent in YAML keeps the partnership's own default
        self.assertTrue(opaque['sign'])
        self.assertTrue(opaque['encrypt'])
        self.assertTrue(opaque['verify_tls'])
        self.assertTrue(opaque['is_audit_log_active'])

# ################################################################################################################################

    def test_outgoing_as2_creation_with_toggles_off(self):
        """ Test that a connection turning its security toggles off keeps them off in the opaque attributes.
        """
        self._setup_test_environment()

        outgoing_as2_defs = self.yaml_config['outgoing_as2']
        _ = self.as2_importer.sync_definitions(outgoing_as2_defs, self.session)

        outgoing = self.session.query(GenericConn).filter_by(
            name='enmasse.outgoing.as2.2',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_AS2
        ).one()

        opaque = loads(outgoing.opaque1)

        self.assertEqual(opaque['as2_from'], 'EnmasseRetail')
        self.assertEqual(opaque['as2_to'], 'LegacyPartner')
        self.assertEqual(opaque['endpoint_url'], 'http://legacy.example.com:8080/as2')
        self.assertEqual(opaque['mdn_mode'], 'none')
        self.assertEqual(opaque['content_type'], 'application/edifact')
        self.assertEqual(opaque['unb_id'], 'LEGACYPARTNER')

        # The toggles the YAML turns off are off ..
        self.assertFalse(opaque['sign'])
        self.assertFalse(opaque['encrypt'])
        self.assertFalse(opaque['verify_tls'])
        self.assertFalse(opaque['is_audit_log_active'])

        # .. while the ones it does not mention keep their defaults.
        self.assertFalse(opaque['compress'])
        self.assertTrue(opaque['mdn_signed'])

# ################################################################################################################################

    def test_outgoing_as2_update(self):
        """ Test updating existing outgoing AS2 connections.
        """
        self._setup_test_environment()

        # First, get an outgoing AS2 definition from YAML and create it
        outgoing_as2_defs = self.yaml_config['outgoing_as2']
        outgoing_def = outgoing_as2_defs[0]  # Use the first definition

        # Create the outgoing AS2 connection
        instance = self.as2_importer.create_definition(outgoing_def, self.session)
        self.session.commit()

        # Prepare an update definition based on the existing one
        update_def = {
            'name': outgoing_def['name'],
            'id': instance.id,
            'as2_from': outgoing_def['as2_from'],
            'as2_to': 'RenamedPartner',                             # Changed partner identity
            'endpoint_url': 'https://new.partnercorp.example.com/as2', # Changed endpoint
            'mdn_mode': 'async',                                    # Changed MDN mode
        }

        # Update the outgoing AS2 connection
        updated_instance = self.as2_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.session.expire_all()
        outgoing = self.session.query(GenericConn).filter_by(id=updated_instance.id).one()
        opaque = loads(outgoing.opaque1)

        self.assertEqual(opaque['as2_to'], 'RenamedPartner')
        self.assertEqual(opaque['endpoint_url'], 'https://new.partnercorp.example.com/as2')
        self.assertEqual(opaque['mdn_mode'], 'async')

        # Make sure other fields were preserved
        self.assertEqual(outgoing.type_, GENERIC.CONNECTION.TYPE.OUTCONN_AS2)

# ################################################################################################################################

    def test_complete_outgoing_as2_import_flow(self):
        """ Test the complete flow of importing outgoing AS2 connections from a YAML file.
        """
        self._setup_test_environment()

        # Process all outgoing AS2 definitions from the YAML
        outgoing_as2_list = self.yaml_config['outgoing_as2']
        as2_created, as2_updated = self.as2_importer.sync_definitions(outgoing_as2_list, self.session)

        # Update main importer's outgoing AS2 definitions
        self.importer.outgoing_as2_defs = self.as2_importer.connection_defs

        # Verify outgoing AS2 connections were created
        count = len(outgoing_as2_list)
        self.assertEqual(len(as2_created), count)
        self.assertEqual(len(as2_updated), 0)

        # Verify the outgoing AS2 connections dictionary was populated
        self.assertEqual(len(self.as2_importer.connection_defs), count)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.outgoing_as2_defs), count)

        # Try importing the same definitions again - should result in updates, not creations
        as2_created2, as2_updated2 = self.as2_importer.sync_definitions(outgoing_as2_list, self.session)
        self.assertEqual(len(as2_created2), 0)
        self.assertEqual(len(as2_updated2), count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

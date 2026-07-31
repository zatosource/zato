# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_fhir import OutgoingFHIRImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.defaults import default_server_base_dir
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# One connection with every field it can carry, one with the required fields only, and one naming
# the security definition it authenticates with.
template_outgoing_fhir = """

security:

  - name: enmasse.fhir.basic_auth.1
    type: basic_auth
    username: enmasse.fhir.1
    password: Zato_Enmasse_Env.FHIRBasicAuth1

outgoing_fhir:

  - name: enmasse.fhir.out.1
    address: http://127.0.0.1:31001/fhir/r4
    is_active: false
    pool_size: 3
    security: enmasse.fhir.basic_auth.1
    is_audit_log_active: true

  - name: enmasse.fhir.out.2
    address: http://127.0.0.1:31002/fhir/r4

  - name: enmasse.fhir.out.3
    address: http://127.0.0.1:31003/fhir/r4
    security: enmasse.fhir.basic_auth.1

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingFHIRImporter(TestCase):
    """ Tests importing outgoing HL7 FHIR connections.
    """

    def setUp(self) -> 'None':

        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_outgoing_fhir.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize the outgoing FHIR importer
        self.outgoing_fhir_importer = OutgoingFHIRImporter(self.importer)

        # A connection may name a security definition, so the definitions have to exist first
        self.security_importer = SecurityImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # A connection that names a security definition can only resolve it once the definitions exist,
        # which is the order the importer itself runs the two sections in
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def _get_connections_by_name(self, connections:'any_') -> 'stranydict':
        out = {}

        for connection in connections:
            out[connection.name] = connection

        return out

# ################################################################################################################################

    def test_outgoing_fhir_creation(self) -> 'None':
        """ Every connection the file declares is created as an outgoing FHIR connection.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']

        connection_def_count = len(connection_defs)
        self.assertEqual(connection_def_count, 3)

        created, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        created_count = len(created)
        self.assertEqual(created_count, connection_def_count)

        for connection in created:
            self.assertEqual(connection.type_, 'outconn-hl7-fhir')
            self.assertTrue(connection.is_outconn)
            self.assertFalse(connection.is_channel)

# ################################################################################################################################

    def test_outgoing_fhir_every_field_is_stored(self) -> 'None':
        """ A connection declaring every field it can carry has each of them stored,
        the columns as columns and the rest in the opaque blob.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']
        created, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        connections_by_name = self._get_connections_by_name(created)
        connection = connections_by_name['enmasse.fhir.out.1']

        self.assertEqual(connection.address, 'http://127.0.0.1:31001/fhir/r4')
        self.assertFalse(connection.is_active)
        self.assertEqual(connection.pool_size, 3)

        opaque = json.loads(connection.opaque1)
        self.assertTrue(opaque['is_audit_log_active'])

# ################################################################################################################################

    def test_outgoing_fhir_required_fields_only(self) -> 'None':
        """ A connection giving nothing but its name and address takes the defaults for the rest.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']
        created, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        connections_by_name = self._get_connections_by_name(created)
        connection = connections_by_name['enmasse.fhir.out.2']

        self.assertEqual(connection.address, 'http://127.0.0.1:31002/fhir/r4')
        self.assertTrue(connection.is_active)
        self.assertEqual(connection.pool_size, 10)

        opaque = json.loads(connection.opaque1)
        self.assertEqual(opaque['security_id'], 0)
        self.assertFalse(opaque['is_audit_log_active'])

# ################################################################################################################################

    def test_outgoing_fhir_security_name_resolves_to_id(self) -> 'None':
        """ The security definition a connection names is stored as that definition's id, and the name
        it was given by never reaches the connection's own fields.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']
        created, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        connections_by_name = self._get_connections_by_name(created)
        expected_id = self.importer.sec_defs['enmasse.fhir.basic_auth.1']['id']

        # The connection that names the definition stores its id and not its name ..
        connection = connections_by_name['enmasse.fhir.out.3']
        opaque = json.loads(connection.opaque1)
        self.assertEqual(opaque['security_id'], expected_id)
        self.assertNotIn('security', opaque)

        # .. and the one that names none sends its requests unauthenticated.
        connection = connections_by_name['enmasse.fhir.out.2']
        opaque = json.loads(connection.opaque1)
        self.assertEqual(opaque['security_id'], 0)

# ################################################################################################################################

    def test_outgoing_fhir_unknown_security_is_rejected(self) -> 'None':
        """ A connection naming a security definition that does not exist is rejected rather than
        created without one, which would leave its requests going out unauthenticated.
        """
        self._setup_test_environment()

        connection_defs = [{
            'name': 'enmasse.fhir.out.unknown.security',
            'address': 'http://127.0.0.1:31004/fhir/r4',
            'security': 'enmasse.no.such.definition',
        }]

        with self.assertRaises(Exception):
            _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

# ################################################################################################################################

    def test_outgoing_fhir_idempotent_update(self) -> 'None':
        """ Importing the same file twice updates what is already there rather than duplicating it.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']

        created, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)
        self.assertEqual(len(created), 3)

        created_again, updated = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        self.assertEqual(len(created_again), 0)
        self.assertEqual(len(updated), 3)

# ################################################################################################################################

    def test_a_file_using_an_old_key_is_refused(self) -> 'None':
        """ The MLLP keys have been renamed, so a file still using one is refused with the name
        it goes by now, rather than imported as though it declared nothing at all.
        """
        for old_key, new_key in [('channel_hl7_mllp', 'channel_mllp'), ('outgoing_hl7_mllp', 'outgoing_mllp')]:

            yaml_string = f'{old_key}:\n  - name: enmasse.hl7.old.key\n'

            with self.assertRaises(ValueError) as context:
                _ = self.importer.from_string(yaml_string)

            message = str(context.exception)
            self.assertIn(old_key, message)
            self.assertIn(new_key, message)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

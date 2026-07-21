# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    any_, anylist, stranydict = any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurity(TestCase):
    """ Tests for security definitions imported from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

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
        cleanup_enmasse(self.server_path)

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

    def test_mtls_creation(self):
        """ Test the creation of mTLS security definitions.
        """
        self._setup_test_environment()

        # Filter only mTLS security definitions
        mtls_defs = []

        for item in self.yaml_config['security']:
            if item['type'] == 'mtls':
                mtls_defs.append(item)

        self.assertTrue(len(mtls_defs) > 0, 'No mTLS definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(mtls_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(mtls_defs), 'Not all mTLS definitions were created')

        # Index the created instances by name for the per-definition checks below ..
        created_by_name = {}

        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            created_by_name[instance.name] = instance

        # .. an outgoing-oriented definition keeps its certificate material paths in opaque attributes ..
        outgoing = created_by_name['enmasse.mtls.1']
        self.assertTrue(outgoing.is_active)

        opaque = json.loads(outgoing.opaque1)
        self.assertEqual(opaque['cert_path'], '/opt/hot-deploy/ssl/enmasse-client-cert.pem')
        self.assertEqual(opaque['key_path'], '/opt/hot-deploy/ssl/enmasse-client-key.pem')
        self.assertEqual(opaque['ca_certs_path'], '/opt/hot-deploy/ssl/enmasse-remote-ca.pem')

        # .. and a channel-oriented definition keeps its match criteria in opaque attributes.
        channel = created_by_name['enmasse.mtls.2']
        self.assertTrue(channel.is_active)

        opaque = json.loads(channel.opaque1)
        self.assertEqual(opaque['client_cert_fingerprint'], '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')
        self.assertEqual(opaque['client_cert_subject_dn'], 'CN=enmasse.client,O=Enmasse,C=US')

# ################################################################################################################################

    def _get_wss_defs_from_yaml(self) -> 'anylist':
        """ Returns all the WS-Security definitions the YAML template holds.
        """

        # Our response to produce
        out = []

        for item in self.yaml_config['security']:
            if item['type'] == 'wss':
                out.append(item)

        return out

# ################################################################################################################################

    def test_wss_creation(self):
        """ Test the creation of WS-Security definitions in all their modes.
        """
        self._setup_test_environment()

        # Filter only WS-Security definitions
        wss_defs = self._get_wss_defs_from_yaml()
        self.assertTrue(len(wss_defs) > 0, 'No WS-Security definitions found in YAML')

        # Process security definitions
        sec_created, _ = self.security_importer.sync_security_definitions(wss_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(sec_created), len(wss_defs), 'Not all WS-Security definitions were created')

        # Index the created instances and the YAML items by name for the per-mode checks below ..
        created_by_name = {}
        yaml_by_name = {}

        for instance in sec_created:
            self.assertIn(instance.name, self.importer.sec_defs)
            self.assertIsNotNone(instance.password)
            created_by_name[instance.name] = instance

        for item in wss_defs:
            yaml_by_name[item['name']] = item

        # .. a UsernameToken definition keeps its mode and digest switch in opaque attributes ..
        username_token = created_by_name['enmasse.wss.1']
        self.assertEqual(username_token.username, 'enmasse.1')
        self.assertTrue(username_token.is_active)

        opaque = json.loads(username_token.opaque1)
        self.assertEqual(opaque['mode'], 'username_token')
        self.assertTrue(opaque['use_digest'])

        # .. an X.509 definition keeps its switches and all of its PEM file paths in opaque attributes ..
        x509 = created_by_name['enmasse.wss.2']
        x509_yaml = yaml_by_name['enmasse.wss.2']
        self.assertEqual(x509.username, 'enmasse.2')
        self.assertTrue(x509.is_active)

        opaque = json.loads(x509.opaque1)
        self.assertEqual(opaque['mode'], 'x509')
        self.assertTrue(opaque['sign'])
        self.assertTrue(opaque['encrypt'])

        for field in ('signing_key', 'signing_certificate_chain', 'decryption_key', 'peer_certificate', 'trust_anchors'):
            self.assertEqual(opaque[field], x509_yaml[field], f'Field {field} mismatch for enmasse.wss.2')

        # .. a SAML definition keeps its assertion fields and signing material in opaque attributes ..
        saml = created_by_name['enmasse.wss.3']
        saml_yaml = yaml_by_name['enmasse.wss.3']
        self.assertEqual(saml.username, 'enmasse.3')
        self.assertTrue(saml.is_active)

        opaque = json.loads(saml.opaque1)
        self.assertEqual(opaque['mode'], 'saml')
        self.assertEqual(opaque['issuer'], 'https://idp.example.com/enmasse')
        self.assertEqual(opaque['subject'], 'enmasse.subject.3')
        self.assertEqual(opaque['audience'], 'https://api.example.com/enmasse')
        self.assertTrue(opaque['sign'])
        self.assertEqual(opaque['signing_key'], saml_yaml['signing_key'])
        self.assertEqual(opaque['signing_certificate_chain'], saml_yaml['signing_certificate_chain'])

        # .. and a definition may be inactive with the digest switched off.
        inactive = created_by_name['enmasse.wss.4']
        self.assertEqual(inactive.username, 'enmasse.4')
        self.assertFalse(inactive.is_active)

        opaque = json.loads(inactive.opaque1)
        self.assertEqual(opaque['mode'], 'username_token')
        self.assertFalse(opaque['use_digest'])

# ################################################################################################################################

    def test_wss_opaque_update(self):
        """ Test that opaque attributes absent from an updated YAML item are preserved from the database.
        """
        self._setup_test_environment()

        # First pass creates all the WS-Security definitions
        wss_defs = self._get_wss_defs_from_yaml()
        _, _ = self.security_importer.sync_security_definitions(wss_defs, self.session)

        # Build an update for the X.509 definition that changes the username
        # and carries none of the PEM file paths the definition already holds.
        original = cast_('stranydict', None)

        for item in wss_defs:
            if item['name'] == 'enmasse.wss.2':
                original = item
                break

        self.assertIsNotNone(original, 'enmasse.wss.2 not found in YAML')

        updated_item = {
            'name': 'enmasse.wss.2',
            'type': 'wss',
            'username': 'enmasse.2.updated',
            'mode': 'x509',
        }

        # Second pass updates the definition from the trimmed-down item
        _, sec_updated = self.security_importer.sync_security_definitions([updated_item], self.session)
        self.assertEqual(len(sec_updated), 1, 'Expected exactly one updated definition')

        # The username change went through ..
        instance = sec_updated[0]
        self.assertEqual(instance.name, 'enmasse.wss.2')
        self.assertEqual(instance.username, 'enmasse.2.updated')

        # .. and the PEM file paths and switches the update did not mention are still there.
        opaque = json.loads(instance.opaque1)
        self.assertEqual(opaque['mode'], 'x509')
        self.assertTrue(opaque['sign'])
        self.assertTrue(opaque['encrypt'])

        for field in ('signing_key', 'signing_certificate_chain', 'decryption_key', 'peer_certificate', 'trust_anchors'):
            self.assertEqual(opaque[field], original[field], f'Field {field} not preserved for enmasse.wss.2')

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
        self.assertIn('mtls', security_types)
        self.assertIn('ntlm', security_types)
        self.assertIn('apikey', security_types)
        self.assertIn('wss', security_types)

    def test_security_rate_limiting(self) -> 'None':
        """ Test that rate_limiting is correctly stored in opaque1 for security definitions.
        """
        self._setup_test_environment()

        # Process all security definitions
        security_list = self.yaml_config['security']
        sec_created, _ = self.security_importer.sync_security_definitions(security_list, self.session)

        # Find enmasse.basic_auth.1 which has rate_limiting in the template
        basic_auth_1 = cast_('any_', None)

        for instance in sec_created:
            if instance.name == 'enmasse.basic_auth.1':
                basic_auth_1 = instance
                break

        self.assertIsNotNone(basic_auth_1, 'enmasse.basic_auth.1 not found')
        self.assertIsNotNone(basic_auth_1.opaque1, 'basic_auth.1 should have opaque1')

        opaque = json.loads(basic_auth_1.opaque1)
        self.assertIn('rate_limiting', opaque)

        rules = opaque['rate_limiting']
        self.assertEqual(len(rules), 1)
        self.assertIn('time_range', rules[0])

        time_range = rules[0]['time_range']
        self.assertEqual(len(time_range), 1)
        self.assertEqual(time_range[0]['limit'], 500)
        self.assertEqual(time_range[0]['limit_unit'], 'month')
        self.assertTrue(time_range[0]['is_all_day'])
        self.assertFalse(time_range[0]['disabled'])
        self.assertFalse(time_range[0]['disallowed'])

# ################################################################################################################################

    def test_security_rate_limiting_update(self) -> 'None':
        """ Test that rate_limiting is preserved during security definition update.
        """
        self._setup_test_environment()

        # Process all security definitions - first pass creates them
        security_list = self.yaml_config['security']
        _, _ = self.security_importer.sync_security_definitions(security_list, self.session)

        # Second pass - should not trigger updates since nothing changed
        _, updated = self.security_importer.sync_security_definitions(security_list, self.session)
        self.assertEqual(len(updated), 0, 'No updates expected when reimporting same data')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################

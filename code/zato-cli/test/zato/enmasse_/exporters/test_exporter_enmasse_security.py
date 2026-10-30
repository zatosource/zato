# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import tempfile
from json import dumps, loads
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.api import MTLS
from zato.common.odb.model import MTLSSecurity
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurityExporter(TestCase):
    """ Tests exporting security definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
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

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_security_export(self):
        self._setup_test_environment()

        # 1. Get security definitions from the YAML template
        security_list_from_yaml = self.yaml_config.get('security', [])

        # 2. Import these definitions into the database to have something to export
        created_security, _ = self.security_importer.sync_security_definitions(security_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_security) > 0, 'No security definitions were created from YAML.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('security', exported_data, 'Exporter did not produce a "security" section.')
        all_exported_security_list = exported_data['security']

        # Filter exported security definitions to only include those with names starting with "enmasse"
        exported_security_list = [item for item in all_exported_security_list if item['name'].startswith('enmasse')]

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_security_list), len(security_list_from_yaml),  'Number of exported security definitions does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_security_by_name = {item['name']: item for item in security_list_from_yaml}
        exported_security_by_name = {item['name']: item for item in exported_security_list}

        for name, yaml_def in yaml_security_by_name.items():
            self.assertIn(name, exported_security_by_name,  f'Security definition "{name}" from YAML not found in export.')
            exported_def = exported_security_by_name[name]

            # Check that the type is preserved
            self.assertEqual(exported_def.get('type'), yaml_def.get('type'),  f'Security type mismatch for "{name}"')

            # Check common fields that should be exported - excludes passwords
            self.assertEqual(exported_def.get('name'), yaml_def.get('name'),  f'Security name mismatch for "{name}"')

            # Check username for all security types except apikey (apikey doesn't export username)
            if 'username' in yaml_def and yaml_def.get('type') != 'apikey':
                self.assertEqual(exported_def.get('username'), yaml_def.get('username'),  f'Username mismatch for security definition "{name}"')

            # Check type-specific fields
            if yaml_def.get('type') == 'bearer_token':
                bearer_fields = [
                    'auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format',
                    'client_auth_method', 'jwt_algorithm', 'key_id', 'scopes', 'assertion_audience', 'certificate',
                ]
                for field in bearer_fields:
                    if field in yaml_def:
                        self.assertEqual(exported_def.get(field), yaml_def.get(field), f'Field {field} mismatch for security definition "{name}"')

                # Check extra_fields if present
                if 'extra_fields' in yaml_def:
                    self.assertEqual(exported_def.get('extra_fields'), yaml_def.get('extra_fields'), f'Extra fields mismatch for security definition "{name}"')

                # The private key is import-only, the same as the password
                self.assertNotIn('private_key', exported_def, f'Private key must not be exported for "{name}"')
                self.assertNotIn('password', exported_def, f'Password must not be exported for "{name}"')

            # Check WS-Security fields - every mode-specific attribute must round-trip through opaque storage
            if yaml_def.get('type') == 'wss':
                wss_fields = [
                    'is_active', 'mode', 'use_digest', 'sign', 'encrypt', 'signing_key', 'signing_certificate_chain',
                    'decryption_key', 'peer_certificate', 'trust_anchors', 'issuer', 'subject', 'audience',
                ]

                for field in wss_fields:
                    if field in yaml_def:
                        self.assertIn(field, exported_def, f'Field {field} missing from export of "{name}"')
                        self.assertEqual(exported_def[field], yaml_def[field], f'Field {field} mismatch for security definition "{name}"')

                # Passwords are never exported
                self.assertNotIn('password', exported_def, f'Password must not be exported for "{name}"')

            # Check mTLS fields - the certificate material paths and channel match criteria
            # must round-trip through opaque storage
            if yaml_def.get('type') == 'mtls':
                mtls_fields = [
                    'is_active', 'use_for', 'cert_path', 'key_path', 'ca_certs_path', 'client_cert_fingerprint',
                    'client_cert_subject_dn',
                ]

                # The fields that the definition's use never reads are not exported at all
                not_applicable = MTLS.Not_Applicable_Fields[yaml_def['use_for']]

                for field in mtls_fields:
                    if field in not_applicable:
                        self.assertNotIn(field, exported_def, f'Field {field} does not apply to "{name}"')
                    elif field in yaml_def:
                        self.assertIn(field, exported_def, f'Field {field} missing from export of "{name}"')
                        self.assertEqual(exported_def[field], yaml_def[field], f'Field {field} mismatch for security definition "{name}"')

                # Passwords are never exported
                self.assertNotIn('password', exported_def, f'Password must not be exported for "{name}"')

                # An mTLS definition carries no username either
                self.assertNotIn('username', exported_def, f'Username must not be exported for "{name}"')

            # Check Kerberos (SPNEGO) fields - the principal and keytab details
            # must round-trip through opaque storage
            if yaml_def.get('type') == 'spnego':
                spnego_fields = [
                    'is_active', 'principal', 'keytab_path', 'target_spn', 'needs_delegation',
                ]

                for field in spnego_fields:
                    if field in yaml_def:
                        self.assertIn(field, exported_def, f'Field {field} missing from export of "{name}"')
                        self.assertEqual(exported_def[field], yaml_def[field], f'Field {field} mismatch for security definition "{name}"')

                # Passwords are never exported
                self.assertNotIn('password', exported_def, f'Password must not be exported for "{name}"')

                # An SPNEGO definition carries no username either
                self.assertNotIn('username', exported_def, f'Username must not be exported for "{name}"')

            # Check rate_limiting if present in the YAML definition
            if rate_limiting := yaml_def.get('rate_limiting'):
                self.assertIn('rate_limiting', exported_def, f'rate_limiting missing from export of "{name}"')
                self.assertEqual(exported_def['rate_limiting'], rate_limiting, f'rate_limiting mismatch for "{name}"')

# ################################################################################################################################

    def test_mtls_stored_without_use_for_exports_default(self) -> 'None':
        """ An mTLS definition stored before use_for existed is exported as used with both sides,
        together with all of its fields.
        """
        self._setup_test_environment()

        name = 'enmasse.mtls.export.stored'
        cert_path = '/opt/hot-deploy/ssl/outgoing/export-client-cert.pem'
        fingerprint = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'

        item = {
            'name': name,
            'type': 'mtls',
            'cert_path': cert_path,
            'client_cert_fingerprint': fingerprint,
        }

        _ = self.security_importer.sync_security_definitions([item], self.session)

        # The definition is made to look like one stored before use_for existed
        definition = self.session.query(MTLSSecurity).filter_by(name=name).one()
        opaque = loads(definition.opaque1)
        del opaque['use_for']
        definition.opaque1 = dumps(opaque)
        self.session.commit()

        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        exported_def = cast_('stranydict', None)

        for exported_item in exported_data['security']:
            if exported_item['name'] == name:
                exported_def = exported_item
                break

        self.assertIsNotNone(exported_def, f'{name} missing from export')
        self.assertEqual(exported_def['use_for'], 'both')
        self.assertEqual(exported_def['cert_path'], cert_path)
        self.assertEqual(exported_def['client_cert_fingerprint'], fingerprint)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

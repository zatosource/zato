# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from unittest import main, TestCase

# Make the shared test helpers importable
_enmasse_tests_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.util.secrets import decrypt_secret, is_encrypted, load_opaque
from zato.common.api import EnvVariable, OAuth as COMMON_OAUTH
from zato.common.odb.model import OAuth
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.test.private_key_jwt import Env_Var_Private_Key, generate_ec_private_key_pem, generate_rsa_private_key_pem, \
    generate_self_signed_certificate_pem, Template_Definition_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Name = 'enmasse.private.key.jwt'
    Client_ID = 'enmasse-private-key-client'
    Auth_Endpoint = 'https://auth.example.com/oauth2/token'
    Key_ID = 'enmasse-key-1'
    Scopes = 'system/Patient.read'

    # The environment variable a YAML item may point its key at, and the placeholder an unset one turns into
    Env_Var = Env_Var_Private_Key
    Env_Var_Reference = 'Zato_Enmasse_Env.' + Env_Var_Private_Key
    Missing = EnvVariable.Missing_Value_Prefix + Env_Var_Private_Key

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePrivateKeyJWT(TestCase):
    """ Tests that enmasse imports create, change, keep and encrypt the private key of bearer token definitions
    that authenticate with a signed JWT, and that the key never leaves through an export.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir
        self.session = get_session_from_server_dir(self.server_path)
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        self.key_a = generate_rsa_private_key_pem()
        self.key_b = generate_rsa_private_key_pem()

        _ = os.environ.pop(ModuleCtx.Env_Var, None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        self.session.close()
        _ = os.environ.pop(ModuleCtx.Env_Var, None)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _definition(self, private_key:'str | None', **extra:'any_') -> 'anydict':
        """ Builds one private key JWT definition, with or without a private_key key.
        """
        out:'anydict' = {
            'name': ModuleCtx.Name,
            'type': 'bearer_token',
            'username': ModuleCtx.Client_ID,
            'auth_endpoint': ModuleCtx.Auth_Endpoint,
            'client_auth_method': COMMON_OAUTH.Client_Auth_Method.Private_Key_JWT,
            'jwt_algorithm': COMMON_OAUTH.JWT_Algorithm.RS384,
            'key_id': ModuleCtx.Key_ID,
            'scopes': ModuleCtx.Scopes,
        }
        out.update(extra)

        if private_key is not None:
            out['private_key'] = private_key

        return out

# ################################################################################################################################

    def _sync(self, definition:'anydict') -> 'tuple':
        created, updated = self.importer.sync_from_yaml({'security': [definition]}, self.session)
        out = created, updated
        return out

# ################################################################################################################################

    def _get_row(self, name:'str'=ModuleCtx.Name) -> 'any_':
        self.session.expire_all()
        out = self.session.query(OAuth).filter_by(name=name).one()
        return out

# ################################################################################################################################

    def _assert_stored_key(self, row:'any_', expected:'str') -> 'None':
        """ Asserts that the row's private key is encrypted in its opaque attributes and decrypts to what is expected.
        """
        opaque = load_opaque(row.opaque1)
        stored = opaque['private_key']

        self.assertTrue(is_encrypted(stored), 'Private key is not encrypted')
        self.assertEqual(decrypt_secret(self.session, stored), expected)

# ################################################################################################################################

    def test_create_with_key(self) -> 'None':
        """ A definition created with a key stores it encrypted along with every other private key JWT field.
        """
        created, _ = self._sync(self._definition(self.key_a))
        self.assertEqual(len(created['security']), 1)

        row = self._get_row()
        self._assert_stored_key(row, self.key_a)

        opaque = load_opaque(row.opaque1)
        self.assertEqual(opaque['client_auth_method'], COMMON_OAUTH.Client_Auth_Method.Private_Key_JWT)
        self.assertEqual(opaque['jwt_algorithm'], COMMON_OAUTH.JWT_Algorithm.RS384)
        self.assertEqual(opaque['key_id'], ModuleCtx.Key_ID)
        self.assertEqual(opaque['scopes'], ModuleCtx.Scopes)
        self.assertEqual(opaque['auth_server_url'], ModuleCtx.Auth_Endpoint)

        # The password column still carries an encrypted value even though the definition never sends it
        self.assertTrue(is_encrypted(row.password))

# ################################################################################################################################

    def test_update_changes_and_keeps_key(self) -> 'None':
        """ A new key replaces the stored one, an absent or placeholder key leaves it in place,
        and a change to another field does not touch it either.
        """
        _ = self._sync(self._definition(self.key_a))

        # The identical definition is no update ..
        _, updated = self._sync(self._definition(self.key_a))
        self.assertNotIn('security', updated)

        # .. a new key is one update and the row decrypts to it ..
        _, updated = self._sync(self._definition(self.key_b))
        self.assertEqual(len(updated['security']), 1)
        self._assert_stored_key(self._get_row(), self.key_b)

        # .. no key at all is no update and B stays ..
        _, updated = self._sync(self._definition(None))
        self.assertNotIn('security', updated)
        self._assert_stored_key(self._get_row(), self.key_b)

        # .. a placeholder for an unset environment variable is no update and B stays ..
        _, updated = self._sync(self._definition(ModuleCtx.Env_Var_Reference))
        self.assertNotIn('security', updated)
        self._assert_stored_key(self._get_row(), self.key_b)

        # .. and a change to the key ID with no key given is one update that keeps B.
        _, updated = self._sync(self._definition(None, key_id='enmasse-key-2'))
        self.assertEqual(len(updated['security']), 1)

        row = self._get_row()
        self._assert_stored_key(row, self.key_b)
        self.assertEqual(load_opaque(row.opaque1)['key_id'], 'enmasse-key-2')

# ################################################################################################################################

    def test_key_from_environment_variable(self) -> 'None':
        """ A key given through an environment variable is read at import time, and the next import
        with the variable gone keeps what was stored.
        """
        os.environ[ModuleCtx.Env_Var] = self.key_a

        created, _ = self._sync(self._definition(ModuleCtx.Env_Var_Reference))
        self.assertEqual(len(created['security']), 1)
        self._assert_stored_key(self._get_row(), self.key_a)

        del os.environ[ModuleCtx.Env_Var]

        _, updated = self._sync(self._definition(ModuleCtx.Env_Var_Reference))
        self.assertNotIn('security', updated)
        self._assert_stored_key(self._get_row(), self.key_a)

# ################################################################################################################################

    def test_create_with_missing_environment_variable(self) -> 'None':
        """ A definition created while its variable is unset stores the placeholder, the same as a password does,
        so the next import with the variable set replaces it with the real key.
        """
        created, _ = self._sync(self._definition(ModuleCtx.Env_Var_Reference))
        self.assertEqual(len(created['security']), 1)
        self._assert_stored_key(self._get_row(), ModuleCtx.Missing)

        os.environ[ModuleCtx.Env_Var] = self.key_a

        _, updated = self._sync(self._definition(ModuleCtx.Env_Var_Reference))
        self.assertEqual(len(updated['security']), 1)
        self._assert_stored_key(self._get_row(), self.key_a)

# ################################################################################################################################

    def test_unparseable_key_stops_the_import(self) -> 'None':
        with self.assertRaises(ValueError) as ctx:
            _ = self._sync(self._definition('-----BEGIN PRIVATE KEY-----\nnot-a-key\n-----END PRIVATE KEY-----'))

        self.assertIn(ModuleCtx.Name, str(ctx.exception))
        self.assertIn('could not be parsed', str(ctx.exception))

# ################################################################################################################################

    def test_key_type_mismatch_stops_the_import(self) -> 'None':
        with self.assertRaises(ValueError) as ctx:
            _ = self._sync(self._definition(generate_ec_private_key_pem()))

        self.assertIn('needs an RSA private key', str(ctx.exception))

# ################################################################################################################################

    def test_certificate_mismatch_stops_the_import(self) -> 'None':
        other_certificate = generate_self_signed_certificate_pem(self.key_b)

        with self.assertRaises(ValueError) as ctx:
            _ = self._sync(self._definition(self.key_a, certificate=other_certificate))

        self.assertIn('does not match', str(ctx.exception))

# ################################################################################################################################

    def test_es384_with_certificate(self) -> 'None':
        ec_key = generate_ec_private_key_pem()
        certificate = generate_self_signed_certificate_pem(ec_key)

        definition = self._definition(ec_key, jwt_algorithm=COMMON_OAUTH.JWT_Algorithm.ES384, certificate=certificate)
        created, _ = self._sync(definition)
        self.assertEqual(len(created['security']), 1)

        row = self._get_row()
        self._assert_stored_key(row, ec_key)

        opaque = load_opaque(row.opaque1)
        self.assertEqual(opaque['jwt_algorithm'], COMMON_OAUTH.JWT_Algorithm.ES384)
        self.assertEqual(opaque['certificate'], certificate)

# ################################################################################################################################

    def test_client_secret_definition_gets_defaults(self) -> 'None':
        """ A dynamic definition that says nothing about its method reads as a client secret one.
        """
        definition = {
            'name': ModuleCtx.Name,
            'type': 'bearer_token',
            'username': ModuleCtx.Client_ID,
            'password': 'enmasse-client-secret',
            'auth_endpoint': ModuleCtx.Auth_Endpoint,
        }

        _ = self._sync(definition)
        opaque = load_opaque(self._get_row().opaque1)

        self.assertEqual(opaque['client_auth_method'], COMMON_OAUTH.Client_Auth_Method.Client_Secret)
        self.assertEqual(opaque['jwt_algorithm'], COMMON_OAUTH.Default.JWT_Algorithm)
        self.assertNotIn('private_key', opaque)

# ################################################################################################################################

    def test_export_never_carries_the_key(self) -> 'None':
        certificate = generate_self_signed_certificate_pem(self.key_a)
        _ = self._sync(self._definition(self.key_a, certificate=certificate, assertion_audience='https://tenant.auth0.com/'))

        exported = self.exporter.export_to_dict(self.session)
        items = [item for item in exported['security'] if item['name'] == ModuleCtx.Name]
        self.assertEqual(len(items), 1)

        item = items[0]
        self.assertNotIn('private_key', item)
        self.assertNotIn('password', item)

        self.assertEqual(item['client_auth_method'], COMMON_OAUTH.Client_Auth_Method.Private_Key_JWT)
        self.assertEqual(item['jwt_algorithm'], COMMON_OAUTH.JWT_Algorithm.RS384)
        self.assertEqual(item['key_id'], ModuleCtx.Key_ID)
        self.assertEqual(item['scopes'], ModuleCtx.Scopes)
        self.assertEqual(item['assertion_audience'], 'https://tenant.auth0.com/')
        self.assertEqual(item['certificate'], certificate)
        self.assertEqual(item['auth_endpoint'], ModuleCtx.Auth_Endpoint)

        for value in item.values():
            self.assertNotEqual(value, self.key_a)

# ################################################################################################################################

    def test_template_definition(self) -> 'None':
        """ The private key JWT definition of the shared template is created from its environment variable.
        """
        os.environ[ModuleCtx.Env_Var] = self.key_a

        yaml_config = self.importer.from_string(template_complex_01)
        definitions = [item for item in yaml_config['security'] if item['name'] == Template_Definition_Name]
        self.assertEqual(len(definitions), 1)

        created, _ = self.importer.sync_from_yaml({'security': definitions}, self.session)
        self.assertEqual(len(created['security']), 1)

        row = self._get_row(Template_Definition_Name)
        self._assert_stored_key(row, self.key_a)

        opaque = load_opaque(row.opaque1)
        self.assertEqual(opaque['client_auth_method'], COMMON_OAUTH.Client_Auth_Method.Private_Key_JWT)
        self.assertEqual(opaque['key_id'], 'enmasse-key-1')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

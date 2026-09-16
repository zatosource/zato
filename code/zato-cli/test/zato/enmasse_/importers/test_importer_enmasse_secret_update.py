# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time
from unittest import main, TestCase

# Make the shared test helpers importable
_enmasse_tests_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.util.secrets import Auto_Password_Prefix, decrypt_secret, get_crypto_manager, is_encrypted, \
    load_opaque
from zato.common.api import AS2, AS4, CONNECTION, EnvVariable
from zato.common.const import SECRETS
from zato.common.json_internal import dumps
from zato.common.odb.model import APIKeySecurity, ChannelAMQP, GenericConn, HTTPBasicAuth, HTTPSOAP, IMAP, NTLM, OAuth, \
    OutgoingAMQP, OutgoingOdoo, SMTP, SQLConnectionPool, WSSecurity
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The three secrets each object goes through - what it is created with, what it is rotated to, and one more for 6.2
    Password_A = 'enmasse-secret-a-1f7c2e9d'
    Password_B = 'enmasse-secret-b-8a4b6c0e'
    Password_C = 'enmasse-secret-c-3d9e1f5a'

    # What preprocess_item turns an environment variable that is not set anywhere into
    Missing = EnvVariable.Missing_Value_Prefix + 'Enmasse_Secret_Update_Not_Set_Anywhere'

    # The names that must never appear in the opaque attributes of a generic connection whose secret is in the column
    Opaque_Never_Keys = ('password', 'secret', 'api_token', 'token', 'api_key', 'client_secret', 'secret_value')

    # The name AMQP channels invoke, which every server deploys
    Service_Name = 'demo.ping'

    # The custom connector deployed for 6.7 - the short type name, its YAML key and its full connection type
    Custom_Type = 'enmassesecretvault'
    Custom_Yaml_Key = 'custom_' + Custom_Type
    Custom_Conn_Type = 'outconn-' + Custom_Type
    Custom_Module_Name = 'enmasse_secret_vault_connector.py'

    # How long the running server may take to register a connector type dropped into its pickup directory
    Deploy_Timeout = 60
    Deploy_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

# A connector class the shared environment's server hot-deploys for 6.7 - it declares one Secret field.
custom_connector_module = '''
# -*- coding: utf-8 -*-

# Zato
from zato.common.sdk import Connector, Field

class EnmasseSecretVaultConnector(Connector):
    """ A connector type used only by the enmasse secret update tests.
    """
    type = 'enmassesecretvault'

    address = Field.Text()
    vault_token = Field.Secret()

    def create_client(self) -> 'object':
        return object()

    def ping(self, client:'object') -> 'None':
        pass
'''

# ################################################################################################################################
# ################################################################################################################################

# One row per security type with a password - the type and the fields the definition needs beyond name and password
security_table = (
    ('basic_auth', HTTPBasicAuth, {'username': 'enmasse.secret.user'}),
    ('apikey', APIKeySecurity, {'header': 'X-Enmasse-Key'}),
    ('ntlm', NTLM, {'username': 'enmasse.secret.user'}),
    ('wss', WSSecurity, {'username': 'enmasse.secret.user', 'mode': 'username_token'}),
    ('bearer_token', OAuth, {'username': 'enmasse.secret.user'}),
)

# ################################################################################################################################

# One row per column-backed connection type - the YAML key, the model, the secret key and the minimal definition
column_table = (
    ('sql', SQLConnectionPool, 'password', {
        'type': 'mysql',
        'host': '127.0.0.1',
        'port': 3306,
        'db_name': 'enmasse_secret_db',
        'username': 'enmasse.secret.user',
    }),
    ('email_imap', IMAP, 'password', {
        'host': 'imap.example.com',
        'port': 993,
        'username': 'enmasse.secret@example.com',
    }),
    ('email_smtp', SMTP, 'password', {
        'host': 'smtp.example.com',
        'port': 587,
        'username': 'enmasse.secret@example.com',
    }),
    ('odoo', OutgoingOdoo, 'password', {
        'host': 'odoo.example.com',
        'port': 8069,
        'user': 'enmasse.secret.user',
        'database': 'enmasse_secret_db',
    }),
    ('channel_amqp', ChannelAMQP, 'password', {
        'address': '127.0.0.1:5672',
        'queue': 'enmasse.secret.queue',
        'username': 'enmasse.secret.user',
        'service': ModuleCtx.Service_Name,
    }),
    ('outgoing_amqp', OutgoingAMQP, 'password', {
        'address': '127.0.0.1:5672',
        'username': 'enmasse.secret.user',
    }),
)

# ################################################################################################################################

# One row per generic connection type whose secret lives in the secret column - the YAML key,
# the secret key and the minimal definition
generic_table = (
    ('ldap', 'password', {'username': 'CN=enmasse', 'server_list': '127.0.0.1:389'}),
    ('ftp', 'password', {'host': '127.0.0.1', 'username': 'enmasse.secret.user'}),
    ('sftp', 'password', {'address': '127.0.0.1:22', 'username': 'enmasse.secret.user'}),
    ('smb', 'password', {'host': '127.0.0.1', 'username': 'enmasse.secret.user'}),
    ('channel_kafka', 'password', {
        'address': '127.0.0.1:9092',
        'topic': 'enmasse.secret.topic',
        'group_id': 'enmasse.secret.group',
        'service': ModuleCtx.Service_Name,
    }),
    ('outgoing_kafka', 'password', {'address': '127.0.0.1:9092', 'topic': 'enmasse.secret.topic'}),
    ('channel_ibm_mq', 'password', {'address': '127.0.0.1:1414', 'username': 'enmasse.secret.user'}),
    ('outgoing_ibm_mq', 'password', {'address': '127.0.0.1:1414', 'username': 'enmasse.secret.user'}),
    ('mongodb', 'password', {'server_list': '127.0.0.1:27017', 'username': 'enmasse.secret.user'}),
    ('elastic_search', 'password', {'address_list': 'http://127.0.0.1:9200'}),
    ('outgoing_grpc', 'password', {'address': '127.0.0.1:50051'}),
    ('outgoing_graphql', 'password', {'address': 'https://graphql.example.com'}),
    ('confluence', 'password', {'address': 'https://example.atlassian.net', 'username': 'enmasse.secret@example.com'}),
    ('jira', 'password', {'address': 'https://example.atlassian.net', 'username': 'enmasse.secret@example.com'}),
    ('odata', 'secret', {'address': 'https://odata.example.com', 'auth_type': 'basic', 'username': 'enmasse.secret.user'}),
    ('sap', 'secret', {'address': 'https://sap.example.com', 'auth_type': 'basic', 'username': 'enmasse.secret.user'}),
    ('microsoft_cloud', 'secret_value', {'client_id': 'enmasse-client-id', 'tenant_id': 'enmasse-tenant-id'}),
    ('microsoft_fabric', 'client_secret', {
        'address': 'https://api.fabric.microsoft.com/v1',
        'client_id': 'enmasse-client-id',
        'tenant_id': 'enmasse-tenant-id',
    }),
    ('microsoft_power_automate', 'client_secret', {
        'address': 'https://api.flow.microsoft.com',
        'client_id': 'enmasse-client-id',
        'tenant_id': 'enmasse-tenant-id',
        'environment_id': 'enmasse-environment-id',
    }),
    ('slack', 'token', {}),
    ('llm', 'secret', {'address': 'https://api.openai.com/v1', 'model': 'gpt-4o-mini'}),
)

# ################################################################################################################################

# A PEM-looking text standing in for a private key - what is asserted is where it lands and how, not what it is
pem_text = '-----BEGIN PRIVATE KEY-----\nenmasse-secret-update-key-material\n-----END PRIVATE KEY-----'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecretUpdate(TestCase):
    """ Tests that enmasse imports change, keep and encrypt the secrets of every object type that has one.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir
        self.session = get_session_from_server_dir(self.server_path)
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

# ################################################################################################################################

    def tearDown(self) -> 'None':
        self.session.close()
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _sync(self, yaml_config:'stranydict') -> 'tuple':
        """ Runs one full import of the configuration and hands back what it created and what it updated.
        """
        created, updated = self.importer.sync_from_yaml(yaml_config, self.session)
        out = created, updated
        return out

# ################################################################################################################################

    def _get_row(self, model:'any_', name:'str', **filters:'any_') -> 'any_':
        """ Returns the row of the given model by name, freshly loaded after the import's commit.
        """
        self.session.expire_all()
        out = self.session.query(model).filter_by(name=name, **filters).one()
        return out

# ################################################################################################################################

    def _assert_stored(self, stored:'any_', expected:'str') -> 'None':
        """ Asserts that a stored value is encrypted and decrypts to what is expected.
        """
        self.assertIsInstance(stored, str)
        self.assertTrue(is_encrypted(stored), f'Not encrypted: {stored!r}')
        self.assertEqual(decrypt_secret(self.session, stored), expected)

# ################################################################################################################################

    def _assert_no_secret_in_opaque(self, instance:'any_') -> 'None':
        """ Asserts that none of the names a secret may be given under carries a value in the opaque attributes.
        A None is a wrapper's default for a key it expects to find and is not a secret.
        """
        opaque = load_opaque(instance.opaque1)
        for key in ModuleCtx.Opaque_Never_Keys:
            if key in opaque:
                self.assertIsNone(opaque[key], f'{key} in opaque1 of {instance.name}: {opaque[key]!r}')

# ################################################################################################################################

    def _write_plaintext(self, row:'any_', column:'str', value:'str') -> 'None':
        """ Writes a value straight into a column of a row, in clear text, the way a legacy row holds it.
        """
        setattr(row, column, value)
        self.session.commit()

# ################################################################################################################################

    def _encrypt_as_server(self, value:'str') -> 'str':
        """ Encrypts a value exactly the way the server's own server.encrypt does.
        """
        crypto_manager = get_crypto_manager(self.session)
        encrypted = cast_('str', crypto_manager.encrypt(value, needs_str=True))
        out = SECRETS.PREFIX + encrypted
        return out

# ################################################################################################################################
# ################################################################################################################################

    def _security_def(self, sec_type:'str', fields:'anydict', password:'str | None', **extra:'any_') -> 'anydict':
        """ Builds one security definition of the given type, with or without a password key.
        """
        out:'anydict' = {'name': f'enmasse.secret.{sec_type}', 'type': sec_type}
        out.update(fields)
        out.update(extra)

        if password is not None:
            if sec_type == 'bearer_token':
                out['static_token'] = password
            else:
                out['password'] = password

        return out

# ################################################################################################################################

    def test_security_password_update(self) -> 'None':
        """ 6.1 - every security type with a password picks up a changed one, keeps it when the YAML gives none
        and never replaces it with an auto-generated one.
        """
        for sec_type, model, fields in security_table:
            with self.subTest(sec_type=sec_type):

                name = f'enmasse.secret.{sec_type}'

                # Created with password A ..
                created, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_A)]})
                self.assertEqual(len(created['security']), 1)
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_A)

                # .. only the password changes to B - one update, stored decrypts to B ..
                created, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_B)]})
                self.assertEqual(len(updated['security']), 1)
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                # .. the identical list is no update ..
                created, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_B)]})
                self.assertNotIn('security', updated)

                # .. no password key is no update and B stays ..
                created, updated = self._sync({'security': [self._security_def(sec_type, fields, None)]})
                self.assertNotIn('security', updated)
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                # .. another field changes and there is no password key - one update, B stays and is not auto-generated ..
                if sec_type == 'apikey':
                    changed = {'header': 'X-Enmasse-Key-Changed'}
                else:
                    changed = {'username': 'enmasse.secret.user.changed'}

                created, updated = self._sync({'security': [self._security_def(sec_type, fields, None, **changed)]})
                self.assertEqual(len(updated['security']), 1)
                stored = self._get_row(model, name).password
                self._assert_stored(stored, ModuleCtx.Password_B)
                self.assertFalse(decrypt_secret(self.session, stored).startswith(Auto_Password_Prefix))

                # .. and a placeholder for an unset environment variable is no update and B stays.
                created, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Missing, **changed)]})
                self.assertNotIn('security', updated)
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def test_security_password_written_by_server(self) -> 'None':
        """ 6.2 - a password the server encrypted is compared through decryption and replaced when it differs.
        """
        sec_type, model, fields = security_table[0]
        name = f'enmasse.secret.{sec_type}'

        _ = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_A)]})

        # The server writes B into the row ..
        row = self._get_row(model, name)
        row.password = self._encrypt_as_server(ModuleCtx.Password_B)
        self.session.commit()

        # .. a YAML with B is no update ..
        _, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_B)]})
        self.assertNotIn('security', updated)
        self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

        # .. and a YAML with C is one update, after which the row decrypts to C.
        _, updated = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_C)]})
        self.assertEqual(len(updated['security']), 1)
        self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_C)

# ################################################################################################################################
# ################################################################################################################################

    def _column_def(self, yaml_key:'str', fields:'anydict', secret_key:'str', secret:'str | None') -> 'anydict':
        """ Builds one definition of a column-backed connection type, with or without its secret key.
        """
        out:'anydict' = {'name': f'enmasse.secret.{yaml_key}'}
        out.update(fields)

        if secret is not None:
            out[secret_key] = secret

        return out

# ################################################################################################################################

    def test_column_password_update(self) -> 'None':
        """ 6.3 - SQL, IMAP, SMTP, Odoo and both AMQP kinds pick up a changed password, keep an absent one
        and ignore a placeholder.
        """
        for yaml_key, model, secret_key, fields in column_table:
            with self.subTest(yaml_key=yaml_key):

                name = f'enmasse.secret.{yaml_key}'

                # Created with A ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Password_A)]})
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_A)

                # .. a password-only change lands encrypted ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Password_B)]})
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                # .. an absent password is preserved ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, None)]})
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                # .. and so is one behind a placeholder.
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Missing)]})
                self._assert_stored(self._get_row(model, name).password, ModuleCtx.Password_B)

                cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

    def test_generic_secret_update(self) -> 'None':
        """ 6.4 - every generic connection type with a column secret picks up a changed one, keeps an absent one,
        ignores a placeholder and never carries a secret in its opaque attributes.
        """
        for yaml_key, secret_key, fields in generic_table:
            with self.subTest(yaml_key=yaml_key):

                name = f'enmasse.secret.{yaml_key}'

                # Created with A ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Password_A)]})
                row = self._get_row(GenericConn, name)
                self._assert_stored(row.secret, ModuleCtx.Password_A)
                self._assert_no_secret_in_opaque(row)

                # .. a secret-only change lands encrypted ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Password_B)]})
                row = self._get_row(GenericConn, name)
                self._assert_stored(row.secret, ModuleCtx.Password_B)
                self._assert_no_secret_in_opaque(row)

                # .. an absent secret is preserved ..
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, None)]})
                row = self._get_row(GenericConn, name)
                self._assert_stored(row.secret, ModuleCtx.Password_B)
                self._assert_no_secret_in_opaque(row)

                # .. and so is one behind a placeholder.
                _ = self._sync({yaml_key: [self._column_def(yaml_key, fields, secret_key, ModuleCtx.Missing)]})
                row = self._get_row(GenericConn, name)
                self._assert_stored(row.secret, ModuleCtx.Password_B)
                self._assert_no_secret_in_opaque(row)

                cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

    def _salesforce_def(self, password:'str | None', consumer_secret:'str | None') -> 'anydict':
        out:'anydict' = {
            'name': 'enmasse.secret.salesforce',
            'address': 'https://example.my.salesforce.com',
            'username': 'enmasse.secret@example.com',
            'consumer_key': 'enmasse-secret-consumer-key',
        }

        if password is not None:
            out['password'] = password

        if consumer_secret is not None:
            out['consumer_secret'] = consumer_secret

        return out

# ################################################################################################################################

    def test_opaque_secrets_salesforce(self) -> 'None':
        """ 6.5 - the three Salesforce secrets live encrypted in the opaque attributes and nowhere else.
        """
        name = 'enmasse.secret.salesforce'

        # Created with A for both the password and the consumer secret ..
        _ = self._sync({'salesforce': [self._salesforce_def(ModuleCtx.Password_A, ModuleCtx.Password_A)]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)

        self.assertIsNone(row.secret)
        self._assert_stored(opaque['password'], ModuleCtx.Password_A)
        self._assert_stored(opaque['consumer_key'], 'enmasse-secret-consumer-key')
        self._assert_stored(opaque['consumer_secret'], ModuleCtx.Password_A)

        # .. a change of the consumer secret alone lands ..
        _ = self._sync({'salesforce': [self._salesforce_def(ModuleCtx.Password_A, ModuleCtx.Password_B)]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)

        self.assertIsNone(row.secret)
        self._assert_stored(opaque['password'], ModuleCtx.Password_A)
        self._assert_stored(opaque['consumer_secret'], ModuleCtx.Password_B)

        # .. and absent ones are preserved.
        _ = self._sync({'salesforce': [self._salesforce_def(None, None)]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)

        self.assertIsNone(row.secret)
        self._assert_stored(opaque['password'], ModuleCtx.Password_A)
        self._assert_stored(opaque['consumer_key'], 'enmasse-secret-consumer-key')
        self._assert_stored(opaque['consumer_secret'], ModuleCtx.Password_B)

# ################################################################################################################################

    def test_opaque_secrets_odata_sap_oauth(self) -> 'None':
        """ 6.5 - the OAuth client secret of OData and SAP connections is encrypted in the opaque attributes, not in the column.
        """
        for yaml_key in ('odata', 'sap'):
            with self.subTest(yaml_key=yaml_key):

                name = f'enmasse.secret.{yaml_key}.oauth'
                definition = {
                    'name': name,
                    'address': f'https://{yaml_key}.example.com',
                    'auth_type': 'oauth',
                    'client_id': 'enmasse-secret-client-id',
                    'client_secret': ModuleCtx.Password_A,
                    'token_url': f'https://{yaml_key}.example.com/oauth/token',
                }

                _ = self._sync({yaml_key: [definition]})
                row = self._get_row(GenericConn, name)
                opaque = load_opaque(row.opaque1)

                self._assert_stored(opaque['client_secret'], ModuleCtx.Password_A)
                self.assertNotIn('password', opaque)
                self.assertNotIn('secret', opaque)

                # The column holds nothing under this name in any form
                if row.secret is not None:
                    self.assertNotEqual(decrypt_secret(self.session, row.secret), ModuleCtx.Password_A)

                cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def test_opaque_secrets_as2(self) -> 'None':
        """ 6.5 - the AS2 signing key is encrypted in the opaque attributes.
        """
        name = 'enmasse.secret.outgoing.as2'
        definition = {
            'name': name,
            'as2_from': 'EnmasseSecret',
            'as2_to': 'PartnerCorp',
            'endpoint_url': 'https://as2.example.com/as2',
            'as2_signing_key': pem_text,
        }

        _ = self._sync({'outgoing_as2': [definition]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)

        self._assert_stored(opaque['as2_signing_key'], pem_text)

        # The other secret fields keep their empty defaults, which are not secrets and are not encrypted
        for field_name in AS2.Secret_Fields:
            if field_name != 'as2_signing_key':
                self.assertEqual(opaque[field_name], '')

# ################################################################################################################################
# ################################################################################################################################

    def _as4_channel_def(self, password:'str | None', signing_key:'str | None', decryption_key:'str | None') -> 'anydict':
        out:'anydict' = {
            'name': 'enmasse.secret.channel.as4',
            'url_path': '/enmasse.secret.as4',
            'as4_profile': 'peppol',
            'as4_to_party': 'enmasse-ap',
            'as4_inbound_topic': 'enmasse.secret.as4.inbound',
        }

        if password is not None:
            out['as4_password'] = password

        if signing_key is not None:
            out['as4_signing_key'] = signing_key

        if decryption_key is not None:
            out['as4_decryption_key'] = decryption_key

        return out

# ################################################################################################################################

    def _as4_outgoing_def(self, password:'str | None', signing_key:'str | None', decryption_key:'str | None') -> 'anydict':
        out:'anydict' = {
            'name': 'enmasse.secret.outgoing.as4',
            'host': 'https://ap.example.com',
            'url_path': '/as4',
            'as4_profile': 'peppol',
            'as4_from_party': 'enmasse-ap',
        }

        if password is not None:
            out['as4_password'] = password

        if signing_key is not None:
            out['as4_signing_key'] = signing_key

        if decryption_key is not None:
            out['as4_decryption_key'] = decryption_key

        return out

# ################################################################################################################################

    def test_as4_secrets(self) -> 'None':
        """ 6.6 - the AS4 keystore secrets are encrypted in the opaque attributes, compared through decryption
        and preserved when absent.
        """
        table = (
            ('channel_as4', self._as4_channel_def, CONNECTION.CHANNEL),
            ('outgoing_as4', self._as4_outgoing_def, CONNECTION.OUTGOING),
        )

        for yaml_key, build, connection in table:
            with self.subTest(yaml_key=yaml_key):

                name = build(None, None, None)['name']

                # Created with all three secrets ..
                created, updated = self._sync({yaml_key: [build(ModuleCtx.Password_A, pem_text, pem_text)]})
                self.assertEqual(len(created[yaml_key]), 1)

                row = self._get_row(HTTPSOAP, name, connection=connection)
                opaque = load_opaque(row.opaque1)

                for field_name in AS4.Secret_Fields:
                    self.assertTrue(is_encrypted(opaque[field_name]), field_name)

                self._assert_stored(opaque['as4_password'], ModuleCtx.Password_A)
                self._assert_stored(opaque['as4_signing_key'], pem_text)
                self._assert_stored(opaque['as4_decryption_key'], pem_text)

                # .. the identical definition is no update ..
                created, updated = self._sync({yaml_key: [build(ModuleCtx.Password_A, pem_text, pem_text)]})
                self.assertNotIn(yaml_key, updated)

                # .. a password-only change is one update ..
                created, updated = self._sync({yaml_key: [build(ModuleCtx.Password_B, pem_text, pem_text)]})
                self.assertEqual(len(updated[yaml_key]), 1)

                row = self._get_row(HTTPSOAP, name, connection=connection)
                opaque = load_opaque(row.opaque1)
                self._assert_stored(opaque['as4_password'], ModuleCtx.Password_B)
                self._assert_stored(opaque['as4_signing_key'], pem_text)

                # .. and absent fields are preserved.
                created, updated = self._sync({yaml_key: [build(None, None, None)]})
                self.assertNotIn(yaml_key, updated)

                row = self._get_row(HTTPSOAP, name, connection=connection)
                opaque = load_opaque(row.opaque1)
                self._assert_stored(opaque['as4_password'], ModuleCtx.Password_B)
                self._assert_stored(opaque['as4_signing_key'], pem_text)
                self._assert_stored(opaque['as4_decryption_key'], pem_text)

                cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

    def _deploy_custom_connector(self) -> 'None':
        """ Drops the connector module into the shared server's pickup directory and waits until the type is registered.
        """
        pickup_dir = os.path.join(self.server_path, 'pickup', 'incoming', 'services')
        log_path = os.path.join(self.server_path, 'logs', 'server.log')
        marker = f'connector type `{ModuleCtx.Custom_Conn_Type}`'

        # The type is registered once per server process - a rerun in the same process finds it already there
        with open(log_path, 'r') as log_file:
            if marker in log_file.read():
                return

        with open(os.path.join(pickup_dir, ModuleCtx.Custom_Module_Name), 'w') as module_file:
            _ = module_file.write(custom_connector_module)

        deadline = time.monotonic() + ModuleCtx.Deploy_Timeout

        while time.monotonic() < deadline:
            with open(log_path, 'r') as log_file:
                if marker in log_file.read():
                    return
            time.sleep(ModuleCtx.Deploy_Poll_Interval)

        raise Exception(f'Connector type {ModuleCtx.Custom_Conn_Type} did not register within {ModuleCtx.Deploy_Timeout}s')

# ################################################################################################################################

    def test_custom_connector_secret(self) -> 'None':
        """ 6.7 - a Secret field of a connector type the server knows is encrypted in the opaque attributes
        and never exported.
        """
        self._deploy_custom_connector()

        name = 'enmasse.secret.custom'
        definition = {
            'name': name,
            'address': 'https://vault.example.com',
            'vault_token': ModuleCtx.Password_A,
        }

        # Created with A ..
        _ = self._sync({ModuleCtx.Custom_Yaml_Key: [definition]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)

        self._assert_stored(opaque['vault_token'], ModuleCtx.Password_A)
        self.assertEqual(row.address, 'https://vault.example.com')

        # .. a token-only change lands ..
        definition['vault_token'] = ModuleCtx.Password_B
        _ = self._sync({ModuleCtx.Custom_Yaml_Key: [definition]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)
        self._assert_stored(opaque['vault_token'], ModuleCtx.Password_B)

        # .. an absent token is preserved ..
        del definition['vault_token']
        _ = self._sync({ModuleCtx.Custom_Yaml_Key: [definition]})
        row = self._get_row(GenericConn, name)
        opaque = load_opaque(row.opaque1)
        self._assert_stored(opaque['vault_token'], ModuleCtx.Password_B)

        # .. and the exporter never lets it out.
        exported = self.exporter.export_to_dict(self.session)
        items = [item for item in exported[ModuleCtx.Custom_Yaml_Key] if item['name'] == name]
        self.assertEqual(len(items), 1)

        item = items[0]
        self.assertNotIn('vault_token', item)
        self.assertEqual(item['address'], 'https://vault.example.com')

        for value in item.values():
            self.assertNotEqual(value, ModuleCtx.Password_A)
            self.assertNotEqual(value, ModuleCtx.Password_B)

# ################################################################################################################################
# ################################################################################################################################

    def test_plaintext_rows_become_encrypted(self) -> 'None':
        """ 6.9 - a secret stored in clear text is encrypted in place by the next import that does not give it.
        """

        # A Basic Auth definition
        sec_type, model, fields = security_table[0]
        sec_name = f'enmasse.secret.{sec_type}'

        _ = self._sync({'security': [self._security_def(sec_type, fields, ModuleCtx.Password_A)]})
        self._write_plaintext(self._get_row(model, sec_name), 'password', ModuleCtx.Password_B)

        _, updated = self._sync({'security': [self._security_def(sec_type, fields, None)]})
        self.assertNotIn('security', updated)
        self._assert_stored(self._get_row(model, sec_name).password, ModuleCtx.Password_B)

        # An SQL connection
        yaml_key, sql_model, secret_key, sql_fields = column_table[0]
        sql_name = f'enmasse.secret.{yaml_key}'

        _ = self._sync({yaml_key: [self._column_def(yaml_key, sql_fields, secret_key, ModuleCtx.Password_A)]})
        self._write_plaintext(self._get_row(sql_model, sql_name), 'password', ModuleCtx.Password_B)

        _ = self._sync({yaml_key: [self._column_def(yaml_key, sql_fields, secret_key, None)]})
        self._assert_stored(self._get_row(sql_model, sql_name).password, ModuleCtx.Password_B)

        # An FTP connection
        ftp_key, ftp_secret_key, ftp_fields = generic_table[1]
        ftp_name = f'enmasse.secret.{ftp_key}'

        _ = self._sync({ftp_key: [self._column_def(ftp_key, ftp_fields, ftp_secret_key, ModuleCtx.Password_A)]})
        self._write_plaintext(self._get_row(GenericConn, ftp_name), 'secret', ModuleCtx.Password_B)

        _ = self._sync({ftp_key: [self._column_def(ftp_key, ftp_fields, ftp_secret_key, None)]})
        row = self._get_row(GenericConn, ftp_name)
        self._assert_stored(row.secret, ModuleCtx.Password_B)
        self._assert_no_secret_in_opaque(row)

        # A Salesforce connection - the secret is inside the opaque attributes
        sf_name = 'enmasse.secret.salesforce'

        _ = self._sync({'salesforce': [self._salesforce_def(ModuleCtx.Password_A, ModuleCtx.Password_A)]})
        row = self._get_row(GenericConn, sf_name)
        opaque = load_opaque(row.opaque1)
        opaque['consumer_secret'] = ModuleCtx.Password_B
        self._write_plaintext(row, 'opaque1', self._dump_opaque(opaque))

        _ = self._sync({'salesforce': [self._salesforce_def(None, None)]})
        row = self._get_row(GenericConn, sf_name)
        opaque = load_opaque(row.opaque1)
        self._assert_stored(opaque['consumer_secret'], ModuleCtx.Password_B)
        self._assert_stored(opaque['password'], ModuleCtx.Password_A)

        # An AS4 channel - the secrets are inside the opaque attributes too
        as4_name = 'enmasse.secret.channel.as4'

        _ = self._sync({'channel_as4': [self._as4_channel_def(ModuleCtx.Password_A, pem_text, pem_text)]})
        row = self._get_row(HTTPSOAP, as4_name, connection=CONNECTION.CHANNEL)
        opaque = load_opaque(row.opaque1)
        opaque['as4_password'] = ModuleCtx.Password_B
        self._write_plaintext(row, 'opaque1', self._dump_opaque(opaque))

        _, updated = self._sync({'channel_as4': [self._as4_channel_def(None, None, None)]})
        self.assertNotIn('channel_as4', updated)

        row = self._get_row(HTTPSOAP, as4_name, connection=CONNECTION.CHANNEL)
        opaque = load_opaque(row.opaque1)
        self._assert_stored(opaque['as4_password'], ModuleCtx.Password_B)
        self._assert_stored(opaque['as4_signing_key'], pem_text)

# ################################################################################################################################

    def _dump_opaque(self, opaque:'anydict') -> 'str':
        """ Serializes opaque attributes the way the rows store them.
        """
        out = dumps(opaque)
        return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

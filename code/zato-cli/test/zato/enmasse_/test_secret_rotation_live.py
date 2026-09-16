# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
import tempfile
from logging import basicConfig, getLogger, WARN
from unittest import main, TestCase

# The directory with the throwaway test environment helpers
_this_directory = os.path.dirname(__file__)
sys.path.insert(0, _this_directory)

# The directory with the shared MongoDB container helpers used by the live server tests
_mongodb_tests_dir = os.path.abspath(
    os.path.join(_this_directory, '..', '..', '..', '..', 'tests', 'python', 'zato-server', 'mongodb'))
sys.path.insert(0, _mongodb_tests_dir)

# The directory with the shared SQL container helpers used by the live database tests
_live_sql_dir = os.path.abspath(os.path.join(_this_directory, '..', '..', '..', '..', 'tests', 'python', 'zato-common', 'lib'))
sys.path.insert(0, _live_sql_dir)

# PyYAML
import yaml  # noqa: E402

# requests
import requests  # noqa: E402

# Zato
from env_helper import create_environment, delete_environment  # noqa: E402
from zato.cli.enmasse.client import get_server_client, get_session_from_server_dir  # noqa: E402
from zato.cli.enmasse.util.secrets import is_encrypted, Secret_Prefixes  # noqa: E402
from zato.common.api import GENERIC  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.odb.model import APIKeySecurity, GenericConn, HTTPBasicAuth, OAuth, SQLConnectionPool  # noqa: E402
from zato.common.typing_ import cast_  # noqa: E402
from zato.common.util.open_ import open_w  # noqa: E402
from zato.common.util.tcp import get_free_port  # noqa: E402
from zato.server.service.internal import Listing_Secret_Keys  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from env_helper import TestEnvironment
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist
    TestEnvironment = TestEnvironment
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The zato binary of the checkout the tests run from
_zato_base = os.path.normpath(os.path.join(_this_directory, '..', '..', '..', '..'))
_zato_bin = os.path.join(_zato_base, 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a single enmasse invocation may take, in seconds
    Enmasse_Timeout = 180

    # How long an HTTP request to the server may take, in seconds
    HTTP_Timeout = 30

    # How long a docker command changing a password inside a container may take, in seconds
    Docker_Timeout = 60

    # The environment keys that let the parts needing an external service run
    Env_Key_Live_SQL = 'Zato_Test_Live_SQL'
    Env_Key_FTP = 'Zato_Test_FTP'
    Env_Key_SFTP = 'Zato_Test_SFTP'
    Env_Key_SMB = 'Zato_Test_SMB'
    Env_Key_MongoDB = 'Zato_Test_MongoDB'

    # The two secrets every object is rotated between
    Password_A = 'enmasse-rotate-a-' + CryptoManager.generate_hex_string()
    Password_B = 'enmasse-rotate-b-' + CryptoManager.generate_hex_string()

    # The service every channel invokes, which every server deploys
    Service_Name = 'demo.ping'

    # Names of the objects the HTTP tests create
    Basic_Auth_Name = 'enmasse.rotate.basic_auth'
    Basic_Auth_Username = 'enmasse.rotate.user'
    API_Key_Name = 'enmasse.rotate.apikey'
    API_Key_Header = 'X-API-Key'
    Bearer_Name = 'enmasse.rotate.bearer'
    Group_Name = 'enmasse.rotate.group'
    Channel_Name = 'enmasse.rotate.channel'
    Channel_Path = '/enmasse/rotate/channel'
    Group_Channel_Name = 'enmasse.rotate.group.channel'
    Group_Channel_Path = '/enmasse/rotate/group/channel'

    # Names of the connections the gated tests create
    SQL_Name = 'enmasse.rotate.sql'
    FTP_Name = 'enmasse.rotate.ftp'
    SFTP_Name = 'enmasse.rotate.sftp'
    SMB_Name = 'enmasse.rotate.smb'
    MongoDB_Name = 'enmasse.rotate.mongodb'

    # The containers the gated tests start
    SQL_Container_Prefix = 'zato-enmasse-rotate-'
    SQL_Username = 'zato_rotate'
    SQL_DB_Name = 'zato_rotate'
    MongoDB_Container_Name = 'zato-enmasse-rotate-mongodb'
    MongoDB_Username = 'zato_rotate'

    # HTTP status codes
    Status_OK = 200
    Status_Unauthorized = 401

    # What a channel secured through a group answers to credentials that match no member
    Status_Forbidden = 403

    # The names of the security types that a listing must never show a secret for
    Security_List_Services = (
        'zato.security.basic-auth.get-list',
        'zato.security.apikey.get-list',
        'zato.security.oauth.get-list',
    )

    # The prefix of every object the listing test creates
    Listing_Prefix = 'enmasse.listing.'

    # The service every listing test object is bound to, where one is needed
    Listing_Service = 'demo.ping'

    # Every listing service that a definition with a password can appear in
    Listing_Services = (
        'zato.security.basic-auth.get-list',
        'zato.security.apikey.get-list',
        'zato.security.oauth.get-list',
        'zato.security.ntlm.get-list',
        'zato.security.wss.get-list',
        'zato.security.get-list',
        'zato.outgoing.sql.get-list',
        'zato.email.smtp.get-list',
        'zato.email.imap.get-list',
        'zato.outgoing.odoo.get-list',
        'zato.channel.amqp.get-list',
        'zato.outgoing.amqp.get-list',
    )

# ################################################################################################################################
# ################################################################################################################################

class EnmasseSecretRotationLiveTestCase(TestCase):
    """ Rotates secrets through enmasse imports against a throwaway environment with a running server
    and proves through HTTP and live pings that each import changes what the server actually uses.
    """

    environment: 'TestEnvironment'
    client: 'ZatoClient'

    @classmethod
    def setUpClass(class_) -> 'None':
        class_.environment = create_environment('zato-enmasse-secret-', needs_server=True)
        class_.client = get_server_client(class_.environment.server_dir)

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        delete_environment(class_.environment)

# ################################################################################################################################

    def _import(self, yaml_dict:'stranydict') -> 'None':
        """ Imports the configuration through the CLI so that the server reloads its configuration afterwards.
        """
        yaml_data = yaml.safe_dump(yaml_dict, allow_unicode=True)

        import_path = os.path.join(tempfile.gettempdir(), f'zato-enmasse-rotate-{CryptoManager.generate_hex_string()}.yaml')

        with open_w(import_path) as import_file:
            _ = import_file.write(yaml_data)

        args = [
            _zato_bin, 'enmasse', self.environment.server_dir,
            '--verbose', '--missing-wait-time', '1', '--import', '--input', import_path,
        ]

        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=ModuleCtx.Enmasse_Timeout)
        finally:
            os.remove(import_path)

        if result.returncode != 0:
            self.fail(f'enmasse failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

    def _get(self, url_path:'str', auth:'tuple | None'=None, headers:'anydict | None'=None) -> 'int':
        """ Sends a GET request to a channel of the server and returns the status code.
        """
        url = self.client.address + url_path
        response = requests.get(url, auth=auth, headers=headers, timeout=ModuleCtx.HTTP_Timeout)
        out = response.status_code
        return out

# ################################################################################################################################

    def _get_row(self, model:'any_', name:'str') -> 'any_':
        """ Returns the row of the given model by name, through a session of its own.
        """
        session = get_session_from_server_dir(self.environment.server_dir)
        try:
            out = session.query(model).filter_by(name=name).one()
            session.expunge(out)
        finally:
            session.close()

        return out

# ################################################################################################################################

    def _assert_row_encrypted(self, model:'any_', name:'str', column:'str') -> 'None':
        """ Asserts that the secret column of a row is stored encrypted.
        """
        row = self._get_row(model, name)
        value = getattr(row, column)
        self.assertIsInstance(value, str)
        self.assertTrue(is_encrypted(value), f'{name}.{column} is not encrypted: {value!r}')

# ################################################################################################################################

    def _assert_listing_hides(self, service_names:'tuple', request:'anydict', *secrets:'str') -> 'None':
        """ Asserts that none of the listing services returns any of the secrets, nor any key a secret is kept under -
        a listing carries no password in any form, encrypted or not.
        """
        for service_name in service_names:
            response = self.client.invoke(service_name, request)
            self.assertTrue(response.ok, f'{service_name} failed: {response.details}')

            text = cast_('str', response.inner_service_response)
            items = cast_('anylist', response.data)

            for secret in secrets:
                self.assertNotIn(secret, text, f'{service_name} returned a secret')

            for item in items:
                for key in Listing_Secret_Keys:
                    self.assertNotIn(key, item, f'{service_name} returned key `{key}`')

# ################################################################################################################################

    def _assert_no_secret_in(self, service_name:'str', value:'any_', passwords:'strlist') -> 'None':
        """ Walks a response recursively - dicts, lists and strings - and fails on any trace of a secret in it.
        """
        if isinstance(value, dict):
            for key, inner in value.items():
                self.assertNotIn(key, Listing_Secret_Keys, f'{service_name} returned key `{key}`')
                self._assert_no_secret_in(service_name, inner, passwords)

        elif isinstance(value, list):
            for inner in value:
                self._assert_no_secret_in(service_name, inner, passwords)

        elif isinstance(value, str):
            self.assertFalse(value.startswith(Secret_Prefixes), f'{service_name} returned an encrypted value `{value}`')
            self.assertNotIn(value, passwords, f'{service_name} returned a password in clear text')

# ################################################################################################################################

    def _assert_security_listing_hides(self, *secrets:'str') -> 'None':
        request = {'cluster_id': self.client.cluster_id}
        self._assert_listing_hides(ModuleCtx.Security_List_Services, request, *secrets)

# ################################################################################################################################

    def _assert_connection_listing_hides(self, type_:'str', *secrets:'str') -> 'None':
        request = {'cluster_id': self.client.cluster_id, 'type_': type_}
        self._assert_listing_hides(('zato.generic.connection.get-list',), request, *secrets)

# ################################################################################################################################
# ################################################################################################################################

    def _basic_auth_yaml(self, password:'str | None', is_active:'bool'=True) -> 'stranydict':
        security:'anydict' = {
            'name': ModuleCtx.Basic_Auth_Name,
            'type': 'basic_auth',
            'username': ModuleCtx.Basic_Auth_Username,
        }

        if password is not None:
            security['password'] = password

        out:'stranydict' = {
            'security': [security],
            'channel_rest': [{
                'name': ModuleCtx.Channel_Name,
                'service': ModuleCtx.Service_Name,
                'url_path': ModuleCtx.Channel_Path,
                'security': ModuleCtx.Basic_Auth_Name,
                'is_active': is_active,
            }],
        }

        return out

# ################################################################################################################################

    def test_basic_auth_rotation(self) -> 'None':
        """ 7.1 - rotating a Basic Auth password flips which credentials pass through a channel.
        """
        auth_a = (ModuleCtx.Basic_Auth_Username, ModuleCtx.Password_A)
        auth_b = (ModuleCtx.Basic_Auth_Username, ModuleCtx.Password_B)

        # With password A ..
        self._import(self._basic_auth_yaml(ModuleCtx.Password_A))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_a), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_b), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(HTTPBasicAuth, ModuleCtx.Basic_Auth_Name, 'password')

        # .. only the password changes to B ..
        self._import(self._basic_auth_yaml(ModuleCtx.Password_B))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(HTTPBasicAuth, ModuleCtx.Basic_Auth_Name, 'password')

        # .. and a YAML without the password, with the channel changed, keeps B.
        self._import(self._basic_auth_yaml(None, is_active=True))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, auth=auth_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(HTTPBasicAuth, ModuleCtx.Basic_Auth_Name, 'password')

        # 7.7 - the listing shows neither secret
        self._assert_security_listing_hides(ModuleCtx.Password_A, ModuleCtx.Password_B)

# ################################################################################################################################
# ################################################################################################################################

    def _apikey_yaml(self, password:'str | None') -> 'stranydict':
        security:'anydict' = {
            'name': ModuleCtx.API_Key_Name,
            'type': 'apikey',
            'header': ModuleCtx.API_Key_Header,
        }

        if password is not None:
            security['password'] = password

        out:'stranydict' = {
            'security': [security],
            'channel_rest': [{
                'name': ModuleCtx.Channel_Name,
                'service': ModuleCtx.Service_Name,
                'url_path': ModuleCtx.Channel_Path,
                'security': ModuleCtx.API_Key_Name,
            }],
        }

        return out

# ################################################################################################################################

    def test_apikey_rotation(self) -> 'None':
        """ 7.2 - rotating an API key flips which header value passes through a channel.
        """
        headers_a = {ModuleCtx.API_Key_Header: ModuleCtx.Password_A}
        headers_b = {ModuleCtx.API_Key_Header: ModuleCtx.Password_B}

        # With key A ..
        self._import(self._apikey_yaml(ModuleCtx.Password_A))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(APIKeySecurity, ModuleCtx.API_Key_Name, 'password')

        # .. only the key changes to B ..
        self._import(self._apikey_yaml(ModuleCtx.Password_B))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(APIKeySecurity, ModuleCtx.API_Key_Name, 'password')

        # .. and a YAML without the key keeps B.
        self._import(self._apikey_yaml(None))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(APIKeySecurity, ModuleCtx.API_Key_Name, 'password')

        self._assert_security_listing_hides(ModuleCtx.Password_A, ModuleCtx.Password_B)

# ################################################################################################################################
# ################################################################################################################################

    def _bearer_yaml(self, token:'str | None') -> 'stranydict':
        security:'anydict' = {
            'name': ModuleCtx.Bearer_Name,
            'type': 'bearer_token',
            'is_static_token': True,
        }

        if token is not None:
            security['static_token'] = token

        out:'stranydict' = {
            'security': [security],
            'channel_rest': [{
                'name': ModuleCtx.Channel_Name,
                'service': ModuleCtx.Service_Name,
                'url_path': ModuleCtx.Channel_Path,
                'security': ModuleCtx.Bearer_Name,
            }],
        }

        return out

# ################################################################################################################################

    def test_bearer_token_rotation(self) -> 'None':
        """ 7.3 - rotating a static bearer token flips which token passes through a channel.
        """
        headers_a = {'Authorization': 'Bearer ' + ModuleCtx.Password_A}
        headers_b = {'Authorization': 'Bearer ' + ModuleCtx.Password_B}

        # With token A ..
        self._import(self._bearer_yaml(ModuleCtx.Password_A))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(OAuth, ModuleCtx.Bearer_Name, 'password')

        # .. only the token changes to B ..
        self._import(self._bearer_yaml(ModuleCtx.Password_B))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(OAuth, ModuleCtx.Bearer_Name, 'password')

        # .. and a YAML without the token keeps B.
        self._import(self._bearer_yaml(None))
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Channel_Path, headers=headers_a), ModuleCtx.Status_Unauthorized)
        self._assert_row_encrypted(OAuth, ModuleCtx.Bearer_Name, 'password')

        self._assert_security_listing_hides(ModuleCtx.Password_A, ModuleCtx.Password_B)

# ################################################################################################################################
# ################################################################################################################################

    def _group_yaml(self, password:'str | None') -> 'stranydict':
        security:'anydict' = {
            'name': ModuleCtx.Basic_Auth_Name,
            'type': 'basic_auth',
            'username': ModuleCtx.Basic_Auth_Username,
        }

        if password is not None:
            security['password'] = password

        out:'stranydict' = {
            'security': [security],
            'groups': [{
                'name': ModuleCtx.Group_Name,
                'members': [ModuleCtx.Basic_Auth_Name],
            }],
            'channel_rest': [{
                'name': ModuleCtx.Group_Channel_Name,
                'service': ModuleCtx.Service_Name,
                'url_path': ModuleCtx.Group_Channel_Path,
                'groups': [ModuleCtx.Group_Name],
            }],
        }

        return out

# ################################################################################################################################

    def test_group_member_rotation(self) -> 'None':
        """ 7.4 - rotating the password of a group member flips which credentials pass through a channel secured by the group.
        """
        auth_a = (ModuleCtx.Basic_Auth_Username, ModuleCtx.Password_A)
        auth_b = (ModuleCtx.Basic_Auth_Username, ModuleCtx.Password_B)

        # With password A ..
        self._import(self._group_yaml(ModuleCtx.Password_A))
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_a), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_b), ModuleCtx.Status_Forbidden)

        # .. only the member's password changes to B ..
        self._import(self._group_yaml(ModuleCtx.Password_B))
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_a), ModuleCtx.Status_Forbidden)

        # .. and a YAML without the password keeps B.
        self._import(self._group_yaml(None))
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_b), ModuleCtx.Status_OK)
        self.assertEqual(self._get(ModuleCtx.Group_Channel_Path, auth=auth_a), ModuleCtx.Status_Forbidden)

        self._assert_row_encrypted(HTTPBasicAuth, ModuleCtx.Basic_Auth_Name, 'password')

# ################################################################################################################################
# ################################################################################################################################

    def _listing_yaml(self, passwords:'strlist') -> 'stranydict':
        """ Builds one YAML with a definition of every type whose listing could show a password,
        each with a distinct password appended to the list given.
        """
        prefix = ModuleCtx.Listing_Prefix

        def _password() -> 'str':
            out = 'enmasse-listing-' + CryptoManager.generate_hex_string()
            passwords.append(out)
            return out

        # None of these hosts exists - the ports are free ones, so nothing listens on them
        host = '127.0.0.1'
        amqp_address = f'amqp://{host}:{get_free_port()}//'

        out:'stranydict' = {
            'security': [
                {
                    'name': prefix + 'basic_auth',
                    'type': 'basic_auth',
                    'username': prefix + 'basic_auth.user',
                    'password': _password(),
                },
                {
                    'name': prefix + 'apikey',
                    'type': 'apikey',
                    'header': ModuleCtx.API_Key_Header,
                    'password': _password(),
                },
                {
                    'name': prefix + 'ntlm',
                    'type': 'ntlm',
                    'username': prefix + 'ntlm.user',
                    'password': _password(),
                },
                {
                    'name': prefix + 'wss',
                    'type': 'wss',
                    'username': prefix + 'wss.user',
                    'password': _password(),
                    'mode': 'username_token',
                    'use_digest': False,
                },
                {
                    'name': prefix + 'bearer',
                    'type': 'bearer_token',
                    'is_static_token': True,
                    'static_token': _password(),
                },
            ],
            'sql': [{
                'name': prefix + 'sql',
                'type': 'mysql',
                'host': host,
                'port': get_free_port(),
                'db_name': 'enmasse_listing',
                'username': prefix + 'sql.user',
                'password': _password(),
            }],
            'email_smtp': [{
                'name': prefix + 'smtp',
                'host': host,
                'port': get_free_port(),
                'username': prefix + 'smtp.user',
                'password': _password(),
            }],
            'email_imap': [{
                'name': prefix + 'imap',
                'host': host,
                'port': get_free_port(),
                'username': prefix + 'imap.user',
                'password': _password(),
            }],
            'odoo': [{
                'name': prefix + 'odoo',
                'host': host,
                'port': get_free_port(),
                'user': prefix + 'odoo.user',
                'password': _password(),
                'database': 'enmasse_listing',
            }],
            'channel_amqp': [{
                'name': prefix + 'channel_amqp',
                'is_active': False,
                'address': amqp_address,
                'username': prefix + 'channel_amqp.user',
                'password': _password(),
                'queue': prefix + 'queue',
                'service': ModuleCtx.Listing_Service,
            }],
            'outgoing_amqp': [{
                'name': prefix + 'outgoing_amqp',
                'is_active': False,
                'address': amqp_address,
                'username': prefix + 'outgoing_amqp.user',
                'password': _password(),
            }],
        }

        return out

# ################################################################################################################################

    def test_listings_hide_secrets(self) -> 'None':
        """ No listing service returns a password of any definition it lists, in any form.
        """
        passwords:'strlist' = []
        self._import(self._listing_yaml(passwords))

        request = {'cluster_id': self.client.cluster_id}

        for service_name in ModuleCtx.Listing_Services:
            response = self.client.invoke(service_name, request)
            self.assertTrue(response.ok, f'{service_name} failed: {response.details}')

            # Every definition the YAML created is expected in its listing, so a listing that is empty
            # is a listing that did not see the import at all
            items = cast_('anylist', response.data)
            self.assertTrue(items, f'{service_name} returned no items')

            self._assert_no_secret_in(service_name, items, passwords)

# ################################################################################################################################
# ################################################################################################################################

    def _ping_sql(self, name:'str') -> 'bool':
        """ Pings an SQL connection through the server and returns whether the ping succeeded.
        """
        row = self._get_row(SQLConnectionPool, name)
        response = self.client.invoke('zato.outgoing.sql.ping', {'id': row.id, 'should_raise_on_error': True})
        out = response.ok
        return out

# ################################################################################################################################

    def _run_in_container(self, container_name:'str', command:'strlist') -> 'None':
        """ Runs a command inside a container and fails the test if it does not succeed.
        """
        args = ['docker', 'exec', container_name] + command
        result = subprocess.run(args, capture_output=True, text=True, timeout=ModuleCtx.Docker_Timeout)

        if result.returncode != 0:
            self.fail(f'docker exec failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

    def _sql_yaml(self, details:'stranydict', password:'str | None') -> 'stranydict':
        connection:'anydict' = {
            'name': ModuleCtx.SQL_Name,
            'type': details['type'],
            'host': details['host'],
            'port': int(details['port']),
            'db_name': details['name'],
            'username': details['username'],
        }

        if password is not None:
            connection['password'] = password

        out:'stranydict' = {'sql': [connection]}
        return out

# ################################################################################################################################

    def _rotate_sql(self, details:'stranydict', change_password:'any_') -> 'None':
        """ Runs the rotation of one SQL connection - the database starts with password A,
        the password becomes B inside the database and an import with B alone makes the connection work again.
        The pool is rebuilt on every import through reload_config, so it is the stored password each ping uses,
        which is why a stale password is caught by re-importing it rather than by relying on the pool to drop.
        """
        # With A the connection works ..
        self._import(self._sql_yaml(details, ModuleCtx.Password_A))
        self.assertTrue(self._ping_sql(ModuleCtx.SQL_Name))
        self._assert_row_encrypted(SQLConnectionPool, ModuleCtx.SQL_Name, 'password')

        # .. the database changes its password to B ..
        change_password()

        # .. so a pool rebuilt from a re-imported A can no longer authenticate ..
        self._import(self._sql_yaml(details, ModuleCtx.Password_A))
        self.assertFalse(self._ping_sql(ModuleCtx.SQL_Name))

        # .. an import with B alone makes it work again ..
        self._import(self._sql_yaml(details, ModuleCtx.Password_B))
        self.assertTrue(self._ping_sql(ModuleCtx.SQL_Name))
        self._assert_row_encrypted(SQLConnectionPool, ModuleCtx.SQL_Name, 'password')

        # .. and an import without the password keeps B.
        self._import(self._sql_yaml(details, None))
        self.assertTrue(self._ping_sql(ModuleCtx.SQL_Name))
        self._assert_row_encrypted(SQLConnectionPool, ModuleCtx.SQL_Name, 'password')

# ################################################################################################################################

    def test_sql_rotation(self) -> 'None':
        """ 7.5 - an SQL connection follows the password of a live database through imports.
        """
        if not os.environ.get(ModuleCtx.Env_Key_Live_SQL):
            self.skipTest(f'Env. key {ModuleCtx.Env_Key_Live_SQL} is not set')

        # Zato
        from live_sql.containers import start_mysql, start_postgresql, stop_container

        # PostgreSQL first ..
        pg_container = ModuleCtx.SQL_Container_Prefix + 'postgresql'
        pg_server = start_postgresql(
            container_name=pg_container,
            port=get_free_port(),
            username=ModuleCtx.SQL_Username,
            password=ModuleCtx.Password_A,
            db_name=ModuleCtx.SQL_DB_Name,
            needs_ssl=False,
        )

        try:
            def _change_pg_password() -> 'None':
                sql = f"ALTER USER {ModuleCtx.SQL_Username} PASSWORD '{ModuleCtx.Password_B}'"
                self._run_in_container(pg_container, ['psql', '-U', ModuleCtx.SQL_Username, '-d', ModuleCtx.SQL_DB_Name, '-c', sql])

            self._rotate_sql(pg_server.details, _change_pg_password)
        finally:
            stop_container(pg_container)

        # .. then MySQL.
        mysql_container = ModuleCtx.SQL_Container_Prefix + 'mysql'
        mysql_server = start_mysql(
            container_name=mysql_container,
            port=get_free_port(),
            username=ModuleCtx.SQL_Username,
            password=ModuleCtx.Password_A,
            db_name=ModuleCtx.SQL_DB_Name,
            needs_ssl=False,
        )

        try:
            def _change_mysql_password() -> 'None':
                sql = f"ALTER USER '{ModuleCtx.SQL_Username}'@'%' IDENTIFIED BY '{ModuleCtx.Password_B}'"
                self._run_in_container(mysql_container, ['mysql', '-uroot', '-p' + ModuleCtx.Password_A, '-e', sql])

            self._rotate_sql(mysql_server.details, _change_mysql_password)
        finally:
            stop_container(mysql_container)

# ################################################################################################################################
# ################################################################################################################################

    def _ping_generic(self, name:'str') -> 'bool':
        """ Pings a generic connection through the server and returns whether the ping succeeded.
        """
        row = self._get_row(GenericConn, name)
        response = self.client.invoke('zato.generic.connection.ping', {'id': row.id})
        self.assertTrue(response.ok, f'Ping of {name} failed: {response.details}')
        data = cast_('anydict', response.data)
        out = data['is_success']
        return out

# ################################################################################################################################

    def _rotate_generic(
        self,
        yaml_key:'str',
        type_:'str',
        name:'str',
        build:'any_',
        change_password:'any_',
    ) -> 'None':
        """ Runs the rotation of one generic connection - the service starts with password A,
        the password becomes B on the service side and an import with B alone makes the connection work again.
        """
        # With A the connection works ..
        self._import({yaml_key: [build(ModuleCtx.Password_A)]})
        self.assertTrue(self._ping_generic(name))
        self._assert_row_encrypted(GenericConn, name, 'secret')

        # .. the service changes the password to B ..
        change_password()

        # .. an import with B alone makes the connection work ..
        self._import({yaml_key: [build(ModuleCtx.Password_B)]})
        self.assertTrue(self._ping_generic(name))
        self._assert_row_encrypted(GenericConn, name, 'secret')

        # .. and an import without the secret keeps B.
        self._import({yaml_key: [build(None)]})
        self.assertTrue(self._ping_generic(name))
        self._assert_row_encrypted(GenericConn, name, 'secret')

        # 7.7 - the listing shows neither secret
        self._assert_connection_listing_hides(type_, ModuleCtx.Password_A, ModuleCtx.Password_B)

# ################################################################################################################################

    def test_ftp_rotation(self) -> 'None':
        """ 7.6 - an FTP connection follows the password of a live FTP server through imports.
        """
        if not os.environ.get(ModuleCtx.Env_Key_FTP):
            self.skipTest(f'Env. key {ModuleCtx.Env_Key_FTP} is not set')

        # Zato
        from zato.common.test.ftp_ import FTPTestServer

        server = FTPTestServer()
        server.password = ModuleCtx.Password_A
        server.start()

        def _build(password:'str | None') -> 'anydict':
            out:'anydict' = {
                'name': ModuleCtx.FTP_Name,
                'host': server.host,
                'port': server.port,
                'username': server.username,
            }
            if password is not None:
                out['password'] = password
            return out

        def _change_password() -> 'None':
            server.password = ModuleCtx.Password_B
            server.restart()

        try:
            self._rotate_generic('ftp', GENERIC.CONNECTION.TYPE.OUTCONN_FTP, ModuleCtx.FTP_Name, _build, _change_password)
        finally:
            server.stop()

# ################################################################################################################################

    def test_sftp_rotation(self) -> 'None':
        """ 7.6 - an SFTP connection follows the passphrase of a live SFTP server's client key through imports.
        """
        if not os.environ.get(ModuleCtx.Env_Key_SFTP):
            self.skipTest(f'Env. key {ModuleCtx.Env_Key_SFTP} is not set')

        # Zato
        from zato.common.test.sftp_ import SFTPTestServer

        server = SFTPTestServer()
        server.password = ModuleCtx.Password_A
        server.start()

        def _build(password:'str | None') -> 'anydict':
            out:'anydict' = {
                'name': ModuleCtx.SFTP_Name,
                'address': f'{server.host}:{server.port}',
                'username': server.username,
                'private_key': server.client_key_encrypted_path,

                # The test server's host key is freshly generated and its port is reused across runs,
                # so every recorded key is ignored rather than checked against.
                'ignore_host_key_changes': True,
            }
            if password is not None:
                out['password'] = password
            return out

        def _change_password() -> 'None':

            # The passphrase of the encrypted client key changes, the key itself and what the server accepts do not
            command = [
                'ssh-keygen', '-p', '-P', ModuleCtx.Password_A, '-N', ModuleCtx.Password_B, '-f', server.client_key_encrypted_path,
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=ModuleCtx.Docker_Timeout)

            if result.returncode != 0:
                self.fail(f'ssh-keygen failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

        try:
            self._rotate_generic('sftp', GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, ModuleCtx.SFTP_Name, _build, _change_password)
        finally:
            server.stop()

# ################################################################################################################################

    def test_smb_rotation(self) -> 'None':
        """ 7.6 - an SMB connection follows the password of a live SMB server through imports.
        """
        if not os.environ.get(ModuleCtx.Env_Key_SMB):
            self.skipTest(f'Env. key {ModuleCtx.Env_Key_SMB} is not set')

        # Zato
        from zato.common.test.smb_ import SMBTestServer

        server = SMBTestServer()
        server.password = ModuleCtx.Password_A
        server.start()

        def _build(password:'str | None') -> 'anydict':
            out:'anydict' = {
                'name': ModuleCtx.SMB_Name,
                'host': server.host,
                'port': server.port,
                'username': server.username,
            }
            if password is not None:
                out['password'] = password
            return out

        def _change_password() -> 'None':
            server.password = ModuleCtx.Password_B
            server.restart()

        try:
            self._rotate_generic('smb', GENERIC.CONNECTION.TYPE.OUTCONN_SMB, ModuleCtx.SMB_Name, _build, _change_password)
        finally:
            server.stop()

# ################################################################################################################################

    def test_mongodb_rotation(self) -> 'None':
        """ 7.6 - a MongoDB connection follows the password of a live MongoDB server through imports.
        """
        if not os.environ.get(ModuleCtx.Env_Key_MongoDB):
            self.skipTest(f'Env. key {ModuleCtx.Env_Key_MongoDB} is not set')

        # Zato
        from containers import start_mongodb, stop_container # type: ignore[import-not-found]

        server = start_mongodb(
            container_name=ModuleCtx.MongoDB_Container_Name,
            port=get_free_port(),
            username=ModuleCtx.MongoDB_Username,
            password=ModuleCtx.Password_A,
            needs_tls=False,
        )

        def _build(password:'str | None') -> 'anydict':
            out:'anydict' = {
                'name': ModuleCtx.MongoDB_Name,
                'server_list': f'{server.host}:{server.port}',
                'username': server.username,
            }
            if password is not None:
                out['password'] = password
            return out

        def _change_password() -> 'None':
            script = f"db.getSiblingDB('admin').changeUserPassword('{server.username}', '{ModuleCtx.Password_B}')"
            command = [
                'mongosh', '--quiet',
                '-u', server.username, '-p', ModuleCtx.Password_A, '--authenticationDatabase', 'admin',
                '--eval', script,
            ]
            self._run_in_container(server.container_name, command)

        try:
            self._rotate_generic(
                'mongodb', GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB, ModuleCtx.MongoDB_Name, _build, _change_password)
        finally:
            stop_container(server.container_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

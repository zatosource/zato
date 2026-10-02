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

# PyYAML
import yaml  # noqa: E402

# Zato
from env_helper import create_environment, delete_environment  # noqa: E402
from zato.cli.enmasse.client import get_session_from_server_dir  # noqa: E402
from zato.cli.enmasse.util.secrets import decrypt_secret, is_encrypted, load_opaque  # noqa: E402
from zato.common.odb.model import OAuth  # noqa: E402
from zato.common.test import rand_string, rand_unicode  # noqa: E402
from zato.common.test.private_key_jwt import Env_Var_Private_Key, generate_rsa_private_key_pem  # noqa: E402
from zato.common.typing_ import cast_  # noqa: E402
from zato.common.util.open_ import open_w  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from env_helper import TestEnvironment
    TestEnvironment = TestEnvironment

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The zato binary of the checkout the tests run from
_zato_base = os.path.normpath(os.path.join(_this_directory, '..', '..', '..', '..'))
_zato_bin = os.path.join(_zato_base, 'bin', 'zato')

# How long a single enmasse invocation may take, in seconds
_enmasse_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

# The YAML below deploys a bearer token definition that signs its token requests with a private key
# read from an environment variable, and an outgoing REST connection that uses it.
template_private_key_jwt = """
security:
  - name: enmasse.bearer.pkjwt.{test_suffix}
    type: bearer_token
    username: enmasse-private-key-client
    auth_endpoint: https://auth.example.com/oauth2/token
    client_auth_method: private_key_jwt
    jwt_algorithm: RS384
    key_id: enmasse-key-{test_suffix}
    private_key: Zato_Enmasse_Env.""" + Env_Var_Private_Key + """
    scopes: system/Patient.read

outgoing_rest:
  - name: enmasse.bearer.pkjwt.outconn.{test_suffix}
    host: https://fhir.example.com
    url_path: /api/FHIR/R4/Patient
    security: enmasse.bearer.pkjwt.{test_suffix}
    data_format: json
"""

# ################################################################################################################################
# ################################################################################################################################

class EnmasseBearerPrivateKeyJWTTestCase(TestCase):
    """ Runs against a throwaway quickstart environment with its own embedded ODB,
    created in setUpClass and deleted in tearDownClass - no pre-existing environment is ever used.
    """

    environment: 'TestEnvironment'

    @classmethod
    def setUpClass(class_) -> 'None':
        class_.environment = create_environment('zato-enmasse-bearer-pkjwt-')

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        delete_environment(class_.environment)

# ################################################################################################################################

    def invoke_enmasse(self, config_path:'str', is_import:'bool'=True, include_type:'str'='', env:'dict | None'=None) -> 'None':
        """ Runs the enmasse CLI against the throwaway environment's server directory.
        """
        args = [_zato_bin, 'enmasse', self.environment.server_dir, '--verbose', '--missing-wait-time', '1']

        if is_import:
            args.extend(['--import', '--input', config_path])
        else:
            args.extend(['--export', '--output', config_path])
            if include_type:
                args.extend(['--include-type', include_type])

        # No server is running in the throwaway environment, so no config reload is possible
        enmasse_env = os.environ.copy()
        enmasse_env['Zato_Needs_Config_Reload'] = 'False'

        if env:
            enmasse_env.update(env)

        result = subprocess.run(args, capture_output=True, text=True, timeout=_enmasse_timeout, env=enmasse_env)

        if result.returncode != 0:
            self.fail(f'enmasse failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

        if 'error' in result.stdout:
            self.fail(f'Found an error in enmasse stdout:\n{result.stdout}')

        if 'error' in result.stderr:
            self.fail(f'Found an error in enmasse stderr:\n{result.stderr}')

# ################################################################################################################################

    def _get_stored_key(self, name:'str') -> 'str':
        """ Returns the decrypted private key the definition of the given name stores.
        """
        session = get_session_from_server_dir(self.environment.server_dir)

        try:
            row = session.query(OAuth).filter_by(name=name).one()
            opaque = load_opaque(row.opaque1)
            stored = opaque['private_key']

            self.assertTrue(is_encrypted(stored), 'Private key is not encrypted')
            out = cast_('str', decrypt_secret(session, stored))
        finally:
            session.close()

        return out

# ################################################################################################################################

    def test_private_key_jwt_round_trip(self) -> 'None':
        """ A private key JWT definition survives an import, an export and a re-import, the key is encrypted
        at rest, it never leaves through an export and a re-import with a new key rotates it.
        """
        tmp_dir = tempfile.gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_path = os.path.join(tmp_dir, f'zato-enmasse-pkjwt-import-{test_suffix}.yaml')
        export_path = os.path.join(tmp_dir, f'zato-enmasse-pkjwt-export-{test_suffix}.yaml')

        key_a = generate_rsa_private_key_pem()
        key_b = generate_rsa_private_key_pem()

        data = template_private_key_jwt.format(test_suffix=test_suffix)

        with open_w(import_path) as import_file:
            _ = import_file.write(data)

        sec_name = f'enmasse.bearer.pkjwt.{test_suffix}'
        outconn_name = f'enmasse.bearer.pkjwt.outconn.{test_suffix}'

        try:
            # Import the definitions with the key in the environment ..
            self.invoke_enmasse(import_path, env={Env_Var_Private_Key: key_a})
            self.assertEqual(self._get_stored_key(sec_name), key_a)

            # .. a second import of the same file must be a no-op, not an error ..
            self.invoke_enmasse(import_path, env={Env_Var_Private_Key: key_a})
            self.assertEqual(self._get_stored_key(sec_name), key_a)

            # .. an import without the variable keeps the stored key ..
            self.invoke_enmasse(import_path)
            self.assertEqual(self._get_stored_key(sec_name), key_a)

            # .. an import with a new key rotates it ..
            self.invoke_enmasse(import_path, env={Env_Var_Private_Key: key_b})
            self.assertEqual(self._get_stored_key(sec_name), key_b)

            # .. now export everything the test created ..
            self.invoke_enmasse(export_path, is_import=False, include_type='security,outgoing_rest')

            with open(export_path, 'r') as export_file:
                export_data = export_file.read()

            exported = yaml.safe_load(export_data)

            # .. the key is nowhere in the export ..
            self.assertNotIn(key_a, export_data)
            self.assertNotIn(key_b, export_data)

            security_by_name = {}

            for item in exported['security']:
                security_by_name[item['name']] = item

            # .. the definition keeps every field but the key ..
            sec_def = security_by_name[sec_name]
            self.assertEqual(sec_def['type'], 'bearer_token')
            self.assertEqual(sec_def['username'], 'enmasse-private-key-client')
            self.assertEqual(sec_def['auth_endpoint'], 'https://auth.example.com/oauth2/token')
            self.assertEqual(sec_def['client_auth_method'], 'private_key_jwt')
            self.assertEqual(sec_def['jwt_algorithm'], 'RS384')
            self.assertEqual(sec_def['key_id'], f'enmasse-key-{test_suffix}')
            self.assertEqual(sec_def['scopes'], 'system/Patient.read')
            self.assertNotIn('private_key', sec_def)
            self.assertNotIn('password', sec_def)

            # .. the outgoing connection keeps its definition ..
            outconns_by_name = {}

            for item in exported['outgoing_rest']:
                outconns_by_name[item['name']] = item

            outconn = outconns_by_name[outconn_name]
            self.assertEqual(outconn['security'], sec_name)

            # .. and re-importing the export must succeed and keep the stored key, proving the round trip is stable.
            self.invoke_enmasse(export_path)
            self.assertEqual(self._get_stored_key(sec_name), key_b)

        finally:
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

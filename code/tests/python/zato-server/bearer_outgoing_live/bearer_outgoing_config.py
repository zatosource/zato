# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names and helpers both the fixture and the tests use. They live under a name of their own
# rather than in conftest.py, because other suites run in the same session have a conftest.py too,
# and a plain `import conftest` returns whichever of them comes first on sys.path.

# stdlib
import os
import subprocess
import tempfile

# Zato
from zato.common.api import OAuth
from zato.common.test.private_key_jwt import generate_ec_private_key_pem, generate_rsa_private_key_pem

# Zato - test helpers
import keycloak_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir import FHIRTestServer
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

Zato_Bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# The services deployed from pickup that call outgoing connections on behalf of the tests
Call_Service_Name      = 'test.bearer.outgoing.call'
FHIR_Read_Service_Name = 'test.bearer.outgoing.fhir.read'

# The FHIR side - a fake FHIR server whose token endpoint takes client assertions, the client it knows
# and the one resource the tests read through it
FHIR_Sec_Def_Name  = 'test.bearer.outgoing.fhir'
FHIR_Outconn_Name  = 'test.bearer.outgoing.fhir.conn'
FHIR_Client_ID     = 'zato-test-fhir-client'
FHIR_Patient_ID    = 'bearer-outgoing-1'

# The definition the channel uses to verify tokens Keycloak issued to the JWT clients
Channel_Sec_Def_Name = 'test.bearer.outgoing.channel'
Channel_Path = '/test/bearer/outgoing'

# Outgoing definitions and connections, one per key family plus one whose key Keycloak does not know
RSA_Sec_Def_Name     = 'test.bearer.outgoing.rsa'
EC_Sec_Def_Name      = 'test.bearer.outgoing.ec'
Unknown_Sec_Def_Name = 'test.bearer.outgoing.unknown'

RSA_Outconn_Name     = 'test.bearer.outgoing.rsa.conn'
EC_Outconn_Name      = 'test.bearer.outgoing.ec.conn'
Unknown_Outconn_Name = 'test.bearer.outgoing.unknown.conn'

# Key IDs registered with Keycloak - the RSA client knows both of its keys from the start,
# so rotating the definition from one to the other needs no change on the Keycloak side
Key_ID_RSA_Primary = 'zato-test-rsa-key-1'
Key_ID_RSA_Rotated = 'zato-test-rsa-key-2'
Key_ID_EC          = 'zato-test-ec-key-1'
Key_ID_Unknown     = 'zato-test-unknown-key'

# Environment variables the enmasse YAML reads the private keys from
Env_RSA_Primary = 'Zato_Test_Bearer_RSA_Primary'
Env_RSA_Rotated = 'Zato_Test_Bearer_RSA_Rotated'
Env_EC          = 'Zato_Test_Bearer_EC'
Env_Unknown     = 'Zato_Test_Bearer_Unknown'

_enmasse_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

class Keys:
    """ The private keys a test run signs with, generated once per session.
    """
    def __init__(self) -> 'None':
        self.rsa_primary = generate_rsa_private_key_pem()
        self.rsa_rotated = generate_rsa_private_key_pem()
        self.ec = generate_ec_private_key_pem()
        self.unknown = generate_rsa_private_key_pem()

    def as_environ(self) -> 'strdict':
        """ Returns the keys under the names the enmasse YAML reads them from.
        """
        out = {
            Env_RSA_Primary: self.rsa_primary,
            Env_RSA_Rotated: self.rsa_rotated,
            Env_EC: self.ec,
            Env_Unknown: self.unknown,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def run_enmasse(server_directory:'str', enmasse_yaml:'str', keys:'Keys') -> 'None':
    """ Imports the given enmasse YAML into a running server, with the private keys passed through the environment
    rather than written into the YAML.
    """
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-bearer-outgoing-live-{os.getpid()}.yaml')

    enmasse_env = os.environ.copy()
    enmasse_env.update(keys.as_environ())

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [Zato_Bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout, env=enmasse_env,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################

def run_enmasse_export(server_directory:'str') -> 'str':
    """ Exports the server's configuration through enmasse and returns the YAML.
    """
    export_path = os.path.join(tempfile.gettempdir(), f'zato-bearer-outgoing-live-export-{os.getpid()}.yaml')

    try:
        result = subprocess.run(
            [Zato_Bin, 'enmasse', server_directory, '--export', '--output', export_path],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --export failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        with open(export_path) as export_file:
            out = export_file.read()

        return out

    finally:
        if os.path.isfile(export_path):
            os.unlink(export_path)

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(
    server_port:'int',
    fhir_server:'FHIRTestServer',
    rsa_env:'str'=Env_RSA_Primary,
    rsa_key_id:'str'=Key_ID_RSA_Primary,
    ) -> 'str':
    """ Returns the enmasse YAML with the channel that verifies Keycloak tokens, the private key JWT definitions,
    the outgoing connections that call the channel through them and the FHIR connection that logs in to the fake
    FHIR server with an assertion. The RSA parameters let tests redeploy the RSA definition with its rotated key.

    No two bearer token definitions share a username, which the ODB requires. The channel's definition
    verifies tokens by issuer and audience alone, so any client stands in as its username, and the definition
    with the unknown key logs in as a client of its own.
    """
    token_url = keycloak_.get_token_url()
    issuer = keycloak_.get_issuer()
    host = f'http://127.0.0.1:{server_port}'

    out = f'''\
security:
  - name: {Channel_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_Accounting}
    auth_endpoint: {token_url}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}

  - name: {RSA_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_RSA}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {rsa_key_id}
    private_key: Zato_Enmasse_Env.{rsa_env}

  - name: {EC_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_EC}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.ES384}
    key_id: {Key_ID_EC}
    private_key: Zato_Enmasse_Env.{Env_EC}

  - name: {Unknown_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_Unknown_Key}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {Key_ID_Unknown}
    private_key: Zato_Enmasse_Env.{Env_Unknown}

  - name: {FHIR_Sec_Def_Name}
    type: bearer_token
    username: {FHIR_Client_ID}
    auth_endpoint: {fhir_server.token_endpoint}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {Key_ID_RSA_Primary}
    private_key: Zato_Enmasse_Env.{Env_RSA_Primary}
    scopes: system/Patient.read

channel_rest:
  - name: test.bearer.outgoing.channel
    service: demo.ping
    url_path: {Channel_Path}
    security: {Channel_Sec_Def_Name}

outgoing_rest:
  - name: {RSA_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {RSA_Sec_Def_Name}

  - name: {EC_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {EC_Sec_Def_Name}

  - name: {Unknown_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {Unknown_Sec_Def_Name}

outgoing_fhir:
  - name: {FHIR_Outconn_Name}
    address: {fhir_server.address}
    security: {FHIR_Sec_Def_Name}
'''
    return out

# ################################################################################################################################
# ################################################################################################################################

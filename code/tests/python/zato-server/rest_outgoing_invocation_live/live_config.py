# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names, the enmasse configuration and the invocation client that the fixture and the tests of the server-level
# group share. They live under a name of their own rather than in conftest.py, because a plain `import conftest`
# returns whichever conftest.py comes first on sys.path.

# stdlib
import os
import subprocess
import tempfile
from base64 import b64encode
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

Zato_Bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# The service deployed from pickup that invokes the outgoing connections on behalf of the tests
Invoke_Service_Name = 'test.rest.outgoing.live.invoke'

# The Basic Auth side - its definition, its connection and the path template the connection invokes
Basic_Sec_Def_Name  = 'test.rest.outgoing.live.basic'
Basic_Outconn_Name  = 'test.rest.outgoing.live.basic.conn'
Basic_Username      = 'john.smith'
Basic_Path_Template = '/live/basic/customers/{customer_id}'
Basic_Password      = 'test.basic.' + CryptoManager.generate_hex_string()

# The OAuth side - its definition, its connection, the path the connection invokes and the token endpoint
OAuth_Sec_Def_Name = 'test.rest.outgoing.live.oauth'
OAuth_Outconn_Name = 'test.rest.outgoing.live.oauth.conn'
OAuth_Client_ID    = 'test.live.client'
Client_Secret      = 'test.secret.' + CryptoManager.generate_hex_string()
OAuth_Scopes       = 'orders.read'
OAuth_Path         = '/live/oauth/orders'
OAuth_Token_Path   = '/live/oauth/token'
OAuth_Token        = 'live.oauth.token.6c1e9f4a2b7d4e8f'

# How long an enmasse run may take, in seconds
_enmasse_timeout = 180

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(endpoint_base:'str', basic_password:'str', client_secret:'str') -> 'str':
    """ Returns the enmasse YAML with a Basic Auth connection and an OAuth bearer token connection, both invoking
    the test endpoint at the given address.
    """
    out = f'''\
security:
  - name: {Basic_Sec_Def_Name}
    type: basic_auth
    username: {Basic_Username}
    password: "{basic_password}"

  - name: {OAuth_Sec_Def_Name}
    type: bearer_token
    username: {OAuth_Client_ID}
    password: "{client_secret}"
    auth_endpoint: {endpoint_base}{OAuth_Token_Path}
    scopes: {OAuth_Scopes}

outgoing_rest:
  - name: {Basic_Outconn_Name}
    host: {endpoint_base}
    url_path: {Basic_Path_Template}
    security: {Basic_Sec_Def_Name}
    data_format: json

  - name: {OAuth_Outconn_Name}
    host: {endpoint_base}
    url_path: {OAuth_Path}
    security: {OAuth_Sec_Def_Name}
    data_format: json
'''
    return out

# ################################################################################################################################

def run_enmasse(server_directory:'str', enmasse_yaml:'str') -> 'None':
    """ Imports the given enmasse YAML into a running server.
    """
    yaml_path = os.path.join(tempfile.gettempdir(), f'zato-rest-outgoing-live-{os.getpid()}.yaml')

    try:
        with open(yaml_path, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [Zato_Bin, 'enmasse', server_directory, '--verbose', '--import', '--input', yaml_path],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise Exception(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(yaml_path):
            os.unlink(yaml_path)

# ################################################################################################################################
# ################################################################################################################################

class InvokeClient:
    """ Invokes services of the server through its invocation API as the admin.invoke user.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url

        credentials = f'admin.invoke:{password}'.encode('utf8')
        self.authorization = 'Basic ' + b64encode(credentials).decode('ascii')

    def invoke(self, service_name:'str', payload:'anydict') -> 'any_':
        """ Invokes a service with a JSON request and returns its JSON response.
        """
        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = dumps(payload).encode('utf8')

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', self.authorization)
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()

        except HTTPError as error:
            error_text = error.read().decode('utf8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        out = loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

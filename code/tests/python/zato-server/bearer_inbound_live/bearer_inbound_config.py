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
from zato.common.crypto.api import CryptoManager

# Zato - test helpers
import keycloak_

# ################################################################################################################################
# ################################################################################################################################

Zato_Bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# Names of the definitions and channels the tests use
Static_Sec_Def_Name = 'test.bearer.inbound.static'
JWT_Sec_Def_Name    = 'test.bearer.inbound.jwt'

Static_Channel_Path = '/test/bearer/static'
JWT_Channel_Path    = '/test/bearer/jwt'

# The exact token static-mode callers must present
Static_Token = 'test.static.' + CryptoManager.generate_hex_string()

_enmasse_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def run_enmasse(server_directory:'str', enmasse_yaml:'str') -> 'None':
    """ Imports the given enmasse YAML into a running server.
    """
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-bearer-inbound-live-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [Zato_Bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(department:'str'=keycloak_.Department_Accounting) -> 'str':
    """ Returns the enmasse YAML with both bearer token definitions and their REST channels.
    The department parameter lets tests redeploy the JWT definition with a different claim filter.
    """
    token_url = keycloak_.get_token_url()
    issuer = keycloak_.get_issuer()

    out = f'''\
security:
  - name: {Static_Sec_Def_Name}
    type: bearer_token
    static_token: "{Static_Token}"

  - name: {JWT_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_Accounting}
    password: "{keycloak_.Secret_Accounting}"
    auth_endpoint: {token_url}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}
    claims:
      - {keycloak_.Claim_Department}={department}

channel_rest:
  - name: test.bearer.inbound.static.channel
    service: demo.ping
    url_path: {Static_Channel_Path}
    security: {Static_Sec_Def_Name}

  - name: test.bearer.inbound.jwt.channel
    service: demo.ping
    url_path: {JWT_Channel_Path}
    security: {JWT_Sec_Def_Name}
'''
    return out

# ################################################################################################################################
# ################################################################################################################################

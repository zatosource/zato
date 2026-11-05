# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK

# Zato
from zato.common.crypto.api import CryptoManager

# local
from _agent import run_agent
from _client import MCPClient
from local_docker import import_enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple

# ################################################################################################################################
# ################################################################################################################################

# Where the container's server answers on the host
_base_url = 'http://127.0.0.1:17010'

# The gateway of this suite
_url_path = '/mcp/test/local-docker'

# The objects are named the same on every run
_security_name = 'test.mcp.local-docker.basic-auth'
_group_name    = 'test.mcp.local-docker.group'
_gateway_name  = 'test.mcp.local-docker.gateway'

_username = 'user.' + _security_name

# The service the gateway exposes as a tool - the quickstart environment deploys it
_greeting_service = 'demo.my-service'

# The name of the import file, on the host and inside the container
_yaml_file_prefix = 'zato-mcp-local-docker'

# How long to wait for the imported credentials to reach enforcement, in seconds
_propagation_timeout = 60

# How often to poll for it, in seconds
_propagation_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _import_gateway(password:'str') -> 'None':
    """ Imports the suite's security definition, group and gateway into the container.
    """

    yaml_text = f"""
security:
  - name: {_security_name}
    type: basic_auth
    username: {_username}
    password: "{password}"

groups:
  - name: {_group_name}
    members:
      - {_security_name}

mcp_gateway:
  - name: {_gateway_name}
    url_path: {_url_path}
    services:
      - {_greeting_service}
    security_groups:
      - {_group_name}
"""

    import_enmasse(yaml_text, _yaml_file_prefix)

# ################################################################################################################################

def _wait_until_authenticated(mcp_url:'str', auth:'anytuple') -> 'None':
    """ Polls the gateway with an initialize request until the imported credentials
    reach live enforcement and are accepted.
    """

    client = MCPClient(mcp_url, auth=auth)
    deadline = time.monotonic() + _propagation_timeout

    while True:
        response = client.jsonrpc('initialize', params={
            'protocolVersion': '2025-06-18',
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
        })

        # Stop as soon as the credentials go through ..
        if response.status_code == OK:
            return

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Credentials were not accepted within {_propagation_timeout}s, ' + \
                f'last status: {response.status_code}, body: {response.text}')

        time.sleep(_propagation_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayInvoke:
    """ One gateway with basic-auth credentials goes into the local container through enmasse
    and one Ollama conversation invokes its tool through the gateway.
    """

# ################################################################################################################################

    def test_the_model_invokes_the_gateway(self, local_container:'None') -> 'None':

        # A fresh password each run - the import updates the definition in place ..
        password = 'password.' + CryptoManager.generate_hex_string()

        _import_gateway(password)

        # .. the gateway accepts the credentials once the import reaches enforcement ..
        mcp_url = _base_url + _url_path
        auth = (_username, password)

        _wait_until_authenticated(mcp_url, auth)

        # .. one conversation asks the model to run the greeting tool ..
        client = MCPClient(mcp_url, auth=auth)
        task = 'Call the greeting tool with the name Ines and repeat the exact salutation it returned.'

        result = run_agent(client, task)

        # .. the model made at least one tool call through the gateway ..
        assert result.tool_calls, result.messages

        # .. and the tool's own salutation reached the final answer.
        assert 'Howdy' in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################

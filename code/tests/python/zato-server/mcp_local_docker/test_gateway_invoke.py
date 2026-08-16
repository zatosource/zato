# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile
import time
from http.client import OK

# Zato
from zato.common.crypto.api import CryptoManager

# local
from _agent import run_agent
from _client import MCPClient
from _local_docker import Container_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where the quickstart environment lives inside the container
_server_directory = '/opt/zato/env/qs-1/server1'
_zato_binary = '/opt/zato/current/bin/zato'

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

# Where the import file lands inside the container
_container_yaml_path = '/tmp/zato-mcp-local-docker.yaml'

# How long one docker command and one enmasse import may take, in seconds
_docker_timeout = 120

# How long to wait for the imported credentials to reach enforcement, in seconds
_propagation_timeout = 60

# How often to poll for it, in seconds
_propagation_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _run_command(command:'strlist') -> 'None':
    """ Runs one host command, raising with the full output when it fails.
    """

    result = subprocess.run(command, capture_output=True, text=True, timeout=_docker_timeout)

    if result.returncode != 0:
        raise Exception(
            f'Command failed (exit {result.returncode}): {command}\nstdout: {result.stdout}\nstderr: {result.stderr}')

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

    host_yaml_path = os.path.join(tempfile.gettempdir(), f'zato-mcp-local-docker-{os.getpid()}.yaml')

    with open(host_yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_text)

    try:
        _run_command(['docker', 'cp', host_yaml_path, f'{Container_Name}:{_container_yaml_path}'])
        _run_command(['docker', 'exec', Container_Name,
            _zato_binary, 'enmasse', _server_directory, '--verbose', '--import', '--input', _container_yaml_path])
        _run_command(['docker', 'exec', Container_Name, 'rm', _container_yaml_path])

    finally:
        os.remove(host_yaml_path)

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

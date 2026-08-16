# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import tempfile
import time

# local
import containers
from _local_docker import Container_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# Where the quickstart environment lives inside the container
_server_directory = '/opt/zato/env/qs-1/server1'
_zato_binary = '/opt/zato/current/bin/zato'

# Where hot-deployed services land inside the container
_pickup_directory = f'{_server_directory}/pickup/incoming/services'

# The objects are named the same on every run
_outconn_name = 'test.llm.local-docker'
_service_name = 'test.llm.local-docker.check'

# The fixture service the container runs to reach the outgoing connection
_service_file_name = 'llm_check.py'

# Where the import file lands inside the container
_container_yaml_path = '/tmp/zato-llm-local-docker.yaml'

# The word the model is told to reply with
_reply_word = 'pineapple'

# How long one docker command may take, in seconds
_docker_timeout = 300

# How long to keep retrying the invocation while the service deploys
# and the connection pool builds, in seconds
_propagation_timeout = 240

# How often to retry it, in seconds
_propagation_poll_interval = 2.0

# ################################################################################################################################
# ################################################################################################################################

def _run_command(command:'strlist') -> 'subprocess.CompletedProcess':
    """ Runs one host command, raising with the full output when it fails.
    """

    out = subprocess.run(command, capture_output=True, text=True, timeout=_docker_timeout)

    if out.returncode != 0:
        raise Exception(
            f'Command failed (exit {out.returncode}): {command}\nstdout: {out.stdout}\nstderr: {out.stderr}')

    return out

# ################################################################################################################################

def _get_bridge_gateway() -> 'str':
    """ Returns the docker bridge gateway address - the container reaches host ports through it.
    """

    result = _run_command(
        ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}', Container_Name])

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _import_outconn(address:'str') -> 'None':
    """ Imports the suite's outgoing LLM connection into the container.
    """

    yaml_text = f"""
llm:
  - name: {_outconn_name}
    address: {address}
    model: {containers.Model_Name}
    api_key: not-needed-for-ollama
"""

    host_yaml_path = os.path.join(tempfile.gettempdir(), f'zato-llm-local-docker-{os.getpid()}.yaml')

    with open(host_yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_text)

    try:
        _ = _run_command(['docker', 'cp', host_yaml_path, f'{Container_Name}:{_container_yaml_path}'])
        _ = _run_command(['docker', 'exec', Container_Name,
            _zato_binary, 'enmasse', _server_directory, '--verbose', '--import', '--input', _container_yaml_path])
        _ = _run_command(['docker', 'exec', Container_Name, 'rm', _container_yaml_path])

    finally:
        os.remove(host_yaml_path)

# ################################################################################################################################

def _deploy_service() -> 'None':
    """ Copies the fixture service into the container's hot-deployment directory.
    """

    service_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'services', _service_file_name)
    _ = _run_command(['docker', 'cp', service_path, f'{Container_Name}:{_pickup_directory}/{_service_file_name}'])

# ################################################################################################################################

def _invoke_until_replied(prompt:'str') -> 'str':
    """ Invokes the fixture service until the model's reply comes back - the first attempts
    may find the service still deploying or the connection pool still building.
    """

    payload = json.dumps({'text': prompt})
    deadline = time.monotonic() + _propagation_timeout
    last_output = ''

    while time.monotonic() < deadline:

        result = subprocess.run(
            ['docker', 'exec', Container_Name,
                _zato_binary, 'service', 'invoke', _server_directory, _service_name, '--payload', payload],
            capture_output=True, text=True, timeout=_docker_timeout,
        )

        last_output = result.stdout + result.stderr

        if 'reply' in last_output:
            return last_output

        time.sleep(_propagation_poll_interval)

    raise Exception(f'No reply from `{_service_name}` within {_propagation_timeout}s, last output: {last_output}')

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnInvoke:
    """ One outgoing LLM connection goes into the local container through enmasse,
    one fixture service is hot-deployed next to it and one invocation runs
    the whole path - service, connection, Ollama and back.
    """

# ################################################################################################################################

    def test_the_service_invokes_the_outconn(self, local_container:'None') -> 'None':

        # The container reaches the host's Ollama through the bridge gateway ..
        gateway = _get_bridge_gateway()
        address = f'http://{gateway}:{containers.Ollama_Port}/v1'

        # .. the connection and the service go in ..
        _import_outconn(address)
        _deploy_service()

        # .. and one invocation crosses the whole path.
        output = _invoke_until_replied(f'Reply with exactly this one word: {_reply_word}')

        assert _reply_word in output.lower(), output

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time

# local
import ollama_containers as containers
from local_docker import deploy_service_file, get_bridge_gateway, import_enmasse, invoke_service

# ################################################################################################################################
# ################################################################################################################################

# The objects are named the same on every run
_outconn_name = 'test.llm.local-docker'
_service_name = 'test.llm.local-docker.check'

# The fixture service the container runs to reach the outgoing connection
_service_file_name = 'llm_check.py'

# The name of the import file, on the host and inside the container
_yaml_file_prefix = 'zato-llm-local-docker'

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

    import_enmasse(yaml_text, _yaml_file_prefix, _docker_timeout)

# ################################################################################################################################

def _deploy_service() -> 'None':
    """ Copies the fixture service into the container's hot-deployment directory.
    """

    service_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'services', _service_file_name)
    deploy_service_file(service_path)

# ################################################################################################################################

def _invoke_until_replied(prompt:'str') -> 'str':
    """ Invokes the fixture service until the model's reply comes back - the first attempts
    may find the service still deploying or the connection pool still building.
    """

    payload = json.dumps({'text': prompt})
    deadline = time.monotonic() + _propagation_timeout
    last_output = ''

    while time.monotonic() < deadline:

        last_output = invoke_service(_service_name, payload, _docker_timeout)

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
        gateway = get_bridge_gateway()
        address = f'http://{gateway}:{containers.Ollama_Port}/v1'

        # .. the connection and the service go in ..
        _import_outconn(address)
        _deploy_service()

        # .. and one invocation crosses the whole path.
        output = _invoke_until_replied(f'Reply with exactly this one word: {_reply_word}')

        assert _reply_word in output.lower(), output

# ################################################################################################################################
# ################################################################################################################################

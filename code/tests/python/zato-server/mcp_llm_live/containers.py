# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import shutil
import subprocess
import time

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The Ollama instance the LLM tests run against - the container and the model volume
# are created once and reused across runs.
Ollama_Image          = 'ollama/ollama'
Ollama_Container_Name = 'zato-test-ollama'
Ollama_Volume_Name    = 'zato-test-ollama-models'
Ollama_Port           = 21434
Ollama_Base_URL       = f'http://localhost:{Ollama_Port}'

# The OpenAI-compatible endpoint the agent loop and self.llm speak to
Ollama_OpenAI_URL = f'{Ollama_Base_URL}/v1'

# The model the tests drive
Model_Name = 'gpt-oss:20b'

# The browser console - Open WebUI connected to the Ollama instance above
Console_Image          = 'ghcr.io/open-webui/open-webui:main'
Console_Container_Name = 'zato-test-open-webui'
Console_Volume_Name    = 'zato-test-open-webui-data'
Console_Port           = 21435
Console_URL            = f'http://localhost:{Console_Port}'

# A stable secret so console logins survive container recreations
_console_secret_key = 'zato-test-open-webui-secret'

# The port Open WebUI listens on inside its container
_console_internal_port = 8080

# The name under which the console's container reaches the host, where Ollama's port is published
_console_host_name = 'host.docker.internal'

# The port Ollama listens on inside its container
_ollama_internal_port = 11434

# How long to wait for the container to accept requests, in seconds
_startup_timeout = 180

# Timeout for individual HTTP requests, in seconds
_http_timeout = 30

# How often to poll for container readiness, in seconds
_readiness_poll_interval = 1.0

# Timeout for docker commands, in seconds
_docker_timeout = 120

# Timeout for docker commands that create a container, in seconds - the first creation also downloads the image
_docker_create_timeout = 1800

# Read timeout for the model pull, in seconds
_pull_timeout = 4 * 60 * 60

# How often to report pull progress, in seconds
_pull_report_interval = 5.0

# ################################################################################################################################
# ################################################################################################################################

def _run_docker(arguments:'strlist', timeout:'int' = _docker_timeout) -> 'subprocess.CompletedProcess':
    """ Runs a docker command and returns the completed process.
    """
    command = ['docker'] + arguments

    out = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    return out

# ################################################################################################################################

def _pull_image(image:'str') -> 'None':
    """ Pulls a docker image, streaming its progress.
    """
    command = ['docker', 'pull', image]

    result = subprocess.run(command, timeout=_docker_create_timeout)

    if result.returncode != 0:
        raise Exception(f'Could not pull image `{image}`')

# ################################################################################################################################

def is_docker_available() -> 'bool':
    """ Whether the docker CLI exists and its daemon answers - the suite skips cleanly when it does not.
    """

    if not shutil.which('docker'):
        return False

    result = _run_docker(['info'])

    out = result.returncode == 0
    return out

# ################################################################################################################################

def _ensure_container_running() -> 'None':
    """ Starts the Ollama container, creating it first if it does not exist at all.
    The model weights live on a named volume, so recreating the container never repeats the pull.
    """

    # Find out whether the container exists and whether it is running ..
    result = _run_docker(['inspect', '--format', '{{.State.Running}}', Ollama_Container_Name])

    # .. a non-zero exit code means there is no such container, so create it ..
    if result.returncode != 0:
        _pull_image(Ollama_Image)

        result = _run_docker([
            'run', '-d',
            '--name', Ollama_Container_Name,
            '-p', f'{Ollama_Port}:{_ollama_internal_port}',
            '-v', f'{Ollama_Volume_Name}:/root/.ollama',
            Ollama_Image,
        ])

        if result.returncode != 0:
            raise Exception(f'Could not start Ollama -> {result.stderr}')

    # .. an existing but stopped container only needs to be started again.
    elif result.stdout.strip() != 'true':
        result = _run_docker(['start', Ollama_Container_Name])

        if result.returncode != 0:
            raise Exception(f'Could not restart Ollama -> {result.stderr}')

# ################################################################################################################################

def _wait_until_ready() -> 'None':
    """ Polls the version endpoint until Ollama responds or the timeout expires.
    """
    readiness_url = f'{Ollama_Base_URL}/api/version'
    deadline = time.monotonic() + _startup_timeout

    while time.monotonic() < deadline:

        try:
            response = requests.get(readiness_url, timeout=_http_timeout)
        except requests.exceptions.ConnectionError:
            time.sleep(_readiness_poll_interval)
            continue

        if response.ok:
            return

        time.sleep(_readiness_poll_interval)

    raise Exception(f'Ollama did not become ready within {_startup_timeout}s')

# ################################################################################################################################

def _is_model_present(model:'str') -> 'bool':
    """ Whether the model is already among the tags the running instance serves.
    """
    response = requests.get(f'{Ollama_Base_URL}/api/tags', timeout=_http_timeout)
    tags = response.json()

    for item in tags['models']:
        if item['name'] == model:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _pull_model(model:'str') -> 'None':
    """ Pulls the model through the streaming pull endpoint, reporting progress every few seconds.
    """
    pull_url = f'{Ollama_Base_URL}/api/pull'
    body = json.dumps({'model': model})

    last_report = time.monotonic()

    with requests.post(pull_url, data=body, stream=True, timeout=(_http_timeout, _pull_timeout)) as response:

        for line in response.iter_lines():

            if not line:
                continue

            status = json.loads(line)

            # A pull that failed reports its error in the stream rather than through the HTTP status
            if 'error' in status:
                raise Exception(f'Could not pull model `{model}` -> {status["error"]}')

            now = time.monotonic()

            if now - last_report >= _pull_report_interval:
                last_report = now

                # Progress lines carry the layer's completed and total byte counts, other lines only a status
                if 'total' in status:
                    completed = status.get('completed')
                    if completed is None:
                        completed = 0
                    total = status['total']
                    print(f'[OLLAMA] pulling `{model}`: {completed}/{total} bytes ({status["status"]})')
                else:
                    print(f'[OLLAMA] pulling `{model}`: {status["status"]}')

# ################################################################################################################################

def ensure_ollama() -> 'None':
    """ Makes sure the Ollama container is running and answering.
    """
    _ensure_container_running()
    _wait_until_ready()

# ################################################################################################################################

def ensure_model(model:'str'=Model_Name) -> 'None':
    """ Makes sure the model is available in the running instance, pulling it only when it is absent.
    """

    if _is_model_present(model):
        print(f'[OLLAMA] model `{model}` already present')
        return

    print(f'[OLLAMA] model `{model}` absent, pulling now')
    _pull_model(model)

    if not _is_model_present(model):
        raise Exception(f'Model `{model}` still absent after the pull')

# ################################################################################################################################

def _ensure_console_container_running() -> 'None':
    """ Starts the console container, creating it first if it does not exist at all.
    The accounts and chats live on a named volume, so recreating the container keeps the logins.
    """

    # Find out whether the container exists and whether it is running ..
    result = _run_docker(['inspect', '--format', '{{.State.Running}}', Console_Container_Name])

    # .. a non-zero exit code means there is no such container, so create it ..
    if result.returncode != 0:
        _pull_image(Console_Image)

        result = _run_docker([
            'run', '-d',
            '--name', Console_Container_Name,
            '-p', f'{Console_Port}:{_console_internal_port}',
            '--add-host', f'{_console_host_name}:host-gateway',
            '-e', f'OLLAMA_BASE_URL=http://{_console_host_name}:{Ollama_Port}',
            '-e', f'WEBUI_SECRET_KEY={_console_secret_key}',
            '-v', f'{Console_Volume_Name}:/app/backend/data',
            Console_Image,
        ])

        if result.returncode != 0:
            raise Exception(f'Could not start the console -> {result.stderr}')

    # .. an existing but stopped container only needs to be started again.
    elif result.stdout.strip() != 'true':
        result = _run_docker(['start', Console_Container_Name])

        if result.returncode != 0:
            raise Exception(f'Could not restart the console -> {result.stderr}')

# ################################################################################################################################

def _wait_until_console_ready() -> 'None':
    """ Polls the console's front page until it responds or the timeout expires.
    """
    deadline = time.monotonic() + _startup_timeout

    while time.monotonic() < deadline:

        try:
            response = requests.get(Console_URL, timeout=_http_timeout)
        except requests.exceptions.ConnectionError:
            time.sleep(_readiness_poll_interval)
            continue

        if response.ok:
            return

        time.sleep(_readiness_poll_interval)

    raise Exception(f'The console did not become ready within {_startup_timeout}s')

# ################################################################################################################################

def ensure_console() -> 'None':
    """ Makes sure the console container is running and answering.
    """
    _ensure_console_container_running()
    _wait_until_console_ready()

# ################################################################################################################################
# ################################################################################################################################

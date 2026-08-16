# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

# The Ollama container helpers live in the LLM MCP suite - both suites share one implementation.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp_llm_live')))
sys.path.insert(0, os.path.dirname(__file__))

# local
import containers
from _local_docker import Container_Name

# ################################################################################################################################
# ################################################################################################################################

# How long one docker command may take, in seconds
_docker_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _is_container_running() -> 'bool':
    """ Tells whether the local Zato container exists and is running.
    """

    try:
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', Container_Name],
            capture_output=True, text=True, timeout=_docker_timeout,
        )
    except FileNotFoundError:
        return False

    if result.returncode != 0:
        return False

    out = result.stdout.strip() == 'true'
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def local_container() -> 'None':
    """ Skips the suite when the local Zato container is not running,
    otherwise makes sure Ollama and the model are available.
    """

    if not _is_container_running():
        pytest.skip(f'Container `{Container_Name}` is not running')

    containers.ensure_ollama()
    containers.ensure_model()

# ################################################################################################################################
# ################################################################################################################################

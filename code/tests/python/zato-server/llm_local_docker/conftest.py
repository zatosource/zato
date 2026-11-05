# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

# The Ollama container helpers live in the LLM MCP suite - both suites share one implementation,
# and the local container helpers are shared by all the local Docker suites.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp_llm_live')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# local
import ollama_containers as containers
from local_docker import Container_Name, is_container_running

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def local_container() -> 'None':
    """ Skips the suite when the local Zato container is not running,
    otherwise makes sure Ollama and the model are available.
    """

    if not is_container_running():
        pytest.skip(f'Container `{Container_Name}` is not running')

    containers.ensure_ollama()
    containers.ensure_model()

# ################################################################################################################################
# ################################################################################################################################

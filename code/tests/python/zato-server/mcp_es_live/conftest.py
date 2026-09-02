# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Where the shared harness and the Elasticsearch runner are imported from.
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
_es_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', 'es'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

# The Elasticsearch runner's directory goes last - it has its own conftest.py
# and going first would shadow this suite's conftest.
sys.path.append(_es_lib_directory)

# pytest
import pytest  # noqa: E402

# Elasticsearch
from elasticsearch import Elasticsearch  # noqa: E402

# Zato - test helpers
from mcp_connections import harness  # noqa: E402

# The LLM agent harness modules import flat.
harness.add_llm_harness_to_path()

# Zato - test helpers
import es_server  # noqa: E402
import ollama_containers  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, tupnone

# ################################################################################################################################
# ################################################################################################################################

def pytest_report_teststatus(report:'any_', config:'any_') -> 'tupnone':
    if report.when == 'call':
        outcome = report.outcome.upper()
        return report.outcome, f' {outcome} ', f'{outcome} {report.nodeid}'
    return None

# ################################################################################################################################
# ################################################################################################################################

# What the suite's objects are called
Security_Name = 'test.mcp.connections.es.auth'
Group_Name = 'mcp.test-connections-es-group'
Connection_Name = 'search.main'
Gateway_Name = 'test.mcp.connections.es'
Gateway_Path = '/mcp/connections-es'

Username = 'test.mcp.connections.es.user'
Password = 'test.mcp.connections.es.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'es.search_main'

# The index the tests operate on and the documents it starts with
Index_Name = 'articles'
Article_First = 'Zato deployment patterns'
Article_Second = 'Integration with message brokers'

# ################################################################################################################################
# ################################################################################################################################

def _seed_articles(address:'str') -> 'None':
    """ Loads a small, predictable set of articles and makes them
    immediately searchable with one refresh.
    """

    client = Elasticsearch(hosts=[address])

    _ = client.index(index=Index_Name, id='article-1', document={'title': Article_First})
    _ = client.index(index=Index_Name, id='article-2', document={'title': Article_Second})

    _ = client.indices.refresh(index=Index_Name)
    client.close()

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(address:'str') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the Elasticsearch connection against the server and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        es_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'elastic_search': [
            {
                'name': Connection_Name,
                'address_list': [address],
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - a real Elasticsearch server from the unpacked
    distribution, a quickstart environment and one enmasse import that creates
    the connection and the gateway exposing it.
    """

    if not os.environ.get(es_server.ModuleCtx.Env_Key_ES_Dir):
        pytest.skip(f'{es_server.ModuleCtx.Env_Key_ES_Dir} is not set')

    # The server comes up first, on a free port of its own, without TLS ..
    es_port = harness.find_free_port()
    backend_server = es_server.start_es(port=es_port, needs_tls=False)

    try:
        # .. the articles the tests read go in right away ..
        es_address = f'http://127.0.0.1:{es_port}'
        _seed_articles(es_address)

        # .. the quickstart environment follows ..
        environment = harness.start_environment('mcp_connections_es')

        try:
            # .. one import creates everything ..
            harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(es_address))

            # .. and the suite starts once the gateway lists the connection tool.
            mcp_url = environment.mcp_url(Gateway_Path)
            auth = (Username, Password)

            harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

            yield {
                'environment': environment,
                'mcp_url': mcp_url,
                'auth': auth,
                'es_address': es_address,
            }

        finally:
            harness.stop_environment(environment)

    finally:
        es_server.stop_es(backend_server)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def ollama() -> 'any_':
    """ Session-scoped fixture that makes sure the Ollama container is running
    with the model pulled - only the test that drives the model depends on it.
    """

    if not ollama_containers.is_docker_available():
        pytest.skip('Docker is not available')

    ollama_containers.ensure_ollama()
    ollama_containers.ensure_model()

    out = {
        'openai_url': ollama_containers.Ollama_OpenAI_URL,
        'model': ollama_containers.Model_Name,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

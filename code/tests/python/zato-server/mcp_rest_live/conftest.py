# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads

# The shared harness lives with the other cross-suite libraries
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

# pytest
import pytest  # noqa: E402

# Zato - test helpers
from mcp_connections import harness  # noqa: E402

# The LLM agent harness modules import flat.
harness.add_llm_harness_to_path()

# Zato - test helpers
import ollama_containers  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, tupnone, type_

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
Security_Name = 'test.mcp.connections.rest.auth'
Group_Name = 'mcp.test-connections-rest-group'
Connection_Name = 'billing.backend'
Gateway_Name = 'test.mcp.connections.rest'
Gateway_Path = '/mcp/connections-rest'

Username = 'test.mcp.connections.rest.user'
Password = 'test.mcp.connections.rest.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'rest.billing_backend'

# Where the backend answers
Backend_Path = '/api/balance'

# What the backend tells every caller
Backend_Balance = 357

# ################################################################################################################################
# ################################################################################################################################

class _BackendState:
    """ What the in-process backend has seen so far.
    """

    def __init__(self) -> 'None':
        self.requests:'dictlist' = []

# ################################################################################################################################

def _make_backend_handler(state:'_BackendState') -> 'type_':
    """ The request handler of the in-process backend - every request is recorded
    and answered with the one balance document.
    """

    class _Handler(BaseHTTPRequestHandler):

        def _handle(self) -> 'None':

            if content_length := self.headers.get('Content-Length'):
                body_bytes = self.rfile.read(int(content_length))
                body = loads(body_bytes.decode('utf8'))
            else:
                body = None

            state.requests.append({
                'method': self.command,
                'path': self.path,
                'body': body,
            })

            response = dumps({'customer_id': '123', 'balance': Backend_Balance})
            response_bytes = response.encode('utf8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.end_headers()
            _ = self.wfile.write(response_bytes)

        def do_GET(self) -> 'None':
            self._handle()

        def do_POST(self) -> 'None':
            self._handle()

        def log_message(self, format:'str', *args:'any_') -> 'None':
            pass

    return _Handler

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(backend_port:'int') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the outgoing REST connection against the backend and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        rest_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'outgoing_rest': [
            {
                'name': Connection_Name,
                'host': f'http://127.0.0.1:{backend_port}',
                'url_path': Backend_Path,
                'data_format': 'json',
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - the in-process REST backend, a quickstart environment
    and one enmasse import that creates the connection and the gateway exposing it.
    """

    # The backend comes up first, on a free port of its own ..
    backend_state = _BackendState()
    backend_port = harness.find_free_port()

    backend_server = ThreadingHTTPServer(('127.0.0.1', backend_port), _make_backend_handler(backend_state))
    backend_thread = threading.Thread(target=backend_server.serve_forever, daemon=True)
    backend_thread.start()

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_rest')

    try:
        # .. one import creates everything ..
        harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(backend_port))

        # .. and the suite starts once the gateway lists the connection tool.
        mcp_url = environment.mcp_url(Gateway_Path)
        auth = (Username, Password)

        harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

        yield {
            'environment': environment,
            'mcp_url': mcp_url,
            'auth': auth,
            'backend_state': backend_state,
            'backend_port': backend_port,
        }

    finally:
        backend_server.shutdown()
        harness.stop_environment(environment)

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

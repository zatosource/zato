# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps
from zato.common.test import _test_identity
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import _mcp_protocol_version, _server_version, MCPHandler
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager
from zato.server.connection.mcp.stateless import _meta_key_server_info
from zato.server.generic.api.gateway_mcp import GatewayMCPWrapper

# Zato - test helpers
from connection_stubs import StubConfigManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anydict, anylist, strnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.mcp.registry import ToolRegistry

    Bunch = Bunch
    ParallelServer = ParallelServer
    ToolRegistry = ToolRegistry

# ################################################################################################################################
# ################################################################################################################################

# The name of the gateway the wrapper tests build
_gateway_name = 'clinic.analytics'

# The public name the tests configure on a gateway
_public_name = 'Clinic Network Analytics'

# What an initialize request carries
_initialize_params = {
    'protocolVersion': _mcp_protocol_version,
    'capabilities': {},
    'clientInfo': {'name': 'test', 'version': '1.0'},
}

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ A tool registry that exposes no tools.
    """

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        out:'anylist' = []
        return out, None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return False

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ A service store with no services in it.
    """
    def __init__(self) -> 'None':
        self.services = {}
        self.name_to_impl_name = {}

# ################################################################################################################################
# ################################################################################################################################

class _MockServer:
    """ The server attributes the gateway wrapper reads when it builds its handler.
    """
    def __init__(self) -> 'None':
        self.service_store = _MockServiceStore()
        self.config_manager = StubConfigManager()
        self.repo_location = ''

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        out:'anydict' = {}
        return out

# ################################################################################################################################
# ################################################################################################################################

class _MockBunch(dict):
    """ A dict whose keys are also readable as attributes, as a gateway's configuration is.
    """
    def __getattr__(self, name:'str') -> 'any_':
        return self[name]

# ################################################################################################################################
# ################################################################################################################################

def _invoke_noop(service_name:'str', payload:'anydict') -> 'anydict':
    """ The invoke function of handlers whose tools are never called.
    """
    out:'anydict' = {}
    return out

# ################################################################################################################################

def _make_handler() -> 'MCPHandler':
    """ A handler with every response stage off, introducing its gateway under the test public name.
    """
    registry = cast_('ToolRegistry', _MockToolRegistry())
    session_manager = MCPSessionManager()
    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})
    skill_prompts = SkillPrompts('', [])

    out = MCPHandler(registry, _invoke_noop, session_manager, safeguard_config, token_cap_config, False, skill_prompts,
        _public_name)

    return out

# ################################################################################################################################

def _make_wrapper_handler(config:'anydict') -> 'MCPHandler':
    """ The handler a gateway wrapper builds out of the given configuration.
    """
    server = cast_('ParallelServer', _MockServer())
    bunch = cast_('Bunch', _MockBunch(config))

    wrapper = GatewayMCPWrapper(bunch, server)
    wrapper.build_wrapper()

    out = cast_('MCPHandler', wrapper.handler)
    return out

# ################################################################################################################################

def _get_initialize_server_info(handler:'MCPHandler') -> 'anydict':
    """ The serverInfo of the result an initialize request receives.
    """
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': _initialize_params,
    }

    raw = dumps(request)
    response = handler.handle_raw_request(raw, _test_identity)

    body = cast_('anydict', response.body)
    result = body['result']

    out = result['serverInfo']
    return out

# ################################################################################################################################

def _dispatch_stateless(handler:'MCPHandler', method:'str') -> 'anydict':
    """ The result of one request of the stateless revision.
    """
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
    }

    raw = dumps(request)

    response = handler.handle_raw_request(
        raw, _test_identity,
        protocol_version_header=MCP.Protocol_Version_Stateless,
        mcp_method_header=method,
    )

    if response.status_code != OK:
        raise Exception(f'Unexpected status code `{response.status_code}` for `{method}`')

    body = cast_('anydict', response.body)

    out = body['result']
    return out

# ################################################################################################################################
# ################################################################################################################################

class HandlerPublicName(TestCase):
    """ The name a handler introduces its gateway with in each result that has a serverInfo.
    """

    def test_initialize_reports_the_public_name(self) -> 'None':

        handler = _make_handler()
        server_info = _get_initialize_server_info(handler)

        self.assertEqual(server_info['name'], _public_name)
        self.assertEqual(server_info['version'], _server_version)

    def test_discover_reports_the_public_name(self) -> 'None':

        handler = _make_handler()
        result = _dispatch_stateless(handler, 'server/discover')

        server_info = result['serverInfo']
        self.assertEqual(server_info['name'], _public_name)
        self.assertEqual(server_info['version'], _server_version)

    def test_stateless_meta_reports_the_public_name(self) -> 'None':

        handler = _make_handler()
        result = _dispatch_stateless(handler, 'tools/list')

        meta = result['_meta']
        server_info = meta[_meta_key_server_info]
        self.assertEqual(server_info['name'], _public_name)

# ################################################################################################################################
# ################################################################################################################################

class WrapperPublicName(TestCase):
    """ The public name a gateway wrapper gives its handler, out of the gateway's configuration.
    """

    def test_configured_public_name(self) -> 'None':

        handler = _make_wrapper_handler({'name': _gateway_name, 'public_name': _public_name})
        self.assertEqual(handler.public_name, _public_name)

        server_info = _get_initialize_server_info(handler)
        self.assertEqual(server_info['name'], _public_name)

# ################################################################################################################################
# ################################################################################################################################

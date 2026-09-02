# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.api import MCP
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import dumps
from zato.common.test import _test_sec_def_id
from zato.common.typing_ import anytuple, cast_, list_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import _mcp_protocol_version, MCPHandler
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.registry import ToolRegistry
from zato.server.connection.mcp.session import MCPSessionManager
from zato.server.generic.api.gateway_mcp import GatewayMCPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The calls a stub records, one tuple per call
anytuple_list = list_[anytuple]

# ################################################################################################################################
# ################################################################################################################################

class StubConfigStore:
    """ The slice of the server's config store the connection tools reach into.
    """

    def __init__(self) -> 'None':
        self.out_plain_http:'anydict' = {}
        self.out_soap:'anydict' = {}
        self.out_odoo:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class StubSQLPoolStore:
    """ The slice of the SQL pool store the SQL tools reach into.
    """

    def __init__(self) -> 'None':
        self.wrappers:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class StubConfigManager:
    """ Stands in for ConfigManager in registry and tools-call tests - it carries
    every config dict the connection tool groups resolve their names in.
    """

    def __init__(self) -> 'None':

        self.config_store = StubConfigStore()
        self.sql_pool_store = StubSQLPoolStore()

        # The generic connection dicts, one per type
        self.cloud_microsoft_365:'anydict' = {}
        self.chat_microsoft_teams:'anydict' = {}
        self.cloud_microsoft_fabric:'anydict' = {}
        self.cloud_microsoft_power_automate:'anydict' = {}
        self.outconn_sap:'anydict' = {}
        self.cloud_confluence:'anydict' = {}
        self.outconn_es:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def make_rest_item(host:'str', url_path:'str', conn:'any_'=None) -> 'Bunch':
    """ One outgoing REST connection the way the config store holds it -
    the config underneath and the wrapper on the item itself.
    """

    out = Bunch()
    out.config = {
        'host': host,
        'url_path': url_path,
    }
    out.conn = conn

    return out

# ################################################################################################################################

def make_soap_item(host:'str', url_path:'str', soap_action:'str', conn:'any_'=None) -> 'Bunch':
    """ One outgoing SOAP connection the way the config store holds it.
    """

    out = Bunch()
    out.config = {
        'host': host,
        'url_path': url_path,
        'soap_action': soap_action,
    }
    out.conn = conn

    return out

# ################################################################################################################################

class StubSQLPoolItem:
    """ One SQL connection pool the way the pool store holds it -
    a config attribute and an execute method.
    """

    def __init__(self, engine:'str', host:'str', db_name:'str') -> 'None':
        self.config = {
            'engine': engine,
            'host': host,
            'db_name': db_name,
        }
        self.executed:'anytuple_list' = []
        self.execute_result:'any_' = []

    def execute(self, query:'str', params:'any_'=None) -> 'any_':
        """ Records the call and returns what the test configured.
        """

        self.executed.append((query, params))

        out = self.execute_result
        return out

# ################################################################################################################################

def make_odoo_item(host:'str', database:'str', protocol:'str', conn:'any_'=None) -> 'Bunch':
    """ One outgoing Odoo connection the way the config store holds it.
    """

    out = Bunch()
    out.config = {
        'host': host,
        'database': database,
        'protocol': protocol,
    }
    out.conn = conn

    return out

# ################################################################################################################################

def make_generic_item(conn:'any_'=None, **extra:'any_') -> 'Bunch':
    """ One generic connection the way the config manager's per-type dicts hold it -
    flat keys like address or address_list and the wrapper under conn.
    """

    out = Bunch()
    out.conn = conn

    for key, value in extra.items():
        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class StubHTTPResponse:
    """ What a stub REST wrapper answers with - the status code and data
    the REST tool's invoke function reads.
    """

    def __init__(self, status_code:'int', data:'any_') -> 'None':
        self.status_code = status_code
        self.data = data

# ################################################################################################################################

class StubRESTWrapper:
    """ Stands in for HTTPSOAPWrapper on REST items - records every http_request call
    and answers with what the test configured.
    """

    def __init__(self, status_code:'int'=200, data:'any_'=None) -> 'None':
        self.calls:'anytuple_list' = []
        self.response = StubHTTPResponse(status_code, data)

    def http_request(self, method:'str', cid:'str', data:'any_'=None, params:'any_'=None) -> 'StubHTTPResponse':
        self.calls.append((method, cid, data, params))

        out = self.response
        return out

# ################################################################################################################################

class StubSOAPWrapper:
    """ Stands in for HTTPSOAPWrapper on SOAP items - records every invoke call
    and answers with what the test configured.
    """

    def __init__(self, response:'any_'=None) -> 'None':
        self.calls:'anytuple_list' = []
        self.response = response

    def invoke(self, cid:'str', operation:'str', message:'any_'=None) -> 'any_':
        self.calls.append((cid, operation, message))

        out = self.response
        return out

# ################################################################################################################################

class StubMethodClient:
    """ A client whose every configured method records its keyword arguments
    and answers with what the test configured - Fabric, Power Automate,
    Confluence, Elasticsearch and Odoo model stubs all build on it.
    """

    def __init__(self, results:'anydict') -> 'None':
        self.calls:'anytuple_list' = []
        self._results = results

    def __getattr__(self, method:'str') -> 'any_':

        if method not in self._results:
            raise AttributeError(method)

        def _call(*args:'any_', **kwargs:'any_') -> 'any_':
            self.calls.append((method, args, kwargs))

            out = self._results[method]
            return out

        return _call

# ################################################################################################################################

class StubPooledWrapper:
    """ Stands in for the wrappers that lend a pooled client through a client()
    context manager - SAP, Confluence and Odoo connections all use one.
    """

    def __init__(self, client:'any_') -> 'None':
        self.pooled_client = client

    @contextmanager
    def client(self, *args:'any_', **kwargs:'any_') -> 'any_':
        yield self.pooled_client

# ################################################################################################################################

class StubOdooClient:
    """ Stands in for an Odoo client - get_model returns the one model stub
    the test configured.
    """

    def __init__(self, model:'any_') -> 'None':
        self.models_requested:'strlist' = []
        self._model = model

    def get_model(self, model_name:'str') -> 'any_':
        self.models_requested.append(model_name)

        out = self._model
        return out

# ################################################################################################################################

class StubESResult:
    """ What a stub Elasticsearch client answers with - the body is what
    the ES tool's invoke function returns.
    """

    def __init__(self, body:'any_') -> 'None':
        self.body = body

# ################################################################################################################################

class StubESClient:
    """ Stands in for an Elasticsearch client - every configured method records
    its keyword arguments and answers with a result whose body the test configured.
    """

    def __init__(self, results:'anydict') -> 'None':
        self.calls:'anytuple_list' = []
        self._results = results

    def __getattr__(self, method:'str') -> 'any_':

        if method not in self._results:
            raise AttributeError(method)

        def _call(**kwargs:'any_') -> 'StubESResult':
            self.calls.append((method, kwargs))

            out = StubESResult(self._results[method])
            return out

        return _call

# ################################################################################################################################
# ################################################################################################################################

class StubServiceStore:
    """ An empty service store - the connection tool tests never resolve services.
    """

    def __init__(self) -> 'None':
        self.name_to_impl_name:'anydict' = {}
        self.services:'anydict' = {}

# ################################################################################################################################

class StubServer:
    """ Stands in for ParallelServer when a GatewayMCPWrapper is built in tests -
    it carries the stub config manager the connection tools resolve their names in.
    """

    def __init__(self, config_manager:'StubConfigManager') -> 'None':
        self.service_store = StubServiceStore()
        self.config_manager = config_manager
        self.repo_location = ''

    def invoke(self, service_name:'str', payload:'any_') -> 'any_':
        raise Exception(f'Unexpected service invocation `{service_name}`')

# ################################################################################################################################

def make_gateway_wrapper(config_manager:'StubConfigManager', **config_keys:'any_') -> 'GatewayMCPWrapper':
    """ A fully built GatewayMCPWrapper on stub parts - the config keys are
    the gateway's allow lists, e.g. rest_connections=['billing'].
    """

    config = Bunch()
    config.name = 'test-gateway'

    for key, value in config_keys.items():
        config[key] = value

    server = StubServer(config_manager)

    out = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
    out.build_wrapper()

    return out

# ################################################################################################################################

def get_tool_registry(wrapper:'GatewayMCPWrapper') -> 'ToolRegistry':
    """ The registry a built gateway wrapper carries.
    """
    out = cast_('ToolRegistry', wrapper.tool_registry)
    return out

# ################################################################################################################################

def make_mcp_handler(wrapper:'GatewayMCPWrapper', invoke_timeout:'int'=MCP.Default_Invoke_Timeout) -> 'MCPHandler':
    """ An MCPHandler wired to a built gateway wrapper the way build_wrapper wires one,
    with response shaping and input validation off.
    """

    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    tool_registry = get_tool_registry(wrapper)

    out = MCPHandler(
        tool_registry, wrapper._invoke_service, session_manager, safeguard_config, token_cap_config,
        False, SkillPrompts('', []), False, invoke_timeout)

    return out

# ################################################################################################################################

def run_tools_call(handler:'MCPHandler', tool_name:'str', arguments:'anydict') -> 'any_':
    """ One tools/call through the handler, with a fresh session - returns the MCPResponse.
    """

    session_id = handler.session_manager.create(_mcp_protocol_version, _test_sec_def_id)

    request = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'id': 1,
        'params': {'name': tool_name, 'arguments': arguments},
    }

    out = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The MCP boundary - a tools/call request through MCPHandler whose invoke function
runs the same dispatch the MCP gateway runs against the server.
"""

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager

# Test corpus
from boundaries import Boundary, dispatch_service
from cases import Family_Dict, Family_String

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strnone
    from cases import PayloadCase
    anydict = anydict
    anylist = anylist
    strnone = strnone
    PayloadCase = PayloadCase

# ################################################################################################################################
# ################################################################################################################################

class _ToolRegistry:
    """ A registry exposing one tool - the service the current case runs.
    """
    def __init__(self, tool_name:'str') -> 'None':
        self.tool_name = tool_name

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        out = [{'name': self.tool_name, 'description': '', 'inputSchema': {'type': 'object'}}]
        return out

# ################################################################################################################################

    def get_tools_page(self, cursor:'strnone'=None) -> 'tuple':
        out = self.get_tools()
        return out, None

# ################################################################################################################################

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        out = service_name == self.tool_name
        return out

# ################################################################################################################################
# ################################################################################################################################

class MCPBoundary(Boundary):
    """ The MCP path - tools/call through the handler, the wire being the text
    content the handler serializes the service's response into.
    """
    name = 'mcp'
    families = (Family_Dict, Family_String)

    def deliver(self, case:'PayloadCase') -> 'str':

        tool_name = case.service_class._Service__service_name

        def invoke_case_service(service_name:'str', payload:'anydict') -> 'any_':
            """ The gateway's invoke function - the same dispatch the server runs for it.
            """
            out, _ = dispatch_service(case.service_class, payload, CHANNEL.INVOKE, DATA_FORMAT.DICT,
                transport='', serialize=False, skip_response_elem=True)
            return out

        # Response shaping and input validation stay off - empty configs keep every stage disabled.
        registry = cast_('any_', _ToolRegistry(tool_name))
        session_manager = MCPSessionManager()
        safeguard_config = build_safeguard_config({})
        token_cap_config = build_token_cap_config({})

        handler = MCPHandler(registry, invoke_case_service, session_manager, safeguard_config, token_cap_config, False)

        # Every method other than initialize needs a session.
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        # The tool arguments are always a JSON object - string-family requests carry none.
        if isinstance(case.request, dict):
            arguments = case.request
        else:
            arguments = {}

        request = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 1,
            'params': {'name': tool_name, 'arguments': arguments},
        }

        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        body = mcp_response.body
        result = body['result']
        content = result['content']
        first_content = content[0]

        out = first_content['text']
        return out

# ################################################################################################################################

    def decode(self, wire:'str', case:'PayloadCase') -> 'any_':

        # The dict family travels as JSON text, with no response at all being an empty string ..
        if case.family == Family_Dict:
            if wire:
                out = loads(wire)
            else:
                out = ''

        # .. and the string family is the text itself.
        else:
            out = wire

        return out

# ################################################################################################################################
# ################################################################################################################################

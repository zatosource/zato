# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import uuid
from http.client import HTTPSConnection, HTTPConnection
from logging import getLogger
from traceback import format_exc
from urllib.parse import urlparse

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

MCP_Protocol_Version = '2024-11-05'

# ################################################################################################################################
# ################################################################################################################################

class AuthType:
    """ Authentication types for MCP servers.
    """
    NoAuth = 'none'
    APIKey = 'api_key'

# ################################################################################################################################
# ################################################################################################################################

class MCPClient:
    """ Generic MCP client implementing the MCP protocol (JSON-RPC over HTTP with SSE).
    """

    def __init__(self, server_id:'str', endpoint:'str', auth_type:'str'=AuthType.NoAuth,
                 auth_data:'anydict | None'=None) -> 'None':
        self.server_id = server_id
        self.endpoint = endpoint
        self.auth_type = auth_type
        self.auth_data = auth_data or {}
        self._session_url = None

# ################################################################################################################################

    def get_server_info(self) -> 'anydict':
        """ Initializes connection and fetches server info from the MCP endpoint.
        Returns dict with 'name', 'description', etc.
        """
        try:
            init_result = self._initialize()
            if 'error' in init_result:
                return init_result

            server_info = init_result.get('result', {}).get('serverInfo', {})
            name = server_info.get('name', '')
            version = server_info.get('version', '')

            tools = self._list_tools()

            return {
                'name': name,
                'version': version,
                'description': f'{name} v{version}' if version else name,
                'tools': tools
            }
        except Exception as e:
            logger.warning('Failed to get MCP server info from %s: %s', self.endpoint, format_exc())
            return {'name': '', 'description': '', 'tools': [], 'error': str(e)}

# ################################################################################################################################

    def _initialize(self) -> 'anydict':
        """ Sends initialize request to MCP server.
        """
        request_id = str(uuid.uuid4())
        payload = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': 'initialize',
            'params': {
                'protocolVersion': MCP_Protocol_Version,
                'capabilities': {},
                'clientInfo': {
                    'name': 'Zato',
                    'version': '4.1'
                }
            }
        }

        response = self._mcp_request(payload)

        if response.get('result'):
            self._send_initialized_notification()

        return response

# ################################################################################################################################

    def _send_initialized_notification(self) -> 'None':
        """ Sends initialized notification after successful init.
        """
        payload = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        }
        self._mcp_request(payload, expect_response=False)

# ################################################################################################################################

    def _list_tools(self) -> 'anylist':
        """ Lists available tools from the MCP server.
        """
        request_id = str(uuid.uuid4())
        payload = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': 'tools/list',
            'params': {}
        }

        response = self._mcp_request(payload)
        result = response.get('result', {})
        tools = result.get('tools', [])
        return tools

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        """ Returns list of tools available from this MCP server.
        """
        try:
            init_result = self._initialize()
            if 'error' in init_result:
                return []

            return self._list_tools()
        except Exception as e:
            logger.warning('Failed to get MCP tools from %s: %s', self.endpoint, format_exc())
            return []

# ################################################################################################################################

    def invoke_tool(self, tool_name:'str', arguments:'anydict') -> 'any_':
        """ Invokes a tool on the MCP server and returns the result.
        """
        try:
            init_result = self._initialize()
            if 'error' in init_result:
                return init_result

            request_id = str(uuid.uuid4())
            payload = {
                'jsonrpc': '2.0',
                'id': request_id,
                'method': 'tools/call',
                'params': {
                    'name': tool_name,
                    'arguments': arguments
                }
            }

            response = self._mcp_request(payload)
            logger.info('MCP tool %s invoked on %s: %s', tool_name, self.server_id, response)

            if 'error' in response:
                return {'error': response['error'].get('message', 'Unknown error')}

            result = response.get('result', {})
            content = result.get('content', [])

            text_parts = []
            for item in content:
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))

            return {'result': '\n'.join(text_parts) if text_parts else result}

        except Exception as e:
            logger.warning('Failed to invoke MCP tool %s on %s: %s', tool_name, self.server_id, format_exc())
            return {'error': str(e)}

# ################################################################################################################################

    def _get_auth_headers(self) -> 'anydict':
        """ Returns authentication headers based on auth_type.
        """
        headers = {}
        if self.auth_type == AuthType.APIKey:
            api_key = self.auth_data.get('api_key', '')
            header_name = self.auth_data.get('header_name', 'Authorization')
            if api_key:
                headers[header_name] = api_key
        return headers

# ################################################################################################################################

    def _mcp_request(self, payload:'anydict', expect_response:'bool'=True) -> 'anydict':
        """ Makes an MCP JSON-RPC request.
        """
        parsed = urlparse(self.endpoint)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'

        if parsed.scheme == 'https':
            conn = HTTPSConnection(host, port, timeout=30)
        else:
            conn = HTTPConnection(host, port, timeout=30)

        headers = self._get_auth_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json, text/event-stream'
        headers['User-Agent'] = 'Zato-MCP-Client'

        body = json.dumps(payload)

        logger.info('MCP request to %s: %s', self.endpoint, body)

        try:
            conn.request('POST', path, body=body, headers=headers)
            response = conn.getresponse()

            if response.status >= 400:
                error_body = response.read().decode('utf-8')
                logger.warning('MCP error response %d: %s', response.status, error_body)
                try:
                    error_json = json.loads(error_body)
                    if 'error' in error_json:
                        return error_json
                except json.JSONDecodeError:
                    pass
                return {'error': {'message': f'HTTP {response.status}: {error_body}'}}

            if not expect_response:
                return {}

            content_type = response.getheader('Content-Type', '')
            body_bytes = response.read()
            body_str = body_bytes.decode('utf-8')

            logger.info('MCP response: %s', body_str[:500])

            if 'text/event-stream' in content_type:
                return self._parse_sse_response(body_str)
            else:
                return json.loads(body_str)

        finally:
            conn.close()

# ################################################################################################################################

    def _parse_sse_response(self, body:'str') -> 'anydict':
        """ Parses SSE response and extracts JSON-RPC message.
        """
        for line in body.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data_str = line[5:].strip()
                if data_str:
                    try:
                        return json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

        return {'error': {'message': 'No valid JSON-RPC response in SSE stream'}}

# ################################################################################################################################
# ################################################################################################################################

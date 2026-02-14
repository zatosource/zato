# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from urllib.request import Request, urlopen

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
    """ Generic MCP client that works with any MCP server.
    """

    def __init__(self, server_id:'str', endpoint:'str', auth_type:'str'=AuthType.NoAuth,
                 auth_data:'anydict | None'=None) -> 'None':
        self.server_id = server_id
        self.endpoint = endpoint
        self.auth_type = auth_type
        self.auth_data = auth_data or {}

# ################################################################################################################################

    def get_server_info(self) -> 'anydict':
        """ Fetches server info from the MCP endpoint.
        Returns dict with 'name', 'description', etc.
        """
        try:
            response = self._http_get(self.endpoint)
            return {
                'name': response.get('name', ''),
                'description': response.get('description', ''),
                'tools': response.get('tools', [])
            }
        except Exception as e:
            logger.warning('Failed to get MCP server info from %s: %s', self.endpoint, e)
            return {'name': '', 'description': '', 'tools': []}

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        """ Returns list of tools available from this MCP server.
        """
        try:
            response = self._http_get(self.endpoint)
            tools = response.get('tools', [])
            logger.info('MCP server %s: %d tools available', self.server_id, len(tools))
            return tools
        except Exception as e:
            logger.warning('Failed to get MCP tools from %s: %s', self.endpoint, e)
            return []

# ################################################################################################################################

    def invoke_tool(self, tool_name:'str', arguments:'anydict') -> 'any_':
        """ Invokes a tool on the MCP server and returns the result.
        """
        try:
            data = {
                'tool': tool_name,
                'arguments': arguments
            }
            response = self._http_post(self.endpoint, data)
            logger.info('MCP tool %s invoked on %s: %s', tool_name, self.server_id, response)
            return response
        except Exception as e:
            logger.warning('Failed to invoke MCP tool %s on %s: %s', tool_name, self.server_id, e)
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

    def _http_get(self, url:'str') -> 'any_':
        """ Makes an HTTP GET request.
        """
        headers = self._get_auth_headers()
        request = Request(url, headers=headers, method='GET')

        with urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
            return json.loads(body)

# ################################################################################################################################

    def _http_post(self, url:'str', data:'anydict') -> 'any_':
        """ Makes an HTTP POST request.
        """
        headers = self._get_auth_headers()
        headers['Content-Type'] = 'application/json'

        body_bytes = json.dumps(data).encode('utf-8')
        request = Request(url, data=body_bytes, headers=headers, method='POST')

        with urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
            return json.loads(body)

# ################################################################################################################################
# ################################################################################################################################

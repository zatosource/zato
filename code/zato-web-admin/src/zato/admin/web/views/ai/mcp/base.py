# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from abc import ABC, abstractmethod
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
    OAuth2 = 'oauth2'

# ################################################################################################################################
# ################################################################################################################################

class BaseMCPClient(ABC):
    """ Base class for MCP clients.
    """

    server_id:'str' = ''
    server_name:'str' = ''
    auth_type:'str' = AuthType.NoAuth

    def __init__(self, endpoint:'str', auth_data:'anydict | None'=None) -> 'None':
        self.endpoint = endpoint
        self.auth_data = auth_data or {}

# ################################################################################################################################

    @abstractmethod
    def get_tools(self) -> 'anylist':
        """ Returns list of tools available from this MCP server.
        Each tool should have: name, description, parameters (JSON schema).
        """
        pass

# ################################################################################################################################

    @abstractmethod
    def invoke_tool(self, tool_name:'str', arguments:'anydict') -> 'any_':
        """ Invokes a tool on the MCP server and returns the result.
        """
        pass

# ################################################################################################################################

    def _http_get(self, url:'str', headers:'anydict | None'=None) -> 'any_':
        """ Makes an HTTP GET request.
        """
        headers = headers or {}
        request = Request(url, headers=headers, method='GET')

        with urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
            return json.loads(body)

# ################################################################################################################################

    def _http_post(self, url:'str', data:'anydict', headers:'anydict | None'=None) -> 'any_':
        """ Makes an HTTP POST request.
        """
        headers = headers or {}
        headers['Content-Type'] = 'application/json'

        body_bytes = json.dumps(data).encode('utf-8')
        request = Request(url, data=body_bytes, headers=headers, method='POST')

        with urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
            return json.loads(body)

# ################################################################################################################################
# ################################################################################################################################

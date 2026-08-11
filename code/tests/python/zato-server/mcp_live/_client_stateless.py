# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# requests
import requests

# local
from _constants import _protocol_version_stateless

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, strnone, tupnone

# ################################################################################################################################
# ################################################################################################################################

# Content type for all MCP JSON-RPC requests
_content_type = 'application/json'

# Timeout in seconds for all HTTP requests
_request_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class MCPStatelessClient:
    """ Test client for the stateless MCP revision.
    There are no sessions - each request carries the MCP-Protocol-Version,
    Mcp-Method and, for tools/call, Mcp-Name headers.
    """

    def __init__(self, mcp_url:'str', auth:'tupnone' = None) -> 'None':
        """ Stores the MCP endpoint URL and optional auth for all subsequent requests.
        """

        self.mcp_url = mcp_url
        self.auth = auth

# ################################################################################################################################

    def jsonrpc(
        self,
        method:'str',
        params:'anydictnone' = None,
        request_id:'any_' = 1,
        mcp_method_header:'strnone' = None,
        mcp_name_header:'strnone' = None,
        protocol_version_header:'strnone' = None,
        include_method_header:'bool' = True,
        include_version_header:'bool' = True,
        ) -> 'requests.Response':
        """ Sends a single JSON-RPC request and returns the raw response.
        The Mcp-Method header defaults to the method itself, and the version header
        defaults to the stateless revision - each can be overridden for mismatch tests.
        """

        # Build the JSON-RPC envelope ..
        body:'anydict' = {
            'jsonrpc': '2.0',
            'method': method,
            'id': request_id,
        }

        if params is not None:
            body['params'] = params

        # .. build the per-request headers of the stateless revision ..
        headers:'anydict' = {
            'Content-Type': _content_type,
        }

        if include_version_header:

            if protocol_version_header is None:
                protocol_version_header = _protocol_version_stateless

            headers['MCP-Protocol-Version'] = protocol_version_header

        if include_method_header:

            if mcp_method_header is None:
                mcp_method_header = method

            headers['Mcp-Method'] = mcp_method_header

        if mcp_name_header:
            headers['Mcp-Name'] = mcp_name_header

        # .. send the request and return the response.
        request_data = dumps(body)

        out = requests.post(self.mcp_url, data=request_data, headers=headers, auth=self.auth, timeout=_request_timeout)
        return out

# ################################################################################################################################

    def discover(self) -> 'requests.Response':
        """ Convenience method: sends a server/discover request.
        """

        out = self.jsonrpc('server/discover')
        return out

# ################################################################################################################################

    def tools_list(self) -> 'requests.Response':
        """ Convenience method: sends a tools/list request.
        """

        out = self.jsonrpc('tools/list')
        return out

# ################################################################################################################################

    def tools_call(self, name:'str', arguments:'anydictnone' = None) -> 'requests.Response':
        """ Convenience method: sends a tools/call request with a matching Mcp-Name header.
        """

        if arguments is None:
            arguments = {}

        params = {'name': name, 'arguments': arguments}

        out = self.jsonrpc('tools/call', params=params, mcp_name_header=name)
        return out

# ################################################################################################################################
# ################################################################################################################################

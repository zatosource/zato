# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from typing import NamedTuple

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, strdictlist, strnone, tupnone

# ################################################################################################################################
# ################################################################################################################################

class InitializeResult(NamedTuple):
    response: 'requests.Response'
    session_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

# Content type for all MCP JSON-RPC requests
_content_type = 'application/json'

# Header name for the MCP session ID
_session_header = 'Mcp-Session-Id'

# Timeout in seconds for all HTTP requests
_request_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class MCPClient:
    """ Test client for MCP JSON-RPC over HTTP.
    Provides methods for single requests, batch requests, raw bytes,
    GET notification polling, and DELETE session termination.
    """

    def __init__(self, mcp_url:'str', auth:'tupnone' = None) -> 'None':
        """ Stores the MCP endpoint URL and optional auth for all subsequent requests.
        """

        self.mcp_url = mcp_url
        self.auth = auth

# ################################################################################################################################

    def _build_headers(self, session_id:'strnone' = None) -> 'anydict':
        """ Builds request headers, including the session ID header if provided.
        """

        out:'anydict' = {
            'Content-Type': _content_type,
        }

        if session_id:
            out[_session_header] = session_id

        return out

# ################################################################################################################################

    def jsonrpc(
        self,
        method:'str',
        params:'anydictnone' = None,
        request_id:'any_' = 1,
        session_id:'strnone' = None,
        extra_headers:'anydictnone' = None,
        ) -> 'requests.Response':
        """ Sends a single JSON-RPC request and returns the raw response.
        """

        # Build the JSON-RPC envelope ..
        body:'anydict' = {
            'jsonrpc': '2.0',
            'method': method,
            'id': request_id,
        }

        if params is not None:
            body['params'] = params

        # .. send the request and return the response.
        headers = self._build_headers(session_id)

        if extra_headers:
            headers.update(extra_headers)

        request_data = dumps(body)
        out = requests.post(self.mcp_url, data=request_data, headers=headers, auth=self.auth, timeout=_request_timeout)

        return out

# ################################################################################################################################

    def jsonrpc_batch(
        self,
        messages:'strdictlist',
        session_id:'strnone' = None,
        ) -> 'requests.Response':
        """ Sends a JSON-RPC batch request (array of messages) and returns the raw response.
        """

        headers = self._build_headers(session_id)

        request_data = dumps(messages)
        out = requests.post(self.mcp_url, data=request_data, headers=headers, auth=self.auth, timeout=_request_timeout)

        return out

# ################################################################################################################################

    def jsonrpc_raw(self, raw_bytes:'bytes', session_id:'strnone' = None) -> 'requests.Response':
        """ Sends raw bytes as the request body for error path testing.
        """

        headers = self._build_headers(session_id)

        out = requests.post(self.mcp_url, data=raw_bytes, headers=headers, auth=self.auth, timeout=_request_timeout)

        return out

# ################################################################################################################################

    def delete_session(self, session_id:'strnone' = None) -> 'requests.Response':
        """ Sends a DELETE request to terminate an MCP session.
        """

        headers = self._build_headers(session_id)

        out = requests.delete(self.mcp_url, headers=headers, auth=self.auth, timeout=_request_timeout)

        return out

# ################################################################################################################################

    def initialize(self) -> 'InitializeResult':
        """ Convenience method: sends an initialize request and extracts the session ID.
        Returns the response and the session ID from the response header.
        """

        response = self.jsonrpc('initialize')
        session_id = response.headers[_session_header]

        out = InitializeResult(response, session_id)

        return out

# ################################################################################################################################
# ################################################################################################################################

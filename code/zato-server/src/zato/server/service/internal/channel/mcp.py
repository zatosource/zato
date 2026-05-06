# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT

# Zato
from zato.common.json_internal import dumps
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# Content type for JSON-RPC responses
_content_type_json = 'application/json'

# MCP session header name (lowercase, as stored by HTTPRequestData._extract_headers)
_session_header = 'mcp-session-id'

# MCP session response header name (original casing for the HTTP response)
_session_response_header = 'Mcp-Session-Id'

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpoint(AdminService):
    """ Built-in service that serves as the MCP endpoint.
    Receives raw JSON-RPC requests, dispatches them through the MCP channel's handler,
    and returns JSON-RPC responses. Supports MCP-Session-Id headers and DELETE for
    session termination.
    """

    name = 'zato.channel.mcp.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes an incoming MCP request.
        """

        # Look up the MCP channel config from the worker store,
        # then reach the ChannelMCPWrapper through its .conn attribute ..
        channel_config = self.server.worker_store.channel_mcp[self.channel.name]
        wrapper = channel_config.conn

        # .. read the session ID from the request header if present ..
        session_id = self.request.http.headers.get(_session_header)

        # .. build the remote address string for session logging ..
        remote_addr = self.wsgi_environ.get('REMOTE_ADDR', '')
        remote_port = self.wsgi_environ.get('REMOTE_PORT', '')
        remote_address = f'{remote_addr}:{remote_port}'

        # .. handle DELETE requests for session termination ..
        if self.request.http.method == 'DELETE':
            mcp_response = wrapper.handler.handle_delete_session(session_id)
            self.response.status_code = mcp_response.status_code
            self.response.payload = ''
            return

        # .. get the raw request body ..
        raw_request = self.request.raw_request

        if isinstance(raw_request, str):
            raw_request = raw_request.encode('utf8')

        # .. dispatch through the MCP handler ..
        mcp_response = wrapper.handler.handle_raw_request(raw_request, session_id, remote_address)

        # .. if the handler returned a session ID (from initialize), set it as a response header ..
        if mcp_response.session_id:
            self.response.headers[_session_response_header] = mcp_response.session_id

        # .. set the response.
        self.response.status_code = mcp_response.status_code

        if mcp_response.status_code == NO_CONTENT:
            self.response.payload = ''

        else:
            self.response.payload = dumps(mcp_response.body)
            self.response.data_format = _content_type_json

# ################################################################################################################################
# ################################################################################################################################

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

# Content type for SSE streaming responses
_content_type_sse = 'text/event-stream'

# MCP session header name (lowercase, as stored by HTTPRequestData._extract_headers)
_session_header = 'mcp-session-id'

# MCP session response header name (original casing for the HTTP response)
_session_response_header = 'Mcp-Session-Id'

# Accept header name (lowercase)
_accept_header = 'accept'

# WSGI environ key signaling that the response payload is a streaming iterator
_streaming_flag = 'zato.mcp.is_streaming'

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

        # Look up the MCP channel config from the config manager,
        # then reach the ChannelMCPWrapper through its .conn attribute ..
        channel_config = self.server.config_manager.channel_mcp[self.channel.name]
        wrapper = channel_config.conn

        # .. read the session ID from the request header if present ..
        session_id = self.request.http.headers.get(_session_header)

        # .. get the remote address for session logging ..
        remote_address = self.wsgi_environ.get('REMOTE_ADDR', '')

        # .. handle GET requests for server-to-client notifications ..
        if self.request.http.method == 'GET':
            mcp_response = wrapper.handler.get_pending_notifications(session_id)
            self.response.status_code = mcp_response.status_code

            if mcp_response.body:
                self.response.payload = dumps(mcp_response.body)
                self.response.data_format = _content_type_json
            else:
                self.response.payload = ''

            return

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

        # .. check whether the client accepts SSE streaming ..
        accept_header = self.request.http.headers.get(_accept_header, '')
        wants_streaming = _content_type_sse in accept_header

        # .. dispatch through the MCP handler ..
        mcp_response = wrapper.handler.handle_raw_request(raw_request, session_id, remote_address)

        # .. if the handler returned a session ID (from initialize), set it as a response header ..
        if mcp_response.session_id:
            self.response.headers[_session_response_header] = mcp_response.session_id

        # .. set the response.
        self.response.status_code = mcp_response.status_code

        if mcp_response.status_code == NO_CONTENT:
            self.response.payload = ''

        elif mcp_response.is_streaming:
            if wants_streaming:
                # .. the handler produced a streaming generator and the client accepts SSE ..
                self.response.content_type = _content_type_sse
                self.response.payload = mcp_response.body
                self.wsgi_environ[_streaming_flag] = True
            else:
                # .. the handler produced a streaming generator but the client wants JSON,
                # .. so drain the generator and return the last frame as a regular response.
                last_chunk = b''
                for chunk in mcp_response.body:
                    last_chunk = chunk
                self.response.payload = last_chunk
                self.response.data_format = _content_type_json

        else:
            self.response.payload = dumps(mcp_response.body)
            self.response.data_format = _content_type_json

# ################################################################################################################################
# ################################################################################################################################

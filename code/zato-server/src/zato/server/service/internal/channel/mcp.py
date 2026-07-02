# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FORBIDDEN, NO_CONTENT, NOT_FOUND

# Zato
from zato.common.json_internal import dumps
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Content type for JSON-RPC responses
_content_type_json = 'application/json'

# MCP session header name (lowercase, as stored by HTTPRequestData._extract_headers)
_session_header = 'mcp-session-id'

# MCP session response header name (original casing for the HTTP response)
_session_response_header = 'Mcp-Session-Id'

# MCP protocol version header name (lowercase, as stored by HTTPRequestData._extract_headers)
_protocol_version_header = 'mcp-protocol-version'

# WSGI environ key set by the Rust HTTP layer with the resolved client address
_remote_addr_key = 'zato.http.remote_addr'

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

        # MCP channels require authentication via security groups ..
        # .. if the HTTP layer did not authenticate the caller, reject immediately.
        channel_security = self.channel.security

        if not channel_security.id:
            logger.info('MCP channel `%s` rejected unauthenticated request', self.channel.name)
            self.response.status_code = FORBIDDEN
            self.response.payload = ''
            return

        logger.info(
            'MCP channel `%s` authenticated sec_def id=`%s` username=`%s`',
            self.channel.name, channel_security.id, channel_security.username)

        # Look up the MCP channel config from the config manager,
        # then reach the ChannelMCPWrapper through its .conn attribute ..
        channel_config = self.server.config_manager.channel_mcp[self.channel.name]
        wrapper = channel_config.conn

        # .. read the session ID from the request header if present ..
        session_id = self.request.http.headers.get(_session_header)

        # .. read the protocol version header if present, used to detect a version mismatch ..
        protocol_version_header = self.request.http.headers.get(_protocol_version_header)

        # .. get the remote address for session logging ..
        remote_address = self.wsgi_environ[_remote_addr_key]

        # .. get the sec_def id of the authenticated caller ..
        sec_def_id = channel_security.id

        # .. get the handler for request dispatch, reading it once into a local so a channel
        # deletion later in this request cannot affect the dispatch already underway ..
        handler = wrapper.handler

        # .. no handler means the channel is not usable - it was not built yet,
        # its build failed, or it is being deleted - in all cases the resource does not exist ..
        if handler is None:
            logger.info('MCP channel `%s` has no handler (not built yet, build failed, or channel deleted)', self.channel.name)
            self.response.status_code = NOT_FOUND
            self.response.payload = ''
            return

        # .. handle DELETE requests for session termination ..
        if self.request.http.method == 'DELETE':

            mcp_response = handler.handle_delete_session(session_id, protocol_version_header, sec_def_id)
            self.response.status_code = mcp_response.status_code

            if mcp_response.body:
                self.response.payload = dumps(mcp_response.body)
                self.response.data_format = _content_type_json
            else:
                self.response.payload = ''

            return

        # .. get the raw request body ..
        raw_request = self.request.raw_request

        if isinstance(raw_request, str):
            raw_request = raw_request.encode('utf8')

        # .. dispatch through the MCP handler ..
        mcp_response = handler.handle_raw_request(
            raw_request, session_id, remote_address, protocol_version_header, sec_def_id)

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

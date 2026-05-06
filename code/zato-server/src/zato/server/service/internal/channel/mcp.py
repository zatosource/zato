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

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpoint(AdminService):
    """ Built-in service that serves as the MCP endpoint.
    Receives raw JSON-RPC requests, dispatches them through the MCP channel's handler,
    and returns JSON-RPC responses.
    """

    name = 'zato.channel.mcp.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes an incoming MCP request.
        """

        # Look up the MCP channel wrapper from the worker store ..
        wrapper = self.server.worker_store.channel_mcp[self.channel.name]

        # .. get the raw request body ..
        raw_request = self.request.raw_request

        if isinstance(raw_request, str):
            raw_request = raw_request.encode('utf8')

        # .. dispatch through the MCP handler ..
        mcp_response = wrapper.handler.handle_raw_request(raw_request)

        # .. set the response.
        self.response.status_code = mcp_response.status_code

        if mcp_response.status_code == NO_CONTENT:
            self.response.payload = ''

        else:
            self.response.payload = dumps(mcp_response.body)
            self.response.data_format = _content_type_json

# ################################################################################################################################
# ################################################################################################################################

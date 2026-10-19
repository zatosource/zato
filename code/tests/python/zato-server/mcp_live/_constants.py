# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# JSON-RPC 2.0 error codes used across MCP tests
_error_parse            = -32700
_error_invalid_request  = -32600
_error_method_not_found = -32601
_error_invalid_params   = -32602

# JSON-RPC error code returned when an Mcp-* header does not agree with the request body
_error_header_mismatch = -32020

# JSON-RPC error code returned when a request asks for a protocol version the server does not speak
_error_unsupported_protocol_version = -32022

# JSON-RPC protocol version
_jsonrpc_version = '2.0'

# The stateless MCP protocol revision
_protocol_version_stateless = '2026-07-28'

# The demo service exposed on the default MCP gateway
_demo_echo_service = 'demo.echo'

# The test service that always raises an exception
_raise_service = 'test.raise'

# The name the default MCP gateway introduces itself with to MCP clients
_mcp_public_name = 'Test MCP Live Gateway'

# The gateway imported with no security groups, which rejects every request
_mcp_without_groups_gateway = 'test.mcp.live.without-groups'

# The gateway imported without a public name, which introduces itself under its own name
_mcp_no_public_name_gateway = 'test.mcp.live.no-public-name'

# The version reported next to the public name in every serverInfo
_server_version = '2.4'

# Header name for the MCP session ID prefix
_session_id_prefix = 'mcp'

# Prefix that identifies Zato-internal services
_zato_internal_prefix = 'zato.'

# ################################################################################################################################
# ################################################################################################################################

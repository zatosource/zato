# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# JSON-RPC 2.0 error codes used across MCP tests
_error_parse            = -32700
_error_invalid_request  = -32600
_error_method_not_found = -32601
_error_invalid_params   = -32602

# JSON-RPC protocol version
_jsonrpc_version = '2.0'

# The demo service exposed on the default MCP channel
_demo_echo_service = 'demo.echo'

# Header name for the MCP session ID
_session_header = 'Mcp-Session-Id'

# MCP session ID prefix
_session_id_prefix = 'mcp'

# Prefix that identifies Zato-internal services
_zato_internal_prefix = 'zato.'

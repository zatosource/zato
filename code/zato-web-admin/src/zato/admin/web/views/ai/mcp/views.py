# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.mcp.registry import MCPRegistry
from zato.common.json_internal import loads

if 0:
    from django.http import HttpRequest

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_servers(req:'HttpRequest') -> 'JsonResponse':
    """ Returns list of configured MCP servers.
    """
    servers = MCPRegistry.get_servers()
    return JsonResponse({'servers': servers})

# ################################################################################################################################

@method_allowed('POST')
def add_server(req:'HttpRequest') -> 'JsonResponse':
    """ Adds an MCP server by fetching its info from the endpoint.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=400)

    endpoint = body.get('endpoint', '')
    auth_type = body.get('auth_type', 'none')
    auth_data = body.get('auth_data', {})

    if not endpoint:
        return JsonResponse({'success': False, 'error': 'Endpoint is required'}, status=400)

    result = MCPRegistry.add_server_from_endpoint(endpoint, auth_type, auth_data)

    if result.get('success'):
        return JsonResponse({'success': True, 'server': result.get('server')})
    else:
        return JsonResponse({'success': False, 'error': result.get('error', 'Unknown error')}, status=400)

# ################################################################################################################################

@method_allowed('POST')
def remove_server(req:'HttpRequest') -> 'JsonResponse':
    """ Removes an MCP server.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=400)

    server_id = body.get('id', '')

    if not server_id:
        return JsonResponse({'success': False, 'error': 'Server ID is required'}, status=400)

    success = MCPRegistry.remove_server(server_id)

    if success:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Server not found'}, status=404)

# ################################################################################################################################

@method_allowed('POST')
def update_server(req:'HttpRequest') -> 'JsonResponse':
    """ Updates an MCP server configuration.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=400)

    server_id = body.get('id', '')
    updates = body.get('updates', {})

    if not server_id:
        return JsonResponse({'success': False, 'error': 'Server ID is required'}, status=400)

    success = MCPRegistry.update_server(server_id, updates)

    if success:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Server not found'}, status=404)

# ################################################################################################################################

@method_allowed('GET')
def get_tools(req:'HttpRequest') -> 'JsonResponse':
    """ Returns all tools from all enabled MCP servers.
    """
    tools = MCPRegistry.get_all_tools()
    return JsonResponse({'tools': tools})

# ################################################################################################################################

@method_allowed('POST')
def invoke_tool(req:'HttpRequest') -> 'JsonResponse':
    """ Invokes a tool on an MCP server.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=400)

    server_id = body.get('server_id', '')
    tool_name = body.get('tool', '')
    arguments = body.get('arguments', {})

    if not server_id or not tool_name:
        return JsonResponse({'success': False, 'error': 'Server ID and tool name are required'}, status=400)

    client = MCPRegistry.get_client(server_id)

    if not client:
        return JsonResponse({'success': False, 'error': 'Server not found or disabled'}, status=404)

    result = client.invoke_tool(tool_name, arguments)

    return JsonResponse({'success': True, 'result': result})

# ################################################################################################################################
# ################################################################################################################################

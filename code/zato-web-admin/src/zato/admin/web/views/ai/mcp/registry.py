# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import uuid
from logging import getLogger

# Zato
from zato.admin.web.views.ai.common import get_redis_client
from zato.admin.web.views.ai.mcp.base import MCPClient

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

REDIS_KEY_MCP_SERVERS = 'zato.ai-chat.mcp-servers'

# ################################################################################################################################
# ################################################################################################################################

class MCPRegistry:
    """ Registry for MCP servers. Stores server configurations in Redis.
    """

# ################################################################################################################################

    @classmethod
    def get_servers(cls) -> 'anylist':
        """ Returns list of configured MCP servers.
        """
        redis_client = get_redis_client()
        servers_json = redis_client.get(REDIS_KEY_MCP_SERVERS)

        if servers_json:
            try:
                return json.loads(servers_json)
            except json.JSONDecodeError:
                return []

        return []

# ################################################################################################################################

    @classmethod
    def save_servers(cls, servers:'anylist') -> 'None':
        """ Saves the list of MCP servers to Redis.
        """
        redis_client = get_redis_client()
        redis_client.set(REDIS_KEY_MCP_SERVERS, json.dumps(servers))

# ################################################################################################################################

    @classmethod
    def add_server_from_endpoint(cls, endpoint:'str', auth_type:'str'='none',
                                  auth_data:'anydict | None'=None) -> 'anydict':
        """ Adds an MCP server by fetching its info from the endpoint.
        Returns the server config or error dict.
        """
        server_id = str(uuid.uuid4())[:8]
        temp_client = MCPClient(server_id, endpoint, auth_type, auth_data)

        server_info = temp_client.get_server_info()
        name = server_info.get('name', '')

        if not name:
            error_msg = server_info.get('error', 'Could not get server name from endpoint')
            return {'error': error_msg}

        servers = cls.get_servers()

        for server in servers:
            if server.get('endpoint') == endpoint:
                return {'error': 'Server with this endpoint already exists'}

        server_config = {
            'id': server_id,
            'endpoint': endpoint,
            'name': name,
            'auth_type': auth_type,
            'auth_data': auth_data or {},
            'enabled': True
        }

        servers.append(server_config)
        cls.save_servers(servers)
        logger.info('MCP server added: %s (%s)', name, endpoint)
        return {'success': True, 'server': server_config}

# ################################################################################################################################

    @classmethod
    def remove_server(cls, server_id:'str') -> 'bool':
        """ Removes an MCP server from the registry.
        """
        servers = cls.get_servers()
        new_servers = [s for s in servers if s.get('id') != server_id]

        if len(new_servers) == len(servers):
            return False

        cls.save_servers(new_servers)
        logger.info('MCP server removed: %s', server_id)
        return True

# ################################################################################################################################

    @classmethod
    def update_server(cls, server_id:'str', updates:'anydict') -> 'bool':
        """ Updates an MCP server configuration.
        """
        servers = cls.get_servers()

        for server in servers:
            if server.get('id') == server_id:
                server.update(updates)
                cls.save_servers(servers)
                logger.info('MCP server updated: %s', server_id)
                return True

        return False

# ################################################################################################################################

    @classmethod
    def get_client(cls, server_id:'str') -> 'MCPClient | None':
        """ Returns an MCP client instance for a server.
        """
        servers = cls.get_servers()

        for server in servers:
            if server.get('id') == server_id and server.get('enabled'):
                endpoint = server.get('endpoint', '')
                auth_type = server.get('auth_type', 'none')
                auth_data = server.get('auth_data', {})
                return MCPClient(server_id, endpoint, auth_type, auth_data)

        return None

# ################################################################################################################################

    @classmethod
    def get_all_clients(cls) -> 'list':
        """ Returns MCP client instances for all enabled servers.
        """
        clients = []
        servers = cls.get_servers()

        for server in servers:
            if server.get('enabled'):
                server_id = server.get('id')
                client = cls.get_client(server_id)
                if client:
                    clients.append(client)

        return clients

# ################################################################################################################################

    @classmethod
    def get_all_tools(cls) -> 'anylist':
        """ Returns all tools from all enabled MCP servers.
        """
        all_tools = []
        clients = cls.get_all_clients()

        for client in clients:
            try:
                tools = client.get_tools()
                for tool in tools:
                    tool['_mcp_server_id'] = client.server_id
                all_tools.extend(tools)
            except Exception as e:
                logger.warning('Failed to get tools from %s: %s', client.server_id, e)

        return all_tools

# ################################################################################################################################
# ################################################################################################################################

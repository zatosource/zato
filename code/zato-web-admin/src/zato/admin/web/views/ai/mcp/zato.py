# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.admin.web.views.ai.mcp.base import AuthType, BaseMCPClient

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ZatoMCPClient(BaseMCPClient):
    """ MCP client for Zato MCP server.
    """

    server_id = 'zato'
    server_name = 'Zato'
    auth_type = AuthType.NoAuth

    def __init__(self, endpoint:'str'='https://zato.io/mcp', auth_data:'anydict | None'=None) -> 'None':
        super().__init__(endpoint, auth_data)

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        """ Returns list of tools available from Zato MCP server.
        """
        try:
            response = self._http_get(self.endpoint)
            tools = response.get('tools', [])
            logger.info('Zato MCP tools: %d tools available', len(tools))
            return tools
        except Exception as e:
            logger.warning('Failed to get Zato MCP tools: %s', e)
            return []

# ################################################################################################################################

    def invoke_tool(self, tool_name:'str', arguments:'anydict') -> 'any_':
        """ Invokes a tool on the Zato MCP server.
        """
        try:
            data = {
                'tool': tool_name,
                'arguments': arguments
            }
            response = self._http_post(self.endpoint, data)
            logger.info('Zato MCP tool %s invoked: %s', tool_name, response)
            return response
        except Exception as e:
            logger.warning('Failed to invoke Zato MCP tool %s: %s', tool_name, e)
            return {'error': str(e)}

# ################################################################################################################################
# ################################################################################################################################

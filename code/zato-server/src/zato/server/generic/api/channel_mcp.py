# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.mcp.handler import MCPHandler
from zato.server.connection.mcp.registry import ToolRegistry
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.bunch import Bunch
    from zato.common.typing_ import any_, strlist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapper:
    """ Holds configuration for an MCP channel, including tool registry and JSON-RPC handler.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        self.handler:'MCPHandler | None' = None

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        """ Initializes the tool registry and handler based on the channel's configuration.
        """

        # The allowed services list is already a top-level key in config,
        # extracted from opaque1 by GenericConnection.to_dict during startup.
        allowed_services:'strlist' = self.config.get('services', [])

        # .. build the tool registry ..
        tool_registry = ToolRegistry(self.server.service_store, allowed_services)

        # .. build the session manager ..
        session_manager = MCPSessionManager()

        # .. build the handler with an invoke function that calls services through the server.
        self.handler = MCPHandler(tool_registry, self._invoke_service, session_manager)

        service_suffix = 'service' if len(allowed_services) == 1 else 'services'
        sorted_services = sorted(allowed_services)
        logger.info('MCP channel `%s` built with %d allowed %s: %s', self.config.name, len(allowed_services), service_suffix, sorted_services)

# ################################################################################################################################

    def _invoke_service(self, service_name:'str', payload:'any_') -> 'any_':
        """ Invokes a Zato service by name and returns its response.
        """

        out = self.server.invoke(service_name, payload)
        return out

# ################################################################################################################################

    def delete(self) -> 'None':
        """ Cleans up when the channel is being removed.
        """
        self.handler = None
        logger.info('MCP channel `%s` deleted', self.config.name)

# ################################################################################################################################
# ################################################################################################################################

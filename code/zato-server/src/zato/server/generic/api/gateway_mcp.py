# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler
from zato.server.connection.mcp.registry import ToolRegistry
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, strlist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class GatewayMCPWrapper:
    """ Holds configuration for an MCP gateway, including tool registry and JSON-RPC handler.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        self.handler:'MCPHandler | None' = None
        self._audit_log:'AuditLog | None' = None

# ################################################################################################################################

    def get_audit_log(self) -> 'AuditLog':
        """ Returns this wrapper's audit log, created on first use so gateways that never
        audit never touch the audit database. The engine behind it is process-wide and cached.
        """

        if self._audit_log is None:
            self._audit_log = AuditLog(self.server.name)

        out = self._audit_log
        return out

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        """ Initializes the tool registry and handler based on the gateway's configuration.
        """

        # The allowed services list is already a top-level key in config,
        # extracted from opaque1 by GenericConnection.to_dict during startup.
        allowed_services:'strlist' = self.config.get('services', [])

        # .. build the tool registry and populate it. This is safe because MCP gateways
        # are only created after all services are deployed ..
        tool_registry = ToolRegistry(self.server.service_store, allowed_services)
        tool_registry.rebuild()

        # .. build the session manager ..
        session_manager = MCPSessionManager()

        # .. response shaping configs come from the same flat gateway config -
        # editing the gateway rebuilds this wrapper, so changes apply without a restart ..
        safeguard_config = build_safeguard_config(self.config)
        token_cap_config = build_token_cap_config(self.config)

        # .. argument validation is on for gateways whose form saved it -
        # configs predating the field lack the key, which means it is off ..
        validate_input = self.config.get('validate_input')
        if validate_input is None:
            validate_input = False

        # .. build the handler with an invoke function that calls services through the server.
        self.handler = MCPHandler(
            tool_registry, self._invoke_service, session_manager, safeguard_config, token_cap_config, validate_input)

        service_suffix = 'service' if len(allowed_services) == 1 else 'services'
        sorted_services = sorted(allowed_services)
        logger.info('MCP gateway `%s` built with %d allowed %s: %s', self.config.name, len(allowed_services), service_suffix, sorted_services)

# ################################################################################################################################

    def _invoke_service(self, service_name:'str', payload:'any_') -> 'any_':
        """ Invokes a Zato service by name and returns its response.
        """

        out = self.server.invoke(service_name, payload)
        return out

# ################################################################################################################################

    def delete(self) -> 'None':
        """ Cleans up when the gateway is being removed.
        """
        self.handler = None
        logger.info('MCP gateway `%s` deleted', self.config.name)

# ################################################################################################################################
# ################################################################################################################################

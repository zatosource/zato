# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import partial
from logging import getLogger

# Zato
from zato.common.api import MCP
from zato.common.audit_log.api import AuditLog
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid
from zato.common.util.logging_ import count_text
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.connection_tools.api import group_registry
from zato.server.connection.mcp.handler import MCPHandler
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.registry import ToolRegistry
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, stranydict, strlist, strlistdict
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
        self.tool_registry:'ToolRegistry | None' = None
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

        # .. the connection allow lists live under one config key per group -
        # configs predating a group lack its key, which means an empty list ..
        connection_lists:'strlistdict' = {}

        for definition in group_registry.values():

            if (connection_names := self.config.get(definition.config_key)) is None:
                connection_names = []

            connection_lists[definition.group] = connection_names

        # .. build the tool registry and populate it. This is safe because MCP gateways
        # are only created after all services are deployed ..
        tool_registry = ToolRegistry(self.server.service_store, allowed_services, connection_lists, self.server.config_manager)
        tool_registry.rebuild()
        self.tool_registry = tool_registry

        # .. build the session manager - a per-gateway idle TTL overrides the default,
        # configs predating the field lack the key and zero means the default too ..
        session_ttl = self.config.get('session_ttl')

        if session_ttl:
            session_manager = MCPSessionManager(ttl=session_ttl)
        else:
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

        # .. the same applies to agent-supplied JSONata response filters ..
        allow_agent_filters = self.config.get('allow_agent_filters')
        if allow_agent_filters is None:
            allow_agent_filters = False

        # .. the skills this gateway serves as prompts - a config without the key serves none,
        # and the files themselves are read from the server's config/repo/skills on each request ..
        allowed_skills:'strlist | None' = self.config.get('skills')
        if allowed_skills is None:
            allowed_skills = []

        skill_prompts = SkillPrompts(self.server.repo_location, allowed_skills)

        # .. how long one tools/call invocation may run for - configs predating the field
        # lack the key and zero means the default too ..
        if not (invoke_timeout := self.config.get('invoke_timeout')):
            invoke_timeout = MCP.Default_Invoke_Timeout

        # .. the hook services, invoked by name for every message and every reply - configs predating
        # the fields lack the keys and an empty name means no hook ..
        request_hook_func = None
        response_hook_func = None

        if request_hook_service := self.config.get('request_hook_service'):
            request_hook_func = partial(self._invoke_request_hook, request_hook_service)

        if response_hook_service := self.config.get('response_hook_service'):
            response_hook_func = partial(self._invoke_response_hook, response_hook_service)

        # .. build the handler with an invoke function that calls services through the server,
        # introducing the gateway to MCP clients under its public name.
        self.handler = MCPHandler(
            tool_registry, self._invoke_service, session_manager, safeguard_config, token_cap_config, validate_input,
            skill_prompts, self.config.public_name, allow_agent_filters, invoke_timeout, request_hook_func,
            response_hook_func)

        service_count_text = count_text(len(allowed_services), 'allowed service', 'allowed services')
        sorted_services = sorted(allowed_services)
        logger.info('MCP gateway `%s` built with %s: %s', self.config.name, service_count_text, sorted_services)

        skill_count_text = count_text(len(allowed_skills), 'skill', 'skills')
        sorted_skills = sorted(allowed_skills)
        logger.info('MCP gateway `%s` serves %s as prompts: %s', self.config.name, skill_count_text, sorted_skills)

        if request_hook_service or response_hook_service:
            logger.info('MCP gateway `%s` hook services: request `%s`, response `%s`',
                self.config.name, request_hook_service, response_hook_service)

# ################################################################################################################################

    def _invoke_service(self, service_name:'str', payload:'any_') -> 'any_':
        """ Invokes what stands behind a tool - for connection tools, the connection
        the registry mapped the tool to, for everything else, a Zato service by name.
        """

        tool_registry = cast_('ToolRegistry', self.tool_registry)

        if service_name in tool_registry.tool_targets:
            out = self.invoke_tool(service_name, payload)
        else:
            out = self.server.invoke(service_name, payload)

        return out

# ################################################################################################################################

    def _invoke_request_hook(self, service_name:'str', identity:'str', message:'stranydict') -> 'stranydict':
        """ Invokes the request hook service with one parsed message and returns the message to process -
        the one the service returned under the request key, or the original one when it returned nothing there.
        """
        payload = {
            'gateway': self.config.name,
            'method': message.get('method'),
            'username': identity,
            'request': message,
        }

        out = self._invoke_hook(service_name, payload, 'request', message)
        return out

# ################################################################################################################################

    def _invoke_response_hook(self, service_name:'str', message:'stranydict | None', body:'stranydict') -> 'stranydict':
        """ Invokes the response hook service with one reply body and returns the body to send -
        the one the service returned under the response key, or the original one when it returned nothing there.
        The message is None when the request body never parsed into an object.
        """

        if message is None:
            method = None
        else:
            method = message.get('method')

        payload = {
            'gateway': self.config.name,
            'method': method,
            'request': message,
            'response': body,
        }

        out = self._invoke_hook(service_name, payload, 'response', body)
        return out

# ################################################################################################################################

    def _invoke_hook(self, service_name:'str', payload:'stranydict', key:'str', original:'stranydict') -> 'stranydict':
        """ Invokes a hook service and returns the object it placed under the key, or the original object
        when the service returned no such key. Anything other than an object under the key is refused.
        """

        # The service's response is whatever it produced, unserialized, possibly nothing at all ..
        response = self.server.invoke(service_name, payload, serialize=False)

        # .. a response without the key leaves the original as it was ..
        if not isinstance(response, dict):
            return original

        if key not in response:
            return original

        out = response[key]

        # .. and a replacement has to be an object, as the message or body it replaces is.
        if not isinstance(out, dict):
            raise Exception(f'Hook service `{service_name}` returned a non-object under `{key}`')

        return out

# ################################################################################################################################

    def invoke_tool(self, tool_name:'str', arguments:'stranydict') -> 'any_':
        """ Invokes the connection behind a connection tool, routing through
        the group's own invoke function.
        """

        # What the tool stands for - recorded by the registry's last rebuild ..
        tool_registry = cast_('ToolRegistry', self.tool_registry)
        group, connection_name = tool_registry.tool_targets[tool_name]
        definition = group_registry[group]

        # .. the connection is resolved anew on each call ..
        config_dict = definition.get_config_dict(self.server.config_manager)
        item = config_dict[connection_name]

        # .. and the group's invoke function does the actual call.
        cid = new_cid()

        out = definition.invoke(cid, item, arguments)
        return out

# ################################################################################################################################

    def delete(self) -> 'None':
        """ Cleans up when the gateway is being removed.
        """
        self.handler = None
        self.tool_registry = None
        logger.info('MCP gateway `%s` deleted', self.config.name)

# ################################################################################################################################
# ################################################################################################################################

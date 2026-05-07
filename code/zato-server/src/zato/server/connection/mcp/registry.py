# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.mcp.schema import sio_to_json_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist, strnone, strlist
    from zato.server.service.store import ServiceStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Internal service namespace - services under this prefix are never exposed as MCP tools
_internal_prefix = 'zato.'

# Default page size for tools/list pagination
_default_page_size = 100

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistry:
    """ Builds and caches the MCP tools/list response for a given set of allowed services.
    Each MCP channel has its own ToolRegistry instance with its own allowlist.
    """
    def __init__(self, service_store:'ServiceStore', allowed_services:'strlist') -> 'None':
        self.service_store = service_store
        self.allowed_services = allowed_services
        self._cached_tools:'strdictlist' = []

# ################################################################################################################################

    def get_tools(self) -> 'strdictlist':
        """ Returns the cached tools list.
        """

        out = self._cached_tools
        return out

# ################################################################################################################################

    def rebuild(self) -> 'None':
        """ Rebuilds the cached tools list by scanning the service store
        for each service in the allowlist.
        """

        # Walk through each allowed service name and try to resolve it ..
        tools:'strdictlist' = []

        for service_name in self.allowed_services:

            # Never expose internal services regardless of allowlist contents
            if service_name.startswith(_internal_prefix):
                logger.warning('Skipping internal service `%s` from MCP tool exposure', service_name)
                continue

            # Look up the service in the store ..
            impl_name = self.service_store.name_to_impl_name.get(service_name)

            if impl_name is None:
                logger.info('MCP allowlist contains service `%s` not yet deployed, will retry on hot-deploy', service_name)
                continue

            service_info = self.service_store.services.get(impl_name)

            if service_info is None:
                logger.warning('No service info for impl `%s` (service `%s`), skipping', impl_name, service_name)
                continue

            # .. extract the service class and its metadata ..
            service_class = service_info['service_class']
            description = service_class.__doc__

            if description is None:
                description = ''

            description = description.strip()
            input_schema = sio_to_json_schema(service_class)

            # .. build the MCP tool definition ..
            tool:'stranydict' = {
                'name': service_name,
                'description': description,
                'inputSchema': input_schema,
            }

            tools.append(tool)

        # .. replace the cached tools list with the newly built one.
        self._cached_tools = tools

        tool_suffix = 'tool' if len(tools) == 1 else 'tools'
        logger.info('MCP tool registry built with %d %s', len(tools), tool_suffix)

# ################################################################################################################################

    def get_tools_page(self, cursor:'strnone'=None) -> 'tuple[strdictlist, strnone]':
        """ Returns a page of tools starting from the given cursor.
        The cursor is an opaque string representing the start index.
        Returns (tools_page, next_cursor) where next_cursor is None if no more pages.
        """

        all_tools = self._cached_tools

        # Decode the cursor into a start index ..
        start = 0

        if cursor:
            start = int(cursor)

        # .. slice out the current page ..
        end = start + _default_page_size
        page = all_tools[start:end]

        # .. if there are more tools beyond this page, produce a next cursor ..
        if end < len(all_tools):
            next_cursor = str(end)
        else:
            next_cursor = None

        # .. and return both the page and the cursor for the next one.
        out = (page, next_cursor)
        return out

# ################################################################################################################################

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        """ Checks whether a service name is in the allowlist and is not internal.
        """

        # Internal services are never exposed as MCP tools ..
        if service_name.startswith(_internal_prefix):
            return False

        # .. otherwise check membership in the allowlist.
        out = service_name in self.allowed_services
        return out

# ################################################################################################################################
# ################################################################################################################################

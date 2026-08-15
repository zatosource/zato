# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from operator import itemgetter
from secrets import token_hex

# Zato
from zato.common.util.logging_ import count_text
from zato.server.connection.mcp.common import InvalidCursor
from zato.server.connection.mcp.schema import io_to_json_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strdictlist, strnone, strlist
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

# How many random bytes go into a registry's cursor token
_cursor_token_bytes = 4

# What separates the cursor token from the page index
_cursor_separator = '.'

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistry:
    """ Builds and caches the MCP tools/list response for a given set of allowed services.
    Each MCP gateway has its own ToolRegistry instance with its own allow list.
    """
    def __init__(self, service_store:'ServiceStore', allowed_services:'strlist') -> 'None':
        self.service_store = service_store
        self.allowed_services = allowed_services
        self._cached_tools:'strdictlist' = []
        self._schema_by_name:'stranydict' = {}

        # Cursors are opaque and bound to this registry - a cursor obtained from one
        # gateway is refused by every other one.
        self._cursor_token = token_hex(_cursor_token_bytes)

# ################################################################################################################################

    def get_tools(self) -> 'strdictlist':
        """ Returns the cached tools list.
        """

        out = self._cached_tools
        return out

# ################################################################################################################################

    def rebuild(self) -> 'None':
        """ Rebuilds the cached tools list by scanning the service store
        for each service in the allow list.
        """

        # Walk through each allowed service name and try to resolve it ..
        tools:'strdictlist' = []
        schema_by_name:'stranydict' = {}

        for service_name in self.allowed_services:

            # Never expose internal services regardless of allow list contents
            if service_name.startswith(_internal_prefix):
                logger.info('Skipping internal service `%s` from MCP tool exposure', service_name)
                continue

            # Look up the service in the store ..
            impl_name = self.service_store.name_to_impl_name.get(service_name)

            if impl_name is None:
                raise ValueError(f'MCP allow list references service `{service_name}` which is not deployed')

            service_info = self.service_store.services.get(impl_name)

            if service_info is None:
                raise ValueError(f'No service info for impl `{impl_name}` (service `{service_name}`)')

            # .. extract the service class and its metadata ..
            service_class = service_info['service_class']
            description = service_class.__doc__

            if description is None:
                description = ''

            description = description.strip()
            input_schema = io_to_json_schema(service_class)

            # .. build the MCP tool definition ..
            tool:'stranydict' = {
                'name': service_name,
                'description': description,
                'inputSchema': input_schema,
            }

            tools.append(tool)
            schema_by_name[service_name] = input_schema

        # .. tools are listed in a deterministic order so clients can cache the list ..
        tools.sort(key=itemgetter('name'))

        # .. replace the cached tools list and the schema lookup with the newly built ones.
        self._cached_tools = tools
        self._schema_by_name = schema_by_name

        tool_count_text = count_text(len(tools), 'tool', 'tools')
        logger.info('MCP tool registry built with %s', tool_count_text)

# ################################################################################################################################

    def get_tools_page(self, cursor:'any_'=None) -> 'tuple[strdictlist, strnone]':
        """ Returns a page of tools starting from the given cursor.
        The cursor is an opaque string this registry itself issued - one of another
        registry, or of any other shape, is refused.
        Returns (tools_page, next_cursor) where next_cursor is None if no more pages.
        Raises InvalidCursor if the cursor is not one this registry issued.
        """

        all_tools = self._cached_tools
        total = len(all_tools)

        # Decode the cursor into a start index ..
        if cursor is None:
            start = 0
        else:
            start = self._decode_cursor(cursor)

            # Clamp to the valid range of [0, total]
            upper_bound = min(start, total)
            start = max(0, upper_bound)

        # .. slice out the current page ..
        end = start + _default_page_size
        page = all_tools[start:end]

        # .. if there are more tools beyond this page, produce a next cursor ..
        if end < total:
            next_cursor = f'{self._cursor_token}{_cursor_separator}{end}'
        else:
            next_cursor = None

        # .. and return both the page and the cursor for the next one.
        out = (page, next_cursor)
        return out

# ################################################################################################################################

    def _decode_cursor(self, cursor:'any_') -> 'int':
        """ Returns the start index a cursor carries.
        Raises InvalidCursor unless the cursor holds this registry's own token and an integer index.
        """

        message = f'Invalid cursor value: `{cursor}`'

        # A cursor is not necessarily a string at all - the client controls what it sends
        if not isinstance(cursor, str):
            raise InvalidCursor(message)

        token, separator, index_text = cursor.partition(_cursor_separator)

        # A cursor without the separator never came from any registry
        if not separator:
            raise InvalidCursor(message)

        # A token this registry never issued makes the cursor foreign
        if token != self._cursor_token:
            raise InvalidCursor(message)

        try:
            out = int(index_text)
        except ValueError:
            raise InvalidCursor(message)

        return out

# ################################################################################################################################

    def get_tool_schema(self, service_name:'str') -> 'stranydict':
        """ Returns the cached inputSchema of a tool - only ever called for tools
        that is_tool_allowed accepted, which rebuild is guaranteed to have resolved.
        """

        out = self._schema_by_name[service_name]
        return out

# ################################################################################################################################

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        """ Checks whether a service name is in the allow list and is not internal.
        """

        # Internal services are never exposed as MCP tools ..
        if service_name.startswith(_internal_prefix):
            return False

        # .. otherwise check membership in the allow list.
        out = service_name in self.allowed_services
        return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from abc import ABC, abstractmethod
from logging import getLogger
from traceback import format_exc

# Zato
from zato.admin.web.views.ai.mcp.registry import MCPRegistry
from zato.admin.web.views.ai.llm.execution import get_recent_executions
from zato.admin.web.views.ai.tools.definitions import get_all_tools as get_enmasse_tools, is_delete_tool, is_update_tool
from zato.admin.web.views.ai.tools.executor import execute_enmasse_batch, is_enmasse_tool
from zato.admin.web.views.ai.tools.delete_executor import execute_delete_tool
from zato.admin.web.views.ai.tools.update_executor import execute_update_tool
from zato.common.ai.prompts.loader import get_system_prompt

if 0:
    from zato.common.typing_ import any_, anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

Max_Tool_Iterations = 10

# ################################################################################################################################
# ################################################################################################################################

class BaseLLMClient(ABC):
    """ Base class for LLM clients.
    """

    def __init__(self, api_key:'str', zato_client:'any_'=None, cluster_id:'int'=None, cluster:'any_'=None, session_id:'str'='') -> 'None':
        self.api_key = api_key
        self.zato_client = zato_client
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.session_id = session_id
        self.system_prompt = get_system_prompt()

# ################################################################################################################################

    def _build_execution_history_context(self) -> 'str':
        """ Builds execution history context from Redis for injection into conversation.
        """
        if not self.session_id:
            return ''

        executions = get_recent_executions(self.session_id, limit=20)
        if not executions:
            return ''

        lines = ['Recent tool executions in this session:']
        for execution in executions:
            tool_name = execution.get('tool_name', '')
            success = execution.get('success', False)
            args = execution.get('arguments', {})
            name = args.get('name', '')
            status = 'succeeded' if success else 'failed'
            lines.append(f'- {tool_name}: {name} ({status})')

        lines.append('')
        lines.append('When answering questions about what was created/updated/deleted, refer ONLY to this list.')

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    @abstractmethod
    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses.
        Yields dicts with 'type' and 'content' keys.
        type can be: 'chunk', 'done', 'error'
        """
        pass

# ################################################################################################################################

    def _format_error(self, error:'any_') -> 'dict':
        """ Formats an error response.
        """
        out = {
            'type': 'error',
            'content': str(error)
        }
        return out

# ################################################################################################################################

    def _format_chunk(self, text:'str') -> 'dict':
        """ Formats a text chunk response.
        """
        out = {
            'type': 'chunk',
            'content': text
        }
        return out

# ################################################################################################################################

    def _format_done(self, input_tokens:'int'=0, output_tokens:'int'=0) -> 'dict':
        """ Formats a done response.
        """
        out = {
            'type': 'done',
            'content': '',
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
        return out

# ################################################################################################################################

    def _format_object_changed(self, action:'str', object_id:'any_', object_name:'str'='') -> 'dict':
        """ Formats an object changed event for UI refresh.
        """
        out = {
            'type': 'object_changed',
            'action': action,
            'object_id': object_id,
            'object_name': object_name
        }
        return out

# ################################################################################################################################

    def _get_mcp_tools(self) -> 'anylist':
        """ Gets all tools from enabled MCP servers.
        """
        try:
            return MCPRegistry.get_all_tools()
        except Exception as e:
            logger.warning('Failed to get MCP tools: %s', e)
            return []

# ################################################################################################################################

    def _get_enmasse_tools(self) -> 'anylist':
        """ Gets all enmasse tools.
        """
        tools = get_enmasse_tools()
        out = []
        for tool in tools:
            tool_copy = dict(tool)
            tool_copy['_enmasse_tool'] = True
            out.append(tool_copy)
        return out

# ################################################################################################################################

    def _get_all_tools(self) -> 'anylist':
        """ Gets all available tools (MCP + enmasse).
        """
        mcp_tools = self._get_mcp_tools()
        enmasse_tools = self._get_enmasse_tools()
        return mcp_tools + enmasse_tools

# ################################################################################################################################

    def _categorize_tool_calls(self, tool_calls:'list', get_tool_name:'callable') -> 'tuple':
        """ Categorizes tool calls into enmasse, delete, update, and mcp calls.
        """
        enmasse_calls = []
        delete_calls = []
        update_calls = []
        mcp_calls = []

        for tool_call in tool_calls:
            tool_name = get_tool_name(tool_call)
            if is_enmasse_tool(tool_name):
                enmasse_calls.append(tool_call)
            elif is_delete_tool(tool_name):
                delete_calls.append(tool_call)
            elif is_update_tool(tool_name):
                update_calls.append(tool_call)
            else:
                mcp_calls.append(tool_call)

        return enmasse_calls, delete_calls, update_calls, mcp_calls

# ################################################################################################################################

    def _execute_enmasse_batch(self, batch:'list') -> 'dict':
        """ Executes a batch of enmasse tool calls.
        """
        try:
            batch_result = execute_enmasse_batch(batch)
            logger.info('Enmasse batch result: %s', batch_result)
            return batch_result
        except Exception as e:
            logger.warning('Enmasse batch error: %s', format_exc())
            return {'error': str(e)}

# ################################################################################################################################

    def _execute_delete_tool(self, tool_name:'str', arguments:'dict') -> 'dict':
        """ Executes a delete tool call.
        """
        try:
            delete_result = execute_delete_tool(
                self.zato_client, self.cluster_id, tool_name, arguments
            )
            logger.info('Delete tool %s result: %s', tool_name, delete_result)
            return delete_result
        except Exception as e:
            logger.warning('Delete tool %s error: %s', tool_name, format_exc())
            return {'success': False, 'error': str(e)}

# ################################################################################################################################

    def _execute_update_tool(self, tool_name:'str', arguments:'dict') -> 'dict':
        """ Executes an update tool call.
        """
        try:
            update_result = execute_update_tool(
                self.zato_client, self.cluster_id, self.cluster, tool_name, arguments
            )
            logger.info('Update tool %s result: %s', tool_name, update_result)
            return update_result
        except Exception as e:
            logger.warning('Update tool %s error: %s', tool_name, format_exc())
            return {'success': False, 'error': str(e)}

# ################################################################################################################################

    def _execute_mcp_tool_core(self, tool_name:'str', arguments:'dict', all_tools:'anylist') -> 'dict':
        """ Core MCP tool execution logic.
        """
        tool_def = None
        for tool in all_tools:
            if tool.get('name') == tool_name:
                tool_def = tool
                break

        if not tool_def:
            return {'error': f'Tool {tool_name} not found'}

        server_id = tool_def.get('_mcp_server_id')
        if not server_id:
            return {'error': f'MCP server not found for tool {tool_name}'}

        client = MCPRegistry.get_client(server_id)
        if not client:
            return {'error': f'MCP server {server_id} not available'}

        try:
            result = client.invoke_tool(tool_name, arguments)
            logger.info('MCP tool %s result: %s', tool_name, result)
            return result
        except Exception as e:
            logger.warning('MCP tool %s error: %s', tool_name, format_exc())
            return {'error': str(e)}

# ################################################################################################################################
# ################################################################################################################################

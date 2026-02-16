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
from zato.admin.web.views.ai.llm.execution import build_execution_context
from zato.admin.web.views.ai.tools.definitions import get_all_tools as get_enmasse_tools, is_delete_tool, is_update_tool
from zato.admin.web.views.ai.tools.executor import execute_enmasse_batch, is_enmasse_tool, is_service_tool, execute_service_tool
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

    def _build_execution_history_context(self, question:'str'='') -> 'str':
        """ Builds execution history context from Redis for injection into conversation.
        Uses intent detection to route to state snapshot or event history.
        """
        if not self.session_id:
            return ''

        out = build_execution_context(self.session_id, question)
        return out

# ################################################################################################################################

    def _extract_last_user_message(self, messages:'list') -> 'str':
        """ Extracts the last user message text from the messages list.
        """
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            return part.get('text', '')
                        if isinstance(part, str):
                            return part
        return ''

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

    def _format_object_changed(self, action:'str', object_id:'any_', object_name:'str'='', object_type:'str'='') -> 'dict':
        """ Formats an object changed event for UI refresh.
        """
        out = {
            'type': 'object_changed',
            'action': action,
            'object_id': object_id,
            'object_name': object_name,
            'object_type': object_type
        }
        return out

# ################################################################################################################################

    def _format_tool_progress(self, status:'str', total:'int'=0, completed:'int'=0, message:'str'='', items:'list'=None) -> 'dict':
        """ Formats a tool progress event for UI spinner/progress display.
        status: 'start', 'progress', 'done'
        items: list of dicts with 'type' and 'name' keys for created objects
        """
        out = {
            'type': 'tool_progress',
            'status': status,
            'total': total,
            'completed': completed,
            'message': message
        }
        if items:
            out['items'] = items
        return out

# ################################################################################################################################

    def _get_tool_progress_message(self, tool_names:'list', is_done:'bool'=False) -> 'str':
        """ Generates an appropriate progress message based on tool names.
        """
        if not tool_names:
            return 'Processing...' if not is_done else 'Done'

        create_count = 0
        update_count = 0
        delete_count = 0
        deploy_count = 0
        search_doc = False
        get_doc = False

        for name in tool_names:
            if name.startswith('create_'):
                create_count += 1
            elif name.startswith('update_'):
                update_count += 1
            elif name.startswith('delete_'):
                delete_count += 1
            elif name == 'deploy_service':
                deploy_count += 1
            elif name == 'search_documentation':
                search_doc = True
            elif name == 'get_document_content':
                get_doc = True

        parts = []

        if search_doc:
            parts.append('Searching documentation' if not is_done else 'Searched documentation')
        if get_doc:
            parts.append('Reading documentation' if not is_done else 'Read documentation')
        if deploy_count > 0:
            word = 'service' if deploy_count == 1 else 'services'
            parts.append(f'Deploying {deploy_count} {word}' if not is_done else f'Deployed {deploy_count} {word}')
        if create_count > 0:
            word = 'object' if create_count == 1 else 'objects'
            parts.append(f'Creating {create_count} {word}' if not is_done else f'Created {create_count} {word}')
        if update_count > 0:
            word = 'object' if update_count == 1 else 'objects'
            parts.append(f'Updating {update_count} {word}' if not is_done else f'Updated {update_count} {word}')
        if delete_count > 0:
            word = 'object' if delete_count == 1 else 'objects'
            parts.append(f'Deleting {delete_count} {word}' if not is_done else f'Deleted {delete_count} {word}')

        if not parts:
            return 'Processing...' if not is_done else 'Done'

        msg = ', '.join(parts)
        if not is_done:
            msg += '...'
        return msg

# ################################################################################################################################

    def _yield_tool_progress_start(self, count:'int', tool_names:'list'=None) -> 'generator_':
        """ Yields a tool progress start event.
        """
        msg = self._get_tool_progress_message(tool_names or [], is_done=False)
        yield self._format_tool_progress('start', total=count, completed=0, message=msg)

# ################################################################################################################################

    def _yield_tool_progress_done(self, count:'int', items:'list'=None, tool_names:'list'=None) -> 'generator_':
        """ Yields a tool progress done event followed by a newline chunk.
        items: list of dicts with 'type' and 'name' keys for created objects
        """
        msg = self._get_tool_progress_message(tool_names or [], is_done=True)
        yield self._format_tool_progress('done', total=count, completed=count, message=msg, items=items)
        yield self._format_chunk('\n\n')

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
        """ Categorizes tool calls into enmasse, delete, update, service, and mcp calls.
        """
        enmasse_calls = []
        delete_calls = []
        update_calls = []
        service_calls = []
        mcp_calls = []

        for tool_call in tool_calls:
            tool_name = get_tool_name(tool_call)
            if is_enmasse_tool(tool_name):
                enmasse_calls.append(tool_call)
            elif is_delete_tool(tool_name):
                delete_calls.append(tool_call)
            elif is_update_tool(tool_name):
                update_calls.append(tool_call)
            elif is_service_tool(tool_name):
                service_calls.append(tool_call)
            else:
                mcp_calls.append(tool_call)

        return enmasse_calls, delete_calls, update_calls, service_calls, mcp_calls

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

    def _execute_service_tool(self, tool_name:'str', arguments:'dict') -> 'dict':
        """ Executes a service deployment or deletion tool.
        """
        try:
            service_result = execute_service_tool(tool_name, arguments, self.zato_client)
            logger.info('Service tool %s result: %s', tool_name, service_result)
            return service_result
        except Exception as e:
            logger.warning('Service tool %s error: %s', tool_name, format_exc())
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

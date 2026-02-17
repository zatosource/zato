# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger
from traceback import format_exc

# Zato
from zato.admin.web.views.ai.browser_tools import get_browser_tool_schemas, is_browser_tool
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

Max_Tool_Iterations = 999999

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class CategorizedToolCalls:
    enmasse: 'list' = field(default_factory=list)
    delete: 'list' = field(default_factory=list)
    update: 'list' = field(default_factory=list)
    service: 'list' = field(default_factory=list)
    browser: 'list' = field(default_factory=list)
    mcp: 'list' = field(default_factory=list)

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

    def _format_waiting(self, waiting_type:'str'='') -> 'dict':
        """ Formats a waiting event to show cycling messages on the client.
        """
        out = {
            'type': 'waiting'
        }
        if waiting_type:
            out['waiting_type'] = waiting_type
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

    def _format_tool_preview(self, file_path:'str', code:'str', is_new:'bool'=True) -> 'dict':
        """ Formats a tool preview event for showing file diffs during streaming.
        """
        return {
            'type': 'tool_preview',
            'file_path': file_path,
            'code': code,
            'is_new': is_new
        }

# ################################################################################################################################

    def _extract_file_previews(self, partial_input:'str', already_previewed:'set'):
        """ Extracts complete file entries from partial JSON and yields preview events.
        """
        import re
        import os

        previews = []
        pattern = r'"file_path"\s*:\s*"([^"]+)"\s*,\s*"code"\s*:\s*"((?:[^"\\]|\\.)*)"\s*}'

        for match in re.finditer(pattern, partial_input):
            file_path = match.group(1)
            if file_path in already_previewed:
                continue

            code_escaped = match.group(2)
            try:
                code = code_escaped.encode().decode('unicode_escape')
            except Exception:
                code = code_escaped

            services_root = os.path.expanduser('~/env/qs-1/server1/pickup/code/impl/src/api')
            full_path = os.path.join(services_root, file_path)
            is_new = not os.path.exists(full_path)

            yield self._format_tool_preview(file_path, code, is_new)
            previews.append({'file_path': file_path, 'code': code, 'is_new': is_new})

        return previews

# ################################################################################################################################

    def _get_tool_progress_message(self, tool_names:'list', is_done:'bool'=False, tool_params:'list'=None) -> 'str':
        """ Generates an appropriate progress message based on tool names.
        tool_params: optional list of dicts with tool parameters (same order as tool_names)
        """
        if not tool_names:
            return 'Processing...' if not is_done else 'Done'

        tool_params = tool_params or []
        parts = []

        for i, name in enumerate(tool_names):
            params = tool_params[i] if i < len(tool_params) else {}

            if name.startswith('create_'):
                obj_type = name[7:].replace('_', ' ')
                obj_name = params.get('name', '')
                if obj_name:
                    parts.append(f'Creating {obj_type} "{obj_name}"' if not is_done else f'Created {obj_type} "{obj_name}"')
                else:
                    parts.append(f'Creating {obj_type}' if not is_done else f'Created {obj_type}')

            elif name.startswith('update_'):
                obj_type = name[7:].replace('_', ' ')
                obj_name = params.get('name', '')
                if obj_name:
                    parts.append(f'Updating {obj_type} "{obj_name}"' if not is_done else f'Updated {obj_type} "{obj_name}"')
                else:
                    parts.append(f'Updating {obj_type}' if not is_done else f'Updated {obj_type}')

            elif name.startswith('delete_'):
                obj_type = name[7:].replace('_', ' ')
                obj_name = params.get('name', '')
                if obj_name:
                    parts.append(f'Deleting {obj_type} "{obj_name}"' if not is_done else f'Deleted {obj_type} "{obj_name}"')
                else:
                    parts.append(f'Deleting {obj_type}' if not is_done else f'Deleted {obj_type}')

            elif name == 'deploy_service':
                files = params.get('files', [])
                if files:
                    file_names = [f.get('file_path', '') for f in files if f.get('file_path')]
                    if file_names:
                        names_display = ', '.join(file_names)
                        parts.append(f'Deploying {names_display}' if not is_done else f'Deployed {names_display}')
                    else:
                        parts.append('Deploying service' if not is_done else 'Deployed service')
                else:
                    parts.append('Deploying service' if not is_done else 'Deployed service')

            elif name == 'search_documentation':
                parts.append('Searching documentation' if not is_done else 'Searched documentation')

            elif name == 'get_document_content':
                parts.append('Reading documentation' if not is_done else 'Read documentation')

            elif name == 'search_internet':
                query = params.get('query', '')
                if query:
                    query_display = query[:50] + '...' if len(query) > 50 else query
                    parts.append(f'Searching the internet: "{query_display}"' if not is_done else f'Searched the Internet: "{query_display}"')
                else:
                    parts.append('Searching the internet' if not is_done else 'Searched the internet')

            elif name == 'visit_page':
                url = params.get('url', '')
                if url:
                    url_display = url[:60] + '...' if len(url) > 60 else url
                    url_link = f'<a href="{url}" target="_blank" class="ai-tool-link">{url_display}</a>'
                    parts.append(f'Visiting page: {url_link}' if not is_done else f'Visited page: {url_link}')
                else:
                    parts.append('Visiting page' if not is_done else 'Visited page')

            else:
                parts.append(f'Running {name}' if not is_done else f'Ran {name}')

        if not parts:
            if tool_names:
                tool_display = ', '.join(tool_names)
                return f'Running {tool_display}...' if not is_done else f'Ran {tool_display}'
            return 'Processing...' if not is_done else 'Done'

        msg = ', '.join(parts)
        if not is_done:
            msg += '...'
        return msg

# ################################################################################################################################

    def _yield_tool_progress_start(self, count:'int', tool_names:'list'=None, tool_params:'list'=None) -> 'generator_':
        """ Yields a tool progress start event.
        """
        msg = self._get_tool_progress_message(tool_names or [], is_done=False, tool_params=tool_params)
        yield self._format_tool_progress('start', total=count, completed=0, message=msg)

# ################################################################################################################################

    def _yield_tool_progress_done(self, count:'int', items:'list'=None, tool_names:'list'=None, tool_params:'list'=None) -> 'generator_':
        """ Yields a tool progress done event followed by a newline chunk.
        items: list of dicts with 'type' and 'name' keys for created objects
        """
        msg = self._get_done_summary_message(tool_names or [], tool_params or [], items or [])
        logger.info('[DEPLOY-TRACE] _yield_tool_progress_done emitting msg=%s items=%s', msg, items)
        yield self._format_tool_progress('done', total=count, completed=count, message=msg, items=items)
        yield self._format_chunk('\n\n')

# ################################################################################################################################

    def _get_done_summary_message(self, tool_names:'list', tool_params:'list', items:'list') -> 'str':
        """ Generates a summary message for completed tools like 'Created 5 objects'.
        """
        if not tool_names:
            return 'Done'

        create_count = 0
        update_count = 0
        delete_count = 0
        deploy_parts = []
        search_parts = []
        visit_parts = []
        other_count = 0

        for i, name in enumerate(tool_names):
            params = tool_params[i] if i < len(tool_params) else {}

            if name.startswith('create_'):
                create_count += 1
            elif name.startswith('update_'):
                update_count += 1
            elif name.startswith('delete_'):
                delete_count += 1
            elif name == 'deploy_service':
                deploy_parts.append('deployed')
            elif name == 'search_internet':
                query = params.get('query', '')
                if query:
                    query_display = query[:50] + '...' if len(query) > 50 else query
                    search_parts.append(f'"{query_display}"')
            elif name == 'search_documentation':
                query = params.get('query', '')
                if query:
                    query_display = query[:50] + '...' if len(query) > 50 else query
                    search_parts.append(f'docs: "{query_display}"')
            elif name == 'visit_page':
                url = params.get('url', '')
                if url:
                    url_display = url[:60] + '...' if len(url) > 60 else url
                    url_link = f'<a href="{url}" target="_blank" class="ai-tool-link">{url_display}</a>'
                    visit_parts.append(url_link)
            elif name == 'get_document_content':
                doc_id = params.get('document_id', '')
                if doc_id:
                    visit_parts.append(f'doc:{doc_id[:20]}')
            else:
                other_count += 1

        parts = []

        if create_count > 0:
            word = 'object' if create_count == 1 else 'objects'
            parts.append(f'Created {create_count} {word}')
        if update_count > 0:
            word = 'object' if update_count == 1 else 'objects'
            parts.append(f'Updated {update_count} {word}')
        if deploy_parts:
            parts.append('Deployed')
        if search_parts:
            parts.append(f'Searched {", ".join(search_parts)}')
        if visit_parts:
            parts.append(f'Visited {", ".join(visit_parts)}')
        if other_count > 0:
            word = 'tool' if other_count == 1 else 'tools'
            parts.append(f'Ran {other_count} {word}')

        if not parts:
            return 'Done'

        return ', '.join(parts)

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
        """ Gets all available tools (MCP + enmasse + browser).
        """
        mcp_tools = self._get_mcp_tools()
        enmasse_tools = self._get_enmasse_tools()
        browser_tools = get_browser_tool_schemas()
        return mcp_tools + enmasse_tools + browser_tools

# ################################################################################################################################

    def _categorize_tool_calls(self, tool_calls:'list', get_tool_name:'callable') -> 'CategorizedToolCalls':
        """ Categorizes tool calls into enmasse, delete, update, service, browser, and mcp calls.
        """
        result = CategorizedToolCalls()

        for tool_call in tool_calls:
            tool_name = get_tool_name(tool_call)
            if is_enmasse_tool(tool_name):
                result.enmasse.append(tool_call)
            elif is_delete_tool(tool_name):
                result.delete.append(tool_call)
            elif is_update_tool(tool_name):
                result.update.append(tool_call)
            elif is_service_tool(tool_name):
                result.service.append(tool_call)
            elif is_browser_tool(tool_name):
                result.browser.append(tool_call)
            else:
                result.mcp.append(tool_call)

        return result

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

    def _execute_browser_tool(self, tool_name:'str', arguments:'dict') -> 'generator_':
        """ Executes a browser tool by yielding an SSE event and waiting for Redis response.
        This is a generator that yields SSE events and returns the result.
        """
        from uuid import uuid4
        from zato.admin.web.views.ai.common import get_redis_client
        from zato.common.json_internal import loads

        request_id = uuid4().hex
        redis_key = 'zato.ai.browser-tool.' + request_id

        logger.info('Executing browser tool %s with request_id %s, params: %s', tool_name, request_id, arguments)

        event = {
            'type': 'browser_tool',
            'request_id': request_id,
            'tool_name': tool_name,
            'params': arguments
        }
        yield event

        redis_client = get_redis_client()
        logger.info('Waiting for browser tool result on key %s', redis_key)

        result = redis_client.blpop(redis_key, timeout=60)

        if result is None:
            logger.warning('Browser tool %s timed out after 60 seconds', tool_name)
            return {'success': False, 'error': 'Browser tool timed out after 60 seconds'}

        _, result_json = result
        result_data = loads(result_json)

        redis_client.delete(redis_key)

        logger.info('Browser tool %s completed with result: %s', tool_name, result_data)

        return result_data

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

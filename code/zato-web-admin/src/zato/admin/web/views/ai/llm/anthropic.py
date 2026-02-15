# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from traceback import format_exc
from urllib.request import Request, urlopen

# Zato
from zato.admin.web.views.ai.llm.base import BaseLLMClient
from zato.admin.web.views.ai.mcp.registry import MCPRegistry
from zato.admin.web.views.ai.tools.definitions import get_tools_by_name
from zato.admin.web.views.ai.tools import executor as enmasse_executor

if 0:
    from zato.common.typing_ import anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL = 'https://api.anthropic.com/v1/messages'
API_Version = '2023-06-01'
Max_Tool_Iterations = 10

# ################################################################################################################################
# ################################################################################################################################

class AnthropicClient(BaseLLMClient):
    """ Client for Anthropic Claude API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from Anthropic with MCP and enmasse tool support.
        """
        enmasse_tool_names = self._select_enmasse_tools(model, messages)
        all_tools = self._get_all_tools(enmasse_tool_names)
        anthropic_tools = self._convert_tools_to_anthropic_format(all_tools)

        working_messages = list(messages)
        total_input_tokens = 0
        total_output_tokens = 0

        for iteration in range(Max_Tool_Iterations):
            result = yield from self._stream_single_request(
                model, working_messages, anthropic_tools
            )

            total_input_tokens += result.get('input_tokens', 0)
            total_output_tokens += result.get('output_tokens', 0)

            if result.get('error'):
                return

            tool_calls = result.get('tool_calls', [])
            if not tool_calls:
                yield self._format_done(total_input_tokens, total_output_tokens)
                return

            assistant_content = result.get('assistant_content', [])
            working_messages.append({'role': 'assistant', 'content': assistant_content})

            tool_results = []
            for tool_call in tool_calls:
                tool_result = self._execute_tool(tool_call, all_tools)
                tool_results.append({
                    'type': 'tool_result',
                    'tool_use_id': tool_call['id'],
                    'content': json.dumps(tool_result)
                })

            working_messages.append({'role': 'user', 'content': tool_results})

        yield self._format_done(total_input_tokens, total_output_tokens)

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

    def _get_enmasse_tools(self, tool_names:'anylist') -> 'anylist':
        """ Gets enmasse tools by name.
        """
        tools = get_tools_by_name(tool_names)
        out = []
        for tool in tools:
            tool_copy = dict(tool)
            tool_copy['_enmasse_tool'] = True
            out.append(tool_copy)
        return out

# ################################################################################################################################

    def _get_all_tools(self, enmasse_tool_names:'anylist'=None) -> 'anylist':
        """ Gets all available tools (MCP + selected enmasse).
        """
        mcp_tools = self._get_mcp_tools()
        if enmasse_tool_names:
            enmasse_tools = self._get_enmasse_tools(enmasse_tool_names)
        else:
            enmasse_tools = []
        return mcp_tools + enmasse_tools

# ################################################################################################################################

    def _select_enmasse_tools(self, model:'str', messages:'list') -> 'anylist':
        """ Asks the LLM which enmasse tools are needed for this request.
        """
        if not self.tool_selection_prompt:
            return []

        last_user_message = ''
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '')
                break

        if not last_user_message:
            return []

        selection_messages = [
            {'role': 'user', 'content': last_user_message}
        ]

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': API_Version,
        }

        body = {
            'model': model,
            'max_tokens': 256,
            'system': self.tool_selection_prompt,
            'messages': selection_messages,
        }

        body_json = json.dumps(body)
        body_bytes = body_json.encode('utf-8')

        try:
            request = Request(API_URL, data=body_bytes, headers=headers, method='POST')
            with urlopen(request) as response:
                response_data = json.loads(response.read().decode('utf-8'))

            content = response_data.get('content', [])
            if content and content[0].get('type') == 'text':
                text = content[0].get('text', '').strip()
                tool_names = json.loads(text)
                if isinstance(tool_names, list):
                    logger.info('Selected enmasse tools: %s', tool_names)
                    return tool_names
        except Exception as e:
            logger.warning('Tool selection failed: %s', e)

        return []

# ################################################################################################################################

    def _convert_tools_to_anthropic_format(self, mcp_tools:'anylist') -> 'anylist':
        """ Converts MCP tools to Anthropic tool format.
        """
        anthropic_tools = []

        for tool in mcp_tools:
            anthropic_tool = {
                'name': tool.get('name', ''),
                'description': tool.get('description', ''),
                'input_schema': tool.get('parameters', tool.get('input_schema', {'type': 'object', 'properties': {}}))
            }
            anthropic_tools.append(anthropic_tool)

        return anthropic_tools

# ################################################################################################################################

    def _execute_tool(self, tool_call:'dict', all_tools:'anylist') -> 'dict':
        """ Executes a tool call via MCP or enmasse.
        """
        tool_name = tool_call.get('name', '')
        arguments = tool_call.get('input', {})

        tool_def = None
        for tool in all_tools:
            if tool.get('name') == tool_name:
                tool_def = tool
                break

        if not tool_def:
            return {'error': f'Tool {tool_name} not found'}

        is_enmasse = tool_def.get('_enmasse_tool', False)

        if is_enmasse:
            try:
                result = enmasse_executor.execute_enmasse_tool(tool_name, arguments)
                logger.info('Enmasse tool %s result: %s', tool_name, result)
                return result
            except Exception as e:
                logger.warning('Enmasse tool %s error: %s', tool_name, format_exc())
                return {'error': str(e)}

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

    def _stream_single_request(self, model:'str', messages:'list', tools:'anylist') -> 'generator_':
        """ Makes a single streaming request to Anthropic API.
        """
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': API_Version,
        }

        body = {
            'model': model,
            'max_tokens': 4096,
            'stream': True,
            'messages': messages,
        }

        if self.system_prompt:
            body['system'] = self.system_prompt

        if tools:
            body['tools'] = tools

        body_json = json.dumps(body)
        body_bytes = body_json.encode('utf-8')

        logger.info('Anthropic request: model=%s messages=%s tools=%d', model, json.dumps(messages, indent=2), len(tools))

        request = Request(API_URL, data=body_bytes, headers=headers, method='POST')

        input_tokens = 0
        output_tokens = 0
        tool_calls = []
        assistant_content = []
        current_tool_call = None

        try:
            with urlopen(request) as response:
                for line in response:
                    line = line.decode('utf-8').strip()

                    if not line:
                        continue

                    if not line.startswith('data: '):
                        continue

                    data_str = line[6:]

                    if data_str == '[DONE]':
                        return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'tool_calls': tool_calls, 'assistant_content': assistant_content}

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = data.get('type', '')

                    logger.info('Anthropic event: %s data=%s', event_type, data_str)

                    if event_type == 'message_start':
                        message = data.get('message', {})
                        usage = message.get('usage', {})
                        input_tokens = usage.get('input_tokens', 0)
                        logger.info('Anthropic input_tokens: %d', input_tokens)

                    elif event_type == 'message_delta':
                        usage = data.get('usage', {})
                        output_tokens = usage.get('output_tokens', 0)
                        logger.info('Anthropic output_tokens: %d', output_tokens)

                    elif event_type == 'content_block_start':
                        content_block = data.get('content_block', {})
                        block_type = content_block.get('type', '')

                        if block_type == 'tool_use':
                            current_tool_call = {
                                'id': content_block.get('id', ''),
                                'name': content_block.get('name', ''),
                                'input': {}
                            }
                            assistant_content.append({
                                'type': 'tool_use',
                                'id': current_tool_call['id'],
                                'name': current_tool_call['name'],
                                'input': {}
                            })
                        elif block_type == 'text':
                            assistant_content.append({'type': 'text', 'text': ''})

                    elif event_type == 'content_block_delta':
                        delta = data.get('delta', {})
                        delta_type = delta.get('type', '')

                        if delta_type == 'text_delta':
                            text = delta.get('text', '')
                            if text:
                                if assistant_content and assistant_content[-1].get('type') == 'text':
                                    assistant_content[-1]['text'] += text
                                chunk = self._format_chunk(text)
                                yield chunk

                        elif delta_type == 'input_json_delta':
                            partial_json = delta.get('partial_json', '')
                            if current_tool_call is not None:
                                if 'partial_input' not in current_tool_call:
                                    current_tool_call['partial_input'] = ''
                                current_tool_call['partial_input'] += partial_json

                    elif event_type == 'content_block_stop':
                        if current_tool_call is not None:
                            partial = current_tool_call.get('partial_input', '{}')
                            try:
                                current_tool_call['input'] = json.loads(partial)
                            except json.JSONDecodeError:
                                current_tool_call['input'] = {}

                            for item in assistant_content:
                                if item.get('type') == 'tool_use' and item.get('id') == current_tool_call['id']:
                                    item['input'] = current_tool_call['input']
                                    break

                            tool_calls.append(current_tool_call)
                            current_tool_call = None

                    elif event_type == 'message_stop':
                        logger.info('Anthropic complete: input_tokens=%d output_tokens=%d tool_calls=%d',
                                    input_tokens, output_tokens, len(tool_calls))
                        return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'tool_calls': tool_calls, 'assistant_content': assistant_content}

                    elif event_type == 'error':
                        error_data = data.get('error', {})
                        error_msg = error_data.get('message', 'Unknown error')
                        error_response = self._format_error(error_msg)
                        yield error_response
                        return {'error': True}

        except Exception as e:
            logger.warning('Anthropic API error: %s', format_exc())
            yield self._format_error(e)
            return {'error': True}

        return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'tool_calls': tool_calls, 'assistant_content': assistant_content}

# ################################################################################################################################
# ################################################################################################################################

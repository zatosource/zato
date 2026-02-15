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
from zato.admin.web.views.ai.tools.definitions import get_all_tools as get_enmasse_tools
from zato.admin.web.views.ai.tools.executor import execute_enmasse_batch, is_enmasse_tool

if 0:
    from zato.common.typing_ import anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL = 'https://api.openai.com/v1/chat/completions'
Max_Tool_Iterations = 10

# ################################################################################################################################
# ################################################################################################################################

class OpenAIClient(BaseLLMClient):
    """ Client for OpenAI GPT API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from OpenAI with tool support.
        """
        all_tools = self._get_all_tools()
        openai_tools = self._convert_tools_to_openai_format(all_tools)

        working_messages = list(messages)
        total_input_tokens = 0
        total_output_tokens = 0

        for iteration in range(Max_Tool_Iterations):
            result = yield from self._stream_single_request(
                model, working_messages, openai_tools
            )

            total_input_tokens += result.get('input_tokens', 0)
            total_output_tokens += result.get('output_tokens', 0)

            if result.get('error'):
                return

            tool_calls = result.get('tool_calls', [])
            if not tool_calls:
                yield self._format_done(total_input_tokens, total_output_tokens)
                return

            assistant_content = result.get('assistant_content', '')
            working_messages.append({
                'role': 'assistant',
                'content': assistant_content,
                'tool_calls': tool_calls
            })

            tool_messages = self._execute_tools_batched(tool_calls, all_tools)
            working_messages.extend(tool_messages)

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

    def _convert_tools_to_openai_format(self, tools:'anylist') -> 'anylist':
        """ Converts tools to OpenAI function calling format.
        """
        openai_tools = []

        for tool in tools:
            openai_tool = {
                'type': 'function',
                'function': {
                    'name': tool.get('name', ''),
                    'description': tool.get('description', ''),
                    'parameters': tool.get('parameters', tool.get('input_schema', {'type': 'object', 'properties': {}}))
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

# ################################################################################################################################

    def _execute_tools_batched(self, tool_calls:'list', all_tools:'anylist') -> 'list':
        """ Executes tool calls, batching enmasse tools together.
        """
        enmasse_calls = []
        mcp_calls = []

        for tool_call in tool_calls:
            function = tool_call.get('function', {})
            tool_name = function.get('name', '')
            if is_enmasse_tool(tool_name):
                enmasse_calls.append(tool_call)
            else:
                mcp_calls.append(tool_call)

        tool_messages = []

        if enmasse_calls:
            batch = []
            for tc in enmasse_calls:
                function = tc.get('function', {})
                tool_name = function.get('name', '')
                arguments_str = function.get('arguments', '{}')
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    arguments = {}
                batch.append((tool_name, arguments))

            try:
                batch_result = execute_enmasse_batch(batch)
                logger.info('Enmasse batch result: %s', batch_result)
            except Exception as e:
                logger.warning('Enmasse batch error: %s', format_exc())
                batch_result = {'error': str(e)}

            for tool_call in enmasse_calls:
                tool_messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call['id'],
                    'content': json.dumps(batch_result)
                })

        for tool_call in mcp_calls:
            tool_result = self._execute_mcp_tool(tool_call, all_tools)
            tool_messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': json.dumps(tool_result)
            })

        return tool_messages

# ################################################################################################################################

    def _execute_mcp_tool(self, tool_call:'dict', all_tools:'anylist') -> 'dict':
        """ Executes a single MCP tool call.
        """
        function = tool_call.get('function', {})
        tool_name = function.get('name', '')
        arguments_str = function.get('arguments', '{}')

        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}

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

    def _stream_single_request(self, model:'str', messages:'list', tools:'anylist') -> 'generator_':
        """ Makes a single streaming request to OpenAI API.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        api_messages = list(messages)
        if self.system_prompt:
            api_messages.insert(0, {'role': 'system', 'content': self.system_prompt})

        body = {
            'model': model,
            'stream': True,
            'messages': api_messages,
        }

        if tools:
            body['tools'] = tools

        body_json = json.dumps(body)
        body_bytes = body_json.encode('utf-8')

        logger.info('OpenAI request: model=%s messages=%d tools=%d', model, len(messages), len(tools))

        request = Request(API_URL, data=body_bytes, headers=headers, method='POST')

        input_tokens = 0
        output_tokens = 0
        tool_calls = []
        current_tool_calls = {}
        assistant_content = ''

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
                        for idx in sorted(current_tool_calls.keys()):
                            tc = current_tool_calls[idx]
                            tool_calls.append({
                                'id': tc.get('id', ''),
                                'type': 'function',
                                'function': {
                                    'name': tc.get('name', ''),
                                    'arguments': tc.get('arguments', '{}')
                                }
                            })
                        return {
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'tool_calls': tool_calls,
                            'assistant_content': assistant_content
                        }

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    usage = data.get('usage', {})
                    if usage:
                        input_tokens = usage.get('prompt_tokens', input_tokens)
                        output_tokens = usage.get('completion_tokens', output_tokens)

                    choices = data.get('choices', [])
                    if not choices:
                        continue

                    first_choice = choices[0]
                    delta = first_choice.get('delta', {})

                    content = delta.get('content', '')
                    if content:
                        assistant_content += content
                        chunk = self._format_chunk(content)
                        yield chunk

                    delta_tool_calls = delta.get('tool_calls', [])
                    for tc in delta_tool_calls:
                        idx = tc.get('index', 0)
                        if idx not in current_tool_calls:
                            current_tool_calls[idx] = {
                                'id': tc.get('id', ''),
                                'name': '',
                                'arguments': ''
                            }
                        if tc.get('id'):
                            current_tool_calls[idx]['id'] = tc['id']
                        func = tc.get('function', {})
                        if func.get('name'):
                            current_tool_calls[idx]['name'] = func['name']
                        if func.get('arguments'):
                            current_tool_calls[idx]['arguments'] += func['arguments']

                    finish_reason = first_choice.get('finish_reason')
                    if finish_reason in ('stop', 'tool_calls'):
                        for idx in sorted(current_tool_calls.keys()):
                            tc = current_tool_calls[idx]
                            tool_calls.append({
                                'id': tc.get('id', ''),
                                'type': 'function',
                                'function': {
                                    'name': tc.get('name', ''),
                                    'arguments': tc.get('arguments', '{}')
                                }
                            })
                        return {
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'tool_calls': tool_calls,
                            'assistant_content': assistant_content
                        }

        except Exception as e:
            logger.warning('OpenAI API error: %s', format_exc())
            yield self._format_error(e)
            return {'error': True}

        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'tool_calls': tool_calls,
            'assistant_content': assistant_content
        }

# ################################################################################################################################
# ################################################################################################################################

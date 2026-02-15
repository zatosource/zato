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
from zato.admin.web.views.ai.tools.executor import execute_enmasse_tool

if 0:
    from zato.common.typing_ import anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL_Template = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}'
Max_Tool_Iterations = 10

# ################################################################################################################################
# ################################################################################################################################

class GoogleClient(BaseLLMClient):
    """ Client for Google Gemini API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from Google Gemini with tool support.
        """
        all_tools = self._get_all_tools()
        gemini_tools = self._convert_tools_to_gemini_format(all_tools)

        working_messages = list(messages)
        total_input_tokens = 0
        total_output_tokens = 0

        for iteration in range(Max_Tool_Iterations):
            result = yield from self._stream_single_request(
                model, working_messages, gemini_tools
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
            working_messages.append({'role': 'assistant', 'parts': assistant_content})

            tool_response_parts = []
            for tool_call in tool_calls:
                tool_result = self._execute_tool(tool_call, all_tools)
                tool_response_parts.append({
                    'functionResponse': {
                        'name': tool_call['name'],
                        'response': tool_result
                    }
                })

            working_messages.append({'role': 'user', 'parts': tool_response_parts})

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
        """ Gets all enmasse tools for creating Zato objects.
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

    def _convert_tools_to_gemini_format(self, tools:'anylist') -> 'list':
        """ Converts tools to Gemini function declaration format.
        """
        if not tools:
            return []

        function_declarations = []

        for tool in tools:
            schema = tool.get('parameters', tool.get('input_schema', {'type': 'object', 'properties': {}}))
            func_decl = {
                'name': tool.get('name', ''),
                'description': tool.get('description', ''),
                'parameters': schema
            }
            function_declarations.append(func_decl)

        return [{'functionDeclarations': function_declarations}]

# ################################################################################################################################

    def _execute_tool(self, tool_call:'dict', all_tools:'anylist') -> 'dict':
        """ Executes a tool call via MCP or enmasse.
        """
        tool_name = tool_call.get('name', '')
        arguments = tool_call.get('args', {})

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
                result = execute_enmasse_tool(tool_name, arguments)
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

    def _stream_single_request(self, model:'str', messages:'list', tools:'list') -> 'generator_':
        """ Makes a single streaming request to Google Gemini API.
        """
        url = API_URL_Template.format(model=model, api_key=self.api_key)

        headers = {
            'Content-Type': 'application/json',
        }

        contents = self._convert_messages(messages)

        body = {
            'contents': contents,
        }

        if tools:
            body['tools'] = tools

        body_json = json.dumps(body)
        body_bytes = body_json.encode('utf-8')

        logger.info('Gemini request: model=%s messages=%d tools=%d', model, len(messages), len(tools))

        request = Request(url, data=body_bytes, headers=headers, method='POST')

        input_tokens = 0
        output_tokens = 0
        tool_calls = []
        assistant_content = []

        try:
            with urlopen(request) as response:
                for line in response:
                    line = line.decode('utf-8').strip()

                    if not line:
                        continue

                    if not line.startswith('data: '):
                        continue

                    data_str = line[6:]

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    usage = data.get('usageMetadata', {})
                    if usage:
                        input_tokens = usage.get('promptTokenCount', input_tokens)
                        output_tokens = usage.get('candidatesTokenCount', output_tokens)

                    candidates = data.get('candidates', [])
                    if not candidates:
                        continue

                    first_candidate = candidates[0]
                    content = first_candidate.get('content', {})
                    parts = content.get('parts', [])

                    for part in parts:
                        text = part.get('text', '')
                        if text:
                            assistant_content.append({'text': text})
                            chunk = self._format_chunk(text)
                            yield chunk

                        function_call = part.get('functionCall')
                        if function_call:
                            tool_calls.append({
                                'name': function_call.get('name', ''),
                                'args': function_call.get('args', {})
                            })
                            assistant_content.append({'functionCall': function_call})

                    finish_reason = first_candidate.get('finishReason')
                    if finish_reason in ('STOP', 'TOOL_CODE'):
                        return {
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'tool_calls': tool_calls,
                            'assistant_content': assistant_content
                        }

        except Exception as e:
            logger.warning('Google Gemini API error: %s', format_exc())
            yield self._format_error(e)
            return {'error': True}

        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'tool_calls': tool_calls,
            'assistant_content': assistant_content
        }

# ################################################################################################################################

    def _convert_messages(self, messages:'list') -> 'list':
        """ Converts OpenAI-style messages to Gemini format.
        """
        out = []

        for msg in messages:
            role = msg.get('role', 'user')

            if role == 'assistant':
                role = 'model'

            parts = msg.get('parts')
            if parts:
                out.append({'role': role, 'parts': parts})
            else:
                content = msg.get('content', '')
                out.append({
                    'role': role,
                    'parts': [{'text': content}]
                })

        return out

# ################################################################################################################################
# ################################################################################################################################

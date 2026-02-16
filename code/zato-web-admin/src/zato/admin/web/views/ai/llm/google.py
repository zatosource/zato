# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from urllib.request import Request, urlopen

# Zato
from zato.admin.web.views.ai.llm.base import BaseLLMClient, Max_Tool_Iterations
from zato.admin.web.views.ai.llm.execution import ExecutionLog

if 0:
    from zato.common.typing_ import anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL_Template = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}'

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
        execution_log = ExecutionLog()

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
                break

            assistant_content = result.get('assistant_content', [])
            working_messages.append({'role': 'assistant', 'parts': assistant_content})

            yield from self._yield_tool_progress_start(len(tool_calls))

            records_before = len(execution_log.records)
            tool_response_parts = self._execute_tools_batched(tool_calls, all_tools, execution_log)
            working_messages.append({'role': 'user', 'parts': tool_response_parts})

            new_records = execution_log.records[records_before:]
            new_items = []
            for record in new_records:
                if record.success and record.action:
                    new_items.append({
                        'type': execution_log._format_object_type(record.model_name),
                        'name': record.object_name
                    })
            yield from self._yield_tool_progress_done(len(tool_calls), items=new_items)

        if execution_log.records:
            object_changes = execution_log.get_object_changes()
            for change in object_changes:
                yield self._format_object_changed(change['action'], change['object_id'], change['object_name'], change['object_type'])

            if self.session_id:
                execution_log.persist(self.session_id)

        yield self._format_done(total_input_tokens, total_output_tokens)

# ################################################################################################################################

    def _extract_response_text(self, assistant_content:'list') -> 'str':
        """ Extracts text from assistant content parts. """
        parts = []
        for part in assistant_content:
            if isinstance(part, dict) and 'text' in part:
                parts.append(part.get('text', ''))
        return ' '.join(parts)

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

    def _execute_tools_batched(self, tool_calls:'list', all_tools:'anylist', execution_log:'ExecutionLog') -> 'list':
        """ Executes tool calls, batching enmasse tools together.
        Records all executions in execution_log for ground-truth injection.
        Returns tool_response_parts for conversation.
        """
        def get_tool_name(tc):
            return tc.get('name', '')

        enmasse_calls, delete_calls, update_calls, service_calls, mcp_calls = self._categorize_tool_calls(tool_calls, get_tool_name)
        tool_response_parts = []

        for tool_call in service_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('args', {})
            service_result = self._execute_service_tool(tool_name, arguments)
            tool_response_parts.append({
                'functionResponse': {
                    'name': tool_call['name'],
                    'response': service_result
                }
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=service_result,
                success=service_result.get('success', False),
                error=service_result.get('error')
            )

        if enmasse_calls:
            batch = [(tc.get('name'), tc.get('args', {})) for tc in enmasse_calls]
            batch_result = self._execute_enmasse_batch(batch)
            for tool_call in enmasse_calls:
                tool_response_parts.append({
                    'functionResponse': {
                        'name': tool_call['name'],
                        'response': batch_result
                    }
                })
                execution_log.add(
                    tool_name=tool_call.get('name', ''),
                    arguments=tool_call.get('args', {}),
                    result=batch_result,
                    success=batch_result.get('success', False),
                    error=batch_result.get('error')
                )

        for tool_call in delete_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('args', {})
            delete_result = self._execute_delete_tool(tool_name, arguments)
            tool_response_parts.append({
                'functionResponse': {
                    'name': tool_call['name'],
                    'response': delete_result
                }
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=delete_result,
                success=delete_result.get('success', False),
                error=delete_result.get('error')
            )

        for tool_call in update_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('args', {})
            update_result = self._execute_update_tool(tool_name, arguments)
            tool_response_parts.append({
                'functionResponse': {
                    'name': tool_call['name'],
                    'response': update_result
                }
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=update_result,
                success=update_result.get('success', False),
                error=update_result.get('error')
            )

        for tool_call in mcp_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('args', {})
            tool_result = self._execute_mcp_tool_core(tool_name, arguments, all_tools)
            tool_response_parts.append({
                'functionResponse': {
                    'name': tool_call['name'],
                    'response': tool_result
                }
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=tool_result,
                success='error' not in tool_result,
                error=tool_result.get('error')
            )

        return tool_response_parts

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

        if self.system_prompt:
            system_prompt = self.system_prompt
            user_question = self._extract_last_user_message(messages)
            execution_history = self._build_execution_history_context(user_question)
            if execution_history:
                system_prompt = system_prompt + '\n\n' + execution_history
            body['systemInstruction'] = {
                'parts': [{'text': system_prompt}]
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

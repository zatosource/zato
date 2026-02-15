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

API_URL = 'https://api.openai.com/v1/chat/completions'

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
        execution_log = ExecutionLog()

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
                break

            assistant_content = result.get('assistant_content', '')
            working_messages.append({
                'role': 'assistant',
                'content': assistant_content,
                'tool_calls': tool_calls
            })

            tool_messages = self._execute_tools_batched(tool_calls, all_tools, execution_log)
            working_messages.extend(tool_messages)

        if execution_log.records:
            object_changes = execution_log.get_object_changes()
            for change in object_changes:
                yield self._format_object_changed(change['action'], change['object_id'], change['object_name'])

            ground_truth = execution_log.build_ground_truth_message()
            working_messages.append({'role': 'user', 'content': ground_truth})
            logger.info('Injected ground-truth execution log with %d records', len(execution_log.records))

            result = yield from self._stream_single_request(model, working_messages, [])
            total_input_tokens += result.get('input_tokens', 0)
            total_output_tokens += result.get('output_tokens', 0)

            response_text = result.get('assistant_content', '')
            issues = execution_log.verify_response(response_text)
            if issues:
                logger.warning('Response verification failed: %s', issues)
                correction = '\n\n---\n' + execution_log.build_deterministic_response()
                yield self._format_chunk(correction)

            if self.session_id:
                execution_log.persist(self.session_id)

        yield self._format_done(total_input_tokens, total_output_tokens)

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

    def _execute_tools_batched(self, tool_calls:'list', all_tools:'anylist', execution_log:'ExecutionLog') -> 'list':
        """ Executes tool calls, batching enmasse tools together.
        Records all executions in execution_log for ground-truth injection.
        Returns tool_messages for conversation.
        """
        def get_tool_name(tc):
            return tc.get('function', {}).get('name', '')

        def parse_arguments(tc):
            arguments_str = tc.get('function', {}).get('arguments', '{}')
            try:
                return json.loads(arguments_str)
            except json.JSONDecodeError:
                return {}

        enmasse_calls, delete_calls, update_calls, mcp_calls = self._categorize_tool_calls(tool_calls, get_tool_name)
        tool_messages = []

        if enmasse_calls:
            batch = [(get_tool_name(tc), parse_arguments(tc)) for tc in enmasse_calls]
            batch_result = self._execute_enmasse_batch(batch)
            for tool_call in enmasse_calls:
                tool_messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call['id'],
                    'content': json.dumps(batch_result)
                })
                execution_log.add(
                    tool_name=get_tool_name(tool_call),
                    arguments=parse_arguments(tool_call),
                    result=batch_result,
                    success=batch_result.get('success', False),
                    error=batch_result.get('error')
                )

        for tool_call in delete_calls:
            tool_name = get_tool_name(tool_call)
            arguments = parse_arguments(tool_call)
            delete_result = self._execute_delete_tool(tool_name, arguments)
            tool_messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': json.dumps(delete_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=delete_result,
                success=delete_result.get('success', False),
                error=delete_result.get('error')
            )

        for tool_call in update_calls:
            tool_name = get_tool_name(tool_call)
            arguments = parse_arguments(tool_call)
            update_result = self._execute_update_tool(tool_name, arguments)
            tool_messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': json.dumps(update_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=update_result,
                success=update_result.get('success', False),
                error=update_result.get('error')
            )

        for tool_call in mcp_calls:
            tool_name = get_tool_name(tool_call)
            arguments = parse_arguments(tool_call)
            tool_result = self._execute_mcp_tool_core(tool_name, arguments, all_tools)
            tool_messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': json.dumps(tool_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=tool_result,
                success='error' not in tool_result,
                error=tool_result.get('error')
            )

        return tool_messages

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
            system_prompt = self.system_prompt
            user_question = self._extract_last_user_message(messages)
            execution_history = self._build_execution_history_context(user_question)
            if execution_history:
                system_prompt = system_prompt + '\n\n' + execution_history
            api_messages.insert(0, {'role': 'system', 'content': system_prompt})

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

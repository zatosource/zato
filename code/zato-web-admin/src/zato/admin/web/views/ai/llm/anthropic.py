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
from zato.admin.web.views.ai.llm.base import BaseLLMClient, Max_Tool_Iterations
from zato.admin.web.views.ai.llm.execution import ExecutionLog

if 0:
    from zato.common.typing_ import anylist, generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL = 'https://api.anthropic.com/v1/messages'
API_Version = '2023-06-01'

# ################################################################################################################################
# ################################################################################################################################

class AnthropicClient(BaseLLMClient):
    """ Client for Anthropic Claude API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from Anthropic with MCP and enmasse tool support.
        """
        all_tools = self._get_all_tools()
        anthropic_tools = self._convert_tools_to_anthropic_format(all_tools)

        working_messages = list(messages)
        total_input_tokens = 0
        total_output_tokens = 0
        execution_log = ExecutionLog()

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
                break

            assistant_content = result.get('assistant_content', [])
            working_messages.append({'role': 'assistant', 'content': assistant_content})

            yield from self._yield_tool_progress_start(len(tool_calls))

            records_before = len(execution_log.records)
            tool_results = self._execute_tools_batched(tool_calls, all_tools, execution_log)
            working_messages.append({'role': 'user', 'content': tool_results})

            new_records = execution_log.records[records_before:]
            new_items = []
            for record in new_records:
                if record.success and record.action:
                    new_items.append({
                        'type': execution_log._format_object_type(record.model_name),
                        'name': record.object_name
                    })
            logger.info('Tool progress done items: %s', new_items)
            yield from self._yield_tool_progress_done(len(tool_calls), items=new_items)

        if execution_log.records:
            object_changes = execution_log.get_object_changes()
            logger.info('Object changes to yield: %s', object_changes)
            for change in object_changes:
                event = self._format_object_changed(change['action'], change['object_id'], change['object_name'], change['object_type'])
                logger.info('Yielding object_changed event: %s', event)
                yield event

            if self.session_id:
                execution_log.persist(self.session_id)

        yield self._format_done(total_input_tokens, total_output_tokens)

# ################################################################################################################################

    def _extract_response_text(self, assistant_content:'list') -> 'str':
        """ Extracts text from assistant content blocks. """
        parts = []
        for block in assistant_content:
            if isinstance(block, dict) and block.get('type') == 'text':
                parts.append(block.get('text', ''))
        return ' '.join(parts)

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

    def _execute_tools_batched(self, tool_calls:'list', all_tools:'anylist', execution_log:'ExecutionLog') -> 'list':
        """ Executes tool calls, batching enmasse tools together.
        Records all executions in execution_log for ground-truth injection.
        Returns tool_results for conversation.
        """
        def get_tool_name(tc):
            return tc.get('name', '')

        enmasse_calls, delete_calls, update_calls, service_calls, mcp_calls = self._categorize_tool_calls(tool_calls, get_tool_name)
        tool_results = []

        if enmasse_calls:
            batch = [(tc.get('name'), tc.get('input', {})) for tc in enmasse_calls]
            batch_result = self._execute_enmasse_batch(batch)
            for tool_call in enmasse_calls:
                tool_results.append({
                    'type': 'tool_result',
                    'tool_use_id': tool_call['id'],
                    'content': json.dumps(batch_result)
                })
                execution_log.add(
                    tool_name=tool_call.get('name', ''),
                    arguments=tool_call.get('input', {}),
                    result=batch_result,
                    success=batch_result.get('success', False),
                    error=batch_result.get('error')
                )

        for tool_call in delete_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('input', {})
            delete_result = self._execute_delete_tool(tool_name, arguments)
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_call['id'],
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
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('input', {})
            update_result = self._execute_update_tool(tool_name, arguments)
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_call['id'],
                'content': json.dumps(update_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=update_result,
                success=update_result.get('success', False),
                error=update_result.get('error')
            )

        for tool_call in service_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('input', {})
            service_result = self._execute_service_tool(tool_name, arguments)
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_call['id'],
                'content': json.dumps(service_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=service_result,
                success=service_result.get('success', False),
                error=service_result.get('error')
            )

        for tool_call in mcp_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('input', {})
            tool_result = self._execute_mcp_tool_core(tool_name, arguments, all_tools)
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_call['id'],
                'content': json.dumps(tool_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=tool_result,
                success='error' not in tool_result,
                error=tool_result.get('error')
            )

        return tool_results

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
            system_prompt = self.system_prompt
            user_question = self._extract_last_user_message(messages)
            execution_history = self._build_execution_history_context(user_question)
            if execution_history:
                system_prompt = system_prompt + '\n\n' + execution_history
            body['system'] = system_prompt

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

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
from zato.admin.web.views.ai.browser_tools import is_browser_tool
from zato.admin.web.views.ai.llm.base import BaseLLMClient, Max_Tool_Iterations
from zato.admin.web.views.ai.llm.execution import ExecutionLog
from zato.admin.web.views.ai.llm.guidance import select_guidance_for_message

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

            if result.get('retry'):
                yield self._format_chunk('Continuing with LLM...\n\n')
                yield self._format_waiting()
                result = yield from self._stream_single_request(
                    model, working_messages, anthropic_tools
                )
                if result.get('retry'):
                    yield self._format_chunk('LLM is temporarily unavailable. Please try again.\n')
                    return

            total_input_tokens += result.get('input_tokens', 0)
            total_output_tokens += result.get('output_tokens', 0)

            if result.get('error'):
                return

            tool_calls = result.get('tool_calls', [])
            if not tool_calls:
                break

            assistant_content = result.get('assistant_content', [])
            working_messages.append({'role': 'assistant', 'content': assistant_content})

            non_browser_calls = [tc for tc in tool_calls if not is_browser_tool(tc.get('name', ''))]

            records_before = len(execution_log.records)
            tool_results, browser_calls = self._execute_tools_batched(tool_calls, all_tools, execution_log)

            for browser_call in browser_calls:
                browser_tool_name = browser_call.get('name', '')
                browser_arguments = browser_call.get('input', {})
                browser_result = yield from self._execute_browser_tool(browser_tool_name, browser_arguments)
                yield from self._yield_tool_progress_done(1, items=[], tool_names=[browser_tool_name], tool_params=[browser_arguments])
                tool_results.append({
                    'type': 'tool_result',
                    'tool_use_id': browser_call['id'],
                    'content': json.dumps(browser_result)
                })
                execution_log.add(
                    tool_name=browser_tool_name,
                    arguments=browser_arguments,
                    result=browser_result,
                    success=browser_result.get('success', False),
                    error=browser_result.get('error')
                )

            working_messages.append({'role': 'user', 'content': tool_results})

            if non_browser_calls:
                new_records = execution_log.records[records_before:]
                new_items = []
                successful_names = []
                successful_params = []
                for record in new_records:
                    if record.success:
                        if record.action:
                            item = {
                                'type': execution_log._format_object_type(record.model_name),
                                'name': record.object_name
                            }
                            if record.tool_name == 'deploy_service':
                                item['old_content'] = record.old_content
                                item['new_content'] = record.new_content
                                item['is_new'] = record.is_new
                            new_items.append(item)
                        for tc in non_browser_calls:
                            if tc.get('name', '') == record.tool_name:
                                if tc.get('name', '') not in successful_names:
                                    successful_names.append(tc.get('name', ''))
                                    successful_params.append(tc.get('input', {}))
                                break
                if successful_names:
                    logger.info('[DEPLOY-TRACE] _yield_tool_progress_done called with successful_names=%s new_items=%s', successful_names, new_items)
                    yield from self._yield_tool_progress_done(len(successful_names), items=new_items, tool_names=successful_names, tool_params=successful_params)

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

        categorized = self._categorize_tool_calls(tool_calls, get_tool_name)
        tool_results = []

        for tool_call in categorized.service:
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

        if categorized.enmasse:
            batch = [(tc.get('name'), tc.get('input', {})) for tc in categorized.enmasse]
            batch_result = self._execute_enmasse_batch(batch)
            for tool_call in categorized.enmasse:
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

        for tool_call in categorized.delete:
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

        for tool_call in categorized.update:
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

        for tool_call in categorized.mcp:
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

        return tool_results, categorized.browser

# ################################################################################################################################

    def _stream_single_request(self, model:'str', messages:'list', tools:'anylist') -> 'generator_':
        """ Makes a single streaming request to Anthropic API.
        """
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': API_Version,
            'anthropic-beta': 'prompt-caching-2024-07-31',
        }

        # Inject ephemeral guidance after last user message
        user_question = self._extract_last_user_message(messages)
        guidance = select_guidance_for_message(user_question)

        messages_with_guidance = list(messages)
        if guidance:
            messages_with_guidance.append({'role': 'user', 'content': guidance})

        body = {
            'model': model,
            'max_tokens': 16384,
            'stream': True,
            'messages': messages_with_guidance,
        }

        if self.system_prompt:
            system_prompt = self.system_prompt
            execution_history = self._build_execution_history_context(user_question)
            if execution_history:
                system_prompt = system_prompt + '\n\n' + execution_history
            body['system'] = [
                {
                    'type': 'text',
                    'text': system_prompt,
                    'cache_control': {'type': 'ephemeral'}
                }
            ]

        if tools:
            cached_tools = []
            for i, tool in enumerate(tools):
                cached_tool = dict(tool)
                if i == len(tools) - 1:
                    cached_tool['cache_control'] = {'type': 'ephemeral'}
                cached_tools.append(cached_tool)
            body['tools'] = cached_tools

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
                            if current_tool_call['name'] == 'deploy_service':
                                yield self._format_waiting('code')
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
                                    current_tool_call['previewed_files'] = set()
                                current_tool_call['partial_input'] += partial_json

                                if current_tool_call.get('name') == 'deploy_service':
                                    previews = yield from self._extract_file_previews(
                                        current_tool_call['partial_input'],
                                        current_tool_call['previewed_files']
                                    )
                                    for preview in previews:
                                        current_tool_call['previewed_files'].add(preview['file_path'])

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

                            yield from self._yield_tool_progress_start(1, tool_names=[current_tool_call['name']], tool_params=[current_tool_call['input']])

                            tool_calls.append(current_tool_call)
                            current_tool_call = None

                    elif event_type == 'message_stop':
                        logger.info('Anthropic complete: input_tokens=%d output_tokens=%d tool_calls=%d',
                                    input_tokens, output_tokens, len(tool_calls))
                        return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'tool_calls': tool_calls, 'assistant_content': assistant_content}

                    elif event_type == 'error':
                        error_data = data.get('error', {})
                        error_msg = error_data.get('message', 'Unknown error')
                        logger.warning('Anthropic API error event: %s', error_msg)
                        return {'retry': True}

        except Exception as e:
            logger.warning('Anthropic API error: %s', format_exc())
            return {'retry': True}

        return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'tool_calls': tool_calls, 'assistant_content': assistant_content}

# ################################################################################################################################
# ################################################################################################################################

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
from zato.admin.web.views.ai.browser_tools import is_browser_tool
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

            non_browser_calls = [tc for tc in tool_calls if not is_browser_tool(tc.get('function', {}).get('name', ''))]

            records_before = len(execution_log.records)
            tool_messages, browser_calls = self._execute_tools_batched(tool_calls, all_tools, execution_log)

            for browser_call in browser_calls:
                browser_tool_name = browser_call.get('function', {}).get('name', '')
                browser_arguments = json.loads(browser_call.get('function', {}).get('arguments', '{}'))
                browser_result = yield from self._execute_browser_tool(browser_tool_name, browser_arguments)
                yield from self._yield_tool_progress_done(1, items=[], tool_names=[browser_tool_name], tool_params=[browser_arguments])
                tool_messages.append({
                    'role': 'tool',
                    'tool_call_id': browser_call['id'],
                    'content': json.dumps(browser_result)
                })
                execution_log.add(
                    tool_name=browser_tool_name,
                    arguments=browser_arguments,
                    result=browser_result,
                    success=browser_result.get('success', False),
                    error=browser_result.get('error')
                )

            working_messages.extend(tool_messages)

            all_succeeded = all(
                json.loads(tm.get('content', '{}')).get('success', False)
                for tm in tool_messages
                if tm.get('role') == 'tool'
            )

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
                            tc_name = tc.get('function', {}).get('name', '')
                            if tc_name == record.tool_name:
                                if tc_name not in successful_names:
                                    successful_names.append(tc_name)
                                    successful_params.append(json.loads(tc.get('function', {}).get('arguments', '{}')))
                                break
                if successful_names:
                    yield from self._yield_tool_progress_done(len(successful_names), items=new_items, tool_names=successful_names, tool_params=successful_params)

            if all_succeeded:
                break

        if execution_log.records:
            object_changes = execution_log.get_object_changes()
            for change in object_changes:
                yield self._format_object_changed(change['action'], change['object_id'], change['object_name'], change['object_type'])

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

        categorized = self._categorize_tool_calls(tool_calls, get_tool_name)
        tool_messages = []

        service_failed = False
        service_error = ''
        for tool_call in categorized.service:
            tool_name = get_tool_name(tool_call)
            arguments = parse_arguments(tool_call)
            service_result = self._execute_service_tool(tool_name, arguments)
            tool_messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': json.dumps(service_result)
            })
            execution_log.add(
                tool_name=tool_name,
                arguments=arguments,
                result=service_result,
                success=service_result.get('success', False),
                error=service_result.get('error')
            )
            if not service_result.get('success', False):
                service_failed = True
                service_error = service_result.get('error', 'Unknown error')

        if categorized.enmasse and service_failed:
            error_msg = f'Service deployment failed: {service_error}'
            for tool_call in categorized.enmasse:
                tool_messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call['id'],
                    'content': json.dumps({'success': False, 'error': error_msg})
                })
                execution_log.add(
                    tool_name=get_tool_name(tool_call),
                    arguments=parse_arguments(tool_call),
                    result={'success': False, 'error': error_msg},
                    success=False,
                    error=error_msg
                )
        elif categorized.enmasse:
            batch = [(get_tool_name(tc), parse_arguments(tc)) for tc in categorized.enmasse]
            batch_result = self._execute_enmasse_batch(batch)
            for tool_call in categorized.enmasse:
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

        for tool_call in categorized.delete:
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

        for tool_call in categorized.update:
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

        for tool_call in categorized.mcp:
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

        return tool_messages, categorized.browser

# ################################################################################################################################

    def _stream_single_request(self, model:'str', messages:'list', tools:'anylist') -> 'generator_':
        """ Makes a single streaming request to OpenAI API.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        api_messages = list(messages)
        user_question = self._extract_last_user_message(messages)

        if self.system_prompt:
            api_messages.insert(0, {'role': 'system', 'content': self.system_prompt})

        execution_history = self._build_execution_history_context(user_question)
        if execution_history:
            api_messages.append({'role': 'user', 'content': execution_history})

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
                        is_new_tool = idx not in current_tool_calls
                        if is_new_tool:
                            current_tool_calls[idx] = {
                                'id': tc.get('id', ''),
                                'name': '',
                                'arguments': '',
                                'previewed_files': set()
                            }
                        if tc.get('id'):
                            current_tool_calls[idx]['id'] = tc['id']
                        func = tc.get('function', {})
                        if func.get('name'):
                            current_tool_calls[idx]['name'] = func['name']
                        if func.get('arguments'):
                            current_tool_calls[idx]['arguments'] += func['arguments']

                        if current_tool_calls[idx].get('name') == 'deploy_service':
                            previews = yield from self._extract_file_previews(
                                current_tool_calls[idx]['arguments'],
                                current_tool_calls[idx]['previewed_files']
                            )
                            for preview in previews:
                                current_tool_calls[idx]['previewed_files'].add(preview['file_path'])

                    finish_reason = first_choice.get('finish_reason')
                    if finish_reason in ('stop', 'tool_calls'):
                        for idx in sorted(current_tool_calls.keys()):
                            tc = current_tool_calls[idx]
                            try:
                                parsed_args = json.loads(tc.get('arguments', '{}'))
                            except json.JSONDecodeError:
                                parsed_args = {}
                            yield from self._yield_tool_progress_start(1, tool_names=[tc.get('name', '')], tool_params=[parsed_args])
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

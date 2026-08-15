# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps, loads

# requests
import requests

# local
import _diag
from containers import Model_Name, Ollama_OpenAI_URL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _client import MCPClient
    from _client_stateless import MCPStatelessClient
    from zato.common.typing_ import any_, anydict, callable_, dictlist, strnone

    MCPClient = MCPClient
    MCPStatelessClient = MCPStatelessClient

# ################################################################################################################################
# ################################################################################################################################

# MCP tool names carry dots but the chat completions API only accepts word characters in function
# names, so tools travel to the model with this separator in place of each dot and back again.
_dot_replacement = '__'

# How many completion rounds one task may take - each round is either tool calls or the final answer
_max_turns = 8

# How long to wait for one chat completion, in seconds - a large model on modest
# hardware takes its time, so this is generous on purpose
_completion_timeout = 900

# The model answers deterministically so the assertions on its behavior are repeatable
_temperature = 0

# What the model is told once the turn bound is hit and only a text answer remains -
# a system message, so a test's own system instructions cannot outrank the stop order
_finalize_instruction = (
    'The tool phase is over and no tools are available anymore - any further tool call fails. '
    'State the outcome so far in plain text.')

# How many closing completions a model that keeps asking for withdrawn tools is granted
_max_finalize_turns = 3

# What a tool call made after the tools were withdrawn is answered with
_no_tools_error = 'Error: no tools are available anymore'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ToolCall:
    """ One tool call the model made and what the gateway answered.
    """
    tool_name: 'str'
    arguments: 'anydict'
    result_text: 'str'
    is_error: 'bool'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AgentResult:
    """ The outcome of one agent conversation - the final answer, every tool call made along the way
    and the full message transcript for assertions.
    """
    final_text: 'str'
    tool_calls: 'list[ToolCall]'
    messages: 'dictlist'
    session_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _tools_for_model(mcp_tools:'dictlist') -> 'dictlist':
    """ Converts MCP tool definitions into the tools parameter of the chat completions API.
    """
    out:'dictlist' = []

    for tool in mcp_tools:

        function_name = tool['name'].replace('.', _dot_replacement)

        out.append({
            'type': 'function',
            'function': {
                'name': function_name,
                'description': tool['description'],
                'parameters': tool['inputSchema'],
            },
        })

    return out

# ################################################################################################################################

def _chat_completion(messages:'dictlist', tools:'dictlist', model:'str', ollama_url:'str') -> 'anydict':
    """ Sends one chat completion request and returns the assistant message it produced.
    A request without tools is how the loop asks for a plain text answer once the turn bound is hit.
    """
    body = {
        'model': model,
        'messages': messages,
        'temperature': _temperature,
    }

    if tools:
        body['tools'] = tools

    _diag.write_entry('chat_request', body)

    response = requests.post(
        f'{ollama_url}/chat/completions', data=dumps(body), headers={'Content-Type': 'application/json'},
        timeout=_completion_timeout)

    if not response.ok:
        raise Exception(f'Chat completion failed with HTTP {response.status_code}: {response.text}')

    completion = response.json()

    _diag.write_entry('chat_response', completion)

    out = completion['choices'][0]['message']
    return out

# ################################################################################################################################

def _execute_tool_call(client:'MCPClient', session_id:'str', function_name:'str', arguments:'anydict') -> 'ToolCall':
    """ Executes one tool call the model asked for against the MCP gateway
    and returns both what was called and what came back.
    """

    tool_name = function_name.replace(_dot_replacement, '.')

    params = {'name': tool_name, 'arguments': arguments}
    response = client.jsonrpc('tools/call', params=params, session_id=session_id)
    body = response.json()

    # Our response to produce
    out = ToolCall()
    out.tool_name = tool_name
    out.arguments = arguments

    # A JSON-RPC error, e.g. invalid params, is reported to the model as text so it can react ..
    if 'error' in body:
        error = body['error']
        out.result_text = f'Error {error["code"]}: {error["message"]}'
        out.is_error = True
        return out

    # .. and so is a tool-level error, e.g. a refused or failed response.
    result = body['result']
    out.result_text = result['content'][0]['text']
    out.is_error = bool(result.get('isError'))

    return out

# ################################################################################################################################

def _run_loop(
    execute_call:'callable_',
    mcp_tools:'dictlist',
    task:'str',
    system_text:'strnone',
    model:'str',
    ollama_url:'str',
    max_turns:'int',
    transform_arguments:'any_',
    ) -> 'AgentResult':
    """ The conversation loop both revisions share - the model gets the task and the tools,
    every tool call it makes runs through the given executor, and the loop ends with the
    model's final answer. A conversation that hits the turn bound gets one more completion
    without tools, so the final answer is always a plain text message.
    """

    tools = _tools_for_model(mcp_tools)

    # The conversation starts with the optional system context and the task itself
    messages:'dictlist' = []

    if system_text:
        messages.append({'role': 'system', 'content': system_text})

    messages.append({'role': 'user', 'content': task})

    # Our response to produce
    out = AgentResult()
    out.tool_calls = []
    out.session_id = ''
    out.final_text = ''

    has_final_answer = False

    for _turn in range(max_turns):

        assistant_message = _chat_completion(messages, tools, model, ollama_url)
        messages.append(assistant_message)

        tool_calls = assistant_message.get('tool_calls')

        # No tool calls means this is the final answer and the conversation is over
        if not tool_calls:
            content = assistant_message['content']
            if content is None:
                content = ''
            out.final_text = content
            has_final_answer = True
            break

        # Every tool call runs against the gateway and its result goes back to the model
        for call in tool_calls:

            function = call['function']
            arguments = function['arguments']

            # The API delivers arguments as a JSON string, Ollama sometimes as a parsed object already
            if isinstance(arguments, str):
                arguments = loads(arguments)

            if transform_arguments is not None:
                tool_name = function['name'].replace(_dot_replacement, '.')
                arguments = transform_arguments(tool_name, arguments)

                # The transcript must show the arguments the gateway actually received -
                # a model whose history says one thing while the error reports another
                # cannot reconcile the two and spirals instead of reacting.
                function['arguments'] = dumps(arguments)

            executed = execute_call(function['name'], arguments)
            out.tool_calls.append(executed)

            messages.append({
                'role': 'tool',
                'tool_call_id': call['id'],
                'content': executed.result_text,
            })

    # A conversation that spent every turn on tool calls still owes its caller an answer -
    # the model is told the tools are gone and completions without them
    # make it state the outcome in plain text.
    if not has_final_answer:

        messages.append({'role': 'system', 'content': _finalize_instruction})

        for _finalize_turn in range(_max_finalize_turns):

            assistant_message = _chat_completion(messages, [], model, ollama_url)
            messages.append(assistant_message)

            tool_calls = assistant_message.get('tool_calls')

            # A model may still ask for a tool it no longer has - the call is refused
            # without reaching the gateway and the model is asked once more.
            if tool_calls:
                for call in tool_calls:
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': call['id'],
                        'content': _no_tools_error,
                    })
                continue

            content = assistant_message['content']
            if content is None:
                content = ''
            out.final_text = content
            break

    out.messages = messages
    return out

# ################################################################################################################################

def run_agent(
    client:'MCPClient',
    task:'str',
    system_text:'strnone' = None,
    model:'str' = Model_Name,
    ollama_url:'str' = Ollama_OpenAI_URL,
    max_turns:'int' = _max_turns,
    transform_arguments:'any_' = None,
    ) -> 'AgentResult':
    """ Plays the MCP host role end to end - reads the gateway's tools, gives them to the model
    together with the task, executes every tool call the model makes, feeds the results back
    and returns the full conversation once the model produces its final answer.

    The optional transform_arguments callable receives each call's tool name and arguments
    and returns the arguments to actually send - the tests use it to hand the gateway
    arguments other than what the model asked for and to watch how the model reacts
    to the resulting error.
    """

    # One session covers the whole conversation
    session_id = client.initialize().session_id

    # The gateway's tools become the model's tools
    tools_response = client.jsonrpc('tools/list', session_id=session_id)
    mcp_tools = tools_response.json()['result']['tools']

    def execute_call(function_name:'str', arguments:'anydict') -> 'ToolCall':
        out = _execute_tool_call(client, session_id, function_name, arguments)
        return out

    out = _run_loop(execute_call, mcp_tools, task, system_text, model, ollama_url, max_turns, transform_arguments)
    out.session_id = session_id
    return out

# ################################################################################################################################

def _execute_stateless_tool_call(client:'MCPStatelessClient', function_name:'str', arguments:'anydict') -> 'ToolCall':
    """ Executes one tool call of the stateless revision - the Mcp-Method and Mcp-Name
    headers travel with it and there is no session anywhere.
    """

    tool_name = function_name.replace(_dot_replacement, '.')

    response = client.tools_call(tool_name, arguments)
    body = response.json()

    # Our response to produce
    out = ToolCall()
    out.tool_name = tool_name
    out.arguments = arguments

    # A JSON-RPC error is reported to the model as text so it can react ..
    if 'error' in body:
        error = body['error']
        out.result_text = f'Error {error["code"]}: {error["message"]}'
        out.is_error = True
        return out

    # .. and so is a tool-level error.
    result = body['result']
    out.result_text = result['content'][0]['text']
    out.is_error = bool(result.get('isError'))

    return out

# ################################################################################################################################

def run_agent_stateless(
    client:'MCPStatelessClient',
    task:'str',
    system_text:'strnone' = None,
    model:'str' = Model_Name,
    ollama_url:'str' = Ollama_OpenAI_URL,
    max_turns:'int' = _max_turns,
    tools_from_discover:'bool' = False,
    ) -> 'AgentResult':
    """ The same host role over the stateless revision - no initialize, no session,
    each request self-contained. The tool list comes from tools/list, or from
    server/discover when tools_from_discover says so.
    """

    if tools_from_discover:
        tools_response = client.discover()
    else:
        tools_response = client.tools_list()

    mcp_tools = tools_response.json()['result']['tools']

    def execute_call(function_name:'str', arguments:'anydict') -> 'ToolCall':
        out = _execute_stateless_tool_call(client, function_name, arguments)
        return out

    out = _run_loop(execute_call, mcp_tools, task, system_text, model, ollama_url, max_turns, None)
    return out

# ################################################################################################################################
# ################################################################################################################################

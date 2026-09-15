# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines of the Alerts popup of an MCP gateway - the core four and the failure lines every type has, built in
# alerts_tab_lines.py, and the gateway's own: the tool calls an agent got wrong, the responses the gateway itself
# refused, the callers it rejected, throttled or saw looping, how long tool calls take, what the size cap cut,
# how many bytes went out, a gateway nobody calls and one exposing too many tools. alerts_tab.py lists them under
# the mcp type next to the other types' lines.

# Zato
from zato.admin.web.alerts_tab_lines import active_line, Auth_Failures_Window_Unit_Field, email_line, error_rate_line, \
    failures_in_a_row_line, Invalid_Calls_Window_Unit_Field, Latency_Window_Unit_Field, Line_Kind_Popover, llm_line, \
    Rejections_Window_Unit_Field, Repeat_Calls_Window_Unit_Field, Section_Callers, Section_Configuration, Section_Failures, \
    Section_Traffic, silence_line, Throttled_Calls_Window_Unit_Field, Truncations_Window_Unit_Field, use_llm_line, \
    Volume_Budget_Unit_Field, Volume_Budget_Window_Unit_Field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# What every line but the tool count says about where its numbers come from
_reads_audit_log = 'The alerts read the gateway\'s audit log, so Audit log under More options has to be on ' + \
    'for anything to be counted.'

# What a gateway is called in the shared silence line's help
_silence_owner = 'gateway'
_silence_noun = 'tool call'

# ################################################################################################################################
# ################################################################################################################################

# The tool calls an agent got wrong - a tool the gateway does not expose or arguments its schema refuses
def _invalid_tool_calls_line() -> 'anydict':
    out = {
        'name': 'invalid_tool_calls',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Invalid tool calls',
        'title': 'Invalid tool calls',
        'fields': ['invalid_calls', 'invalid_calls_window'],
        'rows': [['invalid_calls'], ['invalid_calls_window']],
        'unit_field': Invalid_Calls_Window_Unit_Field,
        'summary': 'Alert after {invalid_calls|invalid tool call|invalid tool calls} ' + \
            f'in the last {{{Invalid_Calls_Window_Unit_Field}@invalid_calls_window}}',
        'how_it_works': 'How many tool calls naming a tool the gateway does not expose, or passing arguments its schema ' + \
            'refuses, raise an alert, and how long the window they are counted over. These are the JSON-RPC errors ' + \
            '-32601 and -32602 - the agent\'s mistake rather than the backend\'s, an agent that hallucinates tool names ' + \
            'or gets a schema wrong. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# The responses the gateway itself refused - a safeguard in reject mode or the size cap in block mode
def _rejected_responses_line() -> 'anydict':
    out = {
        'name': 'rejected_responses',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Rejected responses',
        'title': 'Rejected responses',
        'fields': ['rejections', 'rejections_window'],
        'rows': [['rejections'], ['rejections_window']],
        'unit_field': Rejections_Window_Unit_Field,
        'summary': 'Alert after {rejections|rejected response|rejected responses} ' + \
            f'in the last {{{Rejections_Window_Unit_Field}@rejections_window}}',
        'how_it_works': 'How many tool responses the gateway refused raise an alert, and how long the window they are ' + \
            'counted over. A safeguard in reject mode found something in what a tool returned, or the size cap in block ' + \
            'mode found it too large - the agent got a refusal instead of the data, so a run of them says a tool keeps ' + \
            'returning what the gateway will not pass on. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# The callers whose credentials did not authenticate
def _rejected_callers_line() -> 'anydict':
    out = {
        'name': 'rejected_callers',
        'section': Section_Callers,
        'kind': Line_Kind_Popover,
        'label': 'Rejected callers',
        'title': 'Rejected callers',
        'fields': ['auth_failures', 'auth_failures_window'],
        'rows': [['auth_failures'], ['auth_failures_window']],
        'unit_field': Auth_Failures_Window_Unit_Field,
        'summary': 'Alert after {auth_failures|rejected caller|rejected callers} ' + \
            f'in the last {{{Auth_Failures_Window_Unit_Field}@auth_failures_window}}',
        'how_it_works': 'How many requests whose credentials did not authenticate raise an alert, and how long the window ' + \
            'they are counted over. An agent with a wrong or an expired credential, or one nobody gave access to, is ' + \
            'answered 403 before any tool runs. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# The callers a security definition's rate limit answered 429
def _throttled_callers_line() -> 'anydict':
    out = {
        'name': 'throttled_callers',
        'section': Section_Callers,
        'kind': Line_Kind_Popover,
        'label': 'Throttled callers',
        'title': 'Throttled callers',
        'fields': ['throttled_calls', 'throttled_calls_window'],
        'rows': [['throttled_calls'], ['throttled_calls_window']],
        'unit_field': Throttled_Calls_Window_Unit_Field,
        'summary': 'Alert after {throttled_calls|throttled call|throttled calls} ' + \
            f'in the last {{{Throttled_Calls_Window_Unit_Field}@throttled_calls_window}}',
        'how_it_works': 'How many requests answered 429 by a security definition\'s rate limit raise an alert, and how ' + \
            'long the window they are counted over. An agent calling faster than its definition allows is told to wait, ' + \
            'and a run of these says one caller is hammering the gateway. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# One session calling one tool over and over - an agent stuck in a loop
def _repeated_calls_line() -> 'anydict':
    out = {
        'name': 'repeated_calls',
        'section': Section_Callers,
        'kind': Line_Kind_Popover,
        'label': 'Repeated calls',
        'title': 'Repeated calls',
        'fields': ['repeat_calls', 'repeat_calls_window'],
        'rows': [['repeat_calls'], ['repeat_calls_window']],
        'unit_field': Repeat_Calls_Window_Unit_Field,
        'summary': 'Alert when one session calls one tool {repeat_calls|time|times} ' + \
            f'in the last {{{Repeat_Calls_Window_Unit_Field}@repeat_calls_window}}',
        'how_it_works': 'How many times one session may call one tool before an alert, and how long the window the calls ' + \
            'are counted over. An agent stuck in a loop calls the same tool again and again, each call costing a backend ' + \
            'round trip and tokens - the alert names the session and the tool. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# How long tool calls take, in seconds - a warning above the first threshold, an error above the second
def _slow_tool_calls_line() -> 'anydict':
    out = {
        'name': 'slow_tool_calls',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': 'Slow tool calls',
        'title': 'Slow tool calls',
        'fields': ['warning_latency', 'error_latency', 'latency_window'],
        'rows': [['warning_latency', 'error_latency'], ['latency_window']],
        'unit_field': Latency_Window_Unit_Field,
        'summary': 'Warning above {warning_latency|second|seconds}, error above {error_latency|second|seconds}, ' + \
            f'averaged over the last {{{Latency_Window_Unit_Field}@latency_window}}',
        'how_it_works': 'Tool calls averaging more than the first number of seconds raise a warning, more than ' + \
            'the second an error, and how long the window they are averaged over. Fractions such as 7.5 are fine. ' + \
            'Only tool calls count - initialize and tools/list are not timed against the backend. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# The responses the size cap cut short - the agent got the beginning and a note that the rest was trimmed
def _truncated_responses_line() -> 'anydict':
    out = {
        'name': 'truncated_responses',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': 'Truncated responses',
        'title': 'Truncated responses',
        'fields': ['truncations', 'truncations_window'],
        'rows': [['truncations'], ['truncations_window']],
        'unit_field': Truncations_Window_Unit_Field,
        'summary': 'Alert after {truncations|truncated response|truncated responses} ' + \
            f'in the last {{{Truncations_Window_Unit_Field}@truncations_window}}',
        'how_it_works': 'How many tool responses the size cap cut short raise an alert, and how long the window they ' + \
            'are counted over. The cap in truncate mode trims what a tool returned to the token limit, so the agent ' + \
            'got a response that reads fine but is incomplete - a run of them says a tool returns more than the ' + \
            'agent can take. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# The bytes of every response added up across the window, the budget a size in kilobytes, megabytes or gigabytes
# with a unit select of its own next to the window's
def _response_volume_line() -> 'anydict':
    out = {
        'name': 'response_volume',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': 'Response volume',
        'title': 'Response volume',
        'fields': ['volume_budget', 'volume_budget_window'],
        'rows': [['volume_budget'], ['volume_budget_window']],
        'unit_field': Volume_Budget_Window_Unit_Field,
        'field_units': {'volume_budget': Volume_Budget_Unit_Field},
        'summary': f'Alert above {{{Volume_Budget_Unit_Field}@volume_budget}} of responses ' + \
            f'in the last {{{Volume_Budget_Window_Unit_Field}@volume_budget_window}}',
        'how_it_works': 'How many bytes of tool responses raise an alert - a size in kilobytes, megabytes or gigabytes, ' + \
            'fractions such as 2.5 are fine - and how long the window they are added up over. Every response the ' + \
            'gateway sent back counts, so the number is what the agents cost in data. ' + _reads_audit_log,
    }
    return out

# ################################################################################################################################

# How many tools the gateway exposes - read off the gateway itself rather than off the audit log, no window
def _too_many_tools_line() -> 'anydict':
    out = {
        'name': 'too_many_tools',
        'section': Section_Configuration,
        'kind': Line_Kind_Popover,
        'label': 'Too many tools',
        'title': 'Too many tools',
        'fields': ['max_tools'],
        'rows': [['max_tools']],
        'summary': 'Alert when the gateway exposes more than {max_tools|tool|tools}',
        'how_it_works': 'How many tools the gateway may expose before an alert. The most capable models degrade past ' + \
            '20 to 25 tools - they pick the wrong one or none at all - so a gateway whose tool count crosses the ' + \
            'number raises one alert that stays open until the count drops. The count is read off the gateway itself, ' + \
            'not off the audit log, so this line works with the audit log off.',
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def mcp_lines() -> 'anylist':
    """ The lines of the Alerts popup of an MCP gateway, in the order they are read - the core four, the failures
    of the backend and of the agent, the callers, the traffic and the one configuration line.
    """
    out = [
        active_line(),
        use_llm_line(),
        llm_line(),
        email_line(),
        failures_in_a_row_line(),
        error_rate_line(),
        _invalid_tool_calls_line(),
        _rejected_responses_line(),
        _rejected_callers_line(),
        _throttled_callers_line(),
        _repeated_calls_line(),
        _slow_tool_calls_line(),
        _truncated_responses_line(),
        _response_volume_line(),
        silence_line(_silence_noun, _silence_owner),
        _too_many_tools_line(),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

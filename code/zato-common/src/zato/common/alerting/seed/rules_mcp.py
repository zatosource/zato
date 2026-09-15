# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of MCP gateways - every count is over the tool calls of one gateway within the rule's window.
# The failures a gateway sees are an agent's as often as a backend's - a tool the gateway does not expose, arguments
# its schema refuses, one session calling one tool over and over - so the rules tell the two apart, and next to the
# traffic there is one number with no window at all, how many tools the gateway exposes, since the most capable
# models degrade past twenty to twenty-five of them. The other types live in rules_connections.py, rules_llm.py
# and rules_mllp.py, the cross-type rules in rules_common.py.

mcp_rules = """
rule
    Gateway_Failing
docs
    An MCP gateway whose three newest tool calls all failed raises an error email alert.
    A failure is a tool call answered with a JSON-RPC error, a result flagged isError, a rejection or a timeout.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mcp' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Error_Rate
docs
    An MCP gateway whose failed-call share reaches a tenth of its recent tool calls raises a warning email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Invalid_Tool_Calls
docs
    An MCP gateway that answered five invalid tool calls within the window raises a warning email alert.
    An invalid call names a tool the gateway does not expose or passes arguments its schema refuses - the JSON-RPC
    errors -32601 and -32602 - which is the agent's mistake rather than the backend's.
defaults
    invalid_call_threshold = 5
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.invalid_call_count is at least default.invalid_call_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Rejected_Responses
docs
    An MCP gateway that rejected three tool responses within the window raises a warning email alert.
    A safeguard in reject mode or the size cap in block mode refused what a tool returned, so the agent received an error
    in place of the response.
defaults
    rejection_threshold = 3
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.rejection_count is at least default.rejection_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Rejected_Callers
docs
    An MCP gateway that turned away ten callers within the window raises a warning email alert.
    A rejected caller carried no credentials or ones that matched none of the gateway's security definitions.
defaults
    auth_failure_threshold = 10
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.auth_failure_count is at least default.auth_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Throttled_Callers
docs
    An MCP gateway that throttled ten calls within the window raises a warning email alert.
    A throttled call was answered with a 429 because its security definition's rate limit was reached.
defaults
    throttled_threshold = 10
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.throttled_count is at least default.throttled_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Repeated_Calls
docs
    An MCP gateway on which one session called one tool twenty times within the window raises a warning email alert.
    An agent calling the same tool over and over is an agent stuck in a loop, and every one of its calls reaches the backend.
defaults
    repeat_call_threshold = 20
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.repeat_call_count is at least default.repeat_call_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Tool_Calls
docs
    An MCP gateway whose average tool-call time within the window exceeds five seconds raises a warning email alert.
    Above fifteen seconds the error rule takes over, which is why this one is bounded from above.
defaults
    warning_avg_duration_ms = 5000
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.avg_duration_ms is at least default.warning_avg_duration_ms and
    alert.avg_duration_ms is less than default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Tool_Calls_Error
docs
    An MCP gateway whose average tool-call time within the window exceeds fifteen seconds raises an error email alert.
defaults
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.avg_duration_ms is at least default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Truncated_Responses
docs
    An MCP gateway that truncated five tool responses within the window raises a warning email alert.
    The size cap in truncate mode cut what a tool returned down to the cap, so the agent received an incomplete response.
defaults
    truncation_threshold = 5
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.truncation_count is at least default.truncation_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Response_Volume
docs
    An MCP gateway whose tool responses added up to more than a hundred megabytes within a day raises a warning email alert.
    The size of every tool response the gateway returned in the window is added up, whatever the tool.
defaults
    volume_budget = 100000000
    window_seconds = 86400
when
    alert.source is 'mcp' and
    alert.volume_bytes is at least default.volume_budget
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Gateway_Silent
docs
    An MCP gateway that expects traffic and received no tool call for an hour raises a warning email alert.
defaults
    silence_seconds = 3600
when
    alert.source is 'mcp' and
    alert.silent_seconds is at least default.silence_seconds
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Too_Many_Tools
docs
    An MCP gateway that exposes more than twenty-five tools raises a warning email alert.
    The most capable models degrade past twenty to twenty-five tools - they pick the wrong one or none at all -
    so the alert stays open until the count drops back under the number.
defaults
    max_tools = 25
when
    alert.source is 'mcp' and
    alert.tool_count is at least default.max_tools
then
    outcome.action = 'email'
    outcome.severity = 'warning'

""".strip()

# ################################################################################################################################
# ################################################################################################################################

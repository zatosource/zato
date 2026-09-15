# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of outgoing LLM connections - the rules every outgoing connection has over the llm source,
# plus what is the LLM's own: a token budget, completions cut short by the token limit and refusals, both of which
# the provider answers with an HTTP 200. The other connection types live in rules_connections.py, the cross-type
# rules in rules_common.py.

llm_rules = """
rule
    Connection_Down
docs
    An LLM connection that failed three consecutive times is considered down and raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'llm' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Completions
docs
    An LLM connection whose average completion time within the window exceeds ten seconds raises a warning email alert.
    Above fifteen seconds the error rule takes over, which is why this one is bounded from above.
defaults
    warning_avg_duration_ms = 10000
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.warning_avg_duration_ms and
    alert.avg_duration_ms is less than default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Completions_Error
docs
    An LLM connection whose average completion time within the window exceeds fifteen seconds raises an error email alert.
defaults
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Error_Rate
docs
    An LLM connection whose failed-completion share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Status_Codes
docs
    An LLM connection answered with one of the status codes it alerts on, three times within the window, raises an error email alert.
    The codes are a comma-separated list of three-digit codes and classes, e.g. 429, 401 and 5xx, and a connection may carry a list of its own.
    A 429 is the provider's rate limit and comes first because it is the code an LLM provider answers with most often -
    a 401 or a 403 is a key that is wrong or lacks access to the model, a 5xx the provider's own trouble.
defaults
    status_codes = '429, 401, 403, 5xx'
    status_code_threshold = 3
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.status_code_count is at least default.status_code_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Connection_Failures
docs
    An LLM connection whose calls failed three times within the window before any response arrived raises an error email alert.
    A timeout, a refused or reset connection, a name that does not resolve and a TLS handshake that fails all count here.
defaults
    connection_failure_threshold = 3
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.connection_failure_count is at least default.connection_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Truncated_Completions
docs
    An LLM connection whose completions were cut short by the token limit three times within the window raises a warning email alert.
    The provider stopped generating because max_tokens was reached - the reply arrived with an HTTP 200 and reads fine, only it is incomplete.
    Raising the connection's max tokens or shortening the prompt is the remedy.
defaults
    truncation_threshold = 3
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.truncation_count is at least default.truncation_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Refusals
docs
    An LLM connection whose completions were refused three times within the window raises a warning email alert.
    The provider declined to answer or a content filter blocked the prompt or the reply - most of them arrive with an HTTP 200,
    so nothing but the finish reason tells a refusal apart from an answer.
defaults
    refusal_threshold = 3
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.refusal_count is at least default.refusal_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Token_Budget
docs
    An LLM connection that used more than ten million tokens within a day raises a warning email alert.
    Input and output tokens are added up across every call the connection made in the window, as the provider reported them.
defaults
    token_budget = 10000000
    window_seconds = 86400
when
    alert.source is 'llm' and
    alert.token_count is at least default.token_budget
then
    outcome.action = 'email'
    outcome.severity = 'warning'

""".strip()

# ################################################################################################################################
# ################################################################################################################################

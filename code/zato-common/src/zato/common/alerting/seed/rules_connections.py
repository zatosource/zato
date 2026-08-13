# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-connection-type default alert rules - one text block per type. The
# cross-type, channel and scheduler rules live in rules_common.py, together
# with the note on how the default thresholds were chosen.

rest_rules = """
rule
    Connection_Down
docs
    A REST or SOAP outgoing connection that failed three consecutive times is considered down and raises a critical email alert.
    A connection's health check is measured on its own, so three failed checks say the same thing as three failed calls.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Responses
docs
    A REST or SOAP outgoing connection whose average response time within the window exceeds five seconds raises an email alert.
    A connection's health check is measured on its own, so a slow check reads as slow whatever the connection's own traffic did.
defaults
    max_avg_duration_ms = 5000
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A REST or SOAP outgoing connection whose error share reaches a tenth of its recent traffic raises an email alert.
    This is the early warning below the diagnose rule's quarter threshold.
    A connection's health check is measured on its own, so the share of failed checks counts apart from the share of failed calls.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    A REST outgoing connection whose error share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
    A connection's health check is measured on its own and is diagnosed on the same threshold.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source in ['rest-outgoing', 'rest-outgoing-health'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

sql_rules = """
rule
    Connection_Down
docs
    A database connection that failed three consecutive times is down - the top of the severity ladder,
    because everything else rests on the database being there.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'sql-outgoing' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Queries
docs
    A database connection whose average query round-trip within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source is 'sql-outgoing' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A database connection whose failed-query share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'sql-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    A database connection whose failed-query share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'sql-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

llm_rules = """
rule
    Connection_Down
docs
    An LLM connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'llm' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Completions
docs
    An LLM connection whose average completion time within the window exceeds ten seconds raises a warning email alert.
    Above fifteen seconds the critical rule takes over, which is why this one is bounded from above.
defaults
    warning_avg_duration_ms = 10000
    critical_avg_duration_ms = 15000
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.warning_avg_duration_ms and
    alert.avg_duration_ms is less than default.critical_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Completions_Critical
docs
    An LLM connection whose average completion time within the window exceeds fifteen seconds raises a critical email alert.
defaults
    critical_avg_duration_ms = 15000
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.critical_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Error_Rate
docs
    An LLM connection whose failed-completion share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'llm' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    An LLM connection whose failed-completion share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'llm' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

mcp_rules = """
rule
    Server_Down
docs
    An MCP connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mcp' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Tool_Calls
docs
    An MCP connection whose average tool-call time within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source is 'mcp' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An MCP connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'mcp' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    An MCP connection whose failed-call share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'mcp' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

microsoft_rules = """
rule
    Connection_Down
docs
    A Microsoft cloud connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'microsoft-cloud' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_API_Calls
docs
    A Microsoft cloud connection whose average call time within the window exceeds two seconds raises an email alert.
defaults
    max_avg_duration_ms = 2000
when
    alert.source is 'microsoft-cloud' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A Microsoft cloud connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'microsoft-cloud' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    A Microsoft cloud connection whose failed-call share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'microsoft-cloud' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'

rule
    Service_Degraded
docs
    A Microsoft service reporting a degraded health state about itself raises an email alert at once, no window.
when
    alert.source is 'microsoft-health' and
    alert.health_state is 'degraded'
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Service_Interrupted
docs
    A Microsoft service reporting a service interruption about itself raises a critical email alert at once, no window.
when
    alert.source is 'microsoft-health' and
    alert.health_state is 'interruption'
then
    outcome.action = 'email'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

email_rules = """
rule
    Connection_Down
docs
    An email connection that failed three consecutive times is considered down and raises a critical email alert,
    dispatched through the remaining notification connections when the failing one is itself the email connection.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Auth_Failures
docs
    An email connection with three or more authentication failures within the window raises an email alert.
    Authentication failing is its own signal, distinct from unreachable, because the remedy is credentials, not networking.
defaults
    auth_failure_threshold = 3
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.auth_failure_count is at least default.auth_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An email connection whose failed-send or failed-fetch share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    An email connection whose failed-send or failed-fetch share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

odoo_rules = """
rule
    Connection_Down
docs
    An Odoo connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'odoo' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Auth_Failures
docs
    An Odoo connection with three or more failed logins within the window raises an email alert.
defaults
    auth_failure_threshold = 3
when
    alert.source is 'odoo' and
    alert.auth_failure_count is at least default.auth_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Calls
docs
    An Odoo connection whose average call time within the window exceeds two seconds raises an email alert.
defaults
    max_avg_duration_ms = 2000
when
    alert.source is 'odoo' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An Odoo connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'odoo' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Diagnose
docs
    An Odoo connection whose failed-call share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'odoo' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'
""".strip()


# ################################################################################################################################

file_transfer_rules = """
rule
    Connection_Down
docs
    A file transfer connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'file-outgoing' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Transfer_Failures
docs
    A file transfer connection with ten or more failed transfers within its window raises a warning email alert.
    This type measures over ten minutes because transfers are burstier than API calls.
    At twenty failures the critical rule takes over, which is why this one is bounded from above.
defaults
    warning_failure_count = 10
    critical_failure_count = 20
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.warning_failure_count and
    alert.error_count is less than default.critical_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Transfer_Failures_Critical
docs
    A file transfer connection with twenty or more failed transfers within its window raises a critical email alert.
defaults
    critical_failure_count = 20
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.critical_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Error_Rate_Diagnose
docs
    A file transfer connection whose failed-transfer share reached a quarter of its recent traffic has its alert diagnosed by the LLM.
    Like the rest of this type, the measure covers a ten-minute window.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'file-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'

rule
    Canary_Failing
docs
    A failing canary check raises a critical email alert at once - the canary uploads, downloads and removes
    a small test file, so its newest outcome speaks for the whole transfer path.
    Ships inactive, like the canary job itself, because the canary writes to the remote system - activating both is the opt-in.
when
    alert.source is 'canary' and
    alert.canary_failed is 1
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Arrival_Overdue
docs
    A schedule whose expected file did not arrive within its own arrival window raises an email alert.
    The measure is a ratio of time since the newest delivered file to the schedule's declared window,
    so one rule sizes itself to every schedule that declares one - a schedule without a window is never measured.
    The dedup window is raised because the measure only grows until a file finally arrives,
    so the alert would otherwise re-fire every sweep.
defaults
    arrival_overdue_multiplier = 1
when
    alert.source is 'file-outgoing' and
    alert.arrival_overdue_ratio is at least default.arrival_overdue_multiplier
then
    outcome.action = 'email'
    outcome.severity = 'warning'
    outcome.dedup_window_seconds = 14400
""".strip()


# ################################################################################################################################
# ################################################################################################################################

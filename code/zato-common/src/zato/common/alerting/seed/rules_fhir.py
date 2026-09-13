# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of outgoing FHIR connections - the rules of an outgoing REST connection over
# the fhir and fhir-health sources, plus the operation outcomes a FHIR server answers with. The other
# connection types live in rules_connections.py, the cross-type rules in rules_common.py.

fhir_rules = """
rule
    Connection_Down
docs
    A FHIR outgoing connection that failed three consecutive times is considered down and raises an error email alert.
    A connection's health check is measured on its own, so three failed checks say the same thing as three failed calls.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['fhir', 'fhir-health'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Responses
docs
    A FHIR outgoing connection whose average response time within the window exceeds five seconds raises an email alert.
    A connection's health check is measured on its own, so a slow check reads as slow whatever the connection's own traffic did.
defaults
    max_avg_duration_ms = 5000
    window_seconds = 300
when
    alert.source in ['fhir', 'fhir-health'] and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A FHIR outgoing connection whose error share reaches a tenth of its recent traffic raises an email alert.
    A connection's health check is measured on its own, so the share of failed checks counts apart from the share of failed calls.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source in ['fhir', 'fhir-health'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Status_Codes
docs
    A FHIR outgoing connection answered with one of the status codes it alerts on, three times within the window, raises an error email alert.
    The codes are a comma-separated list of three-digit codes and classes, e.g. 401, 403 and 5xx, and a connection may carry a list of its own.
    A response carrying an OperationOutcome is counted by its issue code under Operation_Outcomes and never here, so the 5xx class
    stands for what is not one - a proxy's error page or a body that is not FHIR on an error status.
defaults
    status_codes = '401, 403, 5xx'
    status_code_threshold = 3
    window_seconds = 300
when
    alert.source is 'fhir' and
    alert.status_code_count is at least default.status_code_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Operation_Outcomes
docs
    A FHIR outgoing connection answered with an OperationOutcome of one of the issue codes it alerts on, three times within the window,
    raises an error email alert. The codes are a comma-separated list of FHIR IssueType codes as the resource carries them - exception,
    transient, timeout, throttled, lock-error, no-store and too-costly say the FHIR server itself is in trouble, invalid, required,
    value and structure say the request was wrong, not-found says the resource is missing, security, login, forbidden and expired
    say the caller was refused. A connection may carry a list of its own, e.g. adding not-found when a missing resource is something to act on.
defaults
    outcome_codes = 'exception, transient, timeout, throttled, lock-error, no-store, too-costly'
    outcome_threshold = 3
    window_seconds = 300
when
    alert.source is 'fhir' and
    alert.outcome_count is at least default.outcome_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Connection_Failures
docs
    A FHIR outgoing connection whose calls failed three times within the window before any response arrived raises an error email alert.
    A timeout, a refused or reset connection, a name that does not resolve and a TLS handshake that fails all count here.
defaults
    connection_failure_threshold = 3
    window_seconds = 300
when
    alert.source is 'fhir' and
    alert.connection_failure_count is at least default.connection_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

""".strip()

# ################################################################################################################################
# ################################################################################################################################

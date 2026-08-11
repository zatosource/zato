# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules, one ruleset per connection type. Every threshold is
# a named default the user tunes in place, no error-rate rule fires on thin
# traffic, and the numbers are the product's own defaults - three consecutive
# failures for down, 10 percent errors over five minutes, 5 seconds for HTTP
# latency, 7 days for certificates, twice the interval for missed scheduled work.

# This module holds the rules that are not about one connection type - the
# cross-type measures, the channels and the scheduler. The per-connection-type
# rules live in rules_connections.py.

common_rules = """
rule
    Outstanding_Backlog
docs
    An object with messages still waiting for their follow-up raises an email alert when the count reaches the threshold.
defaults
    outstanding_threshold = 100
when
    alert.outstanding is at least default.outstanding_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Feed_Silent
docs
    A feed that has been silent for two hours or more raises an email alert.
defaults
    silent_threshold_seconds = 7200
when
    alert.silent_seconds is at least default.silent_threshold_seconds
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Certificate_Expiring
docs
    A connection whose TLS certificate expires within a week raises an email alert.
    A days-left value of zero means the certificate was not measured at all, which is why the rule also requires at least one day.
defaults
    cert_warning_days = 7
    min_days_measured = 1
when
    alert.source is 'certificate' and
    alert.cert_days_left is at least default.min_days_measured and
    alert.cert_days_left is less than default.cert_warning_days
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()


# ################################################################################################################################

channels_rules = """
rule
    Channel_Error_Rate
docs
    An inbound channel whose error share reaches a tenth of its recent traffic raises an email alert.
    The rule waits for at least ten events in the window, so one failure out of two calls never wakes anyone up.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['rest-channel', 'soap-channel', 'mllp-channel'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()


# ################################################################################################################################

scheduler_rules = """
rule
    Job_Error_Rate
docs
    Scheduled jobs whose error share reaches a tenth of their recent runs raise an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'scheduler' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Job_Error_Rate_Diagnose
docs
    Scheduled jobs whose error share reached a quarter of their recent runs have their alert diagnosed by the LLM.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'scheduler' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'diagnose'
    outcome.severity = 'critical'

rule
    Missed_Run
docs
    A job that has not run for longer than twice its own interval raises an email alert.
    The measure is a ratio of time since the newest run to the job's interval, so it sizes itself to each job.
defaults
    overdue_multiplier = 2
when
    alert.source is 'scheduler' and
    alert.overdue_ratio is at least default.overdue_multiplier
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Start_Delay
docs
    A job whose delay between planned and actual fire time exceeds five seconds raises an email alert.
defaults
    max_start_delay_ms = 5000
when
    alert.source is 'scheduler' and
    alert.start_delay_ms is at least default.max_start_delay_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()


# ################################################################################################################################
# ################################################################################################################################

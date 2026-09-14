# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of HL7 MLLP channels and outgoing connections - the rules of a REST or SOAP channel over
# the mllp-channel source, minus everything that reads an HTTP status, plus the negative acknowledgments a channel
# sends, and the rules of an outgoing HTTP connection over the mllp-outgoing source, plus the negative acknowledgments
# a connection is answered. The HTTP channels live in rules_common.py, the connection types in rules_connections.py.

mllp_channel_rules = """
rule
    Channel_Failing
docs
    An MLLP channel whose three newest messages were all acknowledged negatively raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mllp-channel' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Error_Rate
docs
    An MLLP channel whose share of negative acknowledgments reaches a tenth of its recent traffic raises an email alert.
    The rule waits for at least ten messages in the window, so one failure out of two messages never wakes anyone up.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'mllp-channel' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Negative_Acks
docs
    An MLLP channel that sent three negative acknowledgments of one of the codes it alerts on within the window
    raises an error email alert. The codes are a comma-separated list out of AE, AR, CE and CR - AE and CE say the
    service failed to process a message, AR and CR that the message was rejected - and a channel may carry a list
    of its own, e.g. AR and CR alone when a failing service is already covered by the error rate.
defaults
    ack_codes = 'AE, AR, CE, CR'
    ack_threshold = 3
    window_seconds = 300
when
    alert.source is 'mllp-channel' and
    alert.ack_count is at least default.ack_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Responses
docs
    An MLLP channel whose acknowledgments take more than five seconds on average in the window raises a warning email alert.
defaults
    max_avg_duration_ms = 5000
    window_seconds = 300
when
    alert.source is 'mllp-channel' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Channel_Silent
docs
    An MLLP channel that expects traffic and received no message for an hour raises a warning email alert.
defaults
    silence_seconds = 3600
when
    alert.source is 'mllp-channel' and
    alert.silent_seconds is at least default.silence_seconds
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

mllp_outgoing_rules = """
rule
    Connection_Down
docs
    An outgoing MLLP connection whose three newest messages all failed - answered negatively or not acknowledged at all -
    is considered down and raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mllp-outgoing' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Error_Rate
docs
    An outgoing MLLP connection whose share of failed messages reaches a tenth of its recent traffic raises an email alert.
    The rule waits for at least ten messages in the window, so one failure out of two messages never wakes anyone up.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'mllp-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Negative_Acks
docs
    An outgoing MLLP connection answered three negative acknowledgments of one of the codes it alerts on within the window
    raises an error email alert. The codes are a comma-separated list out of AE, AR, CE and CR - AE and CE say the remote
    application failed to process a message, AR and CR that it rejected the message - and a connection may carry a list
    of its own, e.g. AR and CR alone when a failing remote application is already covered by the error rate.
defaults
    ack_codes = 'AE, AR, CE, CR'
    ack_threshold = 3
    window_seconds = 300
when
    alert.source is 'mllp-outgoing' and
    alert.ack_count is at least default.ack_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Connection_Failures
docs
    An outgoing MLLP connection whose messages went unacknowledged three times within the window raises an error email alert.
    A timeout waiting for the acknowledgment, a refused or reset connection, a connection closed before the acknowledgment
    arrived and a TLS handshake that fails all count here.
defaults
    connection_failure_threshold = 3
    window_seconds = 300
when
    alert.source is 'mllp-outgoing' and
    alert.connection_failure_count is at least default.connection_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Responses
docs
    An outgoing MLLP connection whose acknowledgments take more than five seconds to arrive on average in the window
    raises a warning email alert.
defaults
    max_avg_duration_ms = 5000
    window_seconds = 300
when
    alert.source is 'mllp-outgoing' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

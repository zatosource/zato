# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The one readable line an alert carries about the fact that raised it - which rule fired on which object
# and what the measures were at that moment. Only the measures that are non-zero speak, each with the window
# it was taken over when the windows differ per measure, and a connection's health check speaks of checks
# where its traffic speaks of calls.

from __future__ import annotations

# Zato
from zato.common.alerting.ack_codes import Ack_Code_Counts_Key
from zato.common.alerting.collectors.common import channel_sources, Measure_Ack_Codes, Measure_Auth_Failures, \
    Measure_Client_Errors, Measure_Connection_Failures, Measure_Latency, Measure_Operation_Outcomes, Measure_Server_Errors, \
    Measure_SOAP_Faults, Measure_Status_Codes, Window_Seconds_By_Measure_Key
from zato.common.alerting.fault_codes import Fault_Code_Counts_Key
from zato.common.alerting.outcome_codes import Outcome_Code_Counts_Key
from zato.common.alerting.status_codes import Status_Code_Counts_Key
from zato.common.audit_log.common import get_source_label, health_sources
from zato.common.util.api import pluralize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strintdict, strlist
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def _measure_window_part(fact:'stranydict', measure:'str') -> 'str':
    """ The window one measure was taken over, as the tail of its phrase - empty when the fact
    does not say, e.g. a fact a test built by hand, and empty when it is the error rate's window,
    which the message has named already.
    """
    windows = fact[Window_Seconds_By_Measure_Key]

    if measure not in windows:
        return ''

    window_seconds = windows[measure]

    if fact['total_count']:
        if window_seconds == fact['window_seconds']:
            return ''

    out = f' over {window_seconds}s'
    return out

# ################################################################################################################################

def _format_status_code_counts(counts:'strintdict') -> 'str':
    """ The matching responses by their code, the codes in their order and each with its count when it has
    more than one - `401 x2, 503`.
    """
    parts:'strlist' = []

    for code in sorted(counts):

        count = counts[code]

        if count == 1:
            parts.append(code)
        else:
            parts.append(f'{code} x{count}')

    out = ', '.join(parts)
    return out

# ################################################################################################################################

def build_fact_message(rule_name:'str', fact:'stranydict') -> 'str':
    """ One readable line saying which rule fired on which object and what
    the measures were at that moment - only the measures that are non-zero speak,
    each with the window it was taken over when the windows differ per measure.
    """
    parts = []

    source = fact['source']
    source_label = get_source_label(source)

    # A connection's own health check is named in the measure rather than after it,
    # because "the check failed" and "the calls failed" are two different sentences.
    is_health_check = source in health_sources

    # A channel's failed responses are sorted by who is at fault, so its measures
    # speak of callers and requests rather than of authentication in general.
    is_channel = source in channel_sources

    if fact['total_count']:
        percent = round(fact['error_rate'] * 100)
        error_part = f'error rate {percent}% ({fact["error_count"]} of {fact["total_count"]}'
        error_part += f' over {fact["window_seconds"]}s)'
        parts.append(error_part)

    if fact['outstanding']:
        parts.append(f'{fact["outstanding"]} outstanding (oldest waiting {fact["oldest_waiting_seconds"]}s)')

    if fact['silent_seconds']:
        parts.append(f'silent for {fact["silent_seconds"]}s')

    if failure_count := fact['consecutive_failures']:
        if is_health_check:
            times_label = pluralize(failure_count, 'time')
            parts.append(f'{source_label} failed {times_label}')
        else:
            failure_label = pluralize(failure_count, 'consecutive failure')
            parts.append(failure_label)

    if fact['avg_duration_ms']:
        parts.append(f'average duration {fact["avg_duration_ms"]}ms' + _measure_window_part(fact, Measure_Latency))

    if auth_failure_count := fact['auth_failure_count']:
        if is_channel:
            auth_failure_label = pluralize(auth_failure_count, 'rejected caller')
        else:
            auth_failure_label = pluralize(auth_failure_count, 'authentication failure')
        parts.append(auth_failure_label + _measure_window_part(fact, Measure_Auth_Failures))

    if client_error_count := fact['client_error_count']:
        client_error_label = pluralize(client_error_count, 'bad request')
        parts.append(client_error_label + _measure_window_part(fact, Measure_Client_Errors))

    if server_error_count := fact['server_error_count']:

        # The rate is the count over the responses of its own window, which may not be the error rate's,
        # so the responses it was taken over are read back off it rather than off total_count
        server_error_rate = fact['server_error_rate']
        server_percent = round(server_error_rate * 100)
        response_count = round(server_error_count / server_error_rate)

        server_part = f'server errors {server_percent}% ({server_error_count} of {response_count}'
        server_part += _measure_window_part(fact, Measure_Server_Errors) + ')'
        parts.append(server_part)

    if status_code_count := fact['status_code_count']:
        responses_label = pluralize(status_code_count, 'response')
        codes_part = _format_status_code_counts(fact[Status_Code_Counts_Key])
        status_part = f'{responses_label} with a status the connection alerts on ({codes_part})'
        parts.append(status_part + _measure_window_part(fact, Measure_Status_Codes))

    if fault_count := fact['fault_count']:
        faults_label = pluralize(fault_count, 'SOAP fault')
        fault_codes_part = _format_status_code_counts(fact[Fault_Code_Counts_Key])
        fault_part = f'{faults_label} the connection alerts on ({fault_codes_part})'
        parts.append(fault_part + _measure_window_part(fact, Measure_SOAP_Faults))

    if outcome_count := fact['outcome_count']:
        outcomes_label = pluralize(outcome_count, 'operation outcome')
        outcome_codes_part = _format_status_code_counts(fact[Outcome_Code_Counts_Key])
        outcome_part = f'{outcomes_label} the connection alerts on ({outcome_codes_part})'
        parts.append(outcome_part + _measure_window_part(fact, Measure_Operation_Outcomes))

    if ack_count := fact['ack_count']:
        acks_label = pluralize(ack_count, 'negative acknowledgment')
        ack_codes_part = _format_status_code_counts(fact[Ack_Code_Counts_Key])
        ack_part = f'{acks_label} the channel alerts on ({ack_codes_part})'
        parts.append(ack_part + _measure_window_part(fact, Measure_Ack_Codes))

    if connection_failure_count := fact['connection_failure_count']:
        if connection_failure_count == 1:
            failures_label = '1 timeout or connection failure'
        else:
            failures_label = f'{connection_failure_count} timeouts or connection failures'
        parts.append(failures_label + _measure_window_part(fact, Measure_Connection_Failures))

    if cert_days_left := fact['cert_days_left']:
        days_label = pluralize(cert_days_left, 'day')
        parts.append(f'certificate expires in {days_label}')

    if fact['health_state']:
        parts.append(f'reported health state `{fact["health_state"]}`')

    if fact['test_transfer_failed']:
        parts.append('the test transfer check failed')

    if fact['start_delay_ms']:
        parts.append(f'started {fact["start_delay_ms"]}ms late')

    if fact['overdue_ratio']:
        parts.append(f'{fact["overdue_ratio"]}x its interval since the last run')

    if seconds_since_last_arrival := fact['seconds_since_last_arrival']:
        parts.append(f'no file for {seconds_since_last_arrival}s')

    if arrival_overdue_ratio := fact['arrival_overdue_ratio']:
        parts.append(f'{arrival_overdue_ratio}x its arrival window since the last file')

    if expected_files_missing := fact['expected_files_missing']:
        missing_label = pluralize(expected_files_missing, 'expected file')
        parts.append(f'{missing_label} still missing today, {fact["delivered_today"]} delivered')

    if list_failed_streak := fact['list_failed_streak']:
        run_label = pluralize(list_failed_streak, 'run')
        parts.append(f'the newest {run_label} never reached the directory')

    if failed_files_in_window := fact['failed_files_in_window']:
        failed_label = pluralize(failed_files_in_window, 'file')
        runs_label = pluralize(fact['runs_failed_in_window'], 'run')
        parts.append(f'{failed_label} failed across {runs_label}')

    if runs_interrupted_in_window := fact['runs_interrupted_in_window']:
        interrupted_label = pluralize(runs_interrupted_in_window, 'run')
        parts.append(f'{interrupted_label} cut short by a server stop')

    if quarantined_count := fact['quarantined_count']:
        quarantined_label = pluralize(quarantined_count, 'file')
        parts.append(f'{quarantined_label} quarantined')

    if verify_failed_count := fact['verify_failed_count']:
        verify_label = pluralize(verify_failed_count, 'stored file')
        parts.append(f'{verify_label} did not verify')

    measures = ', '.join(parts)

    # A streak measure on a health source already opens with the source's name, so
    # repeating it in parentheses would say the same thing twice in one sentence ..
    if is_health_check:
        if fact['consecutive_failures']:
            out = f'Rule `{rule_name}` matched `{fact["object_name"]}` - {measures}'
            return out

    # .. every other measure reads the same on either stream, so the source is what tells them apart.
    out = f'Rule `{rule_name}` matched `{fact["object_name"]}` ({source_label}) - {measures}'
    return out

# ################################################################################################################################
# ################################################################################################################################

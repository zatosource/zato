# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import SERVICE_UNAVAILABLE

# Zato
from zato.common.b2b.common.outcome import FailureCause, FinalState
from zato.common.b2b.common.retry import RetryAction
from zato.common.b2b.ebms2.common import ErrorCode
from zato.common.b2b.ebms2.outbound import accept_no_answer, accept_response, give_up, next_action, OutboundState, \
    record_resend
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import answer, deliver, new_exchange, send, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    Exchange = Exchange
    OutboundMessage = OutboundMessage
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_retry_interval_seconds = 30

# ################################################################################################################################
# ################################################################################################################################

def _run_out_of_retries(exchange:'Exchange', outbound:'OutboundMessage', status:'int') -> 'None':
    """ Delivers a message again on each retry, each delivery answered with the given HTTP status code,
    or with no answer for a status code of zero, and gives up once the retries run out.
    """
    while True:

        if status:
            _ = accept_response(outbound, status, {}, b'', exchange.clock)
        else:
            accept_no_answer(outbound)

        exchange.clock.advance(_retry_interval_seconds)
        decision = next_action(outbound, exchange.clock)

        if decision.action == RetryAction.Give_Up:
            give_up(outbound)
            break

        record_resend(outbound, exchange.clock)

# ################################################################################################################################
# ################################################################################################################################

class TestFailureCause:
    """ The cause of the failure of the delivery of a message is that of its last delivery.
    """

    def test_no_answer(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        _run_out_of_retries(exchange, outbound, 0)

        assert outbound.state == OutboundState.Failed
        assert outbound.outcome.final_state == FinalState.Failed
        assert outbound.outcome.error_code == ErrorCode.Delivery_Failure
        assert outbound.outcome.failure_cause == FailureCause.No_Answer
        assert outbound.outcome.failure_detail == ''

    def test_http_error(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        _run_out_of_retries(exchange, outbound, SERVICE_UNAVAILABLE)

        assert outbound.state == OutboundState.Failed
        assert outbound.outcome.error_code == ErrorCode.Delivery_Failure
        assert outbound.outcome.failure_cause == FailureCause.HTTP_Error
        assert outbound.outcome.failure_detail == f'{SERVICE_UNAVAILABLE}'

    def test_protocol_error(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        other_settings = new_settings(parties, Start_Time)
        other_settings.cpa_id = 'b2b-other-agreement'
        other_exchange = new_exchange(parties, other_settings)

        outbound = send(exchange)
        result = deliver(other_exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Failed
        assert outcome.error_code == ErrorCode.Value_Not_Recognized
        assert outcome.failure_cause == FailureCause.Protocol_Error
        assert outcome.failure_detail == ErrorCode.Value_Not_Recognized

    def test_last_delivery_decides(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        _ = accept_response(outbound, SERVICE_UNAVAILABLE, {}, b'', exchange.clock)

        assert outbound.state == OutboundState.Pending
        assert outbound.outcome.failure_cause == FailureCause.HTTP_Error

        exchange.clock.advance(_retry_interval_seconds)
        record_resend(outbound, exchange.clock)
        _run_out_of_retries(exchange, outbound, 0)

        assert outbound.outcome.failure_cause == FailureCause.No_Answer

    def test_acknowledgment_clears_cause(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        _ = accept_response(outbound, SERVICE_UNAVAILABLE, {}, b'', exchange.clock)

        exchange.clock.advance(_retry_interval_seconds)
        record_resend(outbound, exchange.clock)

        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Acknowledged
        assert outcome.delivered
        assert outcome.failure_cause == ''
        assert outcome.failure_detail == ''

# ################################################################################################################################
# ################################################################################################################################

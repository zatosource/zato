# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# httpx
import httpx

# Zato
from .wire import do_send, new_exchange, use_responder
from zato.common.as2.common import AS2Error, DigestAlgorithm, Failure, SendError
from zato.common.as2.inbound import handle
from zato.common.as2.mdn import build_mdn, Disposition, DispositionType, MDNRequest, new_error_disposition, \
    new_failure_disposition, new_processed_disposition, new_warning_disposition
from zato.common.as2.outbound import describe_send_result

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# A digest of the right shape for a message whose content is not the one that was sent.
_wrong_mic = 'QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUE=, sha-256'

# A Message-ID belonging to some other exchange entirely.
_other_message_id = '<some-other-message@partnercorp.example.com>'

# ################################################################################################################################
# ################################################################################################################################

def _new_mdn_request(request:'httpx.Request') -> 'any_':
    """ The receipt request for the message that just arrived, so a crafted receipt answers
    the real delivery rather than something made up.
    """
    out = MDNRequest()

    out.message_id = request.headers['message-id']
    out.as2_from = request.headers['as2-from']
    out.as2_to = request.headers['as2-to']

    return out

# ################################################################################################################################

def _respond_with(exchange:'any_', disposition:'any_', mic:'str' = '', message_id:'str' = '') -> 'None':
    """ Puts a receipt of the given shape on the HTTP response of the next delivery, which is how
    each way a partner can answer without acknowledging the message is reproduced.
    """

    def _responder(request:'httpx.Request') -> 'any_':
        _ = request.read()

        mdn_request = _new_mdn_request(request)

        if message_id:
            mdn_request.message_id = message_id

        body, headers = build_mdn(mdn_request, disposition, mic)

        out = httpx.Response(OK, content=body, headers=headers)
        return out

    use_responder(exchange, _responder)

# ################################################################################################################################
# ################################################################################################################################

class TestUnacknowledgedDeliveries:
    """ A delivery that left, reached the partner and came back with an HTTP 200 can still be
    unacknowledged in several distinct ways. They look identical from the outside - the send
    succeeded and the message is not delivered - so each one names itself in the result, which
    is the only thing that tells an operator what to do next.
    """

    def test_a_response_without_a_content_type_carries_no_receipt(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        def _responder(request:'httpx.Request') -> 'any_':
            _ = request.read()

            out = httpx.Response(OK)
            return out

        use_responder(exchange, _responder)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn is None
        assert result.http_status == OK
        assert result.mdn_error == SendError.No_Content_Type

# ################################################################################################################################

    def test_a_body_that_is_not_a_receipt_is_told_apart_from_an_absent_one(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        def _responder(request:'httpx.Request') -> 'any_':
            _ = request.read()
            headers = {'Content-Type': 'text/plain'}

            out = httpx.Response(OK, content=b'This is not an MDN', headers=headers)
            return out

        use_responder(exchange, _responder)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn is None

        # The partner did answer with something, which is a different problem from answering
        # with nothing - a misconfigured endpoint rather than a missing receipt.
        assert result.mdn_error == SendError.Unparseable_MDN

# ################################################################################################################################

    def test_a_receipt_for_another_message_does_not_acknowledge_this_one(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        disposition = new_processed_disposition()
        _respond_with(exchange, disposition, message_id=_other_message_id)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.Message_ID_Mismatch

# ################################################################################################################################

    def test_a_receipt_that_reports_no_processing_at_all(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A failed disposition carrying no modifier at all - the partner did not process
        # the message and says nothing more about why.
        disposition = Disposition()
        disposition.disposition_type = DispositionType.Failed

        _respond_with(exchange, disposition)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.Not_Processed

# ################################################################################################################################

    def test_a_receipt_reporting_a_processing_error(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        disposition = new_error_disposition(AS2Error.Decryption_Failed)
        _respond_with(exchange, disposition)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.Error_Modifier

# ################################################################################################################################

    def test_a_receipt_refusing_the_message_itself(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        disposition = new_failure_disposition(Failure.Unsupported_MIC_Algorithms)
        _respond_with(exchange, disposition)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.Failure_Modifier

# ################################################################################################################################

    def test_a_receipt_reporting_a_different_digest(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        disposition = new_processed_disposition()
        _respond_with(exchange, disposition, mic=_wrong_mic)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.MIC_Mismatch

# ################################################################################################################################

    def test_a_receipt_digesting_under_another_algorithm(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        def _responder(request:'httpx.Request') -> 'any_':
            body = request.read()
            headers = dict(request.headers)

            # The real receiver computes the real digest, so the receipt reports the right bytes
            # under the wrong algorithm - a partner following a different rule rather than one
            # that received different content, which the operator takes up with them differently.
            received = handle(body, headers, exchange.receiver_partnerships, exchange.receiver_keystore)

            digest, _, _ = received.mic.partition(', ')
            mic = f'{digest}, {DigestAlgorithm.SHA1}'

            mdn_request = _new_mdn_request(request)
            disposition = new_processed_disposition()

            mdn_body, mdn_headers = build_mdn(mdn_request, disposition, mic)

            out = httpx.Response(OK, content=mdn_body, headers=mdn_headers)
            return out

        use_responder(exchange, _responder)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn_error == SendError.MIC_Algorithm_Mismatch

# ################################################################################################################################
# ################################################################################################################################

class TestAcknowledgedDeliveries:
    """ The receipts that do acknowledge the message leave no reason behind, which is what makes
    the reason worth reading when there is one.
    """

    def test_a_clean_receipt_names_no_reason(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn_error == ''

# ################################################################################################################################

    def test_a_warning_still_acknowledges_the_message(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A duplicate the partner accepted anyway is a warning, not a refusal.
        disposition = new_warning_disposition('duplicate-document')
        _respond_with(exchange, disposition)

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn_error == ''

# ################################################################################################################################
# ################################################################################################################################

class TestSendReport:
    """ The reason reaches the send report, which is what the test-message action in the Dashboard
    renders - without it the operator sees a delivery that succeeded and a message that is not
    acknowledged, with nothing in between.
    """

    def test_the_reason_reaches_the_report(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        disposition = new_error_disposition(AS2Error.Insufficient_Message_Security)
        _respond_with(exchange, disposition)

        result = do_send(exchange)
        report = describe_send_result(result)

        assert report['is_ok'] is False
        assert report['has_mdn'] is True
        assert report['mdn_error'] == SendError.Error_Modifier

        # The transport exception field stays empty - the message did leave.
        assert report['error'] == ''

# ################################################################################################################################

    def test_a_clean_report_names_no_reason(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)
        report = describe_send_result(result)

        assert report['is_ok'] is True
        assert report['mdn_error'] == ''

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.common.as2.mdn import describe_disposition, MDNDetails
from zato.common.as2.outbound import describe_send_result, new_send_report, SendResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_result(is_ok:'bool'=True, mic:'str'='QUFB, sha-256', mdn:'any_'=None) -> 'SendResult':
    """ Builds one delivery result the way a real send produces it.
    """
    out = SendResult()
    out.is_ok = is_ok
    out.message_id = '<test-message@zato>'
    out.mic = mic
    out.mdn = mdn
    out.http_status = OK

    return out

# ################################################################################################################################

def _make_mdn(
    disposition:'any_'='processed',
    modifier_kind:'any_'='',
    modifier:'any_'='',
    mic:'any_'='QUFB',
    mic_algorithm:'any_'='sha-256',
    is_signed:'any_'=True,
) -> 'any_':
    """ Builds one parsed MDN the way parse_mdn returns it.
    """
    out = MDNDetails()
    out.original_message_id = '<test-message@zato>'
    out.disposition = disposition
    out.modifier_kind = modifier_kind
    out.modifier = modifier
    out.mic = mic
    out.mic_algorithm = mic_algorithm
    out.is_signed = is_signed

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestNewSendReport:

    def test_the_empty_report_has_every_key_a_delivery_fills_in(self) -> 'None':

        report = new_send_report()

        assert report == {
            'is_ok': False,
            'message_id': '',
            'http_status': 0,
            'has_mdn': False,
            'mdn_signed': False,
            'disposition': '',
            'mic_matched': None,
            'error': '',
        }

# ################################################################################################################################
# ################################################################################################################################

class TestDescribeSendResult:

    def test_clean_delivery_with_a_signed_mdn_and_a_matching_mic(self) -> 'None':

        mdn = _make_mdn()
        result = _make_result(mdn=mdn)

        report = describe_send_result(result)

        assert report['is_ok'] is True
        assert report['message_id'] == '<test-message@zato>'
        assert report['http_status'] == OK
        assert report['has_mdn'] is True
        assert report['mdn_signed'] is True
        assert report['disposition'] == 'processed'
        assert report['mic_matched'] is True
        assert report['error'] == ''

# ################################################################################################################################

    def test_an_error_disposition_carries_its_modifier(self) -> 'None':

        mdn = _make_mdn(modifier_kind='error', modifier='unknown-trading-partner', mic='', mic_algorithm='', is_signed=False)
        result = _make_result(is_ok=False, mdn=mdn)

        report = describe_send_result(result)

        assert report['is_ok'] is False
        assert report['has_mdn'] is True
        assert report['mdn_signed'] is False
        assert report['disposition'] == 'processed/error: unknown-trading-partner'

# ################################################################################################################################

    def test_a_digest_mismatch_is_reported(self) -> 'None':

        mdn = _make_mdn(mic='QkJC')
        result = _make_result(is_ok=False, mdn=mdn)

        report = describe_send_result(result)

        assert report['mic_matched'] is False

# ################################################################################################################################

    def test_an_algorithm_mismatch_is_reported(self) -> 'None':

        mdn = _make_mdn(mic_algorithm='sha-1')
        result = _make_result(is_ok=False, mdn=mdn)

        report = describe_send_result(result)

        assert report['mic_matched'] is False

# ################################################################################################################################

    def test_an_mdn_without_a_mic_leaves_the_comparison_undecided(self) -> 'None':

        mdn = _make_mdn(mic='', mic_algorithm='')
        result = _make_result(mdn=mdn)

        report = describe_send_result(result)

        assert report['mic_matched'] is None

# ################################################################################################################################

    def test_a_response_without_an_mdn_reports_the_transport_outcome_only(self) -> 'None':

        result = _make_result(is_ok=False)

        report = describe_send_result(result)

        assert report['is_ok'] is False
        assert report['has_mdn'] is False
        assert report['mdn_signed'] is False
        assert report['disposition'] == ''
        assert report['mic_matched'] is None
        assert report['http_status'] == OK

# ################################################################################################################################
# ################################################################################################################################

class TestDescribeDisposition:

    def test_a_clean_disposition_is_the_type_alone(self) -> 'None':

        out = describe_disposition('processed', '', '')

        assert out == 'processed'

# ################################################################################################################################

    def test_a_modifier_rides_after_the_type(self) -> 'None':

        out = describe_disposition('processed', 'warning', 'duplicate-document')

        assert out == 'processed/warning: duplicate-document'

# ################################################################################################################################
# ################################################################################################################################

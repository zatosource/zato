# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .mdn_helpers import Message_ID
from zato.common.as2.mdn import parse_mdn_request

# ################################################################################################################################
# ################################################################################################################################

class TestMDNRequestParsing:

    def test_full_signed_sync_request(self) -> 'None':
        headers = {
            'message-id': Message_ID,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'disposition-notification-options':
                'signed-receipt-protocol=optional, pkcs7-signature; signed-receipt-micalg=optional, sha-256, sha1',
        }

        request = parse_mdn_request(headers)

        assert request.message_id == Message_ID
        assert request.as2_from == 'PartnerCorp'
        assert request.as2_to == 'ZatoRetail'
        assert request.requests_mdn is True
        assert request.requests_signed_mdn is True
        assert request.signed_receipt_protocol == 'pkcs7-signature'
        assert request.mic_algorithms == ['sha-256', 'sha1']
        assert request.async_mdn_url == ''

# ################################################################################################################################

    def test_async_request(self) -> 'None':
        headers = {
            'message-id': Message_ID,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'receipt-delivery-option': 'https://partnercorp.example.com/as2/mdn',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is True
        assert request.requests_signed_mdn is False
        assert request.async_mdn_url == 'https://partnercorp.example.com/as2/mdn'

# ################################################################################################################################

    def test_no_mdn_requested(self) -> 'None':
        headers = {
            'message-id': Message_ID,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is False
        assert request.requests_signed_mdn is False

# ################################################################################################################################

    def test_empty_protocol_value_is_tolerated(self) -> 'None':
        # The specification shows this degenerate shape explicitly - it must not be rejected.
        headers = {
            'message-id': Message_ID,
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'disposition-notification-options': 'signed-receipt-protocol=optional,; signed-receipt-micalg=optional,,,',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is True
        assert request.requests_signed_mdn is False
        assert request.signed_receipt_protocol == ''
        assert request.mic_algorithms == []

# ################################################################################################################################
# ################################################################################################################################

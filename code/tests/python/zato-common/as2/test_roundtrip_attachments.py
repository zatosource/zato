# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from .wire import do_send, new_exchange, Payload as _payload
from zato.common.as2.inbound import payloads as inbound_payloads
from zato.common.as2.outbound import PayloadItem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestMultipleAttachments:
    """ Several documents ride together in a multipart/related - the ship-notice-plus-PDF shape.
    """

    def test_two_documents_roundtrip(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        pdf_data = b'%PDF-1.7 Test bill of lading content'

        payload = [
            PayloadItem(_payload, 'application/edi-x12', 'ship-notice-856.edi'),
            PayloadItem(pdf_data, 'application/pdf', 'bill-of-lading.pdf'),
        ]

        result = do_send(exchange, payload=payload)

        assert result.is_ok

        inbound = exchange.results[0]
        assert len(inbound.payloads) == 2

        first, second = inbound.payloads

        assert first.data == _payload
        assert first.content_type == 'application/edi-x12'
        assert first.filename == 'ship-notice-856.edi'

        assert second.data == pdf_data
        assert second.content_type == 'application/pdf'
        assert second.filename == 'bill-of-lading.pdf'

# ################################################################################################################################

    def test_filename_preservation_for_a_single_document(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename='po-850.edi')

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == 'po-850.edi'

# ################################################################################################################################

    def test_no_filename_without_preservation(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange, filename='po-850.edi')

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == ''

# ################################################################################################################################
# ################################################################################################################################

class TestPeerSuppliedFilename:
    """ The filename arrives from the peer and travels into the routed message and the stored
    audit data. Nothing here writes a file under it, but a service or subscriber that does would
    be the one exposed, so it is reduced to a plain name at this boundary instead.
    """

    @pytest.mark.parametrize('sent,expected', [
        ('../../../etc/passwd', 'passwd'),
        ('..\\..\\windows\\system32\\config', 'config'),
        ('/absolute/path/po-850.edi', 'po-850.edi'),
        ('subdir/po-850.edi', 'po-850.edi'),
        ('..', ''),
        ('...', ''),
        ('/', ''),
        ('po-850.edi', 'po-850.edi'),
    ])
    def test_the_name_is_reduced_to_a_plain_one(self, parties:'TestParties', sent:'any_', expected:'any_') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename=sent)

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == expected

# ################################################################################################################################

    def test_a_name_longer_than_a_filesystem_accepts_is_truncated(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename='a' * 400)

        assert result.is_ok

        received = exchange.results[0]
        assert len(received.payloads[0].filename) == inbound_payloads._max_filename_length

# ################################################################################################################################
# ################################################################################################################################

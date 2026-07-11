# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import ACCEPTED, OK

# httpx
import httpx

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4Exception, EbMSError, Severity
from zato.common.as4.ebms import build_envelope, build_error
from zato.common.as4.inbound import handle
from zato.common.as4.outbound import build_push_message, new_part, pull, send
from zato.common.as4.profiles import new_edelivery1_pmode, new_ics2_pmode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.config import PMode
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

Payload = b'<Declaration xmlns="urn:test">ENS data</Declaration>'
Endpoint_URL = 'https://as4.invalid/msh'

# ################################################################################################################################
# ################################################################################################################################

def _make_pmode(factory:'any_') -> 'PMode':
    out = factory()

    out.endpoint_url = Endpoint_URL
    out.initiator.party_id = 'party-a'
    out.responder.party_id = 'party-b'

    out.service = 'urn:test:service'
    out.action = 'SubmitDeclaration'

    return out

# ################################################################################################################################

def _mock_client(handler:'any_') -> 'httpx.Client':
    transport = httpx.MockTransport(handler)

    out = httpx.Client(transport=transport)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSend:

    def test_send_with_synchronous_receipt(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_pmode(new_edelivery1_pmode)

        def responder(request:'httpx.Request') -> 'httpx.Response':
            # The responder runs the real inbound pipeline and returns its receipt.
            result = handle(request.content, request.headers['content-type'], [pmode], rsa_parties.receiver)

            out = httpx.Response(OK, content=result.body, headers={'Content-Type': result.content_type})
            return out

        part = new_part(Payload)

        with _mock_client(responder) as client:
            result = send(pmode, rsa_parties.sender, [part], client=client)

        assert result.is_ok
        assert result.http_status == OK
        assert result.receipt
        assert result.receipt.ref_to_message_id == result.message_id
        assert not result.errors

# ################################################################################################################################

    def test_send_receipt_digest_mismatch_is_detected(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_pmode(new_edelivery1_pmode)

        def responder(request:'httpx.Request') -> 'httpx.Response':
            result = handle(request.content, request.headers['content-type'], [pmode], rsa_parties.receiver)

            # Corrupt one digest inside the receipt before returning it.
            body = result.body
            start = body.find(b'<ds:DigestValue>') + len(b'<ds:DigestValue>')
            tampered = body[:start] + b'AAAA' + body[start + 4:]

            out = httpx.Response(OK, content=tampered, headers={'Content-Type': result.content_type})
            return out

        part = new_part(Payload)

        with _mock_client(responder) as client:
            with pytest.raises(AS4Exception) as exception_info:
                _ = send(pmode, rsa_parties.sender, [part], client=client)

        error_text = str(exception_info.value)
        assert 'digest mismatch' in error_text.lower()

# ################################################################################################################################

    def test_send_error_signal_is_reported(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_pmode(new_edelivery1_pmode)

        def responder(request:'httpx.Request') -> 'httpx.Response':
            # The receiver cannot verify a message tampered with in transit.
            tampered = request.content.replace(b'SubmitDeclaration', b'submitdeclaration', 1)
            result = handle(tampered, request.headers['content-type'], [pmode], rsa_parties.receiver)

            out = httpx.Response(OK, content=result.body, headers={'Content-Type': result.content_type})
            return out

        part = new_part(Payload)

        with _mock_client(responder) as client:
            result = send(pmode, rsa_parties.sender, [part], client=client)

        assert not result.is_ok
        assert not result.receipt
        assert result.errors
        assert result.errors[0].error_code == EbMSError.Failed_Authentication

# ################################################################################################################################

    def test_send_empty_response_means_async_receipt(self, rsa_parties:'TestParties') -> 'None':
        pmode = _make_pmode(new_edelivery1_pmode)

        def responder(request:'httpx.Request') -> 'httpx.Response':
            out = httpx.Response(ACCEPTED)
            return out

        part = new_part(Payload)

        with _mock_client(responder) as client:
            result = send(pmode, rsa_parties.sender, [part], client=client)

        assert result.is_ok
        assert result.http_status == ACCEPTED
        assert not result.receipt

# ################################################################################################################################
# ################################################################################################################################

class TestPull:

    def test_pull_receives_and_acknowledges_a_message(self, rsa_parties:'TestParties') -> 'None':
        # The trader pulls from customs - customs signs with the 'sender' identity
        # and encrypts for the trader, who is the 'receiver' identity.
        customs_pmode = _make_pmode(new_edelivery1_pmode)
        trader_pmode = _make_pmode(new_ics2_pmode)
        trader_pmode.mpc = 'urn:test:mpc:eori:pl:1234'
        trader_pmode.security.token_type = customs_pmode.security.token_type

        requests_seen = []

        def customs(request:'httpx.Request') -> 'httpx.Response':
            requests_seen.append(request.content)
            request_count = len(requests_seen)

            # The first request is the pull - answer with a waiting user message.
            if request_count == 1:
                part = new_part(Payload)
                body, content_type, _, _ = build_push_message(customs_pmode, rsa_parties.sender, [part])

                out = httpx.Response(OK, content=body, headers={'Content-Type': content_type})
                return out

            # The second request is the trader's receipt for the pulled message.
            out = httpx.Response(OK)
            return out

        with _mock_client(customs) as client:
            result = pull(trader_pmode, rsa_parties.receiver, client=client)

        assert result.is_ok
        assert result.has_message

        assert result.user_message is not None
        assert result.user_message.action == 'SubmitDeclaration'
        assert result.payloads[0].data == Payload
        assert result.receipt_sent

        # The pull request went out first, then the receipt.
        request_count = len(requests_seen)
        assert request_count == 2

        assert b'PullRequest' in requests_seen[0]
        assert b'urn:test:mpc:eori:pl:1234' in requests_seen[0]
        assert b'Receipt' in requests_seen[1]

# ################################################################################################################################

    def test_pull_from_empty_channel(self, rsa_parties:'TestParties') -> 'None':
        trader_pmode = _make_pmode(new_ics2_pmode)

        def customs(request:'httpx.Request') -> 'httpx.Response':
            # An empty channel yields the EBMS:0006 warning signal.
            envelope = build_envelope()
            _ = build_error(envelope, None, EbMSError.Empty_Message_Partition, 'EmptyMessagePartitionChannel',
                'No message available', Severity.Warning)

            body = etree.tostring(envelope)

            out = httpx.Response(OK, content=body, headers={'Content-Type': 'application/soap+xml'})
            return out

        with _mock_client(customs) as client:
            result = pull(trader_pmode, rsa_parties.receiver, client=client)

        assert not result.has_message
        assert result.payloads == []
        assert result.errors[0].error_code == EbMSError.Empty_Message_Partition

# ################################################################################################################################
# ################################################################################################################################

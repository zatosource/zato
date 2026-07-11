# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep, time

# httpx
import httpx

# Zato
from zato.common.as2.outbound import send
from zato.common.typing_ import optional

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

pathnone = optional['Path']

# ################################################################################################################################
# ################################################################################################################################

# The document our side delivers to the counterparty.
_outgoing_document = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*OPENAS2PEER    '
    + b'*260711*0900*U*00401*000000101*0*P*>~GS*PO*ZATORETAIL*OPENAS2PEER*20260711*0900*101*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523902**20260711~SE*3*0001~GE*1*101~IEA*1*000000101~'
)

# The document the counterparty delivers to us.
_incoming_document = (
    b'ISA*00*          *00*          *ZZ*OPENAS2PEER    *ZZ*ZATORETAIL     '
    + b'*260711*0905*U*00401*000000202*0*P*>~GS*PO*OPENAS2PEER*ZATORETAIL*20260711*0905*202*X*004010~'
    + b'ST*850*0001~BEG*00*NE*781244**20260711~SE*3*0001~GE*1*202~IEA*1*000000202~'
)

# How long to wait for files and deliveries and how long to sleep between attempts -
# the counterparty polls its outbox every five seconds, so the waits have to be generous.
_wait_timeout = 90.0
_poll_sleep = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _first_file_under(directory:'Path') -> 'pathnone':
    """ Returns the first file anywhere under the directory tree, or None when there is none yet.
    """

    # Our response to produce
    out:'pathnone' = None

    # The counterparty creates its directories lazily, so the tree may not exist yet.
    if directory.exists():
        for candidate in sorted(directory.rglob('*')):
            if candidate.is_file():
                out = candidate
                break

    return out

# ################################################################################################################################

def _wait_for_file(directory:'Path') -> 'Path':
    """ Waits until a file appears under the directory tree and returns its path.
    """
    deadline = time() + _wait_timeout
    found:'pathnone' = None

    while time() < deadline:
        found = _first_file_under(directory)
        if found:
            break
        sleep(_poll_sleep)

    if not found:
        raise Exception(f'No file appeared under {directory}')

    return found

# ################################################################################################################################

def _wait_for_inbound(wire:'any_') -> 'any_':
    """ Waits until our own listener has run the inbound pipeline at least once
    and returns the most recent of its decisions.
    """
    deadline = time() + _wait_timeout

    while time() < deadline:
        if wire.results:
            break
        sleep(_poll_sleep)

    if not wire.results:
        raise Exception('The counterparty never delivered to our listener')

    out = wire.results[-1]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSendToOpenAS2:
    """ Our sender against the counterparty's receiver - signed, encrypted, compressed X12
    over the real wire, with the returned signed MDN reconciled on our side
    and the delivered document asserted on its side.
    """

    def test_signed_encrypted_compressed_delivery(self, wire:'any_') -> 'None':

        client = httpx.Client()
        result = send(wire.partnership, wire.keystore, _outgoing_document, None, client)

        # The counterparty answered with a signed MDN and everything on it reconciled -
        # its signature, its Original-Message-ID and its Received-Content-MIC.
        assert result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is True
        assert result.mdn.disposition == 'processed'

        # Both sides computed the same MIC over the same content.
        digest, _, algorithm = result.mic.partition(', ')
        assert result.mdn.mic == digest
        assert result.mdn.mic_algorithm == algorithm

        # The document itself landed in the counterparty's inbox, byte for byte.
        inbox_dir = wire.data_dir / 'ZatoRetail-OpenAS2Peer' / 'inbox'
        inbox_file = _wait_for_file(inbox_dir)

        assert inbox_file.read_bytes() == _outgoing_document

# ################################################################################################################################
# ################################################################################################################################

class TestReceiveFromOpenAS2:
    """ The counterparty's sender against our inbound pipeline - a file dropped into its outbox
    travels signed, encrypted and compressed to our listener, and our signed MDN
    has to satisfy the counterparty's own reconciliation.
    """

    def test_outbox_drop_reaches_us_and_our_mdn_satisfies_it(self, wire:'any_') -> 'None':

        # The file is written outside the polled directory first, so the poller
        # never picks up a half-written document, and then moved in atomically.
        staging_dir = wire.data_dir / 'staging'
        staging_dir.mkdir(exist_ok=True)

        staging_path = staging_dir / 'purchase-order-850.edi'
        _ = staging_path.write_bytes(_incoming_document)

        outbox_path = wire.data_dir / 'outbox' / 'ZatoRetail' / 'purchase-order-850.edi'
        _ = staging_path.rename(outbox_path)

        # Our pipeline received the very bytes that went into the outbox.
        inbound = _wait_for_inbound(wire)

        assert not inbound.is_error
        assert not inbound.is_duplicate
        assert len(inbound.payloads) == 1
        assert inbound.payloads[0].data == _incoming_document

        # The counterparty accepted our MDN and stored the receipt ..
        mdn_dir = wire.data_dir / 'OpenAS2Peer-ZatoRetail' / 'mdn'
        _ = _wait_for_file(mdn_dir)

        # .. and nothing of its delivery landed in the error or resend queues.
        error_dir = wire.data_dir / 'outbox' / 'error'
        resend_dir = wire.data_dir / 'resend'

        assert _first_file_under(error_dir) is None
        assert _first_file_under(resend_dir) is None

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK

# Zato
from .channel_runtime_helpers import build_wire_message, cleanup_env, Connection_Name, make_runtime, \
    Receiver_Identifier, Sender_Identifier

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicates:

    def test_replay_gets_the_stored_mdn_and_is_not_routed_again(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)

            # The replay reuses the same body and headers, Message-ID included.
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert second.is_duplicate

            # The stored MDN bytes went out exactly as the first time ..
            assert second.body == first.body
            assert second.status_code == first.status_code

            # .. and the payload was routed only once.
            assert len(server.pubsub_backend.published) == 1

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_fresh_message_ids_are_not_duplicates(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_wire_message(parties)
            first = runtime.handle('cid-1', body, headers)

            body, headers, _, _ = build_wire_message(parties)
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert not second.is_duplicate

            assert len(server.pubsub_backend.published) == 2

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_losing_the_claim_delivers_nothing_and_returns_the_winners_mdn(
        self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            body, headers, message_id, _ = build_wire_message(parties)

            # Another server claimed this very message between the duplicate check and the
            # routing, which is the window a read followed by a write leaves open. Its own MDN
            # is already in the store.
            normalized_id = message_id.strip('<>')
            winner_body = b'the MDN of the delivery that won'
            winner_headers = {'Content-Type': 'multipart/report; report-type=disposition-notification'}

            claimed = runtime.duplicates.claim(
                Sender_Identifier, Receiver_Identifier, normalized_id, OK, winner_body, winner_headers)

            assert claimed is True

            result = runtime.handle('cid-1', body, headers)

            # Nothing was handed over ..
            assert server.invoked == []
            assert server.pubsub_backend.published == []
            assert result.payloads == []

            # .. and the answer is the winner's receipt, not the one just built.
            assert result.is_duplicate
            assert result.body == winner_body
            assert result.status_code == OK
            assert result.content_type == winner_headers['Content-Type']

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_replay_protection_survives_the_audit_log_being_off(
        self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            # The partner's exchanges are not recorded, which is a logging preference and must
            # not take replay protection with it.
            config = server.config_manager.outconn_as2[Connection_Name]
            config['is_audit_log_active'] = False

            body, headers, _, _ = build_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert second.is_duplicate

            # The document was delivered once, not twice.
            assert len(server.pubsub_backend.published) == 1

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

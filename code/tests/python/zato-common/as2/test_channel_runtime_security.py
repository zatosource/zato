# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timedelta, timezone

# Zato
from .channel_runtime_helpers import build_wire_message, certificate_to_pem, cleanup_env, Connection_Name, \
    make_partnership_config, make_runtime, rotated_sender_keystore, sender_certificate_to_pem
from zato.common.as2.common import AS2Error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateRotation:

    def test_message_signed_with_the_activated_next_certificate_is_accepted(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
        make_rotated_pair:'any_',
    ) -> 'None':
        try:
            # The partner rotated its signing pair and the next certificate activated yesterday.
            rotated = make_rotated_pair('as2-sender-next')
            activation = datetime.now(timezone.utc) - timedelta(days=1)

            sender_certificate_pem = sender_certificate_to_pem(parties)
            next_certificate_pem = certificate_to_pem(rotated.certificate)
            activation_iso = activation.isoformat()

            options = {
                'partner_certificate': sender_certificate_pem,
                'next_certificate': next_certificate_pem,
                'next_certificate_from': activation_iso,
                }
            server, runtime = make_runtime(tmp_path, parties, **options)

            sender_keystore = rotated_sender_keystore(parties, rotated)
            body, headers, _, _ = build_wire_message(parties, sender_keystore=sender_keystore)

            result = runtime.handle('cid-1', body, headers)

            # The overlap window admits the new signer and the document was routed.
            assert not result.is_error
            assert len(server.pubsub_backend.published) == 1

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_message_signed_with_a_not_yet_activated_certificate_is_rejected(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
        make_rotated_pair:'any_',
    ) -> 'None':
        try:
            # The same rotation, except the next certificate only activates a month from now.
            rotated = make_rotated_pair('as2-sender-next')
            activation = datetime.now(timezone.utc) + timedelta(days=30)

            sender_certificate_pem = sender_certificate_to_pem(parties)
            next_certificate_pem = certificate_to_pem(rotated.certificate)
            activation_iso = activation.isoformat()

            options = {
                'partner_certificate': sender_certificate_pem,
                'next_certificate': next_certificate_pem,
                'next_certificate_from': activation_iso,
                }
            server, runtime = make_runtime(tmp_path, parties, **options)

            sender_keystore = rotated_sender_keystore(parties, rotated)
            body, headers, _, _ = build_wire_message(parties, sender_keystore=sender_keystore)

            result = runtime.handle('cid-1', body, headers)

            # The signer is not live yet, so the message was rejected and nothing was routed.
            assert result.is_error
            assert result.error_modifier == AS2Error.Authentication_Failed
            assert server.pubsub_backend.published == []

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestRejections:

    def test_unknown_partner_is_rejected_and_nothing_is_routed(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties, with_partnership=False)

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert result.is_error
            assert result.error_modifier == AS2Error.Unknown_Trading_Relationship

            assert server.invoked == []
            assert server.pubsub_backend.published == []

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_rejected_message_is_not_remembered_as_a_duplicate(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties, with_partnership=False)

            body, headers, _, _ = build_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)
            assert first.is_error

            # The partnership arrives - the same message must now be processable,
            # because a failed delivery never counted as processed.
            config = make_partnership_config()

            server.config_manager.outconn_as2[Connection_Name] = config
            server.config_manager.as2_config_generation += 1

            second = runtime.handle('cid-2', body, headers)

            assert not second.is_duplicate
            assert not second.is_error
            assert len(server.pubsub_backend.published) == 1

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

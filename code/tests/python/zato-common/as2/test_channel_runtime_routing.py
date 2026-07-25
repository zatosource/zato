# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK

# Zato
from .channel_runtime_helpers import build_wire_message, cleanup_env, Connection_Name, make_partnership_config, \
    make_runtime, Payload, Receiver_Identifier, Sender_Identifier
from zato.common.api import AS2

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestRouting:

    def test_default_topic_when_nothing_else_is_configured(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error
            assert result.status_code == OK

            # The one document went to the default AS2 topic ..
            assert server.invoked == []
            assert len(server.pubsub_backend.published) == 1

            topic, message = server.pubsub_backend.published[0]
            assert topic == AS2.Default.Inbound_Topic

            # .. carrying the AS2 identities and the payload ..
            assert message['message_id'] == result.message_id
            assert message['as2_from'] == Sender_Identifier
            assert message['as2_to'] == Receiver_Identifier
            assert message['data'] == Payload.decode('utf8')

            # .. plus the EDI envelope identifiers routing and reporting key on.
            edi = message['edi']

            assert edi['format'] == 'x12'
            assert edi['document_type'] == '850'
            assert edi['sender_id'] == 'ZATORETAIL'
            assert edi['interchange_control_number'] == '000000001'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_channel_topic_overrides_the_default(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties, channel_topic='orders.custom')

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            topic, _ = server.pubsub_backend.published[0]
            assert topic == 'orders.custom'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_channel_service_overrides_the_topic(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties, service_name='orders.channel-service')

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            assert server.pubsub_backend.published == []
            assert len(server.invoked) == 1

            service_name, message = server.invoked[0]
            edi = message['edi']

            assert service_name == 'orders.channel-service'
            assert edi['document_type'] == '850'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_partner_topic_overrides_the_channel(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            server, runtime = make_runtime(
                tmp_path, parties, service_name='orders.channel-service', partner_topic='orders.partner')

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            # The partner's own topic wins over the channel's service.
            assert server.invoked == []

            topic, _ = server.pubsub_backend.published[0]
            assert topic == 'orders.partner'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_partner_service_overrides_everything(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            options = {
                'service_name': 'orders.channel-service',
                'partner_service': 'orders.partner-service',
                'partner_topic': 'orders.partner',
                }
            server, runtime = make_runtime(tmp_path, parties, **options)

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            assert server.pubsub_backend.published == []

            service_name, _ = server.invoked[0]
            assert service_name == 'orders.partner-service'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_partnership_edits_take_effect_without_a_restart(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            server, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error
            topic, _ = server.pubsub_backend.published[0]
            assert topic == AS2.Default.Inbound_Topic

            # An edit of the Dashboard-managed connection reroutes the very next message - the edit
            # event replaces the config and moves the generation on, exactly as the real one does.
            config = make_partnership_config(inbound_topic='orders.after-the-edit')

            server.config_manager.outconn_as2[Connection_Name] = config
            server.config_manager.as2_config_generation += 1

            body, headers, _, _ = build_wire_message(parties)
            result = runtime.handle('cid-2', body, headers)

            assert not result.is_error
            topic, _ = server.pubsub_backend.published[1]
            assert topic == 'orders.after-the-edit'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_partnerships_are_not_rebuilt_per_message(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            _, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_wire_message(parties)
            _ = runtime.handle('cid-1', body, headers)

            first = runtime._get_partnerships()

            body, headers, _, _ = build_wire_message(parties)
            _ = runtime.handle('cid-2', body, headers)

            second = runtime._get_partnerships()

            # Building a partnership parses an X.509 certificate per configured partner, so the
            # same objects have to come back until the configuration says otherwise - a new list
            # each time would mean that parse ran again for a message that changed nothing.
            assert second is first

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

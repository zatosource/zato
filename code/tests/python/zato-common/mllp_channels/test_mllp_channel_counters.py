# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import ConnectionContext, HL7MLLPServer
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings

from mllp_live_util import sample_adt_a01

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_channel_name = 'test-mllp-counters'

# Who the messages are taken to be arriving from
_sender_ip   = '203.0.113.10'
_sender_port = 40000

# A message whose MSH-9 names a structure the parser does not know, which is what makes
# the parse step reject it with a negative acknowledgment.
_unknown_structure_message = (
    'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ZZZ^Z99|CTRL_PARSE_1|P|2.5\r'
    'PID|||12345^^^MRN||Doe^John||19800101|M'
).encode('utf-8')

# ################################################################################################################################
# ################################################################################################################################

class _RecordingCallback:
    """ Records each message it is handed, standing in for a channel's service.
    """

    def __init__(self) -> 'None':
        self.messages:'anylist' = []

    def __call__(self, message:'object', cid:'str') -> 'None':
        self.messages.append(message)
        return None

# ################################################################################################################################
# ################################################################################################################################

class TestChannelCounters(TestCase):
    """ Tests that what a channel answers with counts on that channel's own live state,
    and not only on the listener's, on every path an acknowledgment leaves by.
    """

    def _make_server(self, settings:'RouteSettings') -> 'tuple':
        """ Builds an in-process server with one default route reading under the given settings.
        """
        callback = _RecordingCallback()

        router = HL7MessageRouter()
        router.add_route(_channel_name, callback, service_name='test.service', is_default=True, settings=settings)

        server = HL7MLLPServer(ListenerConfig(), router)

        out = (server, router, callback)
        return out

# ################################################################################################################################

    def test_duplicate_ack_counts_on_the_channel(self) -> 'None':
        """ A duplicate is acknowledged positively without being delivered, and that
        acknowledgment counts on the matched channel's own state.
        """

        # The route deduplicates and hands the raw text over, so the callback records it verbatim
        settings = RouteSettings(
            should_parse_on_input=False,
            dedup_ttl_value=60,
            dedup_ttl_unit='minutes',
        )
        server, router, callback = self._make_server(settings)

        message = sample_adt_a01('CTRL_DUP_001')
        message_text = message.decode('utf-8')
        message_lines = message_text.split('\r')
        msh_line = message_lines[0]

        matched_route = router.match(msh_line)
        assert matched_route is not None

        connection_context = ConnectionContext(_sender_ip, _sender_port, '')
        mock_socket = MagicMock()

        # The same message arrives twice ..
        server._handle_message(mock_socket, message, connection_context, matched_route, matched_route.settings)
        server._handle_message(mock_socket, message, connection_context, matched_route, matched_route.settings)

        channel_state = server.get_channel_state(_channel_name)

        # .. the callback ran once because the second arrival was a duplicate ..
        self.assertEqual(len(callback.messages), 1)

        # .. and both acknowledgments count on the channel's own state.
        self.assertEqual(channel_state.acked, 2)
        self.assertEqual(channel_state.received, 1)

# ################################################################################################################################

    def test_parse_failure_nack_counts_on_the_channel(self) -> 'None':
        """ A message the parser rejects is answered with an application error, and that
        negative acknowledgment counts on the matched channel's own state.
        """

        # The route parses on input, which is the step the message under test fails at
        settings = RouteSettings()
        server, router, callback = self._make_server(settings)

        message_text = _unknown_structure_message.decode('utf-8')
        message_lines = message_text.split('\r')
        msh_line = message_lines[0]

        matched_route = router.match(msh_line)
        assert matched_route is not None

        connection_context = ConnectionContext(_sender_ip, _sender_port, '')
        mock_socket = MagicMock()

        server._handle_message(
            mock_socket, _unknown_structure_message, connection_context, matched_route, matched_route.settings)

        channel_state = server.get_channel_state(_channel_name)

        # The callback never ran ..
        self.assertEqual(len(callback.messages), 0)

        # .. the rejection counts on the channel's own state ..
        self.assertEqual(channel_state.received, 1)
        self.assertEqual(channel_state.nacked, 1)
        self.assertEqual(channel_state.acked, 0)

        # .. and the sender was answered with an application error.
        sent_arguments = mock_socket.sendall.call_args.args
        sent_bytes = sent_arguments[0]
        self.assertIn(b'MSA|AE', sent_bytes)

# ################################################################################################################################
# ################################################################################################################################

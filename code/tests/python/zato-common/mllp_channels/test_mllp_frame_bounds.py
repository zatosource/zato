# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from threading import Thread
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.codec import frame_encode
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.hl7.mllp.settings import Default_End_Sequence, Default_Start_Sequence, ListenerConfig, RouteSettings

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The listener's own ceiling, lower than what any channel's defaults would give
_listener_max_message_size = 200

# A channel that takes only one sending application, so anything else goes unmatched
_channel_name = 'test-frame-bounds'
_channel_sending_application = 'ONLY_THIS_ONE'

# What a sender that reached the listener directly is taken to be
_peer_address = ('127.0.0.1', 40200)

_socket_timeout = 5.0
_recv_buffer    = 4096

# ################################################################################################################################
# ################################################################################################################################

class _RecordingCallback:
    """ Records each message it is handed, standing in for a channel's service.
    """
    def __init__(self) -> 'None':
        self.messages:'anylist' = []

    def __call__(self, message:'object', cid:'str') -> 'any_':
        self.messages.append(message)

# ################################################################################################################################

def _tcp_pair() -> 'tuple':
    """ Two ends of one TCP connection over the loopback, the sender's and the listener's, because
    the keepalive options a matched channel sets are TCP's own and a Unix socket pair has none.
    """
    accepting = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accepting.bind(('127.0.0.1', 0))
    accepting.listen(1)

    sender_socket = socket.create_connection(accepting.getsockname())
    listener_socket, _ = accepting.accept()
    accepting.close()

    out = (sender_socket, listener_socket)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFramesAreReadUnderTheListenerCeiling(TestCase):
    """ The listener's own ceilings bound every frame read down a connection, including one that
    matched no channel and so is read under nobody's settings but the defaults.
    """

    def setUp(self) -> 'None':

        self.callback = _RecordingCallback()
        listener_config = ListenerConfig(max_message_size=_listener_max_message_size)

        # A channel's settings are brought under the listener's ceilings when they are built,
        # which is what the channel does before it registers its route
        settings = RouteSettings(should_parse_on_input=False)
        settings.apply_listener_bounds(listener_config)

        router = HL7MessageRouter()
        router.add_route(_channel_name, self.callback, service_name='test.service', is_default=False,
            settings=settings, msh3_sending_application=_channel_sending_application)

        self.server = HL7MLLPServer(listener_config, router)

# ################################################################################################################################

    def _send_down_a_connection(self, payload:'bytes') -> 'bytes':
        """ Opens a connection to the listener's handler, sends one frame down it and returns whatever
        came back before the listener was done with the connection.
        """
        sender_socket, listener_socket = _tcp_pair()

        handler = Thread(target=self.server._handle_connection, args=(listener_socket, _peer_address))
        handler.start()

        try:
            sender_socket.settimeout(_socket_timeout)
            sender_socket.sendall(frame_encode(payload, Default_Start_Sequence, Default_End_Sequence))

            # The listener answers and then ends the connection, so everything it had to say is read here
            out = sender_socket.recv(_recv_buffer)

            # .. and the ack arrives before the close, which is what a sender reading until the end sees
            sender_socket.shutdown(socket.SHUT_WR)

        finally:
            sender_socket.close()
            handler.join(_socket_timeout)

        return out

# ################################################################################################################################

    def test_an_unmatched_frame_over_the_listener_ceiling_is_refused(self) -> 'None':
        """ A frame no channel took, longer than the listener allows, is answered AE as unreadable
        rather than read in full under the defaults and answered as merely unmatched.
        """
        payload = b'MSH|^~\\&|SOMEONE_ELSE|FAC|RecvApp|RecvFac|20230101120000||ADT^A01|BIG_UNMATCHED|P|2.5\r' + \
            b'PID|' + b'X' * _listener_max_message_size * 2

        response = self._send_down_a_connection(payload)

        self.assertIn(b'MSA|AE|BIG_UNMATCHED', response)
        self.assertEqual(self.callback.messages, [])

# ################################################################################################################################

    def test_an_unmatched_frame_within_the_listener_ceiling_is_answered_as_unmatched(self) -> 'None':
        """ A frame no channel took, within what the listener allows, is read in full and answered AR,
        which is what the listener says of a message nobody wanted.
        """
        payload = b'MSH|^~\\&|SOMEONE_ELSE|FAC|RecvApp|RecvFac|20230101120000||ADT^A01|SMALL_UNMATCHED|P|2.5'

        response = self._send_down_a_connection(payload)

        self.assertIn(b'MSA|AR|SMALL_UNMATCHED', response)
        self.assertEqual(self.callback.messages, [])

# ################################################################################################################################

    def test_a_matched_frame_over_the_listener_ceiling_is_refused(self) -> 'None':
        """ A channel's own size is capped at the listener's, so a frame the channel took is bound
        by the listener all the same.
        """
        payload = b'MSH|^~\\&|ONLY_THIS_ONE|FAC|RecvApp|RecvFac|20230101120000||ADT^A01|BIG_MATCHED|P|2.5\r' + \
            b'PID|' + b'X' * _listener_max_message_size * 2

        response = self._send_down_a_connection(payload)

        self.assertIn(b'MSA|AE|BIG_MATCHED', response)
        self.assertEqual(self.callback.messages, [])

# ################################################################################################################################
# ################################################################################################################################

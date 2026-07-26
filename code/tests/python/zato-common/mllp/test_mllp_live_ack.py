# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# Zato
from zato.common.hl7.mllp.ack import Condition_Data_Type_Error
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from mllp_live_util import announce_sender, end_sequence, sample_adt_a01, start_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

# Long enough that a reply the listener does send arrives, short enough that one it does not
# send is noticed rather than waited out
_socket_timeout = 10.0

_recv_buffer_size = 4096

# What the listener is told to accept, and how much of an observation is hung off a message
# to take it past that
_small_message_size = 500
_padding_size       = 2_000

# What the decoder reading the reply will accept, which is not what the listener will
_reply_message_size = 1_000_000

# ################################################################################################################################

def _oversized_message(control_id:'str') -> 'bytes':
    """ Returns an ordinary message with an observation long enough to carry it past the size
    the listener is told to accept.
    """
    out = sample_adt_a01(control_id) + b'\rOBX|1|ST|NOTE||' + b'X' * _padding_size

    return out

# ################################################################################################################################

def _connect(port:'int') -> 'socket.socket':
    """ Opens a connection and announces the sender on it, as the load balancer would.
    """

    out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out.settimeout(_socket_timeout)
    out.connect(('127.0.0.1', port))
    announce_sender(out)

    return out

# ################################################################################################################################

def _read_one_reply(sock:'socket.socket') -> 'bytes':
    """ Reads until one whole framed reply has arrived, returning empty where the far side
    closed without sending anything.
    """

    decoder = FrameDecoder(start_sequence, end_sequence, _reply_message_size)

    while True:

        chunk = sock.recv(_recv_buffer_size)

        if not chunk:
            return b''

        decoder.feed(chunk)
        message = decoder.next_message()

        if message is not None:
            return message

# ################################################################################################################################
# ################################################################################################################################

class TestAFrameTooLargeToRead:
    """ A frame over the size limit leaves the stream with no boundary anyone can find, so the
    connection has to end. What the sender must not be left with is silence on a connection it
    is still holding open waiting for a reply.
    """

# ################################################################################################################################

    def test_an_oversized_frame_is_acknowledged(self) -> 'None':
        """ The sender is told its message was not taken, rather than waiting out its own timeout.
        """

        process, port = start_server(
            max_msg_size=_small_message_size,
            should_return_errors=True,
            use_relay=False,
        )

        try:
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(_oversized_message('BIG00001'), start_sequence, end_sequence))
                reply = _read_one_reply(sock)
            finally:
                sock.close()

            assert reply, 'An oversized frame was met with silence'
            assert b'MSA|AE|' in reply, f'An oversized frame was not rejected: {reply!r}'

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_the_rejection_says_what_was_wrong(self) -> 'None':
        """ And it says the message could not be read, not that the application failed on it,
        because the application never saw it.
        """

        process, port = start_server(
            max_msg_size=_small_message_size,
            should_return_errors=True,
            use_relay=False,
        )

        try:
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(_oversized_message('BIG00002'), start_sequence, end_sequence))
                reply = _read_one_reply(sock)
            finally:
                sock.close()

            assert Condition_Data_Type_Error.code.encode() in reply, f'The wrong condition was reported: {reply!r}'

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_the_connection_ends_after_the_rejection(self) -> 'None':
        """ There is no known boundary left in the stream, so carrying on would be guessing.
        """

        process, port = start_server(
            max_msg_size=_small_message_size,
            should_return_errors=True,
            use_relay=False,
        )

        try:
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(_oversized_message('BIG00003'), start_sequence, end_sequence))
                _ = _read_one_reply(sock)

                # Whatever follows the acknowledgment, the far side is done talking
                try:
                    remainder = sock.recv(_recv_buffer_size)
                except ConnectionResetError:
                    remainder = b''

                assert remainder == b'', f'The connection stayed open after an oversized frame: {remainder!r}'

            finally:
                sock.close()

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_a_message_within_the_limit_is_served(self) -> 'None':
        """ The limit is a limit and not a wall - what fits under it is taken as it always was.
        """

        process, port = start_server(should_return_errors=True, use_relay=False)

        try:
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(sample_adt_a01('FITS0001'), start_sequence, end_sequence))
                reply = _read_one_reply(sock)
            finally:
                sock.close()

            assert b'MSA|AA|FITS0001' in reply, f'A message within the limit was rejected: {reply!r}'

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestAHeaderThatCannotBeRead:
    """ A header with no field separator in it used to take the connection down with it, which
    cost every message queued behind it on the same connection.
    """

# ################################################################################################################################

    def test_a_header_with_no_field_separator_is_answered(self) -> 'None':
        """ One malformed frame is answered rather than being the end of the conversation.
        """

        process, port = start_server(should_return_errors=True, use_relay=False)

        try:
            sock = _connect(port)

            try:
                message = b'MSH no separator here\rPID|||12345^^^MRN||Doe^John'
                sock.sendall(frame_encode(message, start_sequence, end_sequence))
                reply = _read_one_reply(sock)
            finally:
                sock.close()

            assert reply, 'A malformed header took the connection down with it'
            assert b'MSA|' in reply, f'A malformed header was not acknowledged: {reply!r}'

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_the_connection_survives_a_malformed_header(self) -> 'None':
        """ And the message behind it on the same connection is served as though nothing happened.
        """

        process, port = start_server(should_return_errors=True, use_relay=False)

        try:
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(b'MSH no separator here\rPID|||1', start_sequence, end_sequence))
                _ = _read_one_reply(sock)

                sock.sendall(frame_encode(sample_adt_a01('AFTER001'), start_sequence, end_sequence))
                reply = _read_one_reply(sock)

                assert b'MSA|AA|AFTER001' in reply, f'The connection did not survive a malformed header: {reply!r}'

            finally:
                sock.close()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

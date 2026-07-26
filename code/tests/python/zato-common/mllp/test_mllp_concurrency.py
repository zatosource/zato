# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import threading
import time

# Zato
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from mllp_live_util import announce_sender, end_sequence, sample_adt_a01, start_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

# Small enough to saturate deliberately, large enough that several senders are genuinely at once
_max_connections = 8

# Long enough to outlast a slow message, which the recovery check waits on the reply to
_socket_timeout    = 30.0
_recv_buffer_size  = 4096
_max_message_size  = 1_000_000

# How long a connection held open by a slow message is given to be seen as such
_saturation_settle_seconds = 1.0

# How long a refused connection is given to come back before it is called a hang
_refusal_timeout_seconds = 5.0

# What the slow callback waits, which is long enough to keep every connection of the first wave open
_slow_callback_delay_seconds = 5

# ################################################################################################################################
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

    decoder = FrameDecoder(start_sequence, end_sequence, _max_message_size)

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

class TestConnectionLimit:
    """ Verifies what the listener does at and beyond the number of connections it will hold
    at once, which is the one thing standing between a burst of senders and the server.
    """

# ################################################################################################################################

    def test_a_full_burst_is_served_in_full(self) -> 'None':
        """ Every sender in a burst that exactly fills the listener gets its reply, so the limit
        does not cost anything up to the point it is reached.
        """

        process, port = start_server(
            callback_mode='ok',
            use_relay=False,
            listener_env={'Zato_HL7_MLLP_Max_Connections': str(_max_connections)},
        )

        replies:'list[bytes]' = []
        errors:'list[str]' = []
        lock = threading.Lock()

        def _send(index:'int') -> 'None':

            try:
                sock = _connect(port)

                try:
                    control_id = f'BURST{index:03d}'
                    sock.sendall(frame_encode(sample_adt_a01(control_id), start_sequence, end_sequence))
                    reply = _read_one_reply(sock)

                    with lock:
                        replies.append(reply)

                finally:
                    sock.close()

            except Exception as exception:
                with lock:
                    errors.append(f'{index}: {exception}')

        try:
            threads = [threading.Thread(target=_send, args=(index,)) for index in range(_max_connections)]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            assert not errors, f'Senders failed: {errors}'
            assert len(replies) == _max_connections

            for reply in replies:
                assert b'MSA|AA|' in reply, f'A sender within the limit was not acknowledged: {reply!r}'

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_a_sender_beyond_the_limit_is_closed_at_once(self) -> 'None':
        """ Once the listener is full the next sender is closed straight away and told nothing,
        rather than being left to wait out its own timeout.
        """

        process, port = start_server(
            callback_mode='slow',
            callback_delay=_slow_callback_delay_seconds,
            use_relay=False,
            listener_env={'Zato_HL7_MLLP_Max_Connections': str(_max_connections)},
        )

        holding:'list[socket.socket]' = []

        try:

            # Fill the listener with senders that will not finish for a while ..
            for index in range(_max_connections):

                sock = _connect(port)
                holding.append(sock)

                control_id = f'HOLD{index:03d}'
                sock.sendall(frame_encode(sample_adt_a01(control_id), start_sequence, end_sequence))

            # .. give the listener a moment to have taken all of them up ..
            time.sleep(_saturation_settle_seconds)

            # .. and see what the next one is met with
            refused = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            refused.settimeout(_refusal_timeout_seconds)
            refused.connect(('127.0.0.1', port))

            try:

                # Either the connection is closed under it or reset outright, and both say the
                # same thing - what must not happen is being left to wait
                try:
                    received = refused.recv(_recv_buffer_size)
                except ConnectionResetError:
                    received = b''

                assert received == b'', f'A refused sender was sent something: {received!r}'

            finally:
                refused.close()

        finally:

            for sock in holding:
                sock.close()

            stop_server(process)

# ################################################################################################################################

    def test_the_listener_keeps_going_after_refusing(self) -> 'None':
        """ Refusing a sender is not the end of the listener - once the senders holding it up
        are done, the next one is served as though nothing had happened.
        """

        process, port = start_server(
            callback_mode='slow',
            callback_delay=_slow_callback_delay_seconds,
            use_relay=False,
            listener_env={'Zato_HL7_MLLP_Max_Connections': str(_max_connections)},
        )

        holding:'list[socket.socket]' = []

        try:

            for index in range(_max_connections):

                sock = _connect(port)
                holding.append(sock)

                sock.sendall(frame_encode(sample_adt_a01(f'HOLD{index:03d}'), start_sequence, end_sequence))

            time.sleep(_saturation_settle_seconds)

            # Turn one away ..
            refused = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            refused.settimeout(_refusal_timeout_seconds)
            refused.connect(('127.0.0.1', port))

            try:
                _ = refused.recv(_recv_buffer_size)
            except ConnectionResetError:
                pass

            refused.close()

            # .. let go of everything holding the listener up ..
            for sock in holding:
                sock.close()

            holding = []

            # .. give the messages already taken up the time they were always going to need,
            # since knocking at the door throughout would only queue up more of them ..
            time.sleep(_slow_callback_delay_seconds + _saturation_settle_seconds)

            # .. and the listener is itself again
            sock = _connect(port)

            try:
                sock.sendall(frame_encode(sample_adt_a01('AFTER001'), start_sequence, end_sequence))
                reply = _read_one_reply(sock)
            finally:
                sock.close()

            assert b'MSA|AA|AFTER001' in reply, f'The listener did not recover after refusing a sender: {reply!r}'

        finally:

            for sock in holding:
                sock.close()

            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestOneSlowSenderDoesNotBlockAnother:
    """ Each connection is served on its own, so what one sender does is its own affair.
    """

# ################################################################################################################################

    def test_a_slow_sender_does_not_hold_up_the_rest(self) -> 'None':
        """ A sender that has connected and gone quiet must not stop anyone else being served,
        which is what serving connections one after another would do.
        """

        process, port = start_server(callback_mode='ok', use_relay=False)

        try:

            # One sender that connects and then says nothing at all ..
            quiet = _connect(port)

            try:

                # .. does not stop another from being served in full
                busy = _connect(port)

                try:
                    busy.sendall(frame_encode(sample_adt_a01('BUSY001'), start_sequence, end_sequence))
                    reply = _read_one_reply(busy)

                    assert b'MSA|AA|BUSY001' in reply, f'A quiet sender held up another: {reply!r}'

                finally:
                    busy.close()

            finally:
                quiet.close()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

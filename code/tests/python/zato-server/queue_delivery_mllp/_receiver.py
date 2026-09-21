# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing MLLP connection - a TCP listener that records every framed message and acknowledges
# it with the code it is scripted to, or drops the connection without an acknowledgment. A connection opened and
# closed again with nothing sent is a ping, recorded as a read.

# stdlib
import logging
import socket
import threading
from dataclasses import dataclass

# Zato
from zato.common.hl7.mllp.ack import build_ack
from zato.common.hl7.mllp.codec import frame_encode, FrameDecoder

# Test support
from queue_delivery.receiver import RecordedRequest, RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_mllp.receiver')

_host = '127.0.0.1'

# The standard MLLP frame
Start_Sequence = b'\x0b'
End_Sequence = b'\x1c\x0d'

_max_message_size = 1024 * 1024
_read_buffer_size = 32768

# How long the listener waits for a connection before checking whether it is still meant to run,
# and how long one connection may take to deliver a whole frame
_accept_timeout_seconds = 0.2
_connection_timeout_seconds = 5.0
_shutdown_timeout_seconds = 5

# What a message is acknowledged with when it is accepted and when it is refused
Accept_Code = 'AA'
Refuse_Code = 'AE'

# The error text a refused message's acknowledgment carries in its ERR segment
Refuse_Error_Text = 'The message was not accepted'

# The connection is closed without an acknowledgment - what a sender reads as no answer at all
Drop_Outcome = 'drop'

# A connection opened and closed again with nothing sent
Ping_Outcome = 'ping'

_segment_separator = '\r'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MLLPRecordedRequest(RecordedRequest):
    """ One message as the endpoint of an outgoing MLLP connection saw it - the body is the ER7 text and the outcome
    is the acknowledgment code it was answered with, or that the connection was dropped.
    """

    @property
    def ack_code(self) -> 'str':
        """ The acknowledgment code the message was answered with.
        """
        out = self.outcome
        return out

# ################################################################################################################################
# ################################################################################################################################

class MLLPRecordingReceiver(RecordingReceiver):
    """ The endpoint of an outgoing MLLP connection.
    """

    Accept_Outcome = Accept_Code
    Refuse_Outcome = Refuse_Code

    def __init__(self, port:'int') -> 'None':
        super().__init__(port)

        self._listener:'socket.socket | None' = None
        self._thread:'threading.Thread | None' = None
        self._is_running = False

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts listening in a thread of its own.
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((_host, self.port))
        listener.listen()
        listener.settimeout(_accept_timeout_seconds)

        self._listener = listener
        self._is_running = True

        thread = threading.Thread(target=self._serve, daemon=True)
        thread.start()

        self._thread = thread

        logger.info('Receiver started on port %d', self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops listening - the port is free again once this returns.
        """
        self._is_running = False

        if self._thread:
            self._thread.join(timeout=_shutdown_timeout_seconds)
            self._thread = None

        if self._listener:
            self._listener.close()
            self._listener = None

        logger.info('Receiver stopped on port %d', self.port)

# ################################################################################################################################

    def _serve(self) -> 'None':
        """ Accepts connections for as long as the receiver runs, each handled on a thread of its own.
        """
        listener = self._listener

        while self._is_running:

            try:
                connection, _ = listener.accept() # type: ignore[union-attr]
            except socket.timeout:
                continue
            except OSError:
                break

            thread = threading.Thread(target=self._handle, args=(connection,), daemon=True)
            thread.start()

# ################################################################################################################################

    def _handle(self, connection:'socket.socket') -> 'None':
        """ Reads one framed message off a connection and answers it, or records a ping when the connection is closed
        with nothing sent.
        """
        connection.settimeout(_connection_timeout_seconds)

        try:
            message = self._read_message(connection)

            if message is None:
                self._record_ping()
                return

            message_text = message.decode('utf-8')
            outcome = self.next_outcome()

            self.add_request(MLLPRecordedRequest(
                body=message_text,
                outcome=outcome,
                is_accepted=self.is_accepted(outcome),
                is_read=False,
            ))

            # A dropped connection is what a sender reads as no acknowledgment at all
            if outcome == Drop_Outcome:
                return

            ack = self._build_ack(message_text, outcome)
            connection.sendall(frame_encode(ack.encode('utf-8'), Start_Sequence, End_Sequence))

        except Exception:
            logger.warning('Receiver on port %d could not handle a connection', self.port, exc_info=True)

        finally:
            connection.close()

# ################################################################################################################################

    def _read_message(self, connection:'socket.socket') -> 'bytes | None':
        """ One complete frame off the connection, or None when the connection was closed before any byte arrived.
        """
        decoder = FrameDecoder(Start_Sequence, End_Sequence, _max_message_size)
        has_bytes = False

        while True:

            chunk = connection.recv(_read_buffer_size)

            if not chunk:
                if has_bytes:
                    raise ValueError('The connection was closed before a whole frame arrived')
                return None

            has_bytes = True
            decoder.feed(chunk)

            message = decoder.next_message()

            if message is not None:
                return message

# ################################################################################################################################

    def _record_ping(self) -> 'None':
        """ A connection opened and closed again with nothing sent - a read, which the script does not apply to.
        """
        self.add_request(MLLPRecordedRequest(
            body='',
            outcome=Ping_Outcome,
            is_accepted=True,
            is_read=True,
        ))

# ################################################################################################################################

    def _build_ack(self, message_text:'str', ack_code:'str') -> 'str':
        """ The acknowledgment of a message - a refused one names why in its ERR segment.
        """
        msh = message_text.split(_segment_separator, 1)[0]

        if ack_code == Accept_Code:
            out = build_ack(msh, ack_code)
        else:
            out = build_ack(msh, ack_code, error_text=Refuse_Error_Text)

        return out

# ################################################################################################################################
# ################################################################################################################################

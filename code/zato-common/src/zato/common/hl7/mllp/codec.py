# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from time import monotonic

# Zato
from zato.common.hl7.exception import HL7Exception

# ################################################################################################################################
# ################################################################################################################################

# The segment terminator every HL7 message uses, which is what ends the first line
Segment_Terminator = b'\r'

# What a segment may be seen to end with while routing, before the matched channel has had its
# say on line endings. A sender that ends its segments with a bare newline still has to be routed
# somewhere, and it is that channel that decides whether the ending is repaired or refused.
_Routing_Terminators = (b'\r', b'\n')

# What a sender that omits the start sequence altogether opens its message with instead
Bare_Message_Prefix = b'MSH'

# ################################################################################################################################
# ################################################################################################################################

def frame_encode(payload:'bytes', start_sequence:'bytes', end_sequence:'bytes') -> 'bytes':
    """ Wraps a raw HL7 payload in MLLP framing (start sequence + payload + end sequence).
    """

    out = start_sequence + payload + end_sequence
    return out

# ################################################################################################################################
# ################################################################################################################################

class FrameDecoder:
    """ Streaming MLLP frame decoder that accepts arbitrary chunks of bytes
    and yields complete, unframed HL7 messages one at a time.
    """

    def __init__(self, start_sequence:'bytes', end_sequence:'bytes', max_message_size:'int') -> 'None':
        self.start_sequence = start_sequence
        self.end_sequence   = end_sequence
        self.max_message_size = max_message_size

        #  Internal buffer accumulating bytes fed so far
        self._buffer = b''

        #  Whether we are currently inside a frame (past the start sequence)
        self._inside_frame = False

# ################################################################################################################################

    def feed(self, data:'bytes') -> 'None':
        """ Appends raw bytes to the internal buffer.
        """
        self._buffer += data

# ################################################################################################################################

    def next_message(self) -> 'bytes | None':
        """ Returns the next complete unframed message, or None if no complete frame is available yet.
        Raises HL7Exception if the frame exceeds max_message_size.
        """

        while True:

            # If we are not yet inside a frame, look for the start sequence ..
            if not self._inside_frame:

                start_position = self._buffer.find(self.start_sequence)

                # .. if no start sequence was found but the buffer begins with MSH
                # (a common real-world quirk where senders omit 0x0B), treat byte 0
                # as the implicit start position ..
                if start_position == -1:
                    if self._buffer.startswith(b'MSH'):
                        start_position = 0
                    else:

                        # .. otherwise discard and wait for more data.
                        self._buffer = b''
                        return None

                # .. skip past the start sequence (or past nothing if the sender omitted it) ..
                bytes_to_skip = start_position + len(self.start_sequence)

                if start_position == 0:
                    if self._buffer.startswith(b'MSH'):
                        bytes_to_skip = 0

                self._buffer = self._buffer[bytes_to_skip:]
                self._inside_frame = True

            # .. now we are inside a frame, look for the end sequence ..
            end_position = self._buffer.find(self.end_sequence)

            # .. end sequence not found yet ..
            if end_position == -1:

                # .. check if the accumulated payload already exceeds the limit ..
                buffer_length = len(self._buffer)

                if buffer_length > self.max_message_size:
                    self._inside_frame = False
                    self._buffer = b''
                    raise HL7Exception(f'MLLP frame exceeds max_message_size ({self.max_message_size} bytes)')

                # .. otherwise, wait for more data.
                return None

            # .. extract the payload between start and end ..
            payload = self._buffer[:end_position]

            # .. advance the buffer past the end sequence ..
            end_of_frame = end_position + len(self.end_sequence)
            self._buffer = self._buffer[end_of_frame:]
            self._inside_frame = False

            # .. check that the extracted payload is within the size limit ..
            payload_length = len(payload)

            if payload_length > self.max_message_size:
                raise HL7Exception(f'MLLP frame exceeds max_message_size ({self.max_message_size} bytes)')

            # .. skip zero-byte payloads (empty frames are meaningless) ..
            if payload_length == 0:
                continue

            # .. we have a valid message.
            return payload

# ################################################################################################################################
# ################################################################################################################################

class FrameReader:
    """ Reads MLLP frames off one connection in two steps, so that the channel a message belongs
    to is known before the rest of that message is read.

    The first line is read under the listener's own bounds, because until it has been matched
    there is no channel whose bounds could apply. Everything after it is read under the bounds of
    the channel it matched.
    """

    def __init__(self, sock:'socket.socket', start_sequences:'list', read_buffer_size:'int') -> 'None':

        self.socket = sock

        # Any of the start sequences configured across all channels opens a frame. They are control
        # bytes that cannot occur in HL7 text, so accepting all of them makes nothing ambiguous.
        self.start_sequences = start_sequences
        self.read_buffer_size = read_buffer_size

        # One buffer for the life of the connection, consumed through an offset rather than
        # resliced, so a large message arriving in small reads is not copied over and over
        self._buffer = bytearray()
        self._offset = 0

        # Where the payload of the frame being read starts, once its opening sequence is behind us
        self._frame_start = 0

        # How much has to be kept when nothing frame-like has been found yet, so that an opening
        # sequence split across two reads is still recognised
        longest_start = max(len(sequence) for sequence in start_sequences)
        self._keep_tail = max(longest_start, len(Bare_Message_Prefix)) - 1

# ################################################################################################################################

    def _compact(self) -> 'None':
        """ Drops what has already been consumed, which is what keeps the buffer from growing
        for the life of a connection that carries thousands of messages.
        """
        if self._offset:
            del self._buffer[:self._offset]
            self._frame_start -= self._offset
            self._offset = 0

# ################################################################################################################################

    def _read_more(self, timeout:'float') -> 'bool':
        """ Waits for more bytes from the peer. Returns False when the peer disconnected.
        """
        self.socket.settimeout(timeout)
        chunk = self.socket.recv(self.read_buffer_size)

        # An empty read is the peer closing its end rather than a slow one
        if not chunk:
            return False

        self._buffer += chunk
        return True

# ################################################################################################################################

    def _find_frame_start(self) -> 'int':
        """ Returns where the payload of the next frame begins, or -1 when no opening has arrived
        yet. A sender that omits the opening sequence and starts at MSH is taken as it comes.
        """
        earliest = -1
        earliest_skip = 0

        for sequence in self.start_sequences:

            position = self._buffer.find(sequence, self._offset)

            if position != -1:
                if earliest == -1 or position < earliest:
                    earliest = position
                    earliest_skip = len(sequence)

        bare_position = self._buffer.find(Bare_Message_Prefix, self._offset)

        # A bare opening only counts when it comes first, so that the sequence of a properly
        # framed message is not skipped in favour of the MSH inside it
        if bare_position != -1:
            if earliest == -1 or bare_position < earliest:
                earliest = bare_position
                earliest_skip = 0

        if earliest == -1:
            return -1

        out = earliest + earliest_skip
        return out

# ################################################################################################################################

    def _find_routing_terminator(self, frame_start:'int') -> 'int':
        """ Returns where the first segment of the frame ends, whichever ending the sender used.
        """

        out = -1

        for terminator in _Routing_Terminators:

            position = self._buffer.find(terminator, frame_start)

            # The earliest ending is the one that closes the segment, the rest are inside the body
            if position != -1 and (out == -1 or position < out):
                out = position

        return out

# ################################################################################################################################

    def read_first_line(self, max_first_line_size:'int', idle_timeout:'float', first_line_timeout:'float') -> 'str | None':
        """ Reads up to the first segment terminator of the next frame and returns it as text,
        which is the MSH line the routing decision is made on. Returns None when the peer
        disconnected before another frame began.

        A connection that produces nothing at all is held for the idle deadline, and one that
        has begun a frame is held for the first-line deadline, so a silent peer and a slow
        one are told apart.
        """

        idle_deadline = monotonic() + idle_timeout
        line_deadline = 0.0

        while True:

            frame_start = self._find_frame_start()

            if frame_start != -1:

                self._frame_start = frame_start
                terminator = self._find_routing_terminator(frame_start)

                if terminator != -1:

                    # The MSH line is ASCII by definition, and only its fields are being read here -
                    # whatever encoding the body is in is the matched channel's business
                    out = self._buffer[frame_start:terminator].decode('ascii', errors='replace')
                    return out

                # A first line this long is not one, so nothing is gained by waiting for more
                if len(self._buffer) - frame_start > max_first_line_size:
                    raise HL7Exception('No segment terminator within the first line size limit')

                # The frame has begun, so the peer is no longer idle and has its own deadline
                if not line_deadline:
                    line_deadline = monotonic() + first_line_timeout

            else:

                # Nothing frame-like so far, so all but the tail that could hold a split
                # opening sequence is dropped rather than accumulated
                surplus = len(self._buffer) - self._offset - self._keep_tail

                if surplus > 0:
                    self._offset += surplus
                    self._compact()

            if line_deadline:
                deadline = line_deadline
                expired_message = 'No first line within the listener deadline'
            else:
                deadline = idle_deadline
                expired_message = 'Connection idle for longer than the listener allows'

            remaining = deadline - monotonic()

            if remaining <= 0:
                raise HL7Exception(expired_message)

            if not self._read_more(remaining):
                return None

# ################################################################################################################################

    def _find_frame_end(self, end_sequences:'list') -> 'tuple':
        """ Returns where the frame being read closes and how long the closing sequence was,
        taking whichever of the accepted sequences comes first.
        """
        earliest = -1
        earliest_length = 0

        for sequence in end_sequences:

            position = self._buffer.find(sequence, self._frame_start)

            if position != -1:
                if earliest == -1 or position < earliest:
                    earliest = position
                    earliest_length = len(sequence)

        out = (earliest, earliest_length)
        return out

# ################################################################################################################################

    def read_rest_of_frame(self, end_sequences:'list', max_message_size:'int', timeout:'float') -> 'bytes':
        """ Reads the remainder of the frame whose first line has already been read and returns
        the whole payload, framing removed, under the matched channel's own bounds.
        """

        deadline = monotonic() + timeout

        while True:

            end_position, end_length = self._find_frame_end(end_sequences)

            if end_position != -1:

                payload = bytes(self._buffer[self._frame_start:end_position])

                # What follows the closing sequence is the start of whatever comes next
                self._offset = end_position + end_length
                self._compact()

                if len(payload) > max_message_size:
                    raise HL7Exception(f'MLLP frame exceeds max_msg_size ({max_message_size} bytes)')

                return payload

            # There is no point reading further into a message already over the limit
            if len(self._buffer) - self._frame_start > max_message_size:

                # The connection is not resynchronised here - the caller answers the sender
                # and closes, because there is no way to tell where the oversized frame ends
                raise HL7Exception(f'MLLP frame exceeds max_msg_size ({max_message_size} bytes)')

            remaining = deadline - monotonic()

            if remaining <= 0:
                raise HL7Exception('Message not complete within the channel receive timeout')

            if not self._read_more(remaining):
                raise HL7Exception('Connection closed mid-frame')

# ################################################################################################################################
# ################################################################################################################################

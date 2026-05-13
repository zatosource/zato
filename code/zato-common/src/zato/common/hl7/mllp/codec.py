# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.hl7.exception import HL7Exception

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

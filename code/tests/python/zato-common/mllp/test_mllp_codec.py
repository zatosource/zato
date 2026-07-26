# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from zato.common.hl7.mllp.preprocess import split_concatenated_messages

# ################################################################################################################################
# ################################################################################################################################

_start_sequence = b'\x0b'
_end_sequence = b'\x1c\x0d'
_max_message_size = 1_000_000

_message = b'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CTRL001|P|2.5\rPID|||123'

# ################################################################################################################################
# ################################################################################################################################

def _new_decoder(max_message_size:'int'=_max_message_size) -> 'FrameDecoder':
    out = FrameDecoder(_start_sequence, _end_sequence, max_message_size)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAWholeFrame:
    """ What the decoder does with framing it has all of.
    """

    def test_a_framed_message_comes_back_unframed(self) -> 'None':
        decoder = _new_decoder()
        decoder.feed(frame_encode(_message, _start_sequence, _end_sequence))

        assert decoder.next_message() == _message

    def test_two_frames_in_one_feed_come_back_in_order(self) -> 'None':
        decoder = _new_decoder()

        first = b'MSH|^~\\&|A|A|A|A|20230101120000||ADT^A01|FIRST|P|2.5'
        second = b'MSH|^~\\&|B|B|B|B|20230101120000||ADT^A01|SECOND|P|2.5'

        decoder.feed(frame_encode(first, _start_sequence, _end_sequence))
        decoder.feed(frame_encode(second, _start_sequence, _end_sequence))

        assert decoder.next_message() == first
        assert decoder.next_message() == second
        assert decoder.next_message() is None

    def test_an_empty_frame_is_passed_over(self) -> 'None':
        decoder = _new_decoder()

        decoder.feed(frame_encode(b'', _start_sequence, _end_sequence))
        decoder.feed(frame_encode(_message, _start_sequence, _end_sequence))

        assert decoder.next_message() == _message

    def test_a_sender_that_omits_the_opening_is_still_read(self) -> 'None':
        decoder = _new_decoder()
        decoder.feed(_message + _end_sequence)

        assert decoder.next_message() == _message

# ################################################################################################################################
# ################################################################################################################################

class TestAFrameArrivingInPieces:
    """ A message reaching the decoder over several reads has to survive a chunk boundary
    landing anywhere in it, the opening included.
    """

    def test_nothing_comes_back_until_the_frame_closes(self) -> 'None':
        decoder = _new_decoder()
        decoder.feed(_start_sequence + _message)

        assert decoder.next_message() is None

        decoder.feed(_end_sequence)

        assert decoder.next_message() == _message

    def test_a_frame_split_byte_by_byte_still_arrives(self) -> 'None':
        decoder = _new_decoder()
        framed = frame_encode(_message, _start_sequence, _end_sequence)

        for index in range(len(framed) - 1):
            decoder.feed(framed[index:index + 1])
            assert decoder.next_message() is None

        decoder.feed(framed[-1:])

        assert decoder.next_message() == _message

    def test_a_boundary_inside_a_bare_header_keeps_the_message(self) -> 'None':
        decoder = _new_decoder()

        # A sender that omits the opening sequence begins at MSH, and the read that carries
        # the M and the S has to be held rather than dropped
        decoder.feed(b'MS')

        assert decoder.next_message() is None

        decoder.feed(_message[2:] + _end_sequence)

        assert decoder.next_message() == _message

    def test_junk_before_a_frame_is_not_accumulated(self) -> 'None':
        decoder = _new_decoder()

        for _ in range(1000):
            decoder.feed(b'0123456789')
            assert decoder.next_message() is None

        # Nothing frame-like arrived, so nothing but the tail an opening could be split
        # across is still being held
        assert len(decoder._buffer) < len(b'MSH')

    def test_junk_before_a_frame_does_not_lose_it(self) -> 'None':
        decoder = _new_decoder()

        decoder.feed(b'noise')
        assert decoder.next_message() is None

        decoder.feed(frame_encode(_message, _start_sequence, _end_sequence))

        assert decoder.next_message() == _message

# ################################################################################################################################
# ################################################################################################################################

class TestAFrameOverTheLimit:
    """ A frame past the size limit is refused rather than buffered further.
    """

    def test_an_oversized_frame_is_refused(self) -> 'None':
        decoder = _new_decoder(max_message_size=100)
        decoder.feed(_start_sequence + b'M' * 200)

        try:
            _ = decoder.next_message()
        except HL7Exception as e:
            assert 'exceeds max_message_size' in str(e)
        else:
            raise AssertionError('An oversized frame was not refused')

    def test_a_refusal_leaves_nothing_behind(self) -> 'None':
        decoder = _new_decoder(max_message_size=100)
        decoder.feed(_start_sequence + b'M' * 200)

        try:
            _ = decoder.next_message()
        except HL7Exception:
            pass

        assert len(decoder._buffer) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestSplittingOneFrameIntoMessages:
    """ A second message in one frame begins where a segment ended, so the split is anchored
    on the segment terminator and text that merely reads like a header stays text.
    """

    def test_two_messages_are_split_apart(self) -> 'None':
        first = 'MSH|^~\\&|A|A|A|A|20230101120000||ADT^A01|FIRST|P|2.5\rPID|||123\r'
        second = 'MSH|^~\\&|B|B|B|B|20230101120000||ORU^R01|SECOND|P|2.5\rPID|||456'

        out = split_concatenated_messages(first + second)

        assert out == [first, second]

    def test_a_single_message_comes_back_whole(self) -> 'None':
        message = 'MSH|^~\\&|A|A|A|A|20230101120000||ADT^A01|ONLY|P|2.5\rPID|||123'

        out = split_concatenated_messages(message)

        assert out == [message]

    def test_a_header_inside_a_field_is_not_a_second_message(self) -> 'None':
        message = (
            'MSH|^~\\&|A|A|A|A|20230101120000||ADT^A01|ONLY|P|2.5\r'
            'NTE|1||The sender said MSH|^~\\&| was rejected'
        )

        out = split_concatenated_messages(message)

        assert out == [message]

    def test_every_message_but_the_last_keeps_its_terminator(self) -> 'None':
        first = 'MSH|^~\\&|A|A|A|A|20230101120000||ADT^A01|FIRST|P|2.5\r'
        second = 'MSH|^~\\&|B|B|B|B|20230101120000||ORU^R01|SECOND|P|2.5\r'
        third = 'MSH|^~\\&|C|C|C|C|20230101120000||ORU^R01|THIRD|P|2.5'

        out = split_concatenated_messages(first + second + third)

        assert out == [first, second, third]

    def test_an_empty_payload_yields_nothing(self) -> 'None':
        assert split_concatenated_messages('') == []

# ################################################################################################################################
# ################################################################################################################################

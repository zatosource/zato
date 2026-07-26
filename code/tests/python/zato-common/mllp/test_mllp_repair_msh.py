# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.preprocess import repair_truncated_msh

# ################################################################################################################################
# ################################################################################################################################

# A header carrying every field the standard requires, which is what a repaired one is measured against
_whole_msh = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20260101120000||ADT^A01|MSG00001|P|2.5'

# How many pipe-separated parts that header has
_whole_length = 12

# ################################################################################################################################

def _field_count(data:'str') -> 'int':
    """ Returns how many pipe-separated parts the header of a message has.
    """
    msh_line = data.split('\r')[0]
    out = len(msh_line.split('|'))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAHeaderCutShortIsFilledOut(TestCase):
    """ A header that stops before MSH-12 leaves everything reading it by field number finding
    the end of the segment where a field should be, which is what the repair is named for.
    """

# ################################################################################################################################

    def test_a_header_missing_its_last_fields_is_padded(self) -> 'None':
        """ The fields that never arrived are there, empty.
        """
        repaired = repair_truncated_msh('MSH|^~\\&|SendApp|SendFac')

        self.assertEqual(_field_count(repaired), _whole_length)

# ################################################################################################################################

    def test_padding_keeps_the_fields_that_did_arrive(self) -> 'None':
        """ What the sender did say is left exactly where it said it.
        """
        repaired = repair_truncated_msh('MSH|^~\\&|SendApp|SendFac')

        fields = repaired.split('|')

        self.assertEqual(fields[1], '^~\\&')
        self.assertEqual(fields[2], 'SendApp')
        self.assertEqual(fields[3], 'SendFac')

# ################################################################################################################################

    def test_a_whole_header_is_left_alone(self) -> 'None':
        """ Nothing is missing, so nothing is added.
        """
        self.assertEqual(repair_truncated_msh(_whole_msh), _whole_msh)

# ################################################################################################################################

    def test_a_header_carrying_more_than_required_is_left_alone(self) -> 'None':
        """ MSH-13 onward are the sender's to send, and padding stops where the standard does.
        """
        with_extras = _whole_msh + '|123|456|789'

        self.assertEqual(repair_truncated_msh(with_extras), with_extras)

# ################################################################################################################################

    def test_only_the_header_is_padded(self) -> 'None':
        """ The segments after it are the message, not the header, and are untouched.
        """
        message = 'MSH|^~\\&|SendApp\rPID|||12345\rPV1||I'

        repaired = repair_truncated_msh(message)
        segments = repaired.split('\r')

        self.assertEqual(segments[1], 'PID|||12345')
        self.assertEqual(segments[2], 'PV1||I')

# ################################################################################################################################

    def test_a_padded_header_keeps_its_message(self) -> 'None':
        """ Padding the header does not cost the message the segments that followed it.
        """
        repaired = repair_truncated_msh('MSH|^~\\&|SendApp\rPID|||12345')

        self.assertEqual(len(repaired.split('\r')), 2)
        self.assertEqual(_field_count(repaired), _whole_length)

# ################################################################################################################################
# ################################################################################################################################

class TestTheRepairsThatWereAlreadyThere(TestCase):
    """ Padding is added alongside what the repair already did rather than in place of it.
    """

# ################################################################################################################################

    def test_a_header_that_lost_its_leading_m_gets_it_back(self) -> 'None':
        """ The first byte going missing is the commonest way a header arrives damaged.
        """
        repaired = repair_truncated_msh('SH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20260101120000||ADT^A01|MSG1|P|2.5')

        self.assertTrue(repaired.startswith('MSH|'))

# ################################################################################################################################

    def test_a_header_that_lost_its_leading_m_is_also_padded(self) -> 'None':
        """ Both repairs apply to one header, which is what running them in sequence gives.
        """
        repaired = repair_truncated_msh('SH|^~\\&|SendApp')

        self.assertTrue(repaired.startswith('MSH|'))
        self.assertEqual(_field_count(repaired), _whole_length)

# ################################################################################################################################

    def test_junk_ahead_of_the_header_is_stripped(self) -> 'None':
        """ Some senders prefix the message with a routing token of their own.
        """
        repaired = repair_truncated_msh('ORU_R01|' + _whole_msh)

        self.assertEqual(repaired, _whole_msh)

# ################################################################################################################################

    def test_a_message_with_no_header_at_all_is_left_alone(self) -> 'None':
        """ There is nothing here to repair, and inventing a header would be worse than not.
        """
        self.assertEqual(repair_truncated_msh('PID|||12345'), 'PID|||12345')

# ################################################################################################################################
# ################################################################################################################################

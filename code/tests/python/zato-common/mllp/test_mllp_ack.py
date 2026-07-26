# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.ack import (
    build_ack,
    Condition_Application_Error,
    Condition_Data_Type_Error,
    Condition_Unsupported_Message,
    Default_Encoding_Characters,
    validate_ack,
)

# ################################################################################################################################
# ################################################################################################################################

_sample_msh = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20260101120000||ADT^A01|MSG00001|P|2.5'

# ################################################################################################################################

def _get_segment(ack:'str', prefix:'str') -> 'str':
    """ Returns the one segment of an acknowledgment that opens with the given prefix, empty
    where the acknowledgment carries none.
    """

    for segment in ack.split('\r'):
        if segment.startswith(prefix):
            return segment

    return ''

# ################################################################################################################################
# ################################################################################################################################

class TestAMalformedHeaderIsStillAnswered(TestCase):
    """ A sender waiting on an acknowledgment has to get one whatever it sent, because a frame
    that cannot be read is exactly the frame its sender most needs to be told about.
    """

# ################################################################################################################################

    def test_a_header_with_no_field_separator_is_answered(self) -> 'None':
        """ The one case that used to end the connection instead of answering it.
        """
        ack = build_ack('MSH', 'AE', error_text='Message could not be read')

        self.assertIn('MSA|AE|', ack)

# ################################################################################################################################

    def test_a_header_with_no_field_separator_gets_the_standard_encoding_characters(self) -> 'None':
        """ An acknowledgment naming no encoding characters could not itself be read, so the
        standard ones stand in where the original named none.
        """
        ack = build_ack('MSH', 'AE', error_text='Message could not be read')

        self.assertTrue(ack.startswith(f'MSH|{Default_Encoding_Characters}|'))

# ################################################################################################################################

    def test_a_header_cut_short_is_answered(self) -> 'None':
        """ A header that stops before the fields the acknowledgment reads back is answered
        with those fields left empty.
        """
        ack = build_ack('MSH|^~\\&|SendApp', 'AE', error_text='Message could not be read')

        self.assertIn('MSA|AE|', ack)

# ################################################################################################################################

    def test_an_empty_header_is_answered(self) -> 'None':
        """ Nothing at all is still something to answer.
        """
        ack = build_ack('', 'AE', error_text='Message could not be read')

        self.assertIn('MSA|AE|', ack)

# ################################################################################################################################
# ################################################################################################################################

class TestTheReportedConditionMatchesWhatHappened(TestCase):
    """ ERR-3 is what a receiving system reads to find out what went wrong, so reporting an
    application error where the application was never reached tells it the wrong thing.
    """

# ################################################################################################################################

    def test_a_named_condition_is_the_one_reported(self) -> 'None':
        """ A caller that knows why the message failed says so and is taken at its word.
        """
        ack = build_ack(_sample_msh, 'AE', 'Message could not be read', Condition_Data_Type_Error)

        err_segment = _get_segment(ack, 'ERR|')
        self.assertIn(f'{Condition_Data_Type_Error.code}^{Condition_Data_Type_Error.text}^HL70357', err_segment)

# ################################################################################################################################

    def test_an_application_error_is_what_ae_reports(self) -> 'None':
        """ Where no condition is named, AE means the application itself failed.
        """
        ack = build_ack(_sample_msh, 'AE', error_text='Service raised')

        err_segment = _get_segment(ack, 'ERR|')
        self.assertIn(Condition_Application_Error.code, err_segment)

# ################################################################################################################################

    def test_a_reject_does_not_report_an_application_error(self) -> 'None':
        """ AR is the interface turning the message away, so reporting that the application
        failed internally would be untrue - this is what the old fixed code got wrong.
        """
        ack = build_ack(_sample_msh, 'AR', error_text='Not accepted')

        err_segment = _get_segment(ack, 'ERR|')

        self.assertNotIn(Condition_Application_Error.code, err_segment)
        self.assertIn(Condition_Unsupported_Message.code, err_segment)

# ################################################################################################################################

    def test_no_error_text_means_no_err_segment(self) -> 'None':
        """ A channel that hides its error details says nothing rather than saying it emptily.
        """
        ack = build_ack(_sample_msh, 'AR')

        self.assertEqual(_get_segment(ack, 'ERR|'), '')

# ################################################################################################################################
# ################################################################################################################################

class TestTheAcknowledgmentTimestamp(TestCase):
    """ MSH-7 with no offset is a time in a place the reader cannot know, which two systems in
    different zones cannot reconcile after the fact.
    """

# ################################################################################################################################

    def test_the_timestamp_carries_an_offset(self) -> 'None':
        """ The offset is what makes the time mean the same thing to both ends.
        """
        ack = build_ack(_sample_msh, 'AA')

        timestamp = ack.split('|')[6]
        self.assertTrue(timestamp.endswith('+0000'), f'MSH-7 carries no offset: {timestamp}')

# ################################################################################################################################

    def test_the_timestamp_is_the_time_in_utc(self) -> 'None':
        """ And the time it carries is the one the offset says it is.
        """
        before = datetime.now(timezone.utc).strftime('%Y%m%d%H%M')

        ack = build_ack(_sample_msh, 'AA')
        timestamp = ack.split('|')[6]

        self.assertTrue(timestamp.startswith(before), f'MSH-7 is not the time in UTC: {timestamp}')

# ################################################################################################################################
# ################################################################################################################################

class TestTheAcknowledgmentControlId(TestCase):
    """ MSH-10 identifies the acknowledgment itself. Handing the sender its own control id back
    means two acknowledgments raised in the same second cannot be told apart.
    """

# ################################################################################################################################

    def test_the_control_id_is_not_the_senders_own(self) -> 'None':
        """ MSA-2 is where the sender's control id belongs, and MSH-10 is not it.
        """
        ack = build_ack(_sample_msh, 'AA')

        self.assertNotIn('MSG00001', ack.split('|')[9])

# ################################################################################################################################

    def test_two_acknowledgments_to_one_message_differ(self) -> 'None':
        """ Raised back to back, and so within the same second, they are still distinguishable.
        """
        first = build_ack(_sample_msh, 'AA').split('|')[9]
        second = build_ack(_sample_msh, 'AA').split('|')[9]

        self.assertNotEqual(first, second)

# ################################################################################################################################

    def test_the_control_id_fits_the_field(self) -> 'None':
        """ MSH-10 holds twenty characters in the oldest version still in the field.
        """
        control_id = build_ack(_sample_msh, 'AA').split('|')[9]

        self.assertTrue(control_id)
        self.assertLessEqual(len(control_id), 20)

# ################################################################################################################################

    def test_the_senders_control_id_still_comes_back_in_msa(self) -> 'None':
        """ Which is what the sender correlates on, and is unaffected by the above.
        """
        ack = build_ack(_sample_msh, 'AA')

        self.assertIn('MSA|AA|MSG00001', ack)

# ################################################################################################################################
# ################################################################################################################################

class TestAnAcknowledgmentThatNamesAnotherMessage(TestCase):
    """ An acknowledgment whose MSA-2 is not the control id we sent is reported the way every
    other problem here is, rather than thrown at a caller holding an AckResult for everything else.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        self.ack = 'MSH|^~\\&|RecvApp|RecvFac|SendApp|SendFac|20260101120000||ACK|A1|P|2.5\rMSA|AA|OTHER'

# ################################################################################################################################

    def test_the_mismatch_is_reported_rather_than_raised(self) -> 'None':
        """ The caller gets a result, not an exception out of one branch of a function that
        returns one everywhere else.
        """
        result = validate_ack(self.ack, 'MSG00001')

        self.assertIn('MSG00001', result.error_text)
        self.assertIn('OTHER', result.error_text)

# ################################################################################################################################

    def test_a_mismatch_is_not_an_acceptance(self) -> 'None':
        """ Whatever the code says, an answer to another message accepts nothing of ours.
        """
        result = validate_ack(self.ack, 'MSG00001')

        self.assertFalse(result.is_accepted)

# ################################################################################################################################

    def test_a_mismatch_is_not_retried(self) -> 'None':
        """ Sending the same message again would not make the reply match, so retrying is
        left unset the way it is for every other permanent problem.
        """
        result = validate_ack(self.ack, 'MSG00001')

        self.assertFalse(result.should_retry)

# ################################################################################################################################

    def test_the_acknowledgment_is_kept_as_it_arrived(self) -> 'None':
        """ It is still what the audit trail stores, mismatch or not.
        """
        result = validate_ack(self.ack, 'MSG00001')

        self.assertEqual(result.ack_text, self.ack)

# ################################################################################################################################

    def test_a_matching_acknowledgment_is_unaffected(self) -> 'None':
        """ The ordinary path still reads the code it was given.
        """
        ack = 'MSH|^~\\&|RecvApp|RecvFac|SendApp|SendFac|20260101120000||ACK|A1|P|2.5\rMSA|AA|MSG00001'

        result = validate_ack(ack, 'MSG00001')

        self.assertTrue(result.is_accepted)
        self.assertEqual(result.error_text, '')

# ################################################################################################################################
# ################################################################################################################################

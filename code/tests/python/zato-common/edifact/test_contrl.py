# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.typing_ import cast_
from zato.edifact.contrl import Action_Acknowledged, Action_Rejected, Contrl, ContrlError, build_contrl, parse_contrl
from zato.edifact.envelope import parse_edifact

# ################################################################################################################################
# ################################################################################################################################

# A minimal interchange with two ORDERS messages.
_interchange = "UNB+UNOA:2+SENDER1+RECIPIENT1+260709:1200+REF001'" + \
    "UNH+1+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-1'" + \
    "UNT+3+1'" + \
    "UNH+2+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-2'" + \
    "UNT+3+2'" + \
    "UNZ+2+REF001'"

# ################################################################################################################################
# ################################################################################################################################

class TestContrl(unittest.TestCase):

    maxDiff = None

    def test_acknowledge_all(self) -> None:
        interchange = parse_edifact(_interchange)

        ack = build_contrl(interchange)
        serialized = ack.serialize()

        reparsed = parse_edifact(serialized)

        # The acknowledgment is addressed back at the sender
        self.assertEqual(reparsed.header.sender.identification, 'RECIPIENT1')
        self.assertEqual(reparsed.header.recipient.identification, 'SENDER1')

        result = parse_contrl(reparsed)

        self.assertEqual(result.interchange_reference, 'REF001')
        self.assertEqual(result.action_code, Action_Acknowledged)
        self.assertTrue(result.is_accepted)

        self.assertEqual(len(result.message_results), 2)

        first = result.message_results[0]
        self.assertEqual(first.message_reference, '1')
        self.assertEqual(first.message_type, 'ORDERS')
        self.assertTrue(first.is_accepted)
        self.assertEqual(first.errors, [])

        second = result.message_results[1]
        self.assertEqual(second.message_reference, '2')
        self.assertTrue(second.is_accepted)

    def test_reject_one_message(self) -> None:
        interchange = parse_edifact(_interchange)

        # The second message is rejected with a segment and element error
        errors = {'2': [ContrlError(2, '12', element_position=1, component_position=2)]}

        ack = build_contrl(interchange, errors)
        result = parse_contrl(parse_edifact(ack.serialize()))

        # One message is still fine, so the interchange as a whole is acknowledged
        self.assertEqual(result.action_code, Action_Acknowledged)

        first = result.message_results[0]
        self.assertTrue(first.is_accepted)

        second = result.message_results[1]
        self.assertEqual(second.action_code, Action_Rejected)
        self.assertEqual(second.error_code, '12')
        self.assertFalse(second.is_accepted)

        error = second.errors[0]
        self.assertEqual(error.segment_position, 2)
        self.assertEqual(error.error_code, '12')
        self.assertEqual(error.element_position, 1)
        self.assertEqual(error.component_position, 2)

    def test_reject_all_messages(self) -> None:
        interchange = parse_edifact(_interchange)

        errors = {
            '1': [ContrlError(2, '16')],
            '2': [ContrlError(3, '18')],
        }

        ack = build_contrl(interchange, errors)
        result = parse_contrl(parse_edifact(ack.serialize()))

        # With every message rejected the whole interchange is too
        self.assertEqual(result.action_code, Action_Rejected)
        self.assertFalse(result.is_accepted)

        # A segment error without element detail stays a bare UCS
        first_error = result.message_results[0].errors[0]
        self.assertEqual(first_error.segment_position, 2)
        self.assertEqual(first_error.error_code, '16')
        self.assertEqual(first_error.element_position, 0)

    def test_segment_count(self) -> None:
        interchange = parse_edifact(_interchange)

        ack = build_contrl(interchange)
        message = cast_(Contrl, ack.message)

        # UNH, UCI, two UCM and UNT
        self.assertEqual(message.unt.segment_count, '5')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################

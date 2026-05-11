# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import parse_message

# ################################################################################################################################
# ################################################################################################################################

_MSH_Only_Message = (
    'MSH|^~\\&|KLINx||AUFN||20260401112408||ADT^A01^ADT_A01|77|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||'
    '2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestSingleSegmentParsing(unittest.TestCase):
    """ A message containing only an MSH segment must parse successfully
    instead of raising 'Segment cursor exhausted'.
    """

    def test_msh_only_message_parses(self) -> 'None':
        """ Parsing a single-segment MSH-only message must not raise an exception.
        """
        message = parse_message(_MSH_Only_Message)
        self.assertIsNotNone(message)

    def test_msh_only_sending_application(self) -> 'None':
        """ The sending application must be accessible on a single-segment message.
        """
        message = parse_message(_MSH_Only_Message)

        out = message.get('MSH.3')
        self.assertEqual(out, 'KLINx')

    def test_msh_only_message_control_id(self) -> 'None':
        """ The message control ID must be accessible on a single-segment message.
        """
        message = parse_message(_MSH_Only_Message)

        out = message.get('MSH.10')
        self.assertEqual(out, '77')

    def test_msh_only_version(self) -> 'None':
        """ The version must be accessible on a single-segment message.
        """
        message = parse_message(_MSH_Only_Message)

        out = message.get('MSH.12')
        self.assertEqual(out, '2.5')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

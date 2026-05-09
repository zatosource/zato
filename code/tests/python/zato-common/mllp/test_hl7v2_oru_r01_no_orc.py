# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato_hl7v2.v2_9 import parse_message

# ################################################################################################################################
# ################################################################################################################################

_ORU_R01_Without_ORC = (
    'MSH|^~\\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1\r'
    'PID|1|5678||43218765\r'
    'PV1|1||SC110|\r'
    'OBX|1|NM|RASS||-4|||||||||202601010600\r'
    'OBX|2|ST|PupilleLinks||e+k|||||||||202612301330\r'
    'OBX|3|ST|PupilleRechts||e+k|||||||||202601010600\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestORUR01WithoutORC(unittest.TestCase):
    """ Real-world ORU^R01 messages from ICU systems can have OBX segments
    without a preceding ORC. These must parse successfully.
    """

    def test_parse_succeeds(self) -> 'None':
        """ Parsing an ORU^R01 without ORC must not raise an exception.
        """
        message = parse_message(_ORU_R01_Without_ORC, validate=False)
        self.assertIsNotNone(message)

    def test_obx_set_id(self) -> 'None':
        """ OBX-1 must be reachable and return '1' for the first OBX.
        """
        message = parse_message(_ORU_R01_Without_ORC, validate=False)

        out = message.get('OBX.1')
        self.assertEqual(out, '1')

    def test_obx_observation_identifier(self) -> 'None':
        """ OBX-3 must return the observation identifier 'RASS'.
        """
        message = parse_message(_ORU_R01_Without_ORC, validate=False)

        out = message.get('OBX.3')
        self.assertEqual(out, 'RASS')

    def test_obx_observation_value(self) -> 'None':
        """ OBX-5 must return the observation value '-4'.
        """
        message = parse_message(_ORU_R01_Without_ORC, validate=False)

        out = message.get('OBX.5')
        self.assertEqual(out, '-4')

    def test_pid_reachable(self) -> 'None':
        """ PID-2 must be reachable and return '5678'.
        """
        message = parse_message(_ORU_R01_Without_ORC, validate=False)

        out = message.get('PID.2')
        self.assertEqual(out, '5678')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

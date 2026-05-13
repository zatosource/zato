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

_Message_With_UTF8 = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestTolerancePreservesUTF8(unittest.TestCase):
    """ The top-level parse_message applies tolerance by default.
    UTF-8 characters must survive tolerance processing
    without mojibake.
    """

    def test_patient_name_preserves_umlaut(self) -> 'None':
        """ PID-5 must return 'Grünwald' not 'GrÃ¼nwald'.
        """
        message = parse_message(_Message_With_UTF8, validate=False)

        out = message.get('PID.5')
        self.assertEqual(out, 'Grünwald')

    def test_sending_facility_preserves_umlaut(self) -> 'None':
        """ MSH-4 must return 'STÄDTISCH_KH' not 'STÃ\x84DTISCH_KH'.
        """
        message = parse_message(_Message_With_UTF8, validate=False)

        out = message.get('MSH.4')
        self.assertEqual(out, 'STÄDTISCH_KH')

    def test_patient_address_preserves_eszett(self) -> 'None':
        """ PID-11 must preserve the eszett in 'Böttcherstraße'.
        """
        message = parse_message(_Message_With_UTF8, validate=False)

        out = message.get('PID.11')
        self.assertIsNotNone(out)
        self.assertIn('Böttcherstraße', out)

    def test_receiving_facility_preserves_umlaut(self) -> 'None':
        """ MSH-6 must return 'RÖNTGEN_KH' not 'RÃ\x96NTGEN_KH'.
        """
        message = parse_message(_Message_With_UTF8, validate=False)

        out = message.get('MSH.6')
        self.assertEqual(out, 'RÖNTGEN_KH')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

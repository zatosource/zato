# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato_hl7v2 import parse_message

# ################################################################################################################################
# ################################################################################################################################

_Message_With_Direct_UTF8 = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestDirectUTF8Roundtrip(unittest.TestCase):
    """ Direct UTF-8 characters (like German umlauts) in the ER7 wire format
    must survive parsing and be accessible without mojibake.
    """

    def test_umlaut_in_sending_facility(self) -> 'None':
        """ MSH-4 with 'STÄDTISCH_KH' must preserve the umlaut.
        """
        message = parse_message(_Message_With_Direct_UTF8)

        out = message.get('MSH.4')
        self.assertEqual(out, 'STÄDTISCH_KH')

    def test_umlaut_in_receiving_facility(self) -> 'None':
        """ MSH-6 with 'RÖNTGEN_KH' must preserve the umlaut.
        """
        message = parse_message(_Message_With_Direct_UTF8)

        out = message.get('MSH.6')
        self.assertEqual(out, 'RÖNTGEN_KH')

    def test_eszett_in_patient_address(self) -> 'None':
        """ PID-11 with 'Böttcherstraße' must preserve the eszett.
        """
        message = parse_message(_Message_With_Direct_UTF8)

        out = message.get('PID.11')
        self.assertIsNotNone(out)
        self.assertIn('Böttcherstraße', out)

    def test_umlaut_in_patient_name(self) -> 'None':
        """ PID-5 first component 'Grünwald' must preserve the umlaut.
        """
        message = parse_message(_Message_With_Direct_UTF8)

        out = message.get('PID.5')
        self.assertEqual(out, 'Grünwald')

    def test_serialize_roundtrip_preserves_utf8(self) -> 'None':
        """ Parse then serialize must preserve UTF-8 characters.
        """
        message = parse_message(_Message_With_Direct_UTF8)

        serialized = message.serialize()
        self.assertIn('STÄDTISCH_KH', serialized)
        self.assertIn('RÖNTGEN_KH', serialized)
        self.assertIn('Grünwald', serialized)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

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

_ADT_A01_Message = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

_Message_With_Extended_MSH = (
    'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\r'
    'EVN|A08|202604061019\r'
    'PID|1||5566^^^&www.praxis.de&DNS^PI||Größe^Frédérique||19560318|F\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestMSHNavigationOffByOne(unittest.TestCase):
    """ msg.get('MSH.N') must return the value at HL7 position N,
    not the value at position N+1.
    """

    def test_msh3_sending_application(self) -> 'None':
        """ MSH-3 must return the sending application, not the sending facility.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.3')
        self.assertEqual(out, 'KLINIK_SND')

    def test_msh4_sending_facility(self) -> 'None':
        """ MSH-4 must return the sending facility.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.4')
        self.assertEqual(out, 'STÄDTISCH_KH')

    def test_msh5_receiving_application(self) -> 'None':
        """ MSH-5 must return the receiving application.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.5')
        self.assertEqual(out, 'LABOR_EMP')

    def test_msh6_receiving_facility(self) -> 'None':
        """ MSH-6 must return the receiving facility.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.6')
        self.assertEqual(out, 'RÖNTGEN_KH')

    def test_msh7_date_time(self) -> 'None':
        """ MSH-7 must return the date/time of message.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.7')
        self.assertEqual(out, '20260315083000')

    def test_msh9_message_type(self) -> 'None':
        """ MSH-9 must return the message type (first component is 'ADT').
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.9')
        self.assertEqual(out, 'ADT')

    def test_msh10_message_control_id(self) -> 'None':
        """ MSH-10 must return the message control ID.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.10')
        self.assertEqual(out, 'CTL00001')

    def test_msh11_processing_id(self) -> 'None':
        """ MSH-11 must return the processing ID.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.11')
        self.assertEqual(out, 'P')

    def test_msh12_version(self) -> 'None':
        """ MSH-12 must return the version ID.
        """
        message = parse_message(_ADT_A01_Message)

        out = message.get('MSH.12')
        self.assertEqual(out, '2.6')

    def test_msh13_sequence_number(self) -> 'None':
        """ MSH-13 must return the sequence number from an extended MSH.
        """
        message = parse_message(_Message_With_Extended_MSH)

        out = message.get('MSH.13')
        self.assertEqual(out, '9E72B53F8AC791B')

    def test_msh15_accept_ack(self) -> 'None':
        """ MSH-15 must return the accept acknowledgment type.
        """
        message = parse_message(_Message_With_Extended_MSH)

        out = message.get('MSH.15')
        self.assertEqual(out, 'AL')

    def test_msh16_application_ack(self) -> 'None':
        """ MSH-16 must return the application acknowledgment type.
        """
        message = parse_message(_Message_With_Extended_MSH)

        out = message.get('MSH.16')
        self.assertEqual(out, 'NE')

    def test_msh18_character_set(self) -> 'None':
        """ MSH-18 must return the character set.
        """
        message = parse_message(_Message_With_Extended_MSH)

        out = message.get('MSH.18')
        self.assertEqual(out, '8859/1')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

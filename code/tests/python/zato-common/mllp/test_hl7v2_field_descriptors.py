# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import parse_message
from zato.hl7v2.base import HL7Field
from zato.hl7v2.v2_9.segments import EVN, PID

# ################################################################################################################################
# ################################################################################################################################

_Message_With_EVN1 = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

_Message_With_PID13 = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00002|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^^||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||'
    '^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe@example.de\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

_Message_With_PID2_PID4 = (
    'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK|20260401151846+0200||ADT^A08^ADT_A01|740298561|P|2.5||||||UNICODE UTF-8\r'
    'EVN|A08|202604011516+0200\r'
    'PID|1|56789|xbc3def912a^^^&www.praxis.de&DNS^PI~56789^^^^PT||Überström^Rikård||19880913|M\r'
    'PV1|1|U\r'
)

_Message_With_PID19 = (
    'MSH|^~\\&|SENDE_APP|SENDE_KH|EMPFANGS_APP|EMPFANGS_KH|20260613083617||ADT^A04|934576120260613|P|2.3||||\r'
    'EVN|A04|20260613083617|||\r'
    'PID|1||246813||MÜNCHHAUSEN^THÉODOR||19550718|M|||Brückenstraße 5^^Zürich^ZH^8001||(044)9391289|||||||2847|99999999\r'
    'PV1|1|O\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestEVNFieldDescriptors(unittest.TestCase):
    """ Verify that the EVN segment has an HL7Field descriptor for event_type_code (EVN-1).
    """

    def test_evn_event_type_code_descriptor_exists(self) -> 'None':
        """ EVN must declare event_type_code at position 1.
        """
        descriptor = getattr(EVN, 'event_type_code', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_evn_event_type_code_position(self) -> 'None':
        """ The event_type_code descriptor must be at position 1.
        """
        descriptor = EVN.event_type_code
        self.assertEqual(descriptor.position, 1)

    def test_evn_event_type_code_parsed_value(self) -> 'None':
        """ Parsing a message with EVN-1 populated must return the correct value.
        """
        message = parse_message(_Message_With_EVN1)

        out = message.evn.event_type_code
        self.assertEqual(out, 'A01')

# ################################################################################################################################
# ################################################################################################################################

class TestPIDFieldDescriptors(unittest.TestCase):
    """ Verify that PID has HL7Field descriptors for previously-missing positions.
    """

    def test_pid_phone_number_home_descriptor_exists(self) -> 'None':
        """ PID must declare phone_number_home at position 13.
        """
        descriptor = getattr(PID, 'phone_number_home', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_phone_number_home_position(self) -> 'None':
        """ The phone_number_home descriptor must be at position 13.
        """
        descriptor = PID.phone_number_home
        self.assertEqual(descriptor.position, 13)

    def test_pid_phone_number_business_descriptor_exists(self) -> 'None':
        """ PID must declare phone_number_business at position 14.
        """
        descriptor = getattr(PID, 'phone_number_business', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_patient_id_descriptor_exists(self) -> 'None':
        """ PID must declare patient_id at position 2.
        """
        descriptor = getattr(PID, 'patient_id', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_alternate_patient_id_descriptor_exists(self) -> 'None':
        """ PID must declare alternate_patient_id at position 4.
        """
        descriptor = getattr(PID, 'alternate_patient_id', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_ssn_number_descriptor_exists(self) -> 'None':
        """ PID must declare ssn_number at position 19.
        """
        descriptor = getattr(PID, 'ssn_number', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_nationality_descriptor_exists(self) -> 'None':
        """ PID must declare nationality at position 28.
        """
        descriptor = getattr(PID, 'nationality', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_patient_id_parsed_value(self) -> 'None':
        """ Parsing a message with PID-2 populated must return the value.
        """
        message = parse_message(_Message_With_PID2_PID4)

        out = message.pid.patient_id
        self.assertEqual(out, '56789')

    def test_pid_ssn_number_parsed_value(self) -> 'None':
        """ Parsing a message with PID-19 populated must return the value.
        """
        message = parse_message(_Message_With_PID19)

        out = message.pid.ssn_number
        self.assertEqual(out, '2847')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

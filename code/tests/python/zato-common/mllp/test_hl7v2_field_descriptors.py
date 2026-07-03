# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.typing_ import cast_
from zato.hl7v2 import parse_hl7
from zato.hl7v2.base import HL7Field
from zato.hl7v2.v2_9.messages import ADT_A01
from zato.hl7v2.v2_9.segments import EVN, PID

# ################################################################################################################################
# ################################################################################################################################

_Message_With_EVN2 = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
)

_Message_With_PID1_PID7 = (
    'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK|20260401151846+0200||ADT^A08^ADT_A01|740298561|P|2.5||||||UNICODE UTF-8\r'
    'EVN|A08|202604011516+0200\r'
    'PID|1||xbc3def912a^^^&www.praxis.de&DNS^PI~56789^^^^PT||Überström^Rikård||19880913|M\r'
    'PV1|1|U\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestEVNFieldDescriptors(unittest.TestCase):
    """ Verify that the EVN segment exposes HL7Field descriptors as defined by the v2.9 XSD.
    """

    def test_evn_recorded_date_time_descriptor_exists(self) -> 'None':
        """ EVN must declare recorded_date_time at position 2.
        """
        descriptor = getattr(EVN, 'recorded_date_time', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_evn_recorded_date_time_position(self) -> 'None':
        """ The recorded_date_time descriptor must be at position 2.
        """
        descriptor = EVN.recorded_date_time
        self.assertEqual(descriptor.position, 2)

    def test_evn_recorded_date_time_parsed_value(self) -> 'None':
        """ Parsing a message with EVN-2 populated must return the correct value.
        """
        message = cast_('ADT_A01', parse_hl7(_Message_With_EVN2))

        out = message.evn.recorded_date_time
        self.assertEqual(out, '20260315083000')

# ################################################################################################################################
# ################################################################################################################################

class TestPIDFieldDescriptors(unittest.TestCase):
    """ Verify that PID exposes HL7Field descriptors as defined by the v2.9 XSD.
    """

    def test_pid_set_id_pid_descriptor_exists(self) -> 'None':
        """ PID must declare set_id_pid at position 1.
        """
        descriptor = getattr(PID, 'set_id_pid', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_set_id_pid_position(self) -> 'None':
        """ The set_id_pid descriptor must be at position 1.
        """
        descriptor = PID.set_id_pid
        self.assertEqual(descriptor.position, 1)

    def test_pid_patient_identifier_list_descriptor_exists(self) -> 'None':
        """ PID must declare patient_identifier_list at position 3.
        """
        descriptor = getattr(PID, 'patient_identifier_list', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_patient_name_descriptor_exists(self) -> 'None':
        """ PID must declare patient_name at position 5.
        """
        descriptor = getattr(PID, 'patient_name', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_patient_account_number_descriptor_exists(self) -> 'None':
        """ PID must declare patient_account_number at position 18.
        """
        descriptor = getattr(PID, 'patient_account_number', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_citizenship_descriptor_exists(self) -> 'None':
        """ PID must declare citizenship at position 26.
        """
        descriptor = getattr(PID, 'citizenship', None)
        self.assertIsNotNone(descriptor)
        self.assertIsInstance(descriptor, HL7Field)

    def test_pid_set_id_pid_parsed_value(self) -> 'None':
        """ Parsing a message with PID-1 populated must return the value.
        """
        message = cast_('ADT_A01', parse_hl7(_Message_With_PID1_PID7))

        out = message.pid.set_id_pid
        self.assertEqual(out, '1')

    def test_pid_date_time_of_birth_parsed_value(self) -> 'None':
        """ Parsing a message with PID-7 populated must return the value.
        """
        message = cast_('ADT_A01', parse_hl7(_Message_With_PID1_PID7))

        out = message.pid.date_time_of_birth
        self.assertEqual(out, '19880913')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

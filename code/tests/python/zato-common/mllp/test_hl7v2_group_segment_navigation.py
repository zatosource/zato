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

_ADT_A01_With_Insurance = (
    'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\r'
    'EVN|A01|20260315083000\r'
    'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402\r'
    'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie\r'
    'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49\r'
)

_ADT_A40_With_Merge = (
    'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A40|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\r'
    'EVN|A40|202604081715\r'
    'PID|1||5566^^^&www.praxis.de&DNS^PI||Größe^Frédérique||19560318|F|||Brückenweg 23^^Düsseldorf^^40545^DE^L\r'
    'MRG|9876~q283746bcde^^^&www.praxis.de&DNS||\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestGroupNavigationIN1(unittest.TestCase):
    """ msg.get() must be able to reach IN1 segments
    that live inside the INSURANCE group of ADT_A01 messages.
    """

    def test_in1_set_id(self) -> 'None':
        """ IN1-1 (set_id) must be reachable via msg.get().
        """
        message = parse_message(_ADT_A01_With_Insurance)

        out = message.get('IN1.1')
        self.assertEqual(out, '1')

    def test_in1_insurance_company_id(self) -> 'None':
        """ IN1-3 (insurance_company_id) must be reachable via msg.get().
        """
        message = parse_message(_ADT_A01_With_Insurance)

        out = message.get('IN1.3')
        self.assertEqual(out, 'KV001')

    def test_in1_insurance_company_name(self) -> 'None':
        """ IN1-4 (insurance_company_name) must be reachable via msg.get().
        """
        message = parse_message(_ADT_A01_With_Insurance)

        out = message.get('IN1.4')
        self.assertEqual(out, 'BÜRGERKRANKENVERSICHERUNG')

    def test_in1_insureds_id_number(self) -> 'None':
        """ IN1-49 (insureds_id_number) must be reachable via msg.get().
        """
        message = parse_message(_ADT_A01_With_Insurance)

        out = message.get('IN1.49')
        self.assertEqual(out, '49')

# ################################################################################################################################
# ################################################################################################################################

class TestGroupNavigationMRG(unittest.TestCase):
    """ msg.get() must reach MRG segments inside groups
    in ADT_A40 merge messages.
    """

    def test_mrg_prior_patient_id(self) -> 'None':
        """ MRG-1 first repetition must be reachable via msg.get().
        """
        message = parse_message(_ADT_A40_With_Merge)

        out = message.get('MRG.1')
        self.assertEqual(out, '9876')

    def test_pid_inside_group(self) -> 'None':
        """ PID inside an ADT_A40 group must be reachable.
        """
        message = parse_message(_ADT_A40_With_Merge)

        out = message.get('PID.1')
        self.assertEqual(out, '1')

    def test_pid_patient_name_inside_group(self) -> 'None':
        """ PID-5 inside an ADT_A40 group must return the patient name.
        """
        message = parse_message(_ADT_A40_With_Merge)

        out = message.get('PID.5')
        self.assertEqual(out, 'Größe')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

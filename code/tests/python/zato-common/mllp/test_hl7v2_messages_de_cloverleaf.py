# -*- coding: utf-8 -*-
# ruff: noqa: F405

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest

# Zato
from zato.hl7v2.v2_9 import parse_message
from zato.hl7v2.v2_9.segments import *  # noqa: F403
from zato.hl7v2.v2_9.datatypes import *  # noqa: F403
from zato.hl7v2.v2_9.messages import *  # noqa: F403

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_01 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202603151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO\rEVN||202603151705||||202603151645\rPID|||8901234^^^Birken-Klinik^PI||Pfeiffer^Lörchen^^^^^L^A^^^G~Hübner^^^^^^M^A^^^G~Pfeiffer^^^^Frau^^D^^^^G||19860419|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^70173^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^70173^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Marienhospital Süd|||DEU^German^HL70171^^deutsch\rPV1|1|I|CHI^302^2^IN^^N^A^4|R|||820301^Böttcher^Thëodor^^^Dr.^^^Birken-Klinik^L^^^DN^^^DN^^G||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202603151645\rPV2|||||||||20250405|4\rZBE|4567^KIS|202603151705||INSERT'

class Test_de_cloverleaf_01_1_ADT_A01_admission_standard_HL7_D_profile_v2_5(unittest.TestCase):
    """ 1. ADT^A01 - admission, standard (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202603151705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/15')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.19.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.19.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.38')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202603151705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202603151645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '8901234')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Pfeiffer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Lörchen')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Hübner')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[2]')
        self.assertEqual(result, 'Pfeiffer')

# ################################################################################################################

    def test_navigate_PID_5_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[2].5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_5_2_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[2].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_2_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.5[2].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19860419')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '70173')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1].5')
        self.assertEqual(result, '70173')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.15.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_15_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.15.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verheiratet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.17.2')
        self.assertEqual(result, 'catholic')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_17_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.17.5')
        self.assertEqual(result, 'katholisch')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.26.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PID_26_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PID.26.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '302')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '820301')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Böttcher')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Thëodor')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.7.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202603151645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20250405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_01, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202603151705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/15'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.38', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202603151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202603151705'
        segment.event_occurred = '202603151645'

        serialized = segment.serialize()
        expected = 'EVN||202603151705||||202603151645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='8901234', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Pfeiffer', xpn_2='Lörchen', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Hübner', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Pfeiffer', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        segment.date_time_of_birth = '19860419'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_5='70173', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_5='70173', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        segment.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        serialized = segment.serialize()
        expected = 'PID|||8901234^^^Birken-Klinik^PI||Pfeiffer^Lörchen^^^^^L^A^^^G~Hübner^^^^^^M^A^^^G~Pfeiffer^^^^Frau^^D^^^^G||19860419|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^70173^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^70173^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Marienhospital Süd|||DEU^German^HL70171^^deutsch'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='820301', xcn_2='Böttcher', xcn_3='Thëodor', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202603151645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^302^2^IN^^N^A^4|R|||820301^Böttcher^Thëodor^^^Dr.^^^Birken-Klinik^L^^^DN^^^DN^^G||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202603151645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20250405'
        segment.estimated_length_of_inpatient_stay = '4'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20250405|4'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202603151705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/15'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.38', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202603151705'
        message.evn.event_occurred = '202603151645'

        message.pid.patient_identifier_list = CX(cx_1='8901234', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Pfeiffer', xpn_2='Lörchen', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Hübner', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Pfeiffer', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        message.pid.date_time_of_birth = '19860419'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_5='70173', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_5='70173', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='820301', xcn_2='Böttcher', xcn_3='Thëodor', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202603151645'

        message.pv2.expected_discharge_date_time = '20250405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_02 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||022604011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|URO^301^1^IN^^N^A^4|R|||820303^Rüttger^Frïedrich^^^Dr.^^^Birken-Klinik^L^^^DN|820311^Zöllner^Wïlhelm^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N\rZBE|4567^KIS|202604011705||INSERT'

class Test_de_cloverleaf_02_2_ADT_A01_admission_with_DRG_HL7_D_profile_v2_5(unittest.TestCase):
    """ 2. ADT^A01 - admission with DRG (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.39')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '022604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Grüber')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'URO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '301')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '820303')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Rüttger')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, '820311')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Zöllner')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Wïlhelm')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_8_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.15')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_8_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.8.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.13')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.18')
        self.assertEqual(result, 'E')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.3')
        self.assertEqual(result, '0101')

# ################################################################################################################

    def test_navigate_PV2_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.3.2')
        self.assertEqual(result, 'vollstationär, Normalfall')

# ################################################################################################################

    def test_navigate_PV2_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.3.3')
        self.assertEqual(result, 'GSG0001')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_02, validate=False)
        result = message.get('PV2.37')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.39', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.event_occurred = '022604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||022604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='820303', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN')
        segment.referring_doctor = XCN(xcn_1='820311', xcn_2='Zöllner', xcn_3='Wïlhelm', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        segment.re_admission_indicator = CWE(cwe_1='R')
        segment.patient_type = CWE(cwe_1='E')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|URO^301^1^IN^^N^A^4|R|||820303^Rüttger^Frïedrich^^^Dr.^^^Birken-Klinik^L^^^DN|820311^Zöllner^Wïlhelm^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.admit_reason = CWE(cwe_1='0101', cwe_2='vollstationär, Normalfall', cwe_3='GSG0001')
        segment.expected_discharge_date_time = '20260405'
        segment.estimated_length_of_inpatient_stay = '4'
        segment.newborn_baby_indicator = 'N'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.39', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '022604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='820303', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.referring_doctor = XCN(xcn_1='820311', xcn_2='Zöllner', xcn_3='Wïlhelm', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        message.pv1.re_admission_indicator = CWE(cwe_1='R')
        message.pv1.patient_type = CWE(cwe_1='E')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.admit_reason = CWE(cwe_1='0101', cwe_2='vollstationär, Normalfall', cwe_3='GSG0001')
        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'
        message.pv2.newborn_baby_indicator = 'N'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_03 = 'MSH|^~\\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO\rSFT|RIS System GmbH^L|3.4|superRIS\rMSA|CA|ADT001'

class Test_de_cloverleaf_03_3_ACK_A01_transport_acknowledgment_HL7_D_profile_v2_5(unittest.TestCase):
    """ 3. ACK^A01 - transport acknowledgment (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.9')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'RIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '3.4')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'superRIS')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_03, validate=False)
        result = message.get('MSA.2')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='RIS')
        segment.receiving_application = HD(hd_1='KIS')
        segment.date_time_of_message = '202604011706'
        segment.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        segment.message_control_id = 'RIS002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.9', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='RIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '3.4'
        segment.software_product_name = 'superRIS'

        serialized = segment.serialize()
        expected = 'SFT|RIS System GmbH^L|3.4|superRIS'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MSA(self) -> 'None':
        segment = MSA()

        segment.acknowledgment_code = 'CA'
        segment.message_control_id = 'ADT001'

        serialized = segment.serialize()
        expected = 'MSA|CA|ADT001'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ACK()

        message.msh.sending_application = HD(hd_1='RIS')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.date_time_of_message = '202604011706'
        message.msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        message.msh.message_control_id = 'RIS002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.9', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='RIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '3.4'
        message.sft.software_product_name = 'superRIS'

        message.msa.acknowledgment_code = 'CA'
        message.msa.message_control_id = 'ADT001'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_04 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO\rEVN||202606051705||||022606051645\rPID|||34567^^^Eichen-Krankenhaus^PI||Hölzl^Bërndt^^^Dr.^^L^A^^^G~Hölzl^Bërndt^^^Herr Dr.^^D^A^^^G||19690117|F|||Schillerweg 44&Schillerweg&44^^Augsburg^^86150^^H||^PRN^PH^^49^821^4681357^^^^^0821/4681357|^WPN^PH^^49^821^97531^^^^^0821/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|HNO^201^2^IN^^N^A^4|R|||820303^Rüttger^Frïedrich^^^Dr.^^^Eichen-Krankenhaus^L^^^^^^DN ||||||||||||418263^^^Eichen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645\rPV2|||||||||20260615|10\rZBE|71823^KIS|202606051705||INSERT'

class Test_de_cloverleaf_04_4_ADT_A01_admission_with_billing_HL7_D_profile_v2_5(unittest.TestCase):
    """ 4. ADT^A01 - admission with billing (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.40')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '022606051645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Eichen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Hölzl')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bërndt')

# ################################################################################################################

    def test_navigate_PID_5_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0].5')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Hölzl')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Bërndt')

# ################################################################################################################

    def test_navigate_PID_5_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1].5')
        self.assertEqual(result, 'Herr Dr.')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19690117')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Schillerweg 44')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Schillerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11.1.3')
        self.assertEqual(result, '44')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Augsburg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '86150')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '201')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '820303')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Rüttger')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Eichen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN ')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '418263')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Eichen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_20(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.20')
        self.assertEqual(result, '01100000')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_25(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.25')
        self.assertEqual(result, '202401')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202606051645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260615')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_04, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '10')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202606051705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.40', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202606051705'
        segment.event_occurred = '022606051645'

        serialized = segment.serialize()
        expected = 'EVN||202606051705||||022606051645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Eichen-Krankenhaus', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Hölzl', xpn_2='Bërndt', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Hölzl', xpn_2='Bërndt', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19690117'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Schillerweg 44&Schillerweg&44', xad_3='Augsburg', xad_5='86150', xad_7='H')
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Eichen-Krankenhaus^PI||Hölzl^Bërndt^^^Dr.^^L^A^^^G~Hölzl^Bërndt^^^Herr Dr.^^D^A^^^G||19690117|F|||Schillerweg 44&Schillerweg&44^^Augsburg^^86150^^H||^PRN^PH^^49^821^4681357^^^^^0821/4681357|^WPN^PH^^49^821^97531^^^^^0821/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='820303', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Eichen-Krankenhaus', xcn_11='L', xcn_18='DN ')
        segment.visit_number = CX(cx_1='418263', cx_4='Eichen-Krankenhaus', cx_5='VN')
        segment.financial_class = FC(fc_1='01100000')
        segment.contract_code = CWE(cwe_1='C')
        segment.contract_effective_date = '202401'
        segment.admit_date_time = '202606051645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^201^2^IN^^N^A^4|R|||820303^Rüttger^Frïedrich^^^Dr.^^^Eichen-Krankenhaus^L^^^^^^DN ||||||||||||418263^^^Eichen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260615'
        segment.estimated_length_of_inpatient_stay = '10'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260615|10'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202606051705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.40', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202606051705'
        message.evn.event_occurred = '022606051645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Eichen-Krankenhaus', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Hölzl', xpn_2='Bërndt', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Hölzl', xpn_2='Bërndt', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19690117'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Schillerweg 44&Schillerweg&44', xad_3='Augsburg', xad_5='86150', xad_7='H')
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='820303', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Eichen-Krankenhaus', xcn_11='L', xcn_18='DN ')
        message.pv1.visit_number = CX(cx_1='418263', cx_4='Eichen-Krankenhaus', cx_5='VN')
        message.pv1.financial_class = FC(fc_1='01100000')
        message.pv1.contract_code = CWE(cwe_1='C')
        message.pv1.contract_effective_date = '202401'
        message.pv1.admit_date_time = '202606051645'

        message.pv2.expected_discharge_date_time = '20260615'
        message.pv2.estimated_length_of_inpatient_stay = '10'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_05 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202504011705||||202504011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||820309^Rüttger^Frïedrich^^^Dr.^^^Birken-Klinik^L^^^DN^^^DN ||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rZBE|4567^KIS|202504011705||REFERENCE'

class Test_de_cloverleaf_05_5_ADT_A03_discharge_standard_HL7_D_profile_v2_5(unittest.TestCase):
    """ 5. ADT^A03 - discharge, standard (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.47')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Grüber')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '820309')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Rüttger')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN ')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_05, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '202504061100')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202504011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.47', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202504011705'
        segment.event_occurred = '202504011645'

        serialized = segment.serialize()
        expected = 'EVN||202504011705||||202504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='820309', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN ')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||820309^Rüttger^Frïedrich^^^Dr.^^^Birken-Klinik^L^^^DN^^^DN ||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A03()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202504011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.47', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202504011705'
        message.evn.event_occurred = '202504011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='820309', xcn_2='Rüttger', xcn_3='Frïedrich', xcn_6='Dr.', xcn_10='Birken-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN ')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.discharge_disposition = CWE(cwe_1='011')
        message.pv1.admit_date_time = '202504011645'
        message.pv1.discharge_date_time = '202504061100'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_06 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO\rEVN||202504011705||||202504011645\rPID|||34567^^^Birken-Klinik^PI||an der Mühle&an der&Mühle^Tïlman^^^^^L^A^^^G||19710803|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse  21&Kirchgasse&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rPV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N\rZBE|4567^KIS|202504011705||REFERENCE'

class Test_de_cloverleaf_06_6_ADT_A03_discharge_with_DRG_HL7_D_profile_v2_5(unittest.TestCase):
    """ 6. ADT^A03 - discharge with DRG (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.48')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'an der Mühle')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.1.2')
        self.assertEqual(result, 'an der')

# ################################################################################################################

    def test_navigate_PID_5_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.1.3')
        self.assertEqual(result, 'Mühle')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Tïlman')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19710803')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse  21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'W')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'widowed')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verwitwet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '202504061100')

# ################################################################################################################

    def test_navigate_PV2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.3')
        self.assertEqual(result, '0102')

# ################################################################################################################

    def test_navigate_PV2_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.3.2')
        self.assertEqual(result, 'vollstationär, Arbeitsunfall')

# ################################################################################################################

    def test_navigate_PV2_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.3.3')
        self.assertEqual(result, 'GSG0001')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.11')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_06, validate=False)
        result = message.get('PV2.37')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202504011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.48', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202504011705'
        segment.event_occurred = '202504011645'

        serialized = segment.serialize()
        expected = 'EVN||202504011705||||202504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='an der Mühle&an der&Mühle', xpn_2='Tïlman', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19710803'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse  21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||an der Mühle&an der&Mühle^Tïlman^^^^^L^A^^^G||19710803|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse  21&Kirchgasse&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.admit_reason = CWE(cwe_1='0102', cwe_2='vollstationär, Arbeitsunfall', cwe_3='GSG0001')
        segment.estimated_length_of_inpatient_stay = '4'
        segment.actual_length_of_inpatient_stay = '4'
        segment.newborn_baby_indicator = 'N'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A03()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202504011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.48', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202504011705'
        message.evn.event_occurred = '202504011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='an der Mühle&an der&Mühle', xpn_2='Tïlman', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19710803'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse  21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.discharge_disposition = CWE(cwe_1='011')
        message.pv1.admit_date_time = '202504011645'
        message.pv1.discharge_date_time = '202504061100'

        message.pv2.admit_reason = CWE(cwe_1='0102', cwe_2='vollstationär, Arbeitsunfall', cwe_3='GSG0001')
        message.pv2.estimated_length_of_inpatient_stay = '4'
        message.pv2.actual_length_of_inpatient_stay = '4'
        message.pv2.newborn_baby_indicator = 'N'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_07 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO\rEVN||202504011705||||202504011645\rPID|||34567^^^Birken-Klinik^PI||an der Mühle&an der&Mühle^Tïlman^^^^^L^A^^^G||19710803|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rPV2||||||||||||||||||||||||||||||||||||N|N\rZBE|4567^KIS|202504011705||REFERENCE'

class Test_de_cloverleaf_07_7_ADT_A03_discharge_with_billing_HL7_D_profile_v2_5(unittest.TestCase):
    """ 7. ADT^A03 - discharge with billing (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.49')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'an der Mühle')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.1.2')
        self.assertEqual(result, 'an der')

# ################################################################################################################

    def test_navigate_PID_5_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.1.3')
        self.assertEqual(result, 'Mühle')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Tïlman')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19710803')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'W')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'widowed')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verwitwet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '202504061100')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_07, validate=False)
        result = message.get('PV2.37')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202504011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.49', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202504011705'
        segment.event_occurred = '202504011645'

        serialized = segment.serialize()
        expected = 'EVN||202504011705||||202504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='an der Mühle&an der&Mühle', xpn_2='Tïlman', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19710803'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||an der Mühle&an der&Mühle^Tïlman^^^^^L^A^^^G||19710803|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.newborn_baby_indicator = 'N'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2||||||||||||||||||||||||||||||||||||N|N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A03()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202504011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.49', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202504011705'
        message.evn.event_occurred = '202504011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='an der Mühle&an der&Mühle', xpn_2='Tïlman', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19710803'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.discharge_disposition = CWE(cwe_1='011')
        message.pv1.admit_date_time = '202504011645'
        message.pv1.discharge_date_time = '202504061100'

        message.pv2.newborn_baby_indicator = 'N'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_08 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011935||||202604011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|9012^KIS|202604011935||INSERT'

class Test_de_cloverleaf_08_8_ADT_A02_transfer_standard_HL7_D_profile_v2_5(unittest.TestCase):
    """ 8. ADT^A02 - transfer, standard (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.44')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Grüber')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_08, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011935'
        segment.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        segment.message_control_id = 'ADT002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.44', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011935'
        segment.event_occurred = '202604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011935||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260405'
        segment.estimated_length_of_inpatient_stay = '4'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260405|4'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A02()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011935'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        message.msh.message_control_id = 'ADT002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.44', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202604011935'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_09 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO\rEVN||202604011935||||202604011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|9012^KIS|202604011935||DELETE'

class Test_de_cloverleaf_09_9_ADT_A12_cancel_transfer_HL7_D_profile_v2_5(unittest.TestCase):
    """ 9. ADT^A12 - cancel transfer (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        self.assertIsInstance(message, ADT_A12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.46')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_09, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011935'
        segment.message_type = MSG(msg_1='ADT', msg_2='A12', msg_3='ADT_A12')
        segment.message_control_id = 'ADT002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.46', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011935'
        segment.event_occurred = '202604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011935||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260405'
        segment.estimated_length_of_inpatient_stay = '4'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260405|4'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A12()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011935'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A12', msg_3='ADT_A12')
        message.msh.message_control_id = 'ADT002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.46', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202604011935'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_10 = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||202604011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645\rZBE|4567^KIS|202604011705||INSERT'

class Test_de_cloverleaf_10_10_ADT_A04_outpatient_registration_HL7_D_profile_v2_5(unittest.TestCase):
    """ 10. ADT^A04 - outpatient registration (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.51')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Grüber')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'O')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'AIN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_10, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.event_occurred = '202604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='O')
        segment.assigned_patient_location = PL(pl_4='AIN', pl_6='D', pl_7='A', pl_8='1')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='O')
        message.pv1.assigned_patient_location = PL(pl_4='AIN', pl_6='D', pl_7='A', pl_8='1')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_11 = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO\rEVN||202604011705|20260601|||202604011645\rPID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|I|IN1^^^CH^^N||||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2||||||||20260601\rZBE|4567^KIS|202604011705||INSERT'

class Test_de_cloverleaf_11_11_ADT_A04_pre_admission_registration_HL7_D_profile_v2_5(unittest.TestCase):
    """ 11. ADT^A04 - pre-admission registration (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.51')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('EVN.3')
        self.assertEqual(result, '20260601')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Feldmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Sïbylle')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Grüber')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19810622')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2917')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_11, validate=False)
        result = message.get('PV2.8')
        self.assertEqual(result, '20260601')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.date_time_planned_event = '20260601'
        segment.event_occurred = '202604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705|20260601|||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19810622'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Feldmann^Sïbylle^^^^^L^A^^^G~Grüber^^^^^^M^A^^^G||19810622|F|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN1', pl_4='CH', pl_6='N')
        segment.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN1^^^CH^^N||||||||||||||||2917^^^Birken-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_admit_date_time = '20260601'

        serialized = segment.serialize()
        expected = 'PV2||||||||20260601'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202604011705'
        message.evn.date_time_planned_event = '20260601'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Feldmann', xpn_2='Sïbylle', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Grüber', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19810622'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN1', pl_4='CH', pl_6='N')
        message.pv1.visit_number = CX(cx_1='2917', cx_4='Birken-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_admit_date_time = '20260601'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_12 = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202604011705||ADT^A31^ADT_A05|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.55^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||202604011645\rPID|||34567^^^Birken-Klinik^PI||Jäger^Rölf^^^^^L^A^^^G~Jäger^Rölfe^^^Herr^^D^A^^^G||19830915|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171\rPV1|1|N'

class Test_de_cloverleaf_12_12_ADT_A31_person_update_HL7_D_profile_v2_5(unittest.TestCase):
    """ 12. ADT^A31 - person update (HL7-D profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        self.assertIsInstance(message, ADT_A05)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A05')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LAB')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A31')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A05')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.55')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '34567')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Birken-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Jäger')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Rölf')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Jäger')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Rölfe')

# ################################################################################################################

    def test_navigate_PID_5_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1].5')
        self.assertEqual(result, 'Herr')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830915')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Lindenallee 6')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Lindenallee')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Kirchgasse 21')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Kirchgasse')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '21')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Stuttgart')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Marienhospital Süd')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_12, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='LAB')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.55', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202604011705||ADT^A31^ADT_A05|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.55^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.event_occurred = '202604011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Jäger', xpn_2='Rölf', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Jäger', xpn_2='Rölfe', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19830915'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Marienhospital Süd'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||34567^^^Birken-Klinik^PI||Jäger^Rölf^^^^^L^A^^^G~Jäger^Rölfe^^^Herr^^D^A^^^G||19830915|M|||Lindenallee 6&Lindenallee&6^^Stuttgart^^^^H~Kirchgasse 21&Kirchgasse&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Marienhospital Süd|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='N')

        serialized = segment.serialize()
        expected = 'PV1|1|N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A05()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='LAB')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.55', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='34567', cx_4='Birken-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Jäger', xpn_2='Rölf', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Jäger', xpn_2='Rölfe', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19830915'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Lindenallee 6&Lindenallee&6', xad_3='Stuttgart', xad_7='H'), XAD(xad_1='Kirchgasse 21&Kirchgasse&21', xad_3='Stuttgart', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Marienhospital Süd'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='N')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_13 = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO\rEVN||202609201025\rPID|||667812^^^KIS^PI||Brückmann&&Brückmann^Hëlga^^^^^L~Süßkind&&Süßkind^Hëlga^^^^^B||19780211|F|||||^PRN^PH^^49^711^4582716^^^^^0711/4582716||DEU^German^HL70296^deutsch|M^^HL70002|EVC^^HL70006|||||||Y|2\rPV1|1|I|IN1^202^^IN^^N^A||||||||||||||||20267891^^^KIS^VN\rOBX|1|NM|11884-4^Gestationsalter^LN||36||1-40|N|||F|||20260920\rZBE|812943|20260920||REFERENCE'

class Test_de_cloverleaf_13_13_ADT_A08_update_with_gestational_age_OBX_HL7_D_DRG_profile_v2_5(unittest.TestCase):
    """ 13. ADT^A08 - update with gestational age OBX (HL7-D DRG profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LAB')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202609201025')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '00013424')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_21_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[0]')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.62')

# ################################################################################################################

    def test_navigate_MSH_21_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[0].3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_0_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[0].4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MSH_21_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[1]')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.52')

# ################################################################################################################

    def test_navigate_MSH_21_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[1].3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('MSH.21[1].4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202609201025')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '667812')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Brückmann')

# ################################################################################################################

    def test_navigate_PID_5_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[0].1.3')
        self.assertEqual(result, 'Brückmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Hëlga')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Süßkind')

# ################################################################################################################

    def test_navigate_PID_5_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[1].1.3')
        self.assertEqual(result, 'Süßkind')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Hëlga')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19780211')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.15.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_15_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.15.4')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'EVC')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_24(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.24')
        self.assertEqual(result, 'Y')

# ################################################################################################################

    def test_navigate_PID_25(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PID.25')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '20267891')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_OBX_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.2')
        self.assertEqual(result, 'NM')

# ################################################################################################################

    def test_navigate_OBX_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.3')
        self.assertEqual(result, '11884-4')

# ################################################################################################################

    def test_navigate_OBX_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.3.2')
        self.assertEqual(result, 'Gestationsalter')

# ################################################################################################################

    def test_navigate_OBX_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.3.3')
        self.assertEqual(result, 'LN')

# ################################################################################################################

    def test_navigate_OBX_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.5')
        self.assertEqual(result, '36')

# ################################################################################################################

    def test_navigate_OBX_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.7')
        self.assertEqual(result, '1-40')

# ################################################################################################################

    def test_navigate_OBX_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.8')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_OBX_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.11')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_OBX_14(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_13, validate=False)
        result = message.get('OBX.14')
        self.assertEqual(result, '20260920')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='LAB')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202609201025'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = '00013424'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'
        segment.message_profile_identifier = [EI(ei_1='2.16.840.1.113883.2.6.9.62', ei_3='2.16.840.1.113883.2.6', ei_4='ISO'), EI(ei_1='2.16.840.1.113883.2.6.9.52', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')]

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202609201025'

        serialized = segment.serialize()
        expected = 'EVN||202609201025'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='667812', cx_4='KIS', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Brückmann&&Brückmann', xpn_2='Hëlga', xpn_8='L'), XPN(xpn_1='Süßkind&&Süßkind', xpn_2='Hëlga', xpn_8='B')]
        segment.date_time_of_birth = '19780211'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_4='deutsch')
        segment.marital_status = CWE(cwe_1='M', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='EVC', cwe_3='HL70006')
        segment.multiple_birth_indicator = 'Y'
        segment.birth_order = '2'

        serialized = segment.serialize()
        expected = 'PID|||667812^^^KIS^PI||Brückmann&&Brückmann^Hëlga^^^^^L~Süßkind&&Süßkind^Hëlga^^^^^B||19780211|F|||||^PRN^PH^^49^711^4582716^^^^^0711/4582716||DEU^German^HL70296^deutsch|M^^HL70002|EVC^^HL70006|||||||Y|2'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN1', pl_2='202', pl_4='IN', pl_6='N', pl_7='A')
        segment.visit_number = CX(cx_1='20267891', cx_4='KIS', cx_5='VN')

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN1^202^^IN^^N^A||||||||||||||||20267891^^^KIS^VN'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '1'
        segment.value_type = 'NM'
        segment.observation_identifier = CWE(cwe_1='11884-4', cwe_2='Gestationsalter', cwe_3='LN')
        segment.observation_value = []
        segment.reference_range = '1-40'
        segment.interpretation_codes = CWE(cwe_1='N')
        segment.observation_result_status = 'F'
        segment.date_time_of_the_observation = '20260920'

        serialized = segment.serialize()
        expected = 'OBX|1|NM|11884-4^Gestationsalter^LN||36||1-40|N|||F|||20260920'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='LAB')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202609201025'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = '00013424'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'
        message.msh.message_profile_identifier = [EI(ei_1='2.16.840.1.113883.2.6.9.62', ei_3='2.16.840.1.113883.2.6', ei_4='ISO'), EI(ei_1='2.16.840.1.113883.2.6.9.52', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')]

        message.evn.recorded_date_time = '202609201025'

        message.pid.patient_identifier_list = CX(cx_1='667812', cx_4='KIS', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Brückmann&&Brückmann', xpn_2='Hëlga', xpn_8='L'), XPN(xpn_1='Süßkind&&Süßkind', xpn_2='Hëlga', xpn_8='B')]
        message.pid.date_time_of_birth = '19780211'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_4='deutsch')
        message.pid.marital_status = CWE(cwe_1='M', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='EVC', cwe_3='HL70006')
        message.pid.multiple_birth_indicator = 'Y'
        message.pid.birth_order = '2'

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN1', pl_2='202', pl_4='IN', pl_6='N', pl_7='A')
        message.pv1.visit_number = CX(cx_1='20267891', cx_4='KIS', cx_5='VN')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_14 = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO\rEVN||202609201025\rPID|||667812^^^KIS^PI||Brückmann&&Brückmann^Hëlga^^^^^L||19780211|F|||||^PRN^PH^^49^711^4582716||DEU^^HL70296|M^^HL70002|EVC^^HL70006|||||||Y|2\rPV1|1|I|IN1^202^^IN^^N^A||||||||||||||||202677891^^^KIS^VN|||||||||||||||||||||||||202609161815\rDG1|1||P07.1^Neugeborenes mit sonstigem niedrigem Geburtsgewicht^I10-2004||20260920|BD|||||||||1|519834^Förster&&Förster^Löthar^^^Dr.^^^^L^^^DN||||518347291^KIS|A\rZBE|671238542^KIS|20260919||REFERENCE'

class Test_de_cloverleaf_14_14_ADT_A08_update_with_diagnosis_DG1_HL7_D_DRG_profile_v2_5(unittest.TestCase):
    """ 14. ADT^A08 - update with diagnosis DG1 (HL7-D DRG profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LAB')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202609201025')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '00013424')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_21_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[0]')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.62')

# ################################################################################################################

    def test_navigate_MSH_21_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[0].3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_0_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[0].4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MSH_21_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[1]')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.52')

# ################################################################################################################

    def test_navigate_MSH_21_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[1].3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('MSH.21[1].4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202609201025')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '667812')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Brückmann')

# ################################################################################################################

    def test_navigate_PID_5_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.5.1.3')
        self.assertEqual(result, 'Brückmann')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Hëlga')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19780211')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'EVC')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_24(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.24')
        self.assertEqual(result, 'Y')

# ################################################################################################################

    def test_navigate_PID_25(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PID.25')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '202677891')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202609161815')

# ################################################################################################################

    def test_navigate_DG1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_DG1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.3')
        self.assertEqual(result, 'P07.1')

# ################################################################################################################

    def test_navigate_DG1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.3.2')
        self.assertEqual(result, 'Neugeborenes mit sonstigem niedrigem Geburtsgewicht')

# ################################################################################################################

    def test_navigate_DG1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.3.3')
        self.assertEqual(result, 'I10-2004')

# ################################################################################################################

    def test_navigate_DG1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.5')
        self.assertEqual(result, '20260920')

# ################################################################################################################

    def test_navigate_DG1_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.6')
        self.assertEqual(result, 'BD')

# ################################################################################################################

    def test_navigate_DG1_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.15')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_DG1_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16')
        self.assertEqual(result, '519834')

# ################################################################################################################

    def test_navigate_DG1_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.2')
        self.assertEqual(result, 'Förster')

# ################################################################################################################

    def test_navigate_DG1_16_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.2.3')
        self.assertEqual(result, 'Förster')

# ################################################################################################################

    def test_navigate_DG1_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.3')
        self.assertEqual(result, 'Löthar')

# ################################################################################################################

    def test_navigate_DG1_16_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_DG1_16_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_DG1_16_13(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.16.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_DG1_20(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.20')
        self.assertEqual(result, '518347291')

# ################################################################################################################

    def test_navigate_DG1_20_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.20.2')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_DG1_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_14, validate=False)
        result = message.get('DG1.21')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='LAB')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202609201025'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = '00013424'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'
        segment.message_profile_identifier = [EI(ei_1='2.16.840.1.113883.2.6.9.62', ei_3='2.16.840.1.113883.2.6', ei_4='ISO'), EI(ei_1='2.16.840.1.113883.2.6.9.52', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')]

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202609201025'

        serialized = segment.serialize()
        expected = 'EVN||202609201025'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='667812', cx_4='KIS', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Brückmann&&Brückmann', xpn_2='Hëlga', xpn_8='L')
        segment.date_time_of_birth = '19780211'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='EVC', cwe_3='HL70006')
        segment.multiple_birth_indicator = 'Y'
        segment.birth_order = '2'

        serialized = segment.serialize()
        expected = 'PID|||667812^^^KIS^PI||Brückmann&&Brückmann^Hëlga^^^^^L||19780211|F|||||^PRN^PH^^49^711^4582716||DEU^^HL70296|M^^HL70002|EVC^^HL70006|||||||Y|2'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN1', pl_2='202', pl_4='IN', pl_6='N', pl_7='A')
        segment.visit_number = CX(cx_1='202677891', cx_4='KIS', cx_5='VN')
        segment.admit_date_time = '202609161815'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN1^202^^IN^^N^A||||||||||||||||202677891^^^KIS^VN|||||||||||||||||||||||||202609161815'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_DG1(self) -> 'None':
        segment = DG1()

        segment.set_id_dg1 = '1'
        segment.diagnosis_code_dg1 = CWE(cwe_1='P07.1', cwe_2='Neugeborenes mit sonstigem niedrigem Geburtsgewicht', cwe_3='I10-2004')
        segment.diagnosis_date_time = '20260920'
        segment.diagnosis_type = CWE(cwe_1='BD')
        segment.diagnosis_priority = '1'
        segment.diagnosing_clinician = XCN(xcn_1='519834', xcn_2='Förster&&Förster', xcn_3='Löthar', xcn_6='Dr.', xcn_11='L', xcn_14='DN')
        segment.diagnosis_identifier = EI(ei_1='518347291', ei_2='KIS')
        segment.diagnosis_action_code = 'A'

        serialized = segment.serialize()
        expected = 'DG1|1||P07.1^Neugeborenes mit sonstigem niedrigem Geburtsgewicht^I10-2004||20260920|BD|||||||||1|519834^Förster&&Förster^Löthar^^^Dr.^^^^L^^^DN||||518347291^KIS|A'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='LAB')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202609201025'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = '00013424'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'
        message.msh.message_profile_identifier = [EI(ei_1='2.16.840.1.113883.2.6.9.62', ei_3='2.16.840.1.113883.2.6', ei_4='ISO'), EI(ei_1='2.16.840.1.113883.2.6.9.52', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')]

        message.evn.recorded_date_time = '202609201025'

        message.pid.patient_identifier_list = CX(cx_1='667812', cx_4='KIS', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Brückmann&&Brückmann', xpn_2='Hëlga', xpn_8='L')
        message.pid.date_time_of_birth = '19780211'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='EVC', cwe_3='HL70006')
        message.pid.multiple_birth_indicator = 'Y'
        message.pid.birth_order = '2'

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN1', pl_2='202', pl_4='IN', pl_6='N', pl_7='A')
        message.pv1.visit_number = CX(cx_1='202677891', cx_4='KIS', cx_5='VN')
        message.pv1.admit_date_time = '202609161815'

        message.dg1.set_id_dg1 = '1'
        message.dg1.diagnosis_code_dg1 = CWE(cwe_1='P07.1', cwe_2='Neugeborenes mit sonstigem niedrigem Geburtsgewicht', cwe_3='I10-2004')
        message.dg1.diagnosis_date_time = '20260920'
        message.dg1.diagnosis_type = CWE(cwe_1='BD')
        message.dg1.diagnosis_priority = '1'
        message.dg1.diagnosing_clinician = XCN(xcn_1='519834', xcn_2='Förster&&Förster', xcn_3='Löthar', xcn_6='Dr.', xcn_11='L', xcn_14='DN')
        message.dg1.diagnosis_identifier = EI(ei_1='518347291', ei_2='KIS')
        message.dg1.diagnosis_action_code = 'A'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_15 = 'MSH|^~\\&|HOSPAT|ADT|DATAGATE|ADT|20260416180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO\rEVN||20260416180000\rPID|||205000418^^^Tannen-Klinikum^PI||Würzburger^Gërd^^^^^L||19660514|M|||Brühlweg 11^^Kempten^^87435^DEU^H|08312649|0831-5287634|08323-291|DEU||EVC||||||Nürnberg|||D\rPV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Tannen-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714\rTXA|1|CN|application/word|||20260416142700|20260416142700||||wörnli|78491||||78491.doc^HOSPAT|DI\rOBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F'

class Test_de_cloverleaf_15_15_MDM_T02_document_notification_with_content_HL7_D_MDM_profile_v2_5(unittest.TestCase):
    """ 15. MDM^T02 - document notification with content (HL7-D MDM profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        self.assertIsInstance(message, MDM_T02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'MDM_T02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'HOSPAT')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'DATAGATE')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260416180000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'MDM')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'T02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'MDM_T02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '102000')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.69')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.1.13883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260416180000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '205000418')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Tannen-Klinikum')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Würzburger')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Gërd')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19660514')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brühlweg 11')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Kempten')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '87435')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'EVC')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'C1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.5')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Tannen-Klinikum')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.21')
        self.assertEqual(result, 'K')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, 'E')

# ################################################################################################################

    def test_navigate_PV1_39(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.39')
        self.assertEqual(result, '7823')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260122155500')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '20260813174000')

# ################################################################################################################

    def test_navigate_PV1_48(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.48')
        self.assertEqual(result, '617')

# ################################################################################################################

    def test_navigate_PV1_50(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('PV1.50')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_TXA_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TXA_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.2')
        self.assertEqual(result, 'CN')

# ################################################################################################################

    def test_navigate_TXA_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.3')
        self.assertEqual(result, 'application/word')

# ################################################################################################################

    def test_navigate_TXA_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.6')
        self.assertEqual(result, '20260416142700')

# ################################################################################################################

    def test_navigate_TXA_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.7')
        self.assertEqual(result, '20260416142700')

# ################################################################################################################

    def test_navigate_TXA_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.11')
        self.assertEqual(result, 'wörnli')

# ################################################################################################################

    def test_navigate_TXA_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.12')
        self.assertEqual(result, '78491')

# ################################################################################################################

    def test_navigate_TXA_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.16')
        self.assertEqual(result, '78491.doc')

# ################################################################################################################

    def test_navigate_TXA_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.16.2')
        self.assertEqual(result, 'HOSPAT')

# ################################################################################################################

    def test_navigate_TXA_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('TXA.17')
        self.assertEqual(result, 'DI')

# ################################################################################################################

    def test_navigate_OBX_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.2')
        self.assertEqual(result, 'ED')

# ################################################################################################################

    def test_navigate_OBX_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.3.2')
        self.assertEqual(result, 'Document Content')

# ################################################################################################################

    def test_navigate_OBX_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.4')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.5.2')
        self.assertEqual(result, 'text/plain')

# ################################################################################################################

    def test_navigate_OBX_5_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.5.4')
        self.assertEqual(result, 'Base64')

# ################################################################################################################

    def test_navigate_OBX_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.5.5')
        self.assertEqual(result, 'VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==')

# ################################################################################################################

    def test_navigate_OBX_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_15, validate=False)
        result = message.get('OBX.11')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='HOSPAT')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='DATAGATE')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '20260416180000'
        segment.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        segment.message_control_id = '102000'
        segment.processing_id = PT(pt_1='D')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.69', ei_3='2.16.840.1.1.13883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|HOSPAT|ADT|DATAGATE|ADT|20260416180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260416180000'

        serialized = segment.serialize()
        expected = 'EVN||20260416180000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='205000418', cx_4='Tannen-Klinikum', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Würzburger', xpn_2='Gërd', xpn_8='L')
        segment.date_time_of_birth = '19660514'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Brühlweg 11', xad_3='Kempten', xad_5='87435', xad_6='DEU', xad_7='H')
        segment.primary_language = CWE(cwe_1='DEU')
        segment.religion = CWE(cwe_1='EVC')
        segment.birth_place = 'Nürnberg'
        segment.citizenship = CWE(cwe_1='D')

        serialized = segment.serialize()
        expected = 'PID|||205000418^^^Tannen-Klinikum^PI||Würzburger^Gërd^^^^^L||19660514|M|||Brühlweg 11^^Kempten^^87435^DEU^H|08312649|0831-5287634|08323-291|DEU||EVC||||||Nürnberg|||D'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='C1', pl_4='CH')
        segment.admission_type = CWE(cwe_1='N')
        segment.preadmit_number = CX(cx_1='6308714')
        segment.visit_number = CX(cx_1='6308714', cx_4='Tannen-Klinikum', cx_5='VN')
        segment.charge_price_indicator = CWE(cwe_1='K')
        segment.discharge_disposition = CWE(cwe_1='E')
        segment.servicing_facility = CWE(cwe_1='7823')
        segment.admit_date_time = '20260122155500'
        segment.discharge_date_time = '20260813174000'
        segment.total_adjustments = '617'
        segment.alternate_visit_id = CX(cx_1='6308714')

        serialized = segment.serialize()
        expected = 'PV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Tannen-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TXA(self) -> 'None':
        segment = TXA()

        segment.set_id_txa = '1'
        segment.document_type = CWE(cwe_1='CN')
        segment.document_content_presentation = 'application/word'
        segment.origination_date_time = '20260416142700'
        segment.transcription_date_time = '20260416142700'
        segment.transcriptionist_code_name = XCN(xcn_1='wörnli')
        segment.unique_document_number = EI(ei_1='78491')
        segment.unique_document_file_name = '78491.doc^HOSPAT'
        segment.document_completion_status = 'DI'

        serialized = segment.serialize()
        expected = 'TXA|1|CN|application/word|||20260416142700|20260416142700||||wörnli|78491||||78491.doc^HOSPAT|DI'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '1'
        segment.value_type = 'ED'
        segment.observation_identifier = CWE(cwe_2='Document Content')
        segment.observation_sub_id = OG(og_1='1')
        segment.observation_value = []
        segment.observation_result_status = 'F'

        serialized = segment.serialize()
        expected = 'OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = MDM_T02()

        message.msh.sending_application = HD(hd_1='HOSPAT')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='DATAGATE')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '20260416180000'
        message.msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        message.msh.message_control_id = '102000'
        message.msh.processing_id = PT(pt_1='D')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.69', ei_3='2.16.840.1.1.13883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '20260416180000'

        message.pid.patient_identifier_list = CX(cx_1='205000418', cx_4='Tannen-Klinikum', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Würzburger', xpn_2='Gërd', xpn_8='L')
        message.pid.date_time_of_birth = '19660514'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = XAD(xad_1='Brühlweg 11', xad_3='Kempten', xad_5='87435', xad_6='DEU', xad_7='H')
        message.pid.primary_language = CWE(cwe_1='DEU')
        message.pid.religion = CWE(cwe_1='EVC')
        message.pid.birth_place = 'Nürnberg'
        message.pid.citizenship = CWE(cwe_1='D')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='C1', pl_4='CH')
        message.pv1.admission_type = CWE(cwe_1='N')
        message.pv1.preadmit_number = CX(cx_1='6308714')
        message.pv1.visit_number = CX(cx_1='6308714', cx_4='Tannen-Klinikum', cx_5='VN')
        message.pv1.charge_price_indicator = CWE(cwe_1='K')
        message.pv1.discharge_disposition = CWE(cwe_1='E')
        message.pv1.servicing_facility = CWE(cwe_1='7823')
        message.pv1.admit_date_time = '20260122155500'
        message.pv1.discharge_date_time = '20260813174000'
        message.pv1.total_adjustments = '617'
        message.pv1.alternate_visit_id = CX(cx_1='6308714')

        message.txa.set_id_txa = '1'
        message.txa.document_type = CWE(cwe_1='CN')
        message.txa.document_content_presentation = 'application/word'
        message.txa.origination_date_time = '20260416142700'
        message.txa.transcription_date_time = '20260416142700'
        message.txa.transcriptionist_code_name = XCN(xcn_1='wörnli')
        message.txa.unique_document_number = EI(ei_1='78491')
        message.txa.unique_document_file_name = '78491.doc^HOSPAT'
        message.txa.document_completion_status = 'DI'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_16 = 'MSH|^~\\&|HOSPAT|ADT|DATAGATE|ADT|20260416181000||MDM^T08^MDM_T02|102001|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO\rEVN||20260416181000\rPID|||205000418^^^Tannen-Klinikum^PI||Würzburger^Gërd^^^^^L||19660514|M|||Brühlweg 11^^Kempten^^87435^DEU^H|08312649|0831-5287634|08323-291|DEU||EVC||||||Nürnberg|||D\rPV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Tannen-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714\rTXA|1|CN|application/word|||20260416142700|20260416142700|20260416170000|||wörnli|78491||||78491.doc^HOSPAT|AU\rOBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F'

class Test_de_cloverleaf_16_16_MDM_T08_document_status_change_HL7_D_MDM_profile_v2_5(unittest.TestCase):
    """ 16. MDM^T08 - document status change (HL7-D MDM profile v2.5)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        self.assertIsInstance(message, MDM_T02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'MDM_T02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'HOSPAT')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'DATAGATE')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260416181000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'MDM')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'T08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'MDM_T02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '102001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.69')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.1.13883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260416181000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '205000418')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Tannen-Klinikum')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Würzburger')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Gërd')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19660514')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brühlweg 11')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Kempten')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '87435')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'EVC')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'C1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.5')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Tannen-Klinikum')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.21')
        self.assertEqual(result, 'K')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, 'E')

# ################################################################################################################

    def test_navigate_PV1_39(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.39')
        self.assertEqual(result, '7823')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260122155500')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '20260813174000')

# ################################################################################################################

    def test_navigate_PV1_48(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.48')
        self.assertEqual(result, '617')

# ################################################################################################################

    def test_navigate_PV1_50(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('PV1.50')
        self.assertEqual(result, '6308714')

# ################################################################################################################

    def test_navigate_TXA_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TXA_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.2')
        self.assertEqual(result, 'CN')

# ################################################################################################################

    def test_navigate_TXA_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.3')
        self.assertEqual(result, 'application/word')

# ################################################################################################################

    def test_navigate_TXA_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.6')
        self.assertEqual(result, '20260416142700')

# ################################################################################################################

    def test_navigate_TXA_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.7')
        self.assertEqual(result, '20260416142700')

# ################################################################################################################

    def test_navigate_TXA_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.8')
        self.assertEqual(result, '20260416170000')

# ################################################################################################################

    def test_navigate_TXA_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.11')
        self.assertEqual(result, 'wörnli')

# ################################################################################################################

    def test_navigate_TXA_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.12')
        self.assertEqual(result, '78491')

# ################################################################################################################

    def test_navigate_TXA_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.16')
        self.assertEqual(result, '78491.doc')

# ################################################################################################################

    def test_navigate_TXA_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.16.2')
        self.assertEqual(result, 'HOSPAT')

# ################################################################################################################

    def test_navigate_TXA_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('TXA.17')
        self.assertEqual(result, 'AU')

# ################################################################################################################

    def test_navigate_OBX_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.2')
        self.assertEqual(result, 'ED')

# ################################################################################################################

    def test_navigate_OBX_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.3.2')
        self.assertEqual(result, 'Document Content')

# ################################################################################################################

    def test_navigate_OBX_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.4')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.5.2')
        self.assertEqual(result, 'text/plain')

# ################################################################################################################

    def test_navigate_OBX_5_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.5.4')
        self.assertEqual(result, 'Base64')

# ################################################################################################################

    def test_navigate_OBX_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.5.5')
        self.assertEqual(result, 'VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==')

# ################################################################################################################

    def test_navigate_OBX_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_16, validate=False)
        result = message.get('OBX.11')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='HOSPAT')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='DATAGATE')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '20260416181000'
        segment.message_type = MSG(msg_1='MDM', msg_2='T08', msg_3='MDM_T02')
        segment.message_control_id = '102001'
        segment.processing_id = PT(pt_1='D')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.69', ei_3='2.16.840.1.1.13883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|HOSPAT|ADT|DATAGATE|ADT|20260416181000||MDM^T08^MDM_T02|102001|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260416181000'

        serialized = segment.serialize()
        expected = 'EVN||20260416181000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='205000418', cx_4='Tannen-Klinikum', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Würzburger', xpn_2='Gërd', xpn_8='L')
        segment.date_time_of_birth = '19660514'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Brühlweg 11', xad_3='Kempten', xad_5='87435', xad_6='DEU', xad_7='H')
        segment.primary_language = CWE(cwe_1='DEU')
        segment.religion = CWE(cwe_1='EVC')
        segment.birth_place = 'Nürnberg'
        segment.citizenship = CWE(cwe_1='D')

        serialized = segment.serialize()
        expected = 'PID|||205000418^^^Tannen-Klinikum^PI||Würzburger^Gërd^^^^^L||19660514|M|||Brühlweg 11^^Kempten^^87435^DEU^H|08312649|0831-5287634|08323-291|DEU||EVC||||||Nürnberg|||D'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='C1', pl_4='CH')
        segment.admission_type = CWE(cwe_1='N')
        segment.preadmit_number = CX(cx_1='6308714')
        segment.visit_number = CX(cx_1='6308714', cx_4='Tannen-Klinikum', cx_5='VN')
        segment.charge_price_indicator = CWE(cwe_1='K')
        segment.discharge_disposition = CWE(cwe_1='E')
        segment.servicing_facility = CWE(cwe_1='7823')
        segment.admit_date_time = '20260122155500'
        segment.discharge_date_time = '20260813174000'
        segment.total_adjustments = '617'
        segment.alternate_visit_id = CX(cx_1='6308714')

        serialized = segment.serialize()
        expected = 'PV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Tannen-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TXA(self) -> 'None':
        segment = TXA()

        segment.set_id_txa = '1'
        segment.document_type = CWE(cwe_1='CN')
        segment.document_content_presentation = 'application/word'
        segment.origination_date_time = '20260416142700'
        segment.transcription_date_time = '20260416142700'
        segment.edit_date_time = '20260416170000'
        segment.transcriptionist_code_name = XCN(xcn_1='wörnli')
        segment.unique_document_number = EI(ei_1='78491')
        segment.unique_document_file_name = '78491.doc^HOSPAT'
        segment.document_completion_status = 'AU'

        serialized = segment.serialize()
        expected = 'TXA|1|CN|application/word|||20260416142700|20260416142700|20260416170000|||wörnli|78491||||78491.doc^HOSPAT|AU'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '1'
        segment.value_type = 'ED'
        segment.observation_identifier = CWE(cwe_2='Document Content')
        segment.observation_sub_id = OG(og_1='1')
        segment.observation_value = []
        segment.observation_result_status = 'F'

        serialized = segment.serialize()
        expected = 'OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = MDM_T02()

        message.msh.sending_application = HD(hd_1='HOSPAT')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='DATAGATE')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '20260416181000'
        message.msh.message_type = MSG(msg_1='MDM', msg_2='T08', msg_3='MDM_T02')
        message.msh.message_control_id = '102001'
        message.msh.processing_id = PT(pt_1='D')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.69', ei_3='2.16.840.1.1.13883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '20260416181000'

        message.pid.patient_identifier_list = CX(cx_1='205000418', cx_4='Tannen-Klinikum', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Würzburger', xpn_2='Gërd', xpn_8='L')
        message.pid.date_time_of_birth = '19660514'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = XAD(xad_1='Brühlweg 11', xad_3='Kempten', xad_5='87435', xad_6='DEU', xad_7='H')
        message.pid.primary_language = CWE(cwe_1='DEU')
        message.pid.religion = CWE(cwe_1='EVC')
        message.pid.birth_place = 'Nürnberg'
        message.pid.citizenship = CWE(cwe_1='D')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='C1', pl_4='CH')
        message.pv1.admission_type = CWE(cwe_1='N')
        message.pv1.preadmit_number = CX(cx_1='6308714')
        message.pv1.visit_number = CX(cx_1='6308714', cx_4='Tannen-Klinikum', cx_5='VN')
        message.pv1.charge_price_indicator = CWE(cwe_1='K')
        message.pv1.discharge_disposition = CWE(cwe_1='E')
        message.pv1.servicing_facility = CWE(cwe_1='7823')
        message.pv1.admit_date_time = '20260122155500'
        message.pv1.discharge_date_time = '20260813174000'
        message.pv1.total_adjustments = '617'
        message.pv1.alternate_visit_id = CX(cx_1='6308714')

        message.txa.set_id_txa = '1'
        message.txa.document_type = CWE(cwe_1='CN')
        message.txa.document_content_presentation = 'application/word'
        message.txa.origination_date_time = '20260416142700'
        message.txa.transcription_date_time = '20260416142700'
        message.txa.edit_date_time = '20260416170000'
        message.txa.transcriptionist_code_name = XCN(xcn_1='wörnli')
        message.txa.unique_document_number = EI(ei_1='78491')
        message.txa.unique_document_file_name = '78491.doc^HOSPAT'
        message.txa.document_completion_status = 'AU'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_17 = 'MSH|^~\\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144021||DFT^P03|a8274de51943f780|P|2.5|||AL|NE|DEU|UNICODE UTF-8\rEVN|P03|20260315144018\rPID|||20260315P00289||Schäffer^Ülrike||19890327|F|||Gärtnerstr. 78^^Brückstadt^^54321||05678/12345-0\rPV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524\rFT1|1|20260315A00078|20260315A00078|20260315143954||CG|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp|||1||||||||||B000852446^Brünner^Rëné^^^Dr. med.|||||D-An1E'

class Test_de_cloverleaf_17_17_DFT_P03_financial_transaction_Thieme_E_ConsentPro(unittest.TestCase):
    """ 17. DFT^P03 - financial transaction (Thieme E-ConsentPro)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        self.assertIsInstance(message, DFT_P03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'DFT_P03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'ECONSENTPRO')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'THIEME')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'KRANKENHAUS')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260315144021')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'DFT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'P03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'a8274de51943f780')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260315144018')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '20260315P00289')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Schäffer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ülrike')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19890327')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Gärtnerstr. 78')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Brückstadt')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, '64')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '6405')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'URO')

# ################################################################################################################

    def test_navigate_PV1_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.16')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '20260315F00134')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'K')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260315133524')

# ################################################################################################################

    def test_navigate_FT1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_FT1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.2')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_FT1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.3')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_FT1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.4')
        self.assertEqual(result, '20260315143954')

# ################################################################################################################

    def test_navigate_FT1_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.6')
        self.assertEqual(result, 'CG')

# ################################################################################################################

    def test_navigate_FT1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.7')
        self.assertEqual(result, 'D-An1E')

# ################################################################################################################

    def test_navigate_FT1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.7.2')
        self.assertEqual(result, 'Narkose/Regionalanästhesie')

# ################################################################################################################

    def test_navigate_FT1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.7.3')
        self.assertEqual(result, 'com.thieme.ecp')

# ################################################################################################################

    def test_navigate_FT1_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.10')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_FT1_20(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.20')
        self.assertEqual(result, 'B000852446')

# ################################################################################################################

    def test_navigate_FT1_20_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.20.2')
        self.assertEqual(result, 'Brünner')

# ################################################################################################################

    def test_navigate_FT1_20_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.20.3')
        self.assertEqual(result, 'Rëné')

# ################################################################################################################

    def test_navigate_FT1_20_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.20.6')
        self.assertEqual(result, 'Dr. med.')

# ################################################################################################################

    def test_navigate_FT1_25(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_17, validate=False)
        result = message.get('FT1.25')
        self.assertEqual(result, 'D-An1E')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='ECONSENTPRO')
        segment.sending_facility = HD(hd_1='THIEME')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='KRANKENHAUS')
        segment.date_time_of_message = '20260315144021'
        segment.message_type = MSG(msg_1='DFT', msg_2='P03')
        segment.message_control_id = 'a8274de51943f780'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144021||DFT^P03|a8274de51943f780|P|2.5|||AL|NE|DEU|UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260315144018'

        serialized = segment.serialize()
        expected = 'EVN|P03|20260315144018'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='20260315P00289')
        segment.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike')
        segment.date_time_of_birth = '19890327'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Gärtnerstr. 78', xad_3='Brückstadt', xad_5='54321')

        serialized = segment.serialize()
        expected = 'PID|||20260315P00289||Schäffer^Ülrike||19890327|F|||Gärtnerstr. 78^^Brückstadt^^54321||05678/12345-0'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='64', pl_2='6405', pl_3='3', pl_4='URO')
        segment.vip_indicator = CWE(cwe_1='N')
        segment.visit_number = CX(cx_1='20260315F00134')
        segment.contract_code = CWE(cwe_1='K')
        segment.admit_date_time = '20260315133524'

        serialized = segment.serialize()
        expected = 'PV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_FT1(self) -> 'None':
        segment = FT1()

        segment.set_id_ft1 = '1'
        segment.transaction_id = CX(cx_1='20260315A00078')
        segment.transaction_batch_id = '20260315A00078'
        segment.transaction_date = DR(dr_1='20260315143954')
        segment.transaction_type = CWE(cwe_1='CG')
        segment.transaction_code = CWE(cwe_1='D-An1E', cwe_2='Narkose/Regionalanästhesie', cwe_3='com.thieme.ecp')
        segment.transaction_quantity = '1'
        segment.performed_by_code = XCN(xcn_1='B000852446', xcn_2='Brünner', xcn_3='Rëné', xcn_6='Dr. med.')
        segment.procedure_code = CNE(cne_1='D-An1E')

        serialized = segment.serialize()
        expected = 'FT1|1|20260315A00078|20260315A00078|20260315143954||CG|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp|||1||||||||||B000852446^Brünner^Rëné^^^Dr. med.|||||D-An1E'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = DFT_P03()

        message.msh.sending_application = HD(hd_1='ECONSENTPRO')
        message.msh.sending_facility = HD(hd_1='THIEME')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='KRANKENHAUS')
        message.msh.date_time_of_message = '20260315144021'
        message.msh.message_type = MSG(msg_1='DFT', msg_2='P03')
        message.msh.message_control_id = 'a8274de51943f780'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '20260315144018'

        message.pid.patient_identifier_list = CX(cx_1='20260315P00289')
        message.pid.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike')
        message.pid.date_time_of_birth = '19890327'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Gärtnerstr. 78', xad_3='Brückstadt', xad_5='54321')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_18 = 'MSH|^~\\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144121||MDM^T01|b3941ca72856e017|P|2.5|||AL|NE|DEU|UNICODE UTF-8\rEVN|T01|20260315144123\rPID|||20260315P00289||Schäffer^Ülrike||19890327|F|||Gärtnerstr. 78^^Brückstadt^^54321||05678/12345-0\rPV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524\rORC|SC|20260315A00078|20260315A00078~001||CM||||20260315144123\rOBR|1|20260315A00078|20260315A00078~001|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp\rNTE|1|L|Maßnahme vom Patienten akzeptiert|RE\rTXA|1|HP|AP|20260315144123||20260315140844|||B000852446^Brünner^Rëné^^^Dr. med.|||7c29a4e1-83df-41b7-9562-d8ef12345a02^com.thieme.ecp||20260315A00078|20260315A00078~001|I_D-An1E_20260315A00078_20260315144103.pdf|LA|U'

class Test_de_cloverleaf_18_18_MDM_T01_consent_document_notification_Thieme_E_ConsentPro(unittest.TestCase):
    """ 18. MDM^T01 - consent document notification (Thieme E-ConsentPro)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        self.assertIsInstance(message, MDM_T01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'MDM_T01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'ECONSENTPRO')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'THIEME')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'KRANKENHAUS')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260315144121')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'MDM')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'T01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'b3941ca72856e017')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260315144123')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '20260315P00289')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Schäffer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ülrike')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19890327')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Gärtnerstr. 78')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Brückstadt')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, '64')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '6405')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'URO')

# ################################################################################################################

    def test_navigate_PV1_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.16')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '20260315F00134')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'K')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260315133524')

# ################################################################################################################

    def test_navigate_ORC_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.1')
        self.assertEqual(result, 'SC')

# ################################################################################################################

    def test_navigate_ORC_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.2')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_ORC_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.3[0]')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_ORC_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.3[1]')
        self.assertEqual(result, '001')

# ################################################################################################################

    def test_navigate_ORC_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.5')
        self.assertEqual(result, 'CM')

# ################################################################################################################

    def test_navigate_ORC_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('ORC.9')
        self.assertEqual(result, '20260315144123')

# ################################################################################################################

    def test_navigate_OBR_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBR_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.2')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_OBR_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.3[0]')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_OBR_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.3[1]')
        self.assertEqual(result, '001')

# ################################################################################################################

    def test_navigate_OBR_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.4')
        self.assertEqual(result, 'D-An1E')

# ################################################################################################################

    def test_navigate_OBR_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.4.2')
        self.assertEqual(result, 'Narkose/Regionalanästhesie')

# ################################################################################################################

    def test_navigate_OBR_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('OBR.4.3')
        self.assertEqual(result, 'com.thieme.ecp')

# ################################################################################################################

    def test_navigate_NTE_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('NTE.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_NTE_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('NTE.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_NTE_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('NTE.3')
        self.assertEqual(result, 'Maßnahme vom Patienten akzeptiert')

# ################################################################################################################

    def test_navigate_NTE_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('NTE.4')
        self.assertEqual(result, 'RE')

# ################################################################################################################

    def test_navigate_TXA_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TXA_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.2')
        self.assertEqual(result, 'HP')

# ################################################################################################################

    def test_navigate_TXA_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.3')
        self.assertEqual(result, 'AP')

# ################################################################################################################

    def test_navigate_TXA_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.4')
        self.assertEqual(result, '20260315144123')

# ################################################################################################################

    def test_navigate_TXA_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.6')
        self.assertEqual(result, '20260315140844')

# ################################################################################################################

    def test_navigate_TXA_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.9')
        self.assertEqual(result, 'B000852446')

# ################################################################################################################

    def test_navigate_TXA_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.9.2')
        self.assertEqual(result, 'Brünner')

# ################################################################################################################

    def test_navigate_TXA_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.9.3')
        self.assertEqual(result, 'Rëné')

# ################################################################################################################

    def test_navigate_TXA_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.9.6')
        self.assertEqual(result, 'Dr. med.')

# ################################################################################################################

    def test_navigate_TXA_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.12')
        self.assertEqual(result, '7c29a4e1-83df-41b7-9562-d8ef12345a02')

# ################################################################################################################

    def test_navigate_TXA_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.12.2')
        self.assertEqual(result, 'com.thieme.ecp')

# ################################################################################################################

    def test_navigate_TXA_14(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.14')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_TXA_15_0(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.15[0]')
        self.assertEqual(result, '20260315A00078')

# ################################################################################################################

    def test_navigate_TXA_15_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.15[1]')
        self.assertEqual(result, '001')

# ################################################################################################################

    def test_navigate_TXA_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.16')
        self.assertEqual(result, 'I_D-An1E_20260315A00078_20260315144103.pdf')

# ################################################################################################################

    def test_navigate_TXA_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.17')
        self.assertEqual(result, 'LA')

# ################################################################################################################

    def test_navigate_TXA_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_18, validate=False)
        result = message.get('TXA.18')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='ECONSENTPRO')
        segment.sending_facility = HD(hd_1='THIEME')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='KRANKENHAUS')
        segment.date_time_of_message = '20260315144121'
        segment.message_type = MSG(msg_1='MDM', msg_2='T01')
        segment.message_control_id = 'b3941ca72856e017'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144121||MDM^T01|b3941ca72856e017|P|2.5|||AL|NE|DEU|UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260315144123'

        serialized = segment.serialize()
        expected = 'EVN|T01|20260315144123'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='20260315P00289')
        segment.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike')
        segment.date_time_of_birth = '19890327'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Gärtnerstr. 78', xad_3='Brückstadt', xad_5='54321')

        serialized = segment.serialize()
        expected = 'PID|||20260315P00289||Schäffer^Ülrike||19890327|F|||Gärtnerstr. 78^^Brückstadt^^54321||05678/12345-0'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='64', pl_2='6405', pl_3='3', pl_4='URO')
        segment.vip_indicator = CWE(cwe_1='N')
        segment.visit_number = CX(cx_1='20260315F00134')
        segment.contract_code = CWE(cwe_1='K')
        segment.admit_date_time = '20260315133524'

        serialized = segment.serialize()
        expected = 'PV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_ORC(self) -> 'None':
        segment = ORC()

        segment.order_control = 'SC'
        segment.placer_order_number = EI(ei_1='20260315A00078')
        segment.filler_order_number = EI(ei_1='20260315A00078')
        segment.order_status = 'CM'
        segment.date_time_of_order_event = '20260315144123'

        serialized = segment.serialize()
        expected = 'ORC|SC|20260315A00078|20260315A00078~001||CM||||20260315144123'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBR(self) -> 'None':
        segment = OBR()

        segment.set_id_obr = '1'
        segment.placer_order_number = EI(ei_1='20260315A00078')
        segment.filler_order_number = EI(ei_1='20260315A00078')
        segment.universal_service_identifier = CWE(cwe_1='D-An1E', cwe_2='Narkose/Regionalanästhesie', cwe_3='com.thieme.ecp')

        serialized = segment.serialize()
        expected = 'OBR|1|20260315A00078|20260315A00078~001|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE(self) -> 'None':
        segment = NTE()

        segment.set_id_nte = '1'
        segment.source_of_comment = 'L'
        segment.comment = 'Maßnahme vom Patienten akzeptiert'
        segment.comment_type = CWE(cwe_1='RE')

        serialized = segment.serialize()
        expected = 'NTE|1|L|Maßnahme vom Patienten akzeptiert|RE'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TXA(self) -> 'None':
        segment = TXA()

        segment.set_id_txa = '1'
        segment.document_type = CWE(cwe_1='HP')
        segment.document_content_presentation = 'AP'
        segment.activity_date_time = '20260315144123'
        segment.origination_date_time = '20260315140844'
        segment.originator_code_name = XCN(xcn_1='B000852446', xcn_2='Brünner', xcn_3='Rëné', xcn_6='Dr. med.')
        segment.unique_document_number = EI(ei_1='7c29a4e1-83df-41b7-9562-d8ef12345a02', ei_2='com.thieme.ecp')
        segment.placer_order_number = EI(ei_1='20260315A00078')
        segment.filler_order_number = EI(ei_1='20260315A00078')
        segment.unique_document_file_name = 'I_D-An1E_20260315A00078_20260315144103.pdf'
        segment.document_completion_status = 'LA'
        segment.document_confidentiality_status = 'U'

        serialized = segment.serialize()
        expected = 'TXA|1|HP|AP|20260315144123||20260315140844|||B000852446^Brünner^Rëné^^^Dr. med.|||7c29a4e1-83df-41b7-9562-d8ef12345a02^com.thieme.ecp||20260315A00078|20260315A00078~001|I_D-An1E_20260315A00078_20260315144103.pdf|LA|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = MDM_T01()

        message.msh.sending_application = HD(hd_1='ECONSENTPRO')
        message.msh.sending_facility = HD(hd_1='THIEME')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='KRANKENHAUS')
        message.msh.date_time_of_message = '20260315144121'
        message.msh.message_type = MSG(msg_1='MDM', msg_2='T01')
        message.msh.message_control_id = 'b3941ca72856e017'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '20260315144123'

        message.pid.patient_identifier_list = CX(cx_1='20260315P00289')
        message.pid.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike')
        message.pid.date_time_of_birth = '19890327'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Gärtnerstr. 78', xad_3='Brückstadt', xad_5='54321')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='64', pl_2='6405', pl_3='3', pl_4='URO')
        message.pv1.vip_indicator = CWE(cwe_1='N')
        message.pv1.visit_number = CX(cx_1='20260315F00134')
        message.pv1.contract_code = CWE(cwe_1='K')
        message.pv1.admit_date_time = '20260315133524'

        message.txa.set_id_txa = '1'
        message.txa.document_type = CWE(cwe_1='HP')
        message.txa.document_content_presentation = 'AP'
        message.txa.activity_date_time = '20260315144123'
        message.txa.origination_date_time = '20260315140844'
        message.txa.originator_code_name = XCN(xcn_1='B000852446', xcn_2='Brünner', xcn_3='Rëné', xcn_6='Dr. med.')
        message.txa.unique_document_number = EI(ei_1='7c29a4e1-83df-41b7-9562-d8ef12345a02', ei_2='com.thieme.ecp')
        message.txa.placer_order_number = EI(ei_1='20260315A00078')
        message.txa.filler_order_number = EI(ei_1='20260315A00078')
        message.txa.unique_document_file_name = 'I_D-An1E_20260315A00078_20260315144103.pdf'
        message.txa.document_completion_status = 'LA'
        message.txa.document_confidentiality_status = 'U'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_19 = 'MSH|^~\\&|SENDESYSTEM|SENDEKH|EMPFANGSSYSTEM|EMPFANGSKH|20260101120000||ADT^A01^ADT_A01|MSG00001|P|2.6\rEVN|A01|20260101120000\rPID|||PAT042^^^Ahornhöhe-Klinik||Schäffer^Ülrike^Bïrgit^^Frau||20080614|F|||Höhenstr. 55^^Brückstadt^^54321||^^PH^05678901234~^^CP^05678901235~^^Internet^ulrike.schaeffer@brückpost.de\rPV1||I|Station A^Zimmer 111^Bett 1^Chirurgie||||ATT001^K.^Gräte^^^Dr.^med.|REF001^Ö.^Fränz^^^Dr.^med.|CON001^W.^Hëlmut^^^Dr.^med.||Station B^Zimmer 222^Bett 2^Innere Medizin||||||||FALL042|||||||||||||||||||||||Station C^Zimmer 333^Bett 3^Neurologie||20260101120000\rIN1|1|0|BKV1|BRÜCKENKRANKENVERSICHERUNG|Höhenstr. 55^^Brückstadt^^54321||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cloverleaf_19_19_ADT_A01_admission_with_insurance_Thieme_E_ConsentPro(unittest.TestCase):
    """ 19. ADT^A01 - admission with insurance (Thieme E-ConsentPro)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'SENDESYSTEM')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'SENDEKH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'EMPFANGSSYSTEM')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'EMPFANGSKH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260101120000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'MSG00001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260101120000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PAT042')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ahornhöhe-Klinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Schäffer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ülrike')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Bïrgit')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '20080614')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Höhenstr. 55')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Brückstadt')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Station A')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Zimmer 111')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Chirurgie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ATT001')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'K.')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Gräte')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'REF001')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Ö.')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Fränz')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'CON001')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'W.')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Hëlmut')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Station B')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Zimmer 222')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL042')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Station C')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Zimmer 333')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurologie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260101120000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'BKV1')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BRÜCKENKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Höhenstr. 55')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'Brückstadt')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_19, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='SENDESYSTEM')
        segment.sending_facility = HD(hd_1='SENDEKH')
        segment.receiving_application = HD(hd_1='EMPFANGSSYSTEM')
        segment.receiving_facility = HD(hd_1='EMPFANGSKH')
        segment.date_time_of_message = '20260101120000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'MSG00001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|SENDESYSTEM|SENDEKH|EMPFANGSSYSTEM|EMPFANGSKH|20260101120000||ADT^A01^ADT_A01|MSG00001|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260101120000'

        serialized = segment.serialize()
        expected = 'EVN|A01|20260101120000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PAT042', cx_4='Ahornhöhe-Klinik')
        segment.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike', xpn_3='Bïrgit', xpn_5='Frau')
        segment.date_time_of_birth = '20080614'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Höhenstr. 55', xad_3='Brückstadt', xad_5='54321')

        serialized = segment.serialize()
        expected = 'PID|||PAT042^^^Ahornhöhe-Klinik||Schäffer^Ülrike^Bïrgit^^Frau||20080614|F|||Höhenstr. 55^^Brückstadt^^54321||^^PH^05678901234~^^CP^05678901235~^^Internet^ulrike.schaeffer@brückpost.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Station A', pl_2='Zimmer 111', pl_3='Bett 1', pl_4='Chirurgie')
        segment.attending_doctor = XCN(xcn_1='ATT001', xcn_2='K.', xcn_3='Gräte', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='REF001', xcn_2='Ö.', xcn_3='Fränz', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='CON001', xcn_2='W.', xcn_3='Hëlmut', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Station B', pl_2='Zimmer 222', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL042')
        segment.pending_location = PL(pl_1='Station C', pl_2='Zimmer 333', pl_3='Bett 3', pl_4='Neurologie')
        segment.admit_date_time = '20260101120000'

        serialized = segment.serialize()
        expected = 'PV1||I|Station A^Zimmer 111^Bett 1^Chirurgie||||ATT001^K.^Gräte^^^Dr.^med.|REF001^Ö.^Fränz^^^Dr.^med.|CON001^W.^Hëlmut^^^Dr.^med.||Station B^Zimmer 222^Bett 2^Innere Medizin||||||||FALL042|||||||||||||||||||||||Station C^Zimmer 333^Bett 3^Neurologie||20260101120000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='BKV1')
        segment.insurance_company_name = XON(xon_1='BRÜCKENKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Höhenstr. 55', xad_3='Brückstadt', xad_5='54321')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|BKV1|BRÜCKENKRANKENVERSICHERUNG|Höhenstr. 55^^Brückstadt^^54321||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='SENDESYSTEM')
        message.msh.sending_facility = HD(hd_1='SENDEKH')
        message.msh.receiving_application = HD(hd_1='EMPFANGSSYSTEM')
        message.msh.receiving_facility = HD(hd_1='EMPFANGSKH')
        message.msh.date_time_of_message = '20260101120000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'MSG00001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260101120000'

        message.pid.patient_identifier_list = CX(cx_1='PAT042', cx_4='Ahornhöhe-Klinik')
        message.pid.patient_name = XPN(xpn_1='Schäffer', xpn_2='Ülrike', xpn_3='Bïrgit', xpn_5='Frau')
        message.pid.date_time_of_birth = '20080614'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Höhenstr. 55', xad_3='Brückstadt', xad_5='54321')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Station A', pl_2='Zimmer 111', pl_3='Bett 1', pl_4='Chirurgie')
        message.pv1.attending_doctor = XCN(xcn_1='ATT001', xcn_2='K.', xcn_3='Gräte', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='REF001', xcn_2='Ö.', xcn_3='Fränz', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='CON001', xcn_2='W.', xcn_3='Hëlmut', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Station B', pl_2='Zimmer 222', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL042')
        message.pv1.pending_location = PL(pl_1='Station C', pl_2='Zimmer 333', pl_3='Bett 3', pl_4='Neurologie')
        message.pv1.admit_date_time = '20260101120000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cloverleaf_20 = 'MSH|^~\\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1\rPID|1|5678||43218765\rPV1|1||SC110|\rOBX|1|NM|RASS||-4|||||||||202601010600\rOBX|2|ST|PupilleLinks||e+k|||||||||202612301330\rOBX|3|ST|PupilleRechts||e+k|||||||||202601010600'

class Test_de_cloverleaf_20_20_ORU_R01_ICU_observation_results_DETECT_UKD_Dresden(unittest.TestCase):
    """ 20. ORU^R01 - ICU observation results (DETECT / UKD Dresden)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        self.assertIsInstance(message, ORU_R01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ORU_R01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'COPRAdetectapi')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, '001')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'detectserver')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ORU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'R01')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'SC110')

# ################################################################################################################

    def test_navigate_OBX_1(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('OBX.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_2(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('OBX.2')
        self.assertEqual(result, 'NM')

# ################################################################################################################

    def test_navigate_OBX_3(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('OBX.3')
        self.assertEqual(result, 'RASS')

# ################################################################################################################

    def test_navigate_OBX_5(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('OBX.5')
        self.assertEqual(result, '-4')

# ################################################################################################################

    def test_navigate_OBX_14(self) -> 'None':
        message = parse_message(_Raw_de_cloverleaf_20, validate=False)
        result = message.get('OBX.14')
        self.assertEqual(result, '202601010600')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='COPRAdetectapi')
        segment.sending_facility = HD(hd_1='001')
        segment.receiving_application = HD(hd_1='detectserver')
        segment.message_type = MSG(msg_1='ORU', msg_2='R01')
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DE'
        segment.character_set = '8859/1'
        segment.message_profile_identifier = EI(ei_1='2.16.840.1')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'

        serialized = segment.serialize()
        expected = 'PID|1|5678||43218765'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.assigned_patient_location = PL(pl_1='SC110')

        serialized = segment.serialize()
        expected = 'PV1|1||SC110|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '1'
        segment.value_type = 'NM'
        segment.observation_identifier = CWE(cwe_1='RASS')
        segment.observation_value = []
        segment.date_time_of_the_observation = '202601010600'

        serialized = segment.serialize()
        expected = 'OBX|1|NM|RASS||-4|||||||||202601010600'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX_2(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '2'
        segment.value_type = 'ST'
        segment.observation_identifier = CWE(cwe_1='PupilleLinks')
        segment.observation_value = []
        segment.date_time_of_the_observation = '202612301330'

        serialized = segment.serialize()
        expected = 'OBX|2|ST|PupilleLinks||e+k|||||||||202612301330'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX_3(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '3'
        segment.value_type = 'ST'
        segment.observation_identifier = CWE(cwe_1='PupilleRechts')
        segment.observation_value = []
        segment.date_time_of_the_observation = '202601010600'

        serialized = segment.serialize()
        expected = 'OBX|3|ST|PupilleRechts||e+k|||||||||202601010600'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ORU_R01()

        message.msh.sending_application = HD(hd_1='COPRAdetectapi')
        message.msh.sending_facility = HD(hd_1='001')
        message.msh.receiving_application = HD(hd_1='detectserver')
        message.msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DE'
        message.msh.character_set = '8859/1'
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

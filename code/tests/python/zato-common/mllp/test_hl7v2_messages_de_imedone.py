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

_Raw_de_imedone_01 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO\rEVN||202612151705||||202612151645\rPID|||7654321^^^Ulmen-Klinik^PI||Winkler^Ingëborg^^^^^L^A^^^G~Schröter^^^^^^M^A^^^G~Winkler^^^^Frau^^D^^^^G||19851023|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^01067^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^01067^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Elisabethen-Spital|||DEU^German^HL70171^^deutsch\rPV1|1|I|CHI^302^2^IN^^N^A^4|R|||620401^Vögler^Thëodor^^^Dr.^^^Ulmen-Klinik^L^^^DN^^^DN^^G||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202612151645\rPV2|||||||||20250405|4\rZBE|5678^KIS|202612151705||INSERT'

class Test_de_imedone_01_1_ADT_A01_Admission_standard_profile_wiki_hl7_de(unittest.TestCase):
    """ 1. ADT^A01 - Admission, standard profile (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202612151705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/15')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.19.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.19.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.38')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202612151705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202612151645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '7654321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Winkler')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Ingëborg')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Schröter')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[2]')
        self.assertEqual(result, 'Winkler')

# ################################################################################################################

    def test_navigate_PID_5_2_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[2].5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_5_2_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[2].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_2_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.5[2].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19851023')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Kastanienweg 31')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Kastanienweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '31')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '01067')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Mühlenstr. 8')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Mühlenstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '8')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1].5')
        self.assertEqual(result, '01067')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.15.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_15_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.15.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verheiratet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.17.2')
        self.assertEqual(result, 'catholic')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_17_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.17.5')
        self.assertEqual(result, 'katholisch')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.26.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PID_26_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PID.26.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '302')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '620401')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Vögler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Thëodor')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.7.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '3142')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202612151645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20250405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_01, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202612151705'
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
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202612151705'
        segment.event_occurred = '202612151645'

        serialized = segment.serialize()
        expected = 'EVN||202612151705||||202612151645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='7654321', cx_4='Ulmen-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Winkler', xpn_2='Ingëborg', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Schröter', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Winkler', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        segment.date_time_of_birth = '19851023'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_5='01067', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_5='01067', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        segment.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        serialized = segment.serialize()
        expected = 'PID|||7654321^^^Ulmen-Klinik^PI||Winkler^Ingëborg^^^^^L^A^^^G~Schröter^^^^^^M^A^^^G~Winkler^^^^Frau^^D^^^^G||19851023|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^01067^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^01067^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Elisabethen-Spital|||DEU^German^HL70171^^deutsch'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='620401', xcn_2='Vögler', xcn_3='Thëodor', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        segment.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        segment.admit_date_time = '202612151645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^302^2^IN^^N^A^4|R|||620401^Vögler^Thëodor^^^Dr.^^^Ulmen-Klinik^L^^^DN^^^DN^^G||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202612151645'
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
        message.msh.date_time_of_message = '202612151705'
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

        message.evn.recorded_date_time = '202612151705'
        message.evn.event_occurred = '202612151645'

        message.pid.patient_identifier_list = CX(cx_1='7654321', cx_4='Ulmen-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Winkler', xpn_2='Ingëborg', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Schröter', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Winkler', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        message.pid.date_time_of_birth = '19851023'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_5='01067', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_5='01067', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='620401', xcn_2='Vögler', xcn_3='Thëodor', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        message.pv1.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202612151645'

        message.pv2.expected_discharge_date_time = '20250405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_02 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||020504011645\rPID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171\rPV1|1|I|URO^301^1^IN^^N^A^4|R|||620403^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN|620405^Büchner^Wïlfried^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N\rZBE|5678^KIS|202604011705||INSERT'

class Test_de_imedone_02_2_ADT_A01_Admission_for_DRG_wiki_hl7_de(unittest.TestCase):
    """ 2. ADT^A01 - Admission for DRG (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.39')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '020504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Nölting')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830711')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Kastanienweg 31')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Kastanienweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '31')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Mühlenstr. 8')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Mühlenstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '8')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'URO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '301')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '620403')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Hüttner')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedhelm')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, '620405')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Büchner')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Wïlfried')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_8_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.15')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_8_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.8.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.13')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.18')
        self.assertEqual(result, 'E')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '3142')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.3')
        self.assertEqual(result, '0101')

# ################################################################################################################

    def test_navigate_PV2_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.3.2')
        self.assertEqual(result, 'vollstationär, Normalfall')

# ################################################################################################################

    def test_navigate_PV2_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.3.3')
        self.assertEqual(result, 'GSG0001')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_imedone_02, validate=False)
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
        segment.event_occurred = '020504011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||020504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19830711'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='620403', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN')
        segment.referring_doctor = XCN(xcn_1='620405', xcn_2='Büchner', xcn_3='Wïlfried', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        segment.re_admission_indicator = CWE(cwe_1='R')
        segment.patient_type = CWE(cwe_1='E')
        segment.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|URO^301^1^IN^^N^A^4|R|||620403^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN|620405^Büchner^Wïlfried^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645'
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
        message.evn.event_occurred = '020504011645'

        message.pid.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19830711'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='620403', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.referring_doctor = XCN(xcn_1='620405', xcn_2='Büchner', xcn_3='Wïlfried', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        message.pv1.re_admission_indicator = CWE(cwe_1='R')
        message.pv1.patient_type = CWE(cwe_1='E')
        message.pv1.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
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

_Raw_de_imedone_03 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO\rEVN||202606051705||||020506051645\rPID|||54321^^^Eschen-Krankenhaus^PI||Ströbel^Hëlmut^^^Dr.^^L^A^^^G~Ströbel^Hëlmut^^^Herr Dr.^^D^A^^^G||19720219|F|||Weinbergstr. 19&Weinbergstr.&19^^Leipzig^^04103^^H||^PRN^PH^^49^341^4681357^^^^^0341/4681357|^WPN^PH^^49^341^97531^^^^^0341/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171\rPV1|1|I|HNO^201^2^IN^^N^A^4|R|||620403^Hüttner^Frïedhelm^^^Dr.^^^Eschen-Krankenhaus^L^^^^^^DN||||||||||||529814^^^Eschen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||200506051645\rPV2|||||||||20260615|10\rZBE|82914^KIS|202606051705||INSERT'

class Test_de_imedone_03_3_ADT_A01_Admission_for_billing_wiki_hl7_de(unittest.TestCase):
    """ 3. ADT^A01 - Admission for billing (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.40')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '020506051645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Eschen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Ströbel')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Hëlmut')

# ################################################################################################################

    def test_navigate_PID_5_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0].5')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Ströbel')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Hëlmut')

# ################################################################################################################

    def test_navigate_PID_5_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1].5')
        self.assertEqual(result, 'Herr Dr.')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19720219')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Weinbergstr. 19')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Weinbergstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11.1.3')
        self.assertEqual(result, '19')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Leipzig')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '04103')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '201')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '620403')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Hüttner')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedhelm')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Eschen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '529814')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Eschen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_20(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.20')
        self.assertEqual(result, '01100000')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.25')
        self.assertEqual(result, '202401')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '200506051645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260615')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_03, validate=False)
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
        segment.event_occurred = '020506051645'

        serialized = segment.serialize()
        expected = 'EVN||202606051705||||020506051645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='54321', cx_4='Eschen-Krankenhaus', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Ströbel', xpn_2='Hëlmut', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Ströbel', xpn_2='Hëlmut', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19720219'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Weinbergstr. 19&Weinbergstr.&19', xad_3='Leipzig', xad_5='04103', xad_7='H')
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||54321^^^Eschen-Krankenhaus^PI||Ströbel^Hëlmut^^^Dr.^^L^A^^^G~Ströbel^Hëlmut^^^Herr Dr.^^D^A^^^G||19720219|F|||Weinbergstr. 19&Weinbergstr.&19^^Leipzig^^04103^^H||^PRN^PH^^49^341^4681357^^^^^0341/4681357|^WPN^PH^^49^341^97531^^^^^0341/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='620403', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Eschen-Krankenhaus', xcn_11='L', xcn_18='DN')
        segment.visit_number = CX(cx_1='529814', cx_4='Eschen-Krankenhaus', cx_5='VN')
        segment.financial_class = FC(fc_1='01100000')
        segment.contract_code = CWE(cwe_1='C')
        segment.contract_effective_date = '202401'
        segment.admit_date_time = '200506051645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^201^2^IN^^N^A^4|R|||620403^Hüttner^Frïedhelm^^^Dr.^^^Eschen-Krankenhaus^L^^^^^^DN||||||||||||529814^^^Eschen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||200506051645'
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
        message.evn.event_occurred = '020506051645'

        message.pid.patient_identifier_list = CX(cx_1='54321', cx_4='Eschen-Krankenhaus', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Ströbel', xpn_2='Hëlmut', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Ströbel', xpn_2='Hëlmut', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19720219'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Weinbergstr. 19&Weinbergstr.&19', xad_3='Leipzig', xad_5='04103', xad_7='H')
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='620403', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Eschen-Krankenhaus', xcn_11='L', xcn_18='DN')
        message.pv1.visit_number = CX(cx_1='529814', cx_4='Eschen-Krankenhaus', cx_5='VN')
        message.pv1.financial_class = FC(fc_1='01100000')
        message.pv1.contract_code = CWE(cwe_1='C')
        message.pv1.contract_effective_date = '202401'
        message.pv1.admit_date_time = '200506051645'

        message.pv2.expected_discharge_date_time = '20260615'
        message.pv2.estimated_length_of_inpatient_stay = '10'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_04 = 'MSH|^~\\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO\rSFT|RIS System GmbH^L|3.4|superRIS\rMSA|CA|ADT001'

class Test_de_imedone_04_4_ACK_A01_Transport_acknowledgment_wiki_hl7_de(unittest.TestCase):
    """ 4. ACK^A01 - Transport acknowledgment (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.9')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'RIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '3.4')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'superRIS')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_04, validate=False)
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

_Raw_de_imedone_05 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011935||||202604011645\rPID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|620409^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|1234^KIS|202604011935||INSERT'

class Test_de_imedone_05_5_ADT_A02_Transfer_standard_profile_wiki_hl7_de(unittest.TestCase):
    """ 5. ADT^A02 - Transfer, standard profile (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.44')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Nölting')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830711')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Kastanienweg 31')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Kastanienweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '31')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Mühlenstr. 8')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Mühlenstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '8')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '620409')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Hüttner')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedhelm')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '3142')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_05, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19830711'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.attending_doctor = XCN(xcn_1='620409', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN')
        segment.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|620409^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19830711'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.attending_doctor = XCN(xcn_1='620409', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_06 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011935||||202604011645\rPID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260406|5||||||||||||||||||||||||||N|N\rZBE|1234^KIS|202604011935||INSERT'

class Test_de_imedone_06_6_ADT_A02_Transfer_for_DRG_wiki_hl7_de(unittest.TestCase):
    """ 6. ADT^A02 - Transfer for DRG (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.45')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Nölting')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830711')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Kastanienweg 31')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Kastanienweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '31')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Mühlenstr. 8')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Mühlenstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '8')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '3142')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260406')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '5')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_imedone_06, validate=False)
        result = message.get('PV2.37')
        self.assertEqual(result, 'N')

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
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.45', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO'
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

        segment.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19830711'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260406'
        segment.estimated_length_of_inpatient_stay = '5'
        segment.newborn_baby_indicator = 'N'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260406|5||||||||||||||||||||||||||N|N'
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
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.45', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.evn.recorded_date_time = '202604011935'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19830711'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260406'
        message.pv2.estimated_length_of_inpatient_stay = '5'
        message.pv2.newborn_baby_indicator = 'N'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_07 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202504011705||||202504011645\rPID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||620407^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN^^^DN||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rZBE|5678^KIS|202504011705||REFERENCE'

class Test_de_imedone_07_7_ADT_A03_Discharge_wiki_hl7_de(unittest.TestCase):
    """ 7. ADT^A03 - Discharge (wiki.hl7.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.47')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Nölting')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830711')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Kastanienweg 31')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Kastanienweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '31')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Mühlenstr. 8')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Mühlenstr.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '8')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Dresden')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Elisabethen-Spital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '620407')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Hüttner')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Frïedhelm')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '3142')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Ulmen-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_imedone_07, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19830711'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Elisabethen-Spital'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||54321^^^Ulmen-Klinik^PI||Bachmann^Liëselotte^^^^^L^A^^^G~Nölting^^^^^^M^A^^^G||19830711|F|||Kastanienweg 31&Kastanienweg&31^^Dresden^^^^H~Mühlenstr. 8&Mühlenstr.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Elisabethen-Spital|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='620407', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN')
        segment.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||620407^Hüttner^Frïedhelm^^^Dr.^^^Ulmen-Klinik^L^^^DN^^^DN||||||||||||3142^^^Ulmen-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
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

        message.pid.patient_identifier_list = CX(cx_1='54321', cx_4='Ulmen-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Nölting', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19830711'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Kastanienweg 31&Kastanienweg&31', xad_3='Dresden', xad_7='H'), XAD(xad_1='Mühlenstr. 8&Mühlenstr.&8', xad_3='Dresden', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Elisabethen-Spital'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='620407', xcn_2='Hüttner', xcn_3='Frïedhelm', xcn_6='Dr.', xcn_10='Ulmen-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN')
        message.pv1.visit_number = CX(cx_1='3142', cx_4='Ulmen-Klinik', cx_5='VN')
        message.pv1.discharge_disposition = CWE(cwe_1='011')
        message.pv1.admit_date_time = '202504011645'
        message.pv1.discharge_date_time = '202504061100'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_08 = 'MSH|^~\\&|MEDOS|RAD|SAP-ISH||20240120116412002||ADT^A01|1325-1|P|2.5|||||DEU|8859/1|DEU\rEVN|A01|20240120164122|20240120140000\rPID|||8765^^^KIS||Bachmann^Liëselotte^^^^^L~Schäfer^Liëselotte^^^^^B||19820504|F|||Falkenweg 15&Falkenweg&15^^Dresden-Neustadt^^01099^DEU^H~^^Chemnitz^^^DEU^N||^PRN^PH^^49^351^7823456~^PRN^FX^^49^351^7823457|^WPN^PH^^49^351^9182736||M|CAT||||||Herz-Jesu-Hospital|||DEU|Bühnentechniker|DEU\rNK1|1|Bachmann^Wërner|FTH|||||||||||M|M|19540108|||DEU|DEU|||||CAT\rPV1|1|I|IN2^4^3^CHI^^^^6||||||||||||||||0712843^^^^VN^KIS^20240120|||||||||||||||||||||||||20240120\rPV2|||||||||20240402'

class Test_de_imedone_08_8_ADT_A01_HL7_v2_5_admission_with_MEDOS_sending_application_oemig_de(unittest.TestCase):
    """ 8. ADT^A01 - HL7 v2.5 admission with MEDOS sending application (oemig.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'MEDOS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'RAD')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'SAP-ISH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20240120116412002')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '1325-1')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20240120164122')

# ################################################################################################################

    def test_navigate_EVN_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('EVN.3')
        self.assertEqual(result, '20240120140000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '8765')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Schäfer')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Liëselotte')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820504')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Falkenweg 15')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Falkenweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '15')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Dresden-Neustadt')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '01099')

# ################################################################################################################

    def test_navigate_PID_11_0_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Chemnitz')

# ################################################################################################################

    def test_navigate_PID_11_1_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[1].6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Herz-Jesu-Hospital')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_27(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PID.27')
        self.assertEqual(result, 'Bühnentechniker')

# ################################################################################################################

    def test_navigate_NK1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_NK1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.2')
        self.assertEqual(result, 'Bachmann')

# ################################################################################################################

    def test_navigate_NK1_2_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.2.2')
        self.assertEqual(result, 'Wërner')

# ################################################################################################################

    def test_navigate_NK1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.3')
        self.assertEqual(result, 'FTH')

# ################################################################################################################

    def test_navigate_NK1_14(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.14')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_NK1_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.15')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_NK1_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.16')
        self.assertEqual(result, '19540108')

# ################################################################################################################

    def test_navigate_NK1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_NK1_20(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.20')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_NK1_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('NK1.25')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN2')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '6')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '0712843')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_19_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.19.6')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_PV1_19_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.19.7')
        self.assertEqual(result, '20240120')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20240120')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_08, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20240402')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='MEDOS')
        segment.sending_facility = HD(hd_1='RAD')
        segment.receiving_application = HD(hd_1='SAP-ISH')
        segment.date_time_of_message = '20240120116412002'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01')
        segment.message_control_id = '1325-1'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|MEDOS|RAD|SAP-ISH||20240120116412002||ADT^A01|1325-1|P|2.5|||||DEU|8859/1|DEU'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20240120164122'
        segment.date_time_planned_event = '20240120140000'

        serialized = segment.serialize()
        expected = 'EVN|A01|20240120164122|20240120140000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='8765', cx_4='KIS')
        segment.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L'), XPN(xpn_1='Schäfer', xpn_2='Liëselotte', xpn_8='B')]
        segment.date_time_of_birth = '19820504'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Falkenweg 15&Falkenweg&15', xad_3='Dresden-Neustadt', xad_5='01099', xad_6='DEU', xad_7='H'), XAD(xad_3='Chemnitz', xad_6='DEU', xad_7='N')]
        segment.marital_status = CWE(cwe_1='M')
        segment.religion = CWE(cwe_1='CAT')
        segment.birth_place = 'Herz-Jesu-Hospital'
        segment.citizenship = CWE(cwe_1='DEU')
        segment.veterans_military_status = CWE(cwe_1='Bühnentechniker')

        serialized = segment.serialize()
        expected = 'PID|||8765^^^KIS||Bachmann^Liëselotte^^^^^L~Schäfer^Liëselotte^^^^^B||19820504|F|||Falkenweg 15&Falkenweg&15^^Dresden-Neustadt^^01099^DEU^H~^^Chemnitz^^^DEU^N||^PRN^PH^^49^351^7823456~^PRN^FX^^49^351^7823457|^WPN^PH^^49^351^9182736||M|CAT||||||Herz-Jesu-Hospital|||DEU|Bühnentechniker|DEU'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NK1(self) -> 'None':
        segment = NK1()

        segment.set_id_nk1 = '1'
        segment.name = XPN(xpn_1='Bachmann', xpn_2='Wërner')
        segment.relationship = CWE(cwe_1='FTH')
        segment.marital_status = CWE(cwe_1='M')
        segment.administrative_sex = CWE(cwe_1='M')
        segment.date_time_of_birth = '19540108'
        segment.citizenship = CWE(cwe_1='DEU')
        segment.primary_language = CWE(cwe_1='DEU')
        segment.religion = CWE(cwe_1='CAT')

        serialized = segment.serialize()
        expected = 'NK1|1|Bachmann^Wërner|FTH|||||||||||M|M|19540108|||DEU|DEU|||||CAT'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN2', pl_2='4', pl_3='3', pl_4='CHI', pl_8='6')
        segment.visit_number = CX(cx_1='0712843', cx_5='VN', cx_6='KIS', cx_7='20240120')
        segment.admit_date_time = '20240120'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN2^4^3^CHI^^^^6||||||||||||||||0712843^^^^VN^KIS^20240120|||||||||||||||||||||||||20240120'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20240402'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20240402'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='MEDOS')
        message.msh.sending_facility = HD(hd_1='RAD')
        message.msh.receiving_application = HD(hd_1='SAP-ISH')
        message.msh.date_time_of_message = '20240120116412002'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        message.msh.message_control_id = '1325-1'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU')

        message.evn.recorded_date_time = '20240120164122'
        message.evn.date_time_planned_event = '20240120140000'

        message.pid.patient_identifier_list = CX(cx_1='8765', cx_4='KIS')
        message.pid.patient_name = [XPN(xpn_1='Bachmann', xpn_2='Liëselotte', xpn_8='L'), XPN(xpn_1='Schäfer', xpn_2='Liëselotte', xpn_8='B')]
        message.pid.date_time_of_birth = '19820504'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Falkenweg 15&Falkenweg&15', xad_3='Dresden-Neustadt', xad_5='01099', xad_6='DEU', xad_7='H'), XAD(xad_3='Chemnitz', xad_6='DEU', xad_7='N')]
        message.pid.marital_status = CWE(cwe_1='M')
        message.pid.religion = CWE(cwe_1='CAT')
        message.pid.birth_place = 'Herz-Jesu-Hospital'
        message.pid.citizenship = CWE(cwe_1='DEU')
        message.pid.veterans_military_status = CWE(cwe_1='Bühnentechniker')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN2', pl_2='4', pl_3='3', pl_4='CHI', pl_8='6')
        message.pv1.visit_number = CX(cx_1='0712843', cx_5='VN', cx_6='KIS', cx_7='20240120')
        message.pv1.admit_date_time = '20240120'

        message.pv2.expected_discharge_date_time = '20240402'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_09 = 'MSH|^~\\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|991765815154685352|P|2.5||||||UNICODE UTF-8\rEVN|A08|202604031516+0200\rPID|1|54321|qcë8bbf2b09^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Nächstname^Rübën^^^Prof.||19970226|M|||Straßenweg 24^^Örtchen^^54321^DE||+49152 666 54321^^CP^^^^^^^^^+49152 666 54321~+49 351 666 789^^PH^^^^^^^^^+49 351 666 789~ëmail@beispiel.örg^NET^X.400^ëmail@beispiel.örg\rPV1|1|U'

class Test_de_imedone_09_9_ADT_A08_Patient_update_samedi_HL7gateway_to_iMedOne_hl7gateway_samedi_de(unittest.TestCase):
    """ 9. ADT^A08 - Patient update, samedi HL7gateway to iMedOne (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'APPLICATION')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'CLINIC')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260403151846+0200')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '991765815154685352')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604031516+0200')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 'qcë8bbf2b09')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Nächstname')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Rübën')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Prof.')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19970226')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Straßenweg 24')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Örtchen')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_09, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='APPLICATION')
        segment.receiving_facility = HD(hd_1='CLINIC')
        segment.date_time_of_message = '20260403151846+0200'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = '991765815154685352'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|991765815154685352|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604031516+0200'

        serialized = segment.serialize()
        expected = 'EVN|A08|202604031516+0200'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='qcë8bbf2b09', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='54321', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Nächstname', xpn_2='Rübën', xpn_5='Prof.')
        segment.date_time_of_birth = '19970226'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Straßenweg 24', xad_3='Örtchen', xad_5='54321', xad_6='DE')

        serialized = segment.serialize()
        expected = 'PID|1|54321|qcë8bbf2b09^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Nächstname^Rübën^^^Prof.||19970226|M|||Straßenweg 24^^Örtchen^^54321^DE||+49152 666 54321^^CP^^^^^^^^^+49152 666 54321~+49 351 666 789^^PH^^^^^^^^^+49 351 666 789~ëmail@beispiel.örg^NET^X.400^ëmail@beispiel.örg'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='U')

        serialized = segment.serialize()
        expected = 'PV1|1|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='APPLICATION')
        message.msh.receiving_facility = HD(hd_1='CLINIC')
        message.msh.date_time_of_message = '20260403151846+0200'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = '991765815154685352'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '202604031516+0200'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='qcë8bbf2b09', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='54321', cx_5='PT')]
        message.pid.patient_name = XPN(xpn_1='Nächstname', xpn_2='Rübën', xpn_5='Prof.')
        message.pid.date_time_of_birth = '19970226'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = XAD(xad_1='Straßenweg 24', xad_3='Örtchen', xad_5='54321', xad_6='DE')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='U')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_10 = 'MSH|^~\\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403152323+0200||ADT^A29^ADT_A21|21471412864163822995|P|2.5||||||UNICODE UTF-8\rEVN|A29|202604031523+0200\rPID|1|77|r72f56c8b65^^^&www.praxis-öst.de&DNS^PI~77^^^^PT||Lëtzt^Ërste||198510201\rPV1|1|U'

class Test_de_imedone_10_10_ADT_A29_Patient_deletion_samedi_HL7gateway_hl7gateway_samedi_de(unittest.TestCase):
    """ 10. ADT^A29 - Patient deletion, samedi HL7gateway (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        self.assertIsInstance(message, ADT_A21)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A21')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'APPLICATION')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'CLINIC')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260403152323+0200')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A29')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A21')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '21471412864163822995')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604031523+0200')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 'r72f56c8b65')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '77')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Lëtzt')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ërste')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '198510201')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_10, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='APPLICATION')
        segment.receiving_facility = HD(hd_1='CLINIC')
        segment.date_time_of_message = '20260403152323+0200'
        segment.message_type = MSG(msg_1='ADT', msg_2='A29', msg_3='ADT_A21')
        segment.message_control_id = '21471412864163822995'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403152323+0200||ADT^A29^ADT_A21|21471412864163822995|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604031523+0200'

        serialized = segment.serialize()
        expected = 'EVN|A29|202604031523+0200'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='r72f56c8b65', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='77', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Lëtzt', xpn_2='Ërste')
        segment.date_time_of_birth = '198510201'

        serialized = segment.serialize()
        expected = 'PID|1|77|r72f56c8b65^^^&www.praxis-öst.de&DNS^PI~77^^^^PT||Lëtzt^Ërste||198510201'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='U')

        serialized = segment.serialize()
        expected = 'PV1|1|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A21()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='APPLICATION')
        message.msh.receiving_facility = HD(hd_1='CLINIC')
        message.msh.date_time_of_message = '20260403152323+0200'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A29', msg_3='ADT_A21')
        message.msh.message_control_id = '21471412864163822995'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '202604031523+0200'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='r72f56c8b65', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='77', cx_5='PT')]
        message.pid.patient_name = XPN(xpn_1='Lëtzt', xpn_2='Ërste')
        message.pid.date_time_of_birth = '198510201'

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='U')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_11 = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1\rEVN|A08|202610260719\rPID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Prüfer^Hëide||19500524|F|||Prüfweg 30&Prüfweg 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH'

class Test_de_imedone_11_11_ADT_A08_Inbound_from_KIS_to_samedi_hl7gateway_samedi_de(unittest.TestCase):
    """ 11. ADT^A08 - Inbound from KIS to samedi (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KomServer')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'KOMSERV')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260523123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638170166537')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E62D52F8DE791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202610260719')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '4566')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '287711')

# ################################################################################################################

    def test_navigate_PID_3_1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[1].4')
        self.assertEqual(result, 'Rädvis')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Prüfer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Hëide')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19500524')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Prüfweg 30')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Prüfweg 30')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Görlitz')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '02826')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_11, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KomServer')
        segment.sending_facility = HD(hd_1='KOMSERV')
        segment.receiving_application = HD(hd_1='samedi-hl7gateway')
        segment.receiving_facility = HD(hd_1='samedi')
        segment.date_time_of_message = '20260523123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08')
        segment.message_control_id = '2638170166537'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E62D52F8DE791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202610260719'

        serialized = segment.serialize()
        expected = 'EVN|A08|202610260719'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='4566', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='287711', cx_4='Rädvis', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Prüfer', xpn_2='Hëide')
        segment.date_time_of_birth = '19500524'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Prüfweg 30&Prüfweg 30', xad_3='Görlitz', xad_5='02826', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Prüfer^Hëide||19500524|F|||Prüfweg 30&Prüfweg 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KomServer')
        message.msh.sending_facility = HD(hd_1='KOMSERV')
        message.msh.receiving_application = HD(hd_1='samedi-hl7gateway')
        message.msh.receiving_facility = HD(hd_1='samedi')
        message.msh.date_time_of_message = '20260523123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        message.msh.message_control_id = '2638170166537'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E62D52F8DE791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202610260719'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='4566', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='287711', cx_4='Rädvis', cx_5='PI')]
        message.pid.patient_name = XPN(xpn_1='Prüfer', xpn_2='Hëide')
        message.pid.date_time_of_birth = '19500524'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Prüfweg 30&Prüfweg 30', xad_3='Görlitz', xad_5='02826', xad_6='DE', xad_7='L')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_12 = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1\rEVN|A40|202502041715\rPID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Prüfer^Hëide||19500524|F|||Prüfweg 30&Prüfweg 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH\rMRG|4567~u263401ef91^^^&www.praxis-öst.de&DNS~4467533^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|'

class Test_de_imedone_12_12_ADT_A40_Patient_merge_hl7gateway_samedi_de(unittest.TestCase):
    """ 12. ADT^A40 - Patient merge (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        self.assertIsInstance(message, ADT_A39)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A39')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KomServer')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'KOMSERV')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260523123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A40')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638170166537')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E62D52F8DE791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202502041715')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '4566')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '287711')

# ################################################################################################################

    def test_navigate_PID_3_1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[1].4')
        self.assertEqual(result, 'Rädvis')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Prüfer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Hëide')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19500524')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Prüfweg 30')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Prüfweg 30')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Görlitz')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '02826')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_MRG_1_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[0]')
        self.assertEqual(result, '4567')

# ################################################################################################################

    def test_navigate_MRG_1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[1]')
        self.assertEqual(result, 'u263401ef91')

# ################################################################################################################

    def test_navigate_MRG_1_1_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[1].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_MRG_1_1_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[1].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_MRG_1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[2]')
        self.assertEqual(result, '4467533')

# ################################################################################################################

    def test_navigate_MRG_1_2_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[2].4.2')
        self.assertEqual(result, '1.2.276.0.76.3.1.660.1.1.1.2.1')

# ################################################################################################################

    def test_navigate_MRG_1_2_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[2].4.3')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MRG_1_2_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_12, validate=False)
        result = message.get('MRG.1[2].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KomServer')
        segment.sending_facility = HD(hd_1='KOMSERV')
        segment.receiving_application = HD(hd_1='samedi-hl7gateway')
        segment.receiving_facility = HD(hd_1='samedi')
        segment.date_time_of_message = '20260523123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A40')
        segment.message_control_id = '2638170166537'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E62D52F8DE791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202502041715'

        serialized = segment.serialize()
        expected = 'EVN|A40|202502041715'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='4566', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='287711', cx_4='Rädvis', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Prüfer', xpn_2='Hëide')
        segment.date_time_of_birth = '19500524'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Prüfweg 30&Prüfweg 30', xad_3='Görlitz', xad_5='02826', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Prüfer^Hëide||19500524|F|||Prüfweg 30&Prüfweg 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MRG(self) -> 'None':
        segment = MRG()

        segment.prior_patient_identifier_list = [CX(cx_1='4567'), CX(cx_1='u263401ef91', cx_4='&www.praxis-öst.de&DNS'), CX(cx_1='4467533', cx_4='&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO', cx_5='PI')]

        serialized = segment.serialize()
        expected = 'MRG|4567~u263401ef91^^^&www.praxis-öst.de&DNS~4467533^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A39()

        message.msh.sending_application = HD(hd_1='KomServer')
        message.msh.sending_facility = HD(hd_1='KOMSERV')
        message.msh.receiving_application = HD(hd_1='samedi-hl7gateway')
        message.msh.receiving_facility = HD(hd_1='samedi')
        message.msh.date_time_of_message = '20260523123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        message.msh.message_control_id = '2638170166537'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E62D52F8DE791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202502041715'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_13 = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|8615615175374780398|P|2.5||||||UNICODE UTF-8\rSCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked\rTQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min\rNTE||_default|Comment\rNTE||Affected body parts|arm~left leg~head\rNTE||Kommentar zum Patienten|patient comment, patient without external patient number\rPID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M|||Gleisstraße 24^^Potsdam^^14467^DE||+49 172 7654321^^CP^^^^^^^^^+49 172 7654321~+49 351 76543-210^^PH^^^^^^^^^+49 351 76543-210~pöst@beispiel.örg^NET^X.400^pöst@beispiel.örg~+49 351 76543-211^^FX^^^^^^^^^+49 351 76543-211\rRGS|1|A\rAIG|1|A|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s\rAIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s'

class Test_de_imedone_13_13_SIU_S12_New_appointment_booking_samedi_to_iMedOne_hl7gateway_samedi_de(unittest.TestCase):
    """ 13. SIU^S12 - New appointment booking, samedi to iMedOne (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260207130859+0100')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '8615615175374780398')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, 'a-ëqcdl7hwscfuze4w')

# ################################################################################################################

    def test_navigate_SCH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('SCH.6')
        self.assertEqual(result, 'BOOKED')

# ################################################################################################################

    def test_navigate_SCH_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('SCH.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_SCH_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('SCH.8.2')
        self.assertEqual(result, 'MRT')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Booked')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '20260516130000+0200')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '20260516133000+0200')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_NTE_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('NTE.2')
        self.assertEqual(result, '_default')

# ################################################################################################################

    def test_navigate_NTE_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('NTE.3')
        self.assertEqual(result, 'Comment')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 's1299de4014')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Förster')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Stëfan')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820511')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Gleisstraße 24')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Potsdam')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '14467')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_AIG_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.2')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_AIG_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_AIG_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.3.2')
        self.assertEqual(result, 'Stëfan Möritz')

# ################################################################################################################

    def test_navigate_AIG_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.3.3')
        self.assertEqual(result, '99SAMEDI-RESOURCE')

# ################################################################################################################

    def test_navigate_AIG_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.3.4')
        self.assertEqual(result, 'radiologist')

# ################################################################################################################

    def test_navigate_AIG_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.8')
        self.assertEqual(result, '20260516130000+0200')

# ################################################################################################################

    def test_navigate_AIG_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.11')
        self.assertEqual(result, '1800')

# ################################################################################################################

    def test_navigate_AIG_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_13, validate=False)
        result = message.get('AIG.12')
        self.assertEqual(result, 's')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='system')
        segment.receiving_facility = HD(hd_1='clinic')
        segment.date_time_of_message = '20260207130859+0100'
        segment.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        segment.message_control_id = '8615615175374780398'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|8615615175374780398|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        segment.event_reason = CWE(cwe_1='BOOKED')
        segment.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        segment.filler_status_code = CWE(cwe_1='Booked')

        serialized = segment.serialize()
        expected = 'SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '20260516130000+0200'
        segment.end_datetime = '20260516133000+0200'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = '_default'
        segment.comment = 'Comment'

        serialized = segment.serialize()
        expected = 'NTE||_default|Comment'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE_2(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = 'Affected body parts'
        segment.comment = ['arm', 'left leg', 'head']

        serialized = segment.serialize()
        expected = 'NTE||Affected body parts|arm~left leg~head'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE_3(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = 'Kommentar zum Patienten'
        segment.comment = 'patient comment, patient without external patient number'

        serialized = segment.serialize()
        expected = 'NTE||Kommentar zum Patienten|patient comment, patient without external patient number'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='s1299de4014', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Förster', xpn_2='Stëfan')
        segment.date_time_of_birth = '19820511'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Gleisstraße 24', xad_3='Potsdam', xad_5='14467', xad_6='DE')

        serialized = segment.serialize()
        expected = 'PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M|||Gleisstraße 24^^Potsdam^^14467^DE||+49 172 7654321^^CP^^^^^^^^^+49 172 7654321~+49 351 76543-210^^PH^^^^^^^^^+49 351 76543-210~pöst@beispiel.örg^NET^X.400^pöst@beispiel.örg~+49 351 76543-211^^FX^^^^^^^^^+49 351 76543-211'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'A'

        serialized = segment.serialize()
        expected = 'RGS|1|A'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '1'
        segment.segment_action_code = 'A'
        segment.resource_id = CWE(cwe_1='2', cwe_2='Stëfan Möritz', cwe_3='99SAMEDI-RESOURCE', cwe_4='radiologist')
        segment.start_date_time = '20260516130000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|1|A|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG_2(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '2'
        segment.segment_action_code = 'A'
        segment.resource_id = CWE(cwe_1='1', cwe_2='Sprechzimmer', cwe_3='99SAMEDI-RESOURCE', cwe_4='room-1')
        segment.start_date_time = '20260516130000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='system')
        message.msh.receiving_facility = HD(hd_1='clinic')
        message.msh.date_time_of_message = '20260207130859+0100'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        message.msh.message_control_id = '8615615175374780398'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.sch.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        message.sch.event_reason = CWE(cwe_1='BOOKED')
        message.sch.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        message.sch.filler_status_code = CWE(cwe_1='Booked')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '20260516130000+0200'
        message.tq1.end_datetime = '20260516133000+0200'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        message.nte.source_of_comment = '_default'
        message.nte.comment = 'Comment'

        message.nte.source_of_comment = 'Affected body parts'
        message.nte.comment = ['arm', 'left leg', 'head']

        message.nte.source_of_comment = 'Kommentar zum Patienten'
        message.nte.comment = 'patient comment, patient without external patient number'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_14 = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131000+0100||SIU^S13^SIU_S12|22310718558850378493|P|2.5||||||UNICODE UTF-8\rSCH||a-ëqcdl7hwscfuze4w||||BOOKED||^Test|1800||^^M30^20260410135000+0200^20260410142000+0200||||||||||||||Booked\rTQ1|1||||||20260410135000+0200|20260410142000+0200|||||30^min\rRGS|1|D\rAIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^c2|||||20260410125500+0200|||1800|s\rRGS|2|A\rAIG|2|A|2^Doc^99SAMEDI-RESOURCE^c1|||||20260410135000+0200|||1800|s'

class Test_de_imedone_14_14_SIU_S13_Appointment_rescheduling_samedi_to_iMedOne_hl7gateway_samedi_de(unittest.TestCase):
    """ 14. SIU^S13 - Appointment rescheduling, samedi to iMedOne (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260207131000+0100')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S13')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '22310718558850378493')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, 'a-ëqcdl7hwscfuze4w')

# ################################################################################################################

    def test_navigate_SCH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('SCH.6')
        self.assertEqual(result, 'BOOKED')

# ################################################################################################################

    def test_navigate_SCH_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('SCH.8.2')
        self.assertEqual(result, 'Test')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Booked')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '20260410135000+0200')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '20260410142000+0200')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_AIG_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.2')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_AIG_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.3.2')
        self.assertEqual(result, 'Sprechzimmer')

# ################################################################################################################

    def test_navigate_AIG_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.3.3')
        self.assertEqual(result, '99SAMEDI-RESOURCE')

# ################################################################################################################

    def test_navigate_AIG_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.3.4')
        self.assertEqual(result, 'c2')

# ################################################################################################################

    def test_navigate_AIG_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.8')
        self.assertEqual(result, '20260410125500+0200')

# ################################################################################################################

    def test_navigate_AIG_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.11')
        self.assertEqual(result, '1800')

# ################################################################################################################

    def test_navigate_AIG_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_14, validate=False)
        result = message.get('AIG.12')
        self.assertEqual(result, 's')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='system')
        segment.receiving_facility = HD(hd_1='clinic')
        segment.date_time_of_message = '20260207131000+0100'
        segment.message_type = MSG(msg_1='SIU', msg_2='S13', msg_3='SIU_S12')
        segment.message_control_id = '22310718558850378493'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131000+0100||SIU^S13^SIU_S12|22310718558850378493|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        segment.event_reason = CWE(cwe_1='BOOKED')
        segment.appointment_type = CWE(cwe_2='Test')
        segment.filler_status_code = CWE(cwe_1='Booked')

        serialized = segment.serialize()
        expected = 'SCH||a-ëqcdl7hwscfuze4w||||BOOKED||^Test|1800||^^M30^20260410135000+0200^20260410142000+0200||||||||||||||Booked'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '20260410135000+0200'
        segment.end_datetime = '20260410142000+0200'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||20260410135000+0200|20260410142000+0200|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'D'

        serialized = segment.serialize()
        expected = 'RGS|1|D'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '1'
        segment.segment_action_code = 'D'
        segment.resource_id = CWE(cwe_1='1', cwe_2='Sprechzimmer', cwe_3='99SAMEDI-RESOURCE', cwe_4='c2')
        segment.start_date_time = '20260410125500+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^c2|||||20260410125500+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS_2(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '2'
        segment.segment_action_code = 'A'

        serialized = segment.serialize()
        expected = 'RGS|2|A'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG_2(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '2'
        segment.segment_action_code = 'A'
        segment.resource_id = CWE(cwe_1='2', cwe_2='Doc', cwe_3='99SAMEDI-RESOURCE', cwe_4='c1')
        segment.start_date_time = '20260410135000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|2|A|2^Doc^99SAMEDI-RESOURCE^c1|||||20260410135000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='system')
        message.msh.receiving_facility = HD(hd_1='clinic')
        message.msh.date_time_of_message = '20260207131000+0100'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S13', msg_3='SIU_S12')
        message.msh.message_control_id = '22310718558850378493'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.sch.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        message.sch.event_reason = CWE(cwe_1='BOOKED')
        message.sch.appointment_type = CWE(cwe_2='Test')
        message.sch.filler_status_code = CWE(cwe_1='Booked')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '20260410135000+0200'
        message.tq1.end_datetime = '20260410142000+0200'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_15 = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131202+0100||SIU^S14^SIU_S12|23267051019177332434|P|2.5||||||UNICODE UTF-8\rSCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Booked\rTQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min\rNTE||_default|updated comment\rNTE||Kommentar zum Patienten|patient comment, patient without external patient number\rPID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M\rRGS|1|X\rAIG|1|X|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516140000+0200|||1800|s\rAIG|2|X|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s'

class Test_de_imedone_15_15_SIU_S14_Appointment_modification_samedi_to_iMedOne_hl7gateway_samedi_de(unittest.TestCase):
    """ 15. SIU^S14 - Appointment modification, samedi to iMedOne (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260207131202+0100')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S14')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '23267051019177332434')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, 'a-ëqcdl7hwscfuze4w')

# ################################################################################################################

    def test_navigate_SCH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('SCH.6')
        self.assertEqual(result, 'BOOKED')

# ################################################################################################################

    def test_navigate_SCH_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('SCH.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_SCH_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('SCH.8.2')
        self.assertEqual(result, 'MRT')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Booked')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '20260516140000+0200')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '20260516143000+0200')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_NTE_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('NTE.2')
        self.assertEqual(result, '_default')

# ################################################################################################################

    def test_navigate_NTE_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('NTE.3')
        self.assertEqual(result, 'updated comment')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 's1299de4014')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Förster')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Stëfan')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820511')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'X')

# ################################################################################################################

    def test_navigate_AIG_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.2')
        self.assertEqual(result, 'X')

# ################################################################################################################

    def test_navigate_AIG_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_AIG_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.3.2')
        self.assertEqual(result, 'Stëfan Möritz')

# ################################################################################################################

    def test_navigate_AIG_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.3.3')
        self.assertEqual(result, '99SAMEDI-RESOURCE')

# ################################################################################################################

    def test_navigate_AIG_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.3.4')
        self.assertEqual(result, 'radiologist')

# ################################################################################################################

    def test_navigate_AIG_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.8')
        self.assertEqual(result, '20260516140000+0200')

# ################################################################################################################

    def test_navigate_AIG_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.11')
        self.assertEqual(result, '1800')

# ################################################################################################################

    def test_navigate_AIG_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_15, validate=False)
        result = message.get('AIG.12')
        self.assertEqual(result, 's')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='system')
        segment.receiving_facility = HD(hd_1='clinic')
        segment.date_time_of_message = '20260207131202+0100'
        segment.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S12')
        segment.message_control_id = '23267051019177332434'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131202+0100||SIU^S14^SIU_S12|23267051019177332434|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        segment.event_reason = CWE(cwe_1='BOOKED')
        segment.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        segment.filler_status_code = CWE(cwe_1='Booked')

        serialized = segment.serialize()
        expected = 'SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Booked'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '20260516140000+0200'
        segment.end_datetime = '20260516143000+0200'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = '_default'
        segment.comment = 'updated comment'

        serialized = segment.serialize()
        expected = 'NTE||_default|updated comment'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE_2(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = 'Kommentar zum Patienten'
        segment.comment = 'patient comment, patient without external patient number'

        serialized = segment.serialize()
        expected = 'NTE||Kommentar zum Patienten|patient comment, patient without external patient number'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='s1299de4014', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Förster', xpn_2='Stëfan')
        segment.date_time_of_birth = '19820511'
        segment.administrative_sex = CWE(cwe_1='M')

        serialized = segment.serialize()
        expected = 'PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'X'

        serialized = segment.serialize()
        expected = 'RGS|1|X'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '1'
        segment.segment_action_code = 'X'
        segment.resource_id = CWE(cwe_1='2', cwe_2='Stëfan Möritz', cwe_3='99SAMEDI-RESOURCE', cwe_4='radiologist')
        segment.start_date_time = '20260516140000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|1|X|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516140000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG_2(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '2'
        segment.segment_action_code = 'X'
        segment.resource_id = CWE(cwe_1='1', cwe_2='Sprechzimmer', cwe_3='99SAMEDI-RESOURCE', cwe_4='room-1')
        segment.start_date_time = '20260516140000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|2|X|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='system')
        message.msh.receiving_facility = HD(hd_1='clinic')
        message.msh.date_time_of_message = '20260207131202+0100'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S12')
        message.msh.message_control_id = '23267051019177332434'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.sch.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        message.sch.event_reason = CWE(cwe_1='BOOKED')
        message.sch.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        message.sch.filler_status_code = CWE(cwe_1='Booked')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '20260516140000+0200'
        message.tq1.end_datetime = '20260516143000+0200'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        message.nte.source_of_comment = '_default'
        message.nte.comment = 'updated comment'

        message.nte.source_of_comment = 'Kommentar zum Patienten'
        message.nte.comment = 'patient comment, patient without external patient number'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_16 = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131507+0100||SIU^S15^SIU_S12|7374561721650221901|P|2.5||||||UNICODE UTF-8\rSCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Deleted\rTQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min\rNTE||_default|updated comment\rNTE||Kommentar zum Patienten|patient comment, patient without external patient number\rPID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M\rRGS|1|D\rAIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s'

class Test_de_imedone_16_16_SIU_S15_Appointment_cancellation_samedi_to_iMedOne_hl7gateway_samedi_de(unittest.TestCase):
    """ 16. SIU^S15 - Appointment cancellation, samedi to iMedOne (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260207131507+0100')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S15')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '7374561721650221901')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, 'a-ëqcdl7hwscfuze4w')

# ################################################################################################################

    def test_navigate_SCH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('SCH.6')
        self.assertEqual(result, 'BOOKED')

# ################################################################################################################

    def test_navigate_SCH_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('SCH.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_SCH_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('SCH.8.2')
        self.assertEqual(result, 'MRT')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Deleted')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '20260516140000+0200')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '20260516143000+0200')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_NTE_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('NTE.2')
        self.assertEqual(result, '_default')

# ################################################################################################################

    def test_navigate_NTE_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('NTE.3')
        self.assertEqual(result, 'updated comment')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 's1299de4014')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Förster')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Stëfan')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820511')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_AIG_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.2')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_AIG_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.3.2')
        self.assertEqual(result, 'Sprechzimmer')

# ################################################################################################################

    def test_navigate_AIG_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.3.3')
        self.assertEqual(result, '99SAMEDI-RESOURCE')

# ################################################################################################################

    def test_navigate_AIG_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.3.4')
        self.assertEqual(result, 'room-1')

# ################################################################################################################

    def test_navigate_AIG_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.8')
        self.assertEqual(result, '20260516140000+0200')

# ################################################################################################################

    def test_navigate_AIG_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.11')
        self.assertEqual(result, '1800')

# ################################################################################################################

    def test_navigate_AIG_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_16, validate=False)
        result = message.get('AIG.12')
        self.assertEqual(result, 's')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='system')
        segment.receiving_facility = HD(hd_1='clinic')
        segment.date_time_of_message = '20260207131507+0100'
        segment.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S12')
        segment.message_control_id = '7374561721650221901'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207131507+0100||SIU^S15^SIU_S12|7374561721650221901|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        segment.event_reason = CWE(cwe_1='BOOKED')
        segment.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        segment.filler_status_code = CWE(cwe_1='Deleted')

        serialized = segment.serialize()
        expected = 'SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Deleted'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '20260516140000+0200'
        segment.end_datetime = '20260516143000+0200'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = '_default'
        segment.comment = 'updated comment'

        serialized = segment.serialize()
        expected = 'NTE||_default|updated comment'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE_2(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = 'Kommentar zum Patienten'
        segment.comment = 'patient comment, patient without external patient number'

        serialized = segment.serialize()
        expected = 'NTE||Kommentar zum Patienten|patient comment, patient without external patient number'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='s1299de4014', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Förster', xpn_2='Stëfan')
        segment.date_time_of_birth = '19820511'
        segment.administrative_sex = CWE(cwe_1='M')

        serialized = segment.serialize()
        expected = 'PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Förster^Stëfan||19820511|M'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'D'

        serialized = segment.serialize()
        expected = 'RGS|1|D'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '1'
        segment.segment_action_code = 'D'
        segment.resource_id = CWE(cwe_1='1', cwe_2='Sprechzimmer', cwe_3='99SAMEDI-RESOURCE', cwe_4='room-1')
        segment.start_date_time = '20260516140000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='system')
        message.msh.receiving_facility = HD(hd_1='clinic')
        message.msh.date_time_of_message = '20260207131507+0100'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S12')
        message.msh.message_control_id = '7374561721650221901'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.sch.filler_appointment_id = EI(ei_1='a-ëqcdl7hwscfuze4w')
        message.sch.event_reason = CWE(cwe_1='BOOKED')
        message.sch.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        message.sch.filler_status_code = CWE(cwe_1='Deleted')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '20260516140000+0200'
        message.tq1.end_datetime = '20260516143000+0200'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        message.nte.source_of_comment = '_default'
        message.nte.comment = 'updated comment'

        message.nte.source_of_comment = 'Kommentar zum Patienten'
        message.nte.comment = 'patient comment, patient without external patient number'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_17 = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207124406+0100||SIU^S12^SIU_S12|5027690727398224048|P|2.5||||||UNICODE UTF-8\rSCH||b-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516100000+0200^20260516103000+0200||||||||||||||Booked\rTQ1|1||||||20260516100000+0200|20260516103000+0200|||||30^min\rNTE||Kommentar zum Patienten|patient with an external patient ID\rPID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Kräuter^Ännelïese|||F\rRGS|1|A\rAIG|1|A|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516100000+0200|||1800|s\rAIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516100000+0200|||1800|'

class Test_de_imedone_17_17_SIU_S12_Appointment_with_external_patient_number_hl7gateway_samedi_de(unittest.TestCase):
    """ 17. SIU^S12 - Appointment with external patient number (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260207124406+0100')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '5027690727398224048')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, 'b-ëqcdl7hwscfuze4w')

# ################################################################################################################

    def test_navigate_SCH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('SCH.6')
        self.assertEqual(result, 'BOOKED')

# ################################################################################################################

    def test_navigate_SCH_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('SCH.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_SCH_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('SCH.8.2')
        self.assertEqual(result, 'MRT')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Booked')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '20260516100000+0200')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '20260516103000+0200')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_NTE_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('NTE.2')
        self.assertEqual(result, 'Kommentar zum Patienten')

# ################################################################################################################

    def test_navigate_NTE_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('NTE.3')
        self.assertEqual(result, 'patient with an external patient ID')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 't4538ef9435')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Kräuter')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ännelïese')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_AIG_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIG_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.2')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_AIG_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_AIG_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.3.2')
        self.assertEqual(result, 'Stëfan Möritz')

# ################################################################################################################

    def test_navigate_AIG_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.3.3')
        self.assertEqual(result, '99SAMEDI-RESOURCE')

# ################################################################################################################

    def test_navigate_AIG_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.3.4')
        self.assertEqual(result, 'radiologist')

# ################################################################################################################

    def test_navigate_AIG_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.8')
        self.assertEqual(result, '20260516100000+0200')

# ################################################################################################################

    def test_navigate_AIG_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.11')
        self.assertEqual(result, '1800')

# ################################################################################################################

    def test_navigate_AIG_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_17, validate=False)
        result = message.get('AIG.12')
        self.assertEqual(result, 's')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='samedi-hl7gateway')
        segment.sending_facility = HD(hd_1='samedi')
        segment.receiving_application = HD(hd_1='system')
        segment.receiving_facility = HD(hd_1='clinic')
        segment.date_time_of_message = '20260207124406+0100'
        segment.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        segment.message_control_id = '5027690727398224048'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|samedi-hl7gateway|samedi|system|clinic|20260207124406+0100||SIU^S12^SIU_S12|5027690727398224048|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='b-ëqcdl7hwscfuze4w')
        segment.event_reason = CWE(cwe_1='BOOKED')
        segment.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        segment.filler_status_code = CWE(cwe_1='Booked')

        serialized = segment.serialize()
        expected = 'SCH||b-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516100000+0200^20260516103000+0200||||||||||||||Booked'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '20260516100000+0200'
        segment.end_datetime = '20260516103000+0200'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||20260516100000+0200|20260516103000+0200|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_NTE(self) -> 'None':
        segment = NTE()

        segment.source_of_comment = 'Kommentar zum Patienten'
        segment.comment = 'patient with an external patient ID'

        serialized = segment.serialize()
        expected = 'NTE||Kommentar zum Patienten|patient with an external patient ID'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='t4538ef9435', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='54321', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Kräuter', xpn_2='Ännelïese')
        segment.administrative_sex = CWE(cwe_1='F')

        serialized = segment.serialize()
        expected = 'PID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Kräuter^Ännelïese|||F'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'A'

        serialized = segment.serialize()
        expected = 'RGS|1|A'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '1'
        segment.segment_action_code = 'A'
        segment.resource_id = CWE(cwe_1='2', cwe_2='Stëfan Möritz', cwe_3='99SAMEDI-RESOURCE', cwe_4='radiologist')
        segment.start_date_time = '20260516100000+0200'
        segment.duration = '1800'
        segment.duration_units = CNE(cne_1='s')

        serialized = segment.serialize()
        expected = 'AIG|1|A|2^Stëfan Möritz^99SAMEDI-RESOURCE^radiologist|||||20260516100000+0200|||1800|s'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIG_2(self) -> 'None':
        segment = AIG()

        segment.set_id_aig = '2'
        segment.segment_action_code = 'A'
        segment.resource_id = CWE(cwe_1='1', cwe_2='Sprechzimmer', cwe_3='99SAMEDI-RESOURCE', cwe_4='room-1')
        segment.start_date_time = '20260516100000+0200'
        segment.duration = '1800'

        serialized = segment.serialize()
        expected = 'AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516100000+0200|||1800|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='samedi-hl7gateway')
        message.msh.sending_facility = HD(hd_1='samedi')
        message.msh.receiving_application = HD(hd_1='system')
        message.msh.receiving_facility = HD(hd_1='clinic')
        message.msh.date_time_of_message = '20260207124406+0100'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        message.msh.message_control_id = '5027690727398224048'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.sch.filler_appointment_id = EI(ei_1='b-ëqcdl7hwscfuze4w')
        message.sch.event_reason = CWE(cwe_1='BOOKED')
        message.sch.appointment_type = CWE(cwe_1='1', cwe_2='MRT')
        message.sch.filler_status_code = CWE(cwe_1='Booked')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '20260516100000+0200'
        message.tq1.end_datetime = '20260516103000+0200'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        message.nte.source_of_comment = 'Kommentar zum Patienten'
        message.nte.comment = 'patient with an external patient ID'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_18 = 'MSH|^~\\&|system|clinic|samedi-hl7gateway|samedi|20260101000000||SIU^S12^SIU_S12|87654|P|2.5||||||8859/1\rSCH||567890^system||||||Sprechstunde, Peter Mueller|||||||||||||||||Booked\rTQ1|1||||||202601150800|202601150830|||||30^min\rPID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Kräuter^Ännelïese|||F\rRGS|1|A\rAIL|1||room-1|||202601150800^YYYYLLDDHHMM|||30|min\rAIP|1||radiologist|||202601150800^YYYYLLDDHHMM|||30|min'

class Test_de_imedone_18_18_SIU_S12_Inbound_from_KIS_to_samedi_hl7gateway_samedi_de(unittest.TestCase):
    """ 18. SIU^S12 - Inbound from KIS to samedi (hl7gateway.samedi.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        self.assertIsInstance(message, SIU_S12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'SIU_S12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'clinic')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260101000000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'SIU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'S12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'SIU_S12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '87654')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_SCH_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('SCH.2')
        self.assertEqual(result, '567890')

# ################################################################################################################

    def test_navigate_SCH_2_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('SCH.2.2')
        self.assertEqual(result, 'system')

# ################################################################################################################

    def test_navigate_SCH_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('SCH.8')
        self.assertEqual(result, 'Sprechstunde, Peter Mueller')

# ################################################################################################################

    def test_navigate_SCH_25(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('SCH.25')
        self.assertEqual(result, 'Booked')

# ################################################################################################################

    def test_navigate_TQ1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('TQ1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_TQ1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('TQ1.7')
        self.assertEqual(result, '202601150800')

# ################################################################################################################

    def test_navigate_TQ1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('TQ1.8')
        self.assertEqual(result, '202601150830')

# ################################################################################################################

    def test_navigate_TQ1_13(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('TQ1.13')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_TQ1_13_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('TQ1.13.2')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 't4538ef9435')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-öst.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Kräuter')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Ännelïese')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_RGS_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('RGS.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_RGS_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('RGS.2')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_AIL_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIL_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.3')
        self.assertEqual(result, 'room-1')

# ################################################################################################################

    def test_navigate_AIL_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.6')
        self.assertEqual(result, '202601150800')

# ################################################################################################################

    def test_navigate_AIL_6_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.6.2')
        self.assertEqual(result, 'YYYYLLDDHHMM')

# ################################################################################################################

    def test_navigate_AIL_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.9')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_AIL_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIL.10')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_navigate_AIP_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_AIP_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.3')
        self.assertEqual(result, 'radiologist')

# ################################################################################################################

    def test_navigate_AIP_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.6')
        self.assertEqual(result, '202601150800')

# ################################################################################################################

    def test_navigate_AIP_6_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.6.2')
        self.assertEqual(result, 'YYYYLLDDHHMM')

# ################################################################################################################

    def test_navigate_AIP_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.9')
        self.assertEqual(result, '30')

# ################################################################################################################

    def test_navigate_AIP_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_18, validate=False)
        result = message.get('AIP.10')
        self.assertEqual(result, 'min')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='system')
        segment.sending_facility = HD(hd_1='clinic')
        segment.receiving_application = HD(hd_1='samedi-hl7gateway')
        segment.receiving_facility = HD(hd_1='samedi')
        segment.date_time_of_message = '20260101000000'
        segment.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        segment.message_control_id = '87654'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|system|clinic|samedi-hl7gateway|samedi|20260101000000||SIU^S12^SIU_S12|87654|P|2.5||||||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SCH(self) -> 'None':
        segment = SCH()

        segment.filler_appointment_id = EI(ei_1='567890', ei_2='system')
        segment.appointment_type = CWE(cwe_1='Sprechstunde, Peter Mueller')
        segment.filler_status_code = CWE(cwe_1='Booked')

        serialized = segment.serialize()
        expected = 'SCH||567890^system||||||Sprechstunde, Peter Mueller|||||||||||||||||Booked'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_TQ1(self) -> 'None':
        segment = TQ1()

        segment.set_id_tq1 = '1'
        segment.start_datetime = '202601150800'
        segment.end_datetime = '202601150830'
        segment.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = segment.serialize()
        expected = 'TQ1|1||||||202601150800|202601150830|||||30^min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='t4538ef9435', cx_4='&www.praxis-öst.de&DNS', cx_5='PI'), CX(cx_1='54321', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Kräuter', xpn_2='Ännelïese')
        segment.administrative_sex = CWE(cwe_1='F')

        serialized = segment.serialize()
        expected = 'PID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Kräuter^Ännelïese|||F'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_RGS(self) -> 'None':
        segment = RGS()

        segment.set_id_rgs = '1'
        segment.segment_action_code = 'A'

        serialized = segment.serialize()
        expected = 'RGS|1|A'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIL(self) -> 'None':
        segment = AIL()

        segment.set_id_ail = '1'
        segment.location_resource_id = PL(pl_1='room-1')
        segment.start_date_time = '202601150800^YYYYLLDDHHMM'
        segment.duration = '30'
        segment.duration_units = CNE(cne_1='min')

        serialized = segment.serialize()
        expected = 'AIL|1||room-1|||202601150800^YYYYLLDDHHMM|||30|min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_AIP(self) -> 'None':
        segment = AIP()

        segment.set_id_aip = '1'
        segment.personnel_resource_id = XCN(xcn_1='radiologist')
        segment.start_date_time = '202601150800^YYYYLLDDHHMM'
        segment.duration = '30'
        segment.duration_units = CNE(cne_1='min')

        serialized = segment.serialize()
        expected = 'AIP|1||radiologist|||202601150800^YYYYLLDDHHMM|||30|min'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = SIU_S12()

        message.msh.sending_application = HD(hd_1='system')
        message.msh.sending_facility = HD(hd_1='clinic')
        message.msh.receiving_application = HD(hd_1='samedi-hl7gateway')
        message.msh.receiving_facility = HD(hd_1='samedi')
        message.msh.date_time_of_message = '20260101000000'
        message.msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        message.msh.message_control_id = '87654'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = '8859/1'

        message.sch.filler_appointment_id = EI(ei_1='567890', ei_2='system')
        message.sch.appointment_type = CWE(cwe_1='Sprechstunde, Peter Mueller')
        message.sch.filler_status_code = CWE(cwe_1='Booked')

        message.tq1.set_id_tq1 = '1'
        message.tq1.start_datetime = '202601150800'
        message.tq1.end_datetime = '202601150830'
        message.tq1.occurrence_duration = CQ(cq_1='30', cq_2='min')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_19 = 'MSH|^~\\&|||||20260912142642||ADT^A01^ADT_A01|MSG00001|P|2.6|\rEVN|A01|20260912142642||\rPID|0||123456789^^^PVS1||Prüffrau^Sïlke||19670714|F|||Prüfstraße 789^^Prüfstadt^^98765||09876/54321-0~^NET^Internet^heinz.prüfmann@prüfpost.com~0987/65432109^^CP\rPV1||I|||||||||||||||||8523|\rIN1|1|0|BKV2|ÜLMENKRANKENVERSICHERUNG|||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_imedone_19_19_ADT_A01_E_ConsentPro_Thieme_Compliance_support_thieme_compliance_de(unittest.TestCase):
    """ 19. ADT^A01 - E-ConsentPro / Thieme Compliance (support.thieme-compliance.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260912142642')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'MSG00001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260912142642')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '123456789')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'PVS1')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Prüffrau')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Sïlke')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19670714')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Prüfstraße 789')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Prüfstadt')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '98765')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '8523')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'BKV2')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'ÜLMENKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_imedone_19, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.date_time_of_message = '20260912142642'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'MSG00001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|||||20260912142642||ADT^A01^ADT_A01|MSG00001|P|2.6|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260912142642'

        serialized = segment.serialize()
        expected = 'EVN|A01|20260912142642||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '0'
        segment.patient_identifier_list = CX(cx_1='123456789', cx_4='PVS1')
        segment.patient_name = XPN(xpn_1='Prüffrau', xpn_2='Sïlke')
        segment.date_time_of_birth = '19670714'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Prüfstraße 789', xad_3='Prüfstadt', xad_5='98765')

        serialized = segment.serialize()
        expected = 'PID|0||123456789^^^PVS1||Prüffrau^Sïlke||19670714|F|||Prüfstraße 789^^Prüfstadt^^98765||09876/54321-0~^NET^Internet^heinz.prüfmann@prüfpost.com~0987/65432109^^CP'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.visit_number = CX(cx_1='8523')

        serialized = segment.serialize()
        expected = 'PV1||I|||||||||||||||||8523|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='BKV2')
        segment.insurance_company_name = XON(xon_1='ÜLMENKRANKENVERSICHERUNG')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|BKV2|ÜLMENKRANKENVERSICHERUNG|||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.date_time_of_message = '20260912142642'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'MSG00001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260912142642'

        message.pid.set_id_pid = '0'
        message.pid.patient_identifier_list = CX(cx_1='123456789', cx_4='PVS1')
        message.pid.patient_name = XPN(xpn_1='Prüffrau', xpn_2='Sïlke')
        message.pid.date_time_of_birth = '19670714'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Prüfstraße 789', xad_3='Prüfstadt', xad_5='98765')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.visit_number = CX(cx_1='8523')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_imedone_20 = 'MSH|^~\\&|||||20260912142642||ADT^A02^ADT_A02|MSG00001|P|2.6|\rEVN|A02|20260912142642||\rPID|0||123456789^^^PVS1||Prüffrau^Sïlke||19670714|F|||Prüfstraße 789^^Prüfstadt^^98765||09876/54321-0~^NET^X.400^heinz.prüfmann@prüfpost.com~0987/65432109^^CP\rPV1||I|neüStation^neüZimmer^neüBett|||ältStation^ältZimmer^ältBett|0100^TÄT,HËINZ|0148^TÄT,MÄJA ES||SUR|||||||0148^TÄT,HËINZ|S|2800|A|||||||||||||||||||GËNKRH||||||'

class Test_de_imedone_20_20_ADT_A02_Transfer_E_ConsentPro_Thieme_Compliance_support_thieme_compliance_de(unittest.TestCase):
    """ 20. ADT^A02 - Transfer, E-ConsentPro / Thieme Compliance (support.thieme-compliance.de)
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260912142642')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'MSG00001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260912142642')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '123456789')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'PVS1')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Prüffrau')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Sïlke')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19670714')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Prüfstraße 789')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Prüfstadt')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '98765')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'neüStation')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'neüZimmer')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'neüBett')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'ältStation')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, 'ältZimmer')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, 'ältBett')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '0100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'TÄT,HËINZ')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, '0148')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'TÄT,MÄJA ES')

# ################################################################################################################

    def test_navigate_PV1_10(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.10')
        self.assertEqual(result, 'SUR')

# ################################################################################################################

    def test_navigate_PV1_17(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.17')
        self.assertEqual(result, '0148')

# ################################################################################################################

    def test_navigate_PV1_17_2(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.17.2')
        self.assertEqual(result, 'TÄT,HËINZ')

# ################################################################################################################

    def test_navigate_PV1_18(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.18')
        self.assertEqual(result, 'S')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '2800')

# ################################################################################################################

    def test_navigate_PV1_20(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.20')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_39(self) -> 'None':
        message = parse_message(_Raw_de_imedone_20, validate=False)
        result = message.get('PV1.39')
        self.assertEqual(result, 'GËNKRH')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.date_time_of_message = '20260912142642'
        segment.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        segment.message_control_id = 'MSG00001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|||||20260912142642||ADT^A02^ADT_A02|MSG00001|P|2.6|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260912142642'

        serialized = segment.serialize()
        expected = 'EVN|A02|20260912142642||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '0'
        segment.patient_identifier_list = CX(cx_1='123456789', cx_4='PVS1')
        segment.patient_name = XPN(xpn_1='Prüffrau', xpn_2='Sïlke')
        segment.date_time_of_birth = '19670714'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Prüfstraße 789', xad_3='Prüfstadt', xad_5='98765')

        serialized = segment.serialize()
        expected = 'PID|0||123456789^^^PVS1||Prüffrau^Sïlke||19670714|F|||Prüfstraße 789^^Prüfstadt^^98765||09876/54321-0~^NET^X.400^heinz.prüfmann@prüfpost.com~0987/65432109^^CP'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='neüStation', pl_2='neüZimmer', pl_3='neüBett')
        segment.prior_patient_location = PL(pl_1='ältStation', pl_2='ältZimmer', pl_3='ältBett')
        segment.attending_doctor = XCN(xcn_1='0100', xcn_2='TÄT,HËINZ')
        segment.referring_doctor = XCN(xcn_1='0148', xcn_2='TÄT,MÄJA ES')
        segment.hospital_service = CWE(cwe_1='SUR')
        segment.admitting_doctor = XCN(xcn_1='0148', xcn_2='TÄT,HËINZ')
        segment.patient_type = CWE(cwe_1='S')
        segment.visit_number = CX(cx_1='2800')
        segment.financial_class = FC(fc_1='A')
        segment.servicing_facility = CWE(cwe_1='GËNKRH')

        serialized = segment.serialize()
        expected = 'PV1||I|neüStation^neüZimmer^neüBett|||ältStation^ältZimmer^ältBett|0100^TÄT,HËINZ|0148^TÄT,MÄJA ES||SUR|||||||0148^TÄT,HËINZ|S|2800|A|||||||||||||||||||GËNKRH||||||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A02()

        message.msh.date_time_of_message = '20260912142642'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        message.msh.message_control_id = 'MSG00001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260912142642'

        message.pid.set_id_pid = '0'
        message.pid.patient_identifier_list = CX(cx_1='123456789', cx_4='PVS1')
        message.pid.patient_name = XPN(xpn_1='Prüffrau', xpn_2='Sïlke')
        message.pid.date_time_of_birth = '19670714'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Prüfstraße 789', xad_3='Prüfstadt', xad_5='98765')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='neüStation', pl_2='neüZimmer', pl_3='neüBett')
        message.pv1.prior_patient_location = PL(pl_1='ältStation', pl_2='ältZimmer', pl_3='ältBett')
        message.pv1.attending_doctor = XCN(xcn_1='0100', xcn_2='TÄT,HËINZ')
        message.pv1.referring_doctor = XCN(xcn_1='0148', xcn_2='TÄT,MÄJA ES')
        message.pv1.hospital_service = CWE(cwe_1='SUR')
        message.pv1.admitting_doctor = XCN(xcn_1='0148', xcn_2='TÄT,HËINZ')
        message.pv1.patient_type = CWE(cwe_1='S')
        message.pv1.visit_number = CX(cx_1='2800')
        message.pv1.financial_class = FC(fc_1='A')
        message.pv1.servicing_facility = CWE(cwe_1='GËNKRH')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

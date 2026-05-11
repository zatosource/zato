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

_Raw_de_cgm_medico_01 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202603151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO\rEVN||202603151705||||202603151645\rPID|||5678901^^^Föhren-Klinik^PI||Krämer^Änne^^^^^L^A^^^G~Böhm^^^^^^M^A^^^G~Krämer^^^^Frau^^D^^^^G||19850713|F|||Römerstraße 28&Römerstraße&28^^München^^80331^^H~Bäckerweg 9&Bäckerweg&9^^München^^80331^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Sankt-Ägidius-Krankenhaus|||DEU^German^HL70171^^deutsch\rPV1|1|I|CHI^302^2^IN^^N^A^4|R|||710201^Schütz^Wölfgang^^^Dr.^^^Föhren-Klinik^L^^^DN^^^DN^^G||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202603151645\rPV2|||||||||20250405|4\rZBE|7891^KIS|202603151705||INSERT'

class Test_de_cgm_medico_01_1_ADT_A01_Aufnahme_admission_standard_profile(unittest.TestCase):
    """ 1. ADT^A01 - Aufnahme (admission), standard profile
    Source: wiki.hl7.de - HL7v2-Profile Aufnahme, Beispiel-Aufnahmenachrichten, Standardnachricht
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202603151705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/15')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.19.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.19.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.38')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202603151705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202603151645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '5678901')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Krämer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Änne')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Böhm')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[2]')
        self.assertEqual(result, 'Krämer')

# ################################################################################################################

    def test_navigate_PID_5_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[2].5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_5_2_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[2].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_2_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.5[2].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19850713')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1].5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.15.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_15_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.15.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verheiratet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.17.2')
        self.assertEqual(result, 'catholic')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_17_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.17.5')
        self.assertEqual(result, 'katholisch')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.26.2')
        self.assertEqual(result, 'German')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PID_26_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PID.26.5')
        self.assertEqual(result, 'deutsch')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '302')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710201')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Schütz')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Wölfgang')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.7.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202603151645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20250405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_01, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='5678901', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Krämer', xpn_2='Änne', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Böhm', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Krämer', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        segment.date_time_of_birth = '19850713'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_5='80331', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_5='80331', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        segment.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        serialized = segment.serialize()
        expected = 'PID|||5678901^^^Föhren-Klinik^PI||Krämer^Änne^^^^^L^A^^^G~Böhm^^^^^^M^A^^^G~Krämer^^^^Frau^^D^^^^G||19850713|F|||Römerstraße 28&Römerstraße&28^^München^^80331^^H~Bäckerweg 9&Bäckerweg&9^^München^^80331^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Sankt-Ägidius-Krankenhaus|||DEU^German^HL70171^^deutsch'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710201', xcn_2='Schütz', xcn_3='Wölfgang', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202603151645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^302^2^IN^^N^A^4|R|||710201^Schütz^Wölfgang^^^Dr.^^^Föhren-Klinik^L^^^DN^^^DN^^G||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202603151645'
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

        message.pid.patient_identifier_list = CX(cx_1='5678901', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Krämer', xpn_2='Änne', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Böhm', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='Krämer', xpn_5='Frau', xpn_8='D', xpn_13='G')]
        message.pid.date_time_of_birth = '19850713'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_5='80331', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_5='80331', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296', cwe_5='deutsch')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002', cwe_5='verheiratet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_2='catholic', cwe_3='HL70006', cwe_5='katholisch')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70171', cwe_5='deutsch')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='302', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710201', xcn_2='Schütz', xcn_3='Wölfgang', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN', xcn_20='G')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202603151645'

        message.pv2.expected_discharge_date_time = '20250405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_02 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||022604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|URO^301^1^IN^^N^A^4|R|||710203^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN|710211^Pförtner^Kläus^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N\rZBE|7891^KIS|202604011705||INSERT'

class Test_de_cgm_medico_02_2_ADT_A01_Aufnahme_admission_DRG_profile(unittest.TestCase):
    """ 2. ADT^A01 - Aufnahme (admission), DRG profile
    Source: wiki.hl7.de - HL7v2-Profile Aufnahme, Beispielnachricht für DRG
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.39')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '022604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'URO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '301')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710203')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, '710211')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Pförtner')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Kläus')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_8_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.15')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_8_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.8.18')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PV1_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.13')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.18')
        self.assertEqual(result, 'E')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.3')
        self.assertEqual(result, '0101')

# ################################################################################################################

    def test_navigate_PV2_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.3.2')
        self.assertEqual(result, 'vollstationär, Normalfall')

# ################################################################################################################

    def test_navigate_PV2_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.3.3')
        self.assertEqual(result, 'GSG0001')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_02, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710203', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        segment.referring_doctor = XCN(xcn_1='710211', xcn_2='Pförtner', xcn_3='Kläus', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        segment.re_admission_indicator = CWE(cwe_1='R')
        segment.patient_type = CWE(cwe_1='E')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|URO^301^1^IN^^N^A^4|R|||710203^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN|710211^Pförtner^Kläus^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='URO', pl_2='301', pl_3='1', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710203', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.referring_doctor = XCN(xcn_1='710211', xcn_2='Pförtner', xcn_3='Kläus', xcn_6='Dr.', xcn_11='L', xcn_14='DN', xcn_16='A', xcn_20='G')
        message.pv1.re_admission_indicator = CWE(cwe_1='R')
        message.pv1.patient_type = CWE(cwe_1='E')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
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

_Raw_de_cgm_medico_03 = 'MSH|^~\\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO\rSFT|RIS System GmbH^L|3.4|superRIS\rMSA|CA|ADT001'

class Test_de_cgm_medico_03_3_ACK_A01_transport_acknowledgment_for_admission(unittest.TestCase):
    """ 3. ACK^A01 - transport acknowledgment for admission
    Source: wiki.hl7.de - HL7v2-Profile Aufnahme, Transportquittung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.9')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'RIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '3.4')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'superRIS')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_03, validate=False)
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

_Raw_de_cgm_medico_04 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO\rEVN||202606051705||||022606051645\rPID|||67890^^^Lärchen-Krankenhaus^PI||Dörfler^Günther^^^Dr.^^L^A^^^G~Dörfler^Günther^^^Herr Dr.^^D^A^^^G||19720116|F|||Dürener Str. 33&Dürener Str.&33^^Würzburg^^97070^^H||^PRN^PH^^49^931^5671234^^^^^0931/5671234|^WPN^PH^^49^931^98765^^^^^0931/98765|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|HNO^201^2^IN^^N^A^4|R|||710203^Köhler^Hëinrich^^^Dr.^^^Lärchen-Krankenhaus^L^^^^^^DN ||||||||||||831642^^^Lärchen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645\rPV2|||||||||20260615|10\rZBE|83217^KIS|202606051705||INSERT'

class Test_de_cgm_medico_04_4_ADT_A01_Aufnahme_admission_billing_profile(unittest.TestCase):
    """ 4. ADT^A01 - Aufnahme (admission), billing profile
    Source: wiki.hl7.de - HL7v2-Profile Aufnahme, Beispielnachricht für die Abrechnung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.40')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202606051705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '022606051645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Lärchen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Dörfler')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PID_5_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0].5')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Dörfler')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PID_5_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1].5')
        self.assertEqual(result, 'Herr Dr.')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19720116')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Dürener Str. 33')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Dürener Str.')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11.1.3')
        self.assertEqual(result, '33')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Würzburg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '97070')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '201')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710203')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Lärchen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN ')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '831642')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Lärchen-Krankenhaus')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_20(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.20')
        self.assertEqual(result, '01100000')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_25(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.25')
        self.assertEqual(result, '202401')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202606051645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260615')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_04, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Lärchen-Krankenhaus', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Dörfler', xpn_2='Günther', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Dörfler', xpn_2='Günther', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19720116'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Dürener Str. 33&Dürener Str.&33', xad_3='Würzburg', xad_5='97070', xad_7='H')
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Lärchen-Krankenhaus^PI||Dörfler^Günther^^^Dr.^^L^A^^^G~Dörfler^Günther^^^Herr Dr.^^D^A^^^G||19720116|F|||Dürener Str. 33&Dürener Str.&33^^Würzburg^^97070^^H||^PRN^PH^^49^931^5671234^^^^^0931/5671234|^WPN^PH^^49^931^98765^^^^^0931/98765|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710203', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Lärchen-Krankenhaus', xcn_11='L', xcn_18='DN ')
        segment.visit_number = CX(cx_1='831642', cx_4='Lärchen-Krankenhaus', cx_5='VN')
        segment.financial_class = FC(fc_1='01100000')
        segment.contract_code = CWE(cwe_1='C')
        segment.contract_effective_date = '202401'
        segment.admit_date_time = '202606051645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^201^2^IN^^N^A^4|R|||710203^Köhler^Hëinrich^^^Dr.^^^Lärchen-Krankenhaus^L^^^^^^DN ||||||||||||831642^^^Lärchen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Lärchen-Krankenhaus', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Dörfler', xpn_2='Günther', xpn_5='Dr.', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Dörfler', xpn_2='Günther', xpn_5='Herr Dr.', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19720116'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Dürener Str. 33&Dürener Str.&33', xad_3='Würzburg', xad_5='97070', xad_7='H')
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='201', pl_3='2', pl_4='IN', pl_6='N', pl_7='A', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710203', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Lärchen-Krankenhaus', xcn_11='L', xcn_18='DN ')
        message.pv1.visit_number = CX(cx_1='831642', cx_4='Lärchen-Krankenhaus', cx_5='VN')
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

_Raw_de_cgm_medico_05 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.20^^2.16.840.1.113883.2.6^ISO\rEVN||202604011705||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^B^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius- Krankenhaus|||DEU^^HL70171\rPV1|1|I|CHI^202^1^CH^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|7891^KIS|202604011705||REFERENCE'

class Test_de_cgm_medico_05_5_ADT_A08_nderung_Patientendaten_update_patient_standard_profile(unittest.TestCase):
    """ 5. ADT^A08 - Änderung Patientendaten (update patient), standard profile
    Source: wiki.hl7.de - HL7v2-Profile Aenderung Patient, Beispiel Standardnachricht
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aenderung_Patient
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.20')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius- Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710207')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_05, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='RIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011705'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.20', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.20^^2.16.840.1.113883.2.6^ISO'
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='B', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius- Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^B^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius- Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='202', pl_3='1', pl_4='CH', pl_6='N', pl_7='C', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^202^1^CH^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.20', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '202604011645'

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='B', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius- Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='202', pl_3='1', pl_4='CH', pl_6='N', pl_7='C', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_06 = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202504011706||ACK^A08^ACK|RIS002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.5^^2.16.840.1.113883.2.6^ISO|\rSFT|KIS System GmbH^L|5.0|A1|\rMSA|CA|ADT001|'

class Test_de_cgm_medico_06_6_ACK_A08_transport_acknowledgment_for_update(unittest.TestCase):
    """ 6. ACK^A08 - transport acknowledgment for update
    Source: wiki.hl7.de - HL7v2-Profile Aenderung Patient, Transportquittung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aenderung_Patient
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.5')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_06, validate=False)
        result = message.get('MSA.2')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='RIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202504011706'
        segment.message_type = MSG(msg_1='ACK', msg_2='A08', msg_3='ACK')
        segment.message_control_id = 'RIS002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.5', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202504011706||ACK^A08^ACK|RIS002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.5^^2.16.840.1.113883.2.6^ISO|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MSA(self) -> 'None':
        segment = MSA()

        segment.acknowledgment_code = 'CA'
        segment.message_control_id = 'ADT001'

        serialized = segment.serialize()
        expected = 'MSA|CA|ADT001|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ACK()

        message.msh.sending_application = HD(hd_1='RIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202504011706'
        message.msh.message_type = MSG(msg_1='ACK', msg_2='A08', msg_3='ACK')
        message.msh.message_control_id = 'RIS002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.5', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.msa.acknowledgment_code = 'CA'
        message.msa.message_control_id = 'ADT001'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_07 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.21^^2.16.840.1.113883.2.6^ISO\rEVN||202604011705||||202504011645\rPID|||67890^^^Föhren-Klinik^PI||aus dem Brück&aus dem&Brück^Rüdiger^^^^^L^A^^^G~aus dem Brück&aus dem&Brück^Rüdger^^^^^M^A^^^G~aus dem Brück&aus dem&Brück^Rüdiger^^^Herr^^D^A^^^G||19840908|M|||Höhenweg 7&Höhenweg&7^^Nürnberg^XA-DE-BY^90402^DEU^H~Grünauer Str. 18&Grünauer Str.&18^^Fürth^^90762^DEU^BDL||^PRN^PH^^49^911^2345678^^^^^0911/2345678|^WPN^PH^^49^911^7654^321^^^^0911/7654-321|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN|710213^^^^^^^^Föhren-Klinik^^^^DN|||||R||||||9281537^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4|||||||||||||||||||||||||||N\rZBE|7891^KIS|202604011705||REFERENCE'

class Test_de_cgm_medico_07_7_ADT_A08_nderung_Patientendaten_update_patient_DRG_profile(unittest.TestCase):
    """ 7. ADT^A08 - Änderung Patientendaten (update patient), DRG profile
    Source: wiki.hl7.de - HL7v2-Profile Aenderung Patient, Beispielnachricht für DRG
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aenderung_Patient
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.21')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Rüdiger')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Rüdger')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_2_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_2_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_2_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].2')
        self.assertEqual(result, 'Rüdiger')

# ################################################################################################################

    def test_navigate_PID_5_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].5')
        self.assertEqual(result, 'Herr')

# ################################################################################################################

    def test_navigate_PID_5_2_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_2_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_2_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.5[2].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Höhenweg 7')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Höhenweg')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '7')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_0_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].4')
        self.assertEqual(result, 'XA-DE-BY')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PID_11_0_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Grünauer Str. 18')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Grünauer Str.')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '18')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'Fürth')

# ################################################################################################################

    def test_navigate_PID_11_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].5')
        self.assertEqual(result, '90762')

# ################################################################################################################

    def test_navigate_PID_11_1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].6')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN2')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710207')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, '710213')

# ################################################################################################################

    def test_navigate_PV1_8_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.8.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_8_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.8.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.13')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '9281537')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_07, validate=False)
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
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.21', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.21^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.event_occurred = '202504011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||202504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdger', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Höhenweg 7&Höhenweg&7', xad_3='Nürnberg', xad_4='XA-DE-BY', xad_5='90402', xad_6='DEU', xad_7='H'), XAD(xad_1='Grünauer Str. 18&Grünauer Str.&18', xad_3='Fürth', xad_5='90762', xad_6='DEU', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||aus dem Brück&aus dem&Brück^Rüdiger^^^^^L^A^^^G~aus dem Brück&aus dem&Brück^Rüdger^^^^^M^A^^^G~aus dem Brück&aus dem&Brück^Rüdiger^^^Herr^^D^A^^^G||19840908|M|||Höhenweg 7&Höhenweg&7^^Nürnberg^XA-DE-BY^90402^DEU^H~Grünauer Str. 18&Grünauer Str.&18^^Fürth^^90762^DEU^BDL||^PRN^PH^^49^911^2345678^^^^^0911/2345678|^WPN^PH^^49^911^7654^321^^^^0911/7654-321|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN2', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='C', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        segment.referring_doctor = XCN(xcn_1='710213', xcn_10='Föhren-Klinik', xcn_14='DN')
        segment.re_admission_indicator = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='9281537', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN|710213^^^^^^^^Föhren-Klinik^^^^DN|||||R||||||9281537^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260405'
        segment.estimated_length_of_inpatient_stay = '4'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260405|4|||||||||||||||||||||||||||N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.21', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '202504011645'

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdger', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Höhenweg 7&Höhenweg&7', xad_3='Nürnberg', xad_4='XA-DE-BY', xad_5='90402', xad_6='DEU', xad_7='H'), XAD(xad_1='Grünauer Str. 18&Grünauer Str.&18', xad_3='Fürth', xad_5='90762', xad_6='DEU', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN2', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='C', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.referring_doctor = XCN(xcn_1='710213', xcn_10='Föhren-Klinik', xcn_14='DN')
        message.pv1.re_admission_indicator = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='9281537', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_08 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.22^^2.16.840.1.113883.2.6^ISO\rEVN||202604011705||||202504011645\rPID|||67890^^^Föhren-Klinik^PI||aus dem Brück&aus dem&Brück^Rüdiger^^^^^L^A^^^G~aus dem Brück&aus dem&Brück^Rüdger^^^^^M^A^^^G~aus dem Brück&aus dem&Brück^Rüdiger^^^Herr^^D^A^^^G||19840908|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|01100001||||C|20260101|||||||||||||||||||202604011645\rPV2|||||||||20260405|4|||||||||||||||||||||||||||N\rZBE|7891^KIS|202604011705||REFERENCE'

class Test_de_cgm_medico_08_8_ADT_A08_nderung_Patientendaten_update_patient_billing_profile(unittest.TestCase):
    """ 8. ADT^A08 - Änderung Patientendaten (update patient), billing profile
    Source: wiki.hl7.de - HL7v2-Profile Aenderung Patient, Beispielnachricht für Abrechnung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aenderung_Patient
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.22')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Rüdiger')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].2')
        self.assertEqual(result, 'Rüdger')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2]')
        self.assertEqual(result, 'aus dem Brück')

# ################################################################################################################

    def test_navigate_PID_5_2_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].1.2')
        self.assertEqual(result, 'aus dem')

# ################################################################################################################

    def test_navigate_PID_5_2_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].1.3')
        self.assertEqual(result, 'Brück')

# ################################################################################################################

    def test_navigate_PID_5_2_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].2')
        self.assertEqual(result, 'Rüdiger')

# ################################################################################################################

    def test_navigate_PID_5_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].5')
        self.assertEqual(result, 'Herr')

# ################################################################################################################

    def test_navigate_PID_5_2_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PID_5_2_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_2_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.5[2].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN2')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710207')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_20(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.20')
        self.assertEqual(result, '01100001')

# ################################################################################################################

    def test_navigate_PV1_24(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.24')
        self.assertEqual(result, 'C')

# ################################################################################################################

    def test_navigate_PV1_25(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.25')
        self.assertEqual(result, '20260101')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_08, validate=False)
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
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = 'ADT001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.22', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.22^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011705'
        segment.event_occurred = '202504011645'

        serialized = segment.serialize()
        expected = 'EVN||202604011705||||202504011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdger', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||aus dem Brück&aus dem&Brück^Rüdiger^^^^^L^A^^^G~aus dem Brück&aus dem&Brück^Rüdger^^^^^M^A^^^G~aus dem Brück&aus dem&Brück^Rüdiger^^^Herr^^D^A^^^G||19840908|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN2', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='C', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.financial_class = FC(fc_1='01100001')
        segment.contract_code = CWE(cwe_1='C')
        segment.contract_effective_date = '20260101'
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|01100001||||C|20260101|||||||||||||||||||202604011645'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV2(self) -> 'None':
        segment = PV2()

        segment.expected_discharge_date_time = '20260405'
        segment.estimated_length_of_inpatient_stay = '4'
        segment.baby_detained_indicator = 'N'

        serialized = segment.serialize()
        expected = 'PV2|||||||||20260405|4|||||||||||||||||||||||||||N'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='RIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011705'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = 'ADT001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.22', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.evn.recorded_date_time = '202604011705'
        message.evn.event_occurred = '202504011645'

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdger', xpn_8='M', xpn_9='A', xpn_13='G'), XPN(xpn_1='aus dem Brück&aus dem&Brück', xpn_2='Rüdiger', xpn_5='Herr', xpn_8='D', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN2', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='C', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710207', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.financial_class = FC(fc_1='01100001')
        message.pv1.contract_code = CWE(cwe_1='C')
        message.pv1.contract_effective_date = '20260101'
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'
        message.pv2.baby_detained_indicator = 'N'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_09 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202504011705||||202504011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||710209^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN^^^DN ||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rZBE|7891^KIS|202504011705||REFERENCE'

class Test_de_cgm_medico_09_9_ADT_A03_Entlassung_discharge_standard_profile(unittest.TestCase):
    """ 9. ADT^A03 - Entlassung (discharge), standard profile
    Source: wiki.hl7.de - HL7v2-Profile Entlassung, Standardnachricht
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.47')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710209')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_7_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.7.16')
        self.assertEqual(result, 'DN ')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_09, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.attending_doctor = XCN(xcn_1='710209', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN ')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||710209^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN^^^DN ||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.attending_doctor = XCN(xcn_1='710209', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN', xcn_18='DN ')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.discharge_disposition = CWE(cwe_1='011')
        message.pv1.admit_date_time = '202504011645'
        message.pv1.discharge_date_time = '202504061100'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_10 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO\rEVN||202504011705||||202504011645\rPID|||67890^^^Föhren-Klinik^PI||von der Lühe&von der&Lühe^Jörg^^^^^L^A^^^G||19740205|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg  9&Bäckerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rPV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N\rZBE|7891^KIS|202504011705||REFERENCE'

class Test_de_cgm_medico_10_10_ADT_A03_Entlassung_discharge_DRG_profile(unittest.TestCase):
    """ 10. ADT^A03 - Entlassung (discharge), DRG profile
    Source: wiki.hl7.de - HL7v2-Profile Entlassung, Nachricht für DRG
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.48')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'von der Lühe')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.1.2')
        self.assertEqual(result, 'von der')

# ################################################################################################################

    def test_navigate_PID_5_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.1.3')
        self.assertEqual(result, 'Lühe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Jörg')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19740205')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg  9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'W')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'widowed')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verwitwet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '202504061100')

# ################################################################################################################

    def test_navigate_PV2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.3')
        self.assertEqual(result, '0102')

# ################################################################################################################

    def test_navigate_PV2_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.3.2')
        self.assertEqual(result, 'vollstationär, Arbeitsunfall')

# ################################################################################################################

    def test_navigate_PV2_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.3.3')
        self.assertEqual(result, 'GSG0001')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.11')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_10, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='von der Lühe&von der&Lühe', xpn_2='Jörg', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19740205'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg  9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||von der Lühe&von der&Lühe^Jörg^^^^^L^A^^^G||19740205|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg  9&Bäckerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='von der Lühe&von der&Lühe', xpn_2='Jörg', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19740205'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg  9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
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

_Raw_de_cgm_medico_11 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO\rEVN||202504011705||||202504011645\rPID|||67890^^^Föhren-Klinik^PI||von der Lühe&von der&Lühe^Jörg^^^^^L^A^^^G||19740205|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100\rPV2||||||||||||||||||||||||||||||||||||N|N\rZBE|7891^KIS|202504011705||REFERENCE'

class Test_de_cgm_medico_11_11_ADT_A03_Entlassung_discharge_billing_profile(unittest.TestCase):
    """ 11. ADT^A03 - Entlassung (discharge), billing profile
    Source: wiki.hl7.de - HL7v2-Profile Entlassung, Nachricht für Abrechnung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.49')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202504011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'von der Lühe')

# ################################################################################################################

    def test_navigate_PID_5_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.1.2')
        self.assertEqual(result, 'von der')

# ################################################################################################################

    def test_navigate_PID_5_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.1.3')
        self.assertEqual(result, 'Lühe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Jörg')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19740205')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'W')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'widowed')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_16_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.16.5')
        self.assertEqual(result, 'verwitwet')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'HNO')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '311')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'B')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.36')
        self.assertEqual(result, '011')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202504011645')

# ################################################################################################################

    def test_navigate_PV1_45(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV1.45')
        self.assertEqual(result, '202504061100')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_11, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='von der Lühe&von der&Lühe', xpn_2='Jörg', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19740205'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||von der Lühe&von der&Lühe^Jörg^^^^^L^A^^^G||19740205|M|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.discharge_disposition = CWE(cwe_1='011')
        segment.admit_date_time = '202504011645'
        segment.discharge_date_time = '202504061100'

        serialized = segment.serialize()
        expected = 'PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='von der Lühe&von der&Lühe', xpn_2='Jörg', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19740205'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='W', cwe_2='widowed', cwe_3='HL70002', cwe_5='verwitwet')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='HNO', pl_2='311', pl_3='3', pl_4='IN', pl_6='N', pl_7='B', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
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

_Raw_de_cgm_medico_12 = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|\rSFT|KIS System GmbH^L|5.0|A1|\rMSA|CA|ADT001|'

class Test_de_cgm_medico_12_12_ACK_A03_transport_acknowledgment_for_discharge(unittest.TestCase):
    """ 12. ACK^A03 - transport acknowledgment for discharge
    Source: wiki.hl7.de - HL7v2-Profile Entlassung, Transportquittung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202504011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.15')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_12, validate=False)
        result = message.get('MSA.2')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='RIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202504011706'
        segment.message_type = MSG(msg_1='ACK', msg_2='A03', msg_3='ACK')
        segment.message_control_id = 'RIS002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.15', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_SFT(self) -> 'None':
        segment = SFT()

        segment.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        segment.software_certified_version_or_release_number = '5.0'
        segment.software_product_name = 'A1'

        serialized = segment.serialize()
        expected = 'SFT|KIS System GmbH^L|5.0|A1|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MSA(self) -> 'None':
        segment = MSA()

        segment.acknowledgment_code = 'CA'
        segment.message_control_id = 'ADT001'

        serialized = segment.serialize()
        expected = 'MSA|CA|ADT001|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ACK()

        message.msh.sending_application = HD(hd_1='RIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202504011706'
        message.msh.message_type = MSG(msg_1='ACK', msg_2='A03', msg_3='ACK')
        message.msh.message_control_id = 'RIS002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.15', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.sft.software_vendor_organization = XON(xon_1='KIS System GmbH', xon_2='L')
        message.sft.software_certified_version_or_release_number = '5.0'
        message.sft.software_product_name = 'A1'

        message.msa.acknowledgment_code = 'CA'
        message.msa.message_control_id = 'ADT001'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_13 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011935||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|710213^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|3456^KIS|202604011935||INSERT'

class Test_de_cgm_medico_13_13_ADT_A02_Verlegung_transfer_standard_profile(unittest.TestCase):
    """ 13. ADT^A02 - Verlegung (transfer), standard profile
    Source: wiki.hl7.de - HL7v2-Profile Verlegung, Standardnachricht
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.44')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '710213')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Köhler')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Hëinrich')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_7_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.7.13')
        self.assertEqual(result, 'DN')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_13, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.attending_doctor = XCN(xcn_1='710213', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|710213^Köhler^Hëinrich^^^Dr.^^^Föhren-Klinik^L^^^DN||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.attending_doctor = XCN(xcn_1='710213', xcn_2='Köhler', xcn_3='Hëinrich', xcn_6='Dr.', xcn_10='Föhren-Klinik', xcn_11='L', xcn_14='DN')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_14 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011935||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260406|5||||||||||||||||||||||||||N|N\rZBE|3456^KIS|202604011935||INSERT'

class Test_de_cgm_medico_14_14_ADT_A02_Verlegung_transfer_DRG_profile(unittest.TestCase):
    """ 14. ADT^A02 - Verlegung (transfer), DRG profile
    Source: wiki.hl7.de - HL7v2-Profile Verlegung, Beispielnachricht für DRG
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.45')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260406')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV2.10')
        self.assertEqual(result, '5')

# ################################################################################################################

    def test_navigate_PV2_36(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
        result = message.get('PV2.36')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV2_37(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_14, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
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

_Raw_de_cgm_medico_15 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO\rEVN||202604011935||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2|||||||||20260405|4\rZBE|3456^KIS|202604011935||DELETE'

class Test_de_cgm_medico_15_15_ADT_A12_Stornierung_Verlegung_cancel_transfer(unittest.TestCase):
    """ 15. ADT^A12 - Stornierung Verlegung (cancel transfer)
    Source: wiki.hl7.de - HL7v2-Profile Verlegung Storno, Stornierung der letzten Verlegung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung_Storno
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        self.assertIsInstance(message, ADT_A12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.46')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_15, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_16 = 'MSH|^~\\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO\rEVN||202604011935||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645|||||||H\rPV2|||||||||20260405|4\rZBE|3456^KIS|202603301345||DELETE'

class Test_de_cgm_medico_16_16_ADT_A12_Stornierung_fr_herer_Verlegung_cancel_earlier_transfer(unittest.TestCase):
    """ 16. ADT^A12 - Stornierung früherer Verlegung (cancel earlier transfer)
    Source: wiki.hl7.de - HL7v2-Profile Verlegung Storno, Stornierung einer früheren Verlegung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung_Storno
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        self.assertIsInstance(message, ADT_A12)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A12')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A12')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A12')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.46')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011935')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.5.8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.5.11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'CHI')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '303')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '4')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_6_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.2')
        self.assertEqual(result, '202')

# ################################################################################################################

    def test_navigate_PV1_6_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_6_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.4')
        self.assertEqual(result, 'IN')

# ################################################################################################################

    def test_navigate_PV1_6_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_6_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.7')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_6_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.6.8')
        self.assertEqual(result, '2')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV1_51(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV1.51')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PV2_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
        result = message.get('PV2.9')
        self.assertEqual(result, '20260405')

# ################################################################################################################

    def test_navigate_PV2_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_16, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G')
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        segment.admission_type = CWE(cwe_1='R')
        segment.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'
        segment.visit_indicator = CWE(cwe_1='H')

        serialized = segment.serialize()
        expected = 'PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645|||||||H'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G')
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='303', pl_3='3', pl_4='CH', pl_6='N', pl_7='D', pl_8='4')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.prior_patient_location = PL(pl_1='IN1', pl_2='202', pl_3='1', pl_4='IN', pl_6='N', pl_7='D', pl_8='2')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'
        message.pv1.visit_indicator = CWE(cwe_1='H')

        message.pv2.expected_discharge_date_time = '20260405'
        message.pv2.estimated_length_of_inpatient_stay = '4'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_17 = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO\rSFT|KIS System GmbH^L|5.0|A1\rEVN||202604011705||||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rZBE|7891^KIS|202604011705||INSERT'

class Test_de_cgm_medico_17_17_ADT_A04_Besuchsmeldung_Registrierung_outpatient_registration(unittest.TestCase):
    """ 17. ADT^A04 - Besuchsmeldung/Registrierung (outpatient registration)
    Source: wiki.hl7.de - HL7v2-Profile Besuchsmeldung, Beispielnachricht 1
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.51')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_SFT_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('SFT.1')
        self.assertEqual(result, 'KIS System GmbH')

# ################################################################################################################

    def test_navigate_SFT_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('SFT.1.2')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_SFT_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('SFT.2')
        self.assertEqual(result, '5.0')

# ################################################################################################################

    def test_navigate_SFT_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('SFT.3')
        self.assertEqual(result, 'A1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'O')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'AIN')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'D')

# ################################################################################################################

    def test_navigate_PV1_3_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.3.7')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.4')
        self.assertEqual(result, 'R')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_17, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='O')
        segment.assigned_patient_location = PL(pl_4='AIN', pl_6='D', pl_7='A', pl_8='1')
        segment.admission_type = CWE(cwe_1='R')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='O')
        message.pv1.assigned_patient_location = PL(pl_4='AIN', pl_6='D', pl_7='A', pl_8='1')
        message.pv1.admission_type = CWE(cwe_1='R')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_18 = 'MSH|^~\\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO\rEVN||202604011705|20260601|||202604011645\rPID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171\rPV1|1|I|IN1^^^CH^^N||||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645\rPV2||||||||20260601\rZBE|7891^KIS|202604011705||INSERT'

class Test_de_cgm_medico_18_18_ADT_A04_Besuchsmeldung_Registrierung_pre_admission_with_planned_date(unittest.TestCase):
    """ 18. ADT^A04 - Besuchsmeldung/Registrierung (pre-admission with planned date)
    Source: wiki.hl7.de - HL7v2-Profile Besuchsmeldung, Beispielnachricht 2
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.51')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011705')

# ################################################################################################################

    def test_navigate_EVN_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('EVN.3')
        self.assertEqual(result, '20260601')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '67890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[0]')
        self.assertEqual(result, 'Stürmer')

# ################################################################################################################

    def test_navigate_PID_5_0_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[0].2')
        self.assertEqual(result, 'Bärbel')

# ################################################################################################################

    def test_navigate_PID_5_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[0].7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_5_0_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[0].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_0_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[0].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_5_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[1]')
        self.assertEqual(result, 'Rößler')

# ################################################################################################################

    def test_navigate_PID_5_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[1].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[1].8')
        self.assertEqual(result, 'A')

# ################################################################################################################

    def test_navigate_PID_5_1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.5[1].11')
        self.assertEqual(result, 'G')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19840908')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Römerstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_0_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[0].1.2')
        self.assertEqual(result, 'Römerstraße')

# ################################################################################################################

    def test_navigate_PID_11_0_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[0].1.3')
        self.assertEqual(result, '28')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'H')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, 'Bäckerweg 9')

# ################################################################################################################

    def test_navigate_PID_11_1_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[1].1.2')
        self.assertEqual(result, 'Bäckerweg')

# ################################################################################################################

    def test_navigate_PID_11_1_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[1].1.3')
        self.assertEqual(result, '9')

# ################################################################################################################

    def test_navigate_PID_11_1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[1].3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_PID_11_1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.11[1].7')
        self.assertEqual(result, 'BDL')

# ################################################################################################################

    def test_navigate_PID_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.15')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_15_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.15.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_PID_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.16')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_16_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.16.2')
        self.assertEqual(result, 'married')

# ################################################################################################################

    def test_navigate_PID_16_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.16.3')
        self.assertEqual(result, 'HL70002')

# ################################################################################################################

    def test_navigate_PID_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.17')
        self.assertEqual(result, 'CAT')

# ################################################################################################################

    def test_navigate_PID_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.17.3')
        self.assertEqual(result, 'HL70006')

# ################################################################################################################

    def test_navigate_PID_23(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.23')
        self.assertEqual(result, 'Sankt-Ägidius-Krankenhaus')

# ################################################################################################################

    def test_navigate_PID_26(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.26')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_PID_26_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PID.26.3')
        self.assertEqual(result, 'HL70171')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'IN1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_3_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.3.6')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, '4711')

# ################################################################################################################

    def test_navigate_PV1_19_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.19.4')
        self.assertEqual(result, 'Föhren-Klinik')

# ################################################################################################################

    def test_navigate_PV1_19_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.19.5')
        self.assertEqual(result, 'VN')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '202604011645')

# ################################################################################################################

    def test_navigate_PV2_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_18, validate=False)
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

        segment.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        segment.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        segment.date_time_of_birth = '19840908'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        segment.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        segment.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        segment.birth_place = 'Sankt-Ägidius-Krankenhaus'
        segment.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        serialized = segment.serialize()
        expected = 'PID|||67890^^^Föhren-Klinik^PI||Stürmer^Bärbel^^^^^L^A^^^G~Rößler^^^^^^M^A^^^G||19840908|F|||Römerstraße 28&Römerstraße&28^^München^^^^H~Bäckerweg 9&Bäckerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sankt-Ägidius-Krankenhaus|||DEU^^HL70171'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='IN1', pl_4='CH', pl_6='N')
        segment.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        segment.admit_date_time = '202604011645'

        serialized = segment.serialize()
        expected = 'PV1|1|I|IN1^^^CH^^N||||||||||||||||4711^^^Föhren-Klinik^VN|||||||||||||||||||||||||202604011645'
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

        message.pid.patient_identifier_list = CX(cx_1='67890', cx_4='Föhren-Klinik', cx_5='PI')
        message.pid.patient_name = [XPN(xpn_1='Stürmer', xpn_2='Bärbel', xpn_8='L', xpn_9='A', xpn_13='G'), XPN(xpn_1='Rößler', xpn_8='M', xpn_9='A', xpn_13='G')]
        message.pid.date_time_of_birth = '19840908'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = [XAD(xad_1='Römerstraße 28&Römerstraße&28', xad_3='München', xad_7='H'), XAD(xad_1='Bäckerweg 9&Bäckerweg&9', xad_3='München', xad_7='BDL')]
        message.pid.primary_language = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        message.pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        message.pid.birth_place = 'Sankt-Ägidius-Krankenhaus'
        message.pid.citizenship = CWE(cwe_1='DEU', cwe_3='HL70171')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='IN1', pl_4='CH', pl_6='N')
        message.pv1.visit_number = CX(cx_1='4711', cx_4='Föhren-Klinik', cx_5='VN')
        message.pv1.admit_date_time = '202604011645'

        message.pv2.expected_admit_date_time = '20260601'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_19 = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202604011706||ACK^A04^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO|\rMSA|CA|ADT001|'

class Test_de_cgm_medico_19_19_ACK_A04_transport_acknowledgment_for_registration(unittest.TestCase):
    """ 19. ACK^A04 - transport acknowledgment for registration
    Source: wiki.hl7.de - HL7v2-Profile Besuchsmeldung, Transportquittung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RIS')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KIS')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '202604011706')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RIS002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.51')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_19, validate=False)
        result = message.get('MSA.2')
        self.assertEqual(result, 'ADT001')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='RIS')
        segment.sending_facility = HD(hd_1='ADT')
        segment.receiving_application = HD(hd_1='KIS')
        segment.receiving_facility = HD(hd_1='ADT')
        segment.date_time_of_message = '202604011706'
        segment.message_type = MSG(msg_1='ACK', msg_2='A04', msg_3='ACK')
        segment.message_control_id = 'RIS002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|RIS|ADT|KIS|ADT|202604011706||ACK^A04^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MSA(self) -> 'None':
        segment = MSA()

        segment.acknowledgment_code = 'CA'
        segment.message_control_id = 'ADT001'

        serialized = segment.serialize()
        expected = 'MSA|CA|ADT001|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ACK()

        message.msh.sending_application = HD(hd_1='RIS')
        message.msh.sending_facility = HD(hd_1='ADT')
        message.msh.receiving_application = HD(hd_1='KIS')
        message.msh.receiving_facility = HD(hd_1='ADT')
        message.msh.date_time_of_message = '202604011706'
        message.msh.message_type = MSG(msg_1='ACK', msg_2='A04', msg_3='ACK')
        message.msh.message_control_id = 'RIS002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.51', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.msa.acknowledgment_code = 'CA'
        message.msa.message_control_id = 'ADT001'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_medico_20 = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\rEVN|A08|202604061019\rPID|1||4477^^^&www.praxis-süd.de&DNS^PI~287433^^^Röntgen^PI|20000053^^^KÖL^PI|Größe^Fränze||19500327|F|||Blücherstr. 41&Blücherstr. 41^^Göttingen^^37073^DE^L||^^PH^^^^0551-9876543 Büro|^^PH'

class Test_de_cgm_medico_20_20_ADT_A08_incoming_from_KIS_via_KomServer_integration(unittest.TestCase):
    """ 20. ADT^A08 - incoming from KIS via KomServer integration
    Source: samedi HL7gateway documentation - Eingehende ADT-Nachricht
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KomServer')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'KOMSERV')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'samedi-hl7gateway')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'samedi')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260410123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638150947283')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E72B53F8AC791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604061019')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '4477')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '287433')

# ################################################################################################################

    def test_navigate_PID_3_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[1].4')
        self.assertEqual(result, 'Röntgen')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Größe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Fränze')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19500327')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Blücherstr. 41')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Blücherstr. 41')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Göttingen')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '37073')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_medico_20, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KomServer')
        segment.sending_facility = HD(hd_1='KOMSERV')
        segment.receiving_application = HD(hd_1='samedi-hl7gateway')
        segment.receiving_facility = HD(hd_1='samedi')
        segment.date_time_of_message = '20260410123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08')
        segment.message_control_id = '2638150947283'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E72B53F8AC791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604061019'

        serialized = segment.serialize()
        expected = 'EVN|A08|202604061019'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='4477', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='287433', cx_4='Röntgen', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Größe', xpn_2='Fränze')
        segment.date_time_of_birth = '19500327'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Blücherstr. 41&Blücherstr. 41', xad_3='Göttingen', xad_5='37073', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||4477^^^&www.praxis-süd.de&DNS^PI~287433^^^Röntgen^PI|20000053^^^KÖL^PI|Größe^Fränze||19500327|F|||Blücherstr. 41&Blücherstr. 41^^Göttingen^^37073^DE^L||^^PH^^^^0551-9876543 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KomServer')
        message.msh.sending_facility = HD(hd_1='KOMSERV')
        message.msh.receiving_application = HD(hd_1='samedi-hl7gateway')
        message.msh.receiving_facility = HD(hd_1='samedi')
        message.msh.date_time_of_message = '20260410123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        message.msh.message_control_id = '2638150947283'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E72B53F8AC791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202604061019'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='4477', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='287433', cx_4='Röntgen', cx_5='PI')]
        message.pid.patient_name = XPN(xpn_1='Größe', xpn_2='Fränze')
        message.pid.date_time_of_birth = '19500327'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Blücherstr. 41&Blücherstr. 41', xad_3='Göttingen', xad_5='37073', xad_6='DE', xad_7='L')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

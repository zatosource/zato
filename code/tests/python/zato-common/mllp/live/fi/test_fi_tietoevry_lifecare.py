# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import parse_hl7
from zato.hl7v2.testing.live_util import load_message, md_path_for
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-tietoevry-lifecare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'LC000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300001', cx_4='TYKS', cx_5='MR'), CX(cx_1='120870-456A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 22', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0221234567~^^CP^0401234571'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='KIR1', pl_3='Huone 305', pl_4='Vuode 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR300^Virtanen^Maarit^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Sappikivitauti')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KELA')
        in1.insurance_company_id = CX(cx_1='300001')
        in1.insurance_company_name = XON(xon_1='KELA - Kansaneläkelaitos')
        in1.insurance_company_address = XAD(xad_1='Nordenskiöldinkatu 12', xad_3='Helsinki', xad_5='00250', xad_6='FIN')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 1)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 1)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg02(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260510091000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'LC000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260510091000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300001', cx_4='TYKS', cx_5='MR'), CX(cx_1='120870-456A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 22', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0221234567~^^CP^0401234571'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='SIS1', pl_3='Huone 412', pl_4='Vuode 2', pl_5='VSSHP')
        pv1.pv1_7 = 'DR300^Virtanen^Maarit^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 2)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 2)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg03(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260514140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'LC000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260514140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300001', cx_4='TYKS', cx_5='MR'), CX(cx_1='120870-456A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 22', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0221234567~^^CP^0401234571'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='SIS1', pl_3='Huone 412', pl_4='Vuode 2', pl_5='VSSHP')
        pv1.pv1_7 = 'DR300^Virtanen^Maarit^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300001')
        pv1.pending_location = PL(pl_1='20260509080000')
        pv1.prior_temporary_location = PL(pl_1='20260514140000')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 3)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 3)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg04(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'LC000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300002', cx_4='TYKS', cx_5='MR'), CX(cx_1='050385-789B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Maija', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19850305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Eerikinkatu 14', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876546'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI1', pl_3='Vastaanottohuone 4', pl_5='VSSHP')
        pv1.pv1_7 = 'DR301^Ahonen^Ilkka^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300001')
        pv1.pending_location = PL(pl_1='20260509093000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='IF')
        in1.insurance_company_id = CX(cx_1='300002')
        in1.insurance_company_name = XON(xon_1='If Vahinkovakuutus')
        in1.insurance_company_address = XAD(xad_1='Niittyportti 4', xad_3='Espoo', xad_5='02200', xad_6='FIN')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 4)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 4)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg05(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'LC000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300003', cx_4='TYKS', cx_5='MR'), CX(cx_1='280960-234C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkinen', xpn_2='Hannu', xpn_3='Viljo', xpn_5='Herra')
        pid.date_time_of_birth = '19600928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Linnankatu 37', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0223456789~^^CP^0407654323'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='KIR2', pl_3='Huone 201', pl_4='Vuode 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR302^Salminen^Tuija^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300002')
        pv1.pending_location = PL(pl_1='20260507090000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Mäkinen', xpn_2='Sirpa')
        nk1.address = XAD(xad_3='CP', xad_4='0407654324')
        nk1.nk1_6 = 'EC'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 5)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 5)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg06(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='VRK')
        msh.receiving_facility = HD(hd_1='DVV')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'LC000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300004', cx_4='TYKS', cx_5='MR'), CX(cx_1='011195-345D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Katja', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19951101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Aurakatu 2', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234572'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 6)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 6)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg07(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'LC000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260509130000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT300005', cx_4='TYKS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Salonen', xpn_2='Risto', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19580713'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Itäinen Pitkäkatu 50', xad_3='Turku', xad_5='20520', xad_6='FIN')
        pid.pid_13 = '^^PH^0225678901'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PT300099', cx_4='TYKS', cx_5='MR')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 7)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 7)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg08(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='TYKSLAB')
        msh.receiving_facility = HD(hd_1='VSSHP')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'LC000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300006', cx_4='TYKS', cx_5='MR'), CX(cx_1='180792-678E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heikkinen', xpn_2='Sami', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19920718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puutarhakatu 9', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234569'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI2', pl_3='Vastaanottohuone 6', pl_5='VSSHP')
        pv1.pv1_7 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300002')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD300001', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509085000^^R'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_10 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300001', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='TYKSLAB')
        obr.observation_date_time = '20260509085000'
        obr.obr_15 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD300001', ei_2='LIFECARE')
        obr_2.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='TYKSLAB')
        obr_2.observation_date_time = '20260509085000'
        obr_2.obr_15 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 8)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 8)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg09(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300006', cx_4='TYKS', cx_5='MR'), CX(cx_1='180792-678E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heikkinen', xpn_2='Sami', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19920718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puutarhakatu 9', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234569'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI2', pl_3='Vastaanottohuone 6', pl_5='VSSHP')
        pv1.pv1_7 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300002')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300001', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300001', ei_2='TYKSLAB')
        orc.orc_7 = '^^^20260509085000^^R'
        orc.date_time_of_order_event = '20260509133000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300001', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300001', ei_2='TYKSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='TYKSLAB')
        obr.observation_date_time = '20260509090000'
        obr.obr_14 = '20260509090000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR303^Tuominen^Riikka^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='TYKSLAB')
        obx.obx_5 = '5.9'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='TYKSLAB')
        obx_2.obx_5 = '155'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '134-167'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='TYKSLAB')
        obx_3.obx_5 = '198'
        obx_3.units = CWE(cwe_1='10E9/l')
        obx_3.reference_range = '150-360'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 9)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 9)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg10(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='LIFECARE_SCHED')
        msh.receiving_facility = HD(hd_1='VSSHP')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'LC000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT300001')
        sch.filler_appointment_id = EI(ei_1='APT300001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260520100000^20260520102000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300007', cx_4='TYKS', cx_5='MR'), CX(cx_1='090488-901F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rantala', xpn_2='Johanna', xpn_3='Elise', xpn_5='Rouva')
        pid.date_time_of_birth = '19880409'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Brahenkatu 5', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234573'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI3', pl_3='Vastaanottohuone 8', pl_5='VSSHP')
        pv1.pv1_7 = 'DR304^Laaksonen^Juha^^^LKT^Lääkäri'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='SISÄPOLI', cwe_2='Sisätautien poliklinikka', cwe_3='LIFECARE')
        ais.start_date_time = '20260520100000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR304^Laaksonen^Juha^^^LKT^Lääkäri'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 10)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 10)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg11(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='LIFECARE_SCHED')
        msh.receiving_facility = HD(hd_1='VSSHP')
        msh.date_time_of_message = '20260512090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S12')
        msh.message_control_id = 'LC000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT300001')
        sch.filler_appointment_id = EI(ei_1='APT300001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260522100000^20260522102000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300007', cx_4='TYKS', cx_5='MR'), CX(cx_1='090488-901F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rantala', xpn_2='Johanna', xpn_3='Elise', xpn_5='Rouva')
        pid.date_time_of_birth = '19880409'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Brahenkatu 5', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234573'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI3', pl_3='Vastaanottohuone 8', pl_5='VSSHP')
        pv1.pv1_7 = 'DR304^Laaksonen^Juha^^^LKT^Lääkäri'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='SISÄPOLI', cwe_2='Sisätautien poliklinikka', cwe_3='LIFECARE')
        ais.start_date_time = '20260522100000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR304^Laaksonen^Juha^^^LKT^Lääkäri'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 11)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 11)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg12(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='VSSHP_RAD')
        msh.date_time_of_message = '20260509104000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'LC000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300008', cx_4='TYKS', cx_5='MR'), CX(cx_1='241155+567G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskela', xpn_2='Olavi', xpn_3='Tapio', xpn_5='Herra')
        pid.date_time_of_birth = '19551124'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 7', xad_3='Turku', xad_5='20500', xad_6='FIN')
        pid.pid_13 = '^^PH^0227654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='PPKL', pl_3='Triage 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR305^Kallio^Merja^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300003')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD300002', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509104000^^S'
        orc.date_time_of_order_event = '20260509104000'
        orc.orc_10 = 'DR305^Kallio^Merja^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300002', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509104000'
        obr.obr_15 = 'DR305^Kallio^Merja^^^LKT^Lääkäri'
        obr.result_status = 'HENGENAHDISTUS^Hengenahdistus'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 12)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 12)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg13(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'LC000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300009', cx_4='TYKS', cx_5='MR'), CX(cx_1='130675-234H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Aalto', xpn_2='Ritva', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19750613'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kaskenkatu 11', xad_3='Turku', xad_5='20700', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876547'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='KIR1', pl_3='Huone 305', pl_4='Vuode 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR306^Koivunen^Arto^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300003')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Hoitokertomus')
        txa.document_content_presentation = 'TX'
        txa.origination_date_time = '20260509150000'
        txa.unique_document_number = EI(ei_1='DOC300001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11506-3', cwe_2='Progress note', cwe_3='LN')
        obx.obx_5 = 'Potilas toipunut leikkauksesta hyvin. Haava siisti, ei infektiomerkkejä. Kipulääkitys riittävä.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 13)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 13)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg14(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509144000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300010', cx_4='TYKS', cx_5='MR'), CX(cx_1='070540+890J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nurmi', xpn_2='Eino', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19400507'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ratapihankatu 15', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0229876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='SIS2', pl_3='Huone 504', pl_4='Vuode 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR307^Mäkelä^Esa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300004')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300003', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300003', ei_2='TYKSLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509144000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300003', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300003', ei_2='TYKSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='TYKSLAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR307^Mäkelä^Esa^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509144000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx.obx_5 = '142'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '50-90'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='P-Urea', cwe_3='LN')
        obx_2.obx_5 = '12.5'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '2.6-6.4'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='ml/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 14)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 14)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg15(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB_PAT')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300011', cx_4='TYKS', cx_5='MR'), CX(cx_1='220378-345K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lahtinen', xpn_2='Mirja', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Uudenmaankatu 3', xad_3='Turku', xad_5='20500', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234574'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI4', pl_3='Vastaanottohuone 2', pl_5='VSSHP')
        pv1.pv1_7 = 'DR308^Rantanen^Ville^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300004')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300004', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300004', ei_2='TYKSLAB_PAT')
        orc.orc_7 = '^^^20260506100000^^R'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300004', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300004', ei_2='TYKSLAB_PAT')
        obr.universal_service_identifier = CWE(cwe_1='60570-9', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20260506102000'
        obr.obr_14 = '20260506102000'
        obr.obr_15 = '^^Biopsia'
        obr.obr_16 = 'DR308^Rantanen^Ville^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report text', cwe_3='LN')
        obx.obx_5 = 'Histologinen tutkimus: Adenokarsinooma colonissa. pT3N1M0.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Patologian lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKL1BhcmVudCAy'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509170000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 15)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 15)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg16(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509152000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300012', cx_4='TYKS', cx_5='MR'), CX(cx_1='160290-012L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Toivonen', xpn_2='Antti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19900216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Maariankatu 20', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407766555'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='SIS1', pl_3='Huone 401', pl_4='Vuode 2', pl_5='VSSHP')
        pv1.pv1_7 = 'DR309^Häkkinen^Leena^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300005')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300005', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300005', ei_2='TYKSLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509152000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300005', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300005', ei_2='TYKSLAB')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Elektrolyytit', cwe_3='LN')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR309^Häkkinen^Leena^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509152000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '140'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx_2.obx_5 = '3.9'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='17861-6', cwe_2='fP-Ca-Ion', cwe_3='LN')
        obx_3.obx_5 = '1.22'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '1.15-1.30'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2601-3', cwe_2='fP-Mg', cwe_3='LN')
        obx_4.obx_5 = '0.85'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '0.71-0.94'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 16)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 16)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg17(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300013', cx_4='TYKS', cx_5='MR'), CX(cx_1='011145+678M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heinonen', xpn_2='Tauno', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19450101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Satamakatu 8', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0222345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='PPKL', pl_3='Triage 3', pl_5='VSSHP')
        pv1.pv1_7 = 'DR310^Kinnunen^Ari^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI300005')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300006', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300006', ei_2='TYKSLAB')
        orc.orc_7 = '^^^20260509103000^^S'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300006', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300006', ei_2='TYKSLAB')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='TYKSLAB')
        obr.observation_date_time = '20260509104000'
        obr.obr_14 = '20260509104000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR310^Kinnunen^Ari^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='P-TnT', cwe_3='LN')
        obx.obx_5 = '89'
        obx.units = CWE(cwe_1='ng/l')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33762-6', cwe_2='P-NTproBNP', cwe_3='LN')
        obx_2.obx_5 = '1250'
        obx_2.units = CWE(cwe_1='ng/l')
        obx_2.reference_range = '<125'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 17)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 17)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg18(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260514160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'LC000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300014', cx_4='TYKS', cx_5='MR'), CX(cx_1='050265-901N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Liisa', xpn_3='Annikki', xpn_5='Rouva')
        pid.date_time_of_birth = '19650205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Aninkaistenkatu 1', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234575'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='KIR1', pl_3='Huone 307', pl_4='Vuode 1', pl_5='VSSHP')
        pv1.pv1_7 = 'DR311^Järvinen^Matti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300006')
        pv1.pending_location = PL(pl_1='20260509080000')
        pv1.prior_temporary_location = PL(pl_1='20260514140000')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.universal_service_identifier = CWE(cwe_1='18842-5', cwe_2='Discharge summary', cwe_3='LN')
        obr.observation_date_time = '20260514160000'
        obr.obr_15 = 'DR311^Järvinen^Matti^^^LKT^Lääkäri'
        obr.filler_field_2 = '20260514160000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Discharge summary text', cwe_3='LN')
        obx.obx_5 = 'Potilas kotiutettu sappileikkauksen jälkeen. Toipuminen edennyt normaalisti. Kontrollikäynti 2 viikon kuluttua.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260514160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Loppulausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260514160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 18)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 18)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg19(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS_KONS')
        msh.date_time_of_message = '20260509141000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'LC000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300015', cx_4='TYKS', cx_5='MR'), CX(cx_1='030582-456P', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Jokinen', xpn_2='Timo', xpn_3='Sakari', xpn_5='Herra')
        pid.date_time_of_birth = '19820503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kristiinankatu 12', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234570'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='SIS2', pl_3='Huone 510', pl_4='Vuode 2', pl_5='VSSHP')
        pv1.pv1_7 = 'DR312^Peltonen^Maria^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300007')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD300007', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509141000^^R'
        orc.date_time_of_order_event = '20260509141000'
        orc.orc_10 = 'DR312^Peltonen^Maria^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300007', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='KONS', cwe_2='Konsultaatio, kardiologia', cwe_3='LIFECARE')
        obr.observation_date_time = '20260509141000'
        obr.obr_15 = 'DR312^Peltonen^Maria^^^LKT^Lääkäri'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Potilaalla toistuvia rintakipujaksoja rasituksessa. Pyydän kardiologin arviota.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 19)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 19)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg20(unittest.TestCase):
    """ Based on live/fi/fi-tietoevry-lifecare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TYKSLAB')
        msh.sending_facility = HD(hd_1='VSSHP')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'TYKSLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT300016', cx_4='TYKS', cx_5='MR'), CX(cx_1='200395-789Q', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karjalainen', xpn_2='Emilia', xpn_3='Sofia', xpn_5='Rouva')
        pid.date_time_of_birth = '19950320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppiaskatu 6', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654325'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='HEM1', pl_3='Vastaanottohuone 3', pl_5='VSSHP')
        pv1.pv1_7 = 'DR313^Lehtinen^Kari^^^LKT^Lääkäri'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD300008', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES300008', ei_2='TYKSLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509163000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300008', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES300008', ei_2='TYKSLAB')
        obr.universal_service_identifier = CWE(cwe_1='3002', cwe_2='B-Diffi', cwe_3='TYKSLAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR313^Lehtinen^Kari^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='TYKSLAB')
        obx.obx_5 = '4.2'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='770-8', cwe_2='B-Neutro', cwe_3='TYKSLAB')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '40-75'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='736-9', cwe_2='B-Lymfo', cwe_3='TYKSLAB')
        obx_3.obx_5 = '35'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '20-45'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5905-5', cwe_2='B-Mono', cwe_3='TYKSLAB')
        obx_4.obx_5 = '6'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '2-10'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='713-8', cwe_2='B-Eosino', cwe_3='TYKSLAB')
        obx_5.obx_5 = '3'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '1-6'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='706-2', cwe_2='B-Baso', cwe_3='TYKSLAB')
        obx_6.obx_5 = '1'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '0-2'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 20)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 20)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################

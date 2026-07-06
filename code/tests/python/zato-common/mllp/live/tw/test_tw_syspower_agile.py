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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, DR, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, DftP03Financial, DftP03Visit, MdmT02Observation, OmlO33ObservationRequest, OmlO33Order, OmlO33OrderPrior, \
    OmlO33Patient, OmlO33PatientVisit, OmlO33PriorResult, OmlO33Specimen, OmlO33SpecimenContainer, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, \
    RdeO11Patient, RdeO11PatientVisit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, DFT_P03, MDM_T02, OML_O33, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, FT1, IN1, MSH, OBR, OBX, ORC, PID, PV1, RGS, RXE, RXO, RXR, SAC, SCH, SPM, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-syspower-agile.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-syspower-agile.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CMUH20260509080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')
        pid.pid_13 = '^^PH^04-23861234~^^CP^0921345678'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C213678945^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.admit_date_time = '20260509080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'
        in1.insureds_relationship_to_patient = CWE(cwe_1='傅', cwe_2='鎮宇')
        in1.insureds_date_of_birth = 'Self'
        in1.insureds_address = XAD(xad_1='19751108')
        in1.assignment_of_benefits = CWE(cwe_1='台中市南屯區公益路二段51號', cwe_3='台中市', cwe_5='40867', cwe_6='TW')

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CMUH20260509093001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')
        pid.pid_13 = '^^PH^04-24521234~^^CP^0964567890'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'D324789056^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260509093000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260516100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CMUH20260516100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260516100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')
        pid.pid_13 = '^^PH^04-23861234~^^CP^0921345678'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C213678945^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.discharged_to_location = DLD(dld_1='9')
        pv1.account_status = CWE(cwe_1='20260516100000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='動脈粥樣硬化性心臟病', cwe_3='ICD-10-CM')
        dg1.diagnosis_date_time = '20260509'
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260510110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CMUH20260510110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260510110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')
        pid.pid_13 = '^^PH^04-24521234~^^CP^0964567890'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'D324789056^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260510110000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260512070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CMUH20260512070001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260512070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')
        pid.pid_13 = '^^PH^04-23861234~^^CP^0921345678'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C213678945^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='加護病房', pl_2='ICU02', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.delete_account_date = '心臟內科^801^A^中國醫藥大學附設醫院'
        pv1.servicing_facility = CWE(cwe_1='20260512070000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509084500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CMUH20260509084501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='ORD20260509010')
        orc.orc_7 = '^^^20260509084500^^R'
        orc.date_time_of_order_event = '20260509084500'
        orc.orc_10 = 'N200100^護理師馮小雲'
        orc.enterers_location = PL(pl_1='D200100', pl_2='鍾雅慧', pl_5='醫師')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='B024184100', cwe_2='Aspirin 100mg', cwe_3='NHI')
        rxo.requested_give_amount_maximum = '100'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.requested_dosage_form = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='QD')
        rxo.rxo_14 = 'D200100^鍾雅慧'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD20260509011')
        orc_2.orc_7 = '^^^20260509084500^^R'
        orc_2.date_time_of_order_event = '20260509084500'
        orc_2.orc_10 = 'N200100^護理師馮小雲'
        orc_2.enterers_location = PL(pl_1='D200100', pl_2='鍾雅慧', pl_5='醫師')

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='C09CA01', cwe_2='Losartan 50mg', cwe_3='NHI')
        rxo_2.requested_give_amount_maximum = '50'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.requested_dosage_form = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')
        rxo_2.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='QD')
        rxo_2.rxo_14 = 'D200100^鍾雅慧'

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build ORC ..
        orc_3 = ORC()
        orc_3.order_control = 'NW'
        orc_3.placer_order_number = EI(ei_1='ORD20260509012')
        orc_3.orc_7 = '^^^20260509084500^^R'
        orc_3.date_time_of_order_event = '20260509084500'
        orc_3.orc_10 = 'N200100^護理師馮小雲'
        orc_3.enterers_location = PL(pl_1='D200100', pl_2='鍾雅慧', pl_5='醫師')

        # .. build RXO ..
        rxo_3 = RXO()
        rxo_3.requested_give_code = CWE(cwe_1='C10AA05', cwe_2='Atorvastatin 20mg', cwe_3='NHI')
        rxo_3.requested_give_amount_maximum = '20'
        rxo_3.requested_give_units = CWE(cwe_1='mg')
        rxo_3.requested_dosage_form = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')
        rxo_3.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='QD-HS')
        rxo_3.rxo_14 = 'D200100^鍾雅慧'

        # .. build RXR ..
        rxr_3 = RXR()
        rxr_3.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, orc_2, rxo_2, rxr_2, orc_3, rxo_3, rxr_3]

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CMUH20260509100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509010')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509010')
        obr.universal_service_identifier = CWE(cwe_1='75571-7', cwe_2='心臟電腦斷層造影', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'D200100^鍾雅慧^^^醫師'
        obr.result_status = '^ROUTINE'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260509120001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509010')
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509010')
        obr.universal_service_identifier = CWE(cwe_1='89579-7', cwe_2='心臟標記檢查', cwe_3='LN')
        obr.observation_date_time = '20260509081000'
        obr.obr_14 = '20260509081000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D200100^鍾雅慧^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='肌鈣蛋白-I', cwe_3='LN')
        obx.obx_5 = '0.04'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='49563-0', cwe_2='CK-MB質量', cwe_3='LN')
        obx_2.obx_5 = '3.2'
        obx_2.units = CWE(cwe_1='ng/mL')
        obx_2.reference_range = '0.0-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33762-6', cwe_2='NT-proBNP', cwe_3='LN')
        obx_3.obx_5 = '450'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '0-125'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='30522-7', cwe_2='C反應蛋白(高敏感)', cwe_3='LN')
        obx_4.obx_5 = '2.8'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.reference_range = '0.0-3.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2093-3', cwe_2='總膽固醇', cwe_3='LN')
        obx_5.obx_5 = '228'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '0-200'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2089-1', cwe_2='LDL膽固醇', cwe_3='LN')
        obx_6.obx_5 = '152'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '0-130'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509120000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260509150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509020')
        orc.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509020')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素', cwe_3='LN')
        obr.observation_date_time = '20260509093500'
        obr.obr_14 = '20260509093500'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D200200^葛明志^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素(HbA1c)', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-5.6'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='空腹血糖', cwe_3='LN')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-100'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='14749-6', cwe_2='葡萄糖(飯後2小時)', cwe_3='LN')
        obx_3.obx_5 = '198'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '70-140'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='CARDIOLOGY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260510160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260510160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='ECHO20260510001')
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECHO20260510001')
        obr.universal_service_identifier = CWE(cwe_1='34552-0', cwe_2='心臟超音波', cwe_3='LN')
        obr.observation_date_time = '20260510140000'
        obr.obr_14 = '20260510140000'
        obr.obr_16 = 'D200100^鍾雅慧^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='10230-1', cwe_2='左心室射出率', cwe_3='LN')
        obx.obx_5 = '55'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '55-70'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='29468-6', cwe_2='左心室舒張末徑', cwe_3='LN')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='mm')
        obx_2.reference_range = '36-56'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='34552-0', cwe_2='心臟超音波結論', cwe_3='LN')
        obx_3.obx_5 = '左心室大小及功能正常, LVEF 55%。瓣膜無明顯異常。主動脈根部正常。無心包膜積液。'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260510160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='心臟超音波報告PDF', cwe_3='L')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzMDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5b+D6Ie96LaF'
            '6Z+z5rOi5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAooTFZFRjogNTUlLCDlt6blv4PlrqTlip/og73mraPluLgpIFRqCjAgLTIwIFRk'
            'Cijnk6PohJznhKHmmI7poa/nlbDluLgpIFRqCjAgLTIwIFRkCijkuLvli5Xohoh+mariueato+W4uCkgVGoKMCAtMjAgVGQKKOeEoeW/g+WMheiGnOepjea2sikgVGoKRVQKZW5kc3Ry'
            'ZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMjY2IDAwMDAwIG4gCjAwMDAwMDA2MTYgMDAwMDAgbiAK'
            'dHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo2ODEKJSVFT0YK'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260510160000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509095500'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CMUH20260509095501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='RX20260509010')
        orc.orc_7 = '^^^20260509095500^^R'
        orc.date_time_of_order_event = '20260509095500'
        orc.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260509^^BID^90^Day'
        rxe.give_amount_minimum = 'A10BA02^Metformin 850mg^NHI'
        rxe.give_amount_maximum = '850'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_strength = '2'
        rxe.give_strength_units = CWE(cwe_1='Tab')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='RX20260509011')
        orc_2.orc_7 = '^^^20260509095500^^R'
        orc_2.date_time_of_order_event = '20260509095500'
        orc_2.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20260509^^QD^90^Day'
        rxe_2.give_amount_minimum = 'A10BH01^Sitagliptin 100mg^NHI'
        rxe_2.give_amount_maximum = '100'
        rxe_2.give_units = CWE(cwe_1='mg')
        rxe_2.give_strength = '1'
        rxe_2.give_strength_units = CWE(cwe_1='Tab')

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build the ORDER group ..
        order_2 = RdeO11Order()
        order_2.orc = orc_2
        order_2.rxe = rxe_2
        order_2.rxr = rxr_2

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='SCHEDULING')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509161000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CMUH20260509161001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260523001')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^15^20260523100000^20260523101500'
        sch.sch_13 = 'D200200^葛明志^^^醫師'
        sch.placer_contact_address = XAD(xad_3='PH', xad_4='04-24521234')
        sch.placer_contact_location = PL(pl_1='台中市西屯區文心路二段281號', pl_3='台中市', pl_5='40758', pl_6='TW')
        sch.filler_contact_person = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')
        pid.pid_13 = '^^CP^0964567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

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
        ais.universal_service_identifier = CWE(cwe_1='新陳代謝科門診', cwe_2='Endocrinology', cwe_3='L')
        ais.start_date_time = '20260523100000'
        ais.start_date_time_offset = '15'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')
        aip.start_date_time_offset_units = CNE(cne_1='20260523100000')
        aip.duration = '15'
        aip.duration_units = CNE(cne_1='min')

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260516120000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CMUH20260516120001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260516120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260509')
        ft1.transaction_batch_id = '20260516'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_4='B024184100', cwe_5='Aspirin 100mg', cwe_6='NHI')
        ft1.ft1_8 = '7'
        ft1.ft1_9 = '100'
        ft1.transaction_quantity = 'mg'
        ft1.performed_by_code = XCN(xcn_1='I25.1', xcn_2='動脈粥樣硬化性心臟病', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260509')
        ft1_2.transaction_batch_id = '20260516'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_4='18003C', cwe_5='心臟電腦斷層造影', cwe_6='NHI')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_9 = '1'
        ft1_2.transaction_quantity = 'EA'
        ft1_2.performed_by_code = XCN(xcn_1='I25.1', xcn_2='動脈粥樣硬化性心臟病', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260509')
        ft1_3.transaction_batch_id = '20260516'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_4='09002C', cwe_5='心臟超音波', cwe_6='NHI')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_9 = '1'
        ft1_3.transaction_quantity = 'EA'
        ft1_3.performed_by_code = XCN(xcn_1='I25.1', xcn_2='動脈粥樣硬化性心臟病', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build FT1 ..
        ft1_4 = FT1()
        ft1_4.set_id_ft1 = '4'
        ft1_4.transaction_id = CX(cx_1='20260509')
        ft1_4.transaction_batch_id = '20260516'
        ft1_4.transaction_date = DR(dr_1='CG')
        ft1_4.transaction_posting_date = 'D'
        ft1_4.transaction_type = CWE(cwe_4='00201A', cwe_5='住院診察費', cwe_6='NHI')
        ft1_4.ft1_8 = '7'
        ft1_4.ft1_9 = '1'
        ft1_4.transaction_quantity = 'EA'
        ft1_4.performed_by_code = XCN(xcn_1='I25.1', xcn_2='動脈粥樣硬化性心臟病', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_4 = DftP03Financial()
        financial_4.ft1 = ft1_4

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2, financial_3, financial_4]

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260516110000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CMUH20260516110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260516110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='出院摘要', cwe_3='L')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20260516110000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        txa.transcription_date_time = '20260516110000'
        txa.originator_code_name = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')
        txa.parent_document_number = EI(ei_1='DOC20260516001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='出院摘要', cwe_3='LN')
        obx.obx_5 = (
            '入院日期: 2026/05/09\\.br\\主訴: 胸悶及活動性喘3天\\.br\\診斷: 動脈粥樣硬化性心臟病 (I25.1)\\.br\\治療: 心臟電腦斷層及超音波評估, 藥物治療\\.br'
            '\\心臟超音波: LVEF 55%, 瓣膜正常\\.br\\出院後注意: 規律服藥, 控制血脂, 避免劇烈運動\\.br\\回診日期: 2026/05/23'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260516110000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509155000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260509155001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509030')
        orc.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509030')
        obr.universal_service_identifier = CWE(cwe_1='94385-7', cwe_2='甲狀腺功能檢查', cwe_3='LN')
        obr.observation_date_time = '20260509094000'
        obr.obr_14 = '20260509094000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D200200^葛明志^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '2.35'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '1.18'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.93-1.70'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '3.05'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.00-4.40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509155000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509073000'
        msh.message_type = MSG(msg_1='OML', msg_2='O33', msg_3='OML_O33')
        msh.message_control_id = 'CMUH20260509073001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO33PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO33Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='全血', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509073000')
        spm.specimen_collection_date_time = DR(dr_1='20260509073500')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='TUBE20260509010')
        sac.additive = CWE(cwe_1='BLD')

        # .. build the SPECIMEN_CONTAINER group ..
        specimen_container = OmlO33SpecimenContainer()
        specimen_container.sac = sac

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LAB20260509010')
        orc.orc_7 = '^^^20260509073000^^R'
        orc.date_time_of_order_event = '20260509073000'
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509010')
        obr.universal_service_identifier = CWE(cwe_1='89579-7', cwe_2='心臟標記檢查', cwe_3='LN')
        obr.observation_date_time = '20260509073000'

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB20260509011')
        orc_2.orc_7 = '^^^20260509073000^^R'
        orc_2.date_time_of_order_event = '20260509073000'
        orc_2.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260509011')
        obr_2.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='脂質檢查', cwe_3='LN')
        obr_2.observation_date_time = '20260509073000'

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO33OrderPrior()
        order_prior.orc = orc_2
        order_prior.obr = obr_2

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO33PriorResult()
        prior_result.order_prior = order_prior

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO33ObservationRequest()
        observation_request.obr = obr
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO33Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. build the SPECIMEN group ..
        specimen = OmlO33Specimen()
        specimen.spm = spm
        specimen.specimen_container = specimen_container
        specimen.order = order

        # .. assemble the full message ..
        msg = OML_O33()
        msg.msh = msh
        msg.patient = patient
        msg.specimen = specimen

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260510090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260510090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260510001')
        orc.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260510001')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='腎功能檢查', cwe_3='LN')
        obr.observation_date_time = '20260509094500'
        obr.obr_14 = '20260509094500'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D200200^葛明志^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obx.obx_5 = '0.85'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '0.5-1.1'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='尿素氮', cwe_3='LN')
        obx_2.obx_5 = '16'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '7-20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_3.obx_5 = '98'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260510090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='14959-1', cwe_2='尿微量白蛋白/肌酸酐比', cwe_3='LN')
        obx_4.obx_5 = '28'
        obx_4.units = CWE(cwe_1='mg/g')
        obx_4.reference_range = '0-30'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260510090000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260511140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260511140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509010')
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509010')
        obr.universal_service_identifier = CWE(cwe_1='75571-7', cwe_2='心臟電腦斷層造影', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_14 = '20260509100000'
        obr.obr_16 = 'D200100^鍾雅慧^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='75571-7', cwe_2='心臟電腦斷層造影', cwe_3='LN')
        obx.obx_5 = (
            '冠狀動脈鈣化分數: 85 (中度風險)\\.br\\左前降支: 近端50%狹窄, 混合斑塊\\.br\\左旋支: 無明顯狹窄\\.br\\右冠狀動脈: 近端30%狹窄, 鈣化斑塊\\.br\\結'
            '論: 中度冠狀動脈粥樣硬化, 建議藥物治療及密切追蹤。'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='心臟CT報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5b+D6Ie96Zu7'
            '6IWm5pa35bGk5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAoo5Yag54uA5YuV6ISI6Yi15YyW5YiG5pW4OiA4NSkgVGoKMCAtMjAgVGQK'
            'KOW3puWJjeemoeaUrzog6L+R56uvNTAl54uH56qqKSBUagowIC0yMCBUZAoo5bem5peL5pSvOiDnhKHmmI7poa/ni7nnqqopIFRqCjAgLTIwIFRkCijlj7PlhqDni4DliofohIg6IOi/'
            'keernTMwJeeLueeptikgVGoKMCAtMjAgVGQKKOe1kOirljog5Lit5bqm5Yag54uA5YuV6ISI57Kl5qij56Gs5YyWKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5'
            'cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAK'
            'MDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDc2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3Qg'
            'MSAwIFIKPj4Kc3RhcnR4cmVmCjgzMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260511140000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260509130001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200100', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='傅', xpn_2='鎮宇', xpn_5='先生')
        pid.date_time_of_birth = '19751108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台中市南屯區公益路二段51號', xad_3='台中市', xad_5='40867', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='心臟內科', pl_2='801', pl_3='A', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200100', xcn_2='鍾雅慧', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509040')
        orc.orc_12 = 'D200100^鍾雅慧^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509040')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='凝血功能檢查', cwe_3='LN')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D200100^鍾雅慧^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='凝血酶原時間(PT)', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-13.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.85-1.15'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='活化部分凝血活酶時間(APTT)', cwe_3='LN')
        obx_3.obx_5 = '28.5'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25.0-35.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='纖維蛋白原', cwe_3='LN')
        obx_4.obx_5 = '285'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509130000'

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
    """ Based on live/tw/tw-syspower-agile.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Agile-HIS')
        msh.sending_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='中國醫藥大學附設醫院')
        msh.date_time_of_message = '20260510170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CMUH20260510170001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT200200', cx_4='中國醫藥大學附設醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='簡', xpn_2='佩芸', xpn_5='女士')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台中市西屯區文心路二段281號', xad_3='台中市', xad_5='40758', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='新陳代謝科門診', pl_2='診間12', pl_4='中國醫藥大學附設醫院')
        pv1.attending_doctor = XCN(xcn_1='D200200', xcn_2='葛明志', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='US20260510001')
        orc.orc_12 = 'D200200^葛明志^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='US20260510001')
        obr.universal_service_identifier = CWE(cwe_1='79103-8', cwe_2='腹部超音波', cwe_3='LN')
        obr.observation_date_time = '20260510150000'
        obr.obr_14 = '20260510150000'
        obr.obr_16 = 'D200200^葛明志^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='79103-8', cwe_2='腹部超音波', cwe_3='LN')
        obx.obx_5 = '肝臟大小正常, 實質回音均勻, 無局灶性病變。膽囊壁光滑, 無結石。胰臟及脾臟正常。雙腎大小正常, 無水腎。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='腹部超音波報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWg6YOo6LaF'
            '6Z+z5rOi5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAoo6IKd6IeP5aSn5bCP5q2j5bi4LCDnhKHlsYDnhabbgOaAp+eXheennSkgVGoK'
            'MCAtMjAgVGQKKOiDhuWbiuWSgOWFiea7kSwg54Sh57WQ55+zKSBUagowIC0yMCBUZAoo6Iac6Ie+5Y+K6IS+6Ie+5q2j5bi4KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoK'
            'PDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAw'
            'MDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDU2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYK'
            'L1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjYzMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510170000'

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

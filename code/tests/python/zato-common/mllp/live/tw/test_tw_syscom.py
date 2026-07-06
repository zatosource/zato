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

_md_path = md_path_for('tw', 'tw-syscom.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-syscom.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TPVGH20260509083001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')
        pid.pid_13 = '^^PH^02-28381234~^^CP^0906123789'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A180456723^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.admit_date_time = '20260509083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'
        in1.insureds_relationship_to_patient = CWE(cwe_1='宋', cwe_2='瑞鵬')
        in1.insureds_date_of_birth = 'Self'
        in1.insureds_address = XAD(xad_1='19680415')
        in1.assignment_of_benefits = CWE(cwe_1='台北市士林區中正路601號', cwe_3='台北市', cwe_5='11146', cwe_6='TW')

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
    """ Based on live/tw/tw-syscom.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'TPVGH20260509091501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509091500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')
        pid.pid_13 = '^^PH^02-22451234~^^CP^0973456012'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'B291567834^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260509091500'

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
    """ Based on live/tw/tw-syscom.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260515140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'TPVGH20260515140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260515140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')
        pid.pid_13 = '^^PH^02-28381234~^^CP^0906123789'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A180456723^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.discharged_to_location = DLD(dld_1='9')
        pv1.account_status = CWE(cwe_1='20260515140000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='肺炎, 未明示', cwe_3='ICD-10-CM')
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
    """ Based on live/tw/tw-syscom.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'TPVGH20260510100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260510100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')
        pid.pid_13 = '^^PH^02-22451234~^^CP^0973456012'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'B291567834^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260510100000'

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
    """ Based on live/tw/tw-syscom.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'TPVGH20260512080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260512080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')
        pid.pid_13 = '^^PH^02-28381234~^^CP^0906123789'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A180456723^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胸腔內科', pl_2='502', pl_3='B', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.delete_account_date = '內科病房^301^A^台北榮民總醫院'
        pv1.servicing_facility = CWE(cwe_1='20260512080000')

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
    """ Based on live/tw/tw-syscom.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509094500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TPVGH20260509094501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='ORD20260509001')
        orc.orc_7 = '^^^20260509094500^^R'
        orc.date_time_of_order_event = '20260509094500'
        orc.orc_10 = 'N100100^護理師孫曉琳'
        orc.enterers_location = PL(pl_1='D100100', pl_2='謝宜芳', pl_5='醫師')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='A029216100', cwe_2='Levofloxacin 500mg', cwe_3='NHI')
        rxo.requested_give_amount_maximum = '500'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.requested_dosage_form = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='QD')
        rxo.rxo_14 = 'D100100^謝宜芳'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD20260509002')
        orc_2.orc_7 = '^^^20260509094500^^R'
        orc_2.date_time_of_order_event = '20260509094500'
        orc_2.orc_10 = 'N100100^護理師孫曉琳'
        orc_2.enterers_location = PL(pl_1='D100100', pl_2='謝宜芳', pl_5='醫師')

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='A032788100', cwe_2='Acetaminophen 500mg', cwe_3='NHI')
        rxo_2.requested_give_amount_maximum = '500'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.requested_dosage_form = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')
        rxo_2.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='Q6H')
        rxo_2.rxo_14 = 'D100100^謝宜芳'

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, orc_2, rxo_2, rxr_2]

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
    """ Based on live/tw/tw-syscom.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509101000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TPVGH20260509101001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509001')
        orc.orc_7 = '^^^20260509101000^^R'
        orc.date_time_of_order_event = '20260509101000'
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509001')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509101000'
        obr.obr_15 = 'D100100^謝宜芳^^^醫師'
        obr.result_status = '^URGENT'

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
    """ Based on live/tw/tw-syscom.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260509113001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260509080000'
        obr.obr_14 = '20260509080000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx.obx_5 = '11.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='紅血球計數', cwe_3='LN')
        obx_2.obx_5 = '4.85'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.50-5.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_3.obx_5 = '14.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.0-17.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='血比容', cwe_3='LN')
        obx_4.obx_5 = '43.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '39.0-49.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='血小板計數', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='嗜中性球百分比', cwe_3='LN')
        obx_6.obx_5 = '72.5'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40.0-70.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509113000'

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
    """ Based on live/tw/tw-syscom.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260509143001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509002')
        orc.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509002')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='基礎代謝功能', cwe_3='LN')
        obr.observation_date_time = '20260509090000'
        obr.obr_14 = '20260509090000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D100200^鄧國豪^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='血糖(飯前)', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='尿素氮', cwe_3='LN')
        obx_2.obx_5 = '15'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '7-20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obx_3.obx_5 = '0.9'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.6-1.2'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='鈉', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='鉀', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx_6.obx_5 = '28'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '7-56'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_7.obx_5 = '22'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '10-40'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

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
        order_observation.observation_7 = observation_7

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
    """ Based on live/tw/tw-syscom.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260509153001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509001')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obx.obx_5 = '兩側肺野清晰, 無明顯浸潤。心臟大小正常, 縱膈腔無異常。肋骨膈角銳利。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='胸部X光報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyMDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IO46YOoWOWF'
            'ieioreWHuuloiuWRiiAtIOWPsOWMl+a0sue4veevhOe4veWQiOmGq+mZoikgVGoKMCAtMjAgVGQKKOWFqeWBtOiCuuW3numHjuW4uCwg5peg5piO6aGv5rWu5r2kLikg VGoKMCAtMjA'
            'gVGQKKOW/g+iHn+Wkp+Wwj+ato+W4uC4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXR'
            'pY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDA'
            'wMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNTE2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNTk3CiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

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
    """ Based on live/tw/tw-syscom.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509095000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'TPVGH20260509095001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RX20260509001')
        orc.orc_7 = '^^^20260509095000^^R'
        orc.date_time_of_order_event = '20260509095000'
        orc.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260509^^TID^7^Day'
        rxe.give_amount_minimum = 'A044338100^Metformin 500mg^NHI'
        rxe.give_amount_maximum = '500'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_strength = '3'
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
        orc_2.placer_order_number = EI(ei_1='RX20260509002')
        orc_2.orc_7 = '^^^20260509095000^^R'
        orc_2.date_time_of_order_event = '20260509095000'
        orc_2.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20260509^^QD^30^Day'
        rxe_2.give_amount_minimum = 'B024560100^Amlodipine 5mg^NHI'
        rxe_2.give_amount_maximum = '5'
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
    """ Based on live/tw/tw-syscom.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='SCHEDULING')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'TPVGH20260509160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260520001')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^30^20260520090000^20260520093000'
        sch.sch_13 = 'D100200^鄧國豪^^^醫師'
        sch.placer_contact_address = XAD(xad_3='PH', xad_4='02-28712121')
        sch.placer_contact_location = PL(pl_1='忠孝東路二段201號', pl_3='台北市', pl_5='11217', pl_6='TW')
        sch.filler_contact_person = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')
        pid.pid_13 = '^^CP^0973456012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

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
        ais.universal_service_identifier = CWE(cwe_1='家醫科門診', cwe_2='General Medicine', cwe_3='L')
        ais.start_date_time = '20260520090000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')
        aip.start_date_time_offset_units = CNE(cne_1='20260520090000')
        aip.duration = '30'
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
    """ Based on live/tw/tw-syscom.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260515150000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'TPVGH20260515150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260515150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260509')
        ft1.transaction_batch_id = '20260515'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_4='A029216100', cwe_5='Levofloxacin 500mg', cwe_6='NHI')
        ft1.ft1_8 = '7'
        ft1.ft1_9 = '500'
        ft1.transaction_quantity = 'mg'
        ft1.performed_by_code = XCN(xcn_1='J18.9', xcn_2='肺炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260509')
        ft1_2.transaction_batch_id = '20260515'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_4='09005C', cwe_5='胸部X光', cwe_6='NHI')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_9 = '1'
        ft1_2.transaction_quantity = 'EA'
        ft1_2.performed_by_code = XCN(xcn_1='J18.9', xcn_2='肺炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260509')
        ft1_3.transaction_batch_id = '20260515'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_4='06012C', cwe_5='全血球計數', cwe_6='NHI')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_9 = '1'
        ft1_3.transaction_quantity = 'EA'
        ft1_3.performed_by_code = XCN(xcn_1='J18.9', xcn_2='肺炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build FT1 ..
        ft1_4 = FT1()
        ft1_4.set_id_ft1 = '4'
        ft1_4.transaction_id = CX(cx_1='20260509')
        ft1_4.transaction_batch_id = '20260515'
        ft1_4.transaction_date = DR(dr_1='CG')
        ft1_4.transaction_posting_date = 'D'
        ft1_4.transaction_type = CWE(cwe_4='00201A', cwe_5='住院診察費', cwe_6='NHI')
        ft1_4.ft1_8 = '7'
        ft1_4.ft1_9 = '1'
        ft1_4.transaction_quantity = 'EA'
        ft1_4.performed_by_code = XCN(xcn_1='J18.9', xcn_2='肺炎', xcn_3='ICD-10-CM')

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
    """ Based on live/tw/tw-syscom.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260515160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'TPVGH20260515160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260515160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='出院摘要', cwe_3='L')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20260515160000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        txa.transcription_date_time = '20260515160000'
        txa.originator_code_name = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')
        txa.parent_document_number = EI(ei_1='DOC20260515001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='出院摘要', cwe_3='LN')
        obx.obx_5 = (
            '入院日期: 2026/05/09\\.br\\主訴: 發燒咳嗽3天\\.br\\診斷: 社區型肺炎 (J18.9)\\.br\\治療: Levofloxacin靜脈注射7天, 症狀改善後轉口服\\.br\\出院後注'
            '意: 繼續口服抗生素5天, 一週後門診追蹤\\.br\\出院醫囑: 返診日期2026/05/22'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260515160000'

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
    """ Based on live/tw/tw-syscom.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260512100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260512100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='MIC20260512001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MIC20260512001')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='細菌培養及鑑定', cwe_3='LN')
        obr.observation_date_time = '20260509120000'
        obr.obr_14 = '20260509120000'
        obr.obr_15 = '痰液^Sputum'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='細菌培養及鑑定', cwe_3='LN')
        obx.obx_5 = (
            '培養結果: Streptococcus pneumoniae\\.br\\菌落計數: >10^'
            '5 CFU/mL\\.br\\感受性試驗:\\.br\\Penicillin - S (MIC 0.03)\\.br\\Levofloxacin - S (MIC 0.5)\\.br\\Erythromycin - R (MIC >8)\\.br\\Ceftriaxone - '
            'S (MIC 0.25)'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='微生物培養報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5b6u55Sf54mp'
            '5Z+56aSK5aCx5ZGKIC0g5Y+w5YyX5qa654mH57i957i957uN6Yar6ZmiKSBUagowIC0yMCBUZAoo5qpC5pys6aGe5YilOiDnl7Dmtrb (Sputum))IFRqCjAgLTIwIFRkCijln7nolL3'
            'oqIjmlbg6ID4xMF41IENGVS9tTCkgVGoKMCAtMjAgVGQKKFN0cmVwdG9jb2NjdXMgcG5ldW1vbmlhZSkgVGoKMCAtMjAgVGQKKFBlbmljaWxsaW46IFMsIExldm9mbG94YWNpbjogUyw'
            'gRXJ5dGhyb215Y2luOiBSKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmV'
            'uZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjY'
            'gMDAwMDAgbiAKMDAwMDAwMDY2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjczMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260512100000'

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
    """ Based on live/tw/tw-syscom.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509075000'
        msh.message_type = MSG(msg_1='OML', msg_2='O33', msg_3='OML_O33')
        msh.message_control_id = 'TPVGH20260509075001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

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
        spm.specimen_risk_code = CWE(cwe_1='20260509075000')
        spm.specimen_collection_date_time = DR(dr_1='20260509075500')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='TUBE20260509001')
        sac.additive = CWE(cwe_1='BLD')

        # .. build the SPECIMEN_CONTAINER group ..
        specimen_container = OmlO33SpecimenContainer()
        specimen_container.sac = sac

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LAB20260509003')
        orc.orc_7 = '^^^20260509075000^^R'
        orc.date_time_of_order_event = '20260509075000'
        orc.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509003')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='基礎代謝功能', cwe_3='LN')
        obr.observation_date_time = '20260509075000'

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB20260509004')
        orc_2.orc_7 = '^^^20260509075000^^R'
        orc_2.date_time_of_order_event = '20260509075000'
        orc_2.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260509004')
        obr_2.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素', cwe_3='LN')
        obr_2.observation_date_time = '20260509075000'

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
    """ Based on live/tw/tw-syscom.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='CARDIOLOGY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260510140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260510140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='ECG20260510001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECG20260510001')
        obr.universal_service_identifier = CWE(cwe_1='11524-6', cwe_2='12導程心電圖', cwe_3='LN')
        obr.observation_date_time = '20260510130000'
        obr.obr_14 = '20260510130000'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='8867-4', cwe_2='心律', cwe_3='LN')
        obx.obx_5 = '78'
        obx.units = CWE(cwe_1='bpm')
        obx.reference_range = '60-100'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8625-6', cwe_2='PR間期', cwe_3='LN')
        obx_2.obx_5 = '168'
        obx_2.units = CWE(cwe_1='ms')
        obx_2.reference_range = '120-200'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8633-0', cwe_2='QRS時間', cwe_3='LN')
        obx_3.obx_5 = '88'
        obx_3.units = CWE(cwe_1='ms')
        obx_3.reference_range = '60-100'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8634-8', cwe_2='QTc間期', cwe_3='LN')
        obx_4.obx_5 = '420'
        obx_4.units = CWE(cwe_1='ms')
        obx_4.reference_range = '350-440'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='11524-6', cwe_2='心電圖結論', cwe_3='LN')
        obx_5.obx_5 = '正常竇性心律, 心率78次/分鐘。PR間期及QRS波正常。無ST-T段異常。'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5

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
    """ Based on live/tw/tw-syscom.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260509160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100200', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='康', xpn_2='怡璇', xpn_5='女士')
        pid.date_time_of_birth = '19820920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市中和區景平路468號', xad_3='新北市', xad_5='23574', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='家醫科門診', pl_2='診間05', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100200', xcn_2='鄧國豪', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509005')
        orc.orc_12 = 'D100200^鄧國豪^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509005')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='尿液常規檢查', cwe_3='LN')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '尿液^Urine'
        obr.obr_16 = 'D100200^鄧國豪^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2756-5', cwe_2='尿液酸鹼值', cwe_3='LN')
        obx.obx_5 = '6.0'
        obx.reference_range = '5.0-8.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2965-2', cwe_2='尿比重', cwe_3='LN')
        obx_2.obx_5 = '1.020'
        obx_2.reference_range = '1.005-1.030'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5804-0', cwe_2='尿蛋白', cwe_3='LN')
        obx_3.obx_5 = '陰性'
        obx_3.reference_range = '陰性'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5792-7', cwe_2='尿糖', cwe_3='LN')
        obx_4.obx_5 = '陰性'
        obx_4.reference_range = '陰性'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5821-4', cwe_2='尿液白血球', cwe_3='LN')
        obx_5.obx_5 = '2'
        obx_5.units = CWE(cwe_1='/HPF')
        obx_5.reference_range = '0-5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='5787-7', cwe_2='尿液紅血球', cwe_3='LN')
        obx_6.obx_5 = '1'
        obx_6.units = CWE(cwe_1='/HPF')
        obx_6.reference_range = '0-3'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/tw/tw-syscom.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='PATHOLOGY')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260516110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260516110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='PATH20260516001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20260516001')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='病理組織檢查', cwe_3='LN')
        obr.observation_date_time = '20260511090000'
        obr.obr_14 = '20260511090000'
        obr.obr_15 = '組織^Tissue'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='病理組織檢查', cwe_3='LN')
        obx.obx_5 = (
            '檢體: 右下肺葉支氣管鏡切片\\.br\\肉眼觀: 灰白色組織碎片3枚\\.br\\鏡檢: 慢性發炎細胞浸潤, 黏膜下纖維化\\.br\\診斷: 慢性支氣管炎, 無惡性細胞\\.br'
            '\\病理醫師: 周德芳醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260516110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='病理報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0MDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo55eF55CG5aCx'
            '5ZGKIC0g5Y+w5YyX5qa654mH57e957i957uN6Yar6ZmiKSBUagowIC0yMCBUZAoo5qpC5pysOiDlj7PkuIvogrrokYnmlK/msKPnrqHpj6Hmj5Lku7YpIFRqCjAgLTIwIFRkCijogonn'
            'nLzop4A6IOeBsOeZveiJsuezlOe5lOeiiueJh+S4ieaemikgVGoKMCAtMjAgVGQKKOmPoemaqDog5oWi5oCn55m854KO57Sw6IOe5rWu5r2kKSBUagowIC0yMCBUZAoo6a2P6IaP5LiL'
            '57ea57at5YyWKSBUagowIC0yMCBUZAoo6Ki65pa3OiDmhaLmgKfmlK/msKPnrqHngogsIOeEoeaDoeaAp+e0sOiDnikgVGoKMCAtMjAgVGQKKOeXheeQhuirlOW4qzog5p2O5piO5b63'
            '6Yar5birKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVm'
            'CjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAK'
            'MDAwMDAwMDcxNiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjc4MQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260516110000'

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
    """ Based on live/tw/tw-syscom.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYSCOM-HIS')
        msh.sending_facility = HD(hd_1='台北榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台北榮民總醫院')
        msh.date_time_of_message = '20260514090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TPVGH20260514090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT100100', cx_4='台北榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='宋', xpn_2='瑞鵬', xpn_5='先生')
        pid.date_time_of_birth = '19680415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台北市士林區中正路601號', xad_3='台北市', xad_5='11146', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='內科病房', pl_2='301', pl_3='A', pl_4='台北榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D100100', xcn_2='謝宜芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260514001')
        orc.orc_12 = 'D100100^謝宜芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260514001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='肝功能檢查', cwe_3='LN')
        obr.observation_date_time = '20260514070000'
        obr.obr_14 = '20260514070000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D100100^謝宜芳^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx.obx_5 = '45'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260514090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_2.obx_5 = '38'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260514090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='鹼性磷酸酶', cwe_3='LN')
        obx_3.obx_5 = '85'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260514090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='膽紅素(總)', cwe_3='LN')
        obx_4.obx_5 = '0.8'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '0.1-1.2'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260514090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2885-2', cwe_2='總蛋白', cwe_3='LN')
        obx_5.obx_5 = '7.2'
        obx_5.units = CWE(cwe_1='g/dL')
        obx_5.reference_range = '6.0-8.3'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260514090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='白蛋白', cwe_3='LN')
        obx_6.obx_5 = '4.1'
        obx_6.units = CWE(cwe_1='g/dL')
        obx_6.reference_range = '3.5-5.5'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260514090000'

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

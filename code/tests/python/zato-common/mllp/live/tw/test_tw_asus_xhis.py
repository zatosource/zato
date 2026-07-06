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

_md_path = md_path_for('tw', 'tw-asus-xhis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-asus-xhis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SKMH20260509073001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509073000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')
        pid.pid_13 = '^^PH^03-5731234~^^CP^0919876543'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G246801357^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.admit_date_time = '20260509073000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'
        in1.insureds_relationship_to_patient = CWE(cwe_1='蘇', cwe_2='志遠')
        in1.insureds_date_of_birth = 'Self'
        in1.insureds_address = XAD(xad_1='19720130')
        in1.assignment_of_benefits = CWE(cwe_1='新竹市東區光復路一段101號', cwe_3='新竹市', cwe_5='30013', cwe_6='TW')

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SKMH20260509090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')
        pid.pid_13 = '^^PH^03-5501234~^^CP^0935678901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'H258901346^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260509090000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260516140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SKMH20260516140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260516140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')
        pid.pid_13 = '^^PH^03-5731234~^^CP^0919876543'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G246801357^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.discharged_to_location = DLD(dld_1='9')
        pv1.account_status = CWE(cwe_1='20260516140000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='膽囊結石伴急性膽囊炎', cwe_3='ICD-10-CM')
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
    """ Based on live/tw/tw-asus-xhis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SKMH20260510100001'
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
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')
        pid.pid_13 = '^^PH^03-5501234~^^CP^0935678901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'H258901346^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')
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
    """ Based on live/tw/tw-asus-xhis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260511060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SKMH20260511060001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260511060000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')
        pid.pid_13 = '^^PH^03-5731234~^^CP^0919876543'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G246801357^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='外科病房', pl_2='502', pl_3='B', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.delete_account_date = '胃腸肝膽科^401^A^新光吳火獅紀念醫院'
        pv1.servicing_facility = CWE(cwe_1='20260511060000')

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SKMH20260509080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='ORD20260509030')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'N400100^護理師曾雅雯'
        orc.enterers_location = PL(pl_1='D400100', pl_2='彭瑞芳', pl_5='醫師')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='J01DD04', cwe_2='Ceftriaxone 2g', cwe_3='NHI')
        rxo.requested_give_amount_maximum = '2'
        rxo.requested_give_units = CWE(cwe_1='g')
        rxo.requested_dosage_form = CWE(cwe_1='IV', cwe_2='靜脈注射', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='Q12H')
        rxo.rxo_14 = 'D400100^彭瑞芳'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='靜脈注射', cwe_3='HL70162')

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD20260509031')
        orc_2.orc_7 = '^^^20260509080000^^R'
        orc_2.date_time_of_order_event = '20260509080000'
        orc_2.orc_10 = 'N400100^護理師曾雅雯'
        orc_2.enterers_location = PL(pl_1='D400100', pl_2='彭瑞芳', pl_5='醫師')

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='A03BA01', cwe_2='Atropine 0.5mg', cwe_3='NHI')
        rxo_2.requested_give_amount_maximum = '0.5'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.requested_dosage_form = CWE(cwe_1='IV', cwe_2='靜脈注射', cwe_3='HL70162')
        rxo_2.providers_administration_instructions = CWE(cwe_4='20260509', cwe_6='PRN')
        rxo_2.rxo_14 = 'D400100^彭瑞芳'

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='IV', cwe_2='靜脈注射', cwe_3='HL70162')

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SKMH20260509083001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509030')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509030')
        obr.universal_service_identifier = CWE(cwe_1='79103-8', cwe_2='腹部超音波', cwe_3='LN')
        obr.observation_date_time = '20260509083000'
        obr.obr_15 = 'D400100^彭瑞芳^^^醫師'
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
    """ Based on live/tw/tw-asus-xhis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260509110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509030')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='肝功能及發炎指標', cwe_3='LN')
        obr.observation_date_time = '20260509075000'
        obr.obr_14 = '20260509075000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D400100^彭瑞芳^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_2.obx_5 = '210'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='鹼性磷酸酶(ALP)', cwe_3='LN')
        obx_3.obx_5 = '320'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='膽紅素(總)', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '0.1-1.2'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1968-7', cwe_2='膽紅素(直接)', cwe_3='LN')
        obx_5.obx_5 = '2.5'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '0.0-0.3'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx_6.obx_5 = '15.8'
        obx_6.units = CWE(cwe_1='10*3/uL')
        obx_6.reference_range = '4.0-10.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1988-5', cwe_2='C反應蛋白', cwe_3='LN')
        obx_7.obx_5 = '85'
        obx_7.units = CWE(cwe_1='mg/L')
        obx_7.reference_range = '0.0-5.0'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509110000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260509140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509030')
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509030')
        obr.universal_service_identifier = CWE(cwe_1='79103-8', cwe_2='腹部超音波', cwe_3='LN')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_16 = 'D400100^彭瑞芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='79103-8', cwe_2='腹部超音波', cwe_3='LN')
        obx.obx_5 = '膽囊壁增厚(6mm), 膽囊內多發結石, 最大約1.5cm。膽總管輕度擴張(8mm)。肝臟實質回音略增, 餘無特殊。脾臟及雙腎正常。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

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
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0MDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWg6YOo6LaF'
            '6Z+z5rOi5aCx5ZGKIC0g6Ie65aSn6Yar6Zmi6Zu75p6X5YiG6ZmiKSBUagowIC0yMCBUZAoo6IaG5Zun5aOB5aKe5Y6aKDZtbSksIOiGh+WbiumFp+Wkmuecvue1kOedtikgVGoKMCAt'
            'MjAgVGQKKOacgOWkp+e0hDEuNWNtKSBUagowIC0yMCBUZAoo6IaG57i957Wh6Lyv5bqm5pO05byjKDhtbSkpIFRqCjAgLTIwIFRkCijogrboh4/lr6boqajlm57pn7PnlaXlop4pIFRq'
            'CjAgLTIwIFRkCijohL7oh4/lj4rpl5vojoTmraPluLgpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250'
            'IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAw'
            'MDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNzE2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNzgxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260509153001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')

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
        orc.orc_12 = 'D400200^廖明哲^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509040')
        obr.universal_service_identifier = CWE(cwe_1='53959-5', cwe_2='婦科檢驗', cwe_3='LN')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D400200^廖明哲^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='15067-2', cwe_2='FSH', cwe_3='LN')
        obx.obx_5 = '6.5'
        obx.units = CWE(cwe_1='mIU/mL')
        obx.reference_range = '3.5-12.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='14715-7', cwe_2='LH', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='mIU/mL')
        obx_2.reference_range = '2.4-12.6'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2243-4', cwe_2='Estradiol (E2)', cwe_3='LN')
        obx_3.obx_5 = '95'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '12.5-166'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2839-9', cwe_2='Progesterone', cwe_3='LN')
        obx_4.obx_5 = '0.8'
        obx_4.units = CWE(cwe_1='ng/mL')
        obx_4.reference_range = '0.2-1.5'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='19080-1', cwe_2='hCG定量', cwe_3='LN')
        obx_5.obx_5 = '<2'
        obx_5.units = CWE(cwe_1='mIU/mL')
        obx_5.reference_range = '0-5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509153000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'SKMH20260509085001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RX20260509030')
        orc.orc_7 = '^^^20260509085000^^R'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260509^^Q12H^5^Day'
        rxe.give_amount_minimum = 'J01DD04^Ceftriaxone 2g^NHI'
        rxe.give_amount_maximum = '2'
        rxe.give_units = CWE(cwe_1='g')
        rxe.give_strength = '2'
        rxe.give_strength_units = CWE(cwe_1='Vial')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='靜脈注射', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='RX20260509031')
        orc_2.orc_7 = '^^^20260509085000^^R'
        orc_2.date_time_of_order_event = '20260509085000'
        orc_2.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20260509^^TID^5^Day'
        rxe_2.give_amount_minimum = 'A02BC01^Omeprazole 40mg^NHI'
        rxe_2.give_amount_maximum = '40'
        rxe_2.give_units = CWE(cwe_1='mg')
        rxe_2.give_strength = '3'
        rxe_2.give_strength_units = CWE(cwe_1='Cap')

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='SCHEDULING')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SKMH20260510080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260512010')
        sch.sch_9 = '120'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^120^20260512080000^20260512100000'
        sch.sch_13 = 'D400100^彭瑞芳^^^醫師'
        sch.placer_contact_address = XAD(xad_3='PH', xad_4='03-5731234')
        sch.placer_contact_location = PL(pl_1='新竹市東區光復路一段101號', pl_3='新竹市', pl_5='30013', pl_6='TW')
        sch.filler_contact_person = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')
        pid.pid_13 = '^^CP^0919876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        ais.universal_service_identifier = CWE(cwe_1='手術室', cwe_2='OR-3', cwe_3='L')
        ais.start_date_time = '20260512080000'
        ais.start_date_time_offset = '120'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        aip.start_date_time_offset_units = CNE(cne_1='20260512080000')
        aip.duration = '120'
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
    """ Based on live/tw/tw-asus-xhis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260516160000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'SKMH20260516160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260516160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='胃腸肝膽科', pl_2='401', pl_3='A', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
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
        ft1.transaction_type = CWE(cwe_4='J01DD04', cwe_5='Ceftriaxone 2g', cwe_6='NHI')
        ft1.ft1_8 = '10'
        ft1.ft1_9 = '2'
        ft1.transaction_quantity = 'g'
        ft1.performed_by_code = XCN(xcn_1='K80.2', xcn_2='膽囊結石伴急性膽囊炎', xcn_3='ICD-10-CM')

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
        ft1_2.transaction_type = CWE(cwe_4='09002C', cwe_5='腹部超音波', cwe_6='NHI')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_9 = '1'
        ft1_2.transaction_quantity = 'EA'
        ft1_2.performed_by_code = XCN(xcn_1='K80.2', xcn_2='膽囊結石伴急性膽囊炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260512')
        ft1_3.transaction_batch_id = '20260512'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_4='62012B', cwe_5='腹腔鏡膽囊切除術', cwe_6='NHI')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_9 = '1'
        ft1_3.transaction_quantity = 'EA'
        ft1_3.performed_by_code = XCN(xcn_1='K80.2', xcn_2='膽囊結石伴急性膽囊炎', xcn_3='ICD-10-CM')

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
        ft1_4.performed_by_code = XCN(xcn_1='K80.2', xcn_2='膽囊結石伴急性膽囊炎', xcn_3='ICD-10-CM')

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260512150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SKMH20260512150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260512150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='外科病房', pl_2='502', pl_3='B', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='手術記錄', cwe_3='L')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20260512150000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        txa.transcription_date_time = '20260512150000'
        txa.originator_code_name = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')
        txa.parent_document_number = EI(ei_1='DOC20260512001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='28570-0', cwe_2='手術記錄', cwe_3='LN')
        obx.obx_5 = (
            '手術名稱: 腹腔鏡膽囊切除術\\.br\\手術日期: 2026/05/12\\.br\\麻醉: 全身麻醉\\.br\\術中所見: 膽囊壁充血水腫, 與大網膜輕度粘連, 膽囊內多發結石\\.br'
            '\\手術過程: 順利完成膽囊切除, 無膽管損傷。出血量約30mL\\.br\\術後診斷: 急性膽囊炎合併膽囊結石 (K80.2)\\.br\\主治醫師: 彭瑞芳'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512150000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260513090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260513090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='外科病房', pl_2='502', pl_3='B', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260513001')
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260513001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='術後肝功能追蹤', cwe_3='LN')
        obr.observation_date_time = '20260513070000'
        obr.obr_14 = '20260513070000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D400100^彭瑞芳^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260513090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260513090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='膽紅素(總)', cwe_3='LN')
        obx_3.obx_5 = '1.5'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.1-1.2'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260513090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx_4.obx_5 = '10.2'
        obx_4.units = CWE(cwe_1='10*3/uL')
        obx_4.reference_range = '4.0-10.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260513090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1988-5', cwe_2='C反應蛋白', cwe_3='LN')
        obx_5.obx_5 = '25'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '0.0-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260513090000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509074000'
        msh.message_type = MSG(msg_1='OML', msg_2='O33', msg_3='OML_O33')
        msh.message_control_id = 'SKMH20260509074001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')

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
        spm.specimen_risk_code = CWE(cwe_1='20260509074000')
        spm.specimen_collection_date_time = DR(dr_1='20260509074500')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='TUBE20260509030')
        sac.additive = CWE(cwe_1='BLD')

        # .. build the SPECIMEN_CONTAINER group ..
        specimen_container = OmlO33SpecimenContainer()
        specimen_container.sac = sac

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LAB20260509040')
        orc.orc_7 = '^^^20260509074000^^R'
        orc.date_time_of_order_event = '20260509074000'
        orc.orc_12 = 'D400200^廖明哲^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509040')
        obr.universal_service_identifier = CWE(cwe_1='53959-5', cwe_2='婦科檢驗', cwe_3='LN')
        obr.observation_date_time = '20260509074000'

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB20260509041')
        orc_2.orc_7 = '^^^20260509074000^^R'
        orc_2.date_time_of_order_event = '20260509074000'
        orc_2.orc_12 = 'D400200^廖明哲^^^醫師'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260509041')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr_2.observation_date_time = '20260509074000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='PATHOLOGY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260515100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260515100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='PATH20260515001')
        orc.orc_12 = 'D400200^廖明哲^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20260515001')
        obr.universal_service_identifier = CWE(cwe_1='10524-7', cwe_2='子宮頸細胞學檢查', cwe_3='LN')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '子宮頸分泌物^Cervical'
        obr.obr_16 = 'D400200^廖明哲^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='10524-7', cwe_2='子宮頸細胞學檢查', cwe_3='LN')
        obx.obx_5 = (
            '檢體適當性: 滿意。\\.br\\一般分類: 上皮細胞異常。\\.br\\描述: 低度鱗狀上皮內病變(LSIL)。\\.br\\建議: 6個月後追蹤抹片或HPV檢測。\\.br\\病理醫師: '
            '陳惠美醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260515100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='子宮頸抹片報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5a2Q5a6u6aCC'
            '5oq55Lmz5aCx5ZGKIC0g6Ie65aSn6Yar6Zmi6Zu66p6X5YiG6ZmiKSBUagowIC0yMCBUZAoo5qqh5pys6YGp55W25oCnOiDmu7/mhI8pIFRqCjAgLTIwIFRkCijkuIDoiKzliIbpoZ46'
            'IOS4iuear+e0sOiDnuexguW4uCkgVGoKMCAtMjAgVGQKKOaPj+i/sDog5L2O5bqm6bqf54uA5LiK55qu5YaF55eF6K6KIChMU0lMKSkgVGoKMCAtMjAgVGQKKOW7uuittjog5pyI5YCL'
            '5pyI5b6M6L+96Lmk5oq55Lmz5oiWSFBW5qqh5ris5L6LKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9u'
            'dCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAw'
            'MDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDY2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjczMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260515100000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260509152000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260509152001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400200', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='葉', xpn_2='佳琳', xpn_5='女士')
        pid.date_time_of_birth = '19880618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新竹縣竹北市光明六路88號', xad_3='新竹縣', xad_5='30266', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='婦產科門診', pl_2='診間08', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400200', xcn_2='廖明哲', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509041')
        orc.orc_12 = 'D400200^廖明哲^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509041')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D400200^廖明哲^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='紅血球計數', cwe_3='LN')
        obx_2.obx_5 = '4.15'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '3.80-5.10'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_3.obx_5 = '12.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='血比容', cwe_3='LN')
        obx_4.obx_5 = '38.5'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='血小板計數', cwe_3='LN')
        obx_5.obx_5 = '268'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509152000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='PATHOLOGY')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260516100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260516100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='外科病房', pl_2='502', pl_3='B', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20260516001')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='手術病理檢查', cwe_3='LN')
        obr.observation_date_time = '20260512120000'
        obr.obr_14 = '20260512120000'
        obr.obr_15 = '組織^Tissue'
        obr.obr_16 = 'D400100^彭瑞芳^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='手術病理檢查', cwe_3='LN')
        obx.obx_5 = (
            '檢體: 膽囊切除標本\\.br\\肉眼觀: 膽囊7.5x3.0cm, 壁厚5mm, 漿膜面充血。腔內含多發黃綠色結石\\.br\\鏡檢: 黏膜慢性發炎合併急性炎症反應, 肌層水腫, 漿'
            '膜下充血\\.br\\診斷: 急性膽囊炎合併慢性膽囊炎, 膽囊結石。無惡性細胞\\.br\\病理醫師: 陳惠美醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260516100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='手術病理報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5omL6KGT55eF'
            '55CG5aCx5ZGKIC0g6Ie65aSn6Yar6Zmi6Zu66p6X5YiG6ZmiKSBUagowIC0yMCBUZAoo5qqh5pysOiDohobm5aGK5YiH6Zmk5qiZ5pysKSBUagowIC0yMCBUZAoo6IaG5ZunNy41eDMu'
            'MGNtLCDlo4HljpU1bW0pIFRqCjAgLTIwIFRkCijogZTog5zmhKLmgKfnmLflkIjmgKXmgKfngonmgKflj43mh5MpIFRqCjAgLTIwIFRkCijogqTlsaTmsLTohq4sIOmFhiDohpzkuIvl'
            'hYXooYApIFRqCjAgLTIwIFRkCijoo7rmlrfml6Xmgqfmgqfph4Y6IOeEoeaDoeaAp+e0sOiDnikgVGoKMCAtMjAgVGQKKOeXheeQhuirlOW4qzog5by16oOg55C06Yar5birKSBUagpF'
            'VAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAw'
            'MDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDc2NiAw'
            'MDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjgzMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260516100000'

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
    """ Based on live/tw/tw-asus-xhis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ASUS-xHIS')
        msh.sending_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='新光吳火獅紀念醫院')
        msh.date_time_of_message = '20260515160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SKMH20260515160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT400100', cx_4='新光吳火獅紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='蘇', xpn_2='志遠', xpn_5='先生')
        pid.date_time_of_birth = '19720130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新竹市東區光復路一段101號', xad_3='新竹市', xad_5='30013', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='外科病房', pl_2='502', pl_3='B', pl_4='新光吳火獅紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D400100', xcn_2='彭瑞芳', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260515001')
        orc.orc_12 = 'D400100^彭瑞芳^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260515001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='出院前檢驗', cwe_3='LN')
        obr.observation_date_time = '20260515070000'
        obr.obr_14 = '20260515070000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D400100^彭瑞芳^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx.obx_5 = '42'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260515160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_2.obx_5 = '35'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260515160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='膽紅素(總)', cwe_3='LN')
        obx_3.obx_5 = '0.9'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.1-1.2'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260515160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx_4.obx_5 = '7.8'
        obx_4.units = CWE(cwe_1='10*3/uL')
        obx_4.reference_range = '4.0-10.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260515160000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1988-5', cwe_2='C反應蛋白', cwe_3='LN')
        obx_5.obx_5 = '8'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '0.0-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260515160000'

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

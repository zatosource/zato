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
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, DFT_P03, MDM_T02, OML_O33, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, FT1, IN1, MSH, OBR, OBX, ORC, PID, PV1, RGS, RXE, RXR, SAC, SCH, SPM, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-syspower-exapacs.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CGMH20260509070001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')
        pid.pid_13 = '^^PH^03-3971234~^^CP^0938912345'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E235891467^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.admit_date_time = '20260509070000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'
        in1.insureds_relationship_to_patient = CWE(cwe_1='丁', cwe_2='漢威')
        in1.insureds_date_of_birth = 'Self'
        in1.insureds_address = XAD(xad_1='19600725')
        in1.assignment_of_benefits = CWE(cwe_1='桃園市龜山區復興一路105號', cwe_3='桃園市', cwe_5='33374', cwe_6='TW')

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CGMH20260509090001'
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
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')
        pid.pid_13 = '^^PH^02-27901234~^^CP^0942678901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F346902578^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260518110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CGMH20260518110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260518110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')
        pid.pid_13 = '^^PH^03-3971234~^^CP^0938912345'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E235891467^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.discharged_to_location = DLD(dld_1='9')
        pv1.account_status = CWE(cwe_1='20260518110000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M17.1', cwe_2='原發性單側膝關節骨關節炎', cwe_3='ICD-10-CM')
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CGMH20260510080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260510080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')
        pid.pid_13 = '^^PH^02-27901234~^^CP^0942678901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F346902578^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260510080000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509074000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGMH20260509074001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509020')
        orc.orc_7 = '^^^20260509074000^^R'
        orc.date_time_of_order_event = '20260509074000'
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509020')
        obr.universal_service_identifier = CWE(cwe_1='37620-2', cwe_2='雙膝X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509074000'
        obr.obr_15 = 'D300100^賴佳蓉^^^醫師'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGMH20260509100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509021')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509021')
        obr.universal_service_identifier = CWE(cwe_1='24566-5', cwe_2='腹部電腦斷層(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'D300200^呂彥霖^^^醫師'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260509113001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509020')
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509020')
        obr.universal_service_identifier = CWE(cwe_1='37620-2', cwe_2='雙膝X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509074000'
        obr.obr_14 = '20260509074000'
        obr.obr_16 = 'D300100^賴佳蓉^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='37620-2', cwe_2='雙膝X光正側位', cwe_3='LN')
        obx.obx_5 = '雙膝正側位X光: 右膝關節間隙明顯狹窄(Kellgren-Lawrence Grade III), 關節面硬化及邊緣骨贅形成。左膝輕度退化性變化(Grade II)。無骨折或脫位。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='膝關節X光報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0MDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6Iag6Zec6IqC'
            'WOWFieioseWHuuloiuWRiiAtIOmVt+W6mue0gOW/tee4veWkp+mGq+mZoikgVGoKMCAtMjAgVGQKKOWPs+iGneaal+eviue+qemWk+mam+aYjumhr+eLueeptikgVGoKMCAtMjAgVGQK'
            'KEtlbGxncmVuLUxhd3JlbmNlIEdyYWRlIElJSSkgVGoKMCAtMjAgVGQKKOmXnOeviumdoueiuOWMluWPiumCiue3s+mqqOi0hSkgVGoKMCAtMjAgVGQKKOW3puiGneiyu+W6pumAgOWM'
            'luaAp+WPiOWMliAoR3JhZGUgSUkpKSBUagowIC0yMCBUZAoo54Sh6aqo5oqY5oiW6ISr5L2NKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1'
            'YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAw'
            'MDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDcxNiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3Rh'
            'cnR4cmVmCjc4MQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509113000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260509163001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509021')
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509021')
        obr.universal_service_identifier = CWE(cwe_1='24566-5', cwe_2='腹部電腦斷層(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_14 = '20260509100000'
        obr.obr_16 = 'D300200^呂彥霖^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24566-5', cwe_2='腹部電腦斷層', cwe_3='LN')
        obx.obx_5 = '肝臟大小正常, 密度均勻, 無局灶性病變。膽囊及膽管未見異常。胰臟、脾臟、雙腎正常。腹主動脈及腸繫膜血管未見異常。無腹水或腹腔淋巴結腫大。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='腹部CT報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWg6YOoQ1Tl'
            'oLHlkYogLSDplbflurfntIDlv7XnuL7phKvpmaIpIFRqCjAgLTIwIFRkCijogrboh4/lpKflsI/mraPluLgsIOWvhm3luqblnYfli7spIFRqCjAgLTIwIFRkCijohb3lm4rlj4rohb3n'
            'rqHmnKrlgYnnmbDluLgpIFRqCjAgLTIwIFRkCijohbDoh5/jgIHohb7oh5/jgIHpm5nojoHmraPluLgpIFRqCjAgLTIwIFRkCijnhKHohbnmsLTmiJbohbnohJTmt4vlt7TntZDohabm'
            'lLApIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2'
            'CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAw'
            'MDAwNjY2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNzMxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509163000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260510090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGMH20260510090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260510001')
        orc.orc_7 = '^^^20260510090000^^R'
        orc.date_time_of_order_event = '20260510090000'
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510001')
        obr.universal_service_identifier = CWE(cwe_1='24969-9', cwe_2='腰椎核磁共振(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260510090000'
        obr.obr_15 = 'D300100^賴佳蓉^^^醫師'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260511150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260511150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260510001')
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510001')
        obr.universal_service_identifier = CWE(cwe_1='24969-9', cwe_2='腰椎核磁共振(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260510090000'
        obr.obr_14 = '20260510090000'
        obr.obr_16 = 'D300100^賴佳蓉^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24969-9', cwe_2='腰椎核磁共振', cwe_3='LN')
        obx.obx_5 = 'L4/L5椎間盤突出, 壓迫左側神經根。L3/L4椎間盤輕度膨出。脊椎管輕度狹窄(L4/L5)。脊髓圓錐正常。椎體骨髓信號正常, 無壓迫性骨折。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='腰椎MRI報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWw5qSOMVJJ'
            '5aCx5ZGKIC0g6ZW35bq557SA5b+157i96Yar6ZmiKSBUagowIC0yMCBUZAooTDQvTDXmpI7plpPnm6Tnqoflh7osIOWjk+i/q+W3puWBtOelnue2k+aguCkgVGoKMCAtMjAgVGQKKEwz'
            'L0w05qSO6ZaT55uk6Lyy5bqm6Iao5Ye6KSBUagowIC0yMCBUZAoo6ISK5qSO566h6Lyy5bqm54uH56qqIChMNC9MNSkpIFRqCjAgLTIwIFRkCijohIrpq5Tlnoto6IyQ5q2j5bi4KSBU'
            'agowIC0yMCBUZAoo5qSO6auU6aqo6auT5L+h6Jmf5q2j5bi4LCDnhKHlo5Pov6vmgKfpqqjmipgpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAov'
            'U3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4'
            'IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNjY2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+Pgpz'
            'dGFydHhyZWYKNzMxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260511150000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGMH20260509110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509022')
        orc.orc_7 = '^^^20260509110000^^R'
        orc.date_time_of_order_event = '20260509110000'
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509022')
        obr.universal_service_identifier = CWE(cwe_1='24627-5', cwe_2='胸部電腦斷層(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509110000'
        obr.obr_15 = 'D300200^呂彥霖^^^醫師'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260510160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260510160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509022')
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509022')
        obr.universal_service_identifier = CWE(cwe_1='24627-5', cwe_2='胸部電腦斷層(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509110000'
        obr.obr_14 = '20260509110000'
        obr.obr_16 = 'D300200^呂彥霖^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24627-5', cwe_2='胸部電腦斷層', cwe_3='LN')
        obx.obx_5 = '雙肺實質清晰, 無結節或腫塊。氣管及支氣管通暢。縱膈腔無淋巴結腫大。心臟大小正常。胸膜無增厚或積液。胸椎骨質正常。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='胸部CT報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzMDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IO46YOoQ1Tl'
            'oLHlkYogLSDplbflurfntIDlv7XnuL7phKvpmaIpIFRqCjAgLTIwIFRkCijpm5nogobogrLmuIXmmrAsIOeEoee1kOeviuaIluiFq+WhnCkgVGoKMCAtMjAgVGQKKOawo+euoeWPiuaU'
            'r+awo+euoemAmuaatCkgVGoKMCAtMjAgVGQKKOe4ruePg+iFlOeEoeWkp+WPiua3i+W3tCkgVGoKMCAtMjAgVGQKKOiDuOiGnOeEoeWinuWOmuaIluepjea2sikgVGoKRVQKZW5kc3Ry'
            'ZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMjY2IDAwMDAwIG4gCjAwMDAwMDA2MTYgMDAwMDAgbiAK'
            'dHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo2ODEKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510160000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CGMH20260509080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RX20260509020')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260509^^TID^7^Day'
        rxe.give_amount_minimum = 'M01AE01^Ibuprofen 400mg^NHI'
        rxe.give_amount_maximum = '400'
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
        orc_2.placer_order_number = EI(ei_1='RX20260509021')
        orc_2.orc_7 = '^^^20260509080000^^R'
        orc_2.date_time_of_order_event = '20260509080000'
        orc_2.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20260509^^BID^7^Day'
        rxe_2.give_amount_minimum = 'M03BX02^Tizanidine 2mg^NHI'
        rxe_2.give_amount_maximum = '2'
        rxe_2.give_units = CWE(cwe_1='mg')
        rxe_2.give_strength = '2'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='SCHEDULING')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CGMH20260509150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260512001')
        sch.sch_9 = '45'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^45^20260512100000^20260512104500'
        sch.sch_13 = 'D300200^呂彥霖^^^醫師'
        sch.placer_contact_address = XAD(xad_3='PH', xad_4='03-3281200')
        sch.placer_contact_location = PL(pl_1='復興街5號', pl_3='桃園市', pl_5='33305', pl_6='TW')
        sch.filler_contact_person = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')
        pid.pid_13 = '^^CP^0942678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        ais.universal_service_identifier = CWE(cwe_1='MRI檢查室', cwe_2='MRI Suite', cwe_3='L')
        ais.start_date_time = '20260512100000'
        ais.start_date_time_offset = '45'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')
        aip.start_date_time_offset_units = CNE(cne_1='20260512100000')
        aip.duration = '45'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260518130000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CGMH20260518130001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260518130000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260509')
        ft1.transaction_batch_id = '20260518'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_4='09005C', cwe_5='雙膝X光', cwe_6='NHI')
        ft1.ft1_8 = '1'
        ft1.ft1_9 = '1'
        ft1.transaction_quantity = 'EA'
        ft1.performed_by_code = XCN(xcn_1='M17.1', xcn_2='膝關節骨關節炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260509')
        ft1_2.transaction_batch_id = '20260518'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_4='33085B', cwe_5='腰椎MRI', cwe_6='NHI')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_9 = '1'
        ft1_2.transaction_quantity = 'EA'
        ft1_2.performed_by_code = XCN(xcn_1='M17.1', xcn_2='膝關節骨關節炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260509')
        ft1_3.transaction_batch_id = '20260518'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_4='M01AE01', cwe_5='Ibuprofen 400mg', cwe_6='NHI')
        ft1_3.ft1_8 = '21'
        ft1_3.ft1_9 = '400'
        ft1_3.transaction_quantity = 'mg'
        ft1_3.performed_by_code = XCN(xcn_1='M17.1', xcn_2='膝關節骨關節炎', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build FT1 ..
        ft1_4 = FT1()
        ft1_4.set_id_ft1 = '4'
        ft1_4.transaction_id = CX(cx_1='20260509')
        ft1_4.transaction_batch_id = '20260518'
        ft1_4.transaction_date = DR(dr_1='CG')
        ft1_4.transaction_posting_date = 'D'
        ft1_4.transaction_type = CWE(cwe_4='00201A', cwe_5='住院診察費', cwe_6='NHI')
        ft1_4.ft1_8 = '10'
        ft1_4.ft1_9 = '1'
        ft1_4.transaction_quantity = 'EA'
        ft1_4.performed_by_code = XCN(xcn_1='M17.1', xcn_2='膝關節骨關節炎', xcn_3='ICD-10-CM')

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CGMH20260511160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260511160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='放射報告', cwe_3='L')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20260511160000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')
        txa.transcription_date_time = '20260511160000'
        txa.originator_code_name = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')
        txa.parent_document_number = EI(ei_1='DOC20260511001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18726-0', cwe_2='放射科報告', cwe_3='LN')
        obx.obx_5 = (
            '檢查: 腰椎核磁共振(含顯影劑)\\.br\\臨床資訊: 下背痛合併左下肢麻木\\.br\\影像所見: L4/L5椎間盤突出壓迫左側L5神經根\\.br\\結論: 建議神經外科會診評'
            '估\\.br\\報告醫師: 呂彥霖'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511160000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGMH20260510100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260510010')
        orc.orc_7 = '^^^20260510100000^^R'
        orc.date_time_of_order_event = '20260510100000'
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510010')
        obr.universal_service_identifier = CWE(cwe_1='38269-7', cwe_2='雙能量X光骨密度檢查', cwe_3='LN')
        obr.observation_date_time = '20260510100000'
        obr.obr_15 = 'D300200^呂彥霖^^^醫師'
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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260511100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260511100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260510010')
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510010')
        obr.universal_service_identifier = CWE(cwe_1='38269-7', cwe_2='雙能量X光骨密度檢查', cwe_3='LN')
        obr.observation_date_time = '20260510100000'
        obr.obr_14 = '20260510100000'
        obr.obr_16 = 'D300200^呂彥霖^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='38265-5', cwe_2='腰椎BMD', cwe_3='LN')
        obx.obx_5 = '1.05'
        obx.units = CWE(cwe_1='g/cm2')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='38264-8', cwe_2='腰椎T-score', cwe_3='LN')
        obx_2.obx_5 = '-0.8'
        obx_2.reference_range = '>-1.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260511100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='38267-1', cwe_2='股骨頸BMD', cwe_3='LN')
        obx_3.obx_5 = '0.92'
        obx_3.units = CWE(cwe_1='g/cm2')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260511100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='38266-3', cwe_2='股骨頸T-score', cwe_3='LN')
        obx_4.obx_5 = '-1.2'
        obx_4.reference_range = '>-1.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260511100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='38269-7', cwe_2='骨密度結論', cwe_3='LN')
        obx_5.obx_5 = '腰椎BMD正常。左股骨頸T-score -1.2, 符合骨量減少(osteopenia)標準。建議補充鈣質及維生素D, 6個月後追蹤。'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260511100000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='OML', msg_2='O33', msg_3='OML_O33')
        msh.message_control_id = 'CGMH20260512080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300100', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='丁', xpn_2='漢威', xpn_5='先生')
        pid.date_time_of_birth = '19600725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='桃園市龜山區復興一路105號', xad_3='桃園市', xad_5='33374', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='骨科病房', pl_2='601', pl_3='B', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300100', xcn_2='賴佳蓉', xcn_5='醫師')

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
        spm.specimen_risk_code = CWE(cwe_1='20260512080000')
        spm.specimen_collection_date_time = DR(dr_1='20260512080500')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='TUBE20260512001')
        sac.additive = CWE(cwe_1='BLD')

        # .. build the SPECIMEN_CONTAINER group ..
        specimen_container = OmlO33SpecimenContainer()
        specimen_container.sac = sac

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LAB20260512001')
        orc.orc_7 = '^^^20260512080000^^R'
        orc.date_time_of_order_event = '20260512080000'
        orc.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260512001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260512080000'

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB20260512002')
        orc_2.orc_7 = '^^^20260512080000^^R'
        orc_2.date_time_of_order_event = '20260512080000'
        orc_2.orc_12 = 'D300100^賴佳蓉^^^醫師'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260512002')
        obr_2.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obr_2.observation_date_time = '20260512080000'

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
    """ Based on live/tw/tw-syspower-exapacs.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ExaPACS')
        msh.sending_facility = HD(hd_1='長庚紀念醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='長庚紀念醫院')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CGMH20260512140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT300200', cx_4='長庚紀念醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='馮', xpn_2='琬婷', xpn_5='女士')
        pid.date_time_of_birth = '19851203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='台北市內湖區成功路四段61號', xad_3='台北市', xad_5='11472', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間03', pl_4='長庚紀念醫院')
        pv1.attending_doctor = XCN(xcn_1='D300200', xcn_2='呂彥霖', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260512001')
        orc.orc_12 = 'D300200^呂彥霖^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260512001')
        obr.universal_service_identifier = CWE(cwe_1='24606-9', cwe_2='乳房攝影', cwe_3='LN')
        obr.observation_date_time = '20260512100000'
        obr.obr_14 = '20260512100000'
        obr.obr_16 = 'D300200^呂彥霖^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24606-9', cwe_2='乳房攝影', cwe_3='LN')
        obx.obx_5 = '雙側乳房攝影: 乳腺組織密度ACR-C (heterogeneously dense)。雙側無明顯腫塊、鈣化或結構異常。BI-RADS分類: 1 (陰性, 正常)。建議每年常規追蹤。'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='乳房攝影報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5Lmz5oi/5pSd'
            '5b2x5aCx5ZGKIC0g6ZW35bq557SA5b+157i96Yar6ZmiKSBUagowIC0yMCBUZAoo5Lmz6IW6576M57mUWC3mt77lkIjlr4bpsqYgKEFDUi1DKSkgVGoKMCAtMjAgVGQKKOmbmeWBtOeE'
            'oeaYjumhr+iFs+WhnOOAgemIo+WMluaIluezh+ani+eVsOW4uCkgVGoKMCAtMjAgVGQKKEJJLVJBRFPliIbpoZ46IDEgKOmZsOaApywg5q2j5bi4KSkgVGoKMCAtMjAgVGQKKOW7uuit'
            't+avj+W5tOW4uOimj+i/vei5pCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+'
            'PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAw'
            'MjY2IDAwMDAwIG4gCjAwMDAwMDA2NjYgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo3MzEKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260512140000'

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

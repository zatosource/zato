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

_md_path = md_path_for('tw', 'tw-iisi-ipacs.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509071000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TCVGH20260509071001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509071000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')
        pid.pid_13 = '^^PH^04-22471234~^^CP^0926543210'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'I259346781^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.admit_date_time = '20260509071000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI001')
        in1.insurance_company_id = CX(cx_1='BNHI')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insurance_company_address = XAD(xad_1='濟南路一段4-1號', xad_3='台北市', xad_5='10041', xad_6='TW')
        in1.in1_7 = '02-21912006'
        in1.insureds_relationship_to_patient = CWE(cwe_1='江', cwe_2='柏翰')
        in1.insureds_date_of_birth = 'Self'
        in1.insureds_address = XAD(xad_1='19650512')
        in1.assignment_of_benefits = CWE(cwe_1='文心路四段698號', cwe_3='台中市', cwe_5='40652', cwe_6='TW')

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'TCVGH20260509085001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509085000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500200', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='洪', xpn_2='詩涵', xpn_5='女士')
        pid.date_time_of_birth = '19930328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='美村路一段200號', xad_3='台中市', xad_5='40356', xad_6='TW')
        pid.pid_13 = '^^PH^04-23721234~^^CP^0958234567'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'J364257892^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間02', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500200', xcn_2='林宗賢', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260509085000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260517100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'TCVGH20260517100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260517100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')
        pid.pid_13 = '^^PH^04-22471234~^^CP^0926543210'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'I259346781^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')
        pv1.discharged_to_location = DLD(dld_1='9')
        pv1.account_status = CWE(cwe_1='20260517100000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.5', cwe_2='腦梗塞, 大腦動脈阻塞', cwe_3='ICD-10-CM')
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260510090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'TCVGH20260510090001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260510090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500200', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='洪', xpn_2='詩涵', xpn_5='女士')
        pid.date_time_of_birth = '19930328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='美村路一段200號', xad_3='台中市', xad_5='40356', xad_6='TW')
        pid.pid_13 = '^^PH^04-23721234~^^CP^0958234567'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = 'J364257892^^^ROC^NNT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間02', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500200', xcn_2='林宗賢', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509002')
        pv1.admit_date_time = '20260510090000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509072000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TCVGH20260509072001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509040')
        orc.orc_7 = '^^^20260509072000^^R'
        orc.date_time_of_order_event = '20260509072000'
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509040')
        obr.universal_service_identifier = CWE(cwe_1='30799-1', cwe_2='腦部電腦斷層(無顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509072000'
        obr.obr_15 = 'D500100^曾俊凱^^^醫師'
        obr.result_status = '^STAT'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260509100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509040')
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509040')
        obr.universal_service_identifier = CWE(cwe_1='30799-1', cwe_2='腦部電腦斷層(無顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509072000'
        obr.obr_14 = '20260509072000'
        obr.obr_16 = 'D500100^曾俊凱^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='30799-1', cwe_2='腦部電腦斷層', cwe_3='LN')
        obx.obx_5 = '右側大腦中動脈供血區域見低密度影, 考慮急性腦梗塞。左側大腦半球未見異常。腦室系統大小正常。中線結構無偏移。顱骨完整。報告醫師: 徐文芳醫師'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='腦部CT報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0MDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWm6YOoQ1Tl'
            'oLHlkYogLSDppqzlgbfntIDlv7XphKvpmaIpIFRqCjAgLTIwIFRkCijlj7PlgbTlpKfohablpKfli5XohIjkvpvooYDljYDln5/kvY7lr4bkuqTlvbEpIFRqCjAgLTIwIFRkCijogIPm'
            'ha7mgKXmgKfohablsq3oganpvb0pIFRqCjAgLTIwIFRkCijlt6blgbTlpKfohablj4rljYrlvbjmnKrlgYvnmbDluLgpIFRqCjAgLTIwIFRkCijohablrqTns7vntbHlpKflsI/mraPl'
            'uLgpIFRqCjAgLTIwIFRkCijkuK3nt5rntZDmp4vnhKHlgY/np7spIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jh'
            'c2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAx'
            'MTUgMDAwMDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNzE2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNzgxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509100000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TCVGH20260509110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509041')
        orc.orc_7 = '^^^20260509110000^^R'
        orc.date_time_of_order_event = '20260509110000'
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509041')
        obr.universal_service_identifier = CWE(cwe_1='24590-5', cwe_2='腦部核磁共振(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509110000'
        obr.obr_15 = 'D500100^曾俊凱^^^醫師'
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260510140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260510140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509041')
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509041')
        obr.universal_service_identifier = CWE(cwe_1='24590-5', cwe_2='腦部核磁共振(含顯影劑)', cwe_3='LN')
        obr.observation_date_time = '20260509110000'
        obr.obr_14 = '20260509110000'
        obr.obr_16 = 'D500100^曾俊凱^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24590-5', cwe_2='腦部核磁共振', cwe_3='LN')
        obx.obx_5 = (
            'DWI序列: 右側大腦中動脈供血區域見擴散受限高信號, 對應ADC圖呈低信號, 符合急性腦梗塞。梗塞範圍約3.5x2.0cm。MRA: 右側大腦中動脈M1段重度狹窄。其餘腦'
            '實質及腦室系統正常。報告醫師: 徐文芳醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='腦部MRI報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWm6YOOMVJJ'
            '5aCx5ZGKIC0g6aas5YG557SA5b+157i96Yar6ZmiKSBUagowIC0yMCBUZAooRFdJOiDlj7PlgbTlpKfohablpKfli5XohIjkvpvooYDljYDln5/mk7TmlaPli5fpmZDpq5jkv6Hmj50p'
            'IFRqCjAgLTIwIFRkCijogIPmha7mgKXmgKfohablsq3oganpvb0sIOais+Whi+evhOWbvjMuNXgyLjBjbSkgVGoKMCAtMjAgVGQKKE1SQTog5Y+z5YGn5aSn6IWm5Lit5YuV6ISITTHm'
            'rrXph43luqbni7nnqqopIFRqCjAgLTIwIFRkCijlhbblppnohablr6boqKrlj4rohablrqTns7vntbHmraPluLgpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlw'
            'ZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAow'
            'MDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNzY2IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAx'
            'IDAgUgo+PgpzdGFydHhyZWYKODMxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260510140000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TCVGH20260510080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.orc_7 = '^^^20260510080000^^R'
        orc.date_time_of_order_event = '20260510080000'
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510010')
        obr.universal_service_identifier = CWE(cwe_1='93880-2', cwe_2='頸動脈超音波', cwe_3='LN')
        obr.observation_date_time = '20260510080000'
        obr.obr_15 = 'D500100^曾俊凱^^^醫師'
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260510170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260510170001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260510010')
        obr.universal_service_identifier = CWE(cwe_1='93880-2', cwe_2='頸動脈超音波', cwe_3='LN')
        obr.observation_date_time = '20260510080000'
        obr.obr_14 = '20260510080000'
        obr.obr_16 = 'D500100^曾俊凱^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93880-2', cwe_2='頸動脈超音波', cwe_3='LN')
        obx.obx_5 = (
            '右側總頸動脈IMT 1.2mm (增厚), 右側內頸動脈起始處見混合型斑塊, 狹窄約40%。左側總頸動脈IMT 0.8mm, 左側內頸動脈未見明顯狹窄。雙側椎動脈血流方向正常'
            '。報告醫師: 徐文芳醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='頸動脈超音波報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0MDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6aCP5YuV6ISI'
            '6LaF6Z+z5rOi5aCx5ZGKIC0g6aas5YG557SA5b+157i96Yar6ZmiKSBUagowIC0yMCBUZAoo5Y+z5YGT57i957i96ISI5YuV6ISISU1UIDEuMm1tICjlop7ljoopKSBUagowIC0yMCBU'
            'ZAoo5Y+z5YGT5YWn6aCP5YuV6ISI5re35ZCI5Z6L5paR5aGKLCDni7nnqqo0MCUpIFRqCjAgLTIwIFRkCijlt6blgbTnt73poLjli5XohIhJTVQgMC44bW0pIFRqCjAgLTIwIFRkCijl'
            't6blgbTlhafpoLjli5XohIjmnKrlgYvmk47mmI7ni7nnqqopIFRqCjAgLTIwIFRkCijpm5nlgbTmpI7li5XohIjooYDmtYHmlrnlkJHmraPluLgpIFRqCkVUCmVuZHN0cmVhbQplbmRv'
            'YmoKNSAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAw'
            'MDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDI2NiAwMDAwMCBuIAowMDAwMDAwNzE2IDAwMDAwIG4gCnRyYWlsZXIK'
            'PDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNzgxCiUlRU9GCg=='
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TCVGH20260509093001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500200', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='洪', xpn_2='詩涵', xpn_5='女士')
        pid.date_time_of_birth = '19930328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='美村路一段200號', xad_3='台中市', xad_5='40356', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間02', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500200', xcn_2='林宗賢', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509050')
        orc.orc_7 = '^^^20260509093000^^R'
        orc.date_time_of_order_event = '20260509093000'
        orc.orc_12 = 'D500200^林宗賢^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509050')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509093000'
        obr.obr_15 = 'D500200^林宗賢^^^醫師'
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260509150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500200', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='洪', xpn_2='詩涵', xpn_5='女士')
        pid.date_time_of_birth = '19930328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='美村路一段200號', xad_3='台中市', xad_5='40356', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間02', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500200', xcn_2='林宗賢', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260509050')
        orc.orc_12 = 'D500200^林宗賢^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260509050')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obr.observation_date_time = '20260509093000'
        obr.obr_14 = '20260509093000'
        obr.obr_16 = 'D500200^林宗賢^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71046-1', cwe_2='胸部X光正側位', cwe_3='LN')
        obx.obx_5 = '兩側肺野清晰, 無浸潤或結節。心臟大小正常(心胸比<0.5)。縱膈腔無異常。肋骨膈角銳利。骨骼結構正常。報告醫師: 徐文芳醫師'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

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
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IO46YOoWOWF'
            'ieioseWHuuloiuWRiiAtIOmppuWBt+e0gOW/temdoumGq+mZoikgVGoKMCAtMjAgVGQKKOWFqeWBtOiCuuW3pemHjuW4uCwg5peg5rW45r2k5oiW57WQ56+AKSBUagowIC0yMCBUZAoo'
            '5b+D6Ie95aSn5bCP5q2j5bi4KSBUagowIC0yMCBUZAoo6IKL6aqo6IaI6KeS6Yql5YipKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5'
            'cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAw'
            'MCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDU2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4'
            'cmVmCjYzMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509075000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'TCVGH20260509075001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RX20260509040')
        orc.orc_7 = '^^^20260509075000^^R'
        orc.date_time_of_order_event = '20260509075000'
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260509^^QD^90^Day'
        rxe.give_amount_minimum = 'B01AC06^Aspirin 100mg^NHI'
        rxe.give_amount_maximum = '100'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_strength = '1'
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
        orc_2.placer_order_number = EI(ei_1='RX20260509041')
        orc_2.orc_7 = '^^^20260509075000^^R'
        orc_2.date_time_of_order_event = '20260509075000'
        orc_2.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20260509^^QD^90^Day'
        rxe_2.give_amount_minimum = 'B01AC04^Clopidogrel 75mg^NHI'
        rxe_2.give_amount_maximum = '75'
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

        # .. build ORC ..
        orc_3 = ORC()
        orc_3.order_control = 'NW'
        orc_3.placer_order_number = EI(ei_1='RX20260509042')
        orc_3.orc_7 = '^^^20260509075000^^R'
        orc_3.date_time_of_order_event = '20260509075000'
        orc_3.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build RXE ..
        rxe_3 = RXE()
        rxe_3.rxe_1 = '^^^20260509^^QD^90^Day'
        rxe_3.give_amount_minimum = 'C10AA01^Simvastatin 40mg^NHI'
        rxe_3.give_amount_maximum = '40'
        rxe_3.give_units = CWE(cwe_1='mg')
        rxe_3.give_strength = '1'
        rxe_3.give_strength_units = CWE(cwe_1='Tab')

        # .. build RXR ..
        rxr_3 = RXR()
        rxr_3.route = CWE(cwe_1='PO', cwe_2='口服', cwe_3='HL70162')

        # .. build the ORDER group ..
        order_3 = RdeO11Order()
        order_3.orc = orc_3
        order_3.rxe = rxe_3
        order_3.rxr = rxr_3

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2, order_3]

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='SCHEDULING')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260517110000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'TCVGH20260517110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260524001')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^20^20260524090000^20260524092000'
        sch.sch_13 = 'D500100^曾俊凱^^^醫師'
        sch.placer_contact_address = XAD(xad_3='PH', xad_4='04-22471234')
        sch.placer_contact_location = PL(pl_1='文心路四段698號', pl_3='台中市', pl_5='40652', pl_6='TW')
        sch.filler_contact_person = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')
        pid.pid_13 = '^^CP^0926543210'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='神經內科門診', pl_2='診間06', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        ais.universal_service_identifier = CWE(cwe_1='神經內科門診', cwe_2='Neurology', cwe_3='L')
        ais.start_date_time = '20260524090000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        aip.start_date_time_offset_units = CNE(cne_1='20260524090000')
        aip.duration = '20'
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260517120000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'TCVGH20260517120001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260517120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260509')
        ft1.transaction_batch_id = '20260517'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_4='18003C', cwe_5='腦部CT', cwe_6='NHI')
        ft1.ft1_8 = '1'
        ft1.ft1_9 = '1'
        ft1.transaction_quantity = 'EA'
        ft1.performed_by_code = XCN(xcn_1='I63.5', xcn_2='腦梗塞', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260509')
        ft1_2.transaction_batch_id = '20260517'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_4='33085B', cwe_5='腦部MRI', cwe_6='NHI')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_9 = '1'
        ft1_2.transaction_quantity = 'EA'
        ft1_2.performed_by_code = XCN(xcn_1='I63.5', xcn_2='腦梗塞', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260509')
        ft1_3.transaction_batch_id = '20260517'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_4='18007C', cwe_5='頸動脈超音波', cwe_6='NHI')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_9 = '1'
        ft1_3.transaction_quantity = 'EA'
        ft1_3.performed_by_code = XCN(xcn_1='I63.5', xcn_2='腦梗塞', xcn_3='ICD-10-CM')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build FT1 ..
        ft1_4 = FT1()
        ft1_4.set_id_ft1 = '4'
        ft1_4.transaction_id = CX(cx_1='20260509')
        ft1_4.transaction_batch_id = '20260517'
        ft1_4.transaction_date = DR(dr_1='CG')
        ft1_4.transaction_posting_date = 'D'
        ft1_4.transaction_type = CWE(cwe_4='00201A', cwe_5='住院診察費', cwe_6='NHI')
        ft1_4.ft1_8 = '9'
        ft1_4.ft1_9 = '1'
        ft1_4.transaction_quantity = 'EA'
        ft1_4.performed_by_code = XCN(xcn_1='I63.5', xcn_2='腦梗塞', xcn_3='ICD-10-CM')

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='EMR-EXCHANGE')
        msh.receiving_facility = HD(hd_1='MOHW-EMR')
        msh.date_time_of_message = '20260517130000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'TCVGH20260517130001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260517130000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        pv1.admitting_doctor = XCN(xcn_1='VN20260509001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='出院摘要', cwe_3='L')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20260517130000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        txa.transcription_date_time = '20260517130000'
        txa.originator_code_name = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')
        txa.parent_document_number = EI(ei_1='DOC20260517001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='出院摘要', cwe_3='LN')
        obx.obx_5 = (
            '入院日期: 2026/05/09\\.br\\主訴: 突發性左側肢體無力及言語不清\\.br\\診斷: 右側大腦中動脈區域急性腦梗塞 (I63.5)\\.br\\影像: 腦部CT見右側MCA區低密'
            '度影, MRI確認急性梗塞3.5x2.0cm, MRA示右MCA M1段重度狹窄\\.br\\治療: 雙重抗血小板(Aspirin+Clopidogrel), 降血脂, 復健治療\\.br\\出院時狀態: 左側肢'
            '體肌力4/5, 日常生活可自理\\.br\\出院後注意: 規律服藥, 控制三高, 門診追蹤\\.br\\回診日期: 2026/05/24'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260517130000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509073000'
        msh.message_type = MSG(msg_1='OML', msg_2='O33', msg_3='OML_O33')
        msh.message_control_id = 'TCVGH20260509073001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        sac.container_identifier = EI(ei_1='TUBE20260509040')
        sac.additive = CWE(cwe_1='BLD')

        # .. build the SPECIMEN_CONTAINER group ..
        specimen_container = OmlO33SpecimenContainer()
        specimen_container.sac = sac

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LAB20260509050')
        orc.orc_7 = '^^^20260509073000^^R'
        orc.date_time_of_order_event = '20260509073000'
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509050')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260509073000'

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB20260509051')
        orc_2.orc_7 = '^^^20260509073000^^R'
        orc_2.date_time_of_order_event = '20260509073000'
        orc_2.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260509051')
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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260509130001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509050')
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509050')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260509073000'
        obr.obr_14 = '20260509073000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D500100^曾俊凱^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球計數', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='紅血球計數', cwe_3='LN')
        obx_2.obx_5 = '5.10'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.50-5.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_3.obx_5 = '15.2'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.0-17.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='血小板計數', cwe_3='LN')
        obx_4.obx_5 = '220'
        obx_4.units = CWE(cwe_1='10*3/uL')
        obx_4.reference_range = '150-400'
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

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'RE'
        orc_2.placer_order_number = EI(ei_1='LAB20260509051')
        orc_2.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order_2 = OruR01CommonOrder()
        common_order_2.orc = orc_2

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB20260509051')
        obr_2.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='脂質檢查', cwe_3='LN')
        obr_2.observation_date_time = '20260509073000'
        obr_2.obr_14 = '20260509073000'
        obr_2.obr_15 = '血液^Blood'
        obr_2.obr_16 = 'D500100^曾俊凱^^^醫師'

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2093-3', cwe_2='總膽固醇', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '0-200'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2571-8', cwe_2='三酸甘油酯', cwe_3='LN')
        obx_6.obx_5 = '180'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '0-150'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2089-1', cwe_2='LDL膽固醇', cwe_3='LN')
        obx_7.obx_5 = '168'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '0-130'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL膽固醇', cwe_3='LN')
        obx_8.obx_5 = '42'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '40-60'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.common_order = common_order_2
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_5
        order_observation_2.observation_2 = observation_6
        order_observation_2.observation_3 = observation_7
        order_observation_2.observation_4 = observation_8

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation
        patient_result.order_observation_2 = order_observation_2

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260509140001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500100', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='江', xpn_2='柏翰', xpn_5='先生')
        pid.date_time_of_birth = '19650512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='文心路四段698號', xad_3='台中市', xad_5='40652', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='神經內科', pl_2='701', pl_3='A', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500100', xcn_2='曾俊凱', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='LAB20260509060')
        orc.orc_12 = 'D500100^曾俊凱^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260509060')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='凝血功能檢查', cwe_3='LN')
        obr.observation_date_time = '20260509074000'
        obr.obr_14 = '20260509074000'
        obr.obr_15 = '血液^Blood'
        obr.obr_16 = 'D500100^曾俊凱^^^醫師'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='凝血酶原時間(PT)', cwe_3='LN')
        obx.obx_5 = '13.0'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-13.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.08'
        obx_2.reference_range = '0.85-1.15'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='活化部分凝血活酶時間(APTT)', cwe_3='LN')
        obx_3.obx_5 = '30.2'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25.0-35.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='48065-7', cwe_2='D-dimer', cwe_3='LN')
        obx_4.obx_5 = '0.45'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.reference_range = '0.00-0.50'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/tw/tw-iisi-ipacs.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='iPACS')
        msh.sending_facility = HD(hd_1='台中榮民總醫院')
        msh.receiving_application = HD(hd_1='RADIOLOGY')
        msh.receiving_facility = HD(hd_1='台中榮民總醫院')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCVGH20260511160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT500200', cx_4='台中榮民總醫院', cx_5='PI')
        pid.patient_name = XPN(xpn_1='洪', xpn_2='詩涵', xpn_5='女士')
        pid.date_time_of_birth = '19930328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='美村路一段200號', xad_3='台中市', xad_5='40356', xad_6='TW')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='放射科門診', pl_2='診間02', pl_4='台中榮民總醫院')
        pv1.attending_doctor = XCN(xcn_1='D500200', xcn_2='林宗賢', xcn_5='醫師')

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
        orc.placer_order_number = EI(ei_1='RAD20260511001')
        orc.orc_12 = 'D500200^林宗賢^^^醫師'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260511001')
        obr.universal_service_identifier = CWE(cwe_1='36803-5', cwe_2='頸部血管MRA', cwe_3='LN')
        obr.observation_date_time = '20260511100000'
        obr.obr_14 = '20260511100000'
        obr.obr_16 = 'D500200^林宗賢^^^醫師'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36803-5', cwe_2='頸部血管MRA', cwe_3='LN')
        obx.obx_5 = (
            '雙側頸動脈及椎動脈走行正常, 管腔通暢。雙側頸內動脈起始處未見明顯狹窄或斑塊。基底動脈正常。Willis環完整。無動脈瘤或血管畸形。報告醫師: 徐文芳醫師'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='頸部MRA報告PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6aCP6YOo6KGA'
            '566hTVJB5aCx5ZGKIC0g6aas5YG557SA5b+157i96Yar6ZmiKSBUagowIC0yMCBUZAoo6ZuZ5YGT6aCP5YuV6ISI5Y+K5qSO5YuV6ISI6LWw6KGM5q2j5bi4KSBUagowIC0yMCBUZAoo'
            '566h6IWU6YCa5pqiKSBUagowIC0yMCBUZAoo5Z+66YOo5YuV6ISI5q2j5bi4KSBUagowIC0yMCBUZAooV2lsbGlz55Kw5a6M5pW0KSBUagowIC0yMCBUZAoo54Sh5YuV6ISI55iu5oiW'
            '6KGA566h55WQ5b2iKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9i'
            'agp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAw'
            'MDAgbiAKMDAwMDAwMDY2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjczMQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260511160000'

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

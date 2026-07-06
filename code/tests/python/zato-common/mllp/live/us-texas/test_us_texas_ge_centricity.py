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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, DLD, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A03, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-ge-centricity.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_SA')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='METH_SA_RAD')
        msh.date_time_of_message = '20250305091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250305001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40001234', cx_4='METHODIST_SA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='VALENZUELA', xpn_2='Ernesto', xpn_3='Miguel', xpn_5='Mr.')
        pid.date_time_of_birth = '19630714'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2718 Huisache Ave', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^4437821'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED8', pl_3='A', pl_4='METHODIST_SA', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '7831204^SUTHERLAND^DEREK^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='7831204', cwe_2='SUTHERLAND', cwe_3='DEREK', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV10001', xcn_4='METHODIST_SA', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICARE')

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
        orc.placer_order_number = EI(ei_1='RAD100001', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250305093000^^S'
        orc.date_time_of_order_event = '20250305091500'
        orc.orc_10 = 'NURSE01^THORNBURY^ROSA^M^^^RN'
        orc.orc_12 = '7831204^SUTHERLAND^DEREK^R^^^MD'
        orc.enterers_location = PL(pl_1='ED', pl_2='BED8', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='METHODIST_SA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD100001', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT HEAD WITHOUT CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250305091500'
        obr.relevant_clinical_information = CWE(cwe_1='STAT')
        obr.placer_field_1 = '7831204^SUTHERLAND^DEREK^R^^^MD'
        obr.placer_field_2 = '^WPN^PH^^^210^9127463'
        obr.diagnostic_serv_sect_id = '20250305093000'
        obr.obr_27 = 'S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R51.9', cwe_2='Headache, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R55', cwe_2='Syncope and collapse', cwe_3='ICD10')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1
        order_detail.dg1_2 = dg1_2

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_SYS')
        msh.sending_facility = HD(hd_1='HOUSTON_IMAGING')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='HI_RAD')
        msh.date_time_of_message = '20250308070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'GE20250308001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250308070000'
        evn.evn_5 = 'REG01^CARTWRIGHT^LINDA^K^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40012345', cx_4='HOUSTON_IMAGING', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SINGLETON', xpn_2='Tamara', xpn_3='Denise', xpn_5='Ms.')
        pid.date_time_of_birth = '19850523'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9214 Briar Forest Dr', xad_3='Houston', xad_4='TX', xad_5='77063', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^6028174'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MRI', pl_2='SUITE1', pl_3='A', pl_4='HOUSTON_IMAGING', pl_8='MRI')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Elective')
        pv1.pv1_7 = '4490217^WAINWRIGHT^HENRY^H^^^MD^RADIOLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='4490217', cwe_2='WAINWRIGHT', cwe_3='HENRY', cwe_4='H', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV20002', xcn_4='HOUSTON_IMAGING', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='UNITED')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='003', cwe_2='UNITED HEALTHCARE')
        in1.insurance_company_id = CX(cx_1='UHC001')
        in1.insurance_company_name = XON(xon_1='UNITED HEALTHCARE OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 740800', xad_3='Atlanta', xad_4='GA', xad_5='30374', xad_6='US')
        in1.group_number = 'GRP55555'
        in1.plan_effective_date = '20240101'
        in1.name_of_insured = XPN(xpn_1='SINGLETON', xpn_2='Tamara', xpn_3='Denise')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19850523'
        in1.insureds_address = XAD(xad_1='9214 Briar Forest Dr', xad_3='Houston', xad_4='TX', xad_5='77063', xad_6='US')
        in1.policy_deductible = CP(cp_1='UHC890123456')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Low back pain', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='HOUSTON_IMAGING')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='HI_RAD')
        msh.date_time_of_message = '20250308071500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250308002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40012345', cx_4='HOUSTON_IMAGING', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SINGLETON', xpn_2='Tamara', xpn_3='Denise', xpn_5='Ms.')
        pid.date_time_of_birth = '19850523'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9214 Briar Forest Dr', xad_3='Houston', xad_4='TX', xad_5='77063', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^6028174'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MRI', pl_2='SUITE1', pl_3='A', pl_4='HOUSTON_IMAGING', pl_8='MRI')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Elective')
        pv1.pv1_7 = '4490217^WAINWRIGHT^HENRY^H^^^MD^RADIOLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='6612843', cwe_2='CROMWELL', cwe_3='THOMAS', cwe_4='T', cwe_7='MD', cwe_8='ORDERING')
        pv1.admitting_doctor = XCN(xcn_1='GV20002', xcn_4='HOUSTON_IMAGING', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='UNITED')

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
        orc.placer_order_number = EI(ei_1='RAD200002', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250308080000^^R'
        orc.date_time_of_order_event = '20250308071500'
        orc.orc_12 = '6612843^CROMWELL^THOMAS^T^^^MD'
        orc.enterers_location = PL(pl_1='CLINIC', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='HOUSTON_IMAGING')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD200002', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='MRI LUMBAR SPINE W/O CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250308080000'
        obr.obr_16 = '6612843^CROMWELL^THOMAS^T^^^MD'
        obr.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='713', xtn_7='3019487')
        obr.results_rpt_status_chng_date_time = '20250308080000'
        obr.result_status = 'F'

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
        obr_2.placer_order_number = EI(ei_1='RAD200002', ei_2='CLINIC_EMR')
        obr_2.universal_service_identifier = CWE(cwe_1='72149', cwe_2='MRI LUMBAR SPINE W CONTRAST', cwe_3='CPT')
        obr_2.observation_date_time = '20250308080000'
        obr_2.obr_16 = '6612843^CROMWELL^THOMAS^T^^^MD'
        obr_2.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='713', xtn_7='3019487')
        obr_2.results_rpt_status_chng_date_time = '20250308080000'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Low back pain', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='M51.16', cwe_2='Intervertebral disc degeneration, lumbar region', cwe_3='ICD10')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1, dg1_2]

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='METH_SA_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='METHODIST_HOSP_SA')
        msh.date_time_of_message = '20250305110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250305002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40001234', cx_4='METHODIST_SA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='VALENZUELA', xpn_2='Ernesto', xpn_3='Miguel', xpn_5='Mr.')
        pid.date_time_of_birth = '19630714'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2718 Huisache Ave', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^4437821'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED8', pl_3='A', pl_4='METHODIST_SA', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '7831204^SUTHERLAND^DEREK^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='7831204', cwe_2='SUTHERLAND', cwe_3='DEREK', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV10001', xcn_4='METHODIST_SA', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='RAD100001', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS300001', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250305093000^^S'
        orc.date_time_of_order_event = '20250305110000'
        orc.orc_12 = '5527301^LANGFORD^RAYMOND^D^^^MD^RADIOLOGIST'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD100001', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS300001', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT HEAD WITHOUT CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250305093500'
        obr.obr_16 = '5527301^LANGFORD^RAYMOND^D^^^MD'
        obr.results_rpt_status_chng_date_time = '20250305105500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: CT Head without contrast\\.br\\\\.br\\CLINICAL INDICATION: Syncope, headache\\.br\\\\.br\\TECHNIQUE: Axial CT images of the brain without '
            'IV contrast.\\.br\\\\.br\\FINDINGS:\\.br\\Brain parenchyma: No acute infarct, hemorrhage, or mass lesion.\\.br\\Ventricles: Normal size and conf'
            'iguration.\\.br\\Extra-axial spaces: No subdural or epidural collection.\\.br\\Calvarium: No fracture.\\.br\\Paranasal sinuses: Clear.\\.br\\\\.'
            'br\\IMPRESSION:\\.br\\1. No acute intracranial abnormality.\\.br\\2. No evidence of hemorrhage or mass effect.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250305105500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='HI_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='HOUSTON_IMAGING')
        msh.date_time_of_message = '20250308143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250308003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40012345', cx_4='HOUSTON_IMAGING', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SINGLETON', xpn_2='Tamara', xpn_3='Denise', xpn_5='Ms.')
        pid.date_time_of_birth = '19850523'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9214 Briar Forest Dr', xad_3='Houston', xad_4='TX', xad_5='77063', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^6028174'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MRI', pl_2='SUITE1', pl_3='A', pl_4='HOUSTON_IMAGING', pl_8='MRI')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='4490217', cwe_2='WAINWRIGHT', cwe_3='HENRY', cwe_4='H', cwe_7='MD')
        pv1.pv1_20 = 'GV20002^^^HOUSTON_IMAGING^VN'

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
        orc.placer_order_number = EI(ei_1='RAD200002', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS400002', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250308080000^^R'
        orc.date_time_of_order_event = '20250308143000'
        orc.orc_12 = '4490217^WAINWRIGHT^HENRY^H^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD200002', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS400002', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='MRI LUMBAR SPINE W/O AND W CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250308081000'
        obr.obr_16 = '4490217^WAINWRIGHT^HENRY^H^^^MD'
        obr.results_rpt_status_chng_date_time = '20250308140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='MRI Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDg4ID4+CnN0cmVhbQpCVAovRjEgMTYgVGYKNzIgNzIwIFRkCihNUkkgTHVtYmFyIFNwaW5lIFJlcG9ydCkgVGoKMCAyNCBUZAovRjEg'
            'MTIgVGYKKEZpbmRpbmdzOiBMNC1MNSBkaXNjIGhlcm5pYXRpb24pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmo='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250308140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx_2.obx_5 = (
            'EXAM: MRI Lumbar Spine without and with contrast\\.br\\\\.br\\CLINICAL INDICATION: Low back pain with radiculopathy\\.br\\\\.br\\FINDINGS:\\.br'
            '\\L3-L4: Mild disc bulge without stenosis.\\.br\\L4-L5: Broad-based left paracentral disc herniation measuring 6mm, contacting the traversing l'
            'eft L5 nerve root. Mild left lateral recess narrowing.\\.br\\L5-S1: Small central disc protrusion without nerve root compression.\\.br\\Conus me'
            'dullaris: Normal in position and signal.\\.br\\No enhancement to suggest infection or neoplasm.\\.br\\\\.br\\IMPRESSION:\\.br\\1. L4-L5 left par'
            'acentral disc herniation with left L5 nerve root contact.\\.br\\2. Mild degenerative changes at L3-L4 and L5-S1.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250308140000'

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='PARKLAND_RAD')
        msh.date_time_of_message = '20250310143000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250310001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40023456', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DORSEY', xpn_2='Darnell', xpn_3='Lamont', xpn_5='Mr.')
        pid.date_time_of_birth = '19750908'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3812 Macon St', xad_3='Dallas', xad_4='TX', xad_5='75216', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^7530946'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTH', pl_2='503', pl_3='A', pl_4='PARKLAND', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='8143560', cwe_2='HARRINGTON', cwe_3='CEDRIC', cwe_4='C', cwe_7='MD')
        pv1.pv1_20 = 'GV30003^^^PARKLAND^VN'
        pv1.charge_price_indicator = CWE(cwe_1='MEDICAID')

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
        orc.placer_order_number = EI(ei_1='RAD300003', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250310150000^^R'
        orc.date_time_of_order_event = '20250310143000'
        orc.orc_10 = 'NURSE02^WINFIELD^TANYA^M^^^RN'
        orc.orc_12 = '8143560^HARRINGTON^CEDRIC^C^^^MD'
        orc.enterers_location = PL(pl_1='5NORTH', pl_2='503', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='PARKLAND')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD300003', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CHEST X-RAY 2 VIEWS', cwe_3='CPT')
        obr.observation_date_time = '20250310143000'
        obr.obr_16 = '8143560^HARRINGTON^CEDRIC^C^^^MD'
        obr.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='8024571')
        obr.results_rpt_status_chng_date_time = '20250310150000'
        obr.result_status = 'R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia, unspecified organism', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='PARKLAND_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.date_time_of_message = '20250310163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250310002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40023456', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DORSEY', xpn_2='Darnell', xpn_3='Lamont', xpn_5='Mr.')
        pid.date_time_of_birth = '19750908'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3812 Macon St', xad_3='Dallas', xad_4='TX', xad_5='75216', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^7530946'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTH', pl_2='503', pl_3='A', pl_4='PARKLAND', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='8143560', cwe_2='HARRINGTON', cwe_3='CEDRIC', cwe_4='C', cwe_7='MD')
        pv1.pv1_20 = 'GV30003^^^PARKLAND^VN'

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
        orc.placer_order_number = EI(ei_1='RAD300003', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS500003', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250310150000^^R'
        orc.date_time_of_order_event = '20250310163000'
        orc.orc_12 = '9274038^UNDERWOOD^PATRICIA^A^^^MD^RADIOLOGIST'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD300003', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS500003', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CHEST X-RAY 2 VIEWS', cwe_3='CPT')
        obr.observation_date_time = '20250310150500'
        obr.obr_16 = '9274038^UNDERWOOD^PATRICIA^A^^^MD'
        obr.results_rpt_status_chng_date_time = '20250310162500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: Chest X-ray PA and Lateral\\.br\\\\.br\\CLINICAL INDICATION: Cough, fever, rule out pneumonia\\.br\\\\.br\\FINDINGS:\\.br\\Heart: Normal s'
            'ize.\\.br\\Lungs: Right lower lobe consolidation with air bronchograms, consistent with pneumonia. No pleural effusion.\\.br\\Mediastinum: Norma'
            'l.\\.br\\Osseous structures: Unremarkable.\\.br\\\\.br\\IMPRESSION:\\.br\\Right lower lobe pneumonia.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310162500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='WOMEN_CENTER_AUSTIN')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='WCA_RAD')
        msh.date_time_of_message = '20250312080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250312001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40034567', cx_4='WOMEN_CENTER', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PRESCOTT', xpn_2='Katherine', xpn_3='Elaine', xpn_5='Mrs.')
        pid.date_time_of_birth = '19690311'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5830 Shoal Creek Blvd', xad_3='Austin', xad_4='TX', xad_5='78756', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^3841267'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MAMMO', pl_2='ROOM2', pl_3='A', pl_4='WOMEN_CENTER', pl_8='MAMMOGRAPHY')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Elective')
        pv1.pv1_7 = '3056189^KENSINGTON^PATRICIA^L^^^MD^RADIOLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='3056189', cwe_2='KENSINGTON', cwe_3='PATRICIA', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV40004', xcn_4='WOMEN_CENTER', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='BCBS')

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
        orc.placer_order_number = EI(ei_1='RAD400004', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250312083000^^R'
        orc.date_time_of_order_event = '20250312080000'
        orc.orc_12 = '3056189^KENSINGTON^PATRICIA^L^^^MD'
        orc.enterers_location = PL(pl_1='MAMMO', pl_2='ROOM2', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='WOMEN_CENTER')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD400004', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='SCREENING MAMMOGRAM BILATERAL', cwe_3='CPT')
        obr.observation_date_time = '20250312083000'
        obr.obr_16 = '3056189^KENSINGTON^PATRICIA^L^^^MD'
        obr.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='512', xtn_7='7190354')
        obr.results_rpt_status_chng_date_time = '20250312083000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.31', cwe_2='Encounter for screening mammogram', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='WCA_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='WOMEN_CENTER_AUSTIN')
        msh.date_time_of_message = '20250312150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250312002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40034567', cx_4='WOMEN_CENTER', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PRESCOTT', xpn_2='Katherine', xpn_3='Elaine', xpn_5='Mrs.')
        pid.date_time_of_birth = '19690311'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5830 Shoal Creek Blvd', xad_3='Austin', xad_4='TX', xad_5='78756', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^3841267'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MAMMO', pl_2='ROOM2', pl_3='A', pl_4='WOMEN_CENTER', pl_8='MAMMOGRAPHY')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='3056189', cwe_2='KENSINGTON', cwe_3='PATRICIA', cwe_4='L', cwe_7='MD')
        pv1.pv1_20 = 'GV40004^^^WOMEN_CENTER^VN'

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
        orc.placer_order_number = EI(ei_1='RAD400004', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS600004', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250312083000^^R'
        orc.date_time_of_order_event = '20250312150000'
        orc.orc_12 = '3056189^KENSINGTON^PATRICIA^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD400004', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS600004', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='SCREENING MAMMOGRAM BILATERAL', cwe_3='CPT')
        obr.observation_date_time = '20250312083500'
        obr.obr_16 = '3056189^KENSINGTON^PATRICIA^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250312145000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: Screening Mammogram Bilateral\\.br\\\\.br\\CLINICAL INDICATION: Annual screening, no symptoms\\.br\\\\.br\\BREAST COMPOSITION: Heterogeneo'
            'usly dense (Category C)\\.br\\\\.br\\FINDINGS:\\.br\\Right breast: No suspicious masses, calcifications, or architectural distortion.\\.br\\Left'
            ' breast: No suspicious masses, calcifications, or architectural distortion.\\.br\\Axillae: No suspicious lymphadenopathy.\\.br\\\\.br\\ASSESSMEN'
            'T: BI-RADS 1 - Negative\\.br\\\\.br\\RECOMMENDATION: Routine annual screening mammography.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250312145000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='36625-2', cwe_2='BIRADS ASSESSMENT', cwe_3='LN')
        obx_2.obx_5 = '1^NEGATIVE^BIRADS'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250312145000'

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='SCOTT_WHITE_TEMPLE')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='BSW_RAD')
        msh.date_time_of_message = '20250315021500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40045678', cx_4='BSW_TEMPLE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='TSUJI', xpn_2='David', xpn_3='Kenji', xpn_5='Mr.')
        pid.date_time_of_birth = '19580219'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1407 Canyon Creek Dr', xad_3='Temple', xad_4='TX', xad_5='76502', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^254^6183042'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED3', pl_3='A', pl_4='BSW_TEMPLE', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '2197403^ASHFORD^MARTIN^M^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='2197403', cwe_2='ASHFORD', cwe_3='MARTIN', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV50005', xcn_4='BSW_TEMPLE', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICARE')

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
        orc.placer_order_number = EI(ei_1='RAD500005', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250315023000^^S'
        orc.date_time_of_order_event = '20250315021500'
        orc.orc_10 = 'NURSE03^ALDRIDGE^SUSAN^Y^^^RN'
        orc.orc_12 = '2197403^ASHFORD^MARTIN^M^^^MD'
        orc.enterers_location = PL(pl_1='ED', pl_2='BED3', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='BSW_TEMPLE')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD500005', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='CT ANGIOGRAPHY CHEST', cwe_3='CPT')
        obr.observation_date_time = '20250315021500'
        obr.relevant_clinical_information = CWE(cwe_1='STAT - PE PROTOCOL')
        obr.placer_field_1 = '2197403^ASHFORD^MARTIN^M^^^MD'
        obr.placer_field_2 = '^WPN^PH^^^254^4019287'
        obr.diagnostic_serv_sect_id = '20250315023000'
        obr.obr_27 = 'S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R06.02', cwe_2='Shortness of breath', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain, unspecified', cwe_3='ICD10')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1
        order_detail.dg1_2 = dg1_2

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='BSW_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='SCOTT_WHITE_TEMPLE')
        msh.date_time_of_message = '20250315033000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250315002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40045678', cx_4='BSW_TEMPLE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='TSUJI', xpn_2='David', xpn_3='Kenji', xpn_5='Mr.')
        pid.date_time_of_birth = '19580219'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1407 Canyon Creek Dr', xad_3='Temple', xad_4='TX', xad_5='76502', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^254^6183042'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED3', pl_3='A', pl_4='BSW_TEMPLE', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '2197403^ASHFORD^MARTIN^M^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='2197403', cwe_2='ASHFORD', cwe_3='MARTIN', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV50005', xcn_4='BSW_TEMPLE', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='RAD500005', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS700005', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250315023000^^S'
        orc.date_time_of_order_event = '20250315033000'
        orc.orc_12 = '7350918^BECKWORTH^VIKRAM^K^^^MD^RADIOLOGIST'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD500005', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS700005', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='CT ANGIOGRAPHY CHEST', cwe_3='CPT')
        obr.observation_date_time = '20250315023500'
        obr.obr_16 = '7350918^BECKWORTH^VIKRAM^K^^^MD'
        obr.results_rpt_status_chng_date_time = '20250315032500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: CT Angiography Chest - PE Protocol\\.br\\\\.br\\CLINICAL INDICATION: Acute dyspnea and chest pain, D-dimer elevated\\.br\\\\.br\\CRITICAL '
            'FINDING COMMUNICATED TO DR. ASHFORD AT 0330 HRS\\.br\\\\.br\\FINDINGS:\\.br\\Pulmonary arteries: Large saddle pulmonary embolus at the bifurcati'
            'on of the main pulmonary artery extending into bilateral lobar and segmental arteries.\\.br\\Right heart: Enlarged right ventricle (RV/LV rati'
            'o 1.4), suggesting right heart strain.\\.br\\Lungs: Wedge-shaped peripheral opacity in right lower lobe, concerning for pulmonary infarct.\\.br'
            '\\Pleural space: Small right pleural effusion.\\.br\\\\.br\\IMPRESSION:\\.br\\1. CRITICAL: Large saddle pulmonary embolus with right heart strai'
            'n.\\.br\\2. Probable right lower lobe pulmonary infarct.\\.br\\3. Small right pleural effusion.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250315032500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='CHRISTUS_SPOHN_CC')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='CHRISTUS_RAD')
        msh.date_time_of_message = '20250318101500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250318001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40056789', cx_4='CHRISTUS_SPOHN', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LEYVA', xpn_2='Maria', xpn_3='Consuelo', xpn_5='Mrs.')
        pid.date_time_of_birth = '19700125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6201 Ayers St', xad_3='Corpus Christi', xad_4='TX', xad_5='78415', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^361^2047831'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='US', pl_2='ROOM1', pl_3='A', pl_4='CHRISTUS_SPOHN', pl_8='ULTRASOUND')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine')
        pv1.pv1_7 = '1638270^MERRIWEATHER^BRANDON^S^^^MD^PCP'
        pv1.ambulatory_status = CWE(cwe_1='1638270', cwe_2='MERRIWEATHER', cwe_3='BRANDON', cwe_4='S', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV60006', xcn_4='CHRISTUS_SPOHN', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='AETNA')

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
        orc.placer_order_number = EI(ei_1='RAD600006', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250318110000^^R'
        orc.date_time_of_order_event = '20250318101500'
        orc.orc_12 = '1638270^MERRIWEATHER^BRANDON^S^^^MD'
        orc.enterers_location = PL(pl_1='CLINIC', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='CHRISTUS_SPOHN')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD600006', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='ULTRASOUND ABDOMEN COMPLETE', cwe_3='CPT')
        obr.observation_date_time = '20250318110000'
        obr.obr_16 = '1638270^MERRIWEATHER^BRANDON^S^^^MD'
        obr.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='361', xtn_7='5190742')
        obr.results_rpt_status_chng_date_time = '20250318110000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.9', cwe_2='Unspecified abdominal pain', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R16.0', cwe_2='Hepatomegaly, not elsewhere classified', cwe_3='ICD10')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1
        order_detail.dg1_2 = dg1_2

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='CHRISTUS_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='CHRISTUS_SPOHN_CC')
        msh.date_time_of_message = '20250318140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250318002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40056789', cx_4='CHRISTUS_SPOHN', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LEYVA', xpn_2='Maria', xpn_3='Consuelo', xpn_5='Mrs.')
        pid.date_time_of_birth = '19700125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6201 Ayers St', xad_3='Corpus Christi', xad_4='TX', xad_5='78415', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^361^2047831'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='US', pl_2='ROOM1', pl_3='A', pl_4='CHRISTUS_SPOHN', pl_8='ULTRASOUND')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='4781209', cwe_2='WHITFIELD', cwe_3='MELISSA', cwe_4='R', cwe_7='MD', cwe_8='RADIOLOGIST')
        pv1.pv1_20 = 'GV60006^^^CHRISTUS_SPOHN^VN'

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
        orc.placer_order_number = EI(ei_1='RAD600006', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS800006', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250318110000^^R'
        orc.date_time_of_order_event = '20250318140000'
        orc.orc_12 = '4781209^WHITFIELD^MELISSA^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD600006', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS800006', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='ULTRASOUND ABDOMEN COMPLETE', cwe_3='CPT')
        obr.observation_date_time = '20250318111500'
        obr.obr_16 = '4781209^WHITFIELD^MELISSA^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250318135000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: Ultrasound Abdomen Complete\\.br\\\\.br\\CLINICAL INDICATION: Abdominal pain, hepatomegaly on exam\\.br\\\\.br\\FINDINGS:\\.br\\Liver: Enl'
            'arged, measuring 18.5 cm. Diffusely echogenic parenchyma consistent with hepatic steatosis. No focal lesions.\\.br\\Gallbladder: Normal wall t'
            'hickness. No cholelithiasis.\\.br\\Common bile duct: 4mm, normal.\\.br\\Pancreas: Visualized portions normal.\\.br\\Spleen: Normal size (10.2 cm'
            ').\\.br\\Kidneys: Right 11.2 cm, Left 11.5 cm. No hydronephrosis or stones.\\.br\\Aorta: Normal caliber.\\.br\\\\.br\\IMPRESSION:\\.br\\1. Hepat'
            'omegaly with diffuse hepatic steatosis.\\.br\\2. No cholelithiasis or biliary dilatation.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250318135000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='SHANNON_SAN_ANGELO')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='SHANNON_RAD')
        msh.date_time_of_message = '20250320090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250320001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40067890', cx_4='SHANNON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GALBRAITH', xpn_2='Billy', xpn_3='Raymond', xpn_5='Mr.')
        pid.date_time_of_birth = '19480612'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1503 Paint Rock Rd', xad_3='San Angelo', xad_4='TX', xad_5='76901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^325^8170493'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='FLUORO', pl_2='ROOM1', pl_3='A', pl_4='SHANNON', pl_8='FLUORO')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine')
        pv1.pv1_7 = '6024317^PEMBERTON^MARGARET^A^^^MD^GI'
        pv1.ambulatory_status = CWE(cwe_1='6024317', cwe_2='PEMBERTON', cwe_3='MARGARET', cwe_4='A', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV70007', xcn_4='SHANNON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICARE')

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
        orc.placer_order_number = EI(ei_1='RAD700007', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250320100000^^R'
        orc.date_time_of_order_event = '20250320090000'
        orc.orc_12 = '6024317^PEMBERTON^MARGARET^A^^^MD'
        orc.enterers_location = PL(pl_1='CLINIC', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='SHANNON')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD700007', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='74240', cwe_2='UPPER GI SERIES', cwe_3='CPT')
        obr.observation_date_time = '20250320100000'
        obr.obr_16 = '6024317^PEMBERTON^MARGARET^A^^^MD'
        obr.order_callback_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='325', xtn_7='6041238')
        obr.results_rpt_status_chng_date_time = '20250320100000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K21.0', cwe_2='Gastro-esophageal reflux disease with esophagitis', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_SYS')
        msh.sending_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='PARKLAND_RAD')
        msh.date_time_of_message = '20250322140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'GE20250322001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250322140000'
        evn.evn_5 = 'CHARGE01^RICHMOND^TIFFANY^L^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40023456', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DORSEY', xpn_2='Darnell', xpn_3='Lamont', xpn_5='Mr.')
        pid.date_time_of_birth = '19750908'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3812 Macon St', xad_3='Dallas', xad_4='TX', xad_5='75216', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^7530946'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='801', pl_3='A', pl_4='PARKLAND', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.preadmit_number = CX(cx_1='5NORTH', cx_2='503', cx_3='A', cx_4='PARKLAND', cx_8='MEDSURG')
        pv1.pv1_7 = '8143560^HARRINGTON^CEDRIC^C^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='8143560', cwe_2='HARRINGTON', cwe_3='CEDRIC', cwe_4='C', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV30003', xcn_4='PARKLAND', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='PARKLAND_RAD')
        msh.date_time_of_message = '20250322141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GE20250322002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40023456', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DORSEY', xpn_2='Darnell', xpn_3='Lamont', xpn_5='Mr.')
        pid.date_time_of_birth = '19750908'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3812 Macon St', xad_3='Dallas', xad_4='TX', xad_5='75216', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^7530946'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='801', pl_3='A', pl_4='PARKLAND', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '8143560^HARRINGTON^CEDRIC^C^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='8143560', cwe_2='HARRINGTON', cwe_3='CEDRIC', cwe_4='C', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV30003', xcn_4='PARKLAND', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

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
        orc.placer_order_number = EI(ei_1='RAD800008', ei_2='CLINIC_EMR')
        orc.orc_7 = '^^^20250322143000^^R'
        orc.date_time_of_order_event = '20250322141500'
        orc.orc_10 = 'NURSE04^BLACKWELL^KEISHA^D^^^RN'
        orc.orc_12 = '8143560^HARRINGTON^CEDRIC^C^^^MD'
        orc.enterers_location = PL(pl_1='ICU', pl_2='801', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='PARKLAND')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD800008', ei_2='CLINIC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='71045', cwe_2='CHEST X-RAY 1 VIEW PORTABLE', cwe_3='CPT')
        obr.observation_date_time = '20250322141500'
        obr.relevant_clinical_information = CWE(cwe_1='PORTABLE')
        obr.placer_field_1 = '8143560^HARRINGTON^CEDRIC^C^^^MD'
        obr.placer_field_2 = '^WPN^PH^^^214^8024571'
        obr.diagnostic_serv_sect_id = '20250322143000'
        obr.obr_27 = 'R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J96.01', cwe_2='Acute respiratory failure with hypoxia', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'ET TUBE PLACEMENT CHECK - PATIENT ON MECHANICAL VENTILATION'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='WCA_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='WOMEN_CENTER_AUSTIN')
        msh.date_time_of_message = '20250325140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GE20250325001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40078901', cx_4='WOMEN_CENTER', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FAIRBANKS', xpn_2='Barbara', xpn_3='Louise', xpn_5='Mrs.')
        pid.date_time_of_birth = '19530818'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2704 Exposition Blvd', xad_3='Austin', xad_4='TX', xad_5='78703', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^9073164'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DEXA', pl_2='ROOM1', pl_3='A', pl_4='WOMEN_CENTER', pl_8='DEXA')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='3056189', cwe_2='KENSINGTON', cwe_3='PATRICIA', cwe_4='L', cwe_7='MD')
        pv1.pv1_20 = 'GV80008^^^WOMEN_CENTER^VN'
        pv1.charge_price_indicator = CWE(cwe_1='MEDICARE')

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
        orc.placer_order_number = EI(ei_1='RAD900009', ei_2='CLINIC_EMR')
        orc.filler_order_number = EI(ei_1='RRIS900009', ei_2='CENTRICITY_RIS')
        orc.orc_7 = '^^^20250325100000^^R'
        orc.date_time_of_order_event = '20250325140000'
        orc.orc_12 = '3056189^KENSINGTON^PATRICIA^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD900009', ei_2='CLINIC_EMR')
        obr.filler_order_number = EI(ei_1='RRIS900009', ei_2='CENTRICITY_RIS')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DEXA BONE DENSITY', cwe_3='CPT')
        obr.observation_date_time = '20250325101500'
        obr.obr_16 = '3056189^KENSINGTON^PATRICIA^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250325135000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='DEXA Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDExMCA+PgpzdHJlYW0KQlQKL0YxIDE2IFRmCjcyIDcyMCBUZAooREVYQSBCb25lIERlbnNpdHkgUmVwb3J0KSBUagowIDI0IFRkCi9G'
            'MSAxMiBUZgooTHVtYmFyIFNwaW5lIFQtU2NvcmU6IC0yLjcgLSBPc3Rlb3Bvcm9zaXMpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmo='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250325135000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx_2.obx_5 = (
            'EXAM: DEXA Bone Density - Lumbar Spine and Hip\\.br\\\\.br\\CLINICAL INDICATION: Postmenopausal female, age 71, screening\\.br\\\\.br\\RESULTS:'
            '\\.br\\Lumbar Spine (L1-L4):\\.br\\  BMD: 0.782 g/cm2\\.br\\  T-Score: -2.7\\.br\\  Z-Score: -1.2\\.br\\\\.br\\Left Femoral Neck:\\.br\\  BMD: 0'
            '.658 g/cm2\\.br\\  T-Score: -2.3\\.br\\  Z-Score: -0.8\\.br\\\\.br\\Total Hip:\\.br\\  BMD: 0.751 g/cm2\\.br\\  T-Score: -2.0\\.br\\  Z-Score: -'
            '0.6\\.br\\\\.br\\ASSESSMENT:\\.br\\Osteoporosis at lumbar spine (T-Score -2.7).\\.br\\Osteopenia at femoral neck and total hip.\\.br\\\\.br\\FRA'
            'CTURE RISK: FRAX 10-year major osteoporotic fracture risk: 22%'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250325135000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='46278-8', cwe_2='LUMBAR SPINE T-SCORE', cwe_3='LN')
        obx_3.obx_5 = '-2.7'
        obx_3.reference_range = '>-1.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250325135000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='46279-6', cwe_2='FEMORAL NECK T-SCORE', cwe_3='LN')
        obx_4.obx_5 = '-2.3'
        obx_4.reference_range = '>-1.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250325135000'

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SCHED_SYS')
        msh.sending_facility = HD(hd_1='UT_SOUTHWESTERN')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='UTSW_RAD')
        msh.date_time_of_message = '20250328100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'GE20250328001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT700234', ei_2='SCHED_SYS')
        sch.filler_appointment_id = EI(ei_1='APT700234', ei_2='SCHED_SYS')
        sch.schedule_id = CWE(cwe_1='CTBX', cwe_2='CT Guided Biopsy', cwe_3='LOCAL')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='60', cwe_2='MIN')
        sch.appointment_type = CWE(cwe_1='1')
        sch.appointment_duration_units = CNE(cne_1='BOOKED')
        sch.sch_16 = '9401753^STRATTON^JOON^J^^^MD^RADIOLOGIST'
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='2081694')
        sch.filler_contact_address = XAD(xad_1='5323 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75390', xad_6='US')
        sch.parent_placer_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40089012', cx_4='UTSW', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CHADWICK', xpn_2='Gregory', xpn_3='Russell', xpn_5='Mr.')
        pid.date_time_of_birth = '19610405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4715 Swiss Ave', xad_3='Dallas', xad_4='TX', xad_5='75214', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^469^3150287'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IR', pl_2='SUITE2', pl_3='A', pl_4='UTSW', pl_8='INTERV_RAD')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Elective')
        pv1.pv1_7 = '9401753^STRATTON^JOON^J^^^MD^RADIOLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='9401753', cwe_2='STRATTON', cwe_3='JOON', cwe_4='J', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV90009', xcn_4='UTSW', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='CIGNA')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='CTBX')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CTBX', cwe_2='CT Guided Biopsy', cwe_3='LOCAL')
        ais.start_date_time = '20250402100000'
        ais.duration = '60^MIN'
        ais.duration_units = CNE(cne_1='60', cne_2='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '9401753^STRATTON^JOON^J^^^MD'
        aip.resource_type = CWE(cwe_1='RADIOLOGIST')
        aip.resource_group = CWE(cwe_1='20250402100000')
        aip.start_date_time_offset_units = CNE(cne_1='60', cne_2='MIN')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='IR', pl_2='SUITE2', pl_3='A', pl_4='UTSW')
        ail.location_type_ail = CWE(cwe_1='INTERV_RAD')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_SYS')
        msh.sending_facility = HD(hd_1='HOUSTON_IMAGING')
        msh.receiving_application = HD(hd_1='CENTRICITY_RIS')
        msh.receiving_facility = HD(hd_1='HI_RAD')
        msh.date_time_of_message = '20250401153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'GE20250401001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250401153000'
        evn.evn_5 = 'NURSE05^HALSTEAD^SANDRA^R^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40090123', cx_4='HOUSTON_IMAGING', cx_5='MR')
        pid.patient_name = XPN(xpn_1='EMBRY', xpn_2='Marcus', xpn_3='Terrell', xpn_5='Mr.')
        pid.date_time_of_birth = '19720615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1815 Wheeler Ave', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^4017562'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OBS', pl_2='BED2', pl_3='A', pl_4='HOUSTON_IMAGING', pl_8='OBSERVATION')
        pv1.admission_type = CWE(cwe_1='O', cwe_2='Observation')
        pv1.pv1_7 = '4490217^WAINWRIGHT^HENRY^H^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='4490217', cwe_2='WAINWRIGHT', cwe_3='HENRY', cwe_4='H', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='GV10010', xcn_4='HOUSTON_IMAGING', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='BCBS')
        pv1.discharged_to_location = DLD(dld_1='DIS')
        pv1.pending_location = PL(pl_1='20250401080000')
        pv1.admit_date_time = '20250401153000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/us-texas/us-texas-ge-centricity.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CENTRICITY_RIS')
        msh.sending_facility = HD(hd_1='METH_SA_RAD')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='METHODIST_HOSP_SA')
        msh.date_time_of_message = '20250305091530'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'GEACK20250305001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'GE20250305001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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

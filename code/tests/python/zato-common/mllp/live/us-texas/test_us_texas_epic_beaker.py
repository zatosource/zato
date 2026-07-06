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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, ERL, HD, MSG, PL, PT, VID, XAD, XCN, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, DftP03Diagnosis, DftP03Financial, DftP03Visit, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, DFT_P03, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, AL1, DG1, ERR, EVN, FT1, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-epic-beaker.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='LAB_AUTO')
        msh.receiving_facility = HD(hd_1='MDACC_LAB')
        msh.date_time_of_message = '20250310060045'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC2025031001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90001234', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HOANG', xpn_2='Mei', xpn_3='Suyin', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5518742'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='L10N', pl_2='1002', pl_3='A', pl_4='MDACC', pl_8='LEUKEMIA')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '1112233^RUTHERFORD^JAMES^L^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='1112233', cwe_2='RUTHERFORD', cwe_3='JAMES', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E10203040', xcn_4='MDACC', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='EPO100001', ei_2='EPIC')
        orc.orc_7 = '^^^20250310063000^^R'
        orc.date_time_of_order_event = '20250310060045'
        orc.orc_10 = 'NURSE01^PEMBERTON^CLAIRE^M^^^RN'
        orc.orc_12 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        orc.enterers_location = PL(pl_1='L10N', pl_2='1002', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='MDACC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO100001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='COMPLETE BLOOD COUNT', cwe_3='CPT')
        obr.observation_date_time = '20250310060000'
        obr.obr_16 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250310063000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C91.00', cwe_2='Acute lymphoblastic leukemia', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MDACC_EMR')
        msh.date_time_of_message = '20250310073512'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025031002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90001234', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HOANG', xpn_2='Mei', xpn_3='Suyin', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5518742'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='L10N', pl_2='1002', pl_3='A', pl_4='MDACC', pl_8='LEUKEMIA')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '1112233^RUTHERFORD^JAMES^L^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='1112233', cwe_2='RUTHERFORD', cwe_3='JAMES', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E10203040', xcn_4='MDACC', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='EPO100001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR200001', ei_2='BEAKER')
        orc.orc_7 = '^^^20250310063000^^R'
        orc.date_time_of_order_event = '20250310073512'
        orc.orc_12 = '1112233^RUTHERFORD^JAMES^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO100001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR200001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='COMPLETE BLOOD COUNT', cwe_3='CPT')
        obr.observation_date_time = '20250310060000'
        obr.obr_16 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250310073000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '1.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '2.81'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.00-5.50'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='HEMOGLOBIN', cwe_3='LN')
        obx_3.obx_5 = '8.2'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='HEMATOCRIT', cwe_3='LN')
        obx_4.obx_5 = '24.5'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '87.2'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='PLATELET COUNT', cwe_3='LN')
        obx_6.obx_5 = '18'
        obx_6.units = CWE(cwe_1='10*3/uL')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='LL')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='770-8', cwe_2='NEUTROPHILS %', cwe_3='LN')
        obx_7.obx_5 = '12.0'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '40.0-70.0'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='736-9', cwe_2='LYMPHOCYTES %', cwe_3='LN')
        obx_8.obx_5 = '82.0'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '20.0-40.0'
        obx_8.interpretation_codes = CWE(cwe_1='HH')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250310072000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
        order_observation.observation_8 = observation_8

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='TEXAS_CHILDRENS')
        msh.receiving_application = HD(hd_1='LAB_AUTO')
        msh.receiving_facility = HD(hd_1='TCH_LAB')
        msh.date_time_of_message = '20250312083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC2025031201'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90012345', cx_4='TCH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BROADNAX', xpn_2='Elijah', xpn_3='Tyrese', xpn_5='')
        pid.date_time_of_birth = '20180605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6712 Reed Rd', xad_3='Houston', xad_4='TX', xad_5='77033', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5573948'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PICU', pl_2='305', pl_3='B', pl_4='TCH', pl_8='PICU')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '2233445^HAWTHORNE^DANIELLE^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='HAWTHORNE', cwe_3='DANIELLE', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E20304050', xcn_4='TCH', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BROADNAX', xpn_2='Shanice', xpn_3='Denise', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='6712 Reed Rd', xad_3='Houston', xad_4='TX', xad_5='77033', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^832^5573948'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='EPO200002', ei_2='EPIC')
        orc.orc_7 = '^^^20250312090000^^S'
        orc.date_time_of_order_event = '20250312083000'
        orc.orc_10 = 'NURSE02^BELLINGHAM^TARA^R^^^RN'
        orc.orc_12 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        orc.enterers_location = PL(pl_1='PICU', pl_2='305', pl_3='B')
        orc.order_control_code_reason = CWE(cwe_1='TCH')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO200002', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='80048', cwe_2='BASIC METABOLIC PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250312083000'
        obr.obr_16 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250312090000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J96.01', cwe_2='Acute respiratory failure with hypoxia', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [nk1, orc, obr, dg1]

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MEMORIAL_HERMANN')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MH_EMR')
        msh.date_time_of_message = '20250315142200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025031501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90023456', cx_4='MH_TMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='THORNTON', xpn_2='Carolyn', xpn_3='Marie', xpn_5='Ms.')
        pid.date_time_of_birth = '19450309'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5840 San Felipe St', xad_3='Houston', xad_4='TX', xad_5='77057', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5546203'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6EAST', pl_2='612', pl_3='A', pl_4='MH_TMC', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='3344556', cwe_2='COVINGTON', cwe_3='ARVIND', cwe_4='K', cwe_7='MD')
        pv1.pv1_20 = 'E30405060^^^MH_TMC^VN'
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
        orc.placer_order_number = EI(ei_1='EPO300003', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR300003', ei_2='BEAKER')
        orc.orc_7 = '^^^20250315080000^^R'
        orc.date_time_of_order_event = '20250315142200'
        orc.orc_12 = '3344556^COVINGTON^ARVIND^K^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO300003', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR300003', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='81001', cwe_2='URINALYSIS WITH MICROSCOPY', cwe_3='CPT')
        obr.observation_date_time = '20250315080000'
        obr.obr_16 = '3344556^COVINGTON^ARVIND^K^^^MD'
        obr.results_rpt_status_chng_date_time = '20250315140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='COLOR', cwe_3='LN')
        obx.obx_5 = 'AMBER'
        obx.reference_range = 'YELLOW'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='APPEARANCE', cwe_3='LN')
        obx_2.obx_5 = 'CLOUDY'
        obx_2.reference_range = 'CLEAR'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5803-2', cwe_2='PH', cwe_3='LN')
        obx_3.obx_5 = '5.5'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5811-5', cwe_2='SPECIFIC GRAVITY', cwe_3='LN')
        obx_4.obx_5 = '1.030'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='PROTEIN', cwe_3='LN')
        obx_5.obx_5 = '2+'
        obx_5.reference_range = 'NEGATIVE'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='GLUCOSE', cwe_3='LN')
        obx_6.obx_5 = 'NEGATIVE'
        obx_6.reference_range = 'NEGATIVE'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5821-4', cwe_2='WBC/HPF', cwe_3='LN')
        obx_7.obx_5 = '50'
        obx_7.units = CWE(cwe_1='/HPF')
        obx_7.reference_range = '0-5'
        obx_7.interpretation_codes = CWE(cwe_1='HH')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5822-2', cwe_2='RBC/HPF', cwe_3='LN')
        obx_8.obx_5 = '10'
        obx_8.units = CWE(cwe_1='/HPF')
        obx_8.reference_range = '0-2'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='5769-5', cwe_2='BACTERIA', cwe_3='LN')
        obx_9.obx_5 = 'MANY'
        obx_9.reference_range = 'NONE'
        obx_9.interpretation_codes = CWE(cwe_1='A')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20250315135000'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
        order_observation.observation_8 = observation_8
        order_observation.observation_9 = observation_9

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MEMORIAL_HERMANN')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MH_EMR')
        msh.date_time_of_message = '20250317160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025031701'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90023456', cx_4='MH_TMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='THORNTON', xpn_2='Carolyn', xpn_3='Marie', xpn_5='Ms.')
        pid.date_time_of_birth = '19450309'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5840 San Felipe St', xad_3='Houston', xad_4='TX', xad_5='77057', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5546203'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6EAST', pl_2='612', pl_3='A', pl_4='MH_TMC', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='3344556', cwe_2='COVINGTON', cwe_3='ARVIND', cwe_4='K', cwe_7='MD')
        pv1.pv1_20 = 'E30405060^^^MH_TMC^VN'
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
        orc.placer_order_number = EI(ei_1='EPO300004', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR300004', ei_2='BEAKER')
        orc.orc_7 = '^^^20250315080000^^R'
        orc.date_time_of_order_event = '20250317160000'
        orc.orc_12 = '3344556^COVINGTON^ARVIND^K^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO300004', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR300004', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='87086', cwe_2='URINE CULTURE', cwe_3='CPT')
        obr.observation_date_time = '20250315080000'
        obr.obr_16 = '3344556^COVINGTON^ARVIND^K^^^MD'
        obr.results_rpt_status_chng_date_time = '20250317155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='BACTERIA IDENTIFIED', cwe_3='LN')
        obx.obx_5 = 'ESCHERICHIA COLI'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-5', cwe_2='COLONY COUNT', cwe_3='LN')
        obx_2.obx_5 = '>100,000 CFU/mL'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18893-7', cwe_2='AMPICILLIN', cwe_3='LN')
        obx_3.obx_5 = 'R^Resistant'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18894-5', cwe_2='AMOXICILLIN-CLAVULANATE', cwe_3='LN')
        obx_4.obx_5 = 'S^Susceptible'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18895-2', cwe_2='CEFTRIAXONE', cwe_3='LN')
        obx_5.obx_5 = 'S^Susceptible'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18896-0', cwe_2='CIPROFLOXACIN', cwe_3='LN')
        obx_6.obx_5 = 'R^Resistant'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18897-8', cwe_2='NITROFURANTOIN', cwe_3='LN')
        obx_7.obx_5 = 'S^Susceptible'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='18928-1', cwe_2='TRIMETHOPRIM-SULFAMETHOXAZOLE', cwe_3='LN')
        obx_8.obx_5 = 'S^Susceptible'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250317150000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
        order_observation.observation_8 = observation_8

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='BAYLOR_DALLAS')
        msh.receiving_application = HD(hd_1='LAB_AUTO')
        msh.receiving_facility = HD(hd_1='BAYLOR_LAB')
        msh.date_time_of_message = '20250320091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC2025032001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90034567', cx_4='BAYLOR_DALLAS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CHILDRESS', xpn_2='Darnell', xpn_3='Wayne', xpn_5='Mr.')
        pid.date_time_of_birth = '19680801'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3814 Kiest Blvd', xad_3='Dallas', xad_4='TX', xad_5='75233', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^469^5529871'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CVICU', pl_2='105', pl_3='A', pl_4='BAYLOR_DALLAS', pl_8='CVICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '4455667^CARMICHAEL^PRIYA^V^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4455667', cwe_2='CARMICHAEL', cwe_3='PRIYA', cwe_4='V', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E40506070', xcn_4='BAYLOR_DALLAS', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='CIGNA')

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
        orc.placer_order_number = EI(ei_1='EPO400005', ei_2='EPIC')
        orc.orc_7 = '^^^20250320100000^^S'
        orc.date_time_of_order_event = '20250320091500'
        orc.orc_10 = 'NURSE03^KINGSLEY^ROSA^A^^^RN'
        orc.orc_12 = '4455667^CARMICHAEL^PRIYA^V^^^MD'
        orc.enterers_location = PL(pl_1='CVICU', pl_2='105', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='BAYLOR_DALLAS')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO400005', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='85610', cwe_2='PROTHROMBIN TIME', cwe_3='CPT')
        obr.observation_date_time = '20250320091500'
        obr.obr_16 = '4455667^CARMICHAEL^PRIYA^V^^^MD'
        obr.results_rpt_status_chng_date_time = '20250320100000'
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
        obr_2.placer_order_number = EI(ei_1='EPO400005', ei_2='EPIC')
        obr_2.universal_service_identifier = CWE(cwe_1='85730', cwe_2='PARTIAL THROMBOPLASTIN TIME', cwe_3='CPT')
        obr_2.observation_date_time = '20250320091500'
        obr_2.obr_16 = '4455667^CARMICHAEL^PRIYA^V^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250320100000'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='Atherosclerotic heart disease', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_HOUSTON')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='METH_EMR')
        msh.date_time_of_message = '20250322041500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025032201'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90045678', cx_4='METH_HOUSTON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='QUINTERO', xpn_2='Raul', xpn_3='Esteban', xpn_5='Mr.')
        pid.date_time_of_birth = '19710416'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1923 Binz St', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^281^5537614'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED12', pl_3='A', pl_4='METH_HOUSTON', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '5566778^WENTWORTH^BRIAN^T^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='5566778', cwe_2='WENTWORTH', cwe_3='BRIAN', cwe_4='T', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E50607080', xcn_4='METH_HOUSTON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='UNITED')

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
        orc.placer_order_number = EI(ei_1='EPO500006', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR500006', ei_2='BEAKER')
        orc.orc_7 = '^^^20250322030000^^S'
        orc.date_time_of_order_event = '20250322041500'
        orc.orc_12 = '5566778^WENTWORTH^BRIAN^T^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO500006', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR500006', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='49563-0', cwe_2='TROPONIN I HIGH SENSITIVITY', cwe_3='LN')
        obr.observation_date_time = '20250322030000'
        obr.obr_16 = '5566778^WENTWORTH^BRIAN^T^^^MD'
        obr.results_rpt_status_chng_date_time = '20250322041000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='TROPONIN I HS - 0HR', cwe_3='LN')
        obx.obx_5 = '245'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '0-19'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322033000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='49563-0', cwe_2='TROPONIN I HS - 3HR', cwe_3='LN')
        obx_2.obx_5 = '1890'
        obx_2.units = CWE(cwe_1='ng/L')
        obx_2.reference_range = '0-19'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322041000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33762-6', cwe_2='NT-proBNP', cwe_3='LN')
        obx_3.obx_5 = '4500'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '0-300'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322033500'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MDACC_EMR')
        msh.date_time_of_message = '20250325143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025032501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90001234', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HOANG', xpn_2='Mei', xpn_3='Suyin', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5518742'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='L10N', pl_2='1002', pl_3='A', pl_4='MDACC', pl_8='LEUKEMIA')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '1112233^RUTHERFORD^JAMES^L^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='1112233', cwe_2='RUTHERFORD', cwe_3='JAMES', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E10203040', xcn_4='MDACC', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='EPO600007', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR600007', ei_2='BEAKER')
        orc.orc_7 = '^^^20250323^^R'
        orc.date_time_of_order_event = '20250325143000'
        orc.orc_12 = '1112233^RUTHERFORD^JAMES^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO600007', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR600007', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='38033-4', cwe_2='FLOW CYTOMETRY', cwe_3='LN')
        obr.observation_date_time = '20250323100000'
        obr.obr_16 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250325140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Flow Cytometry Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDc1ID4+CnN0cmVhbQpCVAovRjEgMTYgVGYKNzIgNzIwIFRkCihGbG93IEN5dG9tZXRyeSBSZXBvcnQgLSBBY3V0ZSBMeW1waG9ibGFz'
            'dGljIExldWtlbWlhKSBUagpFVAplbmRzdHJlYW0KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250325140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='38033-4', cwe_2='FLOW CYTOMETRY INTERPRETATION', cwe_3='LN')
        obx_2.obx_5 = (
            'SPECIMEN: Peripheral blood\\.br\\\\.br\\FINDINGS:\\.br\\Blast population identified comprising 78% of analyzed events.\\.br\\Immunophenotype: CD'
            '10+, CD19+, CD20 dim, CD34+, TdT+, CD45 dim\\.br\\Consistent with B-lymphoblastic leukemia/lymphoma\\.br\\\\.br\\INTERPRETATION:\\.br\\Flow cyto'
            'metry findings consistent with B-ALL. Correlate with morphology and cytogenetics.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250325140000'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='TEXAS_CHILDRENS')
        msh.receiving_application = HD(hd_1='BB_SYS')
        msh.receiving_facility = HD(hd_1='TCH_BLOODBANK')
        msh.date_time_of_message = '20250328110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC2025032801'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90012345', cx_4='TCH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BROADNAX', xpn_2='Elijah', xpn_3='Tyrese', xpn_5='')
        pid.date_time_of_birth = '20180605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6712 Reed Rd', xad_3='Houston', xad_4='TX', xad_5='77033', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5573948'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PICU', pl_2='305', pl_3='B', pl_4='TCH', pl_8='PICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '2233445^HAWTHORNE^DANIELLE^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='HAWTHORNE', cwe_3='DANIELLE', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E20304050', xcn_4='TCH', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        orc.orc_7 = '^^^20250328113000^^S'
        orc.date_time_of_order_event = '20250328110000'
        orc.orc_10 = 'NURSE04^ALDERTON^LUCIA^L^^^RN'
        orc.orc_12 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        orc.enterers_location = PL(pl_1='PICU', pl_2='305', pl_3='B')
        orc.order_control_code_reason = CWE(cwe_1='TCH')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='86900', cwe_2='BLOOD TYPE ABO', cwe_3='CPT')
        obr.observation_date_time = '20250328110000'
        obr.obr_16 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250328113000'
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
        obr_2.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        obr_2.universal_service_identifier = CWE(cwe_1='86901', cwe_2='BLOOD TYPE RH', cwe_3='CPT')
        obr_2.observation_date_time = '20250328110000'
        obr_2.obr_16 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250328113000'
        obr_2.result_status = 'F'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        obr_3.universal_service_identifier = CWE(cwe_1='86850', cwe_2='ANTIBODY SCREEN', cwe_3='CPT')
        obr_3.observation_date_time = '20250328110000'
        obr_3.obr_16 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        obr_3.results_rpt_status_chng_date_time = '20250328113000'
        obr_3.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='D61.9', cwe_2='Aplastic anemia, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, dg1]

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='TEXAS_CHILDRENS')
        msh.receiving_application = HD(hd_1='BB_RECV')
        msh.receiving_facility = HD(hd_1='TCH_EMR')
        msh.date_time_of_message = '20250328133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025032802'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90012345', cx_4='TCH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BROADNAX', xpn_2='Elijah', xpn_3='Tyrese', xpn_5='')
        pid.date_time_of_birth = '20180605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6712 Reed Rd', xad_3='Houston', xad_4='TX', xad_5='77033', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5573948'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PICU', pl_2='305', pl_3='B', pl_4='TCH', pl_8='PICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '2233445^HAWTHORNE^DANIELLE^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='HAWTHORNE', cwe_3='DANIELLE', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E20304050', xcn_4='TCH', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR700008', ei_2='BEAKER')
        orc.orc_7 = '^^^20250328113000^^S'
        orc.date_time_of_order_event = '20250328133000'
        orc.orc_12 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO700008', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR700008', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='86900', cwe_2='BLOOD TYPE ABO', cwe_3='CPT')
        obr.observation_date_time = '20250328110000'
        obr.obr_16 = '2233445^HAWTHORNE^DANIELLE^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250328132000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO GROUP', cwe_3='LN')
        obx.obx_5 = 'O'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250328130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='RH TYPE', cwe_3='LN')
        obx_2.obx_5 = 'POSITIVE'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250328130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='890-4', cwe_2='ANTIBODY SCREEN', cwe_3='LN')
        obx_3.obx_5 = 'NEGATIVE'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250328130000'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='UT_SOUTHWESTERN')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='UTSW_EMR')
        msh.date_time_of_message = '20250401094500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025040101'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90056789', cx_4='UTSW', cx_5='MR')
        pid.patient_name = XPN(xpn_1='NAKAMURA', xpn_2='Kenji', xpn_3='Hiroshi', xpn_5='Mr.')
        pid.date_time_of_birth = '19650728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2915 Maple Ave', xad_3='Dallas', xad_4='TX', xad_5='75201', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5584326'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='EXAM2', pl_3='A', pl_4='UTSW', pl_8='ENDOCRINE')
        pv1.hospital_service = CWE(cwe_1='ENDO')
        pv1.patient_type = CWE(cwe_1='6677889', cwe_2='MERRIFIELD', cwe_3='KATHERINE', cwe_4='L', cwe_7='MD')
        pv1.pv1_20 = 'E60708090^^^UTSW^VN'
        pv1.charge_price_indicator = CWE(cwe_1='AETNA')

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
        orc.placer_order_number = EI(ei_1='EPO800009', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR800009', ei_2='BEAKER')
        orc.orc_7 = '^^^20250401080000^^R'
        orc.date_time_of_order_event = '20250401094500'
        orc.orc_12 = '6677889^MERRIFIELD^KATHERINE^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO800009', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR800009', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obr.observation_date_time = '20250401080000'
        obr.obr_16 = '6677889^MERRIFIELD^KATHERINE^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250401093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obx.obx_5 = '9.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-5.6'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250401093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='27353-2', cwe_2='ESTIMATED AVERAGE GLUCOSE', cwe_3='LN')
        obx_2.obx_5 = '217'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250401093000'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='TEXAS_CHILDRENS')
        msh.receiving_application = HD(hd_1='LAB_ADT')
        msh.receiving_facility = HD(hd_1='TCH_LAB')
        msh.date_time_of_message = '20250405001200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EPIC2025040501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250405001200'
        evn.evn_5 = 'NCHARGE01^PRESCOTT^VALERIE^A^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90067890', cx_4='TCH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CISNEROS', xpn_2='Baby Boy', xpn_4='')
        pid.date_time_of_birth = '20250405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='8307 Glenview Dr', xad_3='San Antonio', xad_4='TX', xad_5='78240', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5517893'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CISNEROS', xpn_2='Adriana', xpn_3='Renee', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='8307 Glenview Dr', xad_3='San Antonio', xad_4='TX', xad_5='78240', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^210^5517893'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='N201', pl_3='A', pl_4='TCH', pl_8='NICU')
        pv1.admission_type = CWE(cwe_1='N', cwe_2='Newborn')
        pv1.pv1_7 = '7788990^STRATTON^FATIMA^Z^^^MD^ATTENDING'
        pv1.pv1_8 = '7788990^STRATTON^FATIMA^Z^^^MD'
        pv1.preadmit_test_indicator = CWE(cwe_1='NEWBORN')
        pv1.vip_indicator = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='A0')
        pv1.patient_type = CWE(cwe_1='7788990', cwe_2='STRATTON', cwe_3='FATIMA', cwe_4='Z', cwe_7='MD')
        pv1.pv1_20 = 'E70809010^^^TCH^VN'
        pv1.charge_price_indicator = CWE(cwe_1='MEDICAID')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='P07.30', cwe_2='Preterm newborn, unspecified weeks of gestation', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='TEXAS_CHILDRENS')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='TCH_EMR')
        msh.date_time_of_message = '20250408102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025040801'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90067890', cx_4='TCH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CISNEROS', xpn_2='Baby Boy', xpn_4='')
        pid.date_time_of_birth = '20250405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='8307 Glenview Dr', xad_3='San Antonio', xad_4='TX', xad_5='78240', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5517893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='N201', pl_3='A', pl_4='TCH', pl_8='NICU')
        pv1.admission_type = CWE(cwe_1='N', cwe_2='Newborn')
        pv1.pv1_7 = '7788990^STRATTON^FATIMA^Z^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='7788990', cwe_2='STRATTON', cwe_3='FATIMA', cwe_4='Z', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E70809010', xcn_4='TCH', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='EPO900010', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR900010', ei_2='BEAKER')
        orc.orc_7 = '^^^20250406^^R'
        orc.date_time_of_order_event = '20250408102000'
        orc.orc_12 = '7788990^STRATTON^FATIMA^Z^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO900010', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR900010', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='NEWBORN SCREEN PANEL', cwe_3='LN')
        obr.observation_date_time = '20250406050000'
        obr.obr_16 = '7788990^STRATTON^FATIMA^Z^^^MD'
        obr.results_rpt_status_chng_date_time = '20250408100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='54090-6', cwe_2='PHENYLKETONURIA', cwe_3='LN')
        obx.obx_5 = 'NEGATIVE'
        obx.reference_range = 'NEGATIVE'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='54079-9', cwe_2='CONGENITAL HYPOTHYROIDISM', cwe_3='LN')
        obx_2.obx_5 = 'NEGATIVE'
        obx_2.reference_range = 'NEGATIVE'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='54081-5', cwe_2='HEMOGLOBINOPATHY', cwe_3='LN')
        obx_3.obx_5 = 'FA (normal newborn pattern)'
        obx_3.reference_range = 'FA'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='54088-0', cwe_2='GALACTOSEMIA', cwe_3='LN')
        obx_4.obx_5 = 'NEGATIVE'
        obx_4.reference_range = 'NEGATIVE'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='57084-6', cwe_2='CYSTIC FIBROSIS', cwe_3='LN')
        obx_5.obx_5 = 'NEGATIVE'
        obx_5.reference_range = 'NEGATIVE'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='54078-1', cwe_2='CONGENITAL ADRENAL HYPERPLASIA', cwe_3='LN')
        obx_6.obx_5 = 'NEGATIVE'
        obx_6.reference_range = 'NEGATIVE'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250408090000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='54091-4', cwe_2='BIOTINIDASE DEFICIENCY', cwe_3='LN')
        obx_7.obx_5 = 'NEGATIVE'
        obx_7.reference_range = 'NEGATIVE'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250408090000'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MDACC_EMR')
        msh.date_time_of_message = '20250410160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025041001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90078901', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CALLAWAY', xpn_2='Rebecca', xpn_3='Diane', xpn_5='Mrs.')
        pid.date_time_of_birth = '19720314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3750 University Blvd', xad_3='Houston', xad_4='TX', xad_5='77005', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5592047'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='BRST', pl_2='405', pl_3='A', pl_4='MDACC', pl_8='BREAST_ONC')
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='8899001', cwe_2='ASHFORD', cwe_3='JENNIFER', cwe_4='C', cwe_7='MD', cwe_8='ONCOLOGIST')
        pv1.pv1_20 = 'E80901020^^^MDACC^VN'
        pv1.charge_price_indicator = CWE(cwe_1='CIGNA')

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
        orc.placer_order_number = EI(ei_1='EPO010011', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR010011', ei_2='BEAKER')
        orc.orc_7 = '^^^20250405^^R'
        orc.date_time_of_order_event = '20250410160000'
        orc.orc_12 = '8899001^ASHFORD^JENNIFER^C^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO010011', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR010011', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='81519', cwe_2='ONCOTYPE DX BREAST CANCER ASSAY', cwe_3='CPT')
        obr.observation_date_time = '20250405090000'
        obr.obr_16 = '8899001^ASHFORD^JENNIFER^C^^^MD'
        obr.results_rpt_status_chng_date_time = '20250410155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Oncotype DX Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDIg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDEwMiA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjcyIDcyMCBUZAooT25jb3R5cGUgRFggQnJlYXN0IENhbmNlciBBc3NheSBSZXN1bHRz'
            'KSBUagowIDI0IFRkCi9GMSAxMiBUZgooUmVjdXJyZW5jZSBTY29yZTogMTggLSBMb3cgUmlzaykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iag=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250410155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='ONCOTYPE_RS', cwe_2='RECURRENCE SCORE', cwe_3='LOCAL')
        obx_2.obx_5 = '18'
        obx_2.reference_range = '0-100'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250410155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='ONCOTYPE_RISK', cwe_2='RISK CATEGORY', cwe_3='LOCAL')
        obx_3.obx_5 = 'LOW'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250410155000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='ONCOTYPE_INTERP', cwe_2='INTERPRETATION', cwe_3='LOCAL')
        obx_4.obx_5 = (
            'Recurrence Score: 18\\.br\\Risk Category: Low\\.br\\\\.br\\The Recurrence Score result of 18 places this tumor in the low risk category.\\.br\\F'
            'or postmenopausal women with ER+, HER2-, node-negative disease,\\.br\\the TAILORx trial showed minimal benefit from adjuvant chemotherapy\\.br\\'
            'for patients with RS 0-25.'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250410155000'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MEMORIAL_HERMANN')
        msh.receiving_application = HD(hd_1='LAB_AUTO')
        msh.receiving_facility = HD(hd_1='MH_LAB')
        msh.date_time_of_message = '20250412022000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC2025041201'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90089012', cx_4='MH_TMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='ALDRIDGE', xpn_2='Gerald', xpn_3='Thomas', xpn_5='Mr.')
        pid.date_time_of_birth = '19500603'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1420 Montrose Blvd', xad_3='Houston', xad_4='TX', xad_5='77019', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5508371'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MICU', pl_2='801', pl_3='A', pl_4='MH_TMC', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '9900112^HARGROVE^DEEPAK^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='9900112', cwe_2='HARGROVE', cwe_3='DEEPAK', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E90102030', xcn_4='MH_TMC', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='EPO110012', ei_2='EPIC')
        orc.orc_7 = '^^^20250412022500^^S'
        orc.date_time_of_order_event = '20250412022000'
        orc.orc_10 = 'NURSE05^WHITFIELD^ADAEZE^N^^^RN'
        orc.orc_12 = '9900112^HARGROVE^DEEPAK^R^^^MD'
        orc.enterers_location = PL(pl_1='MICU', pl_2='801', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='MH_TMC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO110012', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='82803', cwe_2='ARTERIAL BLOOD GAS', cwe_3='CPT')
        obr.observation_date_time = '20250412022000'
        obr.relevant_clinical_information = CWE(cwe_1='ARTERIAL')
        obr.placer_field_1 = '9900112^HARGROVE^DEEPAK^R^^^MD'
        obr.diagnostic_serv_sect_id = '20250412022500'
        obr.obr_27 = 'S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J96.00', cwe_2='Acute respiratory failure', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MEMORIAL_HERMANN')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='MH_EMR')
        msh.date_time_of_message = '20250412024500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPIC2025041202'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90089012', cx_4='MH_TMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='ALDRIDGE', xpn_2='Gerald', xpn_3='Thomas', xpn_5='Mr.')
        pid.date_time_of_birth = '19500603'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1420 Montrose Blvd', xad_3='Houston', xad_4='TX', xad_5='77019', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5508371'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MICU', pl_2='801', pl_3='A', pl_4='MH_TMC', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '9900112^HARGROVE^DEEPAK^R^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='9900112', cwe_2='HARGROVE', cwe_3='DEEPAK', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E90102030', xcn_4='MH_TMC', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='EPO110012', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR110012', ei_2='BEAKER')
        orc.orc_7 = '^^^20250412022500^^S'
        orc.date_time_of_order_event = '20250412024500'
        orc.orc_12 = '9900112^HARGROVE^DEEPAK^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPO110012', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR110012', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='82803', cwe_2='ARTERIAL BLOOD GAS', cwe_3='CPT')
        obr.observation_date_time = '20250412022000'
        obr.obr_16 = '9900112^HARGROVE^DEEPAK^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250412024000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='PH ARTERIAL', cwe_3='LN')
        obx.obx_5 = '7.28'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250412023500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='PCO2 ARTERIAL', cwe_3='LN')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250412023500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='PO2 ARTERIAL', cwe_3='LN')
        obx_3.obx_5 = '58'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250412023500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='BICARBONATE ARTERIAL', cwe_3='LN')
        obx_4.obx_5 = '25'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250412023500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='O2 SATURATION ARTERIAL', cwe_3='LN')
        obx_5.obx_5 = '88'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '95-100'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250412023500'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1960-4', cwe_2='BASE EXCESS', cwe_3='LN')
        obx_6.obx_5 = '-1.2'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '-2.0-2.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250412023500'

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='BAYLOR_DALLAS')
        msh.receiving_application = HD(hd_1='LAB_ADT')
        msh.receiving_facility = HD(hd_1='BAYLOR_LAB')
        msh.date_time_of_message = '20250415110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EPIC2025041501'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250415110000'
        evn.evn_5 = 'PHARM01^LOCKHART^SANDRA^J^^^PharmD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90034567', cx_4='BAYLOR_DALLAS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CHILDRESS', xpn_2='Darnell', xpn_3='Wayne', xpn_5='Mr.')
        pid.date_time_of_birth = '19680801'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3814 Kiest Blvd', xad_3='Dallas', xad_4='TX', xad_5='75233', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^469^5529871'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CVICU', pl_2='105', pl_3='A', pl_4='BAYLOR_DALLAS', pl_8='CVICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '4455667^CARMICHAEL^PRIYA^V^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4455667', cwe_2='CARMICHAEL', cwe_3='PRIYA', cwe_4='V', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E40506070', xcn_4='BAYLOR_DALLAS', xcn_5='VN')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='70618', cwe_2='PENICILLIN', cwe_3='RXNORM')
        al1.allergy_severity_code = CWE(cwe_1='SV', cwe_2='Severe')
        al1.allergy_reaction_code = 'ANAPHYLAXIS'
        al1.al1_6 = '20100315'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='DA')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='2670', cwe_2='CODEINE', cwe_3='RXNORM')
        al1_2.allergy_severity_code = CWE(cwe_1='MO', cwe_2='Moderate')
        al1_2.allergy_reaction_code = 'NAUSEA, VOMITING'
        al1_2.al1_6 = '20150820'

        # .. build AL1 ..
        al1_3 = AL1()
        al1_3.set_id_al1 = '3'
        al1_3.allergen_type_code = CWE(cwe_1='DA')
        al1_3.allergen_code_mnemonic_description = CWE(cwe_1='82122', cwe_2='IODINATED CONTRAST', cwe_3='RXNORM')
        al1_3.allergy_severity_code = CWE(cwe_1='MI', cwe_2='Mild')
        al1_3.allergy_reaction_code = 'RASH'
        al1_3.al1_6 = '20200112'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.al1 = [al1, al1_2, al1_3]

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='UT_SOUTHWESTERN')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='UTSW_OUTREACH')
        msh.date_time_of_message = '20250418140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EPIC2025041801'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT500123', ei_2='EPIC')
        sch.filler_appointment_id = EI(ei_1='APT500123', ei_2='EPIC')
        sch.schedule_id = CWE(cwe_1='PHLEB', cwe_2='Phlebotomy Draw', cwe_3='LOCAL')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='15', cwe_2='MIN')
        sch.appointment_type = CWE(cwe_1='1')
        sch.appointment_duration_units = CNE(cne_1='BOOKED')
        sch.sch_16 = '0011223^ELLSWORTH^MARCO^M^^^MLT'
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='5541087')
        sch.filler_contact_address = XAD(xad_1='5323 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75390', xad_6='US')
        sch.parent_placer_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90056789', cx_4='UTSW', cx_5='MR')
        pid.patient_name = XPN(xpn_1='NAKAMURA', xpn_2='Kenji', xpn_3='Hiroshi', xpn_5='Mr.')
        pid.date_time_of_birth = '19650728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2915 Maple Ave', xad_3='Dallas', xad_4='TX', xad_5='75201', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5584326'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABDRAW', pl_2='CHAIR3', pl_3='A', pl_4='UTSW', pl_8='OUTREACH')
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='6677889', cwe_2='MERRIFIELD', cwe_3='KATHERINE', cwe_4='L', cwe_7='MD')
        pv1.pv1_20 = 'E60708090^^^UTSW^VN'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='PHLEB')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='PHLEB', cwe_2='Phlebotomy Draw', cwe_3='LOCAL')
        ais.start_date_time = '20250425074500'
        ais.duration = '15^MIN'
        ais.duration_units = CNE(cne_1='15', cne_2='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '0011223^ELLSWORTH^MARCO^M^^^MLT'
        aip.resource_type = CWE(cwe_1='PHLEBOTOMIST')
        aip.resource_group = CWE(cwe_1='20250425074500')
        aip.start_date_time_offset_units = CNE(cne_1='15', cne_2='MIN')

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
        ail.location_resource_id = PL(pl_1='LABDRAW', pl_2='CHAIR3', pl_3='A', pl_4='UTSW')
        ail.location_type_ail = CWE(cwe_1='LAB')

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_AUTO')
        msh.sending_facility = HD(hd_1='BAYLOR_LAB')
        msh.receiving_application = HD(hd_1='EPICBEAKER')
        msh.receiving_facility = HD(hd_1='BAYLOR_DALLAS')
        msh.date_time_of_message = '20250420091234'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'ACK2025042001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AE'
        msa.message_control_id = 'EPIC2025042099'
        msa.msa_3 = 'DUPLICATE ORDER - Order EPO999999 already exists for patient MRN90034567 with same test and collection time'
        msa.expected_sequence_number = '207'

        # .. build ERR ..
        err = ERR()
        err.error_location = ERL(erl_1='ORC', erl_2='1', erl_3='1', erl_4='1')
        err.hl7_error_code = CWE(cwe_1='207', cwe_2='Application internal error', cwe_3='HL70357')
        err.severity = 'E'
        err.user_message = 'Duplicate order detected'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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
    """ Based on live/us-texas/us-texas-epic-beaker.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICBEAKER')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='FIN_SYS')
        msh.receiving_facility = HD(hd_1='MDACC_BILLING')
        msh.date_time_of_message = '20250422163000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'EPIC2025042201'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20250422163000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN90001234', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HOANG', xpn_2='Mei', xpn_3='Suyin', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5518742'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='L10N', pl_2='1002', pl_3='A', pl_4='MDACC', pl_8='LEUKEMIA')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '1112233^RUTHERFORD^JAMES^L^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='1112233', cwe_2='RUTHERFORD', cwe_3='JAMES', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='E10203040', xcn_4='MDACC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='BCBS')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20250325')
        ft1.transaction_batch_id = '20250325143000'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = '38033-4^FLOW CYTOMETRY COMPREHENSIVE^LN'
        ft1.transaction_type = CWE(cwe_1='88187', cwe_2='FLOW CYTOMETRY', cwe_3='CPT')
        ft1.ft1_8 = '1'
        ft1.ft1_11 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        ft1.ordered_by_code = XCN(xcn_1='88187')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20250323')
        ft1_2.transaction_batch_id = '20250323100000'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = '85025^CBC^LN'
        ft1_2.transaction_type = CWE(cwe_1='85025', cwe_2='COMPLETE BLOOD COUNT', cwe_3='CPT')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_11 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        ft1_2.ordered_by_code = XCN(xcn_1='85025')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20250310')
        ft1_3.transaction_batch_id = '20250310060000'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = '85025^CBC^LN'
        ft1_3.transaction_type = CWE(cwe_1='85025', cwe_2='COMPLETE BLOOD COUNT', cwe_3='CPT')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_11 = '1112233^RUTHERFORD^JAMES^L^^^MD'
        ft1_3.ordered_by_code = XCN(xcn_1='85025')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C91.00', cwe_2='Acute lymphoblastic leukemia', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2, financial_3]
        msg.diagnosis = diagnosis

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

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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MOC, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ACK, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, IN1, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-quest.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-quest.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='PREMIER_CARE_DALLAS')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250305080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250305001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88001234', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN12001', cx_4='PREMIER_CARE', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ALVARADO', xpn_2='Maria', xpn_3='Beatriz', xpn_5='Mrs.')
        pid.date_time_of_birth = '19790622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4718 Cedar Springs Rd', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5551234'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='PREMIER_CARE')
        pv1.pv1_7 = '1122334^THORNBERRY^MICHAEL^R^^^MD^PCP'
        pv1.ambulatory_status = CWE(cwe_1='1122334', cwe_2='THORNBERRY', cwe_3='MICHAEL', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV10001', xcn_4='PREMIER_CARE', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='BCBS')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='001', cwe_2='BCBS OF TEXAS')
        in1.insurance_company_id = CX(cx_1='BCBS001')
        in1.insurance_company_name = XON(xon_1='BLUE CROSS BLUE SHIELD OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 660044', xad_3='Dallas', xad_4='TX', xad_5='75266', xad_6='US')
        in1.group_number = 'GRP88888'
        in1.plan_effective_date = '20240101'
        in1.name_of_insured = XPN(xpn_1='ALVARADO', xpn_2='Maria', xpn_3='Beatriz')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19790622'
        in1.insureds_address = XAD(xad_1='4718 Cedar Springs Rd', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US')
        in1.policy_number = 'BCBS456789012'

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='QO100001', ei_2='PREMIER_EMR')
        orc.orc_7 = '^^^20250305^^^R'
        orc.date_time_of_order_event = '20250305080000'
        orc.orc_12 = '1122334^THORNBERRY^MICHAEL^R^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='5559999')
        orc.orc_17 = 'PREMIER_CARE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO100001', ei_2='PREMIER_EMR')
        obr.universal_service_identifier = CWE(cwe_1='83721', cwe_2='LIPID PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250305080000'
        obr.relevant_clinical_information = CWE(cwe_1='FASTING')
        obr.placer_field_1 = '1122334^THORNBERRY^MICHAEL^R^^^MD'
        obr.diagnostic_serv_sect_id = '20250305'
        obr.obr_27 = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E78.5', cwe_2='Hyperlipidemia, unspecified', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-quest.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='PREMIER_CARE_DALLAS')
        msh.date_time_of_message = '20250306141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250306001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88001234', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN12001', cx_4='PREMIER_CARE', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ALVARADO', xpn_2='Maria', xpn_3='Beatriz', xpn_5='Mrs.')
        pid.date_time_of_birth = '19790622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4718 Cedar Springs Rd', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='PREMIER_CARE')
        pv1.pv1_7 = '1122334^THORNBERRY^MICHAEL^R^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='1122334', cwe_2='THORNBERRY', cwe_3='MICHAEL', cwe_4='R', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV10001', xcn_4='PREMIER_CARE', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO100001', ei_2='PREMIER_EMR')
        orc.filler_order_number = EI(ei_1='QR200001', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250305^^^R'
        orc.date_time_of_order_event = '20250306141500'
        orc.orc_12 = '1122334^THORNBERRY^MICHAEL^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO100001', ei_2='PREMIER_EMR')
        obr.filler_order_number = EI(ei_1='QR200001', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='83721', cwe_2='LIPID PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250305080000'
        obr.obr_16 = '1122334^THORNBERRY^MICHAEL^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250306140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='CHOLESTEROL TOTAL', cwe_3='LN')
        obx.obx_5 = '248'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250306120000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='TRIGLYCERIDES', cwe_3='LN')
        obx_2.obx_5 = '185'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250306120000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL CHOLESTEROL', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250306120000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL CHOLESTEROL CALC', cwe_3='LN')
        obx_4.obx_5 = '169'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<100'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250306120000'
        obx_4.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='VLDL CHOLESTEROL', cwe_3='LN')
        obx_5.obx_5 = '37'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '5-40'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250306120000'
        obx_5.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='9830-1', cwe_2='CHOL/HDL RATIO', cwe_3='LN')
        obx_6.obx_5 = '5.9'
        obx_6.reference_range = '<5.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250306120000'
        obx_6.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='AUSTIN_FAMILY_MED')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250310093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250310001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88012345', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN22002', cx_4='AUSTIN_FAM', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='FAIRCLOTH', xpn_2='Cynthia', xpn_3='Elaine', xpn_5='Ms.')
        pid.date_time_of_birth = '19850915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2809 Rio Grande St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^5554567'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='AUSTIN_FAM')
        pv1.pv1_7 = '2233445^VANDERBURG^NISHA^K^^^MD^PCP'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='VANDERBURG', cwe_3='NISHA', cwe_4='K', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV20002', xcn_4='AUSTIN_FAM', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        orc.orc_7 = '^^^20250310^^^R'
        orc.date_time_of_order_event = '20250310093000'
        orc.orc_12 = '2233445^VANDERBURG^NISHA^K^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='512', xtn_7='5559876')
        orc.orc_17 = 'AUSTIN_FAM'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        obr.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH', cwe_3='CPT')
        obr.observation_date_time = '20250310093000'
        obr.obr_16 = '2233445^VANDERBURG^NISHA^K^^^MD'
        obr.results_rpt_status_chng_date_time = '20250310'
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
        obr_2.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        obr_2.universal_service_identifier = CWE(cwe_1='84436', cwe_2='FREE T4', cwe_3='CPT')
        obr_2.observation_date_time = '20250310093000'
        obr_2.obr_16 = '2233445^VANDERBURG^NISHA^K^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250310'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E03.9', cwe_2='Hypothyroidism, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='AUSTIN_FAMILY_MED')
        msh.date_time_of_message = '20250311103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250311001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88012345', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN22002', cx_4='AUSTIN_FAM', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='FAIRCLOTH', xpn_2='Cynthia', xpn_3='Elaine', xpn_5='Ms.')
        pid.date_time_of_birth = '19850915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2809 Rio Grande St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^5554567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='AUSTIN_FAM')
        pv1.pv1_7 = '2233445^VANDERBURG^NISHA^K^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='VANDERBURG', cwe_3='NISHA', cwe_4='K', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV20002', xcn_4='AUSTIN_FAM', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        orc.filler_order_number = EI(ei_1='QR300002', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250310^^^R'
        orc.date_time_of_order_event = '20250311103000'
        orc.orc_12 = '2233445^VANDERBURG^NISHA^K^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        obr.filler_order_number = EI(ei_1='QR300002', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH', cwe_3='CPT')
        obr.observation_date_time = '20250310093000'
        obr.obr_16 = '2233445^VANDERBURG^NISHA^K^^^MD'
        obr.results_rpt_status_chng_date_time = '20250311100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.45'
        obx.units = CWE(cwe_1='uIU/mL')
        obx.reference_range = '0.45-4.50'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250311090000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='QO200002', ei_2='AUSTIN_EMR')
        obr_2.filler_order_number = EI(ei_1='QR300003', ei_2='QUEST_HUB')
        obr_2.universal_service_identifier = CWE(cwe_1='84436', cwe_2='FREE T4', cwe_3='CPT')
        obr_2.observation_date_time = '20250310093000'
        obr_2.obr_16 = '2233445^VANDERBURG^NISHA^K^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250311100000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='FREE T4', cwe_3='LN')
        obx_2.obx_5 = '0.6'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250311090000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_2

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='WOMENS_HEALTH_SA')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250315100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88023456', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN33003', cx_4='WOMENS_SA', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BECERRA', xpn_2='Isabella', xpn_3='Rosario', xpn_5='Mrs.')
        pid.date_time_of_birth = '19950418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='7800 IH 10 West', xad_3='San Antonio', xad_4='TX', xad_5='78230', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5553456'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='WOMENS_SA')
        pv1.pv1_7 = '3344556^WHITFIELD^MARIA^L^^^MD^OBGYN'
        pv1.ambulatory_status = CWE(cwe_1='3344556', cwe_2='WHITFIELD', cwe_3='MARIA', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV30003', xcn_4='WOMENS_SA', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO300003', ei_2='WOMENS_EMR')
        orc.orc_7 = '^^^20250315^^^R'
        orc.date_time_of_order_event = '20250315100000'
        orc.orc_12 = '3344556^WHITFIELD^MARIA^L^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='210', xtn_7='5558765')
        orc.orc_17 = 'WOMENS_SA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO300003', ei_2='WOMENS_EMR')
        obr.universal_service_identifier = CWE(cwe_1='80055', cwe_2='PRENATAL PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250315100000'
        obr.obr_16 = '3344556^WHITFIELD^MARIA^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250315'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z34.00', cwe_2='Encounter for supervision of normal first pregnancy, unspecified trimester', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-quest.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='WOMENS_HEALTH_SA')
        msh.date_time_of_message = '20250317140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250317001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88023456', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN33003', cx_4='WOMENS_SA', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BECERRA', xpn_2='Isabella', xpn_3='Rosario', xpn_5='Mrs.')
        pid.date_time_of_birth = '19950418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='7800 IH 10 West', xad_3='San Antonio', xad_4='TX', xad_5='78230', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5553456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='WOMENS_SA')
        pv1.pv1_7 = '3344556^WHITFIELD^MARIA^L^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='3344556', cwe_2='WHITFIELD', cwe_3='MARIA', cwe_4='L', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV30003', xcn_4='WOMENS_SA', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO300003', ei_2='WOMENS_EMR')
        orc.filler_order_number = EI(ei_1='QR400003', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250315^^^R'
        orc.date_time_of_order_event = '20250317140000'
        orc.orc_12 = '3344556^WHITFIELD^MARIA^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO300003', ei_2='WOMENS_EMR')
        obr.filler_order_number = EI(ei_1='QR400003', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='80055', cwe_2='PRENATAL PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250315100000'
        obr.obr_16 = '3344556^WHITFIELD^MARIA^L^^^MD'
        obr.results_rpt_status_chng_date_time = '20250317133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO GROUP', cwe_3='LN')
        obx.obx_5 = 'A'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250316100000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

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
        obx_2.date_time_of_the_observation = '20250316100000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

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
        obx_3.date_time_of_the_observation = '20250316100000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='718-7', cwe_2='HEMOGLOBIN', cwe_3='LN')
        obx_4.obx_5 = '12.8'
        obx_4.units = CWE(cwe_1='g/dL')
        obx_4.reference_range = '12.0-16.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250316110000'
        obx_4.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='HEMATOCRIT', cwe_3='LN')
        obx_5.obx_5 = '38.2'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '36.0-46.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250316110000'
        obx_5.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5196-1', cwe_2='RUBELLA AB', cwe_3='LN')
        obx_6.obx_5 = 'IMMUNE'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250316120000'
        obx_6.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='5292-8', cwe_2='HEPATITIS B SURFACE AG', cwe_3='LN')
        obx_7.obx_5 = 'NONREACTIVE'
        obx_7.reference_range = 'NONREACTIVE'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250316130000'
        obx_7.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='5195-3', cwe_2='HIV 1/2 AB+AG', cwe_3='LN')
        obx_8.obx_5 = 'NONREACTIVE'
        obx_8.reference_range = 'NONREACTIVE'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250317090000'
        obx_8.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='20507-0', cwe_2='RPR', cwe_3='LN')
        obx_9.obx_5 = 'NONREACTIVE'
        obx_9.reference_range = 'NONREACTIVE'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20250317100000'
        obx_9.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='OCCUPATIONAL_HOUSTON')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250320070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250320001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88034567', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN44004', cx_4='OCC_HOUSTON', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CARRILLO', xpn_2='Carlos', xpn_3='Alejandro', xpn_5='Mr.')
        pid.date_time_of_birth = '19880301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5203 Bellaire Blvd', xad_3='Houston', xad_4='TX', xad_5='77401', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5556789'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='OCC_HOUSTON')
        pv1.pv1_7 = '4455667^ASHWORTH^STEVEN^T^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='4455667', cwe_2='ASHWORTH', cwe_3='STEVEN', cwe_4='T', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV40004', xcn_4='OCC_HOUSTON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SELF_PAY')

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
        orc.placer_order_number = EI(ei_1='QO400004', ei_2='OCC_EMR')
        orc.orc_7 = '^^^20250320^^^R'
        orc.date_time_of_order_event = '20250320070000'
        orc.orc_12 = '4455667^ASHWORTH^STEVEN^T^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='832', xtn_7='5551111')
        orc.orc_17 = 'OCC_HOUSTON'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO400004', ei_2='OCC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='80305', cwe_2='DRUG SCREEN 10 PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250320070000'
        obr.danger_code = CWE(cwe_1='RANDOM')
        obr.obr_17 = '4455667^ASHWORTH^STEVEN^T^^^MD'
        obr.charge_to_practice = MOC(moc_1='20250320')
        obr.parent_result = PRL(prl_1='F')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'PRE-EMPLOYMENT DRUG SCREEN - EMPLOYER: SHELL OIL COMPANY'

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='OCCUPATIONAL_HOUSTON')
        msh.date_time_of_message = '20250321160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250321001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88034567', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN44004', cx_4='OCC_HOUSTON', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CARRILLO', xpn_2='Carlos', xpn_3='Alejandro', xpn_5='Mr.')
        pid.date_time_of_birth = '19880301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5203 Bellaire Blvd', xad_3='Houston', xad_4='TX', xad_5='77401', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5556789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='OCC_HOUSTON')
        pv1.pv1_7 = '4455667^ASHWORTH^STEVEN^T^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='4455667', cwe_2='ASHWORTH', cwe_3='STEVEN', cwe_4='T', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV40004', xcn_4='OCC_HOUSTON', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO400004', ei_2='OCC_EMR')
        orc.filler_order_number = EI(ei_1='QR500004', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250320^^^R'
        orc.date_time_of_order_event = '20250321160000'
        orc.orc_12 = '4455667^ASHWORTH^STEVEN^T^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO400004', ei_2='OCC_EMR')
        obr.filler_order_number = EI(ei_1='QR500004', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='80305', cwe_2='DRUG SCREEN 10 PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250320070000'
        obr.obr_16 = '4455667^ASHWORTH^STEVEN^T^^^MD'
        obr.results_rpt_status_chng_date_time = '20250321155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='3397-7', cwe_2='AMPHETAMINES', cwe_3='LN')
        obx.obx_5 = 'NEGATIVE'
        obx.reference_range = 'NEGATIVE'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321140000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='3398-5', cwe_2='BARBITURATES', cwe_3='LN')
        obx_2.obx_5 = 'NEGATIVE'
        obx_2.reference_range = 'NEGATIVE'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321140000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='3399-3', cwe_2='BENZODIAZEPINES', cwe_3='LN')
        obx_3.obx_5 = 'NEGATIVE'
        obx_3.reference_range = 'NEGATIVE'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321140000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='3426-4', cwe_2='COCAINE METABOLITE', cwe_3='LN')
        obx_4.obx_5 = 'NEGATIVE'
        obx_4.reference_range = 'NEGATIVE'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321140000'
        obx_4.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='3400-9', cwe_2='CANNABINOIDS', cwe_3='LN')
        obx_5.obx_5 = 'NEGATIVE'
        obx_5.reference_range = 'NEGATIVE'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321140000'
        obx_5.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='3773-9', cwe_2='METHADONE', cwe_3='LN')
        obx_6.obx_5 = 'NEGATIVE'
        obx_6.reference_range = 'NEGATIVE'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321140000'
        obx_6.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='19659-2', cwe_2='OPIATES', cwe_3='LN')
        obx_7.obx_5 = 'NEGATIVE'
        obx_7.reference_range = 'NEGATIVE'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250321140000'
        obx_7.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='3835-6', cwe_2='PHENCYCLIDINE', cwe_3='LN')
        obx_8.obx_5 = 'NEGATIVE'
        obx_8.reference_range = 'NEGATIVE'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250321140000'
        obx_8.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='59310-6', cwe_2='OXYCODONE', cwe_3='LN')
        obx_9.obx_5 = 'NEGATIVE'
        obx_9.reference_range = 'NEGATIVE'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20250321140000'
        obx_9.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'ST'
        obx_10.observation_identifier = CWE(cwe_1='72829-8', cwe_2='FENTANYL', cwe_3='LN')
        obx_10.obx_5 = 'NEGATIVE'
        obx_10.reference_range = 'NEGATIVE'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20250321140000'
        obx_10.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

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
        order_observation.observation_10 = observation_10

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='ONCOLOGY_HOUSTON')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250325110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250325001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88045678', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN55005', cx_4='ONC_HOUSTON', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GOODWIN', xpn_2='Stephanie', xpn_3='Renee', xpn_5='Mrs.')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2100 West Loop South', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5559012'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='ONC_HOUSTON')
        pv1.pv1_7 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD^ONCOLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='5566778', cwe_2='BRECKENRIDGE', cwe_3='HASSAN', cwe_4='N', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV50005', xcn_4='ONC_HOUSTON', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO500005', ei_2='ONC_EMR')
        orc.orc_7 = '^^^20250325^^^R'
        orc.date_time_of_order_event = '20250325110000'
        orc.orc_12 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='713', xtn_7='5552222')
        orc.orc_17 = 'ONC_HOUSTON'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO500005', ei_2='ONC_EMR')
        obr.universal_service_identifier = CWE(cwe_1='81162', cwe_2='BRCA1 BRCA2 FULL SEQUENCE', cwe_3='CPT')
        obr.observation_date_time = '20250325110000'
        obr.obr_16 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD'
        obr.results_rpt_status_chng_date_time = '20250325'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z80.3', cwe_2='Family history of malignant neoplasm of breast', cwe_3='ICD10')
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
        nte.comment = 'PATIENT HAS STRONG FAMILY HISTORY: MOTHER AND MATERNAL AUNT WITH BREAST CANCER'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='ONCOLOGY_HOUSTON')
        msh.date_time_of_message = '20250408150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250408001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88045678', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN55005', cx_4='ONC_HOUSTON', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GOODWIN', xpn_2='Stephanie', xpn_3='Renee', xpn_5='Mrs.')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2100 West Loop South', xad_3='Houston', xad_4='TX', xad_5='77027', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5559012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='ONC_HOUSTON')
        pv1.pv1_7 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='5566778', cwe_2='BRECKENRIDGE', cwe_3='HASSAN', cwe_4='N', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV50005', xcn_4='ONC_HOUSTON', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO500005', ei_2='ONC_EMR')
        orc.filler_order_number = EI(ei_1='QR600005', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250325^^^R'
        orc.date_time_of_order_event = '20250408150000'
        orc.orc_12 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO500005', ei_2='ONC_EMR')
        obr.filler_order_number = EI(ei_1='QR600005', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='81162', cwe_2='BRCA1 BRCA2 FULL SEQUENCE', cwe_3='CPT')
        obr.observation_date_time = '20250325110000'
        obr.obr_16 = '5566778^BRECKENRIDGE^HASSAN^N^^^MD'
        obr.results_rpt_status_chng_date_time = '20250408145000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Genetic Testing Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDMg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDk4ID4+CnN0cmVhbQpCVAovRjEgMTggVGYKNzIgNzIwIFRkCihCUkNBMS9CUkNBMiBHZW5ldGljIFRlc3RpbmcgUmVwb3J0KSBUagow'
            'IDI0IFRkCi9GMSAxMiBUZgooUmVzdWx0OiBQYXRob2dlbmljIFZhcmlhbnQgRGV0ZWN0ZWQgLSBCUkNBMSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iag=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250408145000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='BRCA1', cwe_2='BRCA1 GENE', cwe_3='LOCAL')
        obx_2.obx_5 = 'PATHOGENIC VARIANT DETECTED'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250408145000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='BRCA1_VAR', cwe_2='BRCA1 VARIANT', cwe_3='LOCAL')
        obx_3.obx_5 = 'c.5266dupC (p.Gln1756Profs*74)'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250408145000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='BRCA2', cwe_2='BRCA2 GENE', cwe_3='LOCAL')
        obx_4.obx_5 = 'NO PATHOGENIC VARIANT DETECTED'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250408145000'
        obx_4.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='INTERP', cwe_2='INTERPRETATION', cwe_3='LOCAL')
        obx_5.obx_5 = (
            'A pathogenic variant was identified in the BRCA1 gene.\\.br\\This variant is associated with significantly increased lifetime risk\\.br\\for bre'
            'ast cancer (60-80%) and ovarian cancer (40-60%).\\.br\\Genetic counseling is recommended for the patient and at-risk family members.'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250408145000'
        obx_5.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='PLANNED_PARENT_ELP')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250401090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250401001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88056789', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN66006', cx_4='PP_ELPASO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DELEON', xpn_2='Andrea', xpn_3='Valentina', xpn_5='Ms.')
        pid.date_time_of_birth = '20000814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4600 Alberta Ave', xad_3='El Paso', xad_4='TX', xad_5='79905', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^915^5553456'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='PP_ELPASO')
        pv1.pv1_7 = '6677889^CROSSLAND^LUISA^F^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='6677889', cwe_2='CROSSLAND', cwe_3='LUISA', cwe_4='F', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV60006', xcn_4='PP_ELPASO', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        orc.orc_7 = '^^^20250401^^^R'
        orc.date_time_of_order_event = '20250401090000'
        orc.orc_12 = '6677889^CROSSLAND^LUISA^F^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='915', xtn_7='5558888')
        orc.orc_17 = 'PP_ELPASO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr.universal_service_identifier = CWE(cwe_1='87491', cwe_2='CHLAMYDIA NAA', cwe_3='CPT')
        obr.observation_date_time = '20250401090000'
        obr.danger_code = CWE(cwe_1='CERVICAL')
        obr.obr_17 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr.charge_to_practice = MOC(moc_1='20250401')
        obr.parent_result = PRL(prl_1='F')

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
        obr_2.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr_2.universal_service_identifier = CWE(cwe_1='87591', cwe_2='GONORRHEA NAA', cwe_3='CPT')
        obr_2.observation_date_time = '20250401090000'
        obr_2.danger_code = CWE(cwe_1='CERVICAL')
        obr_2.obr_17 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr_2.charge_to_practice = MOC(moc_1='20250401')
        obr_2.parent_result = PRL(prl_1='F')

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr_3.universal_service_identifier = CWE(cwe_1='86780', cwe_2='TREPONEMA PALLIDUM AB', cwe_3='CPT')
        obr_3.observation_date_time = '20250401090000'
        obr_3.obr_16 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr_3.results_rpt_status_chng_date_time = '20250401'
        obr_3.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z11.3', cwe_2='Encounter for screening for STI', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, dg1]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='PLANNED_PARENT_ELP')
        msh.date_time_of_message = '20250403110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250403001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88056789', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN66006', cx_4='PP_ELPASO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DELEON', xpn_2='Andrea', xpn_3='Valentina', xpn_5='Ms.')
        pid.date_time_of_birth = '20000814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4600 Alberta Ave', xad_3='El Paso', xad_4='TX', xad_5='79905', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^915^5553456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='PP_ELPASO')
        pv1.pv1_7 = '6677889^CROSSLAND^LUISA^F^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='6677889', cwe_2='CROSSLAND', cwe_3='LUISA', cwe_4='F', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV60006', xcn_4='PP_ELPASO', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        orc.filler_order_number = EI(ei_1='QR700006', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250401^^^R'
        orc.date_time_of_order_event = '20250403110000'
        orc.orc_12 = '6677889^CROSSLAND^LUISA^F^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr.filler_order_number = EI(ei_1='QR700006', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='87491', cwe_2='CHLAMYDIA NAA', cwe_3='CPT')
        obr.observation_date_time = '20250401090000'
        obr.obr_16 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr.results_rpt_status_chng_date_time = '20250403100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='21613-5', cwe_2='CHLAMYDIA TRACHOMATIS NAA', cwe_3='LN')
        obx.obx_5 = 'DETECTED'
        obx.reference_range = 'NOT DETECTED'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250403090000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr_2.filler_order_number = EI(ei_1='QR700007', ei_2='QUEST_HUB')
        obr_2.universal_service_identifier = CWE(cwe_1='87591', cwe_2='GONORRHEA NAA', cwe_3='CPT')
        obr_2.observation_date_time = '20250401090000'
        obr_2.obr_16 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250403100000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='21415-5', cwe_2='NEISSERIA GONORRHOEAE NAA', cwe_3='LN')
        obx_2.obx_5 = 'NOT DETECTED'
        obx_2.reference_range = 'NOT DETECTED'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250403090000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_2

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='QO600006', ei_2='PP_EMR')
        obr_3.filler_order_number = EI(ei_1='QR700008', ei_2='QUEST_HUB')
        obr_3.universal_service_identifier = CWE(cwe_1='86780', cwe_2='TREPONEMA PALLIDUM AB', cwe_3='CPT')
        obr_3.observation_date_time = '20250401090000'
        obr_3.obr_16 = '6677889^CROSSLAND^LUISA^F^^^MD'
        obr_3.results_rpt_status_chng_date_time = '20250403100000'
        obr_3.result_status = 'F'

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '1'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='22461-8', cwe_2='TREPONEMA PALLIDUM AB', cwe_3='LN')
        obx_3.obx_5 = 'NONREACTIVE'
        obx_3.reference_range = 'NONREACTIVE'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250403090000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation_3 = OruR01OrderObservation()
        order_observation_3.obr = obr_3
        order_observation_3.observation = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation
        patient_result.order_observation_2 = order_observation_2
        patient_result.order_observation_3 = order_observation_3

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='UROLOGY_FW')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250408080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250408002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88067890', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN77007', cx_4='URO_FW', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LASSITER', xpn_2='George', xpn_3='William', xpn_5='Mr.')
        pid.date_time_of_birth = '19560930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='801 W Terrell Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76104', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^817^5556789'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='URO_FW')
        pv1.pv1_7 = '7788990^PEMBERTON^MARK^D^^^MD^UROLOGIST'
        pv1.ambulatory_status = CWE(cwe_1='7788990', cwe_2='PEMBERTON', cwe_3='MARK', cwe_4='D', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV70007', xcn_4='URO_FW', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        orc.orc_7 = '^^^20250408^^^R'
        orc.date_time_of_order_event = '20250408080000'
        orc.orc_12 = '7788990^PEMBERTON^MARK^D^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='817', xtn_7='5553333')
        orc.orc_17 = 'URO_FW'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        obr.universal_service_identifier = CWE(cwe_1='84153', cwe_2='PSA TOTAL', cwe_3='CPT')
        obr.observation_date_time = '20250408080000'
        obr.obr_16 = '7788990^PEMBERTON^MARK^D^^^MD'
        obr.results_rpt_status_chng_date_time = '20250408'
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
        obr_2.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        obr_2.universal_service_identifier = CWE(cwe_1='84154', cwe_2='PSA FREE', cwe_3='CPT')
        obr_2.observation_date_time = '20250408080000'
        obr_2.obr_16 = '7788990^PEMBERTON^MARK^D^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250408'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.5', cwe_2='Encounter for screening for malignant neoplasm of prostate', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='UROLOGY_FW')
        msh.date_time_of_message = '20250409140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250409001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88067890', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN77007', cx_4='URO_FW', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LASSITER', xpn_2='George', xpn_3='William', xpn_5='Mr.')
        pid.date_time_of_birth = '19560930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='801 W Terrell Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76104', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^817^5556789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='URO_FW')
        pv1.pv1_7 = '7788990^PEMBERTON^MARK^D^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='7788990', cwe_2='PEMBERTON', cwe_3='MARK', cwe_4='D', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV70007', xcn_4='URO_FW', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        orc.filler_order_number = EI(ei_1='QR800007', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250408^^^R'
        orc.date_time_of_order_event = '20250409140000'
        orc.orc_12 = '7788990^PEMBERTON^MARK^D^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        obr.filler_order_number = EI(ei_1='QR800007', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='84153', cwe_2='PSA TOTAL', cwe_3='CPT')
        obr.observation_date_time = '20250408080000'
        obr.obr_16 = '7788990^PEMBERTON^MARK^D^^^MD'
        obr.results_rpt_status_chng_date_time = '20250409133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA TOTAL', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.0-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250409120000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='QO700007', ei_2='URO_EMR')
        obr_2.filler_order_number = EI(ei_1='QR800008', ei_2='QUEST_HUB')
        obr_2.universal_service_identifier = CWE(cwe_1='84154', cwe_2='PSA FREE', cwe_3='CPT')
        obr_2.observation_date_time = '20250408080000'
        obr_2.obr_16 = '7788990^PEMBERTON^MARK^D^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250409133000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10886-0', cwe_2='PSA FREE', cwe_3='LN')
        obx_2.obx_5 = '1.2'
        obx_2.units = CWE(cwe_1='ng/mL')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250409120000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '2'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='12841-3', cwe_2='PSA FREE/TOTAL RATIO', cwe_3='LN')
        obx_3.obx_5 = '15'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>25'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250409120000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_2
        order_observation_2.observation_2 = observation_3

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='INTERNAL_MED_PLANO')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250412083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250412001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88078901', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN88008', cx_4='IM_PLANO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PADMANABHAN', xpn_2='Priya', xpn_3='Lakshmi', xpn_5='Mrs.')
        pid.date_time_of_birth = '19780205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3201 Preston Rd', xad_3='Plano', xad_4='TX', xad_5='75093', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^972^5551234'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='IM_PLANO')
        pv1.pv1_7 = '8899001^DRUMMOND^DEEPAK^M^^^MD^PCP'
        pv1.ambulatory_status = CWE(cwe_1='8899001', cwe_2='DRUMMOND', cwe_3='DEEPAK', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV80008', xcn_4='IM_PLANO', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        orc.orc_7 = '^^^20250412^^^R'
        orc.date_time_of_order_event = '20250412083000'
        orc.orc_12 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='972', xtn_7='5559999')
        orc.orc_17 = 'IM_PLANO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        obr.universal_service_identifier = CWE(cwe_1='82306', cwe_2='VITAMIN D 25-HYDROXY', cwe_3='CPT')
        obr.observation_date_time = '20250412083000'
        obr.obr_16 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        obr.results_rpt_status_chng_date_time = '20250412'
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
        obr_2.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        obr_2.universal_service_identifier = CWE(cwe_1='82607', cwe_2='VITAMIN B12', cwe_3='CPT')
        obr_2.observation_date_time = '20250412083000'
        obr_2.obr_16 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250412'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R53.83', cwe_2='Other fatigue', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='INTERNAL_MED_PLANO')
        msh.date_time_of_message = '20250414100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250414001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88078901', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN88008', cx_4='IM_PLANO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PADMANABHAN', xpn_2='Priya', xpn_3='Lakshmi', xpn_5='Mrs.')
        pid.date_time_of_birth = '19780205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3201 Preston Rd', xad_3='Plano', xad_4='TX', xad_5='75093', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^972^5551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='IM_PLANO')
        pv1.pv1_7 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='8899001', cwe_2='DRUMMOND', cwe_3='DEEPAK', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV80008', xcn_4='IM_PLANO', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        orc.filler_order_number = EI(ei_1='QR900008', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250412^^^R'
        orc.date_time_of_order_event = '20250414100000'
        orc.orc_12 = '8899001^DRUMMOND^DEEPAK^M^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        obr.filler_order_number = EI(ei_1='QR900008', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='82306', cwe_2='VITAMIN D 25-HYDROXY', cwe_3='CPT')
        obr.observation_date_time = '20250412083000'
        obr.obr_16 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        obr.results_rpt_status_chng_date_time = '20250414093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='VITAMIN D 25-HYDROXY', cwe_3='LN')
        obx.obx_5 = '14'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '30-100'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250413150000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='QO800008', ei_2='IM_EMR')
        obr_2.filler_order_number = EI(ei_1='QR900009', ei_2='QUEST_HUB')
        obr_2.universal_service_identifier = CWE(cwe_1='82607', cwe_2='VITAMIN B12', cwe_3='CPT')
        obr_2.observation_date_time = '20250412083000'
        obr_2.obr_16 = '8899001^DRUMMOND^DEEPAK^M^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250414093000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2132-9', cwe_2='VITAMIN B12', cwe_3='LN')
        obx_2.obx_5 = '180'
        obx_2.units = CWE(cwe_1='pg/mL')
        obx_2.reference_range = '200-900'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250413150000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_2

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='URGENT_CARE_ARLINGTON')
        msh.date_time_of_message = '20250418160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250418001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88089012', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN99009', cx_4='UC_ARLINGTON', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='HAYWOOD', xpn_2='Jennifer', xpn_3='Louise', xpn_5='Ms.')
        pid.date_time_of_birth = '19920207'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1500 E Lamar Blvd', xad_3='Arlington', xad_4='TX', xad_5='76011', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^817^5550123'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='UC_ARLINGTON')
        pv1.pv1_7 = '9900112^KIRKPATRICK^JONATHAN^P^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='9900112', cwe_2='KIRKPATRICK', cwe_3='JONATHAN', cwe_4='P', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV90009', xcn_4='UC_ARLINGTON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='AETNA')

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
        orc.placer_order_number = EI(ei_1='QO900009', ei_2='UC_EMR')
        orc.filler_order_number = EI(ei_1='QR010009', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250417^^^R'
        orc.date_time_of_order_event = '20250418160000'
        orc.orc_12 = '9900112^KIRKPATRICK^JONATHAN^P^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO900009', ei_2='UC_EMR')
        obr.filler_order_number = EI(ei_1='QR010009', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='87635', cwe_2='SARS-COV-2 RNA NAA', cwe_3='CPT')
        obr.observation_date_time = '20250417140000'
        obr.danger_code = CWE(cwe_1='NASAL SWAB')
        obr.obr_17 = '9900112^KIRKPATRICK^JONATHAN^P^^^MD'
        obr.charge_to_practice = MOC(moc_1='20250418155000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='COVID-19 Test Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDg1ID4+CnN0cmVhbQpCVAovRjEgMTYgVGYKNzIgNzIwIFRkCihTQVJTLUNvVi0yIFJULVBDUiBUZXN0IFJlcG9ydCkgVGoKMCAyNCBU'
            'ZAooUmVzdWx0OiBOb3QgRGV0ZWN0ZWQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmo='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250418155000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-COV-2 RNA', cwe_3='LN')
        obx_2.obx_5 = 'NOT DETECTED'
        obx_2.reference_range = 'NOT DETECTED'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250418150000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_MOLECULAR')

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='ALLERGY_HOUSTON')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250420100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'QST20250420001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88090123', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN10010', cx_4='ALLERGY_H', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='KIMBLE', xpn_2='Taylor', xpn_3='Simone', xpn_5='Ms.')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9900 Memorial Dr', xad_3='Houston', xad_4='TX', xad_5='77024', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5554567'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='ALLERGY_H')
        pv1.pv1_7 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD^ALLERGIST'
        pv1.ambulatory_status = CWE(cwe_1='0011223', cwe_2='HOLLINGSWORTH', cwe_3='MARIA', cwe_4='C', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV10010', xcn_4='ALLERGY_H', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='BCBS')

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
        nk1.name = XPN(xpn_1='KIMBLE', xpn_2='David', xpn_3='R', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='9900 Memorial Dr', xad_3='Houston', xad_4='TX', xad_5='77024', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^713^5554567'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='QO010010', ei_2='ALLERGY_EMR')
        orc.orc_7 = '^^^20250420^^^R'
        orc.date_time_of_order_event = '20250420100000'
        orc.orc_12 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD'
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='713', xtn_7='5557777')
        orc.orc_17 = 'ALLERGY_H'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO010010', ei_2='ALLERGY_EMR')
        obr.universal_service_identifier = CWE(cwe_1='86003', cwe_2='ALLERGEN SPECIFIC IGE PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250420100000'
        obr.obr_16 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD'
        obr.results_rpt_status_chng_date_time = '20250420'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J30.1', cwe_2='Allergic rhinitis due to pollen', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [nk1, orc, obr, dg1]

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_HUB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLINIC_EMR')
        msh.receiving_facility = HD(hd_1='ALLERGY_HOUSTON')
        msh.date_time_of_message = '20250423140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QST20250423001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='QST88090123', cx_4='QUEST', cx_5='PI'), CX(cx_1='MRN10010', cx_4='ALLERGY_H', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='KIMBLE', xpn_2='Taylor', xpn_3='Simone', xpn_5='Ms.')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9900 Memorial Dr', xad_3='Houston', xad_4='TX', xad_5='77024', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5554567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_3='A', pl_4='ALLERGY_H')
        pv1.pv1_7 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='0011223', cwe_2='HOLLINGSWORTH', cwe_3='MARIA', cwe_4='C', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='QV10010', xcn_4='ALLERGY_H', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='QO010010', ei_2='ALLERGY_EMR')
        orc.filler_order_number = EI(ei_1='QR110010', ei_2='QUEST_HUB')
        orc.orc_7 = '^^^20250420^^^R'
        orc.date_time_of_order_event = '20250423140000'
        orc.orc_12 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QO010010', ei_2='ALLERGY_EMR')
        obr.filler_order_number = EI(ei_1='QR110010', ei_2='QUEST_HUB')
        obr.universal_service_identifier = CWE(cwe_1='86003', cwe_2='ALLERGEN SPECIFIC IGE PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250420100000'
        obr.obr_16 = '0011223^HOLLINGSWORTH^MARIA^C^^^MD'
        obr.results_rpt_status_chng_date_time = '20250423133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6844-5', cwe_2='TOTAL IGE', cwe_3='LN')
        obx.obx_5 = '450'
        obx.units = CWE(cwe_1='IU/mL')
        obx.reference_range = '0-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250423100000'
        obx.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6095-4', cwe_2='CAT DANDER IGE', cwe_3='LN')
        obx_2.obx_5 = '12.5'
        obx_2.units = CWE(cwe_1='kU/L')
        obx_2.reference_range = '<0.35'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250423100000'
        obx_2.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6085-5', cwe_2='DUST MITE IGE', cwe_3='LN')
        obx_3.obx_5 = '28.7'
        obx_3.units = CWE(cwe_1='kU/L')
        obx_3.reference_range = '<0.35'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250423100000'
        obx_3.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6189-5', cwe_2='GRASS MIX IGE', cwe_3='LN')
        obx_4.obx_5 = '8.9'
        obx_4.units = CWE(cwe_1='kU/L')
        obx_4.reference_range = '<0.35'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250423100000'
        obx_4.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6206-7', cwe_2='OAK TREE IGE', cwe_3='LN')
        obx_5.obx_5 = '15.3'
        obx_5.units = CWE(cwe_1='kU/L')
        obx_5.reference_range = '<0.35'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250423100000'
        obx_5.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='6027-6', cwe_2='RAGWEED IGE', cwe_3='LN')
        obx_6.obx_5 = '22.1'
        obx_6.units = CWE(cwe_1='kU/L')
        obx_6.reference_range = '<0.35'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250423100000'
        obx_6.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='6075-5', cwe_2='MOLD MIX IGE', cwe_3='LN')
        obx_7.obx_5 = '0.2'
        obx_7.units = CWE(cwe_1='kU/L')
        obx_7.reference_range = '<0.35'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250423100000'
        obx_7.responsible_observer = XCN(xcn_1='QUEST_TX_LAB')

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
    """ Based on live/us-texas/us-texas-quest.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIC_EMR')
        msh.sending_facility = HD(hd_1='PREMIER_CARE_DALLAS')
        msh.receiving_application = HD(hd_1='QUEST_HUB')
        msh.receiving_facility = HD(hd_1='QUEST_TX')
        msh.date_time_of_message = '20250306141530'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'ACK20250306001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'QST20250306001'
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

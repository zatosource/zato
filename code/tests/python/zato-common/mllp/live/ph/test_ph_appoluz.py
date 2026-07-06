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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, EI, FC, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05Insurance, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ph', 'ph-appoluz.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ph/ph-appoluz.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250601080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'APZ-MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250601080000'
        evn.operator_id = XCN(xcn_1='VILLANUEVA', xcn_2='ARMANDO', xcn_3='REYES', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='OLLH-20250601-0022', cx_4='OLLH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGBANUA', xpn_2='ERNESTO', xpn_3='CALUPITAN')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 V. Mapa St', xad_3='Sta. Mesa', xad_4='NCR', xad_5='1016', xad_6='PH')
        pid.pid_13 = '+63-2-8714-9021~+63-917-345-6712'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH401234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='OLLH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.pv1_8 = 'CASANOVA^MARIBEL^LUNA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'OLLH_MANILA'
        pv1.discharge_date_time = '20250601080000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Congestive heart failure, acute exacerbation')
        pv2.visit_protection_indicator = 'AI'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='MAGBANUA', aui_2='ERNESTO', aui_3='CALUPITAN')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19670415')
        in1.insureds_relationship_to_patient = CWE(cwe_1='88 V. Mapa St', cwe_3='Sta. Mesa', cwe_4='NCR', cwe_5='1016', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH4012345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Heart failure, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250601'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/ph/ph-appoluz.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250601090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APZ-MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='OLLH-20250601-0022', cx_4='OLLH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGBANUA', xpn_2='ERNESTO', xpn_3='CALUPITAN')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 V. Mapa St', xad_3='Sta. Mesa', xad_4='NCR', xad_5='1016', xad_6='PH')
        pid.pid_13 = '+63-2-8714-9021~+63-917-345-6712'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH401234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='OLLH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'OLLH_MANILA'
        pv1.discharge_date_time = '20250601080000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20250601090000'
        orc.orc_10 = 'NURSE^ELENA^CRUZ'
        orc.enterers_location = PL(pl_1='OLLH_MANILA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        obr.universal_service_identifier = CWE(cwe_1='BNP', cwe_2='BNP', cwe_3='L')
        obr.observation_date_time = '20250601090000'
        obr.obr_15 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        obr.result_status = '^^^^^S'

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
        obr_2.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        obr_2.universal_service_identifier = CWE(cwe_1='TROPONIN', cwe_2='Troponin I', cwe_3='L')
        obr_2.observation_date_time = '20250601090000'
        obr_2.obr_15 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        obr_2.result_status = '^^^^^S'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        obr_3.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr_3.observation_date_time = '20250601090000'
        obr_3.obr_15 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        obr_3.result_status = '^^^^^S'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/ph/ph-appoluz.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250601113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='OLLH-20250601-0022', cx_4='OLLH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGBANUA', xpn_2='ERNESTO', xpn_3='CALUPITAN')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 V. Mapa St', xad_3='Sta. Mesa', xad_4='NCR', xad_5='1016', xad_6='PH')
        pid.pid_13 = '+63-2-8714-9021~+63-917-345-6712'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH401234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='OLLH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'OLLH_MANILA'
        pv1.discharge_date_time = '20250601080000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        orc.orc_12 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        obr.universal_service_identifier = CWE(cwe_1='BNP', cwe_2='BNP', cwe_3='L')
        obr.observation_date_time = '20250601090000'
        obr.obr_16 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250601113000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='BNP', cwe_2='B-type Natriuretic Peptide', cwe_3='L')
        obx.obx_5 = '1250'
        obx.units = CWE(cwe_1='pg/mL')
        obx.reference_range = '0-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

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
        obr_2.placer_order_number = EI(ei_1='ORD-APZ-20250601-001')
        obr_2.universal_service_identifier = CWE(cwe_1='TROPONIN', cwe_2='Troponin I', cwe_3='L')
        obr_2.observation_date_time = '20250601090000'
        obr_2.obr_16 = 'VILLANUEVA^ARMANDO^REYES^^^DR^MD'
        obr_2.results_rpt_status_chng_date_time = '20250601113000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='TROP-I', cwe_2='Troponin I', cwe_3='L')
        obx_2.obx_5 = '0.02'
        obx_2.units = CWE(cwe_1='ng/mL')
        obx_2.reference_range = '0.00-0.04'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

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
    """ Based on live/ph/ph-appoluz.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250602083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'APZ-MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250602083000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='FRONT')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250602-0055', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='AMOR', xpn_3='PANGILINAN')
        pid.date_time_of_birth = '19920820'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unit 8, Burgundy Towers', xad_3='Makati', xad_4='NCR', xad_5='1229', xad_6='PH')
        pid.pid_13 = '+63-2-8889-5127~+63-935-208-4455'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH402345678900')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-DIAG', pl_2='001', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250602083000'

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
    """ Based on live/ph/ph-appoluz.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250602110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250602-0055', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='AMOR', xpn_3='PANGILINAN')
        pid.date_time_of_birth = '19920820'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unit 8, Burgundy Towers', xad_3='Makati', xad_4='NCR', xad_5='1229', xad_6='PH')
        pid.pid_13 = '+63-2-8889-5127~+63-935-208-4455'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH402345678900')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-DIAG', pl_2='001', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250602083000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250602-008')
        orc.orc_12 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250602-008')
        obr.universal_service_identifier = CWE(cwe_1='CBC-DIFF', cwe_2='CBC with Differential', cwe_3='L')
        obr.observation_date_time = '20250602090000'
        obr.obr_16 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250602110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Blood Cell Count', cwe_3='L')
        obx.obx_5 = '7.5'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='NEUT', cwe_2='Neutrophils', cwe_3='L')
        obx_2.obx_5 = '0.62'
        obx_2.reference_range = '0.40-0.70'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='LYMPH', cwe_2='Lymphocytes', cwe_3='L')
        obx_3.obx_5 = '0.28'
        obx_3.reference_range = '0.20-0.40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='MONO', cwe_2='Monocytes', cwe_3='L')
        obx_4.obx_5 = '0.06'
        obx_4.reference_range = '0.02-0.08'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='EOS', cwe_2='Eosinophils', cwe_3='L')
        obx_5.obx_5 = '0.03'
        obx_5.reference_range = '0.01-0.06'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='BASO', cwe_2='Basophils', cwe_3='L')
        obx_6.obx_5 = '0.01'
        obx_6.reference_range = '0.00-0.02'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='RBC', cwe_2='Red Blood Cell Count', cwe_3='L')
        obx_7.obx_5 = '4.5'
        obx_7.units = CWE(cwe_1='10*6/uL')
        obx_7.reference_range = '3.80-5.20'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobin', cwe_3='L')
        obx_8.obx_5 = '132'
        obx_8.units = CWE(cwe_1='g/L')
        obx_8.reference_range = '120-160'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrit', cwe_3='L')
        obx_9.obx_5 = '0.40'
        obx_9.units = CWE(cwe_1='L/L')
        obx_9.reference_range = '0.36-0.46'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='L')
        obx_10.obx_5 = '280'
        obx_10.units = CWE(cwe_1='10*3/uL')
        obx_10.reference_range = '150-400'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'

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
    """ Based on live/ph/ph-appoluz.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250603100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APZ-MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4034567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250603-0012', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAQUINIO', xpn_2='GENEROSO', xpn_3='PAGSANJAN')
        pid.date_time_of_birth = '19550710'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='C. Raymundo Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8826-4301~+63-919-607-7788'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH403456789000')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULMO-2A', pl_2='210', pl_3='B', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PULMO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250602180000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250603-005')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250603100000'
        orc.orc_10 = 'NURSE^ROSALINDA^GARCIA'
        orc.enterers_location = PL(pl_1='TMC_PASIG')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250603-005')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT Chest with Contrast', cwe_3='CPT')
        obr.observation_date_time = '20250603100000'
        obr.obr_15 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        obr.result_status = '^^^^^R'

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
    """ Based on live/ph/ph-appoluz.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250603153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4034567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250603-0012', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAQUINIO', xpn_2='GENEROSO', xpn_3='PAGSANJAN')
        pid.date_time_of_birth = '19550710'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='C. Raymundo Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8826-4301~+63-919-607-7788'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH403456789000')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULMO-2A', pl_2='210', pl_3='B', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PULMO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250602180000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250603-005')
        orc.orc_12 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250603-005')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT Chest with Contrast', cwe_3='CPT')
        obr.observation_date_time = '20250603110000'
        obr.obr_16 = 'OCAMPO^ALEJANDRO^BUENAVENTURA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250603153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RAD-IMP', cwe_2='Radiology Impression', cwe_3='L')
        obx.obx_5 = 'Bilateral pleural effusions, moderate. Cardiomegaly. No pulmonary mass lesion identified.'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF-RPT', cwe_2='CT Chest Report', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKENUIENoZXN0IFJlcG9ydCAt'
            'IE1DUCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgow'
            'IDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAw'
            'MDAwMDA0MDcgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0OTgKJSVFT0YK'
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')

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
    """ Based on live/ph/ph-appoluz.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='CDH_CEBU')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDH_CEBU')
        msh.date_time_of_message = '20250604150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'APZ-MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250604150000'
        evn.operator_id = XCN(xcn_1='SARMIENTO', xcn_2='PATRICIA', xcn_3='AGONCILLO', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4045678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDH-20250601-0033', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ESCUETA', xpn_2='FLORA', xpn_3='MACARAEG')
        pid.date_time_of_birth = '19780205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='44 Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-253-7731~+63-928-501-2211'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH404567890100')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='305', pl_3='B', pl_4='CDH_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDH_CEBU'
        pv1.discharge_date_time = '20250601100000'
        pv1.total_charges = '20250604150000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250601'
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
    """ Based on live/ph/ph-appoluz.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250605091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'APZ-MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250605091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='PHIC')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4056789012', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250604-0077', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LACSAMANA', xpn_2='ROMEO', xpn_3='BATUNGBAKAL')
        pid.date_time_of_birth = '19600815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-906-312-5566'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH405678901200')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2B', pl_2='208', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'FERRER^IGNACIO^MAGSAYSAY^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'FERRER^IGNACIO^MAGSAYSAY^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250604080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='LACSAMANA', aui_2='ROMEO', aui_3='BATUNGBAKAL')
        in1.plan_type = CWE(cwe_1='NMP')
        in1.name_of_insured = XPN(xpn_1='19600815')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Taft Ave', cwe_3='Manila', cwe_4='NCR', cwe_5='1000', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH4056789012'

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
    """ Based on live/ph/ph-appoluz.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='SLM_TAGUIG')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='SLM_TAGUIG')
        msh.date_time_of_message = '20250606100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'APZ-MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT-20250610-001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Cardiology follow-up', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20250610090000^20250610093000'
        sch.sch_13 = 'DIZON^FERNANDO^ALONZO^^^DR^MD'
        sch.placer_contact_address = XAD(xad_1='+63-2-8789-7700')
        sch.placer_contact_location = PL(pl_1='SLM CARDIO CLINIC', pl_2='3rd Floor', pl_4='Taguig', pl_5='NCR', pl_6='1634', pl_7='PH')
        sch.filler_contact_person = XCN(xcn_1='SLM_TAGUIG')
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4067890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLM-20250606-0008', cx_4='SLM', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CABRERA', xpn_2='ROSA', xpn_3='ILUSTRE')
        pid.date_time_of_birth = '19720330'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rizal Drive', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8789-7700~+63-917-224-8877'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH406789012300')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='CARD-FU', cwe_2='Cardiology Follow-up', cwe_3='L')
        ais.start_date_time = '20250610090000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'DIZON^FERNANDO^ALONZO^^^DR^MD'
        aip.resource_type = CWE(cwe_1='CARD')
        aip.start_date_time_offset_units = CNE(cne_1='20250610090000')
        aip.allow_substitution_code = CWE(cwe_1='30')
        aip.filler_status_code = CWE(cwe_1='MIN')

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
    """ Based on live/ph/ph-appoluz.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='SLM_QC')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='SLM_QC')
        msh.date_time_of_message = '20250607102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4078901234', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLM-20250607-0019', cx_4='SLM', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PARADO', xpn_2='MICHAEL', xpn_3='FELICIANO')
        pid.date_time_of_birth = '19850512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Timog Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1103', xad_6='PH')
        pid.pid_13 = '+63-2-8867-3333~+63-935-610-2233'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH407890123400')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-EXEC', pl_2='001', pl_4='SLM_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'LIM^JENNY^CHUA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LIM^JENNY^CHUA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLM_QC'
        pv1.discharge_date_time = '20250607080000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250607-003')
        orc.orc_12 = 'LIM^JENNY^CHUA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250607-003')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Fasting Lipid Panel', cwe_3='L')
        obr.observation_date_time = '20250607081500'
        obr.obr_16 = 'LIM^JENNY^CHUA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250607102000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='CHOL', cwe_2='Total Cholesterol', cwe_3='L')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.2'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='TRIG', cwe_2='Triglycerides', cwe_3='L')
        obx_2.obx_5 = '1.9'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<1.7'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HDL', cwe_2='HDL Cholesterol', cwe_3='L')
        obx_3.obx_5 = '1.3'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='LDL', cwe_2='LDL Cholesterol', cwe_3='L')
        obx_4.obx_5 = '3.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.4'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

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
    """ Based on live/ph/ph-appoluz.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250608160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'APZ-MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250608160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4089012345', cx_4='PHIC', cx_5='SS'), CX(cx_1='OLLH-20250605-0044', cx_4='OLLH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TANGILAG', xpn_2='CARMEN', xpn_3='RESURRECCION')
        pid.date_time_of_birth = '19680822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='San Miguel Ave', xad_3='Sta. Mesa', xad_4='NCR', xad_5='1016', xad_6='PH')
        pid.pid_13 = '+63-2-8714-2201~+63-917-888-6677'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH408901234500')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-3A', pl_2='312', pl_3='A', pl_4='OLLH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'PANGILINAN^GREGORIO^MARASIGAN^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'PANGILINAN^GREGORIO^MARASIGAN^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'OLLH_MANILA'
        pv1.discharge_date_time = '20250605090000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PATH', cwe_2='Pathology Report')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20250608150000'
        txa.txa_5 = 'REYES^LILIA^NAVARRO^^^DR^MD'
        txa.transcription_date_time = '20250608160000'
        txa.txa_9 = 'PANGILINAN^GREGORIO^MARASIGAN^^^DR^MD'
        txa.parent_document_number = EI(ei_1='DOC-APZ-20250608-001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PATH-RPT', cwe_2='Pathology Report PDF', cwe_3='L')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFBhdGhvbG9neSBSZXBvcnQg'
            'T0xMSCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgow'
            'IDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAw'
            'MDAwMDA0MDUgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0OTYKJSVFT0YK'
        )
        obx.interpretation_codes = CWE(cwe_1='F')

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
    """ Based on live/ph/ph-appoluz.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250609100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'APZ-MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250609100000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SURG')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4190123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250609-0015', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BALICANTA', xpn_2='DANTE', xpn_3='SORIANO')
        pid.date_time_of_birth = '19750905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Scout Rallos St', xad_3='Quezon City', xad_4='NCR', xad_5='1103', xad_6='PH')
        pid.pid_13 = '+63-2-8928-4611~+63-928-703-1133'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH419012345600')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BALICANTA', xpn_2='LOURDES', xpn_3='REYES')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Scout Rallos St', xad_3='Quezon City', xad_4='NCR', xad_5='1103', xad_6='PH')
        nk1.nk1_5 = '+63-928-703-1134'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG-PRE', pl_2='001', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='PR')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250609100000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='BALICANTA', aui_2='DANTE', aui_3='SORIANO')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19750905')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Scout Rallos St', cwe_3='Quezon City', cwe_4='NCR', cwe_5='1103', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH4190123456'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/ph/ph-appoluz.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250610084500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4190123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250609-0015', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BALICANTA', xpn_2='DANTE', xpn_3='SORIANO')
        pid.date_time_of_birth = '19750905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Scout Rallos St', xad_3='Quezon City', xad_4='NCR', xad_5='1103', xad_6='PH')
        pid.pid_13 = '+63-2-8928-4611~+63-928-703-1133'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH419012345600')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-2A', pl_2='201', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250610060000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250610-002')
        orc.orc_12 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250610-002')
        obr.universal_service_identifier = CWE(cwe_1='BT', cwe_2='Blood Typing and Crossmatch', cwe_3='L')
        obr.observation_date_time = '20250610070000'
        obr.obr_16 = 'MANLAPAZ^RAMON^DALISAY^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250610084500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='ABO', cwe_2='ABO Blood Group', cwe_3='L')
        obx.obx_5 = 'B'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='RH', cwe_2='Rh Factor', cwe_3='L')
        obx_2.obx_5 = 'Positive'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='XMATCH', cwe_2='Crossmatch', cwe_3='L')
        obx_3.obx_5 = 'Compatible with 2 units PRBC'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='AB-SCREEN', cwe_2='Antibody Screen', cwe_3='L')
        obx_4.obx_5 = 'Negative'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

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
    """ Based on live/ph/ph-appoluz.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_RCV')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250611080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'APZ-MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'APZ-MSG-ADT-20250611-001'
        msa.msa_3 = 'Admission processed successfully'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/ph/ph-appoluz.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='CDO_MED')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDO_MED')
        msh.date_time_of_message = '20250612060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'APZ-MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250612060000'
        evn.operator_id = XCN(xcn_1='DUTY', xcn_2='NURSE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4101234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDO-20250610-0044', cx_4='CDO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TALAVERA', xpn_2='BERNARDO', xpn_3='MONTERO')
        pid.date_time_of_birth = '19630720'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Corrales Ave', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-856-1861~+63-919-888-2233'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH410123456700')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OR', pl_2='002', pl_3='A', pl_4='CDO_MED', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.delete_account_indicator = CWE(cwe_1='MED-3A', cwe_2='301', cwe_3='B', cwe_4='CDO_MED', cwe_7='N')
        pv1.account_status = CWE(cwe_1='CDO_MED')
        pv1.current_patient_balance = '20250610120000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-appoluz.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='CDH_CEBU')
        msh.receiving_application = HD(hd_1='PHARM')
        msh.receiving_facility = HD(hd_1='CDH_CEBU')
        msh.date_time_of_message = '20250613140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APZ-MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4112345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDH-20250612-0019', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PACQUIAO', xpn_2='LILIA', xpn_3='MAGTULIS')
        pid.date_time_of_birth = '19700225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-255-9731~+63-928-444-6677'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH411234567800')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-2B', pl_2='215', pl_3='A', pl_4='CDH_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDH_CEBU'
        pv1.discharge_date_time = '20250612080000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250613-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250613140000'
        orc.orc_10 = 'NURSE^ALMA^REYES'
        orc.enterers_location = PL(pl_1='CDH_CEBU')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='TRAM', cwe_2='Tramadol 50mg', cwe_3='L')
        rxo.requested_give_amount_minimum = '50'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='CAP', cwe_2='Capsule')
        rxo.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo.allow_substitutions = '3^TID PRN'
        rxo.rxo_14 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='CEFUR', cwe_2='Cefuroxime 500mg', cwe_3='L')
        rxo_2.requested_give_amount_minimum = '500'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo_2.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo_2.allow_substitutions = '2^BID'
        rxo_2.rxo_14 = 'SARMIENTO^PATRICIA^AGONCILLO^^^DR^MD'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxo_2]

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
    """ Based on live/ph/ph-appoluz.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='DVH_DAVAO')
        msh.receiving_application = HD(hd_1='APPOLUZ')
        msh.receiving_facility = HD(hd_1='DVH_DAVAO')
        msh.date_time_of_message = '20250614160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'APZ-MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4123456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='DVH-20250612-0055', cx_4='DVH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGLALANG', xpn_2='ANTONIO', xpn_3='CORDERO')
        pid.date_time_of_birth = '19680101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='J.P. Laurel Ave', xad_3='Davao', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-227-1861~+63-906-333-7788'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH412345678900')
        pid.mothers_identifier = CX(cx_1='Davao', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-3A', pl_2='310', pl_3='B', pl_4='DVH_DAVAO', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'DVH_DAVAO'
        pv1.discharge_date_time = '20250612120000'

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
        orc.placer_order_number = EI(ei_1='ORD-APZ-20250614-007')
        orc.orc_12 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-APZ-20250614-007')
        obr.universal_service_identifier = CWE(cwe_1='CULT', cwe_2='Wound Culture and Sensitivity', cwe_3='L')
        obr.observation_date_time = '20250613090000'
        obr.obr_16 = 'ESPIRITU^SANTOS^LORENZO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250614160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='ORGANISM', cwe_2='Organism Isolated', cwe_3='L')
        obx.obx_5 = 'Staphylococcus aureus (MSSA)'
        obx.probability = 'N'
        obx.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='AMPI', cwe_2='Ampicillin', cwe_3='L')
        obx_2.obx_5 = 'Sensitive'
        obx_2.probability = 'N'
        obx_2.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='AMCL', cwe_2='Amoxicillin-Clavulanate', cwe_3='L')
        obx_3.obx_5 = 'Sensitive'
        obx_3.probability = 'N'
        obx_3.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='CEPH', cwe_2='Cephalexin', cwe_3='L')
        obx_4.obx_5 = 'Sensitive'
        obx_4.probability = 'N'
        obx_4.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='OXAC', cwe_2='Oxacillin', cwe_3='L')
        obx_5.obx_5 = 'Sensitive'
        obx_5.probability = 'N'
        obx_5.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='ERYT', cwe_2='Erythromycin', cwe_3='L')
        obx_6.obx_5 = 'Resistant'
        obx_6.probability = 'A'
        obx_6.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='CLIN', cwe_2='Clindamycin', cwe_3='L')
        obx_7.obx_5 = 'Sensitive'
        obx_7.probability = 'N'
        obx_7.effective_date_of_reference_range = 'F'

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
    """ Based on live/ph/ph-appoluz.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='OLLH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='OLLH_MANILA')
        msh.date_time_of_message = '20250615090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'APZ-MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250615090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4134567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='OLLH-20250501-0088', cx_4='OLLH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GATMAITAN', xpn_2='ROSARIO', xpn_3='LUNA')
        pid.date_time_of_birth = '19820610'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='P. Noval St', xad_3='Sampaloc', xad_4='NCR', xad_5='1015', xad_6='PH')
        pid.pid_13 = '+63-2-8714-3301~+63-917-555-3344'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH413456789000')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='OLLH-20250310-DUP012', cx_4='OLLH', cx_5='MR')
        mrg.mrg_2 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REG', pl_2='001', pl_4='OLLH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.visit_number = CX(cx_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='PHIC')
        pv1.account_status = CWE(cwe_1='OLLH_MANILA')
        pv1.current_patient_balance = '20250615090000'

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
    """ Based on live/ph/ph-appoluz.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APPOLUZ')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250616100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A31')
        msh.message_control_id = 'APZ-MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250616100000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH4145678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250616-0003', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DALISAY', xpn_2='VICTORIA', xpn_3='CUNANAN')
        pid.date_time_of_birth = '19900115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ayala Ave', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8888-1234~+63-935-777-8899'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH414567890100')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-GEN', pl_2='001', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^CATAPANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250616100000'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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

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
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01NextOfKin, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, \
    OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ph', 'ph-sms-global.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ph/ph-sms-global.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='SLMC_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SLMC_MANILA')
        msh.date_time_of_message = '20250801083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SMS-MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250801083000'
        evn.operator_id = XCN(xcn_1='SORIANO', xcn_2='RENATO', xcn_3='CRUZ', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250801-0044', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BAUTISTA', xpn_2='JOAQUIN', xpn_3='VELASCO')
        pid.date_time_of_birth = '19700920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rizal Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8723-4455~+63-917-301-2288'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH601234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='308', pl_3='A', pl_4='SLMC_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.pv1_8 = 'MENDOZA^CLARA^DIZON^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_MANILA'
        pv1.discharge_date_time = '20250801083000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chronic kidney disease, stage 4')
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
        in1.authorization_information = AUI(aui_1='BAUTISTA', aui_2='JOAQUIN', aui_3='VELASCO')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19700920')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Rizal Ave', cwe_3='Manila', cwe_4='NCR', cwe_5='1000', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH6012345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.4', cwe_2='Chronic kidney disease, stage 4', cwe_3='I10')
        dg1.diagnosis_date_time = '20250801'
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
    """ Based on live/ph/ph-sms-global.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='SLMC_MANILA')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='SLMC_MANILA')
        msh.date_time_of_message = '20250801100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SMS-MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250801-0044', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BAUTISTA', xpn_2='JOAQUIN', xpn_3='VELASCO')
        pid.date_time_of_birth = '19700920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rizal Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8723-4455~+63-917-301-2288'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH601234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='308', pl_3='A', pl_4='SLMC_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_MANILA'
        pv1.discharge_date_time = '20250801083000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250801-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250801100000'
        orc.orc_10 = 'NURSE^MARICEL^TABLIZO'
        orc.enterers_location = PL(pl_1='SLMC_MANILA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250801-001')
        obr.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Renal Function Panel', cwe_3='L')
        obr.observation_date_time = '20250801100000'
        obr.obr_15 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        obr.result_status = '^^^^^R'

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
        obr_2.placer_order_number = EI(ei_1='ORD-SMS-20250801-001')
        obr_2.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr_2.observation_date_time = '20250801100000'
        obr_2.obr_15 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        obr_2.result_status = '^^^^^R'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/ph/ph-sms-global.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='SLMC_MANILA')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='SLMC_MANILA')
        msh.date_time_of_message = '20250801140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250801-0044', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BAUTISTA', xpn_2='JOAQUIN', xpn_3='VELASCO')
        pid.date_time_of_birth = '19700920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rizal Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8723-4455~+63-917-301-2288'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH601234567800')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='308', pl_3='A', pl_4='SLMC_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_MANILA'
        pv1.discharge_date_time = '20250801083000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250801-001')
        orc.orc_12 = 'SORIANO^RENATO^CRUZ^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250801-001')
        obr.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Renal Function Panel', cwe_3='L')
        obr.observation_date_time = '20250801100000'
        obr.obr_16 = 'SORIANO^RENATO^CRUZ^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250801140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='BUN', cwe_2='Blood Urea Nitrogen', cwe_3='L')
        obx.obx_5 = '22.5'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '2.5-7.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='L')
        obx_2.obx_5 = '398'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='GFR', cwe_2='Estimated GFR', cwe_3='L')
        obx_3.obx_5 = '12'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='UA', cwe_2='Uric Acid', cwe_3='L')
        obx_4.obx_5 = '571'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '202-416'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='NA', cwe_2='Sodium', cwe_3='L')
        obx_5.obx_5 = '135'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='L')
        obx_6.obx_5 = '6.1'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.1'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='CA', cwe_2='Calcium, Total', cwe_3='L')
        obx_7.obx_5 = '1.88'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '2.15-2.55'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='PHOS', cwe_2='Phosphorus', cwe_3='L')
        obx_8.obx_5 = '2.35'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '0.81-1.45'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

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
    """ Based on live/ph/ph-sms-global.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250802070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'SMS-MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250802070000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='DIALYSIS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250802-D001', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGILINAN', xpn_2='ROGELIO', xpn_3='TAGUMPAY')
        pid.date_time_of_birth = '19650503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-920-415-3322'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH602345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAL', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250802070000'

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
    """ Based on live/ph/ph-sms-global.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250802090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250802-D001', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGILINAN', xpn_2='ROGELIO', xpn_3='TAGUMPAY')
        pid.date_time_of_birth = '19650503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-920-415-3322'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH602345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAL', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250802070000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250802-001')
        orc.orc_12 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250802-001')
        obr.universal_service_identifier = CWE(cwe_1='PREDIAL', cwe_2='Pre-Dialysis Panel', cwe_3='L')
        obr.observation_date_time = '20250802073000'
        obr.obr_16 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250802090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='BUN', cwe_2='Blood Urea Nitrogen', cwe_3='L')
        obx.obx_5 = '28.5'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '2.5-7.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='L')
        obx_2.obx_5 = '620'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='L')
        obx_3.obx_5 = '5.9'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.5-5.1'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='NA', cwe_2='Sodium', cwe_3='L')
        obx_4.obx_5 = '133'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobin', cwe_3='L')
        obx_5.obx_5 = '88'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '120-160'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrit', cwe_3='L')
        obx_6.obx_5 = '0.27'
        obx_6.units = CWE(cwe_1='L/L')
        obx_6.reference_range = '0.36-0.46'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='PDF-RPT', cwe_2='Pre-Dialysis Lab Report', cwe_3='L')
        obx_7.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFByZS1EaWFseXNpcyBMYWIg'
            'UmVwb3J0IElESCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoK'
            'eHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAw'
            'IG4gCjAwMDAwMDA0MTMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo1MDQKJSVFT0YK'
        )
        obx_7.interpretation_codes = CWE(cwe_1='F')

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
    """ Based on live/ph/ph-sms-global.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250803150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SMS-MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250803150000'
        evn.operator_id = XCN(xcn_1='TOLENTINO', xcn_2='RICARDO', xcn_3='MAGNO', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6034567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250730-0011', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='REYES', xpn_2='ANALISA', xpn_3='DOMINGUEZ')
        pid.date_time_of_birth = '19680315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ayala Ave', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8888-1234~+63-928-705-6677'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH603456789000')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEPH-2A', pl_2='205', pl_3='B', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250730090000'
        pv1.total_charges = '20250803150000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.5', cwe_2='Chronic kidney disease, stage 5', cwe_3='I10')
        dg1.diagnosis_date_time = '20250730'
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I12.0', cwe_2='Hypertensive chronic kidney disease with stage 5', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250730'
        dg1_2.diagnosis_type = CWE(cwe_1='F')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/ph/ph-sms-global.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='CDH_CEBU')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDH_CEBU')
        msh.date_time_of_message = '20250804091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'SMS-MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250804091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='BILLING')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6045678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDH-20250803-0022', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='VILLAREAL', xpn_2='MIGUEL', xpn_3='ANDRADE')
        pid.date_time_of_birth = '19750612'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-253-7890~+63-906-812-4455'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH604567890100')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-2A', pl_2='210', pl_3='A', pl_4='CDH_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^LUISA^HERRERA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^LUISA^HERRERA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDH_CEBU'
        pv1.discharge_date_time = '20250803080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='VILLAREAL', aui_2='MIGUEL', aui_3='ANDRADE')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19750612')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Osmena Blvd', cwe_3='Cebu City', cwe_4='VII', cwe_5='6000', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH6045678901'

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
    """ Based on live/ph/ph-sms-global.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250805103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6056789012', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250805-0005', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGSAYSAY', xpn_2='TERESA', xpn_3='RECTO')
        pid.date_time_of_birth = '19880220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-939-201-5533'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH605678901200')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-1A', pl_2='105', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AGUILAR^DANTE^FAJARDO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AGUILAR^DANTE^FAJARDO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250804200000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250805-003')
        orc.orc_12 = 'AGUILAR^DANTE^FAJARDO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250805-003')
        obr.universal_service_identifier = CWE(cwe_1='MALARIA', cwe_2='Malarial Smear', cwe_3='L')
        obr.observation_date_time = '20250805060000'
        obr.obr_16 = 'AGUILAR^DANTE^FAJARDO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250805103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='MP-THICK', cwe_2='Thick Smear', cwe_3='L')
        obx.obx_5 = 'Positive for Plasmodium falciparum'
        obx.reference_range = 'Negative'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='MP-THIN', cwe_2='Thin Smear', cwe_3='L')
        obx_2.obx_5 = 'Plasmodium falciparum, ring forms'
        obx_2.reference_range = 'Negative'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='MP-DENS', cwe_2='Parasite Density', cwe_3='L')
        obx_3.obx_5 = '2500'
        obx_3.units = CWE(cwe_1='parasites/uL')
        obx_3.reference_range = '0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobin', cwe_3='L')
        obx_4.obx_5 = '95'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '120-160'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='L')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

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
    """ Based on live/ph/ph-sms-global.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250806100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SMS-MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='DIAL-20250809-001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Hemodialysis session', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '240'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^240^20250809070000^20250809110000'
        sch.sch_13 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        sch.placer_contact_address = XAD(xad_1='+63-2-8635-6789')
        sch.placer_contact_location = PL(pl_1='TMC DIALYSIS UNIT', pl_2='2nd Floor', pl_4='Pasig', pl_5='NCR', pl_6='1605', pl_7='PH')
        sch.filler_contact_person = XCN(xcn_1='TMC_PASIG')
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250802-D001', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGILINAN', xpn_2='ROGELIO', xpn_3='TAGUMPAY')
        pid.date_time_of_birth = '19650503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-920-415-3322'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH602345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
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
        ais.universal_service_identifier = CWE(cwe_1='HEMO', cwe_2='Hemodialysis', cwe_3='L')
        ais.start_date_time = '20250809070000'
        ais.duration = '240'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        aip.resource_type = CWE(cwe_1='NEPH')
        aip.start_date_time_offset_units = CNE(cne_1='20250809070000')
        aip.allow_substitution_code = CWE(cwe_1='240')
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
    """ Based on live/ph/ph-sms-global.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='CDO_POLYMEDIC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDO_POLYMEDIC')
        msh.date_time_of_message = '20250807023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SMS-MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250807023000'
        evn.operator_id = XCN(xcn_1='DUTY', xcn_2='NURSE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6067890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDO-20250805-0033', cx_4='CDO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DALISAY', xpn_2='ERNESTO', xpn_3='MACAPAGAL')
        pid.date_time_of_birth = '19580815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Corrales Ave', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-856-1020~+63-917-603-7711'
        pid.primary_language = CWE(cwe_1='BIS')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH606789012300')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='003', pl_3='A', pl_4='CDO_POLYMEDIC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.delete_account_indicator = CWE(cwe_1='MED-3A', cwe_2='302', cwe_3='B', cwe_4='CDO_POLYMEDIC', cwe_7='N')
        pv1.account_status = CWE(cwe_1='CDO_POLYMEDIC')
        pv1.current_patient_balance = '20250805140000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-sms-global.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CDO_POLYMEDIC')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='CDO_POLYMEDIC')
        msh.date_time_of_message = '20250808160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6067890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDO-20250805-0033', cx_4='CDO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DALISAY', xpn_2='ERNESTO', xpn_3='MACAPAGAL')
        pid.date_time_of_birth = '19580815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Corrales Ave', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-856-1020~+63-917-603-7711'
        pid.primary_language = CWE(cwe_1='BIS')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH606789012300')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='003', pl_3='A', pl_4='CDO_POLYMEDIC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDO_POLYMEDIC'
        pv1.discharge_date_time = '20250805140000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250806-005')
        orc.orc_12 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250806-005')
        obr.universal_service_identifier = CWE(cwe_1='BC', cwe_2='Blood Culture', cwe_3='L')
        obr.observation_date_time = '20250806080000'
        obr.obr_16 = 'PASCUAL^JAIME^ELIAS^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250808160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='BC-ORG', cwe_2='Organism Isolated', cwe_3='L')
        obx.obx_5 = 'Escherichia coli'
        obx.probability = 'A'
        obx.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='BC-AMPI', cwe_2='Ampicillin', cwe_3='L')
        obx_2.obx_5 = 'Resistant'
        obx_2.probability = 'A'
        obx_2.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='BC-AMCL', cwe_2='Amoxicillin-Clavulanate', cwe_3='L')
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
        obx_4.observation_identifier = CWE(cwe_1='BC-CEFT', cwe_2='Ceftriaxone', cwe_3='L')
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
        obx_5.observation_identifier = CWE(cwe_1='BC-GENT', cwe_2='Gentamicin', cwe_3='L')
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
        obx_6.observation_identifier = CWE(cwe_1='BC-CIPR', cwe_2='Ciprofloxacin', cwe_3='L')
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
        obx_7.observation_identifier = CWE(cwe_1='BC-MERO', cwe_2='Meropenem', cwe_3='L')
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
    """ Based on live/ph/ph-sms-global.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250809120000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SMS-MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250809120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250802-D001', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGILINAN', xpn_2='ROGELIO', xpn_3='TAGUMPAY')
        pid.date_time_of_birth = '19650503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-920-415-3322'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH602345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAL', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250809070000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DIAL', cwe_2='Dialysis Treatment Summary')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20250809110000'
        txa.txa_5 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        txa.transcription_date_time = '20250809120000'
        txa.txa_9 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        txa.parent_document_number = EI(ei_1='DOC-SMS-20250809-001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='DIAL-RPT', cwe_2='Dialysis Summary PDF', cwe_3='L')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKERpYWx5c2lzIFRyZWF0bWVu'
            'dCBTdW1tYXJ5IFJlcG9ydCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+Pgpl'
            'bmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2'
            'IDAwMDAwIG4gCjAwMDAwMDA0MTcgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo1MDgKJSVFT0YK'
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
    """ Based on live/ph/ph-sms-global.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='SLMC_MANILA')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='SLMC_MANILA')
        msh.date_time_of_message = '20250810080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'SMS-MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'LIS-ORU-20250810-012'
        msa.msa_3 = 'Lab results received and filed'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/ph/ph-sms-global.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='CDH_CEBU')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='CDH_CEBU')
        msh.date_time_of_message = '20250811093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SMS-MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6078901234', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDH-20250811-0008', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='QUIJANO', xpn_2='CARMELA', xpn_3='TABIGNE')
        pid.date_time_of_birth = '19800425'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Colon St', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-255-0880~+63-935-718-9944'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH607890123400')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='210', pl_3='B', pl_4='CDH_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LEDESMA^ARTURO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GI')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LEDESMA^ARTURO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDH_CEBU'
        pv1.discharge_date_time = '20250810140000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250811-002')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250811093000'
        orc.orc_10 = 'NURSE^CHERRY^LAGMAN'
        orc.enterers_location = PL(pl_1='CDH_CEBU')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250811-002')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Ultrasound Abdomen Complete', cwe_3='CPT')
        obr.observation_date_time = '20250811093000'
        obr.obr_15 = 'LEDESMA^ARTURO^VILLANUEVA^^^DR^MD'
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
    """ Based on live/ph/ph-sms-global.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250812111000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6089012345', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250812-0003', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='SALAZAR', xpn_2='MYRNA', xpn_3='EVANGELISTA')
        pid.date_time_of_birth = '19750118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Jupiter St', xad_3='Makati', xad_4='NCR', xad_5='1209', xad_6='PH')
        pid.pid_13 = '+63-2-8817-5555~+63-917-490-3366'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH608901234500')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-ENDO', pl_2='001', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='ENDO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250812080000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250812-001')
        orc.orc_12 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250812-001')
        obr.universal_service_identifier = CWE(cwe_1='TFT', cwe_2='Thyroid Function Test', cwe_3='L')
        obr.observation_date_time = '20250812081500'
        obr.obr_16 = 'TOLENTINO^RICARDO^MAGNO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250812111000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TSH', cwe_2='Thyroid Stimulating Hormone', cwe_3='L')
        obx.obx_5 = '0.15'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='FT4', cwe_2='Free Thyroxine', cwe_3='L')
        obx_2.obx_5 = '32.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='FT3', cwe_2='Free Triiodothyronine', cwe_3='L')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

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
    """ Based on live/ph/ph-sms-global.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='SLMC_TAGUIG')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SLMC_TAGUIG')
        msh.date_time_of_message = '20250813100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'SMS-MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250813100000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='PRE-REG')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6190123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250813-0022', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CORPUZ', xpn_2='BENJAMIN', xpn_3='LAZARO')
        pid.date_time_of_birth = '19770318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bonifacio Global City', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8789-7700~+63-939-110-4488'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH619012345600')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CORPUZ', xpn_2='PATRICIA', xpn_3='LUNA')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Bonifacio Global City', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        nk1.nk1_5 = '+63-939-110-4489'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG-PRE', pl_2='001', pl_4='SLMC_TAGUIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SANTOS^GREGORIO^ARCENAS^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SANTOS^GREGORIO^ARCENAS^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='PR')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_TAGUIG'
        pv1.discharge_date_time = '20250813100000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='CORPUZ', aui_2='BENJAMIN', aui_3='LAZARO')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19770318')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Bonifacio Global City', cwe_3='Taguig', cwe_4='NCR', cwe_5='1634', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH6190123456'

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
    """ Based on live/ph/ph-sms-global.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='PHARM')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250814080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SMS-MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250802-D001', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGILINAN', xpn_2='ROGELIO', xpn_3='TAGUMPAY')
        pid.date_time_of_birth = '19650503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-920-415-3322'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH602345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAL', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250814070000'

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
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250814-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250814080000'
        orc.orc_10 = 'NURSE^DIALYSIS^UNIT'
        orc.enterers_location = PL(pl_1='TMC_PASIG')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='EPO', cwe_2='Erythropoietin 4000IU', cwe_3='L')
        rxo.requested_give_amount_minimum = '4000'
        rxo.requested_give_units = CWE(cwe_1='IU')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='INJ', cwe_2='Injection')
        rxo.providers_administration_instructions = CWE(cwe_2='SC', cwe_3='Subcutaneous')
        rxo.allow_substitutions = '1^3x weekly'
        rxo.rxo_14 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='CALCIT', cwe_2='Calcitriol 0.25mcg', cwe_3='L')
        rxo_2.requested_give_amount_minimum = '0.25'
        rxo_2.requested_give_units = CWE(cwe_1='mcg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='CAP', cwe_2='Capsule')
        rxo_2.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo_2.allow_substitutions = '1^OD'
        rxo_2.rxo_14 = 'NAVARRO^ELIZABETH^GALANG^^^DR^MD'

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
    """ Based on live/ph/ph-sms-global.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250815090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A31')
        msh.message_control_id = 'SMS-MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250815090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6101234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250815-0001', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='GLORIA', xpn_3='UMALI')
        pid.date_time_of_birth = '19850930'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Commonwealth Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1121', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0001~+63-928-300-5566'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH610123456700')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-GEN', pl_2='001', pl_4='SLMC_QC', pl_7='P')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'CASTRO^MANUEL^VILLEGAS^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CASTRO^MANUEL^VILLEGAS^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250815090000'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-sms-global.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SMSGLOBAL')
        msh.sending_facility = HD(hd_1='CDH_CEBU')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDH_CEBU')
        msh.date_time_of_message = '20250816091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'SMS-MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250816091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6112345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDH-20250701-0088', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LABRADOR', xpn_2='CONSUELO', xpn_3='DIMACALI')
        pid.date_time_of_birth = '19700505'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gen. Maxilom Ave', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-233-8080~+63-906-522-1199'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH611234567800')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='CDH-20250515-DUP008', cx_4='CDH', cx_5='MR')
        mrg.mrg_2 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REG', pl_2='001', pl_4='CDH_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.visit_number = CX(cx_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='PHIC')
        pv1.account_status = CWE(cwe_1='CDH_CEBU')
        pv1.current_patient_balance = '20250816091500'

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
    """ Based on live/ph/ph-sms-global.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='SMSGLOBAL')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250817102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMS-MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH6123456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250817-0009', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TINIO', xpn_2='GABRIEL', xpn_3='MANALO')
        pid.date_time_of_birth = '20080622'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Espana Blvd', xad_3='Manila', xad_4='NCR', xad_5='1008', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-939-620-7711'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH612345678900')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='TINIO', xpn_2='ROSALINDA', xpn_3='CRUZ')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='Espana Blvd', xad_3='Manila', xad_4='NCR', xad_5='1008', xad_6='PH')
        nk1.nk1_5 = '+63-939-620-7711'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED08', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'DELA VEGA^ALFONSO^BUENAVENTURA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'DELA VEGA^ALFONSO^BUENAVENTURA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='ER')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250817080000'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-SMS-20250817-002')
        orc.orc_12 = 'DELA VEGA^ALFONSO^BUENAVENTURA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SMS-20250817-002')
        obr.universal_service_identifier = CWE(cwe_1='DENGUE', cwe_2='Dengue Rapid Test', cwe_3='L')
        obr.observation_date_time = '20250817083000'
        obr.obr_16 = 'DELA VEGA^ALFONSO^BUENAVENTURA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250817102000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='NS1AG', cwe_2='Dengue NS1 Antigen', cwe_3='L')
        obx.obx_5 = 'POSITIVE'
        obx.reference_range = 'NEGATIVE'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='DENV-IGM', cwe_2='Dengue IgM', cwe_3='L')
        obx_2.obx_5 = 'NEGATIVE'
        obx_2.reference_range = 'NEGATIVE'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='DENV-IGG', cwe_2='Dengue IgG', cwe_3='L')
        obx_3.obx_5 = 'NEGATIVE'
        obx_3.reference_range = 'NEGATIVE'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='L')
        obx_4.obx_5 = '95'
        obx_4.units = CWE(cwe_1='10*3/uL')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrit', cwe_3='L')
        obx_5.obx_5 = '0.42'
        obx_5.units = CWE(cwe_1='L/L')
        obx_5.reference_range = '0.35-0.45'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

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

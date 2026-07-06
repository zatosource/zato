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

_md_path = md_path_for('ph', 'ph-sancy.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ph/ph-sancy.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250601083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SDS-MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250601083000'
        evn.operator_id = XCN(xcn_1='AQUINO', xcn_2='MARCO', xcn_3='VILLANUEVA', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='301', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.pv1_8 = 'NAVARRO^CRISTINA^MENDEZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250601083000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Stroke, cerebral infarction')
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
        in1.authorization_information = AUI(aui_1='RAMOS', aui_2='JEROME', aui_3='DALISAY')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19680515')
        in1.insureds_relationship_to_patient = CWE(cwe_1='E. Rodriguez Sr. Ave', cwe_3='Quezon City', cwe_4='NCR', cwe_5='1112', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH2012345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Cerebral infarction, unspecified', cwe_3='I10')
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
    """ Based on live/ph/ph-sancy.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250601093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SDS-MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='301', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250601083000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20250601093000'
        orc.orc_10 = 'NURSE^LOURDES^REYES'
        orc.enterers_location = PL(pl_1='STLUKES_BGC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr.observation_date_time = '20250601093000'
        obr.obr_15 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
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
        obr_2.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        obr_2.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Panel', cwe_3='L')
        obr_2.observation_date_time = '20250601093000'
        obr_2.obr_15 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        obr_2.result_status = '^^^^^S'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        obr_3.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Lipid Panel', cwe_3='L')
        obr_3.observation_date_time = '20250601093000'
        obr_3.obr_15 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
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
    """ Based on live/ph/ph-sancy.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250601130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='301', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250601083000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        orc.orc_12 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250601-001')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Panel', cwe_3='L')
        obr.observation_date_time = '20250601093000'
        obr.obr_16 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250601130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='PT', cwe_2='Prothrombin Time', cwe_3='L')
        obx.obx_5 = '14.2'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='INR', cwe_2='International Normalized Ratio', cwe_3='L')
        obx_2.obx_5 = '1.2'
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='APTT', cwe_2='Activated Partial Thromboplastin Time', cwe_3='L')
        obx_3.obx_5 = '38.5'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25.0-35.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='FIB', cwe_2='Fibrinogen', cwe_3='L')
        obx_4.obx_5 = '4.5'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='DDIMER', cwe_2='D-Dimer', cwe_3='L')
        obx_5.obx_5 = '1.8'
        obx_5.units = CWE(cwe_1='mg/L FEU')
        obx_5.reference_range = '<0.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ph/ph-sancy.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250602083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'SDS-MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250602083000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='OPD')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250602-0009', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='ERLINDA', xpn_3='BIRON')
        pid.date_time_of_birth = '19750220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8635-6789~+63-928-333-4455'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH202345678900')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-NEURO', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'TOLENTINO^RICARDO^MAGBANUA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEURO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TOLENTINO^RICARDO^MAGBANUA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
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
    """ Based on live/ph/ph-sancy.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250601160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='301', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250601083000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250601-RAD01')
        orc.orc_12 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250601-RAD01')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT Head without Contrast', cwe_3='CPT')
        obr.observation_date_time = '20250601110000'
        obr.obr_16 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250601160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RAD-IMP', cwe_2='Radiology Impression', cwe_3='L')
        obx.obx_5 = 'Acute infarct in the left middle cerebral artery territory. No hemorrhagic transformation. No midline shift.'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF-RPT', cwe_2='CT Brain Report', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKENUIEJyYWluIFJlcG9ydCAt'
            'IEFVRk1DKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVm'
            'CjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAK'
            'MDAwMDAwMDQwNyAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjQ5OAolJUVPRgo='
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
    """ Based on live/ph/ph-sancy.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250601180000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SDS-MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250601180000'
        evn.operator_id = XCN(xcn_1='AQUINO', xcn_2='MARCO', xcn_3='VILLANUEVA', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STROKE', pl_2='001', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEURO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.delete_account_indicator = CWE(cwe_1='MED-3A', cwe_2='301', cwe_3='A', cwe_4='STLUKES_BGC', cwe_7='N')
        pv1.account_status = CWE(cwe_1='STLUKES_BGC')
        pv1.current_patient_balance = '20250601083000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-sancy.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250610140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SDS-MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250610140000'
        evn.operator_id = XCN(xcn_1='SALAZAR', xcn_2='PATRICIA', xcn_3='IGNACIO', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2034567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250605-0011', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='VILLAREAL', xpn_2='CONSUELO', xpn_3='MAGTALAS')
        pid.date_time_of_birth = '19700118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Jupiter St', xad_3='Makati', xad_4='NCR', xad_5='1209', xad_6='PH')
        pid.pid_13 = '+63-2-8888-8999~+63-919-444-5566'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH203456789000')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO-2A', pl_2='205', pl_3='B', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEURO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250605090000'
        pv1.total_charges = '20250610140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G40.909', cwe_2='Epilepsy, unspecified, not intractable', cwe_3='I10')
        dg1.diagnosis_date_time = '20250605'
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
    """ Based on live/ph/ph-sancy.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CEBUDOC_CEBU')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='CEBUDOC_CEBU')
        msh.date_time_of_message = '20250611110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2045678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDU-20250611-0005', cx_4='CEBUDOC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ABELLANA', xpn_2='LILIA', xpn_3='TANDOG')
        pid.date_time_of_birth = '19800915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-253-1234~+63-935-222-7788'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH204567890100')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-INT', pl_2='001', pl_4='CEBUDOC_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CEBUDOC_CEBU'
        pv1.discharge_date_time = '20250611080000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250611-002')
        orc.orc_12 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250611-002')
        obr.universal_service_identifier = CWE(cwe_1='METABOLIC', cwe_2='Metabolic Panel', cwe_3='L')
        obr.observation_date_time = '20250611081500'
        obr.obr_16 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250611110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='FBS', cwe_2='Fasting Blood Sugar', cwe_3='L')
        obx.obx_5 = '6.5'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='CHOL', cwe_2='Total Cholesterol', cwe_3='L')
        obx_2.obx_5 = '6.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<5.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='TRIG', cwe_2='Triglycerides', cwe_3='L')
        obx_3.obx_5 = '2.4'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '<1.7'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HDL', cwe_2='HDL Cholesterol', cwe_3='L')
        obx_4.obx_5 = '0.9'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '>1.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='LDL', cwe_2='LDL Cholesterol', cwe_3='L')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '<3.4'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='UA', cwe_2='Uric Acid', cwe_3='L')
        obx_6.obx_5 = '450'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '155-357'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

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
    """ Based on live/ph/ph-sancy.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250612100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SDS-MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='REHAB-20250616-001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Physical therapy for stroke rehabilitation', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '60'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^60^20250616090000^20250616100000'
        sch.sch_13 = 'PT^MARICRIS^BAUTISTA^RPT'
        sch.placer_contact_address = XAD(xad_1='+63-2-8723-0101')
        sch.placer_contact_location = PL(pl_1='ST LUKES REHAB CENTER', pl_3='Taguig', pl_4='NCR', pl_5='1634', pl_6='PH')
        sch.filler_contact_person = XCN(xcn_1='STLUKES_BGC')
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250601-0022', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RAMOS', xpn_2='JEROME', xpn_3='DALISAY')
        pid.date_time_of_birth = '19680515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='E. Rodriguez Sr. Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-222-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH201234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
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
        ais.universal_service_identifier = CWE(cwe_1='PT-STROKE', cwe_2='Stroke Rehabilitation PT', cwe_3='L')
        ais.start_date_time = '20250616090000'
        ais.duration = '60'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='PT', xcn_2='MARICRIS', xcn_3='BAUTISTA', xcn_4='RPT')
        aip.resource_type = CWE(cwe_1='PT')
        aip.start_date_time_offset_units = CNE(cne_1='20250616090000')
        aip.allow_substitution_code = CWE(cwe_1='60')
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
    """ Based on live/ph/ph-sancy.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250613091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'SDS-MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250613091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2056789012', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250611-0033', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LACSON', xpn_2='BERNARDO', xpn_3='ESTACIO')
        pid.date_time_of_birth = '19630820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-928-555-1122'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH205678901200')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-4B', pl_2='410', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250611080000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='LACSON', xpn_2='IMELDA', xpn_3='REYES')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        nk1.nk1_5 = '+63-928-555-1123'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='LACSON', xpn_2='MARIO', xpn_3='BERNARDO')
        nk1_2.relationship = CWE(cwe_1='SON')
        nk1_2.address = XAD(xad_1='Ermita', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        nk1_2.nk1_5 = '+63-917-333-4455'
        nk1_2.contact_role = CWE(cwe_1='EC')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, nk1_2]

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
    """ Based on live/ph/ph-sancy.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250614055000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2067890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250613-0077', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='SORIANO', xpn_2='ROBERTO', xpn_3='CUNANAN')
        pid.date_time_of_birth = '19570210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='C5 Rd', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8789-1234~+63-919-666-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH206789012300')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CCU', pl_2='002', pl_3='A', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250613200000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250614-001')
        orc.orc_12 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250614-001')
        obr.universal_service_identifier = CWE(cwe_1='CARDIAC', cwe_2='Cardiac Enzymes Serial', cwe_3='L')
        obr.observation_date_time = '20250614040000'
        obr.obr_16 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250614055000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TROP-I', cwe_2='Troponin I (6hr)', cwe_3='L')
        obx.obx_5 = '5.82'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='CKMB', cwe_2='CK-MB (6hr)', cwe_3='L')
        obx_2.obx_5 = '65.0'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '0-25'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='LDH', cwe_2='Lactate Dehydrogenase', cwe_3='L')
        obx_3.obx_5 = '580'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '125-243'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='BNP', cwe_2='BNP', cwe_3='L')
        obx_4.obx_5 = '850'
        obx_4.units = CWE(cwe_1='pg/mL')
        obx_4.reference_range = '0-100'
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
    """ Based on live/ph/ph-sancy.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250615160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SDS-MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250615160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2078901234', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250612-0019', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CATALAN', xpn_2='GLORIA', xpn_3='VERZOSA')
        pid.date_time_of_birth = '19720405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ayala Ave', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8888-1999~+63-935-777-2233'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH207890123400')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='210', pl_3='B', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250612090000'
        pv1.total_charges = '20250615160000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20250615150000'
        txa.txa_5 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        txa.transcription_date_time = '20250615160000'
        txa.txa_9 = 'SALAZAR^PATRICIA^IGNACIO^^^DR^MD'
        txa.parent_document_number = EI(ei_1='DOC-SDS-20250615-001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='DSUM', cwe_2='Discharge Summary PDF', cwe_3='L')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKERpc2NoYXJnZSBTdW1tYXJ5'
            'IC0gQ0xESCBUYXJsYWMpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5k'
            'b2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAw'
            'MDAwMCBuIAowMDAwMDAwNDExIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTAyCiUlRU9GCg=='
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
    """ Based on live/ph/ph-sancy.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_RCV')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250616080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'SDS-MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'SDS-MSG-ADT-20250616-001'
        msa.msa_3 = 'Admission processed successfully'

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
    """ Based on live/ph/ph-sancy.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250617090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SDS-MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2089012345', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250617-0008', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGNO', xpn_2='GABRIEL', xpn_3='BUENAVENTURA')
        pid.date_time_of_birth = '19750330'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pedro Gil St', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-3333~+63-917-888-4455'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH208901234500')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO-2A', pl_2='208', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEURO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250616140000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250617-003')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250617090000'
        orc.orc_10 = 'NURSE^ROSALINDA^GARCIA'
        orc.enterers_location = PL(pl_1='PGH_MANILA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250617-003')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI Brain with and without Contrast', cwe_3='CPT')
        obr.observation_date_time = '20250617090000'
        obr.obr_15 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
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
    """ Based on live/ph/ph-sancy.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250618111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2190123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250618-0003', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='AGONCILLO', xpn_2='TERESA', xpn_3='LAUREL')
        pid.date_time_of_birth = '19850210'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Padre Faura St', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-7890~+63-928-222-6677'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH219012345600')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-INT', pl_2='001', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250618080000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250618-001')
        orc.orc_12 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250618-001')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Blood Chemistry', cwe_3='L')
        obr.observation_date_time = '20250618081500'
        obr.obr_16 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250618111500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='GLU', cwe_2='Glucose, Fasting', cwe_3='L')
        obx.obx_5 = '5.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='BUN', cwe_2='Blood Urea Nitrogen', cwe_3='L')
        obx_2.obx_5 = '5.5'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.5-7.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='L')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '62-115'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='UA', cwe_2='Uric Acid', cwe_3='L')
        obx_4.obx_5 = '310'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '155-357'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='CHOL', cwe_2='Total Cholesterol', cwe_3='L')
        obx_5.obx_5 = '4.8'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '<5.2'
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
    """ Based on live/ph/ph-sancy.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='CEBUDOC_CEBU')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CEBUDOC_CEBU')
        msh.date_time_of_message = '20250619100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'SDS-MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250619100000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='PRE-REG')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2101234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDU-20250619-0001', cx_4='CEBUDOC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CABRERA', xpn_2='ROLANDO', xpn_3='ESPINA')
        pid.date_time_of_birth = '19780620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Colon St', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-255-2345~+63-935-444-1122'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH210123456700')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CABRERA', xpn_2='PILAR', xpn_3='SANTOS')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Colon St', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        nk1.nk1_5 = '+63-935-444-1123'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG-PRE', pl_2='001', pl_4='CEBUDOC_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CUENCO^RAMON^LAGUDA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='PR')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CEBUDOC_CEBU'
        pv1.discharge_date_time = '20250619100000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='CABRERA', aui_2='ROLANDO', aui_3='ESPINA')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19780620')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Colon St', cwe_3='Cebu City', cwe_4='VII', cwe_5='6000', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH2101234567'

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
    """ Based on live/ph/ph-sancy.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='STLUKES_BGC')
        msh.receiving_application = HD(hd_1='PHARM')
        msh.receiving_facility = HD(hd_1='STLUKES_BGC')
        msh.date_time_of_message = '20250620080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SDS-MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2112345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLK-20250618-0055', cx_4='STLUKES', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PASCUAL', xpn_2='JULIO', xpn_3='BUENCAMINO')
        pid.date_time_of_birth = '19600715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='McKinley Rd', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8789-4444~+63-917-666-8899'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH211234567800')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD-2A', pl_2='205', pl_3='B', pl_4='STLUKES_BGC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'STLUKES_BGC'
        pv1.discharge_date_time = '20250618090000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250620-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250620080000'
        orc.orc_10 = 'NURSE^GRACE^VILLANUEVA'
        orc.enterers_location = PL(pl_1='STLUKES_BGC')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='WARF', cwe_2='Warfarin 5mg', cwe_3='L')
        rxo.requested_give_amount_minimum = '5'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo.allow_substitutions = '1^OD'
        rxo.rxo_14 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='ASA', cwe_2='Aspirin 80mg', cwe_3='L')
        rxo_2.requested_give_amount_minimum = '80'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo_2.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo_2.allow_substitutions = '1^OD'
        rxo_2.rxo_14 = 'AQUINO^MARCO^VILLANUEVA^^^DR^MD'

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
    """ Based on live/ph/ph-sancy.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='DAVAO_MED')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='DAVAO_MED')
        msh.date_time_of_message = '20250621090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A31')
        msh.message_control_id = 'SDS-MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250621090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2123456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='DVM-20250621-0002', cx_4='DAVMED', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MATUGAS', xpn_2='CORAZON', xpn_3='LIBRODO')
        pid.date_time_of_birth = '19900305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bolton St', xad_3='Davao', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-227-8901~+63-928-777-3344'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH212345678900')
        pid.mothers_identifier = CX(cx_1='Davao', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-GEN', pl_2='001', pl_4='DAVAO_MED', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'DUTERTE^BENJAMIN^CARPIO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'DUTERTE^BENJAMIN^CARPIO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'DAVAO_MED'
        pv1.discharge_date_time = '20250621090000'

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
    """ Based on live/ph/ph-sancy.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SANCY')
        msh.sending_facility = HD(hd_1='CDOH_CDO')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='CDOH_CDO')
        msh.date_time_of_message = '20250622091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'SDS-MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250622091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2134567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDO-20250301-0099', cx_4='CDOH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PELAEZ', xpn_2='ESPERANZA', xpn_3='CHAVES')
        pid.date_time_of_birth = '19780815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Divisoria', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-856-5555~+63-935-888-1122'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH213456789000')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='CDO-20250115-DUP011', cx_4='CDOH', cx_5='MR')
        mrg.mrg_2 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REG', pl_2='001', pl_4='CDOH_CDO', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.visit_number = CX(cx_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='PHIC')
        pv1.account_status = CWE(cwe_1='CDOH_CDO')
        pv1.current_patient_balance = '20250622091500'

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
    """ Based on live/ph/ph-sancy.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='SANCY')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250623102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SDS-MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH2145678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250623-0007', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DELA CRUZ', xpn_2='ANTONIO', xpn_3='PANGANIBAN')
        pid.date_time_of_birth = '19650520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rizal Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-3456~+63-906-111-5566'
        pid.primary_language = CWE(cwe_1='KAP')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH214567890100')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='205', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250622160000'

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
        orc.placer_order_number = EI(ei_1='ORD-SDS-20250623-002')
        orc.orc_12 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-SDS-20250623-002')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr.observation_date_time = '20250623060000'
        obr.obr_16 = 'OCAMPO^FELIX^MARIANO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250623102000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Blood Cell Count', cwe_3='L')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Red Blood Cell Count', cwe_3='L')
        obx_2.obx_5 = '3.2'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.50-5.50'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobin', cwe_3='L')
        obx_3.obx_5 = '92'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-170'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrit', cwe_3='L')
        obx_4.obx_5 = '0.28'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.40-0.50'
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
        obx_5.obx_5 = '450'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='MCV', cwe_2='Mean Corpuscular Volume', cwe_3='L')
        obx_6.obx_5 = '87.5'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80.0-96.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='MCH', cwe_2='Mean Corpuscular Hemoglobin', cwe_3='L')
        obx_7.obx_5 = '28.8'
        obx_7.units = CWE(cwe_1='pg')
        obx_7.reference_range = '27.0-33.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='MCHC', cwe_2='Mean Corpuscular Hemoglobin Conc', cwe_3='L')
        obx_8.obx_5 = '329'
        obx_8.units = CWE(cwe_1='g/L')
        obx_8.reference_range = '320-360'
        obx_8.interpretation_codes = CWE(cwe_1='N')
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

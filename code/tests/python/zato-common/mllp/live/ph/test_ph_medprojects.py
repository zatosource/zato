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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ph', 'ph-medprojects.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ph/ph-medprojects.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250401090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MC-MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250401090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SYSTEM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250401-0033', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='RAFAEL', xpn_3='LUCERO')
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Katipunan Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1108', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-301-4456'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH801234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.pv1_8 = 'PANGILINAN^ANA^REYES^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250401090000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute coronary syndrome')
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
        in1.authorization_information = AUI(aui_1='DIMACULANGAN', aui_2='RAFAEL', aui_3='LUCERO')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19700425')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Katipunan Ave', cwe_3='Quezon City', cwe_4='NCR', cwe_5='1108', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH8012345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I24.9', cwe_2='Acute ischemic heart disease, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
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
    """ Based on live/ph/ph-medprojects.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250401100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MC-MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250401-0033', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='RAFAEL', xpn_3='LUCERO')
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Katipunan Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1108', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-301-4456'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH801234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250401090000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20250401100000'
        orc.orc_10 = 'NURSE^MARICEL^TEOPACO'
        orc.enterers_location = PL(pl_1='SLMC_QC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        obr.universal_service_identifier = CWE(cwe_1='TROPONIN', cwe_2='Troponin I', cwe_3='L')
        obr.observation_date_time = '20250401100000'
        obr.obr_15 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
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
        obr_2.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        obr_2.universal_service_identifier = CWE(cwe_1='CKMB', cwe_2='CK-MB', cwe_3='L')
        obr_2.observation_date_time = '20250401100000'
        obr_2.obr_15 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        obr_2.result_status = '^^^^^S'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        obr_3.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr_3.observation_date_time = '20250401100000'
        obr_3.obr_15 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
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
    """ Based on live/ph/ph-medprojects.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250401130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250401-0033', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='RAFAEL', xpn_3='LUCERO')
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Katipunan Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1108', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-301-4456'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH801234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250401090000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        orc.orc_12 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        obr.universal_service_identifier = CWE(cwe_1='TROPONIN', cwe_2='Troponin I', cwe_3='L')
        obr.observation_date_time = '20250401100000'
        obr.obr_16 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250401130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TROP-I', cwe_2='Troponin I', cwe_3='L')
        obx.obx_5 = '1.85'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
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
        obr_2.placer_order_number = EI(ei_1='ORD-MC-20250401-001')
        obr_2.universal_service_identifier = CWE(cwe_1='CKMB', cwe_2='CK-MB', cwe_3='L')
        obr_2.observation_date_time = '20250401100000'
        obr_2.obr_16 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        obr_2.results_rpt_status_chng_date_time = '20250401130000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='CKMB', cwe_2='CK-MB', cwe_3='L')
        obx_2.obx_5 = '38.5'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '0-25'
        obx_2.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ph/ph-medprojects.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250402201500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MC-MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250402201500'
        evn.operator_id = XCN(xcn_1='TRIAGE', xcn_2='ER')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250402-ER022', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGTANGGOL', xpn_2='IRENE', xpn_3='SALAZAR')
        pid.date_time_of_birth = '19850310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-928-710-2233'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH802345678900')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='TRIAGE', pl_3='001', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='ER')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250402201500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.001A', cwe_2='Fracture of unspecified part of neck of right femur', cwe_3='I10')
        dg1.diagnosis_date_time = '20250402'
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/ph/ph-medprojects.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250402210000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MC-MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250402-ER022', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGTANGGOL', xpn_2='IRENE', xpn_3='SALAZAR')
        pid.date_time_of_birth = '19850310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-928-710-2233'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH802345678900')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED03', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='ER')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250402201500'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250402-ER001')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20250402210000'
        orc.orc_10 = 'NURSE^JENNY^PASCUAL'
        orc.enterers_location = PL(pl_1='PGH_MANILA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250402-ER001')
        obr.universal_service_identifier = CWE(cwe_1='73502', cwe_2='X-Ray Hip Right', cwe_3='CPT')
        obr.observation_date_time = '20250402210000'
        obr.obr_15 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        obr.result_status = '^^^^^S'

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
    """ Based on live/ph/ph-medprojects.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250402230000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250402-ER022', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGTANGGOL', xpn_2='IRENE', xpn_3='SALAZAR')
        pid.date_time_of_birth = '19850310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-928-710-2233'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH802345678900')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED03', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='ER')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250402201500'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250402-ER001')
        orc.orc_12 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250402-ER001')
        obr.universal_service_identifier = CWE(cwe_1='73502', cwe_2='X-Ray Hip Right', cwe_3='CPT')
        obr.observation_date_time = '20250402213000'
        obr.obr_16 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250402230000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RAD-IMP', cwe_2='Radiology Impression', cwe_3='L')
        obx.obx_5 = 'Right femoral neck fracture, non-displaced. No associated acetabular fracture. Mild osteopenia.'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF-RPT', cwe_2='X-Ray Hip Report', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFgtUmF5IEhpcCBSZXBvcnQg'
            'UEdIKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAg'
            'NgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAw'
            'MDAwMDQwNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjQ5NgolJUVPRgo='
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
    """ Based on live/ph/ph-medprojects.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250403140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MC-MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250403140000'
        evn.operator_id = XCN(xcn_1='DUTY', xcn_2='NURSE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8034567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250402-0055', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='AGCAOILI', xpn_2='CARMELA', xpn_3='VELASCO')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Meralco Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8689-8888~+63-919-504-7721'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH803456789000')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='002', pl_3='A', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.delete_account_indicator = CWE(cwe_1='MED-3A', cwe_2='305', cwe_3='B', cwe_4='TMC_PASIG', cwe_7='N')
        pv1.account_status = CWE(cwe_1='TMC_PASIG')
        pv1.current_patient_balance = '20250402100000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-medprojects.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250405150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MC-MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250405150000'
        evn.operator_id = XCN(xcn_1='LACSAMANA', xcn_2='ROBERTO', xcn_3='MAGNO', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8012345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250401-0033', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='RAFAEL', xpn_3='LUCERO')
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Katipunan Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1108', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-917-301-4456'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH801234567800')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='201', pl_3='A', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LACSAMANA^ROBERTO^MAGNO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250401090000'
        pv1.total_charges = '20250405150000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I24.9', cwe_2='Acute ischemic heart disease, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='Atherosclerotic heart disease without angina', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250401'
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
    """ Based on live/ph/ph-medprojects.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250406110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8045678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250406-0011', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='QUISUMBING', xpn_2='ANDRES', xpn_3='FELICIANO')
        pid.date_time_of_birth = '19800228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amorsolo St', xad_3='Makati', xad_4='NCR', xad_5='1229', xad_6='PH')
        pid.pid_13 = '+63-2-8888-8999~+63-928-602-3378'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH804567890100')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-4A', pl_2='402', pl_3='B', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250405080000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250406-003')
        orc.orc_12 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250406-003')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr.observation_date_time = '20250406060000'
        obr.obr_16 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250406110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Blood Cell Count', cwe_3='L')
        obx.obx_5 = '14.5'
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
        obx_2.obx_5 = '4.8'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.50-5.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobin', cwe_3='L')
        obx_3.obx_5 = '145'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-170'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrit', cwe_3='L')
        obx_4.obx_5 = '0.43'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.40-0.50'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='L')
        obx_5.obx_5 = '320'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
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
    """ Based on live/ph/ph-medprojects.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='CDU_CEBU')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='CDU_CEBU')
        msh.date_time_of_message = '20250407100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MC-MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT-20250414-001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Orthopedic follow-up', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20250414090000^20250414093000'
        sch.sch_13 = 'VILLAROSA^CARLOS^MENDEZ^^^DR^MD'
        sch.placer_contact_address = XAD(xad_1='+63-32-253-7511')
        sch.placer_contact_location = PL(pl_1='CDU ORTHO CLINIC', pl_3='Cebu City', pl_4='VII', pl_5='6000', pl_6='PH')
        sch.filler_contact_person = XCN(xcn_1='CDU_CEBU')
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8056789012', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDU-20250407-0005', cx_4='CDU', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MONTECILLO', xpn_2='DANILO', xpn_3='AGUSTIN')
        pid.date_time_of_birth = '19750515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Banilad Rd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-253-7511~+63-920-815-4490'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH805678901200')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
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
        ais.universal_service_identifier = CWE(cwe_1='ORTHO-FU', cwe_2='Orthopedic Follow-up', cwe_3='L')
        ais.start_date_time = '20250414090000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'VILLAROSA^CARLOS^MENDEZ^^^DR^MD'
        aip.resource_type = CWE(cwe_1='ORTHO')
        aip.start_date_time_offset_units = CNE(cne_1='20250414090000')
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
    """ Based on live/ph/ph-medprojects.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250408080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'MC-MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'ORD-MC-20250408-001'
        msa.msa_3 = 'Order routed and acknowledged by LIS'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/ph/ph-medprojects.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250409160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MC-MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250409160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8067890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250407-0077', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PAGLICAWAN', xpn_2='JOSEFINA', xpn_3='ALVAREZ')
        pid.date_time_of_birth = '19700315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Julia Vargas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1605', xad_6='PH')
        pid.pid_13 = '+63-2-8689-7700~+63-906-331-8845'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH806789012300')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3B', pl_2='315', pl_3='A', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250407090000'
        pv1.total_charges = '20250409160000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20250409150000'
        txa.txa_5 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        txa.transcription_date_time = '20250409160000'
        txa.txa_9 = 'TAÑEDO^ERNESTO^LOZANO^^^DR^MD'
        txa.parent_document_number = EI(ei_1='DOC-MC-20250409-001')
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
            'IC0gVE1DIFBhc2lnKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9i'
            'agp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAw'
            'MDAgbiAKMDAwMDAwMDQxMSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjUwMgolJUVPRgo='
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
    """ Based on live/ph/ph-medprojects.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='CDU_CEBU')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='CDU_CEBU')
        msh.date_time_of_message = '20250410093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MC-MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250410093000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8078901234', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDU-20250408-0044', cx_4='CDU', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='YBANEZ', xpn_2='CRISTINA', xpn_3='ABOGADO')
        pid.date_time_of_birth = '19880614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-253-7511~+63-935-920-5541'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH807890123400')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-5A', pl_2='505', pl_3='B', pl_4='CDU_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'VILLAROSA^CARLOS^MENDEZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'VILLAROSA^CARLOS^MENDEZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDU_CEBU'
        pv1.discharge_date_time = '20250408090000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='YBANEZ', xpn_2='LEON', xpn_3='TORREFRANCA')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Osmena Blvd', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        nk1.nk1_5 = '+63-935-920-5542'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/ph/ph-medprojects.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='CDO_HOSP')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='CDO_HOSP')
        msh.date_time_of_message = '20250411140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8089012345', cx_4='PHIC', cx_5='SS'), CX(cx_1='CDO-20250411-0022', cx_4='CDO', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='CABRERA', xpn_2='WILFREDO', xpn_3='TUMBOKON')
        pid.date_time_of_birth = '19600905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Corrales Ave', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-857-1000~+63-917-432-6690'
        pid.primary_language = CWE(cwe_1='CEB')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH808901234500')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='310', pl_3='A', pl_4='CDO_HOSP', pl_7='P')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'SORIANO^GRACE^MARIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'SORIANO^GRACE^MARIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDO_HOSP'
        pv1.discharge_date_time = '20250410140000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250411-005')
        orc.orc_12 = 'SORIANO^GRACE^MARIANO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250411-005')
        obr.universal_service_identifier = CWE(cwe_1='ELEC', cwe_2='Electrolyte Panel', cwe_3='L')
        obr.observation_date_time = '20250411060000'
        obr.obr_16 = 'SORIANO^GRACE^MARIANO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250411140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='NA', cwe_2='Sodium', cwe_3='L')
        obx.obx_5 = '141'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136-145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='L')
        obx_2.obx_5 = '4.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CL', cwe_2='Chloride', cwe_3='L')
        obx_3.obx_5 = '103'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98-106'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='CO2', cwe_2='Total CO2', cwe_3='L')
        obx_4.obx_5 = '25'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-29'
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
    """ Based on live/ph/ph-medprojects.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='ALL')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250412090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'MC-MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250412090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8190123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='SLMC-20250301-0099', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GATMAITAN', xpn_2='ENRIQUE', xpn_3='BUENAFLOR')
        pid.date_time_of_birth = '19730515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Aurora Blvd', xad_3='Quezon City', xad_4='NCR', xad_5='1112', xad_6='PH')
        pid.pid_13 = '+63-2-8723-0101~+63-906-209-3318'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH819012345600')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='SLMC-20250115-DUP022', cx_4='SLMC', cx_5='MR')
        mrg.mrg_2 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REG', pl_2='001', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.visit_number = CX(cx_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='PHIC')
        pv1.account_status = CWE(cwe_1='SLMC_QC')
        pv1.current_patient_balance = '20250412090000'

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
    """ Based on live/ph/ph-medprojects.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='PHARM')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250413080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MC-MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8101234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250412-0033', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TOLENTINO', xpn_2='GREGORIO', xpn_3='MANANSALA')
        pid.date_time_of_birth = '19750210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ayala Ave', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8888-8999~+63-917-615-8832'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH810123456700')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3A', pl_2='310', pl_3='B', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250412090000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250413-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250413080000'
        orc.orc_10 = 'NURSE^ROWENA^CASTILLO'
        orc.enterers_location = PL(pl_1='MMC_MAKATI')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='ENALAPRIL', cwe_2='Enalapril 10mg', cwe_3='L')
        rxo.requested_give_amount_minimum = '10'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo.allow_substitutions = '1^OD'
        rxo.rxo_14 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='FURO', cwe_2='Furosemide 40mg', cwe_3='L')
        rxo_2.requested_give_amount_minimum = '40'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo_2.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo_2.allow_substitutions = '1^OD AM'
        rxo_2.rxo_14 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxo_2]

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
    """ Based on live/ph/ph-medprojects.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='SPMC_DAVAO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='SPMC_DAVAO')
        msh.date_time_of_message = '20250414100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'MC-MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250414100000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='PRE-REG')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8112345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='SPMC-20250414-0011', cx_4='SPMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BATUNGBAKAL', xpn_2='LEILANI', xpn_3='CORDERO')
        pid.date_time_of_birth = '19820730'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bolton St', xad_3='Davao City', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-227-2731~+63-935-481-6623'
        pid.primary_language = CWE(cwe_1='BIS')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH811234567800')
        pid.mothers_identifier = CX(cx_1='Davao City', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BATUNGBAKAL', xpn_2='RODEL', xpn_3='FAJARDO')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Bolton St', xad_3='Davao City', xad_4='XI', xad_5='8000', xad_6='PH')
        nk1.nk1_5 = '+63-935-481-6624'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG-PRE', pl_2='001', pl_4='SPMC_DAVAO', pl_7='P')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'REGALADO^ANTONIO^BELMONTE^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'REGALADO^ANTONIO^BELMONTE^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='PR')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SPMC_DAVAO'
        pv1.discharge_date_time = '20250414100000'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-medprojects.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='TMC_TAGUIG')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='TMC_TAGUIG')
        msh.date_time_of_message = '20250415143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8123456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='TMC-20250415-0005', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGBANUA', xpn_2='AURORA', xpn_3='ILAGAN')
        pid.date_time_of_birth = '19900420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='McKinley Rd', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8789-7700~+63-928-503-2241'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH812345678900')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-INF', pl_2='001', pl_4='TMC_TAGUIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'DALISAY^RAMON^PANGILINAN^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'DALISAY^RAMON^PANGILINAN^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_TAGUIG'
        pv1.discharge_date_time = '20250415080000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250415-001')
        orc.orc_12 = 'DALISAY^RAMON^PANGILINAN^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250415-001')
        obr.universal_service_identifier = CWE(cwe_1='COVID', cwe_2='SARS-CoV-2 RT-PCR', cwe_3='L')
        obr.observation_date_time = '20250415083000'
        obr.obr_16 = 'DALISAY^RAMON^PANGILINAN^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250415143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='COVID-PCR', cwe_2='SARS-CoV-2 RT-PCR', cwe_3='L')
        obx.obx_5 = 'NOT DETECTED'
        obx.reference_range = 'NOT DETECTED'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='COVID-CT', cwe_2='Cycle Threshold', cwe_3='L')
        obx_2.reference_range = '<37.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

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
    """ Based on live/ph/ph-medprojects.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250416090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A31')
        msh.message_control_id = 'MC-MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250416090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8134567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='PGH-20250416-0002', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='SALCEDO', xpn_2='ESPERANZA', xpn_3='VILLAREAL')
        pid.date_time_of_birth = '19850912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Padre Faura St', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8554-8400~+63-917-712-0055'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH813456789000')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-GEN', pl_2='001', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BUENAVENTURA^MIGUEL^OCAMPO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250416090000'

        # .. assemble the full message ..
        msg = ADT_A05()
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
    """ Based on live/ph/ph-medprojects.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250417142000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MC-MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH8145678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='MMC-20250417-0009', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RESURRECCION', xpn_2='GABRIELA', xpn_3='NAVIDAD')
        pid.date_time_of_birth = '19700110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Paseo de Roxas', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8888-8999~+63-935-510-7723'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH814567890100')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2B', pl_2='220', pl_3='A', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GI')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250416100000'

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
        orc.placer_order_number = EI(ei_1='ORD-MC-20250417-004')
        orc.orc_12 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-MC-20250417-004')
        obr.universal_service_identifier = CWE(cwe_1='LFT', cwe_2='Liver Function Test', cwe_3='L')
        obr.observation_date_time = '20250417060000'
        obr.obr_16 = 'EVANGELISTA^PATRICIA^DOMINGUEZ^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250417142000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='ALT', cwe_2='Alanine Aminotransferase', cwe_3='L')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='AST', cwe_2='Aspartate Aminotransferase', cwe_3='L')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='ALP', cwe_2='Alkaline Phosphatase', cwe_3='L')
        obx_3.obx_5 = '120'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='GGT', cwe_2='Gamma-Glutamyl Transferase', cwe_3='L')
        obx_4.obx_5 = '85'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '9-48'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='TBIL', cwe_2='Total Bilirubin', cwe_3='L')
        obx_5.obx_5 = '28'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '5-21'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='ALB', cwe_2='Albumin', cwe_3='L')
        obx_6.obx_5 = '32'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-52'
        obx_6.interpretation_codes = CWE(cwe_1='L')
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

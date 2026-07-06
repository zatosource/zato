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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, \
    DftP03Visit, MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIG, AIL, AIS, AL1, DG1, EVN, FT1, IN1, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PRA, PV1, PV2, \
    RGS, RXA, RXC, RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-mckesson.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260401110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MCKN20260401110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401105500'
        evn.evn_5 = 'EDRN^Pemberton^Rosa^M^^^RN'
        evn.event_occurred = '20260401105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN60001', cx_4='SHANNONMC', cx_5='MR'), CX(cx_1='538-71-4296', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Esparza^Miguel^Renaldo^^Mr.^'
        pid.date_time_of_birth = '19680225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3020 Knickerbocker Rd', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5559123'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '538-71-4296'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Shannon Medical Center^^^^NPI'
        pd1.pd1_4 = '1234560101^Westbrook^Roberto^C^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Esparza', xpn_2='Isabel', xpn_3='Rosario', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3020 Knickerbocker Rd', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^325^5559124'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2104', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '1234560101^Westbrook^Roberto^C^^^MD^^^^NPI'
        pv1.pv1_8 = '2345670202^Fairchild^Diane^L^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='A', cwe_2='Accident', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260401001^^^SHANNONMC^VN'
        pv1.discharge_date_time = '20260401105500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Diabetic ketoacidosis with glucose 487 mg/dL')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E10.10', cwe_2='Type 1 diabetes mellitus with ketoacidosis without coma', cwe_3='I10')
        dg1.diagnosis_date_time = '20260401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E87.2', cwe_2='Acidosis', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260401'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BCBS001')
        in1.insurance_company_id = CX(cx_1='60054', cx_2='Blue Cross Blue Shield of Texas')
        in1.in1_4 = 'BCBSTX^^Dallas^TX^75201'
        in1.group_name = XON(xon_1='BCBSGRP')
        in1.plan_type = CWE(cwe_1='Esparza', cwe_2='Miguel', cwe_3='Renaldo')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19680225')
        in1.insureds_date_of_birth = '3020 Knickerbocker Rd^^San Angelo^TX^76904^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='BCBSPOL678901')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]
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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260403140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MCKN20260403140000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260403135500'
        evn.evn_5 = 'SURGRN^Lockwood^Janet^R^^^RN'
        evn.event_occurred = '20260403135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60002', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Ashworth^Dorothy^Elaine^^Mrs.^'
        pid.date_time_of_birth = '19450718'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1501 Pine St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5558234'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '241-52-8937'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='3101', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '3456780303^Greenfield^Steven^M^^^MD^^^^NPI'
        pv1.pv1_8 = '4567890404^Northcutt^Linda^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='GS', xcn_2='General Surgery', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260401002^^^CITIZENSMC^VN'
        pv1.servicing_facility = CWE(cwe_1='01', cwe_2='Discharged to home', cwe_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20260401130000')
        pv1.admit_date_time = '20260403135500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K35.80', cwe_2='Unspecified acute appendicitis without perforation', cwe_3='I10')
        dg1.diagnosis_date_time = '20260401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='44970', cne_2='Laparoscopic appendectomy', cne_3='CPT4')
        pr1.pr1_4 = '^Laparoscopic appendectomy'
        pr1.procedure_date_time = '20260401150000'
        pr1.anesthesia_minutes = '3456780303^Greenfield^Steven^M^^^MD^^^^NPI'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1
        msg.procedure = procedure

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260404110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MCKN20260404110000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60003', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Grayson^Gloria^Renee^^Ms.^'
        pid.date_time_of_birth = '19720620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4200 College Hills Blvd', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5553456'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '372-84-6153'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260404003', cx_4='SHANNONMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60003', ei_2='MCKN')
        orc.filler_order_number = EI(ei_1='FIL60003', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260404080000')
        orc.orc_11 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60003', ei_2='MCKN')
        obr.filler_order_number = EI(ei_1='FIL60003', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='34015-7', cwe_2='Thyroid function panel', cwe_3='LN')
        obr.observation_date_time = '20260404080000'
        obr.obr_16 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260404103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH [Units/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '8.7'
        obx.units = CWE(cwe_1='mIU/L', cwe_2='milli-international units per liter', cwe_3='UCUM')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260404103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4 [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '0.6'
        obx_2.units = CWE(cwe_1='ng/dL', cwe_2='nanograms per deciliter', cwe_3='UCUM')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260404103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3 [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '1.8'
        obx_3.units = CWE(cwe_1='pg/mL', cwe_2='picograms per milliliter', cwe_3='UCUM')
        obx_3.reference_range = '2.3-4.2'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260404103000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5385-0', cwe_2='Thyroid peroxidase Ab [Units/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='IU/mL', cwe_2='international units per milliliter', cwe_3='UCUM')
        obx_4.reference_range = '<9'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260404103000'

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260405090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MCKN20260405090000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60004', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Bradshaw^Betty^Caroline^^Mrs.^'
        pid.date_time_of_birth = '19520830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='302 E Airline Rd', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5559012'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '483-69-2107'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='0002', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260405004', cx_4='CITIZENSMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60004', ei_2='MCKN')
        orc.placer_order_group_number = EI(ei_1='GRP60004', ei_2='MCKN')
        orc.date_time_of_order_event = '20260405083000'
        orc.orc_12 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'
        orc.orc_17 = 'CITIZENSMC^Citizens Medical Center'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60004', ei_2='MCKN')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DXA bone density axial', cwe_3='CPT4')
        obr.observation_date_time = '20260405083000'
        obr.obr_15 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M81.0', cwe_2='Age-related osteoporosis without current pathological fracture', cwe_3='I10')
        dg1.diagnosis_date_time = '20260405'
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
        nte.comment = 'Postmenopausal woman age 73. History of wrist fracture 2023. Follow-up DEXA scan.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260406140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MCKN20260406140000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60004', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Bradshaw^Betty^Caroline^^Mrs.^'
        pid.date_time_of_birth = '19520830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='302 E Airline Rd', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5559012'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '483-69-2107'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='0002', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260406005', cx_4='CITIZENSMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60005', ei_2='MCKN')
        orc.filler_order_number = EI(ei_1='FIL60005', ei_2='RAD')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260405100000')
        orc.orc_11 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60005', ei_2='MCKN')
        obr.filler_order_number = EI(ei_1='FIL60005', ei_2='RAD')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DXA bone density axial', cwe_3='CPT4')
        obr.observation_date_time = '20260405100000'
        obr.obr_16 = '6789010606^Whitfield^Patricia^B^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260406133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='46278-8', cwe_2='BMD femoral neck T-score', cwe_3='LN')
        obx.obx_5 = '-2.8'
        obx.reference_range = '>-1.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260406133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='46275-4', cwe_2='BMD lumbar spine T-score', cwe_3='LN')
        obx_2.obx_5 = '-3.1'
        obx_2.reference_range = '>-1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260406133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='77080', cwe_2='DXA interpretation', cwe_3='L')
        obx_3.obx_5 = (
            'DEXA SCAN REPORT\\.br\\\\.br\\Femoral Neck: T-score -2.8 (Osteoporosis)\\.br\\Lumbar Spine L1-L4: T-score -3.1 (Osteoporosis)\\.br\\\\.br\\IMPRE'
            'SSION: Osteoporosis at both sites. Worsened from prior study (2023 T-scores: femoral neck -2.3, lumbar -2.7).\\.br\\RECOMMENDATION: Continue b'
            'isphosphonate therapy. Consider endocrinology referral.'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260406133000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='DEXA Scan Report', cwe_3='AUSPDI')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMjgKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihERVhBIEJvbmUgRGVuc2l0'
            'eSBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooQ2l0aXplbnMgTWVkaWNhbCBDZW50ZXIpIFRqCjAgLTIwIFRkCihQYXRpZW50OiBCcmFkc2hhdywgQmV0dHkpIFRqCkVUCmVu'
            'ZHN0cmVhbQplbmRvYmoK'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260406133000'

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260407100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MCKN20260407100000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260407095500'
        evn.evn_5 = 'PHRN^Lockwood^Amanda^T^^^RN'
        evn.event_occurred = '20260407095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60006', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Saucedo^Carmen^Valentina^^Mrs.^'
        pid.date_time_of_birth = '19830914'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1910 Sherwood Way', xad_3='San Angelo', xad_4='TX', xad_5='76901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5554567'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '591-73-8204'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2201', pl_3='02', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '7890120707^Aldridge^James^B^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260406006', cx_4='SHANNONMC', cx_5='VN')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='Drug allergy', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='70618', cwe_2='Penicillin', cwe_3='RxNorm')
        al1.allergy_severity_code = CWE(cwe_1='SV', cwe_2='Severe', cwe_3='HL70128')
        al1.allergy_reaction_code = 'Anaphylaxis'
        al1.al1_6 = '20150320'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='DA', cwe_2='Drug allergy', cwe_3='HL70127')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='2670', cwe_2='Codeine', cwe_3='RxNorm')
        al1_2.allergy_severity_code = CWE(cwe_1='MO', cwe_2='Moderate', cwe_3='HL70128')
        al1_2.allergy_reaction_code = 'Nausea and vomiting'
        al1_2.al1_6 = '20180115'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.al1 = [al1, al1_2]

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260408090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MCKN20260408090000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT60007', ei_2='MCKN')
        sch.appointment_reason = CWE(cwe_1='ORTFU', cwe_2='Orthopedic Follow-up', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='20', cwe_2='MIN')
        sch.sch_9 = 'MIN^Minutes^ISO+'
        sch.appointment_duration_units = CNE(cne_4='20260415093000', cne_6='20', cne_7='MIN')
        sch.placer_contact_location = PL(pl_1='8901230808', pl_2='Hargrove', pl_3='David', pl_4='W', pl_7='MD', pl_11='NPI')
        sch.sch_16 = '^PRN^PH^^1^361^5553456'
        sch.sch_21 = '8901230808^Hargrove^David^W^^^MD^^^^NPI'
        sch.placer_order_number = EI(ei_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60007', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Delaney^William^Patrick^^Mr.^'
        pid.date_time_of_birth = '19610422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='601 E Rio Grande St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5557890'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '714-83-9265'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='0001', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8901230808^Hargrove^David^W^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Orthopedics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408007', cx_4='CITIZENSMC', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='ORT_CLINIC')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='99214', cwe_2='Office visit established level 4', cwe_3='CPT4')
        ais.start_date_time = '20260415093000'
        ais.duration = '20^MIN'
        ais.duration_units = CNE(cne_1='MIN', cne_2='Minutes', cne_3='ISO+')
        ais.filler_status_code = CWE(cwe_1='Confirmed')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='8901230808', cwe_2='Hargrove', cwe_3='David', cwe_4='W', cwe_7='MD', cwe_11='NPI')
        aig.start_date_time = '20260415093000'
        aig.duration = '20^MIN'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='ORT', pl_2='0001', pl_3='01', pl_4='CITIZENSMC')
        ail.start_date_time_offset_units = CNE(cne_1='20260415093000')
        ail.allow_substitution_code = CWE(cwe_1='20', cwe_2='MIN')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = '6-week follow-up post right hip arthroplasty. Evaluate wound, ROM, and weight-bearing status.'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail
        location_resource.nte = nte

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.general_resource = general_resource
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PHARM_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260409180000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MCKN20260409180000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60008', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Hubbard^Raymond^Curtis^^Mr.^'
        pid.date_time_of_birth = '19570311'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2800 Sunset Dr', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5558901'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '804-26-3571'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2105', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '9012340909^Thornton^Linda^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260409008', cx_4='SHANNONMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60008', ei_2='MCKN')
        orc.placer_order_group_number = EI(ei_1='GRP60008', ei_2='MCKN')
        orc.date_time_of_order_event = '20260409173000'
        orc.orc_12 = '9012340909^Thornton^Linda^A^^^MD^^^^NPI'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^CONTINUOUS^HL70335'
        rxe.give_code = CWE(cwe_1='5224', cwe_2='Heparin sodium 25000 units/500 mL', cwe_3='NDC')
        rxe.give_amount_minimum = '25000'
        rxe.give_amount_maximum = '25000'
        rxe.give_units = CWE(cwe_1='units', cwe_2='units', cwe_3='ISO+')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxe.number_of_refills = '0'
        rxe.prescription_number = '9012340909^Thornton^Linda^A^^^MD^^^^NPI'
        rxe.supplementary_code = CWE(cwe_1='0', cwe_2='MIN')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenous', cwe_3='HL70162')

        # .. build RXC ..
        rxc = RXC()
        rxc.rx_component_type = 'B'
        rxc.component_code = CWE(cwe_1='D5W')
        rxc.component_amount = '500'
        rxc.component_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr
        order.rxc = rxc

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.99', cwe_2='Other pulmonary embolism without acute cor pulmonale', cwe_3='I10')
        dg1.diagnosis_date_time = '20260409'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Weight-based heparin protocol. Loading dose 80 units/kg bolus, then 18 units/kg/hr. Target aPTT 60-80 seconds. Check aPTT q6h.'

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [dg1, nte]

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260410140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MCKN20260410140000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260410135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60002', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Ashworth^Dorothy^Elaine^^Mrs.^'
        pid.date_time_of_birth = '19450718'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1501 Pine St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5558234'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '241-52-8937'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='3101', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '3456780303^Greenfield^Steven^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='GS', xcn_2='General Surgery', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260401002', cx_4='CITIZENSMC', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operative Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260410135000')
        txa.transcriptionist_code_name = XCN(xcn_1='DOC60009', xcn_2='CITIZENSMC')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='28572-5', cwe_2='Operative note', cwe_3='LN')
        obx.obx_5 = (
            'OPERATIVE REPORT\\.br\\Patient: Ashworth, Dorothy Elaine\\.br\\DOB: 07/18/1945\\.br\\Procedure Date: 04/01/2026\\.br\\\\.br\\PROCEDURE: Laparosc'
            'opic appendectomy\\.br\\SURGEON: Steven M. Greenfield, MD\\.br\\ANESTHESIA: General endotracheal\\.br\\\\.br\\INDICATIONS: 80-year-old female wi'
            'th acute appendicitis confirmed by CT scan\\.br\\\\.br\\FINDINGS: Inflamed, non-perforated appendix with surrounding erythema\\.br\\\\.br\\TECHN'
            'IQUE: Standard 3-port laparoscopic technique. Mesoappendix divided with harmonic scalpel. Appendix base secured with two endoloops and divid'
            'ed. Specimen retrieved in endocatch bag. Hemostasis confirmed.\\.br\\\\.br\\ESTIMATED BLOOD LOSS: 15 mL\\.br\\COMPLICATIONS: None\\.br\\SPECIMEN'
            'S: Appendix to pathology'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260410135000'

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='FIN_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260411160000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'MCKN20260411160000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260411155500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60010', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Tovar^Ana^Marisol^^Mrs.^'
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1515 S Bryant Blvd', xad_3='San Angelo', xad_4='TX', xad_5='76903', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5551234'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '827-41-5063'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0002', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260411010', cx_4='SHANNONMC', cx_5='VN')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_date = DR(dr_1='20260411090000')
        ft1.transaction_posting_date = '20260411093000'
        ft1.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1.transaction_code = CWE(cwe_1='99215', cwe_2='Office visit established level 5', cwe_3='CPT4')
        ft1.ft1_9 = '1'
        ft1.assigned_patient_location = PL(pl_1='CLI', pl_2='0002', pl_3='01', pl_4='SHANNONMC')
        ft1.ft1_21 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_date = DR(dr_1='20260411093000')
        ft1_2.transaction_posting_date = '20260411093000'
        ft1_2.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_2.transaction_code = CWE(cwe_1='36415', cwe_2='Venipuncture routine', cwe_3='CPT4')
        ft1_2.ft1_9 = '1'
        ft1_2.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='SHANNONMC')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_date = DR(dr_1='20260411094000')
        ft1_3.transaction_posting_date = '20260411094000'
        ft1_3.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_3.transaction_code = CWE(cwe_1='93000', cwe_2='ECG routine', cwe_3='CPT4')
        ft1_3.ft1_9 = '1'
        ft1_3.assigned_patient_location = PL(pl_1='CLI', pl_2='0002', pl_3='01', pl_4='SHANNONMC')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essential primary hypertension', cwe_3='I10')
        dg1.diagnosis_date_time = '20260411'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E11.65', cwe_2='Type 2 diabetes mellitus with hyperglycemia', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260411'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis_2 = DftP03Diagnosis()
        diagnosis_2.dg1 = dg1_2

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2, financial_3]
        msg.diagnosis = [diagnosis, diagnosis_2]

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TX_DSHS')
        msh.date_time_of_message = '20260412103000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'MCKN20260412103000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'ER'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60011', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Langston^James^Terrence^^Mr.^'
        pid.date_time_of_birth = '19890228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='904 E Mockingbird Ln', xad_3='Victoria', xad_4='TX', xad_5='77904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5553210'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '946-18-3072'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '0123451111^Caldwell^Sandra^K^^^MD^^^^NPI'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0001', pl_3='01', pl_4='CITIZENSMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '0123451111^Caldwell^Sandra^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260412011', cx_4='CITIZENSMC', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD60011', ei_2='MCKN')
        orc.placer_order_group_number = EI(ei_1='GRP60011', ei_2='MCKN')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260412100000')
        orc.orc_11 = '0123451111^Caldwell^Sandra^K^^^MD^^^^NPI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20260412100000'
        rxa.administered_code = CWE(cwe_1='115', cwe_2='Tdap', cwe_3='CVX')
        rxa.administered_amount = '0.5'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.rxa_15 = '49281-0400-15^^NDC'
        rxa.completion_status = 'CP^Complete^HL70322'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LD', cwe_2='Left Deltoid', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Vaccine funding program eligibility category', cwe_3='LN')
        obx.obx_5 = 'V01^Not VFC eligible^HL70064'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TS'
        obx_2.observation_identifier = CWE(cwe_1='29768-9', cwe_2='Date vaccine information statement published', cwe_3='LN')
        obx_2.obx_5 = '20240101'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TS'
        obx_3.observation_identifier = CWE(cwe_1='29769-7', cwe_2='Date vaccine information statement presented', cwe_3='LN')
        obx_3.obx_5 = '20260412'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = VxuV04Observation()
        observation_3.obx = obx_3

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation
        order.observation_2 = observation_2
        order.observation_3 = observation_3

        # .. assemble the full message ..
        msg = VXU_V04()
        msg.msh = msh
        msg.pid = pid
        msg.pd1 = pd1
        msg.patient_visit = patient_visit
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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260413080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MCKN20260413080000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260413075500'
        evn.evn_5 = 'REG^Montoya^Maria^C^^^ADM'
        evn.event_occurred = '20260413075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60012', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Truong^Lisa^Phuong^^Ms.^'
        pid.date_time_of_birth = '19950312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3100 W Beauregard Ave', xad_3='San Angelo', xad_4='TX', xad_5='76901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5557890'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '147-62-3891'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0001', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '1234561212^Westbrook^Roberto^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260413012', cx_4='SHANNONMC', cx_5='VN')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Sore throat and low-grade fever for 3 days')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J02.9', cwe_2='Acute pharyngitis unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260413'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260414110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MCKN20260414110000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60010', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Tovar^Ana^Marisol^^Mrs.^'
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1515 S Bryant Blvd', xad_3='San Angelo', xad_4='TX', xad_5='76903', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5551234'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '827-41-5063'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260414013', cx_4='SHANNONMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60013', ei_2='MCKN')
        orc.filler_order_number = EI(ei_1='FIL60013', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260414080000')
        orc.orc_11 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60013', ei_2='MCKN')
        obr.filler_order_number = EI(ei_1='FIL60013', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obr.observation_date_time = '20260414080000'
        obr.obr_16 = '5678900505^Pemberton^Margaret^A^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260414103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obx.obx_5 = '9.2'
        obx.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx.reference_range = '<5.7'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260414103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '198'
        obx_2.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_2.reference_range = '74-106'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260414103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Lab Report', cwe_3='AUSPDI')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMTgKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihMYWJvcmF0b3J5IFJlcG9y'
            'dCkgVGoKMCAtMjAgVGQKL0YxIDEwIFRmCihTaGFubm9uIE1lZGljYWwgQ2VudGVyKSBUagowIC0yMCBUZAooSGJBMWM6IDkuMiUpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260414103000'

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260415100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MCKN20260415100000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260415095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN60014', cx_4='CITIZENSMC', cx_5='MR'), CX(cx_1='782-15-4630', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Kapoor^Tiffany^Anisha^^Ms.^'
        pid.date_time_of_birth = '19880107'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2300 N Navarro St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5554567'
        pid.pid_14 = '^WPN^PH^^1^361^5559876'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '782-15-4630'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Citizens Medical Center^^^^NPI'
        pd1.pd1_4 = '8901230808^Hargrove^David^W^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Kapoor', xpn_2='Priya', xpn_3='Sunita', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2300 N Navarro St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^361^5554568'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260416200000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MCKN20260416200000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260416195500'
        evn.evn_5 = 'MEDRN^Fairchild^Tanya^R^^^RN'
        evn.event_occurred = '20260416195500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60015', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Hinojosa^Jose^Alejandro^^Mr.^'
        pid.date_time_of_birth = '19740628'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4100 Arden Rd', xad_3='San Angelo', xad_4='TX', xad_5='76901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5553789'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '362-48-7193'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2108', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '1234561515^Westbrook^Roberto^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260416015^^^SHANNONMC^VN'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain, troponin negative, observation to inpatient conversion')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260417100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MCKN20260417100000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260417095500'
        evn.evn_5 = 'HIM^Stanfield^Karen^D^^^HIM'
        evn.event_occurred = '20260417095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60016', cx_4='CITIZENSMC', cx_5='MR')
        pid.pid_5 = 'Garibay^Maria^Luciana^^Mrs.^'
        pid.date_time_of_birth = '19830915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1800 E Red River St', xad_3='Victoria', xad_4='TX', xad_5='77901', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^361^5558901'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '473-59-6284'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN60016DUP', cx_4='CITIZENSMC', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='Garibay', xpn_2='Maria', xpn_3='L')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260418110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MCKN20260418110000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260418105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60017', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Forsythe^Brenda^Colleen^^Mrs.^'
        pid.date_time_of_birth = '19600212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2500 Loop 306', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5556789'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '581-64-9037'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Shannon Medical Center^^^^NPI'
        pd1.pd1_4 = '2345671717^Stratton^Maria^R^^^MD^^^^NPI'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='CITIZENSMC', hd_2='2.16.840.1.113883.3.5502', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MF_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260419090000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'MCKN20260419090000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='Practitioner master file', cwe_3='HL70175')
        mfi.file_level_event_code = 'UPD^Update^HL70180'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD^Add record to master file^HL70180'
        mfe.mfn_control_id = '20260419085500'
        mfe.mfe_4 = '3456781818^Yamazaki^Daniel^Koji^^MD'
        mfe.primary_key_value_type = 'CWE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='3456781818')
        stf.staff_identifier_list = CX(cx_1='U3456781818')
        stf.staff_name = XPN(xpn_1='Yamazaki', xpn_2='Daniel', xpn_3='Koji', xpn_5='MD')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19850314'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.stf_12 = '^WPN^PH^^1^361^5551234'

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='3456781818', cwe_2='Yamazaki', cwe_3='Daniel', cwe_4='Koji', cwe_6='MD')
        pra.practitioner_group = CWE(cwe_1='CITIZENSMC', cwe_2='Citizens Medical Center')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='Institution', cwe_3='HL70186')
        pra.date_entered_practice = '208M00000X^Hospitalist^NUCC'

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf
        mf_staff.pra = pra

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = mf_staff

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PARAGON')
        msh.sending_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260420020000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MCKN20260420020000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60019', cx_4='SHANNONMC', cx_5='MR')
        pid.pid_5 = 'Joiner^Patricia^Elise^^Mrs.^'
        pid.date_time_of_birth = '19780530'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3600 N Chadbourne St', xad_3='San Angelo', xad_4='TX', xad_5='76903', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^325^5552345'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '693-82-4150'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2103', pl_3='01', pl_4='SHANNONMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260419019', cx_4='SHANNONMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60019', ei_2='MCKN')
        orc.placer_order_group_number = EI(ei_1='GRP60019', ei_2='MCKN')
        orc.date_time_of_order_event = '20260420013000'
        orc.orc_12 = '4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI'
        orc.orc_17 = 'SHANNONMC^Shannon Medical Center'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60019', ei_2='MCKN')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Blood culture bacterial', cwe_3='CPT4')
        obr.observation_date_time = '20260420013000'
        obr.obr_15 = '4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI'
        obr.result_status = '9^Stat^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R65.20', cwe_2='Severe sepsis without septic shock', cwe_3='I10')
        dg1.diagnosis_date_time = '20260419'
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
        nte.comment = 'Febrile to 39.4C, WBC 18.2, tachycardic. Collect 2 sets from separate sites before starting antibiotics.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/us-texas/us-texas-mckesson.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_RECV')
        msh.sending_facility = HD(hd_1='TX_HIE')
        msh.receiving_application = HD(hd_1='PARAGON')
        msh.receiving_facility = HD(hd_1='SHANNONMC', hd_2='2.16.840.1.113883.3.5501', hd_3='ISO')
        msh.date_time_of_message = '20260421080000'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'MCKN20260421080000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MCKN20260420020000019'
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

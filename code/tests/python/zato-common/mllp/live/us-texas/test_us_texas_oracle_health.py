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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, EIP, ERL, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, \
    DftP03Visit, MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIG, AIL, AIS, DG1, ERR, EVN, FT1, IN1, IN2, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PRA, PV1, \
    PV2, RGS, RXA, RXC, RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-oracle-health.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260410081500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CERN20260410081500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260410080000'
        evn.evn_5 = 'ADMRN^Carrington^Jolene^T^^^RN'
        evn.event_occurred = '20260410080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN30001', cx_4='JPSHN', cx_5='MR'), CX(cx_1='648-91-3207', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Longoria^Mateo^Alejandro^^Mr.^'
        pid.date_time_of_birth = '19720314'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3417 Bluebonnet Cir', xad_3='Fort Worth', xad_4='TX', xad_5='76109', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5539247'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '648-91-3207'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'JPS Health Network^^^^NPI'
        pd1.pd1_4 = '1834927561^Danforth^Steven^R^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Longoria', xpn_2='Catalina', xpn_3='Sofia', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3417 Bluebonnet Cir', xad_3='Fort Worth', xad_4='TX', xad_5='76109', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^682^5539248'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULM', pl_2='3204', pl_3='02', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '1834927561^Danforth^Steven^R^^^MD^^^^NPI'
        pv1.pv1_8 = '2947183605^Eastman^Rachel^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PUL', xcn_2='Pulmonology', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='A', cwe_2='Accident', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260410001^^^JPSHN^VN'
        pv1.discharge_date_time = '20260410080000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Community acquired pneumonia with hypoxia')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.1', cwe_2='Lobar pneumonia unspecified organism', cwe_3='I10')
        dg1.diagnosis_date_time = '20260410'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J96.01', cwe_2='Acute respiratory failure with hypoxia', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260410'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MCARE001')
        in1.insurance_company_id = CX(cx_1='00451', cx_2='Medicare')
        in1.in1_4 = 'Centers for Medicare^^Baltimore^MD^21244'
        in1.group_name = XON(xon_1='MCAREGRP')
        in1.plan_type = CWE(cwe_1='Longoria', cwe_2='Mateo', cwe_3='Alejandro')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19720314')
        in1.insureds_date_of_birth = '3417 Bluebonnet Cir^^Fort Worth^TX^76109^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='MCAREPOL234567')

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260412153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CERN20260412153000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260412152500'
        evn.evn_5 = 'LDRN^Fulbright^Tamara^N^^^RN'
        evn.event_occurred = '20260412152500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30002', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Gatewood^Tamika^Renee^^Mrs.^'
        pid.date_time_of_birth = '19930818'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4017 W Pioneer Pkwy', xad_3='Arlington', xad_4='TX', xad_5='76013', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5538476'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '314-58-7923'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OB', pl_2='2101', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '3751842960^Garrison^Michelle^A^^^MD^^^^NPI'
        pv1.pv1_8 = '4068293175^Blackwood^Sandra^L^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='OBG', xcn_2='Obstetrics', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260410002^^^THR^VN'
        pv1.servicing_facility = CWE(cwe_1='01', cwe_2='Discharged to home', cwe_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20260410060000')
        pv1.admit_date_time = '20260412152500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Encounter for full-term uncomplicated delivery', cwe_3='I10')
        dg1.diagnosis_date_time = '20260411'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z37.0', cwe_2='Single live birth', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260411'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='59400', cne_2='Routine obstetric care', cne_3='CPT4')
        pr1.pr1_4 = '^Vaginal delivery'
        pr1.procedure_date_time = '20260411082000'
        pr1.anesthesia_minutes = '3751842960^Garrison^Michelle^A^^^MD^^^^NPI'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]
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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260413101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN20260413101500003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30003', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Hutton^Denise^Lorraine^^Ms.^'
        pid.date_time_of_birth = '19680502'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2818 8th Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76110', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5537694'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '527-63-8410'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0002', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5291740836^Whitmore^Jerome^D^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260413003', cx_4='JPSHN', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30001', ei_2='CERN')
        orc.filler_order_number = EI(ei_1='FIL30001', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260413080000')
        orc.orc_11 = '5291740836^Whitmore^Jerome^D^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD30001', ei_2='CERN')
        obr.filler_order_number = EI(ei_1='FIL30001', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='80048', cwe_2='Basic metabolic panel', cwe_3='CPT4')
        obr.observation_date_time = '20260413080000'
        obr.obr_16 = '5291740836^Whitmore^Jerome^D^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260413100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '142'
        obx.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx.reference_range = '74-106'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea nitrogen [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '18'
        obx_2.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_2.reference_range = '6-20'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '0.9'
        obx_3.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_3.reference_range = '0.7-1.3'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '139'
        obx_4.units = CWE(cwe_1='mmol/L', cwe_2='millimoles per liter', cwe_3='UCUM')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='mmol/L', cwe_2='millimoles per liter', cwe_3='UCUM')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_6.obx_5 = '101'
        obx_6.units = CWE(cwe_1='mmol/L', cwe_2='millimoles per liter', cwe_3='UCUM')
        obx_6.reference_range = '98-106'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='mmol/L', cwe_2='millimoles per liter', cwe_3='UCUM')
        obx_7.reference_range = '21-31'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260413100000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_8.obx_5 = '9.4'
        obx_8.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_8.reference_range = '8.5-10.5'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260413100000'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='CARD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260414090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN20260414090000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30004', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Calhoun^Timothy^Scott^^Mr.^'
        pid.date_time_of_birth = '19580901'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7503 Hulen St', xad_3='Plano', xad_4='TX', xad_5='75024', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^972^5533946'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '412-67-8934'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='0006', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6190482537^Pembrook^Angela^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260414004', cx_4='THR', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30004', ei_2='CERN')
        orc.placer_order_group_number = EI(ei_1='GRP30004', ei_2='CERN')
        orc.date_time_of_order_event = '20260414085000'
        orc.orc_12 = '6190482537^Pembrook^Angela^R^^^MD^^^^NPI'
        orc.orc_17 = 'THR^Texas Health Resources'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD30004', ei_2='CERN')
        obr.universal_service_identifier = CWE(cwe_1='93306', cwe_2='Echocardiography transthoracic', cwe_3='CPT4')
        obr.observation_date_time = '20260414085000'
        obr.obr_15 = '6190482537^Pembrook^Angela^R^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Heart failure unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260414'
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
        nte.comment = 'Evaluate LV function. Patient reports worsening dyspnea on exertion.'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260415140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN20260415140000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30005', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Olivares^Lucia^Marisol^^Mrs.^'
        pid.date_time_of_birth = '19800106'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5040 Trail Lake Dr', xad_3='Fort Worth', xad_4='TX', xad_5='76133', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5532178'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '739-24-5618'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='4302', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='GS', xcn_2='General Surgery', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260414005', cx_4='JPSHN', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30005', ei_2='CERN')
        orc.filler_order_number = EI(ei_1='FIL30005', ei_2='SURG')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260414100000')
        orc.orc_11 = '7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD30005', ei_2='CERN')
        obr.filler_order_number = EI(ei_1='FIL30005', ei_2='SURG')
        obr.universal_service_identifier = CWE(cwe_1='28272-4', cwe_2='Operative note', cwe_3='LN')
        obr.observation_date_time = '20260414100000'
        obr.obr_16 = '7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260415135000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Operative Note', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMjMKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihPcGVyYXRpdmUgTm90ZSkg'
            'VGoKMCAtMjAgVGQKL0YxIDExIFRmCihQcm9jZWR1cmU6IExhcGFyb3Njb3BpYyBDaG9sZWN5c3RlY3RvbXkpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260415135000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='28272-4', cwe_2='Operative note narrative', cwe_3='LN')
        obx_2.obx_5 = (
            'OPERATIVE NOTE\\.br\\Procedure: Laparoscopic cholecystectomy\\.br\\Surgeon: Victor Charles Hargrove, MD\\.br\\Anesthesia: General endotracheal\\'
            '.br\\Findings: Chronically inflamed gallbladder with multiple stones\\.br\\Estimated Blood Loss: 25 mL\\.br\\Complications: None\\.br\\Specimens'
            ': Gallbladder sent to pathology'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260415135000'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260416110000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CERN20260416110000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT30006', ei_2='CERN')
        sch.appointment_reason = CWE(cwe_1='CARDFU', cwe_2='Cardiology Follow-up', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='20', cwe_2='MIN')
        sch.sch_9 = 'MIN^Minutes^ISO+'
        sch.appointment_duration_units = CNE(cne_4='20260423093000', cne_6='20', cne_7='MIN')
        sch.placer_contact_location = PL(pl_1='6190482537', pl_2='Pembrook', pl_3='Angela', pl_4='R', pl_7='MD', pl_11='NPI')
        sch.sch_16 = '^PRN^PH^^1^817^5537100'
        sch.sch_21 = '6190482537^Pembrook^Angela^R^^^MD^^^^NPI'
        sch.placer_order_number = EI(ei_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30006', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Eldridge^Dorothy^Christine^^Mrs.^'
        pid.date_time_of_birth = '19510418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3200 W Lancaster Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76107', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5534321'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '823-46-9015'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='0006', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6190482537^Pembrook^Angela^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260416006', cx_4='THR', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='CARD_CLINIC')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='99214', cwe_2='Office visit established level 4', cwe_3='CPT4')
        ais.start_date_time = '20260423093000'
        ais.duration = '20^MIN'
        ais.duration_units = CNE(cne_1='MIN', cne_2='Minutes', cne_3='ISO+')
        ais.filler_status_code = CWE(cwe_1='Confirmed')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='6190482537', cwe_2='Pembrook', cwe_3='Angela', cwe_4='R', cwe_7='MD', cwe_11='NPI')
        aig.start_date_time = '20260423093000'
        aig.duration = '20^MIN'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CARD', pl_2='0006', pl_3='01', pl_4='THR')
        ail.start_date_time_offset_units = CNE(cne_1='20260423093000')
        ail.allow_substitution_code = CWE(cwe_1='20', cwe_2='MIN')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260417140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CERN20260417140000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260417135500'
        evn.evn_5 = 'REGIST^Ashford^Tracy^A^^^ADM'
        evn.event_occurred = '20260417135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30007', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Menchaca^Ricardo^Fernando^^Mr.^'
        pid.date_time_of_birth = '19850919'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='6812 Meadowbrook Dr', xad_3='Fort Worth', xad_4='TX', xad_5='76112', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5538923'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '461-82-7039'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0010', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260417007', cx_4='JPSHN', cx_5='VN')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UHC001')
        in1.insurance_company_id = CX(cx_1='87726', cx_2='UnitedHealthcare')
        in1.in1_4 = 'UHC^^Dallas^TX^75201'
        in1.group_name = XON(xon_1='UHCGRP')
        in1.plan_type = CWE(cwe_1='Menchaca', cwe_2='Ricardo', cwe_3='Fernando')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19850919')
        in1.insureds_date_of_birth = '6812 Meadowbrook Dr^^Fort Worth^TX^76112^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='UHCPOL456789')

        # .. build IN2 ..
        in2 = IN2()
        in2.military_handicapped_program = CWE(cwe_1='Menchaca', cwe_2='Ricardo', cwe_3='Fernando')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PHARM_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260418160000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CERN20260418160000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30008', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Kendricks^Jerome^Darnell^^Mr.^'
        pid.date_time_of_birth = '19480721'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5501 E Lancaster Ave', xad_3='Arlington', xad_4='TX', xad_5='76014', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5536234'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '293-57-8146'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='3105', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '9183462057^Lattimore^Denise^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260417008', cx_4='THR', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30008', ei_2='CERN')
        orc.placer_order_group_number = EI(ei_1='GRP30008', ei_2='CERN')
        orc.date_time_of_order_event = '20260418153000'
        orc.orc_12 = '9183462057^Lattimore^Denise^K^^^MD^^^^NPI'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^Q8H^HL70335'
        rxe.give_code = CWE(cwe_1='3640', cwe_2='Piperacillin-tazobactam 3.375g IV', cwe_3='NDC')
        rxe.give_amount_minimum = '3.375'
        rxe.give_amount_maximum = '3.375'
        rxe.give_units = CWE(cwe_1='g', cwe_2='grams', cwe_3='ISO+')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxe.number_of_refills = '0'
        rxe.prescription_number = '9183462057^Lattimore^Denise^K^^^MD^^^^NPI'
        rxe.supplementary_code = CWE(cwe_1='30', cwe_2='MIN')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenous', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LA', cwe_2='Left Arm', cwe_3='HL70163')

        # .. build RXC ..
        rxc = RXC()
        rxc.rx_component_type = 'B'
        rxc.component_code = CWE(cwe_1='0.9% Sodium Chloride')
        rxc.component_amount = '100'
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
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.1', cwe_2='Lobar pneumonia unspecified organism', cwe_3='I10')
        dg1.diagnosis_date_time = '20260417'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [dg1]

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260419100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CERN20260419100000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260419095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30009', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Venkatesh^Rohit^Anand^^Mr.^'
        pid.date_time_of_birth = '19750213'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3720 E Rosedale St', xad_3='Fort Worth', xad_4='TX', xad_5='76105', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5533019'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '715-38-2964'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='0005', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '0247183956^Caldwell^James^H^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260419009', cx_4='JPSHN', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RI', cwe_2='Radiology Interpretation', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260419095000')
        txa.transcriptionist_code_name = XCN(xcn_1='DOC30009', xcn_2='JPSHN')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='36643-5', cwe_2='Chest X-ray interpretation', cwe_3='LN')
        obx.obx_5 = (
            'CHEST X-RAY PA AND LATERAL\\.br\\\\.br\\CLINICAL INDICATION: Cough and fever\\.br\\\\.br\\FINDINGS:\\.br\\Heart size normal. No cardiomegaly. Lu'
            'ngs are clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax. Mediastinal contour is normal. Bony structures are int'
            'act.\\.br\\\\.br\\IMPRESSION:\\.br\\No acute cardiopulmonary abnormality.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260419095000'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='FIN_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260420140000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CERN20260420140000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260420135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30010', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Farnsworth^Alice^Louise^^Mrs.^'
        pid.date_time_of_birth = '19630711'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='8900 Camp Bowie Blvd', xad_3='Denton', xad_4='TX', xad_5='76201', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5537012'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '184-53-6729'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='4201', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '1038274659^Stratton^Robert^W^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='GS', xcn_2='General Surgery', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260419010', cx_4='THR', cx_5='VN')
        pv1.current_patient_balance = '20260419070000'
        pv1.total_charges = '20260420130000'

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_date = DR(dr_1='20260419090000')
        ft1.transaction_posting_date = '20260419120000'
        ft1.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1.transaction_code = CWE(cwe_1='47562', cwe_2='Laparoscopic cholecystectomy', cwe_3='CPT4')
        ft1.ft1_9 = '1'
        ft1.assigned_patient_location = PL(pl_1='SURG', pl_2='4201', pl_3='01', pl_4='THR')
        ft1.ft1_21 = '1038274659^Stratton^Robert^W^^^MD^^^^NPI'

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_date = DR(dr_1='20260419090000')
        ft1_2.transaction_posting_date = '20260419120000'
        ft1_2.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_2.transaction_code = CWE(cwe_1='00790', cwe_2='Anesthesia intraperitoneal procedures upper abdomen', cwe_3='CPT4')
        ft1_2.ft1_9 = '1'
        ft1_2.assigned_patient_location = PL(pl_1='ANES', pl_2='0001', pl_3='01', pl_4='THR')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_date = DR(dr_1='20260419130000')
        ft1_3.transaction_posting_date = '20260419130000'
        ft1_3.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_3.transaction_code = CWE(cwe_1='88305', cwe_2='Surgical pathology', cwe_3='CPT4')
        ft1_3.ft1_9 = '1'
        ft1_3.assigned_patient_location = PL(pl_1='PATH', pl_2='0001', pl_3='01', pl_4='THR')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.10', cwe_2='Calculus of gallbladder with chronic cholecystitis without obstruction', cwe_3='I10')
        dg1.diagnosis_date_time = '20260419'
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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TX_DSHS')
        msh.date_time_of_message = '20260421103000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'CERN20260421103000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'ER'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30011', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Irvine^Brenda^Monique^^Ms.^'
        pid.date_time_of_birth = '19710305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2001 N Sylvania Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76111', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5534890'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '603-49-2187'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Irvine', xpn_2='Marcus', xpn_3='Terrell', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SON', cwe_2='Son', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2001 N Sylvania Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76111', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^682^5534891'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0010', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260421011', cx_4='JPSHN', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD30011', ei_2='CERN')
        orc.placer_order_group_number = EI(ei_1='GRP30011', ei_2='CERN')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260421100000')
        orc.orc_11 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20260421100000'
        rxa.administered_code = CWE(cwe_1='197', cwe_2='Influenza high-dose injectable', cwe_3='CVX')
        rxa.administered_amount = '0.7'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.rxa_15 = '49281-0703-55^^NDC'
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
        obx.obx_5 = 'V05^VFC eligible uninsured^HL70064'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TS'
        obx_2.observation_identifier = CWE(cwe_1='29768-9', cwe_2='Date vaccine information statement published', cwe_3='LN')
        obx_2.obx_5 = '20230810'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TS'
        obx_3.observation_identifier = CWE(cwe_1='29769-7', cwe_2='Date vaccine information statement presented', cwe_3='LN')
        obx_3.obx_5 = '20260421'
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
        msg.nk1 = nk1
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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260422070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CERN20260422070000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260422065500'
        evn.evn_5 = 'REG^Waverly^Carol^S^^^ADM'
        evn.event_occurred = '20260422065500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30012', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Palacios^Pedro^Enrique^^Mr.^'
        pid.date_time_of_birth = '19880624'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1900 Hemphill St', xad_3='Dallas', xad_4='TX', xad_5='75208', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5531789'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '847-20-6193'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='THR', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '2059381476^Kingsley^Sandra^L^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260422012', cx_4='THR', cx_5='VN')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Annual lab work, fasting')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z00.00', cwe_2='Encounter for general adult medical examination without abnormal findings', cwe_3='I10')
        dg1.diagnosis_date_time = '20260422'
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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260423160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN20260423160000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30013', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Agarwal^Priya^Sunita^^Ms.^'
        pid.date_time_of_birth = '19790820'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4200 South Fwy', xad_3='Fort Worth', xad_4='TX', xad_5='76115', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5539567'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '936-14-5782'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='3201', pl_3='02', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '3607294185^Winslow^David^S^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260421013', cx_4='JPSHN', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30013', ei_2='CERN')
        orc.filler_order_number = EI(ei_1='FIL30013', ei_2='MICRO')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260421100000')
        orc.orc_11 = '3607294185^Winslow^David^S^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD30013', ei_2='CERN')
        obr.filler_order_number = EI(ei_1='FIL30013', ei_2='MICRO')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Culture bacterial blood', cwe_3='CPT4')
        obr.observation_date_time = '20260421100000'
        obr.obr_16 = '3607294185^Winslow^David^S^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260423150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified in Blood by Culture', cwe_3='LN')
        obx.obx_5 = (
            'Organism: Escherichia coli\\.br\\Colony count: >100,000 CFU/mL\\.br\\\\.br\\Susceptibility Results:\\.br\\Ampicillin: Resistant (MIC >32)\\.br\\'
            'Ceftriaxone: Susceptible (MIC <=1)\\.br\\Ciprofloxacin: Susceptible (MIC <=0.25)\\.br\\Gentamicin: Susceptible (MIC <=1)\\.br\\Piperacillin-Tazo'
            'bactam: Susceptible (MIC <=4)\\.br\\Trimethoprim-Sulfamethoxazole: Susceptible (MIC <=1)'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260423150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Microbiology Report', cwe_3='AUSPDI')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNTUKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNaWNyb2Jpb2xvZ3kgQ3Vs'
            'dHVyZSBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooU3BlY2ltZW46IEJsb29kIEN1bHR1cmUpIFRqCjAgLTIwIFRkCihPcmdhbmlzbTogRS4gY29saSkgVGoKRVQKZW5kc3Ry'
            'ZWFtCmVuZG9iago='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260423150000'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260424090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'CERN20260424090000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260424085500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN30014', cx_4='THR', cx_5='MR'), CX(cx_1='502-71-8364', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Harada^Kenji^Takashi^^Mr.^'
        pid.date_time_of_birth = '19920310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2701 W Berry St', xad_3='McKinney', xad_4='TX', xad_5='75070', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5532345'
        pid.pid_14 = '^WPN^PH^^1^469^5538901'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '502-71-8364'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Texas Health Fort Worth^^^^NPI'
        pd1.pd1_4 = '2059381476^Kingsley^Sandra^L^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Harada', xpn_2='Yuki', xpn_3='Emiko', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2701 W Berry St', xad_3='McKinney', xad_4='TX', xad_5='75070', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^469^5532346'
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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260425020000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CERN20260425020000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260425015500'
        evn.evn_5 = 'ICURN^Prescott^Ashley^R^^^RN'
        evn.event_occurred = '20260425015500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30015', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Jarrett^Walter^Terrence^^Mr.^'
        pid.date_time_of_birth = '19530429'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1601 Pennsylvania Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76104', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5537821'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '278-64-9301'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='1002', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '4081523967^Montague^Denise^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CCM', xcn_2='Critical Care', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260424015^^^JPSHN^VN'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Respiratory decompensation requiring intubation')

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260425160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'CERN20260425160000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260425155500'
        evn.evn_5 = 'HIM^Northcutt^Maria^P^^^HIM'
        evn.event_occurred = '20260425155500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30016', cx_4='THR', cx_5='MR')
        pid.pid_5 = 'Dunham^Shannon^Elise^^Ms.^'
        pid.date_time_of_birth = '19870123'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4100 McCart Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76110', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5533456'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '581-92-4067'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN30016B', cx_4='THR', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='Dunham', xpn_2='Shannon', xpn_3='E')

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260426110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'CERN20260426110000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260426105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30017', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Bartlett^Charles^Raymond^^Mr.^'
        pid.date_time_of_birth = '19600211'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7200 Calmont Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76116', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5539012'
        pid.pid_14 = '^WPN^PH^^1^817^5533478'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '362-81-4057'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'JPS Health Network^^^^NPI'
        pd1.pd1_4 = '5174920638^Hensley^Susan^E^^^MD^^^^NPI'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='THR', hd_2='2.16.840.1.113883.3.2102', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MF_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260427090000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'CERN20260427090000018'
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
        mfe.mfn_control_id = '20260427085500'
        mfe.mfe_4 = '6295014738^Villarreal^Maria^Elena^^MD'
        mfe.primary_key_value_type = 'CWE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='6295014738')
        stf.staff_identifier_list = CX(cx_1='U6295014738')
        stf.staff_name = XPN(xpn_1='Villarreal', xpn_2='Maria', xpn_3='Elena', xpn_5='MD')
        stf.administrative_sex = CWE(cwe_1='F')
        stf.date_time_of_birth = '19800515'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.stf_12 = '^WPN^PH^^1^817^5531234'

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='6295014738', cwe_2='Villarreal', cwe_3='Maria', cwe_4='Elena', cwe_6='MD')
        pra.practitioner_group = CWE(cwe_1='THR', cwe_2='Texas Health Resources')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='Institution', cwe_3='HL70186')
        pra.date_entered_practice = '207Q00000X^Family Medicine^NUCC'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260428080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN20260428080000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30019', cx_4='JPSHN', cx_5='MR')
        pid.pid_5 = 'Quintanilla^Isabella^Carmen^^Mrs.^'
        pid.date_time_of_birth = '19780102'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3100 Purington Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76103', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^682^5535678'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '428-60-3917'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0010', pl_3='01', pl_4='JPSHN', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260428019', cx_4='JPSHN', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD30019', ei_2='CERN')
        orc.placer_order_group_number = EI(ei_1='GRP30019', ei_2='CERN')
        orc.date_time_of_order_event = '20260428075000'
        orc.orc_12 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD30019', ei_2='CERN')
        obr.universal_service_identifier = CWE(cwe_1='81001', cwe_2='Urinalysis automated with microscopy', cwe_3='CPT4')
        obr.observation_date_time = '20260428075000'
        obr.obr_15 = '8362015749^Thornton^Patricia^M^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N39.0', cwe_2='Urinary tract infection site not specified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260428'
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
        nte.comment = 'Patient reports dysuria and frequency for 2 days. No fever.'

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
    """ Based on live/us-texas/us-texas-oracle-health.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_RECV')
        msh.sending_facility = HD(hd_1='TX_HIE')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='JPSHN', hd_2='2.16.840.1.113883.3.1901', hd_3='ISO')
        msh.date_time_of_message = '20260429080000'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'CERN20260429080000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AE'
        msa.message_control_id = 'CERN20260413101500003'
        msa.msa_3 = 'Unknown patient identifier in PID-3'
        msa.expected_sequence_number = '207'

        # .. build ERR ..
        err = ERR()
        err.error_location = ERL(erl_1='PID', erl_2='1', erl_3='3')
        err.hl7_error_code = CWE(cwe_1='204', cwe_2='Unknown key identifier', cwe_3='HL70357')
        err.severity = 'E'
        err.inform_person_indicator = CWE(cwe_1='Patient MRN not found in receiving system')

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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

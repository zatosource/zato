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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, DftP03Visit, \
    MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIG, AIL, AIS, DG1, EVN, FT1, IN1, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PRA, PV1, PV2, RGS, RXA, \
    RXC, RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-rhapsody.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260401080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'RHAP20260401080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401075500'
        evn.evn_5 = 'OBRN^Endicott^Lorraine^T^^^RN'
        evn.event_occurred = '20260401075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN50001', cx_4='SETON', cx_5='MR'), CX(cx_1='841-73-2905', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Villegas^Catalina^Renata^^Mrs.^'
        pid.date_time_of_birth = '19940211'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2917 Guadalupe St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5559123'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '841-73-2905'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Ascension Seton Medical Center^^^^NPI'
        pd1.pd1_4 = '1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Villegas', xpn_2='Marco', xpn_3='Antonio', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2917 Guadalupe St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^512^5559124'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OB', pl_2='2201', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI'
        pv1.pv1_8 = '2345600202^Faulkner^Ingrid^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='OBG', xcn_2='Obstetrics', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260401001^^^SETON^VN'
        pv1.discharge_date_time = '20260401075500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Active labor, 39 weeks gestational age')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Encounter for full-term uncomplicated delivery', cwe_3='I10')
        dg1.diagnosis_date_time = '20260401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AETNA001')
        in1.insurance_company_id = CX(cx_1='80314', cx_2='Aetna')
        in1.in1_4 = 'Aetna^^Dallas^TX^75201'
        in1.group_name = XON(xon_1='AETGRP')
        in1.plan_type = CWE(cwe_1='Villegas', cwe_2='Catalina', cwe_3='Renata')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19940211')
        in1.insureds_date_of_birth = '2917 Guadalupe St^^Austin^TX^78705^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='AETPOL567890')

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
        msg.dg1 = dg1
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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260403141500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'RHAP20260403141500002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260403140000'
        evn.evn_5 = 'BHRN^Goodrich^Tamara^K^^^RN'
        evn.event_occurred = '20260403140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50002', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Pemberton^Cedric^Lamont^^Mr.^'
        pid.date_time_of_birth = '19850610'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4710 Bellaire Blvd', xad_3='Houston', xad_4='TX', xad_5='77401', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5553847'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '372-48-6193'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='BH', pl_2='1205', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '3456700303^Halstead^Norman^D^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PSY', xcn_2='Psychiatry', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260324002^^^UTHEALTH^VN'
        pv1.servicing_facility = CWE(cwe_1='01', cwe_2='Discharged to home', cwe_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20260324100000')
        pv1.admit_date_time = '20260403140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='F10.20', cwe_2='Alcohol dependence uncomplicated', cwe_3='I10')
        dg1.diagnosis_date_time = '20260324'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='F32.1', cwe_2='Major depressive disorder single episode moderate', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260324'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260404100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RHAP20260404100000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50003', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Harrington^Diane^Lucille^^Ms.^'
        pid.date_time_of_birth = '19700815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3200 Red River St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5554567'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '517-62-8034'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '4567800404^Kimball^Patricia^B^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260404003', cx_4='SETON', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50003', ei_2='RHAP')
        orc.filler_order_number = EI(ei_1='FIL50003', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260404070000')
        orc.orc_11 = '4567800404^Kimball^Patricia^B^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50003', ei_2='RHAP')
        obr.filler_order_number = EI(ei_1='FIL50003', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='57698-3', cwe_2='Lipid panel', cwe_3='LN')
        obr.observation_date_time = '20260404070000'
        obr.obr_16 = '4567800404^Kimball^Patricia^B^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260404093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '238'
        obx.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260404093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '165'
        obx_2.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260404093000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '52'
        obx_3.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_3.reference_range = '>40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260404093000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL cholesterol calc [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '153'
        obx_4.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_4.reference_range = '<100'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260404093000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='VLDL cholesterol calc [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '33'
        obx_5.units = CWE(cwe_1='mg/dL', cwe_2='milligrams per deciliter', cwe_3='UCUM')
        obx_5.reference_range = '5-40'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260404093000'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ENDO_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'RHAP20260405100000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50004', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Zarate^Emilio^Ricardo^^Mr.^'
        pid.date_time_of_birth = '19720328'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='8502 Katy Fwy', xad_3='Houston', xad_4='TX', xad_5='77024', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5558901'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '609-71-4823'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GI', pl_2='0002', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5678900505^Lockwood^Sandra^E^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='GI', xcn_2='Gastroenterology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260405004', cx_4='UTHEALTH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50004', ei_2='RHAP')
        orc.placer_order_group_number = EI(ei_1='GRP50004', ei_2='RHAP')
        orc.date_time_of_order_event = '20260405093000'
        orc.orc_12 = '5678900505^Lockwood^Sandra^E^^^MD^^^^NPI'
        orc.orc_17 = 'UTHEALTH^UT Health Houston'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50004', ei_2='RHAP')
        obr.universal_service_identifier = CWE(cwe_1='45378', cwe_2='Colonoscopy diagnostic', cwe_3='CPT4')
        obr.observation_date_time = '20260405093000'
        obr.obr_15 = '5678900505^Lockwood^Sandra^E^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.11', cwe_2='Encounter for screening for malignant neoplasm of colon', cwe_3='I10')
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
        nte.comment = 'Age 53, average risk. Family history of colon cancer in father at age 68. Patient completed bowel prep.'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PFT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260406150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RHAP20260406150000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50005', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Montague^Russell^Vernon^^Mr.^'
        pid.date_time_of_birth = '19550212'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1100 W 34th St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5553201'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '734-85-1267'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PUL', pl_2='0003', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6789000606^Prescott^Steven^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PUL', xcn_2='Pulmonology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260406005', cx_4='SETON', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50005', ei_2='RHAP')
        orc.filler_order_number = EI(ei_1='FIL50005', ei_2='PFT')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260406130000')
        orc.orc_11 = '6789000606^Prescott^Steven^R^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50005', ei_2='RHAP')
        obr.filler_order_number = EI(ei_1='FIL50005', ei_2='PFT')
        obr.universal_service_identifier = CWE(cwe_1='94010', cwe_2='Spirometry including graphic record', cwe_3='CPT4')
        obr.observation_date_time = '20260406130000'
        obr.obr_16 = '6789000606^Prescott^Steven^R^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260406145000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='19868-9', cwe_2='FEV1 measured', cwe_3='LN')
        obx.obx_5 = '2.1'
        obx.units = CWE(cwe_1='L', cwe_2='liters', cwe_3='UCUM')
        obx.reference_range = '>2.5'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260406145000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='19876-2', cwe_2='FVC measured', cwe_3='LN')
        obx_2.obx_5 = '3.8'
        obx_2.units = CWE(cwe_1='L', cwe_2='liters', cwe_3='UCUM')
        obx_2.reference_range = '>3.5'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260406145000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='19926-5', cwe_2='FEV1/FVC', cwe_3='LN')
        obx_3.obx_5 = '55.3'
        obx_3.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx_3.reference_range = '>70'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260406145000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='94010', cwe_2='Spirometry interpretation', cwe_3='L')
        obx_4.obx_5 = (
            'INTERPRETATION:\\.br\\Obstructive pattern with reduced FEV1/FVC ratio.\\.br\\FEV1 at 65% of predicted.\\.br\\Consistent with moderate COPD.\\.br'
            '\\Recommend post-bronchodilator testing.'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260406145000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Spirometry Report', cwe_3='AUSPDI')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMzUKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihTcGlyb21ldHJ5IFJlcG9y'
            'dCkgVGoKMCAtMjAgVGQKL0YxIDEwIFRmCihBc2NlbnNpb24gU2V0b24gTWVkaWNhbCBDZW50ZXIpIFRqCjAgLTIwIFRkCihQYXRpZW50OiBNb250YWd1ZSwgUnVzc2VsbCkgVGoKRVQK'
            'ZW5kc3RyZWFtCmVuZG9iago='
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260406145000'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260407110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'RHAP20260407110000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260407105500'
        evn.evn_5 = 'MEDRN^Thornton^Jeanette^L^^^RN'
        evn.event_occurred = '20260407105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50006', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Stafford^Terrence^Darnell^^Mr.^'
        pid.date_time_of_birth = '19780821'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3400 Elgin St', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^832^5553890'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '483-96-7210'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='4102', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '7890100707^Merriweather^Pamela^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260405006', cx_4='UTHEALTH', cx_5='VN')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K85.9', cwe_2='Acute pancreatitis unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260405'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='F10.20', cwe_2='Alcohol dependence uncomplicated', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260405'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_3 = DG1()
        dg1_3.set_id_dg1 = '3'
        dg1_3.diagnosis_code_dg1 = CWE(cwe_1='E87.1', cwe_2='Hypo-osmolality and hyponatremia', cwe_3='I10')
        dg1_3.diagnosis_date_time = '20260407'
        dg1_3.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2, dg1_3]

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260408090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'RHAP20260408090000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT50007', ei_2='RHAP')
        sch.appointment_reason = CWE(cwe_1='DERM', cwe_2='Dermatology Consultation', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='MIN')
        sch.sch_9 = 'MIN^Minutes^ISO+'
        sch.appointment_duration_units = CNE(cne_4='20260415140000', cne_6='30', cne_7='MIN')
        sch.placer_contact_location = PL(pl_1='8901200808', pl_2='Whitfield', pl_3='Rebecca', pl_4='J', pl_7='MD', pl_11='NPI')
        sch.sch_16 = '^PRN^PH^^1^512^5556789'
        sch.sch_21 = '8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI'
        sch.placer_order_number = EI(ei_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50007', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Yoshida^Akiko^Mei^^Ms.^'
        pid.date_time_of_birth = '19850503'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='900 E 30th St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5554321'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '256-93-4018'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='0001', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='DER', xcn_2='Dermatology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408007', cx_4='SETON', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='DERM_CLINIC')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='99203', cwe_2='Office visit new patient level 3', cwe_3='CPT4')
        ais.start_date_time = '20260415140000'
        ais.duration = '30^MIN'
        ais.duration_units = CNE(cne_1='MIN', cne_2='Minutes', cne_3='ISO+')
        ais.filler_status_code = CWE(cwe_1='Confirmed')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='8901200808', cwe_2='Whitfield', cwe_3='Rebecca', cwe_4='J', cwe_7='MD', cwe_11='NPI')
        aig.start_date_time = '20260415140000'
        aig.duration = '30^MIN'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='DERM', pl_2='0001', pl_3='01', pl_4='SETON')
        ail.start_date_time_offset_units = CNE(cne_1='20260415140000')
        ail.allow_substitution_code = CWE(cwe_1='30', cwe_2='MIN')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'New patient. Multiple suspicious moles on back and arms. Family history of melanoma.'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PHARM_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260409020000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'RHAP20260409020000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50008', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Redmond^Shanice^Elaine^^Ms.^'
        pid.date_time_of_birth = '19910714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='8100 Cambridge St', xad_3='Houston', xad_4='TX', xad_5='77054', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5557012'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '615-28-9347'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='1003', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '9012300909^Ashworth^Marcus^T^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CCM', xcn_2='Critical Care', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408008', cx_4='UTHEALTH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50008', ei_2='RHAP')
        orc.placer_order_group_number = EI(ei_1='GRP50008', ei_2='RHAP')
        orc.date_time_of_order_event = '20260409013000'
        orc.orc_12 = '9012300909^Ashworth^Marcus^T^^^MD^^^^NPI'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^CONTINUOUS^HL70335'
        rxe.give_code = CWE(cwe_1='6980', cwe_2='Insulin regular human 100 units/mL', cwe_3='NDC')
        rxe.give_amount_minimum = '100'
        rxe.give_amount_maximum = '100'
        rxe.give_units = CWE(cwe_1='units/mL', cwe_2='units per milliliter', cwe_3='ISO+')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxe.number_of_refills = '0'
        rxe.prescription_number = '9012300909^Ashworth^Marcus^T^^^MD^^^^NPI'
        rxe.supplementary_code = CWE(cwe_1='0', cwe_2='MIN')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenous', cwe_3='HL70162')

        # .. build RXC ..
        rxc = RXC()
        rxc.rx_component_type = 'B'
        rxc.component_code = CWE(cwe_1='0.9% Sodium Chloride')
        rxc.component_amount = '250'
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
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E10.10', cwe_2='Type 1 diabetes mellitus with ketoacidosis without coma', cwe_3='I10')
        dg1.diagnosis_date_time = '20260408'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'DKA protocol. Start at 0.1 units/kg/hr. Target glucose 150-200 mg/dL. Check BMP and glucose hourly.'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260410160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'RHAP20260410160000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260410155500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50009', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Lockhart^Winston^Barrett^^Mr.^'
        pid.date_time_of_birth = '19500808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2001 S Lamar Blvd', xad_3='Austin', xad_4='TX', xad_5='78704', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5558901'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '927-14-5682'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='3108', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '0123401010^Bancroft^Gregory^D^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408009', cx_4='SETON', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Consultation Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260410155000')
        txa.transcriptionist_code_name = XCN(xcn_1='DOC50009', xcn_2='SETON')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11488-4', cwe_2='Consult note', cwe_3='LN')
        obx.obx_5 = (
            'NEPHROLOGY CONSULTATION\\.br\\Patient: Lockhart, Winston Barrett\\.br\\DOB: 08/08/1950\\.br\\\\.br\\REASON FOR CONSULTATION: Acute kidney injury'
            ' with creatinine 4.2 mg/dL from baseline 1.1\\.br\\\\.br\\ASSESSMENT:\\.br\\1. Acute kidney injury, likely prerenal etiology in setting of sepsi'
            's\\.br\\2. CKD stage 2 at baseline\\.br\\3. Hyperkalemia 5.8 mEq/L\\.br\\\\.br\\RECOMMENDATIONS:\\.br\\1. Aggressive IV fluid resuscitation with'
            ' LR at 200 mL/hr\\.br\\2. Hold ACE inhibitor and NSAIDs\\.br\\3. Kayexalate 30g for hyperkalemia\\.br\\4. Monitor urine output closely\\.br\\5. '
            'Recheck BMP in 6 hours'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260410155000'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='FIN_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260411170000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'RHAP20260411170000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260411165500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50010', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Cardenas^Dolores^Yolanda^^Mrs.^'
        pid.date_time_of_birth = '19810322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5200 Almeda Rd', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5554567'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '248-36-7159'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ASC', pl_2='0001', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '1234501111^Ellsworth^David^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Orthopedics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260411010', cx_4='UTHEALTH', cx_5='VN')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_date = DR(dr_1='20260411080000')
        ft1.transaction_posting_date = '20260411110000'
        ft1.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1.transaction_code = CWE(cwe_1='29881', cwe_2='Arthroscopy knee surgical with meniscectomy', cwe_3='CPT4')
        ft1.ft1_9 = '1'
        ft1.assigned_patient_location = PL(pl_1='ASC', pl_2='0001', pl_3='01', pl_4='UTHEALTH')
        ft1.ft1_21 = '1234501111^Ellsworth^David^C^^^MD^^^^NPI'

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_date = DR(dr_1='20260411080000')
        ft1_2.transaction_posting_date = '20260411110000'
        ft1_2.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_2.transaction_code = CWE(cwe_1='01382', cwe_2='Anesthesia knee arthroscopy', cwe_3='CPT4')
        ft1_2.ft1_9 = '1'
        ft1_2.assigned_patient_location = PL(pl_1='ANES', pl_2='0001', pl_3='01', pl_4='UTHEALTH')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M23.211', cwe_2='Derangement of anterior horn of medial meniscus due to old tear right knee', cwe_3='I10')
        dg1.diagnosis_date_time = '20260411'
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
        msg.financial = [financial, financial_2]
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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TX_DSHS')
        msh.date_time_of_message = '20260412100000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'RHAP20260412100000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'ER'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50011', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Venkataraman^Arun^Suresh^^Mr.^'
        pid.date_time_of_birth = '19950630'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='6100 Airport Blvd', xad_3='Austin', xad_4='TX', xad_5='78752', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5553456'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '368-52-7941'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '2345601212^Osgood^Linda^M^^^MD^^^^NPI'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0003', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '2345601212^Osgood^Linda^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260412011', cx_4='SETON', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD50011', ei_2='RHAP')
        orc.placer_order_group_number = EI(ei_1='GRP50011', ei_2='RHAP')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260412093000')
        orc.orc_11 = '2345601212^Osgood^Linda^M^^^MD^^^^NPI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20260412093000'
        rxa.administered_code = CWE(cwe_1='45', cwe_2='Hepatitis B unspecified formulation', cwe_3='CVX')
        rxa.administered_amount = '1.0'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.rxa_15 = '58160-0820-11^^NDC'
        rxa.completion_status = 'CP^Complete^HL70322'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RD', cwe_2='Right Deltoid', cwe_3='HL70163')

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
        obx_2.obx_5 = '20231020'
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

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Dose 2 of 3. First dose given 2026-02-12. Third dose due 2026-08-12.'

        # .. build the OBSERVATION group ..
        observation_3 = VxuV04Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260413060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'RHAP20260413060000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260413055500'
        evn.evn_5 = 'EDRN^Rutledge^Amanda^G^^^RN'
        evn.event_occurred = '20260413055500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50012', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Kensington^Brenda^Elise^^Ms.^'
        pid.date_time_of_birth = '19790901'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3100 Cleburne St', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^832^5557890'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '591-43-8726'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OBS', pl_2='0002', pl_3='01', pl_4='UTHEALTH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '3456701313^Hadley^William^P^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260413012', cx_4='UTHEALTH', cx_5='VN')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain, low risk, observation protocol')
        pv2.visit_protection_indicator = '3^Urgent^HL70217'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain unspecified', cwe_3='I10')
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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='CARD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260414140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RHAP20260414140000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50013', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Fierro^Santiago^Andres^^Mr.^'
        pid.date_time_of_birth = '19620414'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2200 S Congress Ave', xad_3='Austin', xad_4='TX', xad_5='78704', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5552345'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '762-53-8194'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='4101', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '4567801414^Caldwell^Kevin^J^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260413013', cx_4='SETON', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50013', ei_2='RHAP')
        orc.filler_order_number = EI(ei_1='FIL50013', ei_2='CATH')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260413140000')
        orc.orc_11 = '4567801414^Caldwell^Kevin^J^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50013', ei_2='RHAP')
        obr.filler_order_number = EI(ei_1='FIL50013', ei_2='CATH')
        obr.universal_service_identifier = CWE(cwe_1='93458', cwe_2='Cardiac catheterization with left ventriculography', cwe_3='CPT4')
        obr.observation_date_time = '20260413140000'
        obr.obr_16 = '4567801414^Caldwell^Kevin^J^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260414133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93458', cwe_2='Cardiac catheterization findings', cwe_3='L')
        obx.obx_5 = (
            'CARDIAC CATHETERIZATION REPORT\\.br\\\\.br\\HEMODYNAMICS:\\.br\\LV end-diastolic pressure: 18 mmHg\\.br\\Cardiac output: 4.8 L/min\\.br\\Cardiac'
            ' index: 2.6 L/min/m2\\.br\\\\.br\\CORONARY ANGIOGRAPHY:\\.br\\Left main: Normal\\.br\\LAD: 70% mid-segment stenosis\\.br\\LCx: 40% proximal sten'
            'osis\\.br\\RCA: Dominant, 90% proximal stenosis\\.br\\\\.br\\LV FUNCTION: EF 45%, inferior hypokinesis\\.br\\\\.br\\IMPRESSION: Two-vessel coron'
            'ary artery disease. Recommend PCI to RCA.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260414133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Cardiac Catheterization Report', cwe_3='AUSPDI')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0Nv'
            'dW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8'
            'PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNjAKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihDYXJkaWFjIENh'
            'dGhldGVyaXphdGlvbiBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooQXNjZW5zaW9uIFNldG9uIE1lZGljYWwgQ2VudGVyKSBUagowIC0yMCBUZAooUGF0aWVudDogRmllcnJv'
            'LCBTYW50aWFnbykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260414133000'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260415100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'RHAP20260415100000014'
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
        pid.patient_identifier_list = CX(cx_1='MRN50014', cx_4='UTHEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Galindo', xpn_2='Baby Girl', xpn_7='')
        pid.date_time_of_birth = '20260415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7900 Cambridge St', xad_3='Houston', xad_4='TX', xad_5='77054', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5559012'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Galindo', xpn_2='Veronica', xpn_3='Isabel', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='7900 Cambridge St', xad_3='Houston', xad_4='TX', xad_5='77054', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^713^5559012'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Galindo', xpn_2='Rafael', xpn_3='Eduardo', xpn_5='Mr.')
        nk1_2.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1_2.address = XAD(xad_1='7900 Cambridge St', xad_3='Houston', xad_4='TX', xad_5='77054', xad_6='US')
        nk1_2.nk1_5 = '^PRN^PH^^1^713^5559013'
        nk1_2.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA05NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260416080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'RHAP20260416080000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260416075500'
        evn.evn_5 = 'PPRN^Winslow^Jessica^A^^^RN'
        evn.event_occurred = '20260416075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50015', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Villegas^Catalina^Renata^^Mrs.^'
        pid.date_time_of_birth = '19940211'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2917 Guadalupe St', xad_3='Austin', xad_4='TX', xad_5='78705', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5559123'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '841-73-2905'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PP', pl_2='2301', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='OBG', xcn_2='Obstetrics', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260401001^^^SETON^VN'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Postpartum care, uncomplicated vaginal delivery')

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260417100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'RHAP20260417100000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260417095500'
        evn.evn_5 = 'HIM^Sutherland^Janet^M^^^HIM'
        evn.event_occurred = '20260417095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50016', cx_4='UTHEALTH', cx_5='MR')
        pid.pid_5 = 'Galindo^Claudia^Sofia^^Mrs.^'
        pid.date_time_of_birth = '19830512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='6200 Hermann Park Dr', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5554321'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '453-67-2819'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN50016OLD', cx_4='UTHEALTH', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='Galindo', xpn_2='Claudia', xpn_3='S')

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260418110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'RHAP20260418110000017'
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
        pid.patient_identifier_list = CX(cx_1='MRN50017', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Norris^Clayton^Walter^^Mr.^'
        pid.date_time_of_birth = '19420305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4500 E 7th St', xad_3='Austin', xad_4='TX', xad_5='78702', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5557890'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '819-46-3057'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Ascension Seton Medical Center^^^^NPI'
        pd1.pd1_4 = '5678901515^Overstreet^Donna^L^^^MD^^^^NPI'
        pd1.protection_indicator = 'Y^Yes^HL70136'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Norris', xpn_2='Kathleen', xpn_3='Marie', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='DAU', cwe_2='Daughter', cwe_3='HL70063')
        nk1.address = XAD(xad_1='8200 Burnet Rd', xad_3='Austin', xad_4='TX', xad_5='78757', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^512^5553210'
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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='UTHEALTH', hd_2='2.16.840.1.113883.3.4402', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MF_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260419090000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'RHAP20260419090000018'
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
        mfe.mfe_4 = '6789011818^Bhandari^Nikhil^Rajan^^MD'
        mfe.primary_key_value_type = 'CWE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='6789011818')
        stf.staff_identifier_list = CX(cx_1='U6789011818')
        stf.staff_name = XPN(xpn_1='Bhandari', xpn_2='Nikhil', xpn_3='Rajan', xpn_5='MD')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19820918'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.stf_12 = '^WPN^PH^^1^713^5551234'

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='6789011818', cwe_2='Bhandari', cwe_3='Nikhil', cwe_4='Rajan', cwe_6='MD')
        pra.practitioner_group = CWE(cwe_1='UTHEALTH', cwe_2='UT Health Houston')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='Institution', cwe_3='HL70186')
        pra.date_entered_practice = '207RN0300X^Nephrology^NUCC'

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_RECV')
        msh.sending_facility = HD(hd_1='TX_HIE')
        msh.receiving_application = HD(hd_1='COREPOINT')
        msh.receiving_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.date_time_of_message = '20260420080000'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'RHAP20260420080000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'RHAP20260401080000001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/us-texas/us-texas-rhapsody.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COREPOINT')
        msh.sending_facility = HD(hd_1='SETON', hd_2='2.16.840.1.113883.3.4401', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260421100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'RHAP20260421100000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50020', cx_4='SETON', cx_5='MR')
        pid.pid_5 = 'Upshaw^Demetrius^Allen^^Mr.^'
        pid.date_time_of_birth = '19770216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3800 N Lamar Blvd', xad_3='Austin', xad_4='TX', xad_5='78756', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^512^5559876'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '694-81-5237'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MRI2', pl_3='01', pl_4='SETON', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '7890102020^Langford^Sandra^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Orthopedics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260421020', cx_4='SETON', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50020', ei_2='RHAP')
        orc.placer_order_group_number = EI(ei_1='GRP50020', ei_2='RHAP')
        orc.date_time_of_order_event = '20260421093000'
        orc.orc_12 = '7890102020^Langford^Sandra^K^^^MD^^^^NPI'
        orc.orc_17 = 'SETON^Ascension Seton Medical Center'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50020', ei_2='RHAP')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='MRI lumbar spine without contrast', cwe_3='CPT4')
        obr.observation_date_time = '20260421093000'
        obr.obr_15 = '7890102020^Langford^Sandra^K^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Low back pain', cwe_3='I10')
        dg1.diagnosis_date_time = '20260421'
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
        nte.comment = 'Chronic low back pain with left leg radiculopathy. MRI to evaluate for disc herniation or stenosis.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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

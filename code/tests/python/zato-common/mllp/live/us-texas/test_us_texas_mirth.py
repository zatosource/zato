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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03NextOfKin, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, \
    DftP03Visit, MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIG, AIL, AIS, DG1, EVN, FT1, GT1, IN1, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PRA, PV1, PV2, RGS, \
    RXA, RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-mirth.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-mirth.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260405102000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MIRTH20260405102000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260405101500'
        evn.evn_5 = 'EDRN^Ashmore^Danielle^P^^^RN'
        evn.event_occurred = '20260405101500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN40001', cx_4='PARKLAND', cx_5='MR'), CX(cx_1='831-47-6290', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Coronado^Rafael^Emilio^^Mr.^'
        pid.date_time_of_birth = '19670811'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1818 Medical District Dr', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5559876'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '831-47-6290'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Parkland Memorial Hospital^^^^NPI'
        pd1.pd1_4 = '1234567001^Sterling^Kathleen^M^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Coronado', xpn_2='Marisol', xpn_3='Adriana', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='1818 Medical District Dr', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5559877'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='5101', pl_3='01', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '2345678002^Winslow^David^L^^^MD^^^^NPI'
        pv1.pv1_8 = '3456789003^Hartwell^Jennifer^S^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neurology', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='A', cwe_2='Accident', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260405001^^^PARKLAND^VN'
        pv1.discharge_date_time = '20260405101500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute left-sided weakness, slurred speech, facial droop')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Cerebral infarction unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260405'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Coronado', xpn_2='Rafael', xpn_3='Emilio', xpn_5='Mr.')
        gt1.guarantor_address = XAD(xad_1='1818 Medical District Dr', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US')
        gt1.guarantor_ph_num_home = XTN(xtn_2='PRN', xtn_3='PH', xtn_5='1', xtn_6='214', xtn_7='5559876')
        gt1.guarantor_relationship = CWE(cwe_1='SE', cwe_2='Self', cwe_3='HL70063')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MCARE001')
        in1.insurance_company_id = CX(cx_1='00451', cx_2='Medicare')
        in1.in1_4 = 'Centers for Medicare^^Baltimore^MD^21244'
        in1.group_name = XON(xon_1='MCAREGRP')
        in1.plan_type = CWE(cwe_1='Coronado', cwe_2='Rafael', cwe_3='Emilio')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19670811')
        in1.insureds_date_of_birth = '1818 Medical District Dr^^Dallas^TX^75235^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='MCAREPOL345678')

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
        msg.gt1 = gt1
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260406143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MIRTH20260406143000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40002', cx_4='METHODIST_SA', cx_5='MR')
        pid.pid_5 = 'Abernathy^Donna^Christine^^Mrs.^'
        pid.date_time_of_birth = '19550630'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7700 Floyd Curl Dr', xad_3='San Antonio', xad_4='TX', xad_5='78229', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5553412'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '614-28-7753^^^USSSA^SS'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T4', pl_4='METHODIST_SA', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '4567890004^Culpepper^Carlos^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260406002', cx_4='METHODIST_SA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40002', ei_2='MIRTH')
        orc.filler_order_number = EI(ei_1='FIL40002', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260406120000')
        orc.orc_11 = '4567890004^Culpepper^Carlos^A^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40002', ei_2='MIRTH')
        obr.filler_order_number = EI(ei_1='FIL40002', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='49563-0', cwe_2='Cardiac biomarkers panel', cwe_3='LN')
        obr.observation_date_time = '20260406120000'
        obr.obr_16 = '4567890004^Culpepper^Carlos^A^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260406140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '0.04'
        obx.units = CWE(cwe_1='ng/mL', cwe_2='nanograms per milliliter', cwe_3='UCUM')
        obx.reference_range = '<0.01'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33762-6', cwe_2='Natriuretic peptide.B prohormone N-Terminal', cwe_3='LN')
        obx_2.obx_5 = '456'
        obx_2.units = CWE(cwe_1='pg/mL', cwe_2='picograms per milliliter', cwe_3='UCUM')
        obx_2.reference_range = '<125'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2157-6', cwe_2='Creatine kinase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '180'
        obx_3.units = CWE(cwe_1='U/L', cwe_2='units per liter', cwe_3='UCUM')
        obx_3.reference_range = '30-200'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13969-1', cwe_2='Creatine kinase.MB [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '5.2'
        obx_4.units = CWE(cwe_1='ng/mL', cwe_2='nanograms per milliliter', cwe_3='UCUM')
        obx_4.reference_range = '0.0-6.3'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='30313-1', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx_5.obx_5 = '11.8'
        obx_5.units = CWE(cwe_1='g/dL', cwe_2='grams per deciliter', cwe_3='UCUM')
        obx_5.reference_range = '12.0-16.0'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260406140000'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='COOKCH', hd_2='2.16.840.1.113883.3.3303', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260407161500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MIRTH20260407161500003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260407160000'
        evn.evn_5 = 'PEDRN^Kingsley^Brittany^L^^^RN'
        evn.event_occurred = '20260407160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40003', cx_4='COOKCH', cx_5='MR')
        pid.pid_5 = 'Granados^Sofia^Valentina^^Miss^'
        pid.date_time_of_birth = '20180302'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3500 W Illinois Ave', xad_3='Dallas', xad_4='TX', xad_5='75211', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5554893'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Granados', xpn_2='Hector', xpn_3='Antonio', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3500 W Illinois Ave', xad_3='Dallas', xad_4='TX', xad_5='75211', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5554894'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA03NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Granados', xpn_2='Claudia', xpn_3='Maria', xpn_5='Mrs.')
        nk1_2.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1_2.address = XAD(xad_1='3500 W Illinois Ave', xad_3='Dallas', xad_4='TX', xad_5='75211', xad_6='US')
        nk1_2.nk1_5 = '^PRN^PH^^1^214^5554893'
        nk1_2.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA03NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='2101', pl_3='01', pl_4='COOKCH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '5678901005^Hartwell^Rachel^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatrics', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260405003^^^COOKCH^VN'
        pv1.servicing_facility = CWE(cwe_1='01', cwe_2='Discharged to home', cwe_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20260405120000')
        pv1.admit_date_time = '20260407160000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J21.0', cwe_2='Acute bronchiolitis due to respiratory syncytial virus', cwe_3='I10')
        dg1.diagnosis_date_time = '20260405'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260408091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MIRTH20260408091000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40004', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Hightower^Crystal^Denise^^Ms.^'
        pid.date_time_of_birth = '19910415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2909 Lemmon Ave', xad_3='Dallas', xad_4='TX', xad_5='75204', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5558271'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '742-53-8196'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OBG', pl_2='0003', pl_3='01', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6789012006^Ashmore^Lisa^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='OBG', xcn_2='Obstetrics and Gynecology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408004', cx_4='PARKLAND', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40004', ei_2='MIRTH')
        orc.placer_order_group_number = EI(ei_1='GRP40004', ei_2='MIRTH')
        orc.date_time_of_order_event = '20260408090000'
        orc.orc_12 = '6789012006^Ashmore^Lisa^A^^^MD^^^^NPI'
        orc.orc_17 = 'PARKLAND^Parkland Memorial Hospital'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40004', ei_2='MIRTH')
        obr.universal_service_identifier = CWE(cwe_1='76856', cwe_2='Ultrasound pelvis complete', cwe_3='CPT4')
        obr.observation_date_time = '20260408090000'
        obr.obr_15 = '6789012006^Ashmore^Lisa^A^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N92.1', cwe_2='Excessive and frequent menstruation with irregular cycle', cwe_3='I10')
        dg1.diagnosis_date_time = '20260408'
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
        nte.comment = 'Evaluate for fibroids. Patient reports heavy irregular menses for 4 months.'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='CARD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260409110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MIRTH20260409110000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40005', cx_4='METHODIST_SA', cx_5='MR')
        pid.pid_5 = 'Caldwell^George^Raymond^^Mr.^'
        pid.date_time_of_birth = '19490320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='123 E Houston St', xad_3='San Antonio', xad_4='TX', xad_5='78205', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5556789'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '518-64-9302'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='0004', pl_3='01', pl_4='METHODIST_SA', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '7890123007^Kingsley^Steven^T^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260409005', cx_4='METHODIST_SA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40005', ei_2='MIRTH')
        orc.filler_order_number = EI(ei_1='FIL40005', ei_2='CARD')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260409090000')
        orc.orc_11 = '7890123007^Kingsley^Steven^T^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40005', ei_2='MIRTH')
        obr.filler_order_number = EI(ei_1='FIL40005', ei_2='CARD')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiogram routine', cwe_3='CPT4')
        obr.observation_date_time = '20260409090000'
        obr.obr_16 = '7890123007^Kingsley^Steven^T^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260409105000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='EKG interpretation', cwe_3='L')
        obx.obx_5 = (
            'Rate: 72 bpm\\.br\\Rhythm: Normal sinus rhythm\\.br\\Axis: Normal\\.br\\Intervals: PR 168ms, QRS 88ms, QTc 420ms\\.br\\ST/T changes: None\\.br\\'
            'Impression: Normal ECG'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260409105000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='EKG Tracing', cwe_3='AUSPDI')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgODQyIDU5NV0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMDIKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNTUwIFRkCihFS0cgVHJhY2luZyAtIDEy'
            'IExlYWQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooUGF0aWVudDogQ2FsZHdlbGwsIEdlb3JnZSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260409105000'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='COOKCH', hd_2='2.16.840.1.113883.3.3303', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260410090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MIRTH20260410090000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260410085500'
        evn.evn_5 = 'CHNURSE^Winslow^Emily^R^^^RN'
        evn.event_occurred = '20260410085500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40006', cx_4='COOKCH', cx_5='MR')
        pid.pid_5 = 'Luevano^Diego^Alejandro^^Master^'
        pid.date_time_of_birth = '20150822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4100 W Clarendon Dr', xad_3='Dallas', xad_4='TX', xad_5='75211', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5553291'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Luevano', xpn_2='Rosa', xpn_3='Patricia', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4100 W Clarendon Dr', xad_3='Dallas', xad_4='TX', xad_5='75211', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5553291'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='3105', pl_3='01', pl_4='COOKCH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '8901234008^Sterling^James^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatrics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260408006', cx_4='COOKCH', cx_5='VN')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260411140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MIRTH20260411140000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT40007', ei_2='MIRTH')
        sch.appointment_reason = CWE(cwe_1='PT', cwe_2='Physical Therapy Evaluation', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='45', cwe_2='MIN')
        sch.sch_9 = 'MIN^Minutes^ISO+'
        sch.appointment_duration_units = CNE(cne_4='20260416100000', cne_6='45', cne_7='MIN')
        sch.placer_contact_location = PL(pl_1='9012345009', pl_2='Culpepper', pl_3='Catherine', pl_4='L', pl_7='DPT', pl_11='NPI')
        sch.sch_16 = '^PRN^PH^^1^214^5558700'
        sch.sch_21 = '9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI'
        sch.placer_order_number = EI(ei_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40007', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Dunlap^James^Colton^^Mr.^'
        pid.date_time_of_birth = '19750113'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5522 La Sierra Dr', xad_3='Dallas', xad_4='TX', xad_5='75231', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5554567'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '293-58-4107'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PT', pl_2='0002', pl_3='01', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PT', xcn_2='Physical Therapy', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260411007', cx_4='PARKLAND', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='PT_REHAB')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='97161', cwe_2='Physical therapy evaluation low complexity', cwe_3='CPT4')
        ais.start_date_time = '20260416100000'
        ais.duration = '45^MIN'
        ais.duration_units = CNE(cne_1='MIN', cne_2='Minutes', cne_3='ISO+')
        ais.filler_status_code = CWE(cwe_1='Confirmed')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='9012345009', cwe_2='Culpepper', cwe_3='Catherine', cwe_4='L', cwe_7='DPT', cwe_11='NPI')
        aig.start_date_time = '20260416100000'
        aig.duration = '45^MIN'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='PT', pl_2='0002', pl_3='01', pl_4='PARKLAND')
        ail.start_date_time_offset_units = CNE(cne_1='20260416100000')
        ail.allow_substitution_code = CWE(cwe_1='45', cwe_2='MIN')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Post-ACL reconstruction, 6 weeks post-op. Begin outpatient rehabilitation.'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PHARM_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260412110000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MIRTH20260412110000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40008', cx_4='METHODIST_SA', cx_5='MR')
        pid.pid_5 = 'Enfield^Martha^Diane^^Mrs.^'
        pid.date_time_of_birth = '19460512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='8400 Datapoint Dr', xad_3='San Antonio', xad_4='TX', xad_5='78229', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5552345'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '385-71-2604'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='3201', pl_3='01', pl_4='METHODIST_SA', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '0123456010^Hartwell^Brian^P^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260411008', cx_4='METHODIST_SA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40008', ei_2='MIRTH')
        orc.placer_order_group_number = EI(ei_1='GRP40008', ei_2='MIRTH')
        orc.date_time_of_order_event = '20260412103000'
        orc.orc_12 = '0123456010^Hartwell^Brian^P^^^MD^^^^NPI'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^QD^HL70335'
        rxe.give_code = CWE(cwe_1='11289', cwe_2='Warfarin 5mg tablet', cwe_3='NDC')
        rxe.give_amount_minimum = '5'
        rxe.give_amount_maximum = '5'
        rxe.give_units = CWE(cwe_1='mg', cwe_2='milligrams', cwe_3='ISO+')
        rxe.give_dosage_form = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxe.dispense_units = CWE(cwe_1='30')
        rxe.number_of_refills = 'EA^each^ISO+'
        rxe.rxe_14 = '0123456010^Hartwell^Brian^P^^^MD^^^^NPI'
        rxe.give_indication = CWE(cwe_1='0', cwe_2='No Refills')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I48.91', cwe_2='Unspecified atrial fibrillation', cwe_3='I10')
        dg1.diagnosis_date_time = '20260411'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Target INR 2.0-3.0. Baseline INR 1.1. First dose tonight at 1800.'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260413200000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MIRTH20260413200000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260413195500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40009', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Trinh^Khoa^Minh^^Mr.^'
        pid.date_time_of_birth = '19830401'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2710 N Stemmons Fwy', xad_3='Dallas', xad_4='TX', xad_5='75207', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5551789'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '406-82-9153'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T12', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '1234560011^Ashmore^Amanda^J^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260413009', cx_4='PARKLAND', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='History and Physical', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260413195000')
        txa.transcriptionist_code_name = XCN(xcn_1='DOC40009', xcn_2='PARKLAND')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11492-6', cwe_2='History and physical note', cwe_3='LN')
        obx.obx_5 = (
            'HISTORY AND PHYSICAL\\.br\\Patient: Trinh, Khoa Minh\\.br\\DOB: 04/01/1983\\.br\\\\.br\\CHIEF COMPLAINT: Severe epigastric pain radiating to bac'
            'k for 6 hours\\.br\\\\.br\\HPI: 43 year old male presenting with acute onset epigastric pain radiating to the back, associated with nausea and v'
            'omiting. Pain rated 9/10. Denies fever, diarrhea, hematemesis. Reports heavy alcohol use over the weekend.\\.br\\\\.br\\EXAM: T 37.8, HR 110, BP'
            ' 148/92, RR 22, SpO2 97% RA\\.br\\Abdomen: Tender epigastrium with guarding, decreased bowel sounds\\.br\\\\.br\\ASSESSMENT: Acute pancreatitis,'
            ' likely alcohol-induced\\.br\\PLAN: NPO, IV fluids, pain management, lipase and CBC'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260413195000'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='FIN_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260414150000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'MIRTH20260414150000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260414145500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40010', cx_4='METHODIST_SA', cx_5='MR')
        pid.pid_5 = 'Pineda^Lucia^Carmen^^Mrs.^'
        pid.date_time_of_birth = '19720908'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5150 Broadway St', xad_3='San Antonio', xad_4='TX', xad_5='78209', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5558901'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '627-39-8401'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='0003', pl_3='01', pl_4='METHODIST_SA', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '2345670012^Winslow^Philip^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260414010', cx_4='METHODIST_SA', cx_5='VN')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_date = DR(dr_1='20260414100000')
        ft1.transaction_posting_date = '20260414100000'
        ft1.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1.transaction_code = CWE(cwe_1='77067', cwe_2='Screening mammography bilateral', cwe_3='CPT4')
        ft1.ft1_9 = '1'
        ft1.assigned_patient_location = PL(pl_1='RAD', pl_2='0003', pl_3='01', pl_4='METHODIST_SA')
        ft1.ft1_21 = '2345670012^Winslow^Philip^C^^^MD^^^^NPI'

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_date = DR(dr_1='20260414100000')
        ft1_2.transaction_posting_date = '20260414100000'
        ft1_2.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_2.transaction_code = CWE(cwe_1='77063', cwe_2='Screening digital breast tomosynthesis bilateral', cwe_3='CPT4')
        ft1_2.ft1_9 = '1'
        ft1_2.assigned_patient_location = PL(pl_1='RAD', pl_2='0003', pl_3='01', pl_4='METHODIST_SA')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.31', cwe_2='Encounter for screening mammogram for malignant neoplasm of breast', cwe_3='I10')
        dg1.diagnosis_date_time = '20260414'
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TX_DSHS')
        msh.date_time_of_message = '20260415100000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'MIRTH20260415100000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'ER'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40011', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Gifford^Sandra^Lynn^^Mrs.^'
        pid.date_time_of_birth = '19640220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='6411 Mockingbird Ln', xad_3='Dallas', xad_4='TX', xad_5='75214', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5557890'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '753-90-1482'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '3456780013^Culpepper^Timothy^M^^^MD^^^^NPI'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='0005', pl_3='01', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '3456780013^Culpepper^Timothy^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='FM', xcn_2='Family Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260415011', cx_4='PARKLAND', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD40011', ei_2='MIRTH')
        orc.placer_order_group_number = EI(ei_1='GRP40011', ei_2='MIRTH')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260415094000')
        orc.orc_11 = '3456780013^Culpepper^Timothy^M^^^MD^^^^NPI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20260415094000'
        rxa.administered_code = CWE(cwe_1='308', cwe_2='COVID-19 mRNA bivalent Pfizer', cwe_3='CVX')
        rxa.administered_amount = '0.3'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.rxa_15 = '00069-2100-01^^NDC'
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
        obx_2.obx_5 = '20231013'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TS'
        obx_3.observation_identifier = CWE(cwe_1='29769-7', cwe_2='Date vaccine information statement presented', cwe_3='LN')
        obx_3.obx_5 = '20260415'
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='COOKCH', hd_2='2.16.840.1.113883.3.3303', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260416180000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MIRTH20260416180000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260416175500'
        evn.evn_5 = 'TRIAGE^Kingsley^Nicole^J^^^RN'
        evn.event_occurred = '20260416175500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40012', cx_4='COOKCH', cx_5='MR')
        pid.pid_5 = 'Ochoa^Isabella^Renata^^Miss^'
        pid.date_time_of_birth = '20120715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2200 W Commerce St', xad_3='Fort Worth', xad_4='TX', xad_5='76102', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5552345'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Ochoa', xpn_2='Ernesto', xpn_3='Manuel', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2200 W Commerce St', xad_3='Fort Worth', xad_4='TX', xad_5='76102', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^817^5552345'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='UC', pl_2='0001', pl_3='01', pl_4='COOKCH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '4567890014^Sterling^Maria^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatrics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260416012', cx_4='COOKCH', cx_5='VN')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='High fever 104F, earache, irritability')
        pv2.visit_protection_indicator = '2^Emergent^HL70217'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='H66.91', cwe_2='Otitis media unspecified right ear', cwe_3='I10')
        dg1.diagnosis_date_time = '20260416'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260417100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MIRTH20260417100000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260417095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN40013', cx_4='METHODIST_SA', cx_5='MR'), CX(cx_1='502-81-6347', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Uddin^Fatima^Zahra^^Mrs.^'
        pid.date_time_of_birth = '19870615'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='9800 Fredericksburg Rd', xad_3='San Antonio', xad_4='TX', xad_5='78240', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5554567'
        pid.pid_14 = '^WPN^PH^^1^210^5559876'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '502-81-6347'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Methodist Hospital San Antonio^^^^NPI'
        pd1.pd1_4 = '5678900015^Hartwell^Angela^M^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Uddin', xpn_2='Tariq', xpn_3='Hassan', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='9800 Fredericksburg Rd', xad_3='San Antonio', xad_4='TX', xad_5='78240', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^210^5554568'
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260418130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MIRTH20260418130000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40014', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Massey^Marcus^Darnell^^Mr.^'
        pid.date_time_of_birth = '19850922'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4510 Columbia Ave', xad_3='Dallas', xad_4='TX', xad_5='75226', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5556234'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '268-41-7503'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T6', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '6789010016^Winslow^Stephanie^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260418014', cx_4='PARKLAND', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40014', ei_2='MIRTH')
        orc.filler_order_number = EI(ei_1='FIL40014', ei_2='TOX')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260418100000')
        orc.orc_11 = '6789010016^Winslow^Stephanie^R^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40014', ei_2='MIRTH')
        obr.filler_order_number = EI(ei_1='FIL40014', ei_2='TOX')
        obr.universal_service_identifier = CWE(cwe_1='97195', cwe_2='Drug screen qualitative', cwe_3='CPT4')
        obr.observation_date_time = '20260418100000'
        obr.obr_16 = '6789010016^Winslow^Stephanie^R^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260418125000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='3426-4', cwe_2='Tetrahydrocannabinol [Presence] in Urine', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
        obx.reference_range = 'Negative'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260418125000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='3399-3', cwe_2='Opiates [Presence] in Urine', cwe_3='LN')
        obx_2.obx_5 = '260415000^Not detected^SCT'
        obx_2.reference_range = 'Negative'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260418125000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='3397-7', cwe_2='Cocaine metabolites [Presence] in Urine', cwe_3='LN')
        obx_3.obx_5 = '260415000^Not detected^SCT'
        obx_3.reference_range = 'Negative'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260418125000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='3390-2', cwe_2='Benzodiazepines [Presence] in Urine', cwe_3='LN')
        obx_4.obx_5 = '260415000^Not detected^SCT'
        obx_4.reference_range = 'Negative'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260418125000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='3349-8', cwe_2='Amphetamines [Presence] in Urine', cwe_3='LN')
        obx_5.obx_5 = '260415000^Not detected^SCT'
        obx_5.reference_range = 'Negative'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260418125000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='PDF', cwe_2='Toxicology Report', cwe_3='AUSPDI')
        obx_6.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNDQKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihUb3hpY29sb2d5IFNjcmVl'
            'biBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooUGFya2xhbmQgTWVtb3JpYWwgSG9zcGl0YWwpIFRqCjAgLTIwIFRkCihTcGVjaW1lbjogVXJpbmUpIFRqCkVUCmVuZHN0cmVh'
            'bQplbmRvYmoK'
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260418125000'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260419230000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MIRTH20260419230000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260419225500'
        evn.evn_5 = 'TELN^Ashmore^Patrick^J^^^RN'
        evn.event_occurred = '20260419225500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40015', cx_4='METHODIST_SA', cx_5='MR')
        pid.pid_5 = 'Varma^Rajesh^Sunil^^Mr.^'
        pid.date_time_of_birth = '19580705'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3200 W Woodlawn Ave', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^210^5551234'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '319-46-8205'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TELE', pl_2='2208', pl_3='01', pl_4='METHODIST_SA', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '7890120017^Kingsley^Douglas^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicine', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260418015^^^METHODIST_SA^VN'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='New onset atrial fibrillation with rapid ventricular response, rate controlled')

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260420100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MIRTH20260420100000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260420095500'
        evn.evn_5 = 'HIM^Culpepper^Karen^R^^^HIM'
        evn.event_occurred = '20260420095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40016', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Norwood^Patricia^Elaine^^Ms.^'
        pid.date_time_of_birth = '19790314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7100 Greenville Ave', xad_3='Dallas', xad_4='TX', xad_5='75231', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5558901'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '481-57-3920'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN40016DUP', cx_4='PARKLAND', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='Norwood', xpn_2='Patricia', xpn_3='E')

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='COOKCH', hd_2='2.16.840.1.113883.3.3303', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260421140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MIRTH20260421140000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260421135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40017', cx_4='COOKCH', cx_5='MR')
        pid.pid_5 = 'Shimizu^Thomas^Kenji^^Mr.^'
        pid.date_time_of_birth = '19680503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3001 Bryan St', xad_3='Dallas', xad_4='TX', xad_5='75204', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5556780'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '592-64-8317'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Shimizu', xpn_2='Linda', xpn_3='Akiko', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3001 Bryan St', xad_3='Dallas', xad_4='TX', xad_5='75204', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5556781'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Shimizu', xpn_2='Robert', xpn_3='Hiroshi', xpn_5='Mr.')
        nk1_2.relationship = CWE(cwe_1='SON', cwe_2='Son', cwe_3='HL70063')
        nk1_2.address = XAD(xad_1='1208 Elm St', xad_3='Dallas', xad_4='TX', xad_5='75202', xad_6='US')
        nk1_2.nk1_5 = '^PRN^PH^^1^469^5553456'
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MF_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260422090000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'MIRTH20260422090000018'
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
        mfe.mfn_control_id = '20260422085500'
        mfe.mfe_4 = '8901230018^Montoya^Elena^Sofia^^NP'
        mfe.primary_key_value_type = 'CWE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='8901230018')
        stf.staff_identifier_list = CX(cx_1='U8901230018')
        stf.staff_name = XPN(xpn_1='Montoya', xpn_2='Elena', xpn_3='Sofia', xpn_5='NP')
        stf.administrative_sex = CWE(cwe_1='F')
        stf.date_time_of_birth = '19850412'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.stf_12 = '^WPN^PH^^1^214^5559800'

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='8901230018', cwe_2='Montoya', cwe_3='Elena', cwe_4='Sofia', cwe_6='NP')
        pra.practitioner_group = CWE(cwe_1='PARKLAND', cwe_2='Parkland Memorial Hospital')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='Institution', cwe_3='HL70186')
        pra.date_entered_practice = '363L00000X^Nurse Practitioner^NUCC'

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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_RECV')
        msh.sending_facility = HD(hd_1='TX_HIE')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='METHODIST_SA', hd_2='2.16.840.1.113883.3.3302', hd_3='ISO')
        msh.date_time_of_message = '20260423100000'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'MIRTH20260423100000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MIRTH20260406143000002'
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
    """ Based on live/us-texas/us-texas-mirth.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PARKLAND', hd_2='2.16.840.1.113883.3.3301', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260424030000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MIRTH20260424030000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40020', cx_4='PARKLAND', cx_5='MR')
        pid.pid_5 = 'Outlaw^Robert^Dwayne^^Mr.^'
        pid.date_time_of_birth = '19430917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1500 E Illinois Ave', xad_3='Dallas', xad_4='TX', xad_5='75216', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5551890'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '714-62-3908'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='1004', pl_3='01', pl_4='PARKLAND', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '9012340019^Sterling^Angela^D^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CCM', xcn_2='Critical Care', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260423020', cx_4='PARKLAND', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40020', ei_2='MIRTH')
        orc.placer_order_group_number = EI(ei_1='GRP40020', ei_2='MIRTH')
        orc.date_time_of_order_event = '20260424025000'
        orc.orc_12 = '9012340019^Sterling^Angela^D^^^MD^^^^NPI'
        orc.orc_17 = 'PARKLAND^Parkland Memorial Hospital'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40020', ei_2='MIRTH')
        obr.universal_service_identifier = CWE(cwe_1='71045', cwe_2='Chest X-ray single view', cwe_3='CPT4')
        obr.observation_date_time = '20260424025000'
        obr.obr_15 = '9012340019^Sterling^Angela^D^^^MD^^^^NPI'
        obr.result_status = '9^Stat^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J96.01', cwe_2='Acute respiratory failure with hypoxia', cwe_3='I10')
        dg1.diagnosis_date_time = '20260423'
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
        nte.comment = 'ICU patient on ventilator. Check ET tube position and interval change.'

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

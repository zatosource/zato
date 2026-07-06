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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, DR, EI, HD, MSG, PIP, PL, PLN, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, DftP03Visit, \
    MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, FT1, IN1, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PRA, PV1, PV2, RGS, RXA, \
    RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-cloverleaf.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_ADT')
        msh.sending_facility = HD(hd_1='UT_HEALTH_SA')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='UTHS_ENGINE')
        msh.date_time_of_message = '20250305120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CLF20250305001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250305115800'
        evn.evn_5 = 'CHARGE01^STRICKLAND^PAMELA^D^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN50001234', cx_4='UT_HEALTH_SA', cx_5='MR'), CX(cx_1='831-47-6205', cx_4='USSSA', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='FUENTES', xpn_2='Ricardo', xpn_3='Emilio', xpn_5='Mr.')
        pid.date_time_of_birth = '19710930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Callaghan Rd', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5478831'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'UT HEALTH SAN ANTONIO^^11111'
        pd1.pd1_4 = '1122334^KIRKPATRICK^DONALD^W^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='FUENTES', xpn_2='Elena', xpn_3='Cristina', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4218 Callaghan Rd', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^210^5478832'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6SOUTH', pl_2='602', pl_3='A', pl_4='UT_HEALTH_SA', pl_8='MEDSURG')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '1122334^KIRKPATRICK^DONALD^W^^^MD^ATTENDING'
        pv1.pv1_8 = '2233445^BEAUMONT^RACHEL^C^^^MD^CONSULTING'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='1122334', cwe_2='KIRKPATRICK', cwe_3='DONALD', cwe_4='W', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V50001234', cwe_4='UT_HEALTH_SA', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BCBS')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute pancreatitis')
        pv2.actual_length_of_inpatient_stay = '4'
        pv2.visit_protection_indicator = 'N'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='001', cwe_2='BCBS OF TEXAS')
        in1.insurance_company_id = CX(cx_1='BCBS001')
        in1.insurance_company_name = XON(xon_1='BLUE CROSS BLUE SHIELD OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 660044', xad_3='Dallas', xad_4='TX', xad_5='75266', xad_6='US')
        in1.group_number = 'GRP77777'
        in1.plan_effective_date = '20240101'
        in1.name_of_insured = XPN(xpn_1='FUENTES', xpn_2='Ricardo', xpn_3='Emilio')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19710930'
        in1.insureds_address = XAD(xad_1='4218 Callaghan Rd', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US')
        in1.policy_limit_days = 'BCBS567890123'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K85.90', cwe_2='Acute pancreatitis without necrosis or infection, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH_REG')
        msh.sending_facility = HD(hd_1='VALLEY_BAPTIST_HRL')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='VB_ENGINE')
        msh.date_time_of_message = '20250308054500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CLF20250308001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250308054500'
        evn.evn_5 = 'REG01^CAVANAUGH^BRENDA^L^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50012345', cx_4='VALLEY_BAPTIST', cx_5='MR')
        pid.patient_name = XPN(xpn_1='VILLARREAL', xpn_2='Marco', xpn_3='Andres', xpn_5='Mr.')
        pid.date_time_of_birth = '19890722'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='814 Morgan Blvd', xad_3='Harlingen', xad_4='TX', xad_5='78550', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^956^5473291'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED5', pl_3='A', pl_4='VALLEY_BAPTIST', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '3344556^MCDERMOTT^JANET^P^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='3344556', cwe_2='MCDERMOTT', cwe_3='JANET', cwe_4='P', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50012345', xcn_4='VALLEY_BAPTIST', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S52.501A', cwe_2='Unspecified fracture of lower end of right radius, initial encounter', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_EMR')
        msh.sending_facility = HD(hd_1='MEDICAL_CITY_DALLAS')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='MC_ENGINE')
        msh.date_time_of_message = '20250310080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CLF20250310001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50023456', cx_4='MEDICAL_CITY', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DANG', xpn_2='Mai', xpn_3='Tuyet', xpn_5='Ms.')
        pid.date_time_of_birth = '19650413'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3920 Belt Line Rd', xad_3='Dallas', xad_4='TX', xad_5='75244', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^972^5536814'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3WEST', pl_2='312', pl_3='A', pl_4='MEDICAL_CITY', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='4455667', cwe_2='PENNINGTON', cwe_3='ROSS', cwe_4='E', cwe_7='MD')
        pv1.pv1_20 = 'V50023456^^^MEDICAL_CITY^VN'
        pv1.charge_price_indicator = CWE(cwe_1='CIGNA')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        orc.orc_7 = '^^^20250310083000^^R'
        orc.date_time_of_order_event = '20250310080000'
        orc.orc_10 = 'NURSE01^STRICKLAND^KAREN^P^^^RN'
        orc.orc_12 = '4455667^PENNINGTON^ROSS^E^^^MD'
        orc.enterers_location = PL(pl_1='3WEST', pl_2='312', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='MEDICAL_CITY')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        obr.universal_service_identifier = CWE(cwe_1='86235', cwe_2='NUCLEAR ANTIBODY', cwe_3='CPT')
        obr.observation_date_time = '20250310080000'
        obr.obr_16 = '4455667^PENNINGTON^ROSS^E^^^MD'
        obr.results_rpt_status_chng_date_time = '20250310083000'
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
        obr_2.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        obr_2.universal_service_identifier = CWE(cwe_1='86200', cwe_2='CCP ANTIBODY', cwe_3='CPT')
        obr_2.observation_date_time = '20250310080000'
        obr_2.obr_16 = '4455667^PENNINGTON^ROSS^E^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250310083000'
        obr_2.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M06.9', cwe_2='Rheumatoid arthritis, unspecified', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QUEST_LAB')
        msh.sending_facility = HD(hd_1='QUEST_TX')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='MC_ENGINE')
        msh.date_time_of_message = '20250312143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CLF20250312001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50023456', cx_4='MEDICAL_CITY', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DANG', xpn_2='Mai', xpn_3='Tuyet', xpn_5='Ms.')
        pid.date_time_of_birth = '19650413'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3920 Belt Line Rd', xad_3='Dallas', xad_4='TX', xad_5='75244', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^972^5536814'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3WEST', pl_2='312', pl_3='A', pl_4='MEDICAL_CITY', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='4455667', cwe_2='PENNINGTON', cwe_3='ROSS', cwe_4='E', cwe_7='MD')
        pv1.pv1_20 = 'V50023456^^^MEDICAL_CITY^VN'

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        orc.filler_order_number = EI(ei_1='QR700234', ei_2='QUEST')
        orc.orc_7 = '^^^20250310083000^^R'
        orc.date_time_of_order_event = '20250312143000'
        orc.orc_12 = '4455667^PENNINGTON^ROSS^E^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        obr.filler_order_number = EI(ei_1='QR700234', ei_2='QUEST')
        obr.universal_service_identifier = CWE(cwe_1='86235', cwe_2='NUCLEAR ANTIBODY', cwe_3='CPT')
        obr.observation_date_time = '20250310080000'
        obr.obr_16 = '4455667^PENNINGTON^ROSS^E^^^MD'
        obr.results_rpt_status_chng_date_time = '20250312140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5048-4', cwe_2='ANA PATTERN', cwe_3='LN')
        obx.obx_5 = 'HOMOGENEOUS'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250312130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30341-2', cwe_2='ANA TITER', cwe_3='LN')
        obx_2.obx_5 = '1:640'
        obx_2.reference_range = '<1:40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250312130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD601234', ei_2='CERNER')
        obr_2.filler_order_number = EI(ei_1='QR700235', ei_2='QUEST')
        obr_2.universal_service_identifier = CWE(cwe_1='86200', cwe_2='CCP ANTIBODY', cwe_3='CPT')
        obr_2.observation_date_time = '20250310080000'
        obr_2.obr_16 = '4455667^PENNINGTON^ROSS^E^^^MD'
        obr_2.results_rpt_status_chng_date_time = '20250312140000'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '1'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='53027-9', cwe_2='CCP ANTIBODY IGG', cwe_3='LN')
        obx_3.obx_5 = '185'
        obx_3.units = CWE(cwe_1='U/mL')
        obx_3.reference_range = '<20'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250312130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_3

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_ADT')
        msh.sending_facility = HD(hd_1='DELL_SETON_AUSTIN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='SETON_ENGINE')
        msh.date_time_of_message = '20250315091000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CLF20250315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250315091000'
        evn.evn_5 = 'REG02^HOLBROOK^CYNTHIA^L^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50034567', cx_4='DELL_SETON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WASHINGTON', xpn_2='Keandra', xpn_3='Simone', xpn_5='Mrs.')
        pid.date_time_of_birth = '19800604'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1807 Manchaca Rd', xad_3='Austin', xad_4='TX', xad_5='78704', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^5419073'
        pid.pid_14 = '^WPN^PH^^^512^5419074'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '742-18-3056'
        pid.birth_place = 'N^Non-Hispanic^HL70189'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='L_AND_D', pl_2='302', pl_3='A', pl_4='DELL_SETON', pl_8='LABOR_DELIVERY')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '5566778^GALLAGHER^THERESA^N^^^MD^OBGYN'
        pv1.ambulatory_status = CWE(cwe_1='5566778', cwe_2='GALLAGHER', cwe_3='THERESA', cwe_4='N', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50034567', xcn_4='DELL_SETON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='AETNA')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WASHINGTON', xpn_2='Darnell', xpn_3='Terrence', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='1807 Manchaca Rd', xad_3='Austin', xad_4='TX', xad_5='78704', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^512^5419075'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='002', cwe_2='AETNA')
        in1.insurance_company_id = CX(cx_1='AET001')
        in1.insurance_company_name = XON(xon_1='AETNA HEALTH OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 14079', xad_3='Lexington', xad_4='KY', xad_5='40512', xad_6='US')
        in1.group_number = 'GRP44444'
        in1.plan_effective_date = '20240601'
        in1.name_of_insured = XPN(xpn_1='WASHINGTON', xpn_2='Keandra', xpn_3='Simone')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19800604'
        in1.insureds_address = XAD(xad_1='1807 Manchaca Rd', xad_3='Austin', xad_4='TX', xad_5='78704', xad_6='US')
        in1.policy_number = 'AET678901234'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_PACS')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_HOUSTON')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='METH_H_ENGINE')
        msh.date_time_of_message = '20250318153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CLF20250318001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50045678', cx_4='METHODIST_HOUSTON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='JEFFERSON', xpn_2='Terrell', xpn_3='Marquise', xpn_5='Mr.')
        pid.date_time_of_birth = '19680210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='9427 Richmond Ave', xad_3='Houston', xad_4='TX', xad_5='77063', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5524198'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CCU', pl_2='801', pl_3='A', pl_4='METHODIST_HOUSTON', pl_8='CCU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '6677889^WHITMORE^ALAN^J^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='6677889', cwe_2='WHITMORE', cwe_3='ALAN', cwe_4='J', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50045678', xcn_4='METHODIST_HOUSTON', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='RAD701234', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='PACS801234', ei_2='GE_PACS')
        orc.orc_7 = '^^^20250318100000^^S'
        orc.date_time_of_order_event = '20250318153000'
        orc.orc_12 = '7788990^PEMBERTON^DIANA^F^^^MD^RADIOLOGIST'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD701234', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='PACS801234', ei_2='GE_PACS')
        obr.universal_service_identifier = CWE(cwe_1='93307', cwe_2='ECHOCARDIOGRAM COMPLETE', cwe_3='CPT')
        obr.observation_date_time = '20250318103000'
        obr.obr_16 = '7788990^PEMBERTON^DIANA^F^^^MD'
        obr.results_rpt_status_chng_date_time = '20250318150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx.obx_5 = (
            'EXAM: Transthoracic Echocardiogram\\.br\\\\.br\\CLINICAL INDICATION: Chest pain, elevated troponin\\.br\\\\.br\\FINDINGS:\\.br\\Left ventricle: '
            'Mildly dilated. EF 35-40% (reduced). Regional wall motion abnormality - akinesis of inferior and inferolateral walls.\\.br\\Right ventricle: N'
            'ormal size and function.\\.br\\Left atrium: Mildly dilated (4.2 cm).\\.br\\Valves: Mild mitral regurgitation. Aortic valve trileaflet without st'
            'enosis.\\.br\\Pericardium: No effusion.\\.br\\\\.br\\IMPRESSION:\\.br\\1. Reduced left ventricular systolic function (EF 35-40%) with regional w'
            'all motion abnormality consistent with ischemic etiology.\\.br\\2. Mild mitral regurgitation.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250318150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='18043-0', cwe_2='LEFT VENTRICULAR EJECTION FRACTION', cwe_3='LN')
        obx_2.obx_5 = '37'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '55-70'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250318150000'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_DOC')
        msh.sending_facility = HD(hd_1='BAYLOR_DALLAS')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='BAYLOR_ENGINE')
        msh.date_time_of_message = '20250320110000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CLF20250320001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250320110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50056789', cx_4='BAYLOR_DALLAS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BOOKER', xpn_2='Gwendolyn', xpn_3='Yvette', xpn_5='Mrs.')
        pid.date_time_of_birth = '19500228'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2945 Forest Ln', xad_3='Dallas', xad_4='TX', xad_5='75234', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5537621'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4NORTH', pl_2='408', pl_3='A', pl_4='BAYLOR_DALLAS', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='8899001', cwe_2='ALDRIDGE', cwe_3='WARREN', cwe_4='J', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V50056789', cwe_4='BAYLOR_DALLAS', cwe_5='VN')
        pv1.visit_number = CX(cx_1='MEDICARE')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='OPERATIVE NOTE', cwe_3='HL70270')
        txa.document_content_presentation = 'FT^Full Text^HL70191'
        txa.activity_date_time = '20250319140000'
        txa.origination_date_time = '20250320110000'
        txa.txa_11 = '8899001^ALDRIDGE^WARREN^J^^^MD'
        txa.unique_document_number = EI(ei_1='DOC890123')
        txa.document_confidentiality_status = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='28570-0', cwe_2='PROCEDURE NOTE', cwe_3='LN')
        obx.obx_5 = (
            'PROCEDURE: Total left knee arthroplasty\\.br\\DATE: 03/19/2025\\.br\\SURGEON: Dr. Warren Aldridge, MD\\.br\\ANESTHESIA: Spinal with sedation\\.b'
            'r\\\\.br\\PREOPERATIVE DIAGNOSIS: Left knee osteoarthritis, severe\\.br\\POSTOPERATIVE DIAGNOSIS: Same\\.br\\\\.br\\FINDINGS: Grade IV chondroma'
            'lacia of medial and lateral compartments. Eburnated bone on tibial plateau.\\.br\\\\.br\\PROCEDURE DETAILS:\\.br\\Standard medial parapatellar a'
            'pproach. Femoral and tibial cuts performed with navigation assistance. Trialed size 5 femoral, size 4 tibial. Final components cemented in p'
            'lace. Knee flexion to 130 degrees, stable in all planes.\\.br\\\\.br\\EBL: 250 mL\\.br\\DISPOSITION: To PACU in stable condition.'
        )
        obx.observation_result_status = 'F'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_PHARM')
        msh.sending_facility = HD(hd_1='CHRISTUS_MOTHER_FRANCES')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='CMF_ENGINE')
        msh.date_time_of_message = '20250322090000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CLF20250322001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50067890', cx_4='CHRISTUS_MF', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CRENSHAW', xpn_2='Judith', xpn_3='Elaine', xpn_5='Mrs.')
        pid.date_time_of_birth = '19550714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3102 Old Henderson Hwy', xad_3='Tyler', xad_4='TX', xad_5='75702', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^903^5417862'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2EAST', pl_2='205', pl_3='A', pl_4='CHRISTUS_MF', pl_8='MEDSURG')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '9900112^CAVANAUGH^DEREK^T^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='9900112', cwe_2='CAVANAUGH', cwe_3='DEREK', cwe_4='T', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='CHRISTUS_MF', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICARE')

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
        orc.placer_order_number = EI(ei_1='RX801234', ei_2='CERNER')
        orc.orc_7 = '^^^20250322090000^^R'
        orc.date_time_of_order_event = '20250322090000'
        orc.orc_10 = 'NURSE02^HOLBROOK^ANGELA^R^^^RN'
        orc.orc_12 = '9900112^CAVANAUGH^DEREK^T^^^MD'
        orc.enterers_location = PL(pl_1='2EAST', pl_2='205', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='CHRISTUS_MF')

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^Q6H^^20250322090000^20250329090000'
        rxe.give_code = CWE(cwe_1='3640', cwe_2='ENOXAPARIN 40MG/0.4ML SYRINGE', cwe_3='NDC')
        rxe.give_amount_minimum = '40'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70484')
        rxe.number_of_refills = '7'
        rxe.give_strength_units = CWE(cwe_1='Q6H', cwe_2='Every 6 hours')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='SC', cwe_2='Subcutaneous', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='ABD', cwe_2='Abdomen', cwe_3='HL70163')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.99', cwe_2='Other pulmonary embolism without acute cor pulmonale', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_SCHED')
        msh.sending_facility = HD(hd_1='UT_SOUTHWESTERN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='UTSW_ENGINE')
        msh.date_time_of_message = '20250325140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CLF20250325001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT800345', ei_2='EPIC')
        sch.filler_appointment_id = EI(ei_1='APT800345', ei_2='EPIC')
        sch.schedule_id = CWE(cwe_1='NEUR', cwe_2='Neurology Follow-up', cwe_3='LOCAL')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='30', cwe_2='MIN')
        sch.appointment_type = CWE(cwe_1='1')
        sch.appointment_duration_units = CNE(cne_1='BOOKED')
        sch.sch_16 = '0011223^HARRINGTON^ELISE^M^^^MD^NEUROLOGIST'
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='5534912')
        sch.filler_contact_address = XAD(xad_1='5323 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75390', xad_6='US')
        sch.parent_placer_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50078901', cx_4='UTSW', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SANDERSON', xpn_2='Warren', xpn_3='Douglas', xpn_5='Mr.')
        pid.date_time_of_birth = '19550117'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6715 Inwood Rd', xad_3='Dallas', xad_4='TX', xad_5='75209', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5538167'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='EXAM5', pl_3='A', pl_4='UTSW', pl_8='NEUROLOGY')
        pv1.hospital_service = CWE(cwe_1='NEUR')
        pv1.patient_type = CWE(cwe_1='0011223', cwe_2='HARRINGTON', cwe_3='ELISE', cwe_4='M', cwe_7='MD')
        pv1.pv1_20 = 'V50078901^^^UTSW^VN'
        pv1.charge_price_indicator = CWE(cwe_1='MEDICARE')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='NEUR')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='NEUR', cwe_2='Neurology Follow-up', cwe_3='LOCAL')
        ais.start_date_time = '20250410143000'
        ais.duration = '30^MIN'
        ais.duration_units = CNE(cne_1='30', cne_2='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '0011223^HARRINGTON^ELISE^M^^^MD'
        aip.resource_type = CWE(cwe_1='NEUROLOGIST')
        aip.resource_group = CWE(cwe_1='20250410143000')
        aip.start_date_time_offset_units = CNE(cne_1='30', cne_2='MIN')

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
        ail.location_resource_id = PL(pl_1='NEUR', pl_2='EXAM5', pl_3='A', pl_4='UTSW')
        ail.location_type_ail = CWE(cwe_1='CLINIC')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_IMM')
        msh.sending_facility = HD(hd_1='DELL_CHILDRENS_AUSTIN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='SETON_ENGINE')
        msh.date_time_of_message = '20250328100000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'CLF20250328001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50089012', cx_4='DELL_CHILDRENS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='XIONG', xpn_2='Kellan', xpn_3='Soua', xpn_5='')
        pid.date_time_of_birth = '20230815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5410 South Lamar Blvd', xad_3='Austin', xad_4='TX', xad_5='78745', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^5497312'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = "DELL CHILDREN'S MEDICAL CENTER^^22222"
        pd1.pd1_4 = '1122334^RUTHERFORD^SONYA^A^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='XIONG', xpn_2='Pang', xpn_3='Ntooj', xpn_5='Ms.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='5410 South Lamar Blvd', xad_3='Austin', xad_4='TX', xad_5='78745', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^512^5497312'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='IMM901234', ei_2='EPIC')
        orc.orc_12 = '1122334^RUTHERFORD^SONYA^A^^^MD'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20250328095000'
        rxa.date_time_end_of_administration = '20250328095100'
        rxa.administered_code = CWE(cwe_1='133', cwe_2='PCV13', cwe_3='CVX')
        rxa.administered_amount = '0.5'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliter', cwe_3='UCUM')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='NEW IMMUNIZATION RECORD', cwe_3='NIP001')
        rxa.rxa_10 = '1122334^RUTHERFORD^SONYA^A^^^MD'
        rxa.rxa_15 = '00006498101^PREVNAR 13^NDC'
        rxa.substance_expiration_date = 'PFR'
        rxa.system_entry_date_time = 'CP'
        rxa.administered_drug_strength_volume = 'A'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LT', cwe_2='Left Thigh', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='VACCINE FUNDING SOURCE', cwe_3='LN')
        obx.obx_5 = 'VXC50^PRIVATE FUNDS^CDCPHINVS'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='30956-7', cwe_2='VACCINE TYPE', cwe_3='LN')
        obx_2.obx_5 = '133^PCV13^CVX'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TS'
        obx_3.observation_identifier = CWE(cwe_1='29768-9', cwe_2='DATE VACCINE INFORMATION STATEMENT PRESENTED', cwe_3='LN')
        obx_3.obx_5 = '20230801'
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
        msg.order = order

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_FIN')
        msh.sending_facility = HD(hd_1='HARRIS_HEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='HARRIS_ENGINE')
        msh.date_time_of_message = '20250401160000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CLF20250401001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20250401160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50090123', cx_4='HARRIS_HEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CALDERON', xpn_2='Marisol', xpn_3='Beatriz', xpn_5='Ms.')
        pid.date_time_of_birth = '19830520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='7614 Harrisburg Blvd', xad_3='Houston', xad_4='TX', xad_5='77011', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5412093'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='EXAM4', pl_3='A', pl_4='HARRIS_HEALTH', pl_8='PRIMARYCARE')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine')
        pv1.pv1_7 = '2233445^PENNINGTON^GRAHAM^M^^^MD'
        pv1.ambulatory_status = CWE(cwe_1='2233445', cwe_2='PENNINGTON', cwe_3='GRAHAM', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50090123', xcn_4='HARRIS_HEALTH', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20250401')
        ft1.transaction_batch_id = '20250401150000'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = '99214^OFFICE VISIT LEVEL 4^CPT'
        ft1.transaction_type = CWE(cwe_1='99214', cwe_2='OFFICE VISIT LEVEL 4', cwe_3='CPT')
        ft1.ft1_8 = '1'
        ft1.ft1_11 = '2233445^PENNINGTON^GRAHAM^M^^^MD'
        ft1.ordered_by_code = XCN(xcn_1='99214')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20250401')
        ft1_2.transaction_batch_id = '20250401151500'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = '36415^VENIPUNCTURE^CPT'
        ft1_2.transaction_type = CWE(cwe_1='36415', cwe_2='VENIPUNCTURE', cwe_3='CPT')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_11 = '2233445^PENNINGTON^GRAHAM^M^^^MD'
        ft1_2.ordered_by_code = XCN(xcn_1='36415')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20250401')
        ft1_3.transaction_batch_id = '20250401151500'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = '80053^COMPREHENSIVE METABOLIC PANEL^CPT'
        ft1_3.transaction_type = CWE(cwe_1='80053', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='CPT')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_11 = '2233445^PENNINGTON^GRAHAM^M^^^MD'
        ft1_3.ordered_by_code = XCN(xcn_1='80053')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.65', cwe_2='Type 2 diabetes mellitus with hyperglycemia', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ADT')
        msh.sending_facility = HD(hd_1='MEDICAL_CITY_DALLAS')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='MC_ENGINE')
        msh.date_time_of_message = '20250403110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CLF20250403001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250403110000'
        evn.evn_5 = 'CASE01^MERCER^PATRICIA^L^^^MSW'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50023456', cx_4='MEDICAL_CITY', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DANG', xpn_2='Mai', xpn_3='Tuyet', xpn_5='Ms.')
        pid.date_time_of_birth = '19650413'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3920 Belt Line Rd', xad_3='Dallas', xad_4='TX', xad_5='75244', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^972^5536814'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3WEST', pl_2='312', pl_3='A', pl_4='MEDICAL_CITY', pl_8='MEDSURG')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '4455667^PENNINGTON^ROSS^E^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4455667', cwe_2='PENNINGTON', cwe_3='ROSS', cwe_4='E', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V50023456', xcn_4='MEDICAL_CITY', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='CIGNA')
        pv1.discharged_to_location = DLD(dld_1='DIS')
        pv1.pending_location = PL(pl_1='20250310080000')
        pv1.admit_date_time = '20250403110000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Rheumatoid arthritis flare, resolved')
        pv2.actual_length_of_inpatient_stay = '4'
        pv2.retention_indicator = 'SNF^Skilled Nursing Facility^HL70112'
        pv2.visit_publicity_code = CWE(cwe_1='N')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M06.9', cwe_2='Rheumatoid arthritis, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='M05.70', cwe_2='Rheumatoid arthritis with rheumatoid factor of unspecified site', cwe_3='ICD10')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_CARD')
        msh.sending_facility = HD(hd_1='TEXAS_HEART_INST')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='THI_ENGINE')
        msh.date_time_of_message = '20250405140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CLF20250405001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50101234', cx_4='TEXAS_HEART', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HARGROVE', xpn_2='Clifton', xpn_3='Ray', xpn_5='Mr.')
        pid.date_time_of_birth = '19580427'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='11302 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77077', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^281^5509247'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CATH', pl_2='LAB2', pl_3='A', pl_4='TEXAS_HEART', pl_8='CATHLAB')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.patient_type = CWE(cwe_1='3344556', cwe_2='DRUMMOND', cwe_3='PAUL', cwe_4='A', cwe_7='MD', cwe_8='CARDIOLOGIST')
        pv1.pv1_20 = 'V50101234^^^TEXAS_HEART^VN'
        pv1.charge_price_indicator = CWE(cwe_1='BCBS')

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
        orc.placer_order_number = EI(ei_1='CATH901234', ei_2='CERNER')
        orc.filler_order_number = EI(ei_1='CATH901234', ei_2='CARD_SYS')
        orc.orc_7 = '^^^20250404^^R'
        orc.date_time_of_order_event = '20250405140000'
        orc.orc_12 = '3344556^DRUMMOND^PAUL^A^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CATH901234', ei_2='CERNER')
        obr.filler_order_number = EI(ei_1='CATH901234', ei_2='CARD_SYS')
        obr.universal_service_identifier = CWE(cwe_1='93458', cwe_2='LEFT HEART CATHETERIZATION', cwe_3='CPT')
        obr.observation_date_time = '20250404090000'
        obr.obr_16 = '3344556^DRUMMOND^PAUL^A^^^MD'
        obr.results_rpt_status_chng_date_time = '20250405133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Cardiac Catheterization Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDIg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDEyNSA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjcyIDcyMCBUZAooQ2FyZGlhYyBDYXRoZXRlcml6YXRpb24gUmVwb3J0KSBUagowIDI0'
            'IFRkCi9GMSAxMiBUZgooTEFEOiA5MCUgc3Rlbm9zaXMgcHJveGltYWwgc2VnbWVudCAtIFN0ZW50IGRlcGxveWVkKSBUagowIDI0IFRkCihSQ0E6IDUwJSBzdGVub3NpcyAtIE1lZGlj'
            'YWwgbWFuYWdlbWVudCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iag=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250405133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='18745-0', cwe_2='CARDIAC CATHETERIZATION REPORT', cwe_3='LN')
        obx_2.obx_5 = (
            'PROCEDURE: Left heart catheterization with coronary angiography and PCI\\.br\\DATE: 04/04/2025\\.br\\OPERATOR: Dr. Paul Drummond, MD\\.br\\\\.br'
            '\\HEMODYNAMICS:\\.br\\LVEDP: 18 mmHg\\.br\\Aortic pressure: 130/75 mmHg\\.br\\\\.br\\CORONARY ANGIOGRAPHY:\\.br\\Left main: No significant disea'
            'se\\.br\\LAD: 90% stenosis proximal segment\\.br\\LCx: 30% stenosis mid segment\\.br\\RCA: 50% stenosis mid segment\\.br\\\\.br\\INTERVENTION:\\'
            '.br\\PCI to proximal LAD with drug-eluting stent (3.0 x 18mm) deployed at 14 atm.\\.br\\Final result: 0% residual stenosis, TIMI 3 flow.\\.br\\'
            '\\.br\\IMPRESSION:\\.br\\Significant single-vessel CAD with successful PCI to LAD.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250405133000'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_MPI')
        msh.sending_facility = HD(hd_1='UT_HEALTH_SA')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='UTHS_ENGINE')
        msh.date_time_of_message = '20250408083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'CLF20250408001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250408083000'
        evn.evn_5 = 'HIM01^LANGFORD^APRIL^D^^^HIM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50001234', cx_4='UT_HEALTH_SA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FUENTES', xpn_2='Ricardo', xpn_3='Emilio', xpn_5='Mr.')
        pid.date_time_of_birth = '19710930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4218 Callaghan Rd', xad_3='San Antonio', xad_4='TX', xad_5='78228', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5478831'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN50001999', cx_4='UT_HEALTH_SA', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='FUENTES', xpn_2='Ricardo', xpn_3='E')

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LAB')
        msh.sending_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='PARKLAND_ENGINE')
        msh.date_time_of_message = '20250410150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CLF20250410001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50112345', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GAINES', xpn_2='Latasha', xpn_3='Denise', xpn_5='Ms.')
        pid.date_time_of_birth = '19770813'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4715 Cedar Springs Rd', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5517340'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='PARKLAND', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='5566778', cwe_2='ASHWORTH', cwe_3='GREGORY', cwe_4='R', cwe_7='MD')
        pv1.pv1_20 = 'V50112345^^^PARKLAND^VN'
        pv1.charge_price_indicator = CWE(cwe_1='MEDICAID')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='SUNQUEST')
        orc.filler_order_number = EI(ei_1='MIC801234', ei_2='SUNQUEST')
        orc.orc_7 = '^^^20250407^^R'
        orc.date_time_of_order_event = '20250410150000'
        orc.orc_12 = '5566778^ASHWORTH^GREGORY^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='SUNQUEST')
        obr.filler_order_number = EI(ei_1='MIC801234', ei_2='SUNQUEST')
        obr.universal_service_identifier = CWE(cwe_1='87081', cwe_2='CULTURE AEROBIC', cwe_3='CPT')
        obr.observation_date_time = '20250407100000'
        obr.relevant_clinical_information = CWE(cwe_1='BLOOD')
        obr.placer_field_1 = '5566778^ASHWORTH^GREGORY^R^^^MD'
        obr.diagnostic_serv_sect_id = '20250410145000'
        obr.obr_27 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='BACTERIA IDENTIFIED', cwe_3='LN')
        obx.obx_5 = 'METHICILLIN-RESISTANT STAPHYLOCOCCUS AUREUS (MRSA)'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250410120000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-5', cwe_2='COLONY COUNT', cwe_3='LN')
        obx_2.obx_5 = 'GROWTH IN 2 OF 2 BOTTLES'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250410120000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18900-0', cwe_2='VANCOMYCIN', cwe_3='LN')
        obx_3.obx_5 = 'S^Susceptible'
        obx_3.reference_range = 'MIC <= 2'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250410130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18903-4', cwe_2='DAPTOMYCIN', cwe_3='LN')
        obx_4.obx_5 = 'S^Susceptible'
        obx_4.reference_range = 'MIC <= 1'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250410130000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18928-1', cwe_2='TRIMETHOPRIM-SULFAMETHOXAZOLE', cwe_3='LN')
        obx_5.obx_5 = 'S^Susceptible'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250410130000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18897-8', cwe_2='LINEZOLID', cwe_3='LN')
        obx_6.obx_5 = 'S^Susceptible'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250410130000'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_REG')
        msh.sending_facility = HD(hd_1='HENDRICK_ABILENE')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='HENDRICK_ENGINE')
        msh.date_time_of_message = '20250412100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'CLF20250412001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250412100000'
        evn.evn_5 = 'REG03^NORTHCUTT^DENISE^A^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN50123456', cx_4='HENDRICK', cx_5='MR'), CX(cx_1='615-82-9437', cx_4='USSSA', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='BLEDSOE', xpn_2='Garrett', xpn_3='Allen', xpn_5='Mr.')
        pid.date_time_of_birth = '19900308'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2410 Barrow St', xad_3='Abilene', xad_4='TX', xad_5='79605', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^325^5437218'
        pid.pid_14 = '^WPN^PH^^^325^5437219'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '615-82-9437'
        pid.birth_place = 'N^Non-Hispanic^HL70189'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'HENDRICK MEDICAL CENTER^^33333'
        pd1.pd1_4 = '6677889^WENTWORTH^THOMAS^E^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BLEDSOE', xpn_2='Suzanne', xpn_3='Marie', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='2410 Barrow St', xad_3='Abilene', xad_4='TX', xad_5='79605', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^325^5437220'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_PATH')
        msh.sending_facility = HD(hd_1='MD_ANDERSON')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='MDACC_ENGINE')
        msh.date_time_of_message = '20250415160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CLF20250415001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50134567', cx_4='MDACC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WHITFIELD', xpn_2='Constance', xpn_3='Elaine', xpn_5='Mrs.')
        pid.date_time_of_birth = '19600925'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='7203 Almeda Rd', xad_3='Houston', xad_4='TX', xad_5='77054', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5546130'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='405', pl_3='A', pl_4='MDACC', pl_8='SURGICAL_ONC')
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='7788990', cwe_2='LINDSTROM', cwe_3='DALE', cwe_4='T', cwe_7='MD', cwe_8='SURGEON')
        pv1.pv1_20 = 'V50134567^^^MDACC^VN'
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
        orc.placer_order_number = EI(ei_1='PATH901234', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='PATH901234', ei_2='PATH_SYS')
        orc.orc_7 = '^^^20250412^^R'
        orc.date_time_of_order_event = '20250415160000'
        orc.orc_12 = '7788990^LINDSTROM^DALE^T^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH901234', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='PATH901234', ei_2='PATH_SYS')
        obr.universal_service_identifier = CWE(cwe_1='88309', cwe_2='SURGICAL PATHOLOGY LEVEL VI', cwe_3='CPT')
        obr.observation_date_time = '20250412140000'
        obr.obr_16 = '7788990^LINDSTROM^DALE^T^^^MD'
        obr.results_rpt_status_chng_date_time = '20250415155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Surgical Pathology Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDIg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDExOCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjcyIDcyMCBUZAooU3VyZ2ljYWwgUGF0aG9sb2d5IFJlcG9ydCkgVGoKMCAyNCBUZAov'
            'RjEgMTIgVGYKKENvbG9uIFJlc2VjdGlvbjogTW9kZXJhdGVseSBkaWZmZXJlbnRpYXRlZCBhZGVub2NhcmNpbm9tYSkgVGoKMCAyNCBUZAooU3RhZ2U6IHBUMk4xTTAgLSBTdGFnZSBJ'
            'SUlBKSBUagpFVAplbmRzdHJlYW0KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250415155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='22637-3', cwe_2='PATHOLOGY REPORT FINAL', cwe_3='LN')
        obx_2.obx_5 = (
            'SPECIMEN: Colon, right hemicolectomy\\.br\\\\.br\\GROSS: 22 cm segment of right colon with attached appendix.\\.br\\Mass: 4.5 x 3.8 cm ulcerated'
            ' mass in cecum.\\.br\\\\.br\\MICROSCOPIC:\\.br\\Tumor type: Adenocarcinoma, moderately differentiated\\.br\\Depth of invasion: Through musculari'
            's propria into pericolonic fat (pT3)\\.br\\Margins: Proximal 8 cm, Distal 12 cm - both negative\\.br\\Lymph nodes: 2 of 18 positive for metastat'
            'ic carcinoma (pN1b)\\.br\\Lymphovascular invasion: Present\\.br\\Perineural invasion: Not identified\\.br\\\\.br\\ANCILLARY:\\.br\\MSI: Microsat'
            'ellite stable (MSS)\\.br\\KRAS: Wild type\\.br\\BRAF: Wild type\\.br\\\\.br\\STAGE: pT3N1bM0 - Stage IIIB'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250415155000'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC_ORD')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_HOUSTON')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='METH_H_ENGINE')
        msh.date_time_of_message = '20250418091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CLF20250418001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50145678', cx_4='METHODIST_HOUSTON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOSLEY', xpn_2='DeShawn', xpn_3='Lamar', xpn_5='Mr.')
        pid.date_time_of_birth = '19720915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4519 Wheeler Ave', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5528471'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5EAST', pl_2='512', pl_3='A', pl_4='METHODIST_HOUSTON', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='8899001', cwe_2='FORSYTHE', cwe_3='DENISE', cwe_4='R', cwe_7='MD')
        pv1.pv1_20 = 'V50145678^^^METHODIST_HOUSTON^VN'
        pv1.charge_price_indicator = CWE(cwe_1='UNITED')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CA'
        orc.placer_order_number = EI(ei_1='ORD801234', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='LAB901234', ei_2='LAB_SYS')
        orc.orc_7 = '^^^20250418080000^^R'
        orc.date_time_of_order_event = '20250418091500'
        orc.orc_12 = '8899001^FORSYTHE^DENISE^R^^^MD'
        orc.enterers_location = PL(pl_1='5EAST', pl_2='512', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='METHODIST_HOUSTON')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801234', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='LAB901234', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='83036', cwe_2='HEMOGLOBIN A1C', cwe_3='CPT')
        obr.observation_date_time = '20250418080000'
        obr.obr_16 = '8899001^FORSYTHE^DENISE^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20250418'
        obr.result_status = 'CA'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'CANCELLED - DUPLICATE ORDER, SEE ORD801200'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CRED_SYS')
        msh.sending_facility = HD(hd_1='BAYLOR_SCOTT_WHITE')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='BSW_ENGINE')
        msh.date_time_of_message = '20250420080000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'CLF20250420001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='PRACTITIONER MASTER FILE', cwe_3='HL70175')
        mfi.file_level_event_code = 'UPD^UPDATE^HL70178'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD'
        mfe.mfn_control_id = '20250420080000'
        mfe.mfe_4 = '9900112^BHATT^ANIL^K^^^MD'
        mfe.primary_key_value_type = 'CE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='9900112')
        stf.staff_identifier_list = CX(cx_1='U9900112', cx_4='BSW', cx_5='EI')
        stf.staff_name = XPN(xpn_1='BHATT', xpn_2='ANIL', xpn_3='K', xpn_5='MD', xpn_7='DR')
        stf.staff_type = CWE(cwe_1='RADIOLOGY')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19800515'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_6='254', cwe_7='5439018')
        stf.stf_10 = '3401 S 31st St^^Temple^TX^76508^US^B'
        stf.backup_person_id = CWE(cwe_1='BAYLOR SCOTT AND WHITE HEALTH')

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='9900112')
        pra.practitioner_group = CWE(cwe_1='BAYLOR SCOTT AND WHITE')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='INSTITUTION', cwe_3='HL70186')
        pra.provider_billing = 'G^GROUP^HL70187'
        pra.practitioner_id_numbers = PLN(pln_1='2085R0202X', pln_2='DIAGNOSTIC RADIOLOGY', pln_3='NUCC')
        pra.privileges = PIP(pip_1='TX', pip_2='TEXAS')
        pra.date_entered_practice = 'TXM789012^TEXAS MEDICAL BOARD'

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
    """ Based on live/us-texas/us-texas-cloverleaf.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLOVERLEAF')
        msh.sending_facility = HD(hd_1='UTHS_ENGINE')
        msh.receiving_application = HD(hd_1='EPIC_ADT')
        msh.receiving_facility = HD(hd_1='UT_HEALTH_SA')
        msh.date_time_of_message = '20250305120005'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'CLFACK20250305001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'CLF20250305001'
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

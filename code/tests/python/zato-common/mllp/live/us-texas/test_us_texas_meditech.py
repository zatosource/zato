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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, HD, MSG, PIP, PL, PLN, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, DftP03Visit, \
    MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, FT1, GT1, IN1, MFE, MFI, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PD1, PID, PRA, PV1, PV2, RGS, RXA, \
    RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-meditech.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-meditech.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_DALLAS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='DALLAS_HIE')
        msh.date_time_of_message = '20250312143022'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00012478'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312142900'
        evn.evn_5 = 'ASHFORD^Ashford^Julia^R^^^MD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN10234567', cx_4='METHODIST_DALLAS', cx_5='MR'), CX(cx_1='648-31-7205', cx_4='USSSA', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='Elena', xpn_5='Mrs.')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5559823'
        pid.pid_14 = '^WPN^PH^^^214^5551234'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '648-31-7205'
        pid.birth_place = 'H^Hispanic^HL70189'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'METHODIST DALLAS MEDICAL CENTER^^12345'
        pd1.pd1_4 = '1830246791^BANCROFT^DAVID^H^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='ELIZONDO', xpn_2='Roberto', xpn_3='Javier', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^214^5559824'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='412', pl_3='A', pl_4='METHODIST_DALLAS', pl_8='MEDSURG')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.prior_patient_location = PL(pl_1='4EAST', pl_2='410', pl_3='B')
        pv1.pv1_7 = '7654321^CHANDLER^CARLOS^A^^^MD^ATTENDING'
        pv1.pv1_8 = '8765432^DEVEREAUX^ANITA^S^^^MD^ADMITTING'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='7654321', cwe_2='CHANDLER', cwe_3='CARLOS', cwe_4='A', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V10203040', cwe_4='METHODIST_DALLAS', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BCBS')
        pv1.diet_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20250312142900')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain, rule out MI')
        pv2.actual_length_of_inpatient_stay = '3'
        pv2.visit_protection_indicator = 'N'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='001', cwe_2='BCBS OF TEXAS')
        in1.insurance_company_id = CX(cx_1='BCBS001')
        in1.insurance_company_name = XON(xon_1='BLUE CROSS BLUE SHIELD OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 660044', xad_3='Dallas', xad_4='TX', xad_5='75266', xad_6='US')
        in1.group_number = 'GRP12345'
        in1.plan_effective_date = '20240101'
        in1.name_of_insured = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='Elena')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19670415'
        in1.insureds_address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US')
        in1.policy_number = 'XYZ987654321'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I20.9', cwe_2='Angina pectoris, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='Elena', xpn_5='Mrs.')
        gt1.guarantor_address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US')
        gt1.guarantor_ph_num_home = XTN(xtn_2='PRN', xtn_3='PH', xtn_6='214', xtn_7='5559823')
        gt1.guarantor_relationship = CWE(cwe_1='SE', cwe_2='Self')

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
        msg.extra_segments = [dg1, gt1]

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_DALLAS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='DALLAS_HIE')
        msh.date_time_of_message = '20250315101530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00012901'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250315101500'
        evn.evn_5 = 'ASHFORD^Ashford^Julia^R^^^MD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN10234567', cx_4='METHODIST_DALLAS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='Elena', xpn_5='Mrs.')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5559823'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='412', pl_3='A', pl_4='METHODIST_DALLAS', pl_8='MEDSURG')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.prior_patient_location = PL(pl_1='4EAST', pl_2='410', pl_3='B')
        pv1.pv1_7 = '7654321^CHANDLER^CARLOS^A^^^MD^ATTENDING'
        pv1.pv1_8 = '8765432^DEVEREAUX^ANITA^S^^^MD^ADMITTING'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='7654321', cwe_2='CHANDLER', cwe_3='CARLOS', cwe_4='A', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V10203040', cwe_4='METHODIST_DALLAS', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BCBS')
        pv1.diet_type = CWE(cwe_1='DIS')
        pv1.prior_temporary_location = PL(pl_1='20250312142900')
        pv1.discharge_date_time = '20250315101500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain resolved')
        pv2.actual_length_of_inpatient_stay = '3'
        pv2.visit_protection_indicator = 'N'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I20.9', cwe_2='Angina pectoris, unspecified', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain, unspecified', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HARRIS_HEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='HARRIS_LAB')
        msh.date_time_of_message = '20250320083045'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00098234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN20345678', cx_4='HARRIS_HEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FLAGG', xpn_2='William', xpn_3='Thomas', xpn_5='Mr.')
        pid.date_time_of_birth = '19520823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1200 Moursund St', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5553456'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU2', pl_2='201', pl_3='A', pl_4='HARRIS_HEALTH', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '4567890^ELLSWORTH^SARAH^M^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4567890', cwe_2='ELLSWORTH', cwe_3='SARAH', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V20304050', xcn_4='HARRIS_HEALTH', xcn_5='VN')
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
        orc.placer_order_number = EI(ei_1='ORD789012', ei_2='MEDITECH')
        orc.orc_7 = '^^^20250320090000^^R'
        orc.date_time_of_order_event = '20250320083045'
        orc.orc_10 = 'TNURSE01^FORSYTHE^TINA^L^^^RN'
        orc.orc_12 = '4567890^ELLSWORTH^SARAH^M^^^MD'
        orc.enterers_location = PL(pl_1='ICU2', pl_2='201', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='HARRIS_HEALTH')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD789012', ei_2='MEDITECH')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250320083000'
        obr.obr_16 = '4567890^ELLSWORTH^SARAH^M^^^MD'
        obr.results_rpt_status_chng_date_time = '20250320090000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N17.9', cwe_2='Acute kidney failure, unspecified', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HARRIS_HEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='RESULT_RECV')
        msh.receiving_facility = HD(hd_1='HARRIS_HEALTH')
        msh.date_time_of_message = '20250320112034'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00098456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN20345678', cx_4='HARRIS_HEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FLAGG', xpn_2='William', xpn_3='Thomas', xpn_5='Mr.')
        pid.date_time_of_birth = '19520823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1200 Moursund St', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5553456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU2', pl_2='201', pl_3='A', pl_4='HARRIS_HEALTH', pl_8='MICU')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '4567890^ELLSWORTH^SARAH^M^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4567890', cwe_2='ELLSWORTH', cwe_3='SARAH', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V20304050', xcn_4='HARRIS_HEALTH', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD789012', ei_2='MEDITECH')
        orc.filler_order_number = EI(ei_1='RES456789', ei_2='LAB_SYS')
        orc.orc_7 = '^^^20250320090000^^R'
        orc.date_time_of_order_event = '20250320112034'
        orc.orc_12 = '4567890^ELLSWORTH^SARAH^M^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD789012', ei_2='MEDITECH')
        obr.filler_order_number = EI(ei_1='RES456789', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='CPT')
        obr.observation_date_time = '20250320083000'
        obr.obr_16 = '4567890^ELLSWORTH^SARAH^M^^^MD'
        obr.results_rpt_status_chng_date_time = '20250320112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='SODIUM', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136-145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='POTASSIUM', cwe_3='LN')
        obx_2.obx_5 = '6.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='CHLORIDE', cwe_3='LN')
        obx_3.obx_5 = '101'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98-106'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2028-9', cwe_2='CO2', cwe_3='LN')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '23-29'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_5.obx_5 = '45'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '7-20'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obx_6.obx_5 = '3.8'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '0.7-1.3'
        obx_6.interpretation_codes = CWE(cwe_1='HH')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2345-7', cwe_2='GLUCOSE', cwe_3='LN')
        obx_7.obx_5 = '112'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '70-100'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250320110000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='17861-6', cwe_2='CALCIUM', cwe_3='LN')
        obx_8.obx_5 = '8.9'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '8.5-10.5'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250320110000'

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='BAYLOR_SCOTT_WHITE')
        msh.receiving_application = HD(hd_1='PATH_RECV')
        msh.receiving_facility = HD(hd_1='BSW_EMR')
        msh.date_time_of_message = '20250401154500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00103456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30456789', cx_4='BSW_TEMPLE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CAVAZOS', xpn_2='Carmen', xpn_3='Isabel', xpn_5='Ms.')
        pid.date_time_of_birth = '19780903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2901 S 31st St', xad_3='Temple', xad_4='TX', xad_5='76508', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^254^5557890'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATHLAB', pl_2='001', pl_3='A', pl_4='BSW_TEMPLE', pl_8='OUTPATH')
        pv1.hospital_service = CWE(cwe_1='PATH')
        pv1.patient_type = CWE(cwe_1='3456789', cwe_2='GLENDALE', cwe_3='MICHAEL', cwe_4='W', cwe_7='MD')
        pv1.pv1_20 = 'V30405060^^^BSW_TEMPLE^VN'

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
        orc.placer_order_number = EI(ei_1='ORD890123', ei_2='MEDITECH')
        orc.filler_order_number = EI(ei_1='PATH567890', ei_2='PATH_SYS')
        orc.orc_7 = '^^^20250328^^R'
        orc.date_time_of_order_event = '20250401154500'
        orc.orc_12 = '3456789^GLENDALE^MICHAEL^W^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD890123', ei_2='MEDITECH')
        obr.filler_order_number = EI(ei_1='PATH567890', ei_2='PATH_SYS')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='SURGICAL PATHOLOGY', cwe_3='CPT')
        obr.observation_date_time = '20250328100000'
        obr.obr_16 = '3456789^GLENDALE^MICHAEL^W^^^MD'
        obr.results_rpt_status_chng_date_time = '20250401150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDQ0ID4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooUGF0aG9sb2d5IFJlcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iag=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250401150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='22634-0', cwe_2='PATHOLOGY REPORT', cwe_3='LN')
        obx_2.obx_5 = (
            'SPECIMEN: Left breast, excisional biopsy\\.br\\DIAGNOSIS: Invasive ductal carcinoma, Grade 2\\.br\\Tumor size: 1.8 cm\\.br\\Margins: Negative (c'
            'losest 0.3 cm)\\.br\\Lymphovascular invasion: Not identified\\.br\\ER: Positive (95%)\\.br\\PR: Positive (80%)\\.br\\HER2: Negative (1+)'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250401150000'

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='CHRISTUS_SPOHN_CC')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='CORPUS_HIE')
        msh.date_time_of_message = '20250405091234'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00104567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250405091200'
        evn.evn_5 = 'ADMIN01^HARGROVE^KAREN^A^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40567890', cx_4='CHRISTUS_SPOHN', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PHAM', xpn_2='Nguyen', xpn_3='Thanh', xpn_5='Mr.')
        pid.date_time_of_birth = '19850211'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='8901 Ocean Dr', xad_3='Corpus Christi', xad_4='TX', xad_5='78404', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^361^5554321'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3NORTH', pl_2='305', pl_3='B', pl_4='CHRISTUS_SPOHN', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='5678901', cwe_2='KIRKWOOD', cwe_3='ELENA', cwe_4='P', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V40506070', cwe_4='CHRISTUS_SPOHN', cwe_5='VN')
        pv1.visit_number = CX(cx_1='AETNA')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='002', cwe_2='AETNA')
        in1.insurance_company_id = CX(cx_1='AET001')
        in1.insurance_company_name = XON(xon_1='AETNA HEALTH OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 14079', xad_3='Lexington', xad_4='KY', xad_5='40512', xad_6='US')
        in1.group_number = 'GRP67890'
        in1.plan_effective_date = '20250401'
        in1.name_of_insured = XPN(xpn_1='PHAM', xpn_2='Nguyen', xpn_3='Thanh')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19850211'
        in1.insureds_address = XAD(xad_1='8901 Ocean Dr', xad_3='Corpus Christi', xad_4='TX', xad_5='78404', xad_6='US')
        in1.policy_number = 'AET123456789'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build IN1 ..
        in1_2 = IN1()
        in1_2.set_id_in1 = '2'
        in1_2.health_plan_id = CWE(cwe_1='001', cwe_2='BCBS OF TEXAS')
        in1_2.insurance_company_id = CX(cx_1='BCBS001')
        in1_2.insurance_company_name = XON(xon_1='BLUE CROSS BLUE SHIELD OF TEXAS')
        in1_2.insurance_company_address = XAD(xad_1='P.O. Box 660044', xad_3='Dallas', xad_4='TX', xad_5='75266', xad_6='US')
        in1_2.group_number = 'GRP12345'
        in1_2.plan_effective_date = '20230101'
        in1_2.plan_expiration_date = '20250331'
        in1_2.name_of_insured = XPN(xpn_1='PHAM', xpn_2='Nguyen', xpn_3='Thanh')
        in1_2.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1_2.insureds_date_of_birth = '19850211'
        in1_2.insureds_address = XAD(xad_1='8901 Ocean Dr', xad_3='Corpus Christi', xad_4='TX', xad_5='78404', xad_6='US')
        in1_2.policy_number = 'BCBS987654'

        # .. build the INSURANCE group ..
        insurance_2 = AdtA01Insurance()
        insurance_2.in1 = in1_2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = [insurance, insurance_2]

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='UT_SOUTHWESTERN')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='UTSW_CLINIC')
        msh.date_time_of_message = '20250410140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00105678'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT901234', ei_2='MEDITECH')
        sch.filler_appointment_id = EI(ei_1='APT901234', ei_2='MEDITECH')
        sch.schedule_id = CWE(cwe_1='CARDCON', cwe_2='Cardiology Consultation', cwe_3='LOCAL')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='30', cwe_2='MIN')
        sch.appointment_type = CWE(cwe_1='1')
        sch.appointment_duration_units = CNE(cne_1='BOOKED')
        sch.sch_16 = '6789012^LANGFORD^RAJESH^K^^^MD^CARDIOLOGIST'
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_6='214', xtn_7='5556789')
        sch.filler_contact_address = XAD(xad_1='5323 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75390', xad_6='US')
        sch.parent_placer_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50678901', cx_4='UTSW', cx_5='MR')
        pid.patient_name = XPN(xpn_1='AINSWORTH', xpn_2='James', xpn_3='Edward', xpn_5='Mr.')
        pid.date_time_of_birth = '19600917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='7234 Greenville Ave', xad_3='Dallas', xad_4='TX', xad_5='75231', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5558901'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDCLIN', pl_2='EXAM3', pl_3='A', pl_4='UTSW', pl_8='CARDIOLOGY')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.patient_type = CWE(cwe_1='6789012', cwe_2='LANGFORD', cwe_3='RAJESH', cwe_4='K', cwe_7='MD')
        pv1.pv1_20 = 'V50607080^^^UTSW^VN'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='CARDCON')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CARDCON', cwe_2='Cardiology Consultation', cwe_3='LOCAL')
        ais.start_date_time = '20250425093000'
        ais.duration = '30^MIN'
        ais.duration_units = CNE(cne_1='30', cne_2='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '6789012^LANGFORD^RAJESH^K^^^MD'
        aip.resource_type = CWE(cwe_1='ATTENDING')
        aip.resource_group = CWE(cwe_1='20250425093000')
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
        ail.location_resource_id = PL(pl_1='CARDCLIN', pl_2='EXAM3', pl_3='A', pl_4='UTSW')
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_SA')
        msh.receiving_application = HD(hd_1='PHARM_SYS')
        msh.receiving_facility = HD(hd_1='METH_SA_PHARM')
        msh.date_time_of_message = '20250412080045'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MSG00106789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60789012', cx_4='METHODIST_SA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BARRERA', xpn_2='Antonio', xpn_3='Miguel', xpn_5='Mr.')
        pid.date_time_of_birth = '19750308'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5430 Fredericksburg Rd', xad_3='San Antonio', xad_4='TX', xad_5='78229', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^210^5552345'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5WEST', pl_2='502', pl_3='A', pl_4='METHODIST_SA', pl_8='CARDIAC')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.pv1_7 = '7890123^MERIWETHER^CHIBUEZE^N^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='7890123', cwe_2='MERIWETHER', cwe_3='CHIBUEZE', cwe_4='N', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V60708090', xcn_4='METHODIST_SA', xcn_5='VN')

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
        orc.placer_order_number = EI(ei_1='RX901234', ei_2='MEDITECH')
        orc.orc_7 = '^^^20250412080000^^R'
        orc.date_time_of_order_event = '20250412080045'
        orc.orc_10 = 'RNURSE02^NORTHCUTT^PATRICIA^M^^^RN'
        orc.orc_12 = '7890123^MERIWETHER^CHIBUEZE^N^^^MD'
        orc.enterers_location = PL(pl_1='5WEST', pl_2='502', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='METHODIST_SA')

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^BID^^20250412080000^20250419080000'
        rxe.give_code = CWE(cwe_1='6918', cwe_2='METOPROLOL TARTRATE 50MG TAB', cwe_3='NDC')
        rxe.give_amount_minimum = '50'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70484')
        rxe.number_of_refills = '14'
        rxe.give_strength_units = CWE(cwe_1='BID', cwe_2='Twice daily')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='PARKLAND_DALLAS')
        msh.receiving_application = HD(hd_1='FIN_SYS')
        msh.receiving_facility = HD(hd_1='PARKLAND_BILLING')
        msh.date_time_of_message = '20250415163022'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'MSG00107890'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20250415163022'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN70890123', cx_4='PARKLAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GRESHAM', xpn_2='Deborah', xpn_3='Ann', xpn_5='Ms.')
        pid.date_time_of_birth = '19880621'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3200 Martin Luther King Jr Blvd', xad_3='Dallas', xad_4='TX', xad_5='75215', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5553456'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='TRAUMA3', pl_3='A', pl_4='PARKLAND', pl_8='ED')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency')
        pv1.pv1_7 = '8901234^PEMBERTON^JENNIFER^H^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='8901234', cwe_2='PEMBERTON', cwe_3='JENNIFER', cwe_4='H', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V70809010', xcn_4='PARKLAND', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICAID')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20250415')
        ft1.transaction_batch_id = '20250415163000'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = '99284^ED VISIT LEVEL 4^CPT'
        ft1.transaction_type = CWE(cwe_1='99284', cwe_2='ED VISIT LEVEL 4', cwe_3='CPT')
        ft1.ft1_8 = '1'
        ft1.ft1_11 = '8901234^PEMBERTON^JENNIFER^H^^^MD'
        ft1.ordered_by_code = XCN(xcn_1='99284')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20250415')
        ft1_2.transaction_batch_id = '20250415155000'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = '71046^CHEST X-RAY 2 VIEWS^CPT'
        ft1_2.transaction_type = CWE(cwe_1='71046', cwe_2='CHEST X-RAY 2 VIEWS', cwe_3='CPT')
        ft1_2.ft1_8 = '1'
        ft1_2.ft1_11 = '8901234^PEMBERTON^JENNIFER^H^^^MD'
        ft1_2.ordered_by_code = XCN(xcn_1='71046')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20250415')
        ft1_3.transaction_batch_id = '20250415160000'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = '93010^ECG INTERPRETATION^CPT'
        ft1_3.transaction_type = CWE(cwe_1='93010', cwe_2='ECG INTERPRETATION', cwe_3='CPT')
        ft1_3.ft1_8 = '1'
        ft1_3.ft1_11 = '8901234^PEMBERTON^JENNIFER^H^^^MD'
        ft1_3.ordered_by_code = XCN(xcn_1='93010')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain, unspecified', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='COOK_CHILDRENS_FW')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TXDSHS')
        msh.date_time_of_message = '20250420101500'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'MSG00108901'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN80901234', cx_4='COOK_CHILDRENS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SALDANA', xpn_2='Sofia', xpn_3='Rose', xpn_5='')
        pid.date_time_of_birth = '20200115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4500 Camp Bowie Blvd', xad_3='Fort Worth', xad_4='TX', xad_5='76107', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^817^5554567'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = "COOK CHILDREN'S MEDICAL CENTER^^67890"
        pd1.pd1_4 = '9012345^QUINLAN^PRIYA^A^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SALDANA', xpn_2='Diego', xpn_3='Luis', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4500 Camp Bowie Blvd', xad_3='Fort Worth', xad_4='TX', xad_5='76107', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^817^5554567'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='IMM345678', ei_2='MEDITECH')
        orc.orc_12 = '9012345^QUINLAN^PRIYA^A^^^MD'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20250420101000'
        rxa.date_time_end_of_administration = '20250420101100'
        rxa.administered_code = CWE(cwe_1='308', cwe_2='HEP B PEDIATRIC', cwe_3='CVX')
        rxa.administered_amount = '0.5'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliter', cwe_3='UCUM')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='NEW IMMUNIZATION RECORD', cwe_3='NIP001')
        rxa.rxa_10 = '9012345^QUINLAN^PRIYA^A^^^MD'
        rxa.rxa_15 = '49281001210^ENGERIX-B^NDC'
        rxa.substance_expiration_date = 'MSD'
        rxa.system_entry_date_time = 'CP'
        rxa.administered_drug_strength_volume = 'A'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RT', cwe_2='Right Thigh', cwe_3='HL70163')

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
        obx_2.obx_5 = '45^HEP B^CVX'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation
        order.observation_2 = observation_2

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HENDRICK_ABILENE')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='HENDRICK_HIM')
        msh.date_time_of_message = '20250422134500'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00109012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250422134500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN91012345', cx_4='HENDRICK', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BEAUCHAMP', xpn_2='Charles', xpn_3='Robert', xpn_5='Mr.')
        pid.date_time_of_birth = '19450712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1234 Sayles Blvd', xad_3='Abilene', xad_4='TX', xad_5='79605', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^325^5556789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2SOUTH', pl_2='210', pl_3='A', pl_4='HENDRICK', pl_8='MEDSURG')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.vip_indicator = CWE(cwe_1='0123456', cwe_2='RIDGEMONT', cwe_3='PATRICIA', cwe_4='D', cwe_7='MD')
        pv1.patient_type = CWE(cwe_1='V80901020', cwe_4='HENDRICK', cwe_5='VN')
        pv1.visit_number = CX(cx_1='MEDICARE')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='DISCHARGE SUMMARY', cwe_3='HL70270')
        txa.document_content_presentation = 'FT^Full Text^HL70191'
        txa.activity_date_time = '20250422130000'
        txa.origination_date_time = '20250422134500'
        txa.txa_11 = '0123456^RIDGEMONT^PATRICIA^D^^^MD'
        txa.unique_document_number = EI(ei_1='DOC789012')
        txa.document_confidentiality_status = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='DISCHARGE SUMMARY', cwe_3='LN')
        obx.obx_5 = (
            'ADMISSION DATE: 04/18/2025\\.br\\DISCHARGE DATE: 04/22/2025\\.br\\\\.br\\ADMITTING DIAGNOSIS: Community-acquired pneumonia\\.br\\\\.br\\HOSPITAL'
            ' COURSE:\\.br\\Patient admitted with fever, productive cough, and right lower lobe consolidation on chest X-ray. Started on IV ceftriaxone and'
            ' azithromycin. Blood cultures negative. Clinically improved by day 3, transitioned to oral antibiotics.\\.br\\\\.br\\DISCHARGE DIAGNOSIS: Commun'
            'ity-acquired pneumonia, resolved\\.br\\\\.br\\DISCHARGE MEDICATIONS:\\.br\\1. Amoxicillin 875mg PO BID x 5 days\\.br\\2. Guaifenesin 600mg PO Q1'
            '2H PRN\\.br\\\\.br\\FOLLOW-UP: PCP in 7-10 days'
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='SHANNON_SAN_ANGELO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='SHANNON_REG')
        msh.date_time_of_message = '20250425070030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00110123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250425070000'
        evn.evn_5 = 'REG01^STANDISH^MICHELLE^R^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN01123456', cx_4='SHANNON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CRAWFORD', xpn_2='Linda', xpn_3='Marie', xpn_5='Mrs.')
        pid.date_time_of_birth = '19710524'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='567 Knickerbocker Rd', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^325^5551234'
        pid.mothers_identifier = CX(cx_1='N', cx_2='Non-Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='SURGI', pl_2='OR2', pl_3='A', pl_4='SHANNON', pl_8='OPSURG')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Elective')
        pv1.pv1_7 = '1234567^THORNBURY^RICHARD^B^^^MD^SURGEON'
        pv1.ambulatory_status = CWE(cwe_1='1234567', cwe_2='THORNBURY', cwe_3='RICHARD', cwe_4='B', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V90102030', xcn_4='SHANNON', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='UNITED')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='003', cwe_2='UNITED HEALTHCARE')
        in1.insurance_company_id = CX(cx_1='UHC001')
        in1.insurance_company_name = XON(xon_1='UNITED HEALTHCARE OF TEXAS')
        in1.insurance_company_address = XAD(xad_1='P.O. Box 740800', xad_3='Atlanta', xad_4='GA', xad_5='30374', xad_6='US')
        in1.group_number = 'GRP34567'
        in1.plan_effective_date = '20240601'
        in1.name_of_insured = XPN(xpn_1='CRAWFORD', xpn_2='Linda', xpn_3='Marie')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL', cwe_2='Self')
        in1.insureds_date_of_birth = '19710524'
        in1.insureds_address = XAD(xad_1='567 Knickerbocker Rd', xad_3='San Angelo', xad_4='TX', xad_5='76904', xad_6='US')
        in1.policy_number = 'UHC567890123'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.20', cwe_2='Calculus of gallbladder without cholecystitis', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HARRIS_HEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HARRIS_BED_MGMT')
        msh.date_time_of_message = '20250426153045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00111234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250426153000'
        evn.evn_5 = 'CHARGE01^WHITFIELD^AMY^K^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN20345678', cx_4='HARRIS_HEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FLAGG', xpn_2='William', xpn_3='Thomas', xpn_5='Mr.')
        pid.date_time_of_birth = '19520823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1200 Moursund St', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^713^5553456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STEPDN', pl_2='401', pl_3='A', pl_4='HARRIS_HEALTH', pl_8='STEPDOWN')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.preadmit_number = CX(cx_1='ICU2', cx_2='201', cx_3='A', cx_4='HARRIS_HEALTH', cx_8='MICU')
        pv1.pv1_7 = '4567890^ELLSWORTH^SARAH^M^^^MD^ATTENDING'
        pv1.ambulatory_status = CWE(cwe_1='4567890', cwe_2='ELLSWORTH', cwe_3='SARAH', cwe_4='M', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='V20304050', xcn_4='HARRIS_HEALTH', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='MEDICARE')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute kidney injury, improving')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='SETON_AUSTIN')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='SETON_EMR')
        msh.date_time_of_message = '20250428091200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00112345'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN11234567', cx_4='SETON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DONOVAN', xpn_2='Robert', xpn_3='Allen', xpn_5='Mr.')
        pid.date_time_of_birth = '19630119'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='8800 Research Blvd', xad_3='Austin', xad_4='TX', xad_5='78758', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^512^5559012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIOL', pl_2='CT1', pl_3='A', pl_4='SETON', pl_8='RADIOLOGY')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='2345678', cwe_2='STRATTON', cwe_3='SUNG', cwe_4='J', cwe_7='MD', cwe_8='RADIOLOGIST')
        pv1.pv1_20 = 'V01203040^^^SETON^VN'

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
        orc.placer_order_number = EI(ei_1='ORD012345', ei_2='MEDITECH')
        orc.filler_order_number = EI(ei_1='RAD678901', ei_2='RAD_SYS')
        orc.orc_7 = '^^^20250427^^R'
        orc.date_time_of_order_event = '20250428091200'
        orc.orc_12 = '2345678^STRATTON^SUNG^J^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD012345', ei_2='MEDITECH')
        obr.filler_order_number = EI(ei_1='RAD678901', ei_2='RAD_SYS')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT ABDOMEN AND PELVIS WITH CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250427141500'
        obr.obr_16 = '2345678^STRATTON^SUNG^J^^^MD'
        obr.results_rpt_status_chng_date_time = '20250428090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvUmVzb3VyY2VzIDQgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50cyA2IDAgUiA+'
            'PgplbmRvYmoKNiAwIG9iago8PCAvTGVuZ3RoIDUwID4+CnN0cmVhbQpCVAovRjEgMTQgVGYKNzIgNzIwIFRkCihDVCBBYmRvbWVuIGFuZCBQZWx2aXMgUmVwb3J0KSBUagpFVAplbmRz'
            'dHJlYW0KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250428090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='DIAGNOSTIC IMAGING REPORT', cwe_3='LN')
        obx_2.obx_5 = (
            'EXAM: CT Abdomen and Pelvis with IV Contrast\\.br\\\\.br\\CLINICAL INDICATION: Abdominal pain, rule out appendicitis\\.br\\\\.br\\FINDINGS:\\.br'
            '\\Liver, spleen, pancreas, adrenals: Unremarkable\\.br\\Kidneys: No hydronephrosis or stones\\.br\\Appendix: Normal caliber, no periappendiceal '
            'inflammation\\.br\\Bowel: No obstruction or wall thickening\\.br\\\\.br\\IMPRESSION:\\.br\\1. No acute intra-abdominal pathology\\.br\\2. No evi'
            'dence of appendicitis'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250428090000'

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='UTHEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='UTHEALTH_MPI')
        msh.date_time_of_message = '20250430100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00113456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250430100000'
        evn.evn_5 = 'REG02^WINSLOW^CAROL^S^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN12345678', cx_4='UTHEALTH', cx_5='MR'), CX(cx_1='714-52-8396', cx_4='USSSA', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='INGRAM', xpn_2='Chidimma', xpn_3='Adaeze', xpn_5='Ms.')
        pid.date_time_of_birth = '19920817'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3901 Fannin St', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^832^5556789'
        pid.pid_14 = '^WPN^PH^^^713^5550123'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '714-52-8396'
        pid.birth_place = 'N^Non-Hispanic^HL70189'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'UT PHYSICIANS^^99999'
        pd1.pd1_4 = '3456789^VANHORNE^CHIBUEZE^N^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='INGRAM', xpn_2='Emeka', xpn_3='Tobias', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3901 Fannin St', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^832^5556790'

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='METHODIST_HOSP_DALLAS')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='DALLAS_MPI')
        msh.date_time_of_message = '20250502083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00114567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250502083000'
        evn.evn_5 = 'ADMIN02^YARDLEY^JAMES^P^^^HIM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN10234567', cx_4='METHODIST_DALLAS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='Elena', xpn_5='Mrs.')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4521 Oaklawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^214^5559823'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN10234999', cx_4='METHODIST_DALLAS', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='ELIZONDO', xpn_2='Maria', xpn_3='E')

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='BAYLOR_SCOTT_WHITE')
        msh.receiving_application = HD(hd_1='RAD_SYS')
        msh.receiving_facility = HD(hd_1='BSW_RADIOLOGY')
        msh.date_time_of_message = '20250503110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00115678'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30456789', cx_4='BSW_TEMPLE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CAVAZOS', xpn_2='Carmen', xpn_3='Isabel', xpn_5='Ms.')
        pid.date_time_of_birth = '19780903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2901 S 31st St', xad_3='Temple', xad_4='TX', xad_5='76508', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^254^5557890'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='301', pl_3='A', pl_4='BSW_TEMPLE', pl_8='ONCOLOGY')
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='4567890', cwe_2='SUTCLIFFE', cwe_3='DAVID', cwe_4='W', cwe_7='MD', cwe_8='ONCOLOGIST')
        pv1.pv1_20 = 'V11203040^^^BSW_TEMPLE^VN'
        pv1.charge_price_indicator = CWE(cwe_1='AETNA')

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
        orc.placer_order_number = EI(ei_1='ORD234567', ei_2='MEDITECH')
        orc.orc_7 = '^^^20250503120000^^R'
        orc.date_time_of_order_event = '20250503110000'
        orc.orc_10 = 'RNURSE03^HALSTEAD^SANDRA^L^^^RN'
        orc.orc_12 = '4567890^SUTCLIFFE^DAVID^W^^^MD'
        orc.enterers_location = PL(pl_1='ONCO', pl_2='301', pl_3='A')
        orc.order_control_code_reason = CWE(cwe_1='BSW_TEMPLE')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD234567', ei_2='MEDITECH')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST WITH CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250503120000'
        obr.obr_16 = '4567890^SUTCLIFFE^DAVID^W^^^MD'
        obr.results_rpt_status_chng_date_time = '20250503120000'
        obr.result_status = 'F'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.90', cwe_2='Malignant neoplasm of unspecified part of bronchus or lung', cwe_3='ICD10')
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='COOK_CHILDRENS_FW')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='COOK_MPI')
        msh.date_time_of_message = '20250505141500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00116789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250505141500'
        evn.evn_5 = 'REG03^WAKEFIELD^BRENDA^K^^^REG'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN80901234', cx_4='COOK_CHILDRENS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SALDANA', xpn_2='Sofia', xpn_3='Rose', xpn_5='')
        pid.date_time_of_birth = '20200115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='6200 Hulen Bend Blvd', xad_3='Fort Worth', xad_4='TX', xad_5='76132', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^817^5558901'
        pid.mothers_identifier = CX(cx_1='H', cx_2='Hispanic', cx_3='HL70189')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = "COOK CHILDREN'S MEDICAL CENTER^^67890"
        pd1.pd1_4 = '9012345^QUINLAN^PRIYA^A^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SALDANA', xpn_2='Diego', xpn_3='Luis', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Father', cwe_3='HL70063')
        nk1.address = XAD(xad_1='6200 Hulen Bend Blvd', xad_3='Fort Worth', xad_4='TX', xad_5='76132', xad_6='US', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^^817^5558901'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='SALDANA', xpn_2='Ana', xpn_3='Carolina', xpn_5='Mrs.')
        nk1_2.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1_2.address = XAD(xad_1='6200 Hulen Bend Blvd', xad_3='Fort Worth', xad_4='TX', xad_5='76132', xad_6='US', xad_7='H')
        nk1_2.nk1_5 = '^PRN^PH^^^817^5558902'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA05NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = [next_of_kin, next_of_kin_2]

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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_RECV')
        msh.sending_facility = HD(hd_1='DALLAS_HIE')
        msh.receiving_application = HD(hd_1='MEDITECH')
        msh.receiving_facility = HD(hd_1='METHODIST_HOSP_DALLAS')
        msh.date_time_of_message = '20250312143025'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00012478'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00012478'
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
    """ Based on live/us-texas/us-texas-meditech.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HARRIS_HEALTH_HOUSTON')
        msh.receiving_application = HD(hd_1='MFN_RECV')
        msh.receiving_facility = HD(hd_1='HARRIS_CRED')
        msh.date_time_of_message = '20250506090000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'MSG00117890'
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
        mfe.mfn_control_id = '20250506090000'
        mfe.mfe_4 = '4567890^ELLSWORTH^SARAH^M^^^MD'
        mfe.primary_key_value_type = 'CE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='4567890')
        stf.staff_identifier_list = CX(cx_1='U4567890', cx_4='HARRIS_HEALTH', cx_5='EI')
        stf.staff_name = XPN(xpn_1='ELLSWORTH', xpn_2='SARAH', xpn_3='M', xpn_5='MD', xpn_7='DR')
        stf.staff_type = CWE(cwe_1='INTERNAL MEDICINE')
        stf.administrative_sex = CWE(cwe_1='F')
        stf.date_time_of_birth = '19750314'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_6='713', cwe_7='5559876')
        stf.stf_10 = '6431 Fannin St^^Houston^TX^77030^US^B'
        stf.backup_person_id = CWE(cwe_1='HARRIS HEALTH SYSTEM')

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='4567890')
        pra.practitioner_group = CWE(cwe_1='HARRIS HEALTH SYSTEM')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='INSTITUTION', cwe_3='HL70186')
        pra.provider_billing = 'G^GROUP^HL70187'
        pra.practitioner_id_numbers = PLN(pln_1='207R00000X', pln_2='INTERNAL MEDICINE', pln_3='NUCC')
        pra.privileges = PIP(pip_1='TX', pip_2='TEXAS')
        pra.date_entered_practice = 'TXM123456^TEXAS MEDICAL BOARD'

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

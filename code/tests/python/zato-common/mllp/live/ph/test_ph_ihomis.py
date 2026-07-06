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

_md_path = md_path_for('ph', 'ph-ihomis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ph/ph-ihomis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250312091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312091500'
        evn.operator_id = XCN(xcn_1='BALINGIT', xcn_2='RENATO', xcn_3='ESCUETA', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0192837465', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250312-0001', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='DIMACULANGAN', xpn_2='MARCO', xpn_3='LIBRADO', xpn_5='JR')
        pid.mothers_maiden_name = XPN(xpn_1='BALGOS', xpn_2='IMELDA')
        pid.date_time_of_birth = '19780415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Unit 5 Blk 12 Sampaloc', xad_3='Manila', xad_4='NCR', xad_5='1008', xad_6='PH')
        pid.pid_13 = '+63-2-8712-3456~+63-917-555-1234'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH019283746500')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-3B', pl_2='301', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'LACSAMANA^CARLOS^VERGARA^^^DR^MD'
        pv1.pv1_8 = 'PAGULAYAN^ANA^LOURDES^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'LACSAMANA^CARLOS^VERGARA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250312091500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Pneumonia, community-acquired')
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
        in1.in1_14 = 'DIMACULANGAN^MARCO^LIBRADO^^JR'
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19780415')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Unit 5 Blk 12 Sampaloc', cwe_3='Manila', cwe_4='NCR', cwe_5='1008', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH0192837465'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250312'
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
    """ Based on live/ph/ph-ihomis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250313080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250313080000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SYSTEM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0288374651', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250313-0042', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PACQUIAO', xpn_2='LORNA', xpn_3='CATIBOG')
        pid.date_time_of_birth = '19850622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='45 Gen. Luna St', xad_3='Quezon City', xad_4='NCR', xad_5='1100', xad_6='PH')
        pid.pid_13 = '+63-2-8642-1122~+63-928-444-7890'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH028837465100')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-GEN', pl_2='001', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'ALMENDRAS^PEDRO^TUAZON^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'ALMENDRAS^PEDRO^TUAZON^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250313080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='PACQUIAO', aui_2='LORNA', aui_3='CATIBOG')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19850622')
        in1.insureds_relationship_to_patient = CWE(cwe_1='45 Gen. Luna St', cwe_3='Quezon City', cwe_4='NCR', cwe_5='1100', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH0288374651'

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
    """ Based on live/ph/ph-ihomis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250314103000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0345678912', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250314-0078', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='VILLAFLOR', xpn_2='ROBERTO', xpn_3='ENRIQUEZ')
        pid.date_time_of_birth = '19650918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='78 Ortigas Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8922-5566~+63-919-333-2211'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH034567891200')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-2A', pl_2='205', pl_3='B', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'BATUNGBAKAL^RICARDO^MAGSAYSAY^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BATUNGBAKAL^RICARDO^MAGSAYSAY^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250314090000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250314-001')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250314103000'
        orc.orc_10 = 'NURSE^ROSARIO^SANTOS'
        orc.enterers_location = PL(pl_1='TMC_PASIG')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250314-001')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr.observation_date_time = '20250314103000'
        obr.obr_15 = 'BATUNGBAKAL^RICARDO^MAGSAYSAY^^^DR^MD'
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
        obr_2.placer_order_number = EI(ei_1='ORD-20250314-001')
        obr_2.universal_service_identifier = CWE(cwe_1='CHEM12', cwe_2='Blood Chemistry Panel', cwe_3='L')
        obr_2.observation_date_time = '20250314103000'
        obr_2.obr_15 = 'BATUNGBAKAL^RICARDO^MAGSAYSAY^^^DR^MD'
        obr_2.result_status = '^^^^^R'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/ph/ph-ihomis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250315141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0456789123', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250315-0033', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TARUC', xpn_2='ANITA', xpn_3='FELICIANO')
        pid.date_time_of_birth = '19720305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='12 Ayala Ave', xad_3='Makati', xad_4='NCR', xad_5='1226', xad_6='PH')
        pid.pid_13 = '+63-2-8254-1890~+63-906-777-3344'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH045678912300')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-1A', pl_2='104', pl_3='A', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'VILLAROSA^ERNESTO^SALONGA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'VILLAROSA^ERNESTO^SALONGA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250315080000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250315-012')
        orc.orc_12 = 'VILLAROSA^ERNESTO^SALONGA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250315-012')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='L')
        obr.observation_date_time = '20250315120000'
        obr.obr_16 = 'VILLAROSA^ERNESTO^SALONGA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250315141500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Blood Cell Count', cwe_3='L')
        obx.obx_5 = '11.2'
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
        obx_2.obx_5 = '4.1'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '3.80-5.20'
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
        obx_3.obx_5 = '118'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '120-160'
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
        obx_4.obx_5 = '0.35'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.36-0.46'
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
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='MCV', cwe_2='Mean Corpuscular Volume', cwe_3='L')
        obx_6.obx_5 = '85.4'
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
        obx_8.obx_5 = '337'
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
    """ Based on live/ph/ph-ihomis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CDU_CEBU')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='CDU_CEBU')
        msh.date_time_of_message = '20250316100500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0567891234', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250316-0019', cx_4='CDU', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGBANUA', xpn_2='FERNANDO', xpn_3='TEJADA')
        pid.date_time_of_birth = '19880712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Colon St', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-8711-4455~+63-935-888-2211'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH056789123400')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-MED', pl_2='003', pl_4='CDU_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'KATIGBAK^LILIA^OCAMPO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'KATIGBAK^LILIA^OCAMPO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDU_CEBU'
        pv1.discharge_date_time = '20250316080000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250316-005')
        orc.orc_12 = 'KATIGBAK^LILIA^OCAMPO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250316-005')
        obr.universal_service_identifier = CWE(cwe_1='UA', cwe_2='Urinalysis', cwe_3='L')
        obr.observation_date_time = '20250316083000'
        obr.obr_16 = 'KATIGBAK^LILIA^OCAMPO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250316100500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='UA-COLOR', cwe_2='Color', cwe_3='L')
        obx.obx_5 = 'Yellow'
        obx.reference_range = 'Yellow'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='UA-CLARITY', cwe_2='Clarity', cwe_3='L')
        obx_2.obx_5 = 'Slightly Hazy'
        obx_2.reference_range = 'Clear'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='UA-PH', cwe_2='pH', cwe_3='L')
        obx_3.obx_5 = '6.0'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='UA-SG', cwe_2='Specific Gravity', cwe_3='L')
        obx_4.obx_5 = '1.020'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='UA-PROT', cwe_2='Protein', cwe_3='L')
        obx_5.obx_5 = 'Trace'
        obx_5.reference_range = 'Negative'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='UA-GLUC', cwe_2='Glucose', cwe_3='L')
        obx_6.obx_5 = 'Negative'
        obx_6.reference_range = 'Negative'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='UA-WBC', cwe_2='WBC', cwe_3='L')
        obx_7.obx_5 = '5'
        obx_7.units = CWE(cwe_1='/hpf')
        obx_7.reference_range = '0-5'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='UA-RBC', cwe_2='RBC', cwe_3='L')
        obx_8.obx_5 = '2'
        obx_8.units = CWE(cwe_1='/hpf')
        obx_8.reference_range = '0-3'
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
    """ Based on live/ph/ph-ihomis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='SPMC_DAVAO')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SPMC_DAVAO')
        msh.date_time_of_message = '20250317150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250317150000'
        evn.operator_id = XCN(xcn_1='MANANSALA', xcn_2='ANTONIO', xcn_3='BORJA', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0678912345', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250310-0012', cx_4='SPMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='LAUREL', xpn_2='ELENA', xpn_3='BUENAVENTURA')
        pid.date_time_of_birth = '19900101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 Quimpo Blvd', xad_3='Davao', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-8882-9900~+63-917-222-6677'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH067891234500')
        pid.mothers_identifier = CX(cx_1='Davao', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-4A', pl_2='402', pl_3='B', pl_4='SPMC_DAVAO', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'MANANSALA^ANTONIO^BORJA^^^DR^MD'
        pv1.pv1_8 = 'CRISOSTOMO^ROSARIO^LIMJUCO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'MANANSALA^ANTONIO^BORJA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SPMC_DAVAO'
        pv1.discharge_date_time = '20250310120000'
        pv1.total_charges = '20250317150000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Dengue fever, unspecified')
        pv2.visit_protection_indicator = 'AI'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A90', cwe_2='Dengue fever', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='D69.6', cwe_2='Thrombocytopenia, unspecified', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250310'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ph/ph-ihomis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='SLMC_TAGUIG')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='SLMC_TAGUIG')
        msh.date_time_of_message = '20250318133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0789123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250318-0055', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='SOTTO', xpn_2='ARTURO', xpn_3='PANGILINAN')
        pid.date_time_of_birth = '19550828'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='56 McKinley Rd', xad_3='Taguig', xad_4='NCR', xad_5='1634', xad_6='PH')
        pid.pid_13 = '+63-2-8421-5566~+63-920-111-8899'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH078912345600')
        pid.mothers_identifier = CX(cx_1='Taguig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='003', pl_3='A', pl_4='SLMC_TAGUIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'MADRIGAL^MIGUEL^QUIAMBAO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'MADRIGAL^MIGUEL^QUIAMBAO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_TAGUIG'
        pv1.discharge_date_time = '20250318060000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250318-029')
        orc.orc_12 = 'MADRIGAL^MIGUEL^QUIAMBAO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250318-029')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Chemistry Panel', cwe_3='L')
        obr.observation_date_time = '20250318090000'
        obr.obr_16 = 'MADRIGAL^MIGUEL^QUIAMBAO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250318133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='GLU', cwe_2='Glucose, Fasting', cwe_3='L')
        obx.obx_5 = '8.2'
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
        obx_2.observation_identifier = CWE(cwe_1='BUN', cwe_2='Blood Urea Nitrogen', cwe_3='L')
        obx_2.obx_5 = '12.1'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.5-7.1'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='L')
        obx_3.obx_5 = '185'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '62-115'
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
        obx_4.obx_5 = '139'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='L')
        obx_5.obx_5 = '5.6'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='CL', cwe_2='Chloride', cwe_3='L')
        obx_6.obx_5 = '101'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '98-106'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='ALT', cwe_2='Alanine Aminotransferase', cwe_3='L')
        obx_7.obx_5 = '45'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='AST', cwe_2='Aspartate Aminotransferase', cwe_3='L')
        obx_8.obx_5 = '62'
        obx_8.units = CWE(cwe_1='U/L')
        obx_8.reference_range = '10-40'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ED'
        obx_9.observation_identifier = CWE(cwe_1='PDF-RPT', cwe_2='Chemistry Panel Report', cwe_3='L')
        obx_9.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKENoZW1pc3RyeSBQYW5lbCBS'
            'ZXBvcnQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYK'
            'MCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAow'
            'MDAwMDAwNDAxIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNDkyCiUlRU9GCg=='
        )

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
    """ Based on live/ph/ph-ihomis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250319111500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250319111500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='RECORDS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0891234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250315-0091', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MACAPAGAL', xpn_2='BENITO', xpn_3='SORIANO')
        pid.date_time_of_birth = '19700214'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='34 Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1004', xad_6='PH')
        pid.pid_13 = '+63-2-8646-0218~+63-939-555-4411'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH089123456700')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG-2B', pl_2='210', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'EVANGELISTA^JULIAN^MANALO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'EVANGELISTA^JULIAN^MANALO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250315100000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MACAPAGAL', xpn_2='CORAZON', xpn_3='BUENCAMINO')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='34 Taft Ave', xad_3='Manila', xad_4='NCR', xad_5='1004', xad_6='PH')
        nk1.nk1_5 = '+63-2-8646-0220~+63-917-888-3322'
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
    """ Based on live/ph/ph-ihomis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='CDH_CAGAYAN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='CDH_CAGAYAN')
        msh.date_time_of_message = '20250320093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH0912345678', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250320-0027', cx_4='CDH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GUEVARRA', xpn_2='ROSALINDA', xpn_3='NAVARRO')
        pid.date_time_of_birth = '19830519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='10 Corrales Ave', xad_3='Cagayan de Oro', xad_4='X', xad_5='9000', xad_6='PH')
        pid.pid_13 = '+63-88-8981-0300~+63-927-666-1122'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH091234567800')
        pid.mothers_identifier = CX(cx_1='Cagayan de Oro', cx_2='X', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEPH-3A', pl_2='312', pl_3='B', pl_4='CDH_CAGAYAN', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'PRIETO^EDGAR^RAMOS^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='NEPH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'PRIETO^EDGAR^RAMOS^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDH_CAGAYAN'
        pv1.discharge_date_time = '20250319140000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250320-015')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250320093000'
        orc.orc_10 = 'NURSE^CRISTINA^LOPEZ'
        orc.enterers_location = PL(pl_1='CDH_CAGAYAN')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250320-015')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Chest X-Ray PA and Lateral', cwe_3='CPT')
        obr.observation_date_time = '20250320093000'
        obr.obr_15 = 'PRIETO^EDGAR^RAMOS^^^DR^MD'
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
    """ Based on live/ph/ph-ihomis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250321140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250321140000'
        evn.operator_id = XCN(xcn_1='DELROSARIO', xcn_2='RAMON', xcn_3='ILAGAN', xcn_6='DR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1023456789', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250318-0006', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ABAD', xpn_2='PATRICIA', xpn_3='GOROSPE')
        pid.date_time_of_birth = '19950830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='99 Quirino Ave', xad_3='Manila', xad_4='NCR', xad_5='1009', xad_6='PH')
        pid.pid_13 = '+63-2-8732-3901~+63-906-333-5544'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH102345678900')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ISO-2', pl_2='205', pl_3='A', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'DELROSARIO^RAMON^ILAGAN^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'DELROSARIO^RAMON^ILAGAN^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.delete_account_indicator = CWE(cwe_1='MED-3A', cwe_2='301', cwe_3='B', cwe_4='PGH_MANILA', cwe_7='N')
        pv1.account_status = CWE(cwe_1='PGH_MANILA')
        pv1.current_patient_balance = '20250318090000'

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
    """ Based on live/ph/ph-ihomis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250322090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT-20250325-001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Follow-up pulmonology consult', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20250325100000^20250325103000'
        sch.sch_13 = 'BUENCAMINO^LUISA^FERNANDEZ^^^DR^MD'
        sch.placer_contact_address = XAD(xad_1='+63-2-8924-6101')
        sch.placer_contact_location = PL(pl_1='SLMC PULMO CLINIC', pl_2='Rm 201', pl_4='Quezon City', pl_5='NCR', pl_6='1100', pl_7='PH')
        sch.filler_contact_person = XCN(xcn_1='SLMC_QC')
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1134567890', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250310-0044', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RECINTO', xpn_2='MANUEL', xpn_3='BAUTISTA')
        pid.date_time_of_birth = '19680305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='23 Congressional Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1126', xad_6='PH')
        pid.pid_13 = '+63-2-8931-7722~+63-918-444-9900'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH113456789000')
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
        ais.universal_service_identifier = CWE(cwe_1='PULMO-CONSULT', cwe_2='Pulmonology Consultation', cwe_3='L')
        ais.start_date_time = '20250325100000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'BUENCAMINO^LUISA^FERNANDEZ^^^DR^MD'
        aip.resource_type = CWE(cwe_1='PULMO')
        aip.start_date_time_offset_units = CNE(cne_1='20250325100000')
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
    """ Based on live/ph/ph-ihomis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='MMC_MAKATI')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='MMC_MAKATI')
        msh.date_time_of_message = '20250323160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250323160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1245678901', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250319-0088', cx_4='MMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='YULO', xpn_2='CRISTINA', xpn_3='PANGAN')
        pid.date_time_of_birth = '19920714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='67 Gil Puyat Ave', xad_3='Makati', xad_4='NCR', xad_5='1200', xad_6='PH')
        pid.pid_13 = '+63-2-8524-1766~+63-935-222-8811'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH124567890100')
        pid.mothers_identifier = CX(cx_1='Makati', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OB-3', pl_2='305', pl_3='A', pl_4='MMC_MAKATI', pl_7='N')
        pv1.admission_type = CWE(cwe_1='D')
        pv1.pv1_7 = 'ARCILLA^ROSA^VALENCIANO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='OBG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'ARCILLA^ROSA^VALENCIANO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'MMC_MAKATI'
        pv1.discharge_date_time = '20250319110000'
        pv1.total_charges = '20250323160000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20250323150000'
        txa.txa_5 = 'ARCILLA^ROSA^VALENCIANO^^^DR^MD'
        txa.transcription_date_time = '20250323160000'
        txa.txa_9 = 'ARCILLA^ROSA^VALENCIANO^^^DR^MD'
        txa.parent_document_number = EI(ei_1='DOC-20250323-001')
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
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NSA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKERpc2NoYXJnZSBTdW1tYXJ5'
            'IC0gT0IgV2FyZCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoK'
            'eHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAw'
            'IG4gCjAwMDAwMDA0MTIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo1MDMKJSVFT0YK'
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
    """ Based on live/ph/ph-ihomis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='PCMC_QC')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PCMC_QC')
        msh.date_time_of_message = '20250324110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250324110000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='NURSERY')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='20250324-NB001', cx_4='PCMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SALCEDO', xpn_2='BABY BOY', xpn_3='')
        pid.date_time_of_birth = '20250324'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='15 Agham Rd', xad_3='Quezon City', xad_4='NCR', xad_5='1105', xad_6='PH')
        pid.pid_13 = '+63-2-8924-0841'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.birth_place = 'Quezon City^NCR^PH'
        pid.identity_unknown_indicator = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SALCEDO', xpn_2='CARMELA', xpn_3='LINGAT')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='15 Agham Rd', xad_3='Quezon City', xad_4='NCR', xad_5='1105', xad_6='PH')
        nk1.nk1_5 = '+63-917-111-5566'
        nk1.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='SALCEDO', xpn_2='GREGORIO', xpn_3='UMALI')
        nk1_2.relationship = CWE(cwe_1='FTH')
        nk1_2.address = XAD(xad_1='15 Agham Rd', xad_3='Quezon City', xad_4='NCR', xad_5='1105', xad_6='PH')
        nk1_2.nk1_5 = '+63-928-222-7788'
        nk1_2.contact_role = CWE(cwe_1='EC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA05NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='001', pl_3='A', pl_4='PCMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='N')
        pv1.pv1_7 = 'FELICIANO^CARMEN^ONGPIN^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'FELICIANO^CARMEN^ONGPIN^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PCMC_QC'
        pv1.discharge_date_time = '20250324110000'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
        msg.pv1 = pv1

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
    """ Based on live/ph/ph-ihomis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='SPMC_DAVAO')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='SPMC_DAVAO')
        msh.date_time_of_message = '20250325143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1356789012', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250325-0011', cx_4='SPMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MONTALBAN', xpn_2='DANILO', xpn_3='QUIJANO')
        pid.date_time_of_birth = '20020910'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='44 J.P. Laurel Ave', xad_3='Davao', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-8807-2628~+63-939-444-5566'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH135678901200')
        pid.mothers_identifier = CX(cx_1='Davao', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INF-2A', pl_2='201', pl_3='B', pl_4='SPMC_DAVAO', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'TIONKO^AURORA^MABINI^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TIONKO^AURORA^MABINI^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SPMC_DAVAO'
        pv1.discharge_date_time = '20250325080000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250325-008')
        orc.orc_12 = 'TIONKO^AURORA^MABINI^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250325-008')
        obr.universal_service_identifier = CWE(cwe_1='DENGUE', cwe_2='Dengue Panel', cwe_3='L')
        obr.observation_date_time = '20250325100000'
        obr.obr_16 = 'TIONKO^AURORA^MABINI^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250325143000'
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
        obx_2.obx_5 = 'POSITIVE'
        obx_2.reference_range = 'NEGATIVE'
        obx_2.interpretation_codes = CWE(cwe_1='A')
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
        obx_4.obx_5 = '78'
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
        obx_5.obx_5 = '0.48'
        obx_5.units = CWE(cwe_1='L/L')
        obx_5.reference_range = '0.40-0.54'
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
    """ Based on live/ph/ph-ihomis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='CDU_CEBU')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='CDU_CEBU')
        msh.date_time_of_message = '20250326090100'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG-ORU-20250326-001'
        msa.msa_3 = 'Message accepted successfully'

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
    """ Based on live/ph/ph-ihomis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='PGH_MANILA')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='PGH_MANILA')
        msh.date_time_of_message = '20250327101500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250327101500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1467890123', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250320-0033', cx_4='PGH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MAGSAYSAY', xpn_2='GABRIEL', xpn_3='TUASON')
        pid.date_time_of_birth = '19880921'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Padre Faura St', xad_3='Manila', xad_4='NCR', xad_5='1000', xad_6='PH')
        pid.pid_13 = '+63-2-8531-9001~+63-906-111-3344'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH146789012300')
        pid.mothers_identifier = CX(cx_1='Manila', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='20250315-DUP042', cx_4='PGH', cx_5='MR')
        mrg.mrg_2 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PSY-OPD', pl_2='001', pl_4='PGH_MANILA', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'BONDOC^TERESA^VIRATA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PSY')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'BONDOC^TERESA^VIRATA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'PGH_MANILA'
        pv1.discharge_date_time = '20250327101500'

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
    """ Based on live/ph/ph-ihomis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='CDU_CEBU')
        msh.receiving_application = HD(hd_1='PHARM')
        msh.receiving_facility = HD(hd_1='CDU_CEBU')
        msh.date_time_of_message = '20250328083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1578901234', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250326-0019', cx_4='CDU', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='BERNARDO', xpn_2='ALFREDO', xpn_3='COJUANGCO')
        pid.date_time_of_birth = '19480630'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='78 Mango Ave', xad_3='Cebu City', xad_4='VII', xad_5='6000', xad_6='PH')
        pid.pid_13 = '+63-32-8927-6426~+63-918-999-2211'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH157890123400')
        pid.mothers_identifier = CX(cx_1='Cebu City', cx_2='VII', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-5A', pl_2='501', pl_3='A', pl_4='CDU_CEBU', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CABRERA^CARLOS^LEGASPI^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CABRERA^CARLOS^LEGASPI^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'CDU_CEBU'
        pv1.discharge_date_time = '20250326140000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250328-007')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20250328083000'
        orc.orc_10 = 'NURSE^JENNIFER^CASTILLO'
        orc.enterers_location = PL(pl_1='CDU_CEBU')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='AMLO5', cwe_2='Amlodipine 5mg', cwe_3='L')
        rxo.requested_give_amount_minimum = '5'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo.allow_substitutions = '1^1x daily'
        rxo.rxo_14 = 'CABRERA^CARLOS^LEGASPI^^^DR^MD'

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='METF500', cwe_2='Metformin 500mg', cwe_3='L')
        rxo_2.requested_give_amount_minimum = '500'
        rxo_2.requested_give_units = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Tablet')
        rxo_2.providers_administration_instructions = CWE(cwe_2='PO', cwe_3='Oral')
        rxo_2.allow_substitutions = '2^2x daily'
        rxo_2.rxo_14 = 'CABRERA^CARLOS^LEGASPI^^^DR^MD'

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
    """ Based on live/ph/ph-ihomis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='TMC_PASIG')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='TMC_PASIG')
        msh.date_time_of_message = '20250329112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1689012345', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250329-0008', cx_4='TMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TOLENTINO', xpn_2='ROSANNA', xpn_3='ALMONTE')
        pid.date_time_of_birth = '19910406'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='55 C. Raymundo Ave', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        pid.pid_13 = '+63-2-8871-3014~+63-935-777-3311'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH168901234500')
        pid.mothers_identifier = CX(cx_1='Pasig', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD-LAB', pl_2='001', pl_4='TMC_PASIG', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'PASCUAL^NOEL^HIDALGO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'PASCUAL^NOEL^HIDALGO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'TMC_PASIG'
        pv1.discharge_date_time = '20250329080000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250329-003')
        orc.orc_12 = 'PASCUAL^NOEL^HIDALGO^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250329-003')
        obr.universal_service_identifier = CWE(cwe_1='HEPB', cwe_2='Hepatitis B Panel', cwe_3='L')
        obr.observation_date_time = '20250329083000'
        obr.obr_16 = 'PASCUAL^NOEL^HIDALGO^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250329112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='HBSAG', cwe_2='Hepatitis B Surface Antigen', cwe_3='L')
        obx.obx_5 = 'Non-Reactive'
        obx.reference_range = 'Non-Reactive'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='HBSAB', cwe_2='Hepatitis B Surface Antibody', cwe_3='L')
        obx_2.obx_5 = 'Reactive'
        obx_2.reference_range = 'Reactive (if vaccinated)'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='HBCAB', cwe_2='Hepatitis B Core Antibody', cwe_3='L')
        obx_3.obx_5 = 'Non-Reactive'
        obx_3.reference_range = 'Non-Reactive'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ph/ph-ihomis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IHOMIS')
        msh.sending_facility = HD(hd_1='SPMC_DAVAO')
        msh.receiving_application = HD(hd_1='ADT_RCV')
        msh.receiving_facility = HD(hd_1='SPMC_DAVAO')
        msh.date_time_of_message = '20250330090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A31')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250330090000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='PHIC')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1790123456', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250301-0061', cx_4='SPMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PANGASINAN', xpn_2='JOSEFINA', xpn_3='MAGAT')
        pid.date_time_of_birth = '19770812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Torres St', xad_3='Davao', xad_4='XI', xad_5='8000', xad_6='PH')
        pid.pid_13 = '+63-82-8292-5544~+63-928-333-4455'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH179012345600')
        pid.mothers_identifier = CX(cx_1='Davao', cx_2='XI', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REG', pl_2='001', pl_4='SPMC_DAVAO', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'AGUINALDO^DANTE^RECTO^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'AGUINALDO^DANTE^RECTO^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SPMC_DAVAO'
        pv1.discharge_date_time = '20250330090000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PHIC')
        in1.insurance_company_id = CX(cx_1='PHILHEALTH')
        in1.insurance_company_name = XON(xon_1='PhilHealth')
        in1.insurance_company_address = XAD(xad_1='Citystate Centre, 709 Shaw Blvd', xad_3='Pasig', xad_4='NCR', xad_5='1600', xad_6='PH')
        in1.insurance_co_contact_person = XPN(xpn_1='+63-2-8441-7442')
        in1.in1_7 = 'PH-PHIC-001'
        in1.authorization_information = AUI(aui_1='PANGASINAN', aui_2='JOSEFINA', aui_3='MAGAT')
        in1.plan_type = CWE(cwe_1='SEL')
        in1.name_of_insured = XPN(xpn_1='19770812')
        in1.insureds_relationship_to_patient = CWE(cwe_1='88 Torres St', cwe_3='Davao', cwe_4='XI', cwe_5='8000', cwe_6='PH')
        in1.assignment_of_benefits = CWE(cwe_1='1')
        in1.delay_before_lr_day = 'PH1790123456'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/ph/ph-ihomis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='SLMC_QC')
        msh.receiving_application = HD(hd_1='IHOMIS')
        msh.receiving_facility = HD(hd_1='SLMC_QC')
        msh.date_time_of_message = '20250331153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_19 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PH1801234567', cx_4='PHIC', cx_5='SS'), CX(cx_1='20250331-0022', cx_4='SLMC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='EJERCITO', xpn_2='RICARDO', xpn_3='CATIBOG')
        pid.date_time_of_birth = '19600118'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='33 Visayas Ave', xad_3='Quezon City', xad_4='NCR', xad_5='1128', xad_6='PH')
        pid.pid_13 = '+63-2-8924-6101~+63-917-888-1100'
        pid.primary_language = CWE(cwe_1='TGL')
        pid.marital_status = CWE(cwe_1='RC')
        pid.religion = CWE(cwe_1='PH180123456700')
        pid.mothers_identifier = CX(cx_1='Quezon City', cx_2='NCR', cx_3='PH')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULMO-2A', pl_2='210', pl_3='B', pl_4='SLMC_QC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'ORTIGAS^GRACE^TANADA^^^DR^MD'
        pv1.hospital_service = CWE(cwe_1='PULMO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'ORTIGAS^GRACE^TANADA^^^DR^MD'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PHIC')
        pv1.pv1_40 = 'SLMC_QC'
        pv1.discharge_date_time = '20250330100000'

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
        orc.placer_order_number = EI(ei_1='ORD-20250331-014')
        orc.orc_12 = 'ORTIGAS^GRACE^TANADA^^^DR^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-20250331-014')
        obr.universal_service_identifier = CWE(cwe_1='GENEXPERT', cwe_2='GeneXpert MTB/RIF', cwe_3='L')
        obr.observation_date_time = '20250331100000'
        obr.obr_16 = 'ORTIGAS^GRACE^TANADA^^^DR^MD'
        obr.results_rpt_status_chng_date_time = '20250331153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='MTB', cwe_2='Mycobacterium tuberculosis', cwe_3='L')
        obx.obx_5 = 'DETECTED'
        obx.reference_range = 'NOT DETECTED'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='RIF-R', cwe_2='Rifampicin Resistance', cwe_3='L')
        obx_2.obx_5 = 'NOT DETECTED'
        obx_2.reference_range = 'NOT DETECTED'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='MTB-QTY', cwe_2='MTB Quantity', cwe_3='L')
        obx_3.obx_5 = 'Medium'
        obx_3.probability = 'N'
        obx_3.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='CT', cwe_2='Cycle Threshold', cwe_3='L')
        obx_4.obx_5 = '18.5'
        obx_4.reference_range = '<28.0'
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

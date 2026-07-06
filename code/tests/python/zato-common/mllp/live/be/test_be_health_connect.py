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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIS, AL1, DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXA, RXO, RXR, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-health-connect.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-health-connect.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='UZLEUVEN')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UZLEUVEN')
        msh.date_time_of_message = '20250312143022+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250312143022001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312143000'
        evn.operator_id = XCN(xcn_1='ADMIN01', xcn_2='Mertens', xcn_3='Lieve', xcn_6='Dr.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='234567890', cx_4='UZLEUVEN', cx_5='PI'), CX(cx_1='96071523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Janssens^Katrien^E^^^Mevr.'
        pid.date_time_of_birth = '19960715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Naamsestraat 42', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '016284531^PRN^PH'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '96071523456^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='301', pl_3='A', pl_4='UZLEUVEN', pl_8='4')
        pv1.prior_patient_location = PL(pl_1='23456', pl_2='Wouters', pl_3='Pieter', pl_6='Dr.', pl_7='MD')
        pv1.pv1_7 = '78901^Bogaert^Hilde^^^Dr.^MD'
        pv1.referring_doctor = XCN(xcn_1='SUR')
        pv1.preadmit_test_indicator = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='23456', cwe_2='Wouters', cwe_3='Pieter', cwe_6='Dr.', cwe_7='MD')
        pv1.vip_indicator = CWE(cwe_1='IN')
        pv1.patient_type = CWE(cwe_1='ZIEKENFONDS')
        pv1.discharged_to_location = DLD(dld_1='UZLEUVEN')
        pv1.pending_location = PL(pl_1='20250312143000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Janssens', xpn_2='Wim', xpn_5='Dhr.')
        nk1.address = XAD(xad_1='016765432', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CM200', cwe_2='CM Leuven')
        in1.insurance_company_id = CX(cx_1='200')
        in1.insurance_company_name = XON(xon_1='Socialistische Mutualiteit')
        in1.policy_number = '200/23456789'

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='A001', cwe_2='Penicilline', cwe_3='LOCAL')
        al1.allergy_reaction_code = 'Anafylaxie'
        al1.al1_6 = '20201115'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1, al1]

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
    """ Based on live/be/be-health-connect.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='AZSTLUCAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='AZSTLUCAS')
        msh.date_time_of_message = '20250418091534+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250418091534002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250418091500'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='Auto')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='098765432', cx_4='AZSTLUCAS', cx_5='PI'), CX(cx_1='92061834567', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Maes^Bram^L^^^Dhr.'
        pid.date_time_of_birth = '19920618'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vlaanderenstraat 87', xad_3='Gent', xad_5='9000', xad_6='BE', xad_7='H')
        pid.pid_13 = '09345612^PRN^PH~0476123456^PRN^CP'
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '92061834567^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='CONSULT', pl_3='1', pl_4='AZSTLUCAS')
        pv1.pv1_7 = '65432^Coppens^Leen^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='ORTH')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='65432', cwe_2='Coppens', cwe_3='Leen', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='MUTUALITE')
        pv1.discharged_to_location = DLD(dld_1='AZSTLUCAS')
        pv1.pending_location = PL(pl_1='20250418090000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Maes', xpn_2='Veerle', xpn_5='Mevr.')
        nk1.address = XAD(xad_1='09987654', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'SPO'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/be/be-health-connect.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='CHULIEGE')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHULIEGE')
        msh.date_time_of_message = '20250520163045+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250520163045003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250520163000'
        evn.operator_id = XCN(xcn_1='DR001', xcn_2='Marchand', xcn_3='Philippe', xcn_6='Dr.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='567890123', cx_4='CHULIEGE', cx_5='PI'), CX(cx_1='77030923456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Dupont^Isabelle^R^^^Mme.'
        pid.date_time_of_birth = '19770309'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Bruxelles 22', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        pid.pid_13 = '04333444^PRN^PH'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '77030923456^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='402', pl_3='B', pl_4='CHULIEGE', pl_8='2')
        pv1.prior_patient_location = PL(pl_1='DR001', pl_2='Marchand', pl_3='Philippe', pl_6='Dr.', pl_7='MD')
        pv1.referring_doctor = XCN(xcn_1='MED')
        pv1.preadmit_test_indicator = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='DR001', cwe_2='Marchand', cwe_3='Philippe', cwe_6='Dr.', cwe_7='MD')
        pv1.vip_indicator = CWE(cwe_1='IN')
        pv1.patient_type = CWE(cwe_1='MUTUALITE')
        pv1.discharged_to_location = DLD(dld_1='CHULIEGE')
        pv1.pending_location = PL(pl_1='20250515100000')
        pv1.discharge_date_time = '20250520163000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.0', cwe_2='Infarctus myocardique aigu', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250515'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/be/be-health-connect.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='UZBRUSSEL')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='UZBRUSSEL')
        msh.date_time_of_message = '20250601084512+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20250601084512001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='345678901', cx_4='UZBRUSSEL', cx_5='PI'), CX(cx_1='84071223456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Peeters^Ruben^D^^^Dhr.'
        pid.date_time_of_birth = '19840712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Laarbeeklaan 33', xad_3='Jette', xad_5='1090', xad_6='BE', xad_7='H')
        pid.pid_13 = '02456789^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEPH', pl_2='501', pl_3='A', pl_4='UZBRUSSEL')
        pv1.pv1_7 = 'DR010^Van Damme^Luc^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250601001')
        orc.filler_order_number = EI(ei_1='LAB20250601001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20250601080000+0200'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250601001')
        obr.filler_order_number = EI(ei_1='LAB20250601001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basic Metabolic Panel', cwe_3='LN')
        obr.observation_date_time = '20250601074500+0200'
        obr.obr_15 = 'DR010^Van Damme^Luc^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '108'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250601083000+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '1.8'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250601083000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_3.obx_5 = '52'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '15-45'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250601083000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '139'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250601083000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '5.6'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250601083000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_6.obx_5 = '2.35'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '2.20-2.65'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250601083000+0200'

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
    """ Based on live/be/be-health-connect.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='AZGROENINGE')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='AZGROENINGE')
        msh.date_time_of_message = '20250415102233+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20250415102233001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789012', cx_4='AZGROENINGE', cx_5='PI'), CX(cx_1='90052523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Claes^Annelies^V^^^Mevr.'
        pid.date_time_of_birth = '19900525'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Brugsesteenweg 44', xad_3='Kortrijk', xad_5='8500', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEMA', pl_2='CONSULT', pl_3='2', pl_4='AZGROENINGE')
        pv1.pv1_7 = 'DR020^Goossens^Tom^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250415001')
        orc.filler_order_number = EI(ei_1='LAB20250415001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250415001')
        obr.filler_order_number = EI(ei_1='LAB20250415001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20250415094500+0200'
        obr.obr_15 = 'DR020^Goossens^Tom^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocyten', cwe_3='LN')
        obx_2.obx_5 = '4.35'
        obx_2.units = CWE(cwe_1='10*12/L')
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
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '94.7'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Thrombocyten', cwe_3='LN')
        obx_6.obx_5 = '245'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-health-connect.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPD')
        msh.sending_facility = HD(hd_1='AZTURNHOUT')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='AZTURNHOUT')
        msh.date_time_of_message = '20250322111500+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORD20250322111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901234', cx_4='AZTURNHOUT', cx_5='PI'), CX(cx_1='81091023456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Willems^Frederik^H^^^Dhr.'
        pid.date_time_of_birth = '19810910'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gasthuisstraat 18', xad_3='Turnhout', xad_5='2300', xad_6='BE', xad_7='H')
        pid.pid_13 = '014678901^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='A', pl_4='AZTURNHOUT')
        pv1.pv1_7 = 'DR030^Mertens^Kris^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250322001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250322111500+0100'
        orc.orc_12 = 'DR030^Mertens^Kris^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250322001')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CT Thorax met contrast', cwe_3='CPT4')
        obr.observation_date_time = '20250322111500+0100'
        obr.obr_16 = 'DR030^Mertens^Kris^^^Dr.^MD'
        obr.results_rpt_status_chng_date_time = 'CT'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Klinische vraag: uitsluiten longembolie. Patient allergisch voor jodium - premedicatie reeds toegediend.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.9', cwe_2='Longembolie', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte
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
    """ Based on live/be/be-health-connect.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CPOE')
        msh.sending_facility = HD(hd_1='UZANTWERPEN')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='UZANTWERPEN')
        msh.date_time_of_message = '20250508153022+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORD20250508153022001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='789012345', cx_4='UZANTWERPEN', cx_5='PI'), CX(cx_1='97111523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Goossens^Elien^S^^^Mevr.'
        pid.date_time_of_birth = '19971115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Quellinstraat 55', xad_3='Antwerpen', xad_5='2018', xad_6='BE', xad_7='H')
        pid.pid_13 = '03567890^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='CONSULT', pl_3='3', pl_4='UZANTWERPEN')
        pv1.pv1_7 = 'DR040^Wouters^Nele^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250508001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250508153000+0200'
        orc.orc_12 = 'DR040^Wouters^Nele^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250508001')
        obr.universal_service_identifier = CWE(cwe_1='83036', cwe_2='HbA1c', cwe_3='CPT4')
        obr.observation_date_time = '20250508153000+0200'
        obr.obr_16 = 'DR040^Wouters^Nele^^^Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='ORD20250508001')
        obr_2.universal_service_identifier = CWE(cwe_1='82947', cwe_2='Glucose nuchter', cwe_3='CPT4')
        obr_2.observation_date_time = '20250508153000+0200'
        obr_2.obr_16 = 'DR040^Wouters^Nele^^^Dr.^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Controle diabetes type 2. Patiënte nuchter sinds middernacht.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, nte]

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
    """ Based on live/be/be-health-connect.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='CLINIQUESTP')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CLINIQUESTP')
        msh.date_time_of_message = '20250610094512+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG20250610094512001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250610094500'
        evn.operator_id = XCN(xcn_1='RECEP01', xcn_2='Laurent', xcn_3='Julie')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='890123456', cx_4='CLINIQUESTP', cx_5='PI'), CX(cx_1='82042023456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Lejeune^Antoine^N^^^M.'
        pid.date_time_of_birth = '19820420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de la Baraque 12', xad_3='Louvain-la-Neuve', xad_5='1348', xad_6='BE', xad_7='H')
        pid.pid_13 = '010345678^PRN^PH'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '82042023456^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='ECHO', pl_3='1', pl_4='CLINIQUESTP')
        pv1.pv1_7 = 'DR050^Renard^Marc^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='CARD')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='DR050', cwe_2='Renard', cwe_3='Marc', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='MUTUALITE')
        pv1.discharged_to_location = DLD(dld_1='CLINIQUESTP')
        pv1.pending_location = PL(pl_1='20250610094500')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MC300', cwe_2='MC Hainaut')
        in1.insurance_company_id = CX(cx_1='300')
        in1.insurance_company_name = XON(xon_1='Mutualite Socialiste')
        in1.policy_number = '300/98765432'

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
    """ Based on live/be/be-health-connect.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MICROBIO')
        msh.sending_facility = HD(hd_1='UZGENT')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='UZGENT')
        msh.date_time_of_message = '20250714121045+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20250714121045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='901234567', cx_4='UZGENT', cx_5='PI'), CX(cx_1='72081223456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Van Damme^Rita^M^^^Mevr.'
        pid.date_time_of_birth = '19720812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Blaarmeersen 4', xad_3='Gent', xad_5='9000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INFECT', pl_2='601', pl_3='C', pl_4='UZGENT')
        pv1.pv1_7 = 'DR060^Bogaert^Dirk^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250714001')
        orc.filler_order_number = EI(ei_1='LAB20250714001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250714001')
        obr.filler_order_number = EI(ei_1='LAB20250714001')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Bloedkweek', cwe_3='LN')
        obr.observation_date_time = '20250712080000+0200'
        obr.obr_15 = 'DR060^Bogaert^Dirk^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Organisme', cwe_3='LN')
        obx.obx_5 = 'ECOLI^Escherichia coli^LOCAL'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Amoxicilline', cwe_3='LN')
        obx_2.obx_5 = 'R'
        obx_2.interpretation_codes = CWE(cwe_1='R')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18862-3', cwe_2='Amoxicilline-clavulaanzuur', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18878-9', cwe_2='Ceftriaxon', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18919-1', cwe_2='Ciprofloxacine', cwe_3='LN')
        obx_5.obx_5 = 'R'
        obx_5.interpretation_codes = CWE(cwe_1='R')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Meropenem', cwe_3='LN')
        obx_6.obx_5 = 'S'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Bloedkweek positief na 14u incubatie. ESBL screening negatief.'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6
        observation_6.nte = nte

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
    """ Based on live/be/be-health-connect.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SCHEDULING')
        msh.sending_facility = HD(hd_1='JYPERMAN')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='JYPERMAN')
        msh.date_time_of_message = '20250305101200+0100'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'APPT20250305101200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT2025030500123')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Raadpleging cardiologie')
        sch.appointment_type = CWE(cwe_1='15')
        sch.sch_9 = 'min'
        sch.appointment_duration_units = CNE(cne_1='1')
        sch.sch_12 = 'DR070^Coppens^Koen^^^Dr.^MD'
        sch.sch_17 = 'DR070^Coppens^Koen^^^Dr.^MD'
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='012345678', cx_4='JYPERMAN', cx_5='PI'), CX(cx_1='68030523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Peeters^Eddy^W^^^Dhr.'
        pid.date_time_of_birth = '19680305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Grote Markt 7', xad_3='Ieper', xad_5='8900', xad_6='BE', xad_7='H')
        pid.pid_13 = '057345678^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='RAADPLEGING', pl_3='1', pl_4='JYPERMAN')
        pv1.pv1_7 = 'DR070^Coppens^Koen^^^Dr.^MD'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CARDCONS', cwe_2='Cardiologie Consultatie', cwe_3='LOCAL')
        ais.start_date_time = '20250320140000+0100'
        ais.start_date_time_offset_units = CNE(cne_1='15')
        ais.duration = 'min'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CARD', pl_2='RAADPLEGING', pl_3='1', pl_4='JYPERMAN')
        ail.location_type_ail = CWE(cwe_1='20250320140000+0100')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource

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
    """ Based on live/be/be-health-connect.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='CHRCITADELLE')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHRCITADELLE')
        msh.date_time_of_message = '20250422183012+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20250422183012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250422183000'
        evn.operator_id = XCN(xcn_1='INFIRM01', xcn_2='Moreau', xcn_3='Marie')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='123456780', cx_4='CHRCITADELLE', cx_5='PI'), CX(cx_1='74051823456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Simon^François^T^^^M.'
        pid.date_time_of_birth = '19740518'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 55', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        pid.pid_13 = '04432567^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='102', pl_3='A', pl_4='CHRCITADELLE', pl_8='1')
        pv1.prior_patient_location = PL(pl_1='DR080', pl_2='Dubois', pl_3='Jean', pl_6='Dr.', pl_7='MD')
        pv1.referring_doctor = XCN(xcn_1='MED')
        pv1.preadmit_test_indicator = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='DR080', cwe_2='Dubois', cwe_3='Jean', cwe_6='Dr.', cwe_7='MD')
        pv1.vip_indicator = CWE(cwe_1='IN')
        pv1.patient_type = CWE(cwe_1='MUTUALITE')
        pv1.discharge_disposition = CWE(cwe_1='CHRCITADELLE')
        pv1.account_status = CWE(cwe_1='20250420090000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Transfert de service de medecine vers soins intensifs')
        pv2.previous_treatment_date = 'CARD^301^B^CHRCITADELLE'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/be/be-health-connect.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHLAB')
        msh.sending_facility = HD(hd_1='AZDELTA')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='AZDELTA')
        msh.date_time_of_message = '20250801143322+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH20250801143322001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='223344556', cx_4='AZDELTA', cx_5='PI'), CX(cx_1='70092023456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Maes^Geert^K^^^Dhr.'
        pid.date_time_of_birth = '19700920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Meensesteenweg 22', xad_3='Roeselare', xad_5='8800', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='301', pl_3='A', pl_4='AZDELTA')
        pv1.pv1_7 = 'DR090^Lejeune^Catherine^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250801001')
        orc.filler_order_number = EI(ei_1='PATH20250801001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250801001')
        obr.filler_order_number = EI(ei_1='PATH20250801001')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Surgical pathology', cwe_3='CPT4')
        obr.observation_date_time = '20250729100000+0200'
        obr.obr_15 = 'DR090^Lejeune^Catherine^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Excisiebiopt huid linker onderarm, 2.3 x 1.5 x 0.8 cm\\.br\\\\.br\\Microscopie: Basaalcelcarcinoom, nodulair type, excisie compleet'
            ' met minimale marge van 2mm\\.br\\\\.br\\Conclusie: Basaalcelcarcinoom, nodulair subtype, volledig geexcideerd.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/be/be-health-connect.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='GHDC')
        msh.receiving_application = HD(hd_1='DOCMGMT')
        msh.receiving_facility = HD(hd_1='GHDC')
        msh.date_time_of_message = '20250912102245+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC20250912102245001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250912102200'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='334455667', cx_4='GHDC', cx_5='PI'), CX(cx_1='85061423456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Lambert^Nathalie^B^^^Mme.'
        pid.date_time_of_birth = '19850614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Marcinelle 33', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='H')
        pid.pid_13 = '071456789^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PNEUMO', pl_2='CONSULT', pl_3='2', pl_4='GHDC')
        pv1.pv1_7 = 'DR100^Michel^Pierre^^^Dr.^MD'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Compte rendu consultation', cwe_3='LOCAL')
        txa.document_content_presentation = 'TX'
        txa.transcription_date_time = '20250912100000+0200'
        txa.txa_9 = 'DR100^Michel^Pierre^^^Dr.^MD'
        txa.parent_document_number = EI(ei_1='DOC-2025-09876')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Discharge summary', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENvbXB0ZSBSZW5kdSBDb25zdWx0YXRpb24gUG5ldW1vbG9naWUpCi9DcmVhdG9yIChIZWFsdGhDb25uZWN0IERvY3VtZW50IEdlbmVy'
            'YXRvcikKL1Byb2R1Y2VyIChJbnRlclN5c3RlbXMgSGVhbHRoQ29ubmVjdCAyMDI1LjEpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTA5MTIxMDIyMDArMDInMDAnKQo+PgplbmRvYmoKMyAw'
            'IG9iago8PAovVHlwZSAvRXh0R1N0YXRlCi9TQSBmYWxzZQovU00gMC4wMgovY2EgMS4wCi9DQSAxLjAKL0FJUyBmYWxzZQo+PgplbmRvYmoKNCAwIG9iagpbL1BhdHRlcm4gL0Rldmlj'
            'ZVJHQl0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNiAwIFIKL1Jlc291cmNlcyA4IDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQy'
            'XQo+PgplbmRvYmoKOCAwIG9iago8PAovRm9udCA8PAovRjEgOSAwIFIKPj4KPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0xlbmd0aCA3IDAgUgovRmlsdGVyIC9GbGF0ZURlY29kZQo+Pgpz'
            'dHJlYW0KeJxNjkEOgCAMRPc9RS/QlBZQ7uHOW7iQxMQDON6+BYm6mZ9M+tOR2OD6NMR4QKBKTnCL4w0hYOVEmpzgGDPf1EKlhLBJotQKMVBFFClR4oc='
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
    """ Based on live/be/be-health-connect.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ECGSYS')
        msh.sending_facility = HD(hd_1='AZNIKOLAAS')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='AZNIKOLAAS')
        msh.date_time_of_message = '20250723091530+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ECG20250723091530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='445566778', cx_4='AZNIKOLAAS', cx_5='PI'), CX(cx_1='57031223456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Wouters^Roger^P^^^Dhr.'
        pid.date_time_of_birth = '19570312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stationsstraat 15', xad_3='Sint-Niklaas', xad_5='9100', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='ECG', pl_3='1', pl_4='AZNIKOLAAS')
        pv1.pv1_7 = 'DR110^Claes^Dirk^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250723001')
        orc.filler_order_number = EI(ei_1='ECG20250723001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250723001')
        obr.filler_order_number = EI(ei_1='ECG20250723001')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='ECG 12 afleiding', cwe_3='CPT4')
        obr.observation_date_time = '20250723090000+0200'
        obr.obr_15 = 'DR110^Claes^Dirk^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='8601-7', cwe_2='ECG interpretatie', cwe_3='LN')
        obx.obx_5 = 'Sinusritme, frequentie 72/min. Normale assen. Geen ST-afwijkingen. Normaal ECG.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11524-6', cwe_2='ECG', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            '^application^dicom^Base64^'
            'AAIAAAAASQ0BAAABAAcDAFMAAgABAAIACQBTCwACADEAFgAPAA8MFQAAAAAAAQQBAAAADxIBABAAEAQVABIAEgwVAAAAAAAAAAAAAQ8VABIAEAARFQAEAAQAER8AEAAQAAAAAAAARUNH'
            'IFdhdmVmb3JtIERhdGEgLSBBWiBOaWtvbGFhcyBDYXJkaW9sb2d5IERlcGFydG1lbnQgLSAxMiBMZWFkIFJlc3RpbmcgRUNHIC0gU2FtcGxlIFJhdGU6IDUwMCBIeiAtIER1cmF0aW9u'
            'OiAxMCBzZWNvbmRzIC0gTGVhZHM6IEksIElJLCBJSUksIGFWUiwgYVZMLCBhVkYsIFYxLCBWMiwgVjMsIFY0LCBWNSwgVjYgLSBBbXBsaXR1ZGU6IDEwIG1tL21WIC0gU3BlZWQ6IDI1'
            'IG1tL3MgLSBGaWx0ZXI6IDAuMDUtMTUwIEh6IC0gUGF0aWVudDogQ29wcGVucyBSb2dlciAtIEFjcXVpc2l0aW9uOiAyMDI1MDcyMyAwOTAwMDAuMDAwIC0gQ29uZmlybWVkOiBOb3Jt'
            'YWwgRUNHIC0gUmVmZXJyaW5nIFBoeXNpY2lhbjogRHIuIFZhbiBEYW1tZQ=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Hartfrequentie', cwe_3='LN')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='/min')
        obx_3.reference_range = '60-100'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8625-6', cwe_2='PR interval', cwe_3='LN')
        obx_4.obx_5 = '164'
        obx_4.units = CWE(cwe_1='ms')
        obx_4.reference_range = '120-200'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8633-0', cwe_2='QRS duur', cwe_3='LN')
        obx_5.obx_5 = '88'
        obx_5.units = CWE(cwe_1='ms')
        obx_5.reference_range = '60-110'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='8634-8', cwe_2='QTc interval', cwe_3='LN')
        obx_6.obx_5 = '412'
        obx_6.units = CWE(cwe_1='ms')
        obx_6.reference_range = '340-450'
        obx_6.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-health-connect.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTH')
        msh.sending_facility = HD(hd_1='BENAT')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='UZLEUVEN')
        msh.date_time_of_message = '20250201083045+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG20250201083045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250201083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='03020323456', cx_4='NISS', cx_5='NNNLD')
        pid.pid_5 = 'Coppens^Eline^F^^^Mevr.'
        pid.date_time_of_birth = '20030203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kuringersteenweg 55', xad_3='Hasselt', xad_5='3500', xad_6='BE', xad_7='H')
        pid.pid_13 = '011345678^PRN^PH~0486654321^PRN^CP'
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '03020323456^^^NISS'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'DR120^Janssens^Bart^^^Dr.^MD^^^^RIZIV&2.16.840.1.113883.3.6777.5.2&ISO^NIHDI'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/be/be-health-connect.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABFLOW')
        msh.sending_facility = HD(hd_1='AML')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20250115161234+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20250115161234001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='556677889', cx_4='AML', cx_5='PI'), CX(cx_1='99082023456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Mertens^Yannick^G^^^Dhr.'
        pid.date_time_of_birth = '19990820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bredabaan 88', xad_3='Merksem', xad_5='2170', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABO', pl_2='AFNAME', pl_3='1', pl_4='AML')
        pv1.pv1_7 = 'DR130^Peeters^Griet^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250115001')
        orc.filler_order_number = EI(ei_1='LAB20250115001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250115001')
        obr.filler_order_number = EI(ei_1='LAB20250115001')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA NAA+probe', cwe_3='LN')
        obr.observation_date_time = '20250115100000+0100'
        obr.obr_15 = 'DR130^Peeters^Griet^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA NAA+probe', cwe_3='LN')
        obx.obx_5 = '260415000^Not detected^SCT'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250115150000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='94746-5', cwe_2='SARS-CoV-2 RNA Ct', cwe_3='LN')
        obx_2.obx_5 = '0'
        obx_2.units = CWE(cwe_1='{Ct}')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250115150000+0100'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Methode: RT-PCR (Roche cobas SARS-CoV-2). Staal: Nasofaryngeaal uitstrijkje.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
    """ Based on live/be/be-health-connect.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PHARMA')
        msh.sending_facility = HD(hd_1='AZMARIAMID')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='AZMARIAMID')
        msh.date_time_of_message = '20250830142056+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'RX20250830142056001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='667788990', cx_4='AZMARIAMID', cx_5='PI'), CX(cx_1='62051523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Willems^Griet^Q^^^Mevr.'
        pid.date_time_of_birth = '19620515'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Coupure Links 44', xad_3='Gent', xad_5='9000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GERI', pl_2='401', pl_3='B', pl_4='AZMARIAMID')
        pv1.pv1_7 = 'DR140^Van Damme^Marc^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='RX20250830001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250830142000+0200'
        orc.orc_12 = 'DR140^Van Damme^Marc^^^Dr.^MD'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='AML05', cwe_2='Amlodipine 5mg', cwe_3='BCFI')
        rxo.requested_give_units = CWE(cwe_1='5')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='PO')
        rxo.providers_administration_instructions = CWE(cwe_1="1x per dag 's ochtends")
        rxo.allow_substitutions = 'G'
        rxo.requested_dispense_amount = '30'
        rxo.requested_dispense_units = CWE(cwe_1='TAB')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Per os', cwe_3='HL70162')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Hypertensie. Start amlodipine, geleidelijk ophogen indien nodig.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, nte]

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
    """ Based on live/be/be-health-connect.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHCONNECT')
        msh.sending_facility = HD(hd_1='AZVESALIUS')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='AZVESALIUS')
        msh.date_time_of_message = '20250228093015+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG20250228093015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250228093000'
        evn.operator_id = XCN(xcn_1='ADM02', xcn_2='Goossens', xcn_3='An')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='778899001', cx_4='AZVESALIUS', cx_5='PI'), CX(cx_1='80030123456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Claes^Stijn^U^^^Dhr.'
        pid.date_time_of_birth = '19800301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Maastrichterstraat 12', xad_3='Tongeren', xad_5='3700', xad_6='BE', xad_7='H')
        pid.pid_13 = '012456789^PRN^PH'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='778899000', cx_4='AZVESALIUS', cx_5='PI')

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
    """ Based on live/be/be-health-connect.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='JESSA')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='JESSA')
        msh.date_time_of_message = '20250605172030+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20250605172030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='889900112', cx_4='JESSA', cx_5='PI'), CX(cx_1='87111023456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Dupont^Sofie^J^^^Mevr.'
        pid.date_time_of_birth = '19871110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Thonissenlaan 8', xad_3='Hasselt', xad_5='3500', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='A', pl_4='JESSA')
        pv1.pv1_7 = 'DR150^Lambert^Jan^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20250605001')
        orc.filler_order_number = EI(ei_1='RAD20250605001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250605001')
        obr.filler_order_number = EI(ei_1='RAD20250605001')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI Hersenen met contrast', cwe_3='CPT4')
        obr.observation_date_time = '20250605140000+0200'
        obr.obr_15 = 'DR150^Lambert^Jan^^^Dr.^MD'
        obr.placer_field_1 = 'RAD20250605001'
        obr.filler_field_1 = 'CT'
        obr.diagnostic_serv_sect_id = '1^^^20250605143000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'MRI Hersenen met gadolinium\\.br\\\\.br\\Indicatie: Hoofdpijn, verdenking ruimte-innemend proces\\.br\\\\.br\\Bevindingen:\\.br\\- Geen intracra'
            'nieel ruimte-innemend proces\\.br\\- Geen afwijkend aankleuren na gadolinium\\.br\\- Ventrikelsysteem normaal van configuratie\\.br\\- Geen midl'
            'ine shift\\.br\\- Sinussen vrij belicht\\.br\\\\.br\\Conclusie: Normaal MRI onderzoek van de hersenen.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/be/be-health-connect.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='VACCINNET')
        msh.sending_facility = HD(hd_1='BENAT')
        msh.receiving_application = HD(hd_1='HEALTHCONNECT')
        msh.receiving_facility = HD(hd_1='HUISARTS')
        msh.date_time_of_message = '20250401111500+0200'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'VAX20250401111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='990011223', cx_4='VACCINNET', cx_5='PI'), CX(cx_1='04061523456', cx_4='NISS', cx_5='NNNLD')]
        pid.pid_5 = 'Maes^Noah^X^^^Dhr.'
        pid.date_time_of_birth = '20040615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stationsstraat 7', xad_3='Zoutleeuw', xad_5='3440', xad_6='BE', xad_7='H')
        pid.pid_13 = '011987654^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HUISARTS', pl_2='KABINET', pl_3='1')
        pv1.pv1_7 = 'DR160^Moreau^An^^^Dr.^MD'

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='VAX20250401001')
        orc.order_status = 'CM'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20250401110000+0200'
        rxa.administered_code = CWE(cwe_1='08', cwe_2='Hepatitis B', cwe_3='CVX')
        rxa.administered_amount = '1'
        rxa.administered_units = CWE(cwe_1='mL')
        rxa.administered_dosage_form = CWE(cwe_1='IM')
        rxa.administration_notes = CWE(cwe_1='ENGERIXB20', cwe_2='Engerix-B 20ug', cwe_3='LOCAL')
        rxa.administered_strength = 'GSK^GlaxoSmithKline^MVX'
        rxa.rxa_16 = 'BT20250301^20260301'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramusculair', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LD', cwe_2='Linker deltoideus', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Vaccine funding source', cwe_3='LN')
        obx.obx_5 = 'VXC1^Public^CDCPHINVS'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation

        # .. assemble the full message ..
        msg = VXU_V04()
        msg.msh = msh
        msg.pid = pid
        msg.patient_visit = patient_visit
        msg.order = order

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

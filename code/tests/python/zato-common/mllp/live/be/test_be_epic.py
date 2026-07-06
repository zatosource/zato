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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, DLD, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, SiuS12Resources, \
    SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIS, AL1, DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXA, RXO, RXR, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-epic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-epic.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250401142530+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG20250401142530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250401142500'
        evn.evn_5 = 'EMP002^Bogaert^Ilse^^^Mevr.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E23456789', cx_4='EPIC', cx_5='MR'), CX(cx_1='86021523456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Lies', xpn_3='M', xpn_5='Mevr.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bondgenotenlaan 22', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216345678^PRN^PH~+32476234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '86021523456^^^NISS'
        pid.birth_place = 'BE'
        pid.veterans_military_status = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7CARD', pl_2='7C-312', pl_3='A', pl_4='UZLGASTHUISBERG', pl_9='7CARD')
        pv1.pv1_7 = 'PRV001^Aerts^Koen^^^Dr.^MD^^^^EPIC^^^^RIZIV&2.16.840.1.113883.3.6777.5.2&ISO'
        pv1.pv1_8 = 'PRV002^Mertens^Leen^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='CAR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PRV001', cwe_2='Aerts', cwe_3='Koen', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ZIEKENFONDS')
        pv1.diet_type = CWE(cwe_1='UZLGASTHUISBERG')
        pv1.prior_temporary_location = PL(pl_1='20250401142500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acuut coronair syndroom')
        pv2.referral_source_code = XCN(xcn_1='2')
        pv2.special_program_code = CWE(cwe_1='20250401')
        pv2.retention_indicator = '20250408'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Peeters', xpn_2='Dirk', xpn_4='Dhr.', xpn_5='')
        nk1.address = XAD(xad_1='+3216765432', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'
        nk1.administrative_sex = CWE(cwe_1='M')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CM200', cwe_2='CM Brabant')
        in1.insurance_company_id = CX(cx_1='200')
        in1.insurance_company_name = XON(xon_1='Socialistische Mutualiteit')
        in1.authorization_information = AUI(aui_1='20250101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '200/23456789'

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='A001', cwe_2='Penicilline', cwe_3='EPIC')
        al1.allergy_reaction_code = 'Anafylactische reactie'
        al1.al1_6 = '20201115'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/be/be-epic.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250518091045+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG20250518091045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250518091000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='Epic')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E34567890', cx_4='EPIC', cx_5='MR'), CX(cx_1='93061834567', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Wout', xpn_3='D', xpn_5='Dhr.')
        pid.date_time_of_birth = '19930618'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tiensestraat 88', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216456789^PRN^PH~+32478345678^PRN^CP'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '93061834567^^^NISS'
        pid.birth_place = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='POLI-NEF-2', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV010^Van Damme^Luc^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='NEPH')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='PRV010', cwe_2='Van Damme', cwe_3='Luc', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='ZIEKENFONDS')
        pv1.discharged_to_location = DLD(dld_1='UZLGASTHUISBERG')
        pv1.pending_location = PL(pl_1='20250518090000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/be/be-epic.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250603152030+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EPICMSG20250603152030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250603152000'
        evn.evn_5 = 'EMP011^Wouters^Hilde^^^Mevr.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E45678901', cx_4='EPIC', cx_5='MR'), CX(cx_1='96050823456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Sofie', xpn_3='L', xpn_5='Mevr.')
        pid.date_time_of_birth = '19960508'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Vital Decosterstraat 55', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216567890^PRN^PH'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '96050823456^^^NISS'
        pid.birth_place = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OBST', pl_2='MAT-201', pl_3='B', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV020^Hendrickx^Pieter^^^Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='OB')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PRV020', cwe_2='Hendrickx', cwe_3='Pieter', cwe_6='Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ZIEKENFONDS')
        pv1.diet_type = CWE(cwe_1='UZLGASTHUISBERG')
        pv1.prior_temporary_location = PL(pl_1='20250531140000')
        pv1.current_patient_balance = '20250603152000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Bevalling spontaan', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250601'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z37.0', cwe_2='Eenling levend geboren', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20250601'
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
    """ Based on live/be/be-epic.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICLAB')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250715083045+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICLAB20250715083045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E56789012', cx_4='EPIC', cx_5='MR'), CX(cx_1='84071234567', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Stijn', xpn_3='R', xpn_5='Dhr.')
        pid.date_time_of_birth = '19840712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Diestsestraat 44', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216678901^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='6E-401', pl_3='A', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV030^Claes^Brigitte^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250715001')
        orc.filler_order_number = EI(ei_1='EPLAB20250715001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20250715074500+0200'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250715001')
        obr.filler_order_number = EI(ei_1='EPLAB20250715001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basic Metabolic Panel', cwe_3='LN')
        obr.observation_date_time = '20250715070000+0200'
        obr.obr_15 = 'PRV030^Claes^Brigitte^^^Prof.Dr.^MD'
        obr.filler_field_2 = '20250715082500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '145'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_2.obx_5 = '9.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '4.0-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_3.obx_5 = '0.95'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.7-1.3'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='14647-2', cwe_2='Cholesterol totaal', cwe_3='LN')
        obx_6.obx_5 = '248'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '<200'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='14646-4', cwe_2='HDL cholesterol', cwe_3='LN')
        obx_7.obx_5 = '38'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '>40'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250715080000+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL cholesterol', cwe_3='LN')
        obx_8.obx_5 = '165'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '<130'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250715080000+0200'

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
    """ Based on live/be/be-epic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICLAB')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250820103015+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICLAB20250820103015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E67890123', cx_4='EPIC', cx_5='MR'), CX(cx_1='77030923456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Willems', xpn_2='Griet', xpn_3='V', xpn_5='Mevr.')
        pid.date_time_of_birth = '19770309'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tervuursevest 100', xad_3='Heverlee', xad_5='3001', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216789012^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMA', pl_2='5H-501', pl_3='C', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV040^Lenaerts^Dirk^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250820001')
        orc.filler_order_number = EI(ei_1='EPLAB20250820001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250820001')
        obr.filler_order_number = EI(ei_1='EPLAB20250820001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20250820092000+0200'
        obr.obr_15 = 'PRV040^Lenaerts^Dirk^^^Prof.Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '42.5'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '2.85'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '3.80-5.20'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '8.2'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit', cwe_3='LN')
        obx_4.obx_5 = '24.8'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='LL')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '87.0'
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
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet', cwe_3='LN')
        obx_6.obx_5 = '45'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='LL')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='26464-8', cwe_2='WBC blasts', cwe_3='LN')
        obx_7.obx_5 = '72'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '0'
        obx_7.interpretation_codes = CWE(cwe_1='HH')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sterk afwijkend bloedbeeld. Morfologisch beeld compatibel met acute leukemie. Flowcytometrie ingezet.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/be/be-epic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250225153045+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPICORD20250225153045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E78901234', cx_4='EPIC', cx_5='MR'), CX(cx_1='91052534567', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Baert', xpn_2='Kevin', xpn_3='T', xpn_5='Dhr.')
        pid.date_time_of_birth = '19910525'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Naamsesteenweg 33', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216890123^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='SEH-BED-8', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV050^Raes^Pieter^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250225001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250225153000+0100'
        orc.orc_12 = 'PRV050^Raes^Pieter^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250225001')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='CT Angio thorax', cwe_3='CPT4')
        obr.observation_date_time = '20250225153000+0100'
        obr.obr_16 = 'PRV050^Raes^Pieter^^^Dr.^MD'
        obr.results_rpt_status_chng_date_time = 'CT'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Klinisch: acute dyspneu en thoracale pijn. D-dimeer 2.8 mg/L. Uitsluiten longembolie. Creatinine 0.8 mg/dL.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.9', cwe_2='Longembolie verdenking', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250225'
        dg1.diagnosis_type = CWE(cwe_1='W')

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
    """ Based on live/be/be-epic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250910081200+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPICORD20250910081200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E89012345', cx_4='EPIC', cx_5='MR'), CX(cx_1='98111523456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Thijs', xpn_2='Laura', xpn_3='N', xpn_5='Mevr.')
        pid.date_time_of_birth = '19981115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Minderbroedersstraat 11', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216901234^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='POLI-END-3', pl_3='2', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250910001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250910081000+0200'
        orc.orc_12 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250910001')
        obr.universal_service_identifier = CWE(cwe_1='83036', cwe_2='HbA1c', cwe_3='CPT4')
        obr.observation_date_time = '20250910081000+0200'
        obr.obr_16 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='EPORD20250910001')
        obr_2.universal_service_identifier = CWE(cwe_1='80061', cwe_2='Lipid panel', cwe_3='CPT4')
        obr_2.observation_date_time = '20250910081000+0200'
        obr_2.obr_16 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='EPORD20250910001')
        obr_3.universal_service_identifier = CWE(cwe_1='80053', cwe_2='CMP', cwe_3='CPT4')
        obr_3.observation_date_time = '20250910081000+0200'
        obr_3.obr_16 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='EPORD20250910001')
        obr_4.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH', cwe_3='CPT4')
        obr_4.observation_date_time = '20250910081000+0200'
        obr_4.obr_16 = 'PRV060^Coppens^Philippe^^^Prof.Dr.^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Controle diabetes type 2 en hypothyreoidie. Nuchter staal. Volgend consult 15/12/2025.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4, nte]

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
    """ Based on live/be/be-epic.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLPELLENBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLPELLENBERG')
        msh.date_time_of_message = '20250708094500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'EPICMSG20250708094500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250708094500'
        evn.operator_id = XCN(xcn_1='RECEP03', xcn_2='Wouters', xcn_3='Anja')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E90123456', cx_4='EPIC', cx_5='MR'), CX(cx_1='69030523456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Raes', xpn_2='Bart', xpn_3='W', xpn_5='Dhr.')
        pid.date_time_of_birth = '19690305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Schoolstraat 8', xad_3='Oud-Heverlee', xad_5='3050', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216012345^PRN^PH'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '69030523456^^^NISS'
        pid.birth_place = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='POLI-ORT-1', pl_3='3', pl_4='UZLPELLENBERG')
        pv1.pv1_7 = 'PRV070^Goossens^Marc^^^Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='ORTH')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='PRV070', cwe_2='Goossens', cwe_3='Marc', cwe_6='Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='ZIEKENFONDS')
        pv1.discharged_to_location = DLD(dld_1='UZLPELLENBERG')
        pv1.pending_location = PL(pl_1='20250708094500')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/be/be-epic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICLAB')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250903141530+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICLAB20250903141530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E01234567', cx_4='EPIC', cx_5='MR'), CX(cx_1='72081223456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='An', xpn_3='K', xpn_5='Mevr.')
        pid.date_time_of_birth = '19720812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Brusselsestraat 55', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216123456^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INFECT', pl_2='4I-601', pl_3='C', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV080^Nijs^Hilde^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250903001')
        orc.filler_order_number = EI(ei_1='EPLAB20250903001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250903001')
        obr.filler_order_number = EI(ei_1='EPLAB20250903001')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Blood culture', cwe_3='LN')
        obr.observation_date_time = '20250901080000+0200'
        obr.obr_15 = 'PRV080^Nijs^Hilde^^^Prof.Dr.^MD'
        obr.filler_field_2 = '20250903140000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Organism identified', cwe_3='LN')
        obx.obx_5 = 'STAUR^Staphylococcus aureus^EPIC'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Oxacilline', cwe_3='LN')
        obx_2.obx_5 = 'S^Gevoelig^EPIC'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Amoxicilline', cwe_3='LN')
        obx_3.obx_5 = 'R^Resistent^EPIC'
        obx_3.interpretation_codes = CWE(cwe_1='R')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Clindamycine', cwe_3='LN')
        obx_4.obx_5 = 'S^Gevoelig^EPIC'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18995-1', cwe_2='Vancomycine', cwe_3='LN')
        obx_5.obx_5 = 'S^Gevoelig^EPIC'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Trimethoprim-sulfamethoxazol', cwe_3='LN')
        obx_6.obx_5 = 'S^Gevoelig^EPIC'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='35659-2', cwe_2='Vancomycine MIC', cwe_3='LN')
        obx_7.obx_5 = '1.0'
        obx_7.units = CWE(cwe_1='mg/L')
        obx_7.reference_range = '<2'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'MSSA bloedkweek positief na 16u. Controlekweek ingezet. Echocardiografie aanbevolen ter uitsluiting endocarditis.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/be/be-epic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250415101200+0200'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EPICAPPT20250415101200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT20250415001')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Raadpleging nefrologie')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'min'
        sch.appointment_duration_units = CNE(cne_1='1')
        sch.sch_12 = 'PRV010^Van Damme^Luc^^^Dr.^MD'
        sch.sch_17 = 'PRV010^Van Damme^Luc^^^Dr.^MD'
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E34567890', cx_4='EPIC', cx_5='MR'), CX(cx_1='93061834567', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Wout', xpn_3='D', xpn_5='Dhr.')
        pid.date_time_of_birth = '19930618'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tiensestraat 88', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216456789^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='POLI-NEF-2', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV010^Van Damme^Luc^^^Dr.^MD'

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
        ais.universal_service_identifier = CWE(cwe_1='NEPHCONS', cwe_2='Nefrologie Consultatie', cwe_3='EPIC')
        ais.start_date_time = '20250502103000+0200'
        ais.start_date_time_offset_units = CNE(cne_1='30')
        ais.duration = 'min'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='NEFRO', pl_2='POLI-NEF-2', pl_3='1', pl_4='UZLGASTHUISBERG')
        ail.location_type_ail = CWE(cwe_1='20250502103000+0200')

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
    """ Based on live/be/be-epic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250512063015+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'EPICMSG20250512063015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250512063000'
        evn.evn_5 = 'EMP021^Hendrickx^Nathalie^^^Mevr.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E12345670', cx_4='EPIC', cx_5='MR'), CX(cx_1='75051823456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Claes', xpn_2='Francois', xpn_3='B', xpn_5='Dhr.')
        pid.date_time_of_birth = '19750518'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Celestijnenlaan 88', xad_3='Heverlee', xad_5='3001', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216223344^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIC', pl_2='3I-102', pl_3='A', pl_4='UZLGASTHUISBERG', pl_8='MIC')
        pv1.prior_patient_location = PL(pl_1='PRV090', pl_2='Thijs', pl_3='Jan', pl_6='Prof.Dr.', pl_7='MD')
        pv1.referring_doctor = XCN(xcn_1='INT')
        pv1.preadmit_test_indicator = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='PRV090', cwe_2='Thijs', cwe_3='Jan', cwe_6='Prof.Dr.', cwe_7='MD')
        pv1.vip_indicator = CWE(cwe_1='IN')
        pv1.patient_type = CWE(cwe_1='ZIEKENFONDS')
        pv1.discharge_disposition = CWE(cwe_1='UZLGASTHUISBERG')
        pv1.account_status = CWE(cwe_1='20250508120000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Transfer MIC naar afdeling inwendige', cwe_6='')
        pv2.previous_treatment_date = 'INT^4I-301^B^UZLGASTHUISBERG'

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
    """ Based on live/be/be-epic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICLAB')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250822163000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICPATH20250822163000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E22334455', cx_4='EPIC', cx_5='MR'), CX(cx_1='71092023456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Van Damme', xpn_2='Marc', xpn_3='S', xpn_5='Dhr.')
        pid.date_time_of_birth = '19710920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tiensestraat 7', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216334455^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='7C-301', pl_3='A', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV100^Wouters^Peter^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250822001')
        orc.filler_order_number = EI(ei_1='EPPATH20250822001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250822001')
        obr.filler_order_number = EI(ei_1='EPPATH20250822001')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Surgical pathology', cwe_3='CPT4')
        obr.observation_date_time = '20250819100000+0200'
        obr.obr_15 = 'PRV100^Wouters^Peter^^^Prof.Dr.^MD'
        obr.filler_field_2 = '20250822160000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Path report', cwe_3='LN')
        obx.obx_5 = (
            'ANATOMOPATHOLOGISCH VERSLAG\\.br\\\\.br\\Materiaal: Colonresectie rechts\\.br\\\\.br\\Macroscopie: Hemicolectomie rechts, 25 cm. Polipoide tumor in '
            'coecum, diameter 4.2 cm.\\.br\\\\.br\\Microscopie: Matig gedifferentieerd adenocarcinoom van het coecum, invasie tot in de subserosa (pT3). 18 l'
            'ymfeklieren onderzocht, 2 positief (pN1a). Resectieranden vrij.\\.br\\\\.br\\Conclusie: Adenocarcinoom coecum, pT3N1aM0, stadium IIIB. MSI testi'
            'ng wordt uitgevoerd.'
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
    """ Based on live/be/be-epic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='DOCMGMT')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250930111500+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'EPICDOC20250930111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250930111500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E33445566', cx_4='EPIC', cx_5='MR'), CX(cx_1='85061423456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mertens', xpn_2='Nele', xpn_3='H', xpn_5='Mevr.')
        pid.date_time_of_birth = '19850614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Parkstraat 15', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216445566^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PNEUMO', pl_2='POLI-PNE-2', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV110^Baert^Stefan^^^Prof.Dr.^MD'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Consultatieverslag', cwe_3='EPIC')
        txa.document_content_presentation = 'TX'
        txa.transcription_date_time = '20250930110000+0200'
        txa.txa_9 = 'PRV110^Baert^Stefan^^^Prof.Dr.^MD'
        txa.parent_document_number = EI(ei_1='EPICDOC-2025-11223')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11488-4', cwe_2='Consult note', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENvbnN1bHRhdGlldmVyc2xhZyBQbmV1bW9sb2dpZSAtIFVaIExldXZlbikKL0NyZWF0b3IgKEVwaWMgRG9jdW1lbnQgR2VuZXJhdG9y'
            'KQovUHJvZHVjZXIgKEVwaWMgMjAyNS4xIEJlbGdpdW0pCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTA5MzAxMTE1MDArMDInMDAnKQo+PgplbmRvYmoKQ09OU1VMVEFUSUVWRVJTTEFHIFBO'
            'RVVNT0xPR0lFCi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KRGF0dW06IDMwLzA5LzIwMjUKQXJ0czogUHJvZi4gRHIuIFZlcmxlZGVuIEdlZXJ0CgpQYXRpZW50OiBWYW5kZW5i'
            'dWxja2UgQW5uCkdlYm9vcnRlZGF0dW06IDE0LzA2LzE5ODMKUmlqa3NyZWdpc3Rlcm51bW1lcjogODMwNjE0MTIzNDUKCkFhbm1lbGRpbmdzcmVkZW46IENvbnRyb2xlIGFzdG1hCgpB'
            'bmFtbmVzZTogUGF0aWVudGUgbWVsZHQgdG9lbmVtZW5kZSBkeXNwbmV1IGJpaiBpbnNwYW5uaW5nLgpHZWVuIG5hY2h0ZWxpamtlIGtsYWNodGVuLiBHZWJydWlrdCBzYWxidXRhbW9s'
            'IDJ4L3dlZWsuCgpPbmRlcnpvZWs6IExvbmdhdXNjdWx0YXRpZTogdmVzaWN1bGFpciwgZ2VlbiB3aGVlemluZy4KU3Bpcm9tZXRyaWU6IEZFVjEgODUlIHZvb3JzcGVsZCwgRkVWMS9G'
            'VkMgNzYlLgoKQmVsZWlkOiBPcGhvZ2VuIElDUyBuYWFyIGJ1ZGVzb25pZGUgNDAwbWNnIDJ4L2RhZy4KQ29udHJvbGUgb3ZlciAzIG1hYW5kZW4uCg=='
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
    """ Based on live/be/be-epic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250615171245+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICRAD20250615171245001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E44556677', cx_4='EPIC', cx_5='MR'), CX(cx_1='58031223456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bogaert', xpn_2='Eddy', xpn_3='F', xpn_5='Dhr.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Parijsstraat 44', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216556677^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='RAD-CT-1', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV120^Maes^Geert^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250615001')
        orc.filler_order_number = EI(ei_1='EPRAD20250615001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250615001')
        obr.filler_order_number = EI(ei_1='EPRAD20250615001')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='CT angiography chest', cwe_3='CPT4')
        obr.observation_date_time = '20250615160000+0200'
        obr.obr_15 = 'PRV050^Raes^Pieter^^^Dr.^MD'
        obr.filler_field_2 = '20250615170000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'CT ANGIOGRAFIE THORAX\\.br\\\\.br\\Indicatie: Verdenking longembolie\\.br\\\\.br\\Techniek: CT thorax na IV toediening van 80ml Ultravist 370\\.br\\\\.'
            'br\\Bevindingen:\\.br\\- Bilaterale longembolieen in segmentele takken van rechter en linker onderlobarterie\\.br\\- Geen RV overbelasting\\.br\\- '
            'Geen pleuravocht\\.br\\- Longparenchym zonder afwijkingen\\.br\\- Mediastinale structuren normaal\\.br\\\\.br\\Conclusie: Bilaterale segmentele long'
            'embolieen zonder tekenen van rechts hartfalen.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Structured report', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='SR')
        obx_2.obx_5 = (
            '^application^dicom^Base64^'
            'U1IgRG9jdW1lbnQgLSBDVCBBbmdpb2dyYWZpZSBUaG9yYXgKLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCkRvY3VtZW50IFRpdGxlOiBDVCBBbmdpb2dyYWZpZSBUaG9yYXggLSBTdHJ1'
            'Y3R1cmVkIFJlcG9ydApEYXRlOiAyMDI1LTA2LTE1VDE3OjAwOjAwKzAyOjAwCkluc3RpdHV0aW9uOiBVWiBMZXV2ZW4gR2FzdGh1aXNiZXJnClN0dWR5IEluc3RhbmNlIFVJRDogMS4y'
            'LjI3Ni4wLjcyMzA3MTAuMy4xLjQuMjAyNjA2MTUuMjM0NTY3OApTZXJpZXMgSW5zdGFuY2UgVUlEOiAxLjIuMjc2LjAuNzIzMDcxMC4zLjEuNC4yMDI2MDYxNS45MDEyMzQ1ClNPUCBJ'
            'bnN0YW5jZSBVSUQ6IDEuMi4yNzYuMC43MjMwNzEwLjMuMS40LjIwMjYwNjE1LjY3ODkwMTIKCkZpbmRpbmdzOgotIExvY2F0aW9uOiBQdWxtb25hcnkgQXJ0ZXJ5IC0gU2VnbWVudGFs'
            'Ci0gTGF0ZXJhbGl0eTogQmlsYXRlcmFsCi0gU2V2ZXJpdHk6IE1vZGVyYXRlCi0gUlYvTFYgUmF0aW86IDAuODUgKE5vcm1hbCkKLSBQbGV1cmFsIEVmZnVzaW9uOiBOb25lCgpDb25j'
            'bHVzaW9uOiBCaWxhdGVyYWwgc2VnbWVudGFsIHB1bG1vbmFyeSBlbWJvbGlzbSB3aXRob3V0IHJpZ2h0IGhlYXJ0IHN0cmFpbi4='
        )
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
    """ Based on live/be/be-epic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTH')
        msh.sending_facility = HD(hd_1='BENAT')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250201083045+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'EPICMSG20250201083045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250201083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='02020323456', cx_4='NISS', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Wouters', xpn_2='Charlotte', xpn_3='J', xpn_5='Mevr.')
        pid.date_time_of_birth = '20040203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Naamsestraat 120', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216667788^PRN^PH~+32487654321^PRN^CP'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '02020323456^^^NISS'
        pid.birth_place = 'BE'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'PRV130^Hendrickx^Bart^^^Dr.^MD^^^^RIZIV&2.16.840.1.113883.3.6777.5.2&ISO^NIHDI'

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
    """ Based on live/be/be-epic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPICLAB')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250118151030+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICLAB20250118151030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E55667788', cx_4='EPIC', cx_5='MR'), CX(cx_1='99082023456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Claes', xpn_2='Pieter', xpn_3='E', xpn_5='Dhr.')
        pid.date_time_of_birth = '19990820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Celestijnenlaan 300', xad_3='Heverlee', xad_5='3001', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216778899^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='SEH-BED-3', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV140^Aerts^Marc^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250118001')
        orc.filler_order_number = EI(ei_1='EPLAB20250118001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250118001')
        obr.filler_order_number = EI(ei_1='EPLAB20250118001')
        obr.universal_service_identifier = CWE(cwe_1='95941-2', cwe_2='Resp virus panel NAA', cwe_3='LN')
        obr.observation_date_time = '20250118120000+0100'
        obr.obr_15 = 'PRV140^Aerts^Marc^^^Dr.^MD'
        obr.filler_field_2 = '20250118150000+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA', cwe_3='LN')
        obx.obx_5 = '260415000^Not detected^SCT'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='92142-9', cwe_2='Influenza A RNA', cwe_3='LN')
        obx_2.obx_5 = '260373001^Detected^SCT'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='92141-1', cwe_2='Influenza B RNA', cwe_3='LN')
        obx_3.obx_5 = '260415000^Not detected^SCT'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='92131-2', cwe_2='RSV RNA', cwe_3='LN')
        obx_4.obx_5 = '260415000^Not detected^SCT'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='92142-9', cwe_2='Influenza A subtype', cwe_3='LN')
        obx_5.obx_5 = 'H3N2'
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Influenza A H3N2 gedetecteerd. COVID-19 negatief. Oseltamivir overwegen indien <48u na symptomatologie.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-epic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='PHARMA')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250830142056+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPICRX20250830142056001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E66778899', cx_4='EPIC', cx_5='MR'), CX(cx_1='62051523456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Lenaerts', xpn_2='Lies', xpn_3='G', xpn_5='Mevr.')
        pid.date_time_of_birth = '19620515'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bondgenotenlaan 77', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216889900^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GERI', pl_2='6G-401', pl_3='B', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV150^Mertens^Erik^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPICRX20250830001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250830142000+0200'
        orc.orc_12 = 'PRV150^Mertens^Erik^^^Prof.Dr.^MD'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='J01CR02', cwe_2='Amoxicilline-clavulaanzuur', cwe_3='ATC')
        rxo.requested_give_units = CWE(cwe_1='1000/200')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='IV')
        rxo.providers_administration_instructions = CWE(cwe_1='3x per dag')
        rxo.allow_substitutions = 'G'
        rxo.requested_dispense_amount = '7'
        rxo.requested_dispense_units = CWE(cwe_1='DAG')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intraveneus', cwe_3='HL70162')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Community-acquired pneumonie. Empirische therapie conform lokaal antibiogram.'

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
    """ Based on live/be/be-epic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250228093015+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EPICMSG20250228093015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250228093000'
        evn.operator_id = XCN(xcn_1='ADM002', xcn_2='Peeters', xcn_3='Sofie')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E77889900', cx_4='EPIC', cx_5='MR'), CX(cx_1='81030123456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Aerts', xpn_2='Jan', xpn_3='P', xpn_5='Dhr.')
        pid.date_time_of_birth = '19810301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kardinaal Mercierlaan 22', xad_3='Heverlee', xad_5='3001', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216990011^PRN^PH'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='E77889011', cx_4='EPIC', cx_5='MR')
        mrg.mrg_2 = ''

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
    """ Based on live/be/be-epic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.date_time_of_message = '20250705172030+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICRAD20250705172030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E88990011', cx_4='EPIC', cx_5='MR'), CX(cx_1='88111023456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Rita', xpn_3='C', xpn_5='Mevr.')
        pid.date_time_of_birth = '19881110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Arenbergpark 3', xad_3='Heverlee', xad_5='3001', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216001122^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='4N-501', pl_3='A', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV160^Willems^Dirk^^^Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='EPORD20250705001')
        orc.filler_order_number = EI(ei_1='EPRAD20250705001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EPORD20250705001')
        obr.filler_order_number = EI(ei_1='EPRAD20250705001')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI Brain with contrast', cwe_3='CPT4')
        obr.observation_date_time = '20250705140000+0200'
        obr.obr_15 = 'PRV160^Willems^Dirk^^^Prof.Dr.^MD'
        obr.filler_field_2 = '20250705170000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'MRI HERSENEN MET GADOLINIUM\\.br\\\\.br\\Indicatie: Epilepsie. Zoeken naar structurele oorzaak.\\.br\\\\.br\\Techniek: 3T MRI met T1, T2, FLAIR, DWI'
            ' en post-contrast T1 sequenties.\\.br\\\\.br\\Bevindingen:\\.br\\- Kleine FLAIR hyperintense laesie rechts mesiotemporaal, 12x8mm\\.br\\- Geen patho'
            'logisch aankleuren\\.br\\- Lichte hippocampale asymmetrie rechts < links\\.br\\- Geen andere intracraniële afwijkingen\\.br\\- Ventrikelsysteem sy'
            'mmetrisch, normale afmetingen\\.br\\\\.br\\Conclusie: Rechts mesiotemporale laesie compatibel met hippocampale sclerose. Correleren met kliniek '
            'en EEG.'
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
    """ Based on live/be/be-epic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UZLGASTHUISBERG')
        msh.receiving_application = HD(hd_1='VACCINNET')
        msh.receiving_facility = HD(hd_1='BENAT')
        msh.date_time_of_message = '20250401111500+0200'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'EPICVAX20250401111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E99001122', cx_4='EPIC', cx_5='MR'), CX(cx_1='05061523456', cx_4='NISS', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Hendrickx', xpn_2='Arthur', xpn_3='W', xpn_5='Dhr.')
        pid.date_time_of_birth = '20050615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vital Decosterstraat 18', xad_3='Leuven', xad_5='3000', xad_6='BE', xad_7='H')
        pid.pid_13 = '+3216112233^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='VAC', pl_2='VAC-1', pl_3='1', pl_4='UZLGASTHUISBERG')
        pv1.pv1_7 = 'PRV170^Maes^Griet^^^Dr.^MD'

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EPICVAX20250401001')
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
        rxa.administration_notes = CWE(cwe_1='ENGERIXB20', cwe_2='Engerix-B 20mcg', cwe_3='LOCAL')
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

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='30956-7', cwe_2='VFC eligibility', cwe_3='LN')
        obx_2.obx_5 = 'V01^Not eligible^HL70064'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Boostervaccinatie Hepatitis B. Registratie via Vaccinnet+.'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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

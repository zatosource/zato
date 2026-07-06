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
from zato.hl7v2.v2_9.datatypes import AUI, CWE, CX, DLD, EI, HD, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA05NextOfKin, AdtA39Patient, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-meierhofer-mkis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-meierhofer-mkis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250415082000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MKISMSG202504150820000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250415082000'
        evn.evn_5 = 'MK001^Doppler^Elfriede^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstrasse 45', xad_3='Linz', xad_5='4020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+43732654321^PRN^PH~+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6782030578^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ', pl_9='INNMED2')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD^^^^ORDKLINLINZ^^^^OAEK&2.16.840.1.113883.2.16.1.4&ISO'
        pv1.pv1_8 = 'MK0088^Fink^Rosemarie^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='MK0042', cwe_2='Kastner', cwe_3='Siegfried', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='ORDKLINLINZ')
        pv1.prior_temporary_location = PL(pl_1='20250415082000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Herzinsuffizienz NYHA III')
        pv2.referral_source_code = XCN(xcn_1='3')
        pv2.special_program_code = CWE(cwe_1='20250415')
        pv2.retention_indicator = '20250422'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Gruber', xpn_2='Hilda', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+43732654322', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'SPO'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='OEGK', cwe_2='OeGK Oberoesterreich')
        in1.insurance_company_id = CX(cx_1='109')
        in1.insurance_company_name = XON(xon_1='Oesterreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20250101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '6782030578'

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='B01', cwe_2='Amoxicillin', cwe_3='MKIS')
        al1.allergy_reaction_code = 'Exanthem'
        al1.al1_6 = '20200315'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Herzinsuffizienz kongestiv', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250415'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1, al1, dg1]

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='BHSRIED')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='BHSRIED')
        msh.date_time_of_message = '20250520101500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MKISMSG202505201015000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250520101500'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='MKIS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00234567', cx_4='BHSRIED', cx_5='PI'), CX(cx_1='8921041285', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Anneliese', xpn_3='Margit', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bahnhofstrasse 18', xad_3='Ried im Innkreis', xad_5='4910', xad_6='AT', xad_7='H')
        pid.pid_13 = '+437752123456^PRN^PH~+436769876543^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '8921041285^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='305', pl_3='B', pl_4='BHSRIED')
        pv1.pv1_7 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='MK0110', cwe_2='Holzer', cwe_3='Bernhard', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='BHSRIED')
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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='KSKSCHWAR')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='KSKSCHWAR')
        msh.date_time_of_message = '20250610150000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MKISMSG202506101500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250610150000'
        evn.evn_5 = 'MK020^Ortner^Dagmar^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00345678', cx_4='KSKSCHWAR', cx_5='PI'), CX(cx_1='5134070872', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Rudolf', xpn_3='Konrad', xpn_5='Herr')
        pid.date_time_of_birth = '19720807'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktplatz 5', xad_3='Schwarzach im Pongau', xad_5='5620', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234568^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5134070872^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='102', pl_3='A', pl_4='KSKSCHWAR', pl_9='ORTHO')
        pv1.pv1_7 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='ORT')
        pv1.re_admission_indicator = CWE(cwe_1='5')
        pv1.vip_indicator = CWE(cwe_1='MK0205', cwe_2='Wimmer', cwe_3='Erich', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='KSKSCHWAR')
        pv1.prior_temporary_location = PL(pl_1='20250605080000')
        pv1.current_patient_balance = '20250610150000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M17.1', cwe_2='Sonstige primaere Gonarthrose', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250605'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z96.65', cwe_2='Zustand nach Kniegelenksprothese', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20250606'
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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250418064500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MKISMSG202504180645000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250418064500'
        evn.evn_5 = 'MK030^Riegler^Sonja^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstrasse 45', xad_3='Linz', xad_5='4020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6782030578^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ', pl_9='INNMED2')
        pv1.prior_patient_location = PL(pl_1='ICU', pl_2='ICU-3', pl_3='1', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        pv1.pv1_8 = 'MK0088^Fink^Rosemarie^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='MK0042', cwe_2='Kastner', cwe_3='Siegfried', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='ORDKLINLINZ')
        pv1.prior_temporary_location = PL(pl_1='20250415082000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='REHAENNS')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='REHAENNS')
        msh.date_time_of_message = '20250701080000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MKISMSG202507010800000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250701080000'
        evn.evn_5 = 'MK040^Stadler^Karin^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00456789', cx_4='REHAENNS', cx_5='PI'), CX(cx_1='7293200690', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Theresia', xpn_3='Waltraud', xpn_5='Frau')
        pid.date_time_of_birth = '19900620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hauptplatz 3', xad_3='Enns', xad_5='4470', xad_6='AT', xad_7='H')
        pid.pid_13 = '+437223654321^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7293200690^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REHA', pl_2='AMB-RE-1', pl_3='1', pl_4='REHAENNS')
        pv1.pv1_7 = 'MK0310^Lechner^Norbert^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='REH')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='MK0310', cwe_2='Lechner', cwe_3='Norbert', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='REHAENNS')
        pv1.pending_location = PL(pl_1='20250701080000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250415090000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MKISORD202504150900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250415001')
        orc.filler_order_number = EI(ei_1='MKLAB20250415001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250415090000+0200'
        orc.orc_12 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250415001')
        obr.filler_order_number = EI(ei_1='MKLAB20250415001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Metabolisches Basispanel', cwe_3='LN')
        obr.observation_date_time = '20250415083000+0200'
        obr.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='MKORD20250415002')
        obr_2.filler_order_number = EI(ei_1='MKLAB20250415002')
        obr_2.universal_service_identifier = CWE(cwe_1='2085-9', cwe_2='BNP', cwe_3='LN')
        obr_2.observation_date_time = '20250415083000+0200'
        obr_2.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250415113000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKLAB202504151130000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250415001')
        orc.filler_order_number = EI(ei_1='MKLAB20250415001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250415001')
        obr.filler_order_number = EI(ei_1='MKLAB20250415001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Metabolisches Basispanel', cwe_3='LN')
        obr.observation_date_time = '20250415083000+0200'
        obr.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250415112500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250415100000+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '1.4'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250415100000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Harnstoff-N', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250415100000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '134'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250415100000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.8'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250415100000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2085-9', cwe_2='BNP', cwe_3='LN')
        obx_6.obx_5 = '1850'
        obx_6.units = CWE(cwe_1='pg/mL')
        obx_6.reference_range = '<100'
        obx_6.interpretation_codes = CWE(cwe_1='HH')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250415100000+0200'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'BNP deutlich erhoeht, passend zu schwerer Herzinsuffizienz.'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='BHSRIED')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='BHSRIED')
        msh.date_time_of_message = '20250520130000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKLAB202505201300000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00234567', cx_4='BHSRIED', cx_5='PI'), CX(cx_1='8921041285', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Anneliese', xpn_3='Margit', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='305', pl_3='B', pl_4='BHSRIED')
        pv1.pv1_7 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250520001')
        orc.filler_order_number = EI(ei_1='MKLAB20250520001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250520001')
        obr.filler_order_number = EI(ei_1='MKLAB20250520001')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC mit Diff', cwe_3='LN')
        obr.observation_date_time = '20250520070000+0200'
        obr.obr_15 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250520125000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '4.10'
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
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx_3.obx_5 = '11.5'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Haematokrit', cwe_3='LN')
        obx_4.obx_5 = '34.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '83.4'
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
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Thrombozyten', cwe_3='LN')
        obx_6.obx_5 = '310'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='751-8', cwe_2='Neutrophile abs', cwe_3='LN')
        obx_7.obx_5 = '9.6'
        obx_7.units = CWE(cwe_1='10*9/L')
        obx_7.reference_range = '2.0-7.5'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Leukozytose mit Neutrophilie, postoperativ. Kontrolle empfohlen.'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='KSKSCHWAR')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KSKSCHWAR')
        msh.date_time_of_message = '20250606091500+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MKISORD202506060915000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00345678', cx_4='KSKSCHWAR', cx_5='PI'), CX(cx_1='5134070872', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Rudolf', xpn_3='Konrad', xpn_5='Herr')
        pid.date_time_of_birth = '19720807'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='102', pl_3='A', pl_4='KSKSCHWAR')
        pv1.pv1_7 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250606001')
        orc.filler_order_number = EI(ei_1='MKFIL20250606001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250606091500+0200'
        orc.orc_12 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250606001')
        obr.filler_order_number = EI(ei_1='MKFIL20250606001')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Roentgen Thorax 2 Ebenen', cwe_3='MKRAD')
        obr.observation_date_time = '20250606091500+0200'
        obr.obr_15 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'
        obr.obr_17 = 'ACC20250606001'
        obr.diagnostic_serv_sect_id = 'CR'
        obr.obr_35 = '71020^Roentgen Thorax 2 Ebenen^MKRAD'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='KSKSCHWAR')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='KSKSCHWAR')
        msh.date_time_of_message = '20250606143000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKRAD202506061430000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00345678', cx_4='KSKSCHWAR', cx_5='PI'), CX(cx_1='5134070872', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Rudolf', xpn_3='Konrad', xpn_5='Herr')
        pid.date_time_of_birth = '19720807'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='102', pl_3='A', pl_4='KSKSCHWAR')
        pv1.pv1_7 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250606001')
        orc.filler_order_number = EI(ei_1='MKFIL20250606001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250606001')
        obr.filler_order_number = EI(ei_1='MKFIL20250606001')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Roentgen Thorax 2 Ebenen', cwe_3='MKRAD')
        obr.observation_date_time = '20250606091500+0200'
        obr.obr_15 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'
        obr.obr_17 = 'ACC20250606001'
        obr.diagnostic_serv_sect_id = 'CR'
        obr.parent_result = PRL(prl_1='20250606142500+0200')
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71020', cwe_2='Roentgen Thorax', cwe_3='MKRAD')
        obx.obx_5 = (
            'Befund:\\.br\\Roentgen Thorax in 2 Ebenen\\.br\\\\.br\\Herz normal gross und konfiguriert. Kein Perikarderguss.\\.br\\Lunge beidseits belüftet, '
            'keine Infiltrate. Kein Pleuraerguss.\\.br\\Kein Pneumothorax.\\.br\\Zwerchfelle glatt begrenzt.\\.br\\Praeoperativer Normalbefund.'
        )
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='71020-PDF', cwe_2='Roentgen Thorax Befund', cwe_3='MKRAD')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4'
            'cmVmCjIwNgolJUVPRgo='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250606142500+0200'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250801090000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MKISMSG202508010900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250801090000'
        evn.evn_5 = 'MK050^Wallner^Sabine^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00567890', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='3415031080', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wagner', xpn_2='Manfred', xpn_3='Herbert', xpn_5='Herr')
        pid.date_time_of_birth = '19801003'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mozartstrasse 12', xad_3='Linz', xad_5='4020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436651234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '3415031080^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MK00567891', cx_4='ORDKLINLINZ', cx_5='PI')

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250416080000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKLAB202504160800000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250416001')
        orc.filler_order_number = EI(ei_1='MKLAB20250416001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250416001')
        obr.filler_order_number = EI(ei_1='MKLAB20250416001')
        obr.universal_service_identifier = CWE(cwe_1='85610-3', cwe_2='Gerinnungspanel', cwe_3='LN')
        obr.observation_date_time = '20250416060000+0200'
        obr.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250416075000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombinzeit (Quick)', cwe_3='LN')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '70-130'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.4'
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25-37'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '480'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '180-350'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='718-7', cwe_2='D-Dimer', cwe_3='LN')
        obx_5.obx_5 = '2.4'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '<0.5'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Erhoehter D-Dimer. Klinisch Lungenembolie ausschliessen.'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='REHAENNS')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='REHAENNS')
        msh.date_time_of_message = '20250630140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MKISMSG202506301400000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250630140000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='MKIS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00456789', cx_4='REHAENNS', cx_5='PI'), CX(cx_1='7293200690', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Theresia', xpn_3='Waltraud', xpn_5='Frau')
        pid.date_time_of_birth = '19900620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hauptplatz 3', xad_3='Enns', xad_5='4470', xad_6='AT', xad_7='H')
        pid.pid_13 = '+437223654321^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7293200690^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Moser', xpn_2='Walter', xpn_4='Herr', xpn_5='')
        nk1.address = XAD(xad_1='+437223654322', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'SPO'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BGASYS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250416143000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKBGA202504161430000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='ICU-3', pl_3='1', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250416BGA')
        orc.filler_order_number = EI(ei_1='MKBGA20250416001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250416BGA')
        obr.filler_order_number = EI(ei_1='MKBGA20250416001')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Blutgasanalyse arteriell', cwe_3='LN')
        obr.observation_date_time = '20250416142500+0200'
        obr.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250416142800+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arteriell', cwe_3='LN')
        obx.obx_5 = '7.38'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '42'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bikarbonat', cwe_3='LN')
        obx_4.obx_5 = '24.5'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Base Excess', cwe_3='LN')
        obx_5.obx_5 = '-0.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='20563-3', cwe_2='Laktat', cwe_3='LN')
        obx_6.obx_5 = '1.2'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '0.5-2.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2713-6', cwe_2='Sauerstoffsaettigung', cwe_3='LN')
        obx_7.obx_5 = '94.5'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '95.0-99.0'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENDOSYS')
        msh.sending_facility = HD(hd_1='BHSRIED')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='BHSRIED')
        msh.date_time_of_message = '20250522110000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKENDO202505221100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00234567', cx_4='BHSRIED', cx_5='PI'), CX(cx_1='8921041285', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Anneliese', xpn_3='Margit', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='305', pl_3='B', pl_4='BHSRIED')
        pv1.pv1_7 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250522001')
        orc.filler_order_number = EI(ei_1='MKENDO20250522001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250522001')
        obr.filler_order_number = EI(ei_1='MKENDO20250522001')
        obr.universal_service_identifier = CWE(cwe_1='43239-9', cwe_2='Oesophagogastroduodenoskopie', cwe_3='LN')
        obr.observation_date_time = '20250522090000+0200'
        obr.obr_15 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250522105000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='43239-9', cwe_2='OeGD Befund', cwe_3='LN')
        obx.obx_5 = (
            'Befund:\\.br\\Oesophagogastroduodenoskopie\\.br\\\\.br\\Oesophagus: Unauffaellige Schleimhaut, kein Barrett.\\.br\\Magen: Antrum mit leichter Er'
            'ythemgastritis. Keine Erosionen oder Ulcera.\\.br\\Duodenum: Bulbus und Pars descendens unauffaellig.\\.br\\\\.br\\Biopsie: 2x Antrum zur HP-Dia'
            'gnostik entnommen.\\.br\\Diagnose: Leichte Antrumgastritis.'
        )
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='43239-9-IMG', cwe_2='Endoskopie Antrum', cwe_3='MKENDO')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2f/2wBDARESEhgVGC8aGC9n'
            'QTtBZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2f/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAFRABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQD/2Q=='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250522105000+0200'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250422071500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = 'MKISMSG202504220715000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250422071500'
        evn.evn_5 = 'MK060^Strobl^Barbara^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstrasse 45', xad_3='Linz', xad_5='4020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6782030578^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ', pl_9='INNMED2')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='MK0042', cwe_2='Kastner', cwe_3='Siegfried', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='ORDKLINLINZ')
        pv1.prior_temporary_location = PL(pl_1='20250415082000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250417093000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKLAB202504170930000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM2', pl_2='201', pl_3='A', pl_4='ORDKLINLINZ')
        pv1.pv1_7 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250417001')
        orc.filler_order_number = EI(ei_1='MKLAB20250417001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250417001')
        obr.filler_order_number = EI(ei_1='MKLAB20250417001')
        obr.universal_service_identifier = CWE(cwe_1='71426-1', cwe_2='Kardiale Marker', cwe_3='LN')
        obr.observation_date_time = '20250417060000+0200'
        obr.obr_15 = 'MK0042^Kastner^Siegfried^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250417092000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin T hs', cwe_3='LN')
        obx.obx_5 = '0.028'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '<0.014'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30522-7', cwe_2='CRP', cwe_3='LN')
        obx_2.obx_5 = '45.2'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.reference_range = '<5.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='BNP', cwe_3='LN')
        obx_3.obx_5 = '1420'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '<100'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='14804-9', cwe_2='LDH', cwe_3='LN')
        obx_4.obx_5 = '280'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '<250'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2157-6', cwe_2='CK', cwe_3='LN')
        obx_5.obx_5 = '195'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '<190'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='13969-1', cwe_2='CK-MB', cwe_3='LN')
        obx_6.obx_5 = '32'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '<24'
        obx_6.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='KSKSCHWAR')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KSKSCHWAR')
        msh.date_time_of_message = '20250604100000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MKISORD202506041000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00345678', cx_4='KSKSCHWAR', cx_5='PI'), CX(cx_1='5134070872', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Rudolf', xpn_3='Konrad', xpn_5='Herr')
        pid.date_time_of_birth = '19720807'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='102', pl_3='A', pl_4='KSKSCHWAR')
        pv1.pv1_7 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250604001')
        orc.filler_order_number = EI(ei_1='MKFIL20250604001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250604100000+0200'
        orc.orc_12 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250604001')
        obr.filler_order_number = EI(ei_1='MKFIL20250604001')
        obr.universal_service_identifier = CWE(cwe_1='73721', cwe_2='MRT Knie rechts ohne KM', cwe_3='MKRAD')
        obr.observation_date_time = '20250604100000+0200'
        obr.obr_15 = 'MK0205^Wimmer^Erich^^^Prim.Dr.^MD'
        obr.obr_17 = 'ACC20250604001'
        obr.diagnostic_serv_sect_id = 'MR'
        obr.obr_35 = '73721^MRT Knie rechts ohne KM^MKRAD'

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MKIS')
        msh.sending_facility = HD(hd_1='ORDKLINLINZ')
        msh.receiving_application = HD(hd_1='MIRTH')
        msh.receiving_facility = HD(hd_1='ORDKLINLINZ')
        msh.date_time_of_message = '20250901140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MKISMSG202509011400000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250901140000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='MKIS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00123456', cx_4='ORDKLINLINZ', cx_5='PI'), CX(cx_1='6782030578', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Georg', xpn_3='Friedrich', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herrenstrasse 22', xad_3='Linz', xad_5='4020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+43732654321^PRN^PH~+436641234567^PRN^CP~georg.gruber@gmx.at^NET^X.400'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6782030578^^^SV-AT'
        pid.birth_place = 'AT'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-meierhofer-mkis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='BHSRIED')
        msh.receiving_application = HD(hd_1='MKIS')
        msh.receiving_facility = HD(hd_1='BHSRIED')
        msh.date_time_of_message = '20250523150000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MKMIK202505231500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MK00234567', cx_4='BHSRIED', cx_5='PI'), CX(cx_1='8921041285', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Anneliese', xpn_3='Margit', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='305', pl_3='B', pl_4='BHSRIED')
        pv1.pv1_7 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='MKORD20250523001')
        orc.filler_order_number = EI(ei_1='MKMIK20250523001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MKORD20250523001')
        obr.filler_order_number = EI(ei_1='MKMIK20250523001')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Wundabstrich Kultur', cwe_3='LN')
        obr.observation_date_time = '20250521100000+0200'
        obr.obr_15 = 'MK0110^Holzer^Bernhard^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250523145000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Wundabstrich Kultur', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli^Escherichia coli^SNOMED'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramm', cwe_3='LN')
        obx_2.obx_5 = 'Ampicillin: resistent (R), Cefuroxim: sensibel (S), Ciprofloxacin: sensibel (S), Cotrimoxazol: sensibel (S), Gentamicin: sensibel (S)'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='ESBL-Nachweis', cwe_3='LN')
        obx_3.obx_5 = 'ESBL negativ'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Kein ESBL-Nachweis. Kalkulierte Therapie mit Cefuroxim empfohlen.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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

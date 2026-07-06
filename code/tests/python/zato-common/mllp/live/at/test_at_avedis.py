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
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-avedis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-avedis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250310081500+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'AVMSG202503100815000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250310081500'
        evn.evn_5 = 'AV001^Maier^Renate^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bruenner Strasse 68', xad_3='Wien', xad_5='1210', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4312701234^PRN^PH~+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5829030175^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD', pl_9='UNFCHIR')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD^^^^KLINFLORIDSD^^^^OAEK&2.16.840.1.113883.2.16.1.4&ISO'
        pv1.pv1_8 = 'AV0088^Resch^Harald^^^OA.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AV0042', cwe_2='Gaebler', cwe_3='Christian', cwe_6='Prim.Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='KLINFLORIDSD')
        pv1.prior_temporary_location = PL(pl_1='20250310081500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Fraktur distaler Radius rechts')
        pv2.referral_source_code = XCN(xcn_1='2')
        pv2.special_program_code = CWE(cwe_1='20250310')
        pv2.retention_indicator = '20250314'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Mayer', xpn_2='Barbara', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+436641234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'SPO'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='OEGK', cwe_2='OeGK Wien')
        in1.insurance_company_id = CX(cx_1='101')
        in1.insurance_company_name = XON(xon_1='Oesterreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20250101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '5829030175'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S52.50', cwe_2='Distale Radiusfraktur rechts', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1, dg1]

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
    """ Based on live/at/at-avedis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250425102000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'AVMSG202504251020000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250425102000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='Avedis')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Thaliastrasse 125', xad_3='Wien', xad_5='1160', xad_6='AT', xad_7='H')
        pid.pid_13 = '+431491234^PRN^PH~+436769876543^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7143150888^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AV0110', cwe_2='Watzinger', cwe_3='Nikolaus', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='KLINOTTAKR')
        pv1.pending_location = PL(pl_1='20250423080000')

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
    """ Based on live/at/at-avedis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFAVOR')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINFAVOR')
        msh.date_time_of_message = '20250530153000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'AVMSG202505301530000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250530153000'
        evn.evn_5 = 'AV020^Wolf^Michaela^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00345678', cx_4='KLINFAVOR', cx_5='PI'), CX(cx_1='9261181190', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Fuchs', xpn_2='Katharina', xpn_3='E', xpn_5='Frau')
        pid.date_time_of_birth = '19901118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kempelengasse 11', xad_3='Wien', xad_5='1100', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4316011234^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '9261181190^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='G401', pl_3='A', pl_4='KLINFAVOR', pl_9='GYN')
        pv1.pv1_7 = 'AV0205^Hefler-Frischmuth^Lukas^^^Prim.Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='GYN')
        pv1.re_admission_indicator = CWE(cwe_1='3')
        pv1.vip_indicator = CWE(cwe_1='AV0205', cwe_2='Hefler-Frischmuth', cwe_3='Lukas', cwe_6='Prim.Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='KLINFAVOR')
        pv1.prior_temporary_location = PL(pl_1='20250527090000')
        pv1.current_patient_balance = '20250530153000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='D25.1', cwe_2='Intramurales Leiomyom des Uterus', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250528'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z96.8', cwe_2='Zustand nach laparoskopischer Myomektomie', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20250528'
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
    """ Based on live/at/at-avedis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250312064500+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'AVMSG202503120645000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250312064500'
        evn.evn_5 = 'AV030^Lechner^Ingrid^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bruenner Strasse 68', xad_3='Wien', xad_5='1210', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5829030175^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U310', pl_3='C', pl_4='KLINFLORIDSD', pl_9='UNFCHIR')
        pv1.prior_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'
        pv1.pv1_8 = 'AV0088^Resch^Harald^^^OA.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AV0042', cwe_2='Gaebler', cwe_3='Christian', cwe_6='Prim.Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='KLINFLORIDSD')
        pv1.prior_temporary_location = PL(pl_1='20250310081500')

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
    """ Based on live/at/at-avedis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINHIETZING')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINHIETZING')
        msh.date_time_of_message = '20250715083000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'AVMSG202507150830000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250715083000'
        evn.evn_5 = 'AV040^Schwarz^Brigitte^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00456789', cx_4='KLINHIETZING', cx_5='PI'), CX(cx_1='4035220695', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Berger', xpn_2='Claudia', xpn_3='N', xpn_5='Frau')
        pid.date_time_of_birth = '19950622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hietzinger Kai 2', xad_3='Wien', xad_5='1130', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4318801234^PRN^PH~+436601234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4035220695^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='AMB-DER-2', pl_3='1', pl_4='KLINHIETZING')
        pv1.pv1_7 = 'AV0310^Gschnait^Friedrich^^^Prim.Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='DER')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='AV0310', cwe_2='Gschnait', cwe_3='Friedrich', cwe_6='Prim.Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='KLINHIETZING')
        pv1.pending_location = PL(pl_1='20250715083000')

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
    """ Based on live/at/at-avedis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250425090000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AVORD202504250900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250425001')
        orc.filler_order_number = EI(ei_1='AVLAB20250425001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250425090000+0200'
        orc.orc_12 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250425001')
        obr.filler_order_number = EI(ei_1='AVLAB20250425001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Metabolisches Basispanel', cwe_3='LN')
        obr.observation_date_time = '20250425083000+0200'
        obr.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='AVORD20250425002')
        obr_2.filler_order_number = EI(ei_1='AVLAB20250425002')
        obr_2.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr_2.observation_date_time = '20250425083000+0200'
        obr_2.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
    """ Based on live/at/at-avedis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250425123000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVLAB202504251230000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250425001')
        orc.filler_order_number = EI(ei_1='AVLAB20250425001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250425001')
        obr.filler_order_number = EI(ei_1='AVLAB20250425001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Metabolisches Basispanel', cwe_3='LN')
        obr.observation_date_time = '20250425083000+0200'
        obr.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250425122000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_2.obx_5 = '8.9'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '4.0-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_3.obx_5 = '0.85'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.7-1.3'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '3.2'
        obx_6.units = CWE(cwe_1='g/dL')
        obx_6.reference_range = '3.5-5.0'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterin gesamt', cwe_3='LN')
        obx_7.obx_5 = '230'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '<200'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250425110000+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglyzeride', cwe_3='LN')
        obx_8.obx_5 = '210'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '<150'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250425110000+0200'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Diabetes mellitus schlecht eingestellt. HbA1c und Nuechternglukose deutlich erhoeht.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/at/at-avedis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250310100000+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AVORD202503101000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250310001')
        orc.filler_order_number = EI(ei_1='AVFIL20250310001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250310100000+0100'
        orc.orc_12 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250310001')
        obr.filler_order_number = EI(ei_1='AVFIL20250310001')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT Schaedel nativ', cwe_3='AVRAD')
        obr.observation_date_time = '20250310100000+0100'
        obr.obr_15 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'
        obr.obr_17 = 'ACC20250310001'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.obr_35 = '70450^CT Schaedel nativ^AVRAD'

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
    """ Based on live/at/at-avedis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250310133000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVRAD202503101330000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250310001')
        orc.filler_order_number = EI(ei_1='AVFIL20250310001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250310001')
        obr.filler_order_number = EI(ei_1='AVFIL20250310001')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT Schaedel nativ', cwe_3='AVRAD')
        obr.observation_date_time = '20250310100000+0100'
        obr.obr_15 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'
        obr.obr_17 = 'ACC20250310001'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.parent_result = PRL(prl_1='20250310132500+0100')
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='70450', cwe_2='CT Schaedel nativ', cwe_3='AVRAD')
        obx.obx_5 = (
            'Befund:\\.br\\CT Schaedel nativ\\.br\\\\.br\\Klinische Angabe: Zustand nach Sturz, Fraktur ausschliessen\\.br\\\\.br\\Befund:\\.br\\Kein Nachweis einer '
            'Fraktur des Neurocraniums oder Viscerocraniums.\\.br\\Kein intrakranielles Haematom. Keine Mittellinienverlagerung.\\.br\\Basale Zisternen frei.'
            ' Innere und aeussere Liquorraeume altersentspr.\\.br\\\\.br\\Beurteilung: Unauffaelliges CCT.'
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
        obx_2.observation_identifier = CWE(cwe_1='70450-PDF', cwe_2='CT Schaedel Befund', cwe_3='AVRAD')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4'
            'cmVmCjIwNgolJUVPRgo='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250310132500+0100'

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
    """ Based on live/at/at-avedis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINFAVOR')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINFAVOR')
        msh.date_time_of_message = '20250528110000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVLAB202505281100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00345678', cx_4='KLINFAVOR', cx_5='PI'), CX(cx_1='9261181190', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Fuchs', xpn_2='Katharina', xpn_3='E', xpn_5='Frau')
        pid.date_time_of_birth = '19901118'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='G401', pl_3='A', pl_4='KLINFAVOR')
        pv1.pv1_7 = 'AV0205^Hefler-Frischmuth^Lukas^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250528001')
        orc.filler_order_number = EI(ei_1='AVLAB20250528001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250528001')
        obr.filler_order_number = EI(ei_1='AVLAB20250528001')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC mit Diff', cwe_3='LN')
        obr.observation_date_time = '20250528060000+0200'
        obr.obr_15 = 'AV0205^Hefler-Frischmuth^Lukas^^^Prim.Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250528105000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx.obx_5 = '8.5'
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
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '3.65'
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
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx_3.obx_5 = '10.8'
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
        obx_4.obx_5 = '32.5'
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
        obx_5.obx_5 = '89.0'
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
        obx_6.obx_5 = '198'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Postoperative Anaemie. Kontrolle in 48h empfohlen.'

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
    """ Based on live/at/at-avedis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250815090000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'AVMSG202508150900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250815090000'
        evn.evn_5 = 'AV050^Pichler^Gertrude^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00567890', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='6148050382', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Müller', xpn_2='Werner', xpn_3='A', xpn_5='Herr')
        pid.date_time_of_birth = '19820503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ottakringer Strasse 55', xad_3='Wien', xad_5='1160', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436501234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6148050382^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='AV00567891', cx_4='KLINOTTAKR', cx_5='PI')

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
    """ Based on live/at/at-avedis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250426090000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVLAB202504260900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250426001')
        orc.filler_order_number = EI(ei_1='AVLAB20250426001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250426001')
        obr.filler_order_number = EI(ei_1='AVLAB20250426001')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinanalyse', cwe_3='LN')
        obr.observation_date_time = '20250426060000+0200'
        obr.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'
        obr.filler_field_2 = '20250426085000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Farbe', cwe_3='LN')
        obx.obx_5 = 'Gelb'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH Urin', cwe_3='LN')
        obx_2.obx_5 = '5.5'
        obx_2.reference_range = '5.0-8.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Spez. Gewicht', cwe_3='LN')
        obx_3.obx_5 = '1.025'
        obx_3.reference_range = '1.005-1.030'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glukose Urin', cwe_3='LN')
        obx_4.obx_5 = '250'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<30'
        obx_4.interpretation_codes = CWE(cwe_1='HH')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein Urin', cwe_3='LN')
        obx_5.obx_5 = '75'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<15'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Leukozyten Urin', cwe_3='LN')
        obx_6.obx_5 = 'negativ'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Ketone Urin', cwe_3='LN')
        obx_7.obx_5 = 'positiv (+)'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Glukosurie und Proteinurie bei bekanntem Diabetes mellitus. Ketonurie beachten.'

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
    """ Based on live/at/at-avedis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINHIETZING')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINHIETZING')
        msh.date_time_of_message = '20250714140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'AVMSG202507141400000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250714140000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='Avedis')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00456789', cx_4='KLINHIETZING', cx_5='PI'), CX(cx_1='4035220695', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Berger', xpn_2='Claudia', xpn_3='N', xpn_5='Frau')
        pid.date_time_of_birth = '19950622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hietzinger Kai 2', xad_3='Wien', xad_5='1130', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4318801234^PRN^PH~+436601234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4035220695^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Berger', xpn_2='Leopold', xpn_4='Herr', xpn_5='')
        nk1.address = XAD(xad_1='+436601234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'FTH'

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
    """ Based on live/at/at-avedis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250424143000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AVORD202504241430000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250424001')
        orc.filler_order_number = EI(ei_1='AVFIL20250424001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250424143000+0200'
        orc.orc_12 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250424001')
        obr.filler_order_number = EI(ei_1='AVFIL20250424001')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Sonographie Abdomen komplett', cwe_3='AVRAD')
        obr.observation_date_time = '20250424143000+0200'
        obr.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'
        obr.obr_17 = 'ACC20250424001'
        obr.diagnostic_serv_sect_id = 'US'
        obr.obr_35 = '76700^Sonographie Abdomen komplett^AVRAD'

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
    """ Based on live/at/at-avedis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='KLINOTTAKR')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINOTTAKR')
        msh.date_time_of_message = '20250424163000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVRAD202504241630000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00234567', cx_4='KLINOTTAKR', cx_5='PI'), CX(cx_1='7143150888', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Susanne', xpn_3='K', xpn_5='Frau')
        pid.date_time_of_birth = '19881015'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='I210', pl_3='B', pl_4='KLINOTTAKR')
        pv1.pv1_7 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250424001')
        orc.filler_order_number = EI(ei_1='AVFIL20250424001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250424001')
        obr.filler_order_number = EI(ei_1='AVFIL20250424001')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Sonographie Abdomen komplett', cwe_3='AVRAD')
        obr.observation_date_time = '20250424143000+0200'
        obr.obr_15 = 'AV0110^Watzinger^Nikolaus^^^Prim.Dr.^MD'
        obr.obr_17 = 'ACC20250424001'
        obr.diagnostic_serv_sect_id = 'US'
        obr.parent_result = PRL(prl_1='20250424162500+0200')
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76700', cwe_2='Sonographie Abdomen', cwe_3='AVRAD')
        obx.obx_5 = (
            'Befund:\\.br\\Sonographie Abdomen komplett\\.br\\\\.br\\Leber: Normal gross, homogenes Parenchym, keine fokalen Laesionen.\\.br\\Gallenblase: Steinf'
            'reil, Wanddicke normal.\\.br\\Pankreas: Soweit einsehbar unauffaellig.\\.br\\Milz: Normal gross (11 cm).\\.br\\Nieren: Beidseits normal gross, kei'
            'n Harnstau. Rechts ein 8mm Zyste im Unterpol.\\.br\\Aorta: Kaliber normal.\\.br\\Kein freier Aszites.\\.br\\\\.br\\Beurteilung: Unauffaelliger Oberb'
            'auch. Kleine Nierenzyste rechts (Bosniak I).'
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
        obx_2.observation_identifier = CWE(cwe_1='76700-IMG', cwe_2='Sonographie Niere rechts', cwe_3='AVRAD')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2f/2wBDARESEhgVGC8aGC9n'
            'QTtBZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2f/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAFRABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQD/2Q=='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250424162500+0200'

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
    """ Based on live/at/at-avedis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINHIETZING')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINHIETZING')
        msh.date_time_of_message = '20250716100000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVLAB202507161000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00456789', cx_4='KLINHIETZING', cx_5='PI'), CX(cx_1='4035220695', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Berger', xpn_2='Claudia', xpn_3='N', xpn_5='Frau')
        pid.date_time_of_birth = '19950622'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='AMB-DER-2', pl_3='1', pl_4='KLINHIETZING')
        pv1.pv1_7 = 'AV0310^Gschnait^Friedrich^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250716001')
        orc.filler_order_number = EI(ei_1='AVLAB20250716001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250716001')
        obr.filler_order_number = EI(ei_1='AVLAB20250716001')
        obr.universal_service_identifier = CWE(cwe_1='83036-9', cwe_2='Schilddruesenpanel', cwe_3='LN')
        obr.observation_date_time = '20250715083000+0200'
        obr.obr_15 = 'AV0310^Gschnait^Friedrich^^^Prim.Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250716095000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '0.15'
        obx.units = CWE(cwe_1='mU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='fT3', cwe_3='LN')
        obx_2.obx_5 = '6.8'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '3.1-6.8'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3024-7', cwe_2='fT4', cwe_3='LN')
        obx_3.obx_5 = '28.5'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '12.0-22.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Latente Hyperthyreose. Weitere Abklaerung empfohlen.'

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
    """ Based on live/at/at-avedis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250314070000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = 'AVMSG202503140700000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250314070000'
        evn.evn_5 = 'AV060^Hofer^Sabine^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bruenner Strasse 68', xad_3='Wien', xad_5='1210', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5829030175^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD', pl_9='UNFCHIR')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AV0042', cwe_2='Gaebler', cwe_3='Christian', cwe_6='Prim.Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='KLINFLORIDSD')
        pv1.prior_temporary_location = PL(pl_1='20250310081500')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-avedis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINFAVOR')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINFAVOR')
        msh.date_time_of_message = '20250527100000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVLAB202505271000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00345678', cx_4='KLINFAVOR', cx_5='PI'), CX(cx_1='9261181190', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Fuchs', xpn_2='Katharina', xpn_3='E', xpn_5='Frau')
        pid.date_time_of_birth = '19901118'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='G401', pl_3='A', pl_4='KLINFAVOR')
        pv1.pv1_7 = 'AV0205^Hefler-Frischmuth^Lukas^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250527001')
        orc.filler_order_number = EI(ei_1='AVLAB20250527001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250527001')
        obr.filler_order_number = EI(ei_1='AVLAB20250527001')
        obr.universal_service_identifier = CWE(cwe_1='85610-3', cwe_2='Gerinnungspanel praeop', cwe_3='LN')
        obr.observation_date_time = '20250527060000+0200'
        obr.obr_15 = 'AV0205^Hefler-Frischmuth^Lukas^^^Prim.Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250527095000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombinzeit (Quick)', cwe_3='LN')
        obx.obx_5 = '95'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '70-130'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '30'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25-37'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '310'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '180-350'
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
    """ Based on live/at/at-avedis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AVEDIS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250901141500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'AVMSG202509011415000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250901141500'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='Avedis')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Donaufelder Strasse 28', xad_3='Wien', xad_5='1210', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4312701234^PRN^PH~+436641234567^PRN^CP~stefan.mayer@email.at^NET^X.400'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5829030175^^^SV-AT'
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
    """ Based on live/at/at-avedis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLINFLORIDSD')
        msh.receiving_application = HD(hd_1='AVEDIS')
        msh.receiving_facility = HD(hd_1='KLINFLORIDSD')
        msh.date_time_of_message = '20250313150000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AVMIK202503131500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AV00123456', cx_4='KLINFLORIDSD', cx_5='PI'), CX(cx_1='5829030175', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Mayer', xpn_2='Stefan', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U301', pl_3='A', pl_4='KLINFLORIDSD')
        pv1.pv1_7 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AVORD20250313001')
        orc.filler_order_number = EI(ei_1='AVMIK20250313001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AVORD20250313001')
        obr.filler_order_number = EI(ei_1='AVMIK20250313001')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Wundabstrich Kultur', cwe_3='LN')
        obr.observation_date_time = '20250311140000+0100'
        obr.obr_15 = 'AV0042^Gaebler^Christian^^^Prim.Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250313145000+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Wundabstrich Kultur', cwe_3='LN')
        obx.obx_5 = 'Kein Wachstum^Kein Wachstum^SNOMED'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Keimnachweis', cwe_3='LN')
        obx_2.obx_5 = 'Kein pathogenes Keimwachstum nach 48h Bebruetung.'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Steril. Kein Antibiogramm erforderlich.'

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

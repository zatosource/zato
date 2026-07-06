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
from zato.hl7v2.v2_9.datatypes import AUI, CP, CWE, CX, DR, EI, FC, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA05Insurance, BarP01Visit, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A06, ADT_A09, ADT_A21, ADT_A30, ADT_A38, BAR_P01, MDM_T02, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, DG1, EVN, FT1, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-cloverleaf.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-cloverleaf.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260401070000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SAPISH20260401070000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401065500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512307845^PRN^PH~+436648812345^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '8241010580^^^SVNR'
        pid.birth_place = 'AUT'
        pid.identity_unknown_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK', pl_9='UCHIR')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.^^^^SAP_ISH'
        pv1.pv1_8 = 'ARZ101^Koller^Sonja^^^OA Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Maier', cwe_3='Heinrich', cwe_6='Univ.Prof.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.prior_temporary_location = PL(pl_1='20260401065500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Polytrauma nach Skiunfall')
        pv2.referral_source_code = XCN(xcn_1='5')
        pv2.special_program_code = CWE(cwe_1='20260401')
        pv2.retention_indicator = '20260410'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Pichler', xpn_2='Ulrike', xpn_4='Frau')
        nk1.address = XAD(xad_1='+43512307846', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'SPO'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ÖGK', cwe_2='Österreichische Gesundheitskasse')
        in1.insurance_company_id = CX(cx_1='01')
        in1.insurance_company_name = XON(xon_1='Österreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20260101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '8241010580'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/at/at-cloverleaf.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260401093000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SAPISH20260401093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260401093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H'),
            XAD(xad_1='Sillgasse 12', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='L'),
        ]
        pid.pid_13 = '+43512307845^PRN^PH~+436648812345^PRN^CP~^^Internet^thomas.pichler@tirol.gv.at'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '8241010580^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Maier', cwe_3='Heinrich', cwe_6='Univ.Prof.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.prior_temporary_location = PL(pl_1='20260401065500')

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
    """ Based on live/at/at-cloverleaf.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260410140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SAPISH20260410140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260410140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        pv1.pv1_8 = 'ARZ101^Koller^Sonja^^^OA Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Maier', cwe_3='Heinrich', cwe_6='Univ.Prof.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.prior_temporary_location = PL(pl_1='20260401065500')
        pv1.current_patient_balance = '20260410140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.0', cwe_2='Schenkelhalsfraktur', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='S82.1', cwe_2='Tibiakopffraktur', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20260401'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_3 = DG1()
        dg1_3.set_id_dg1 = '3'
        dg1_3.diagnosis_code_dg1 = CWE(cwe_1='S27.0', cwe_2='Pneumothorax traumatisch', cwe_3='ICD10')
        dg1_3.diagnosis_date_time = '20260401'
        dg1_3.diagnosis_type = CWE(cwe_1='W')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2, dg1_3]

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
    """ Based on live/at/at-cloverleaf.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260403120000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SAPISH20260403120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260403120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC305', pl_3='1', pl_4='LKI_INNSBRUCK', pl_9='UCHIR')
        pv1.preadmit_number = CX(cx_1='UCHIR', cx_2='UC301', cx_3='2', cx_4='LKI_INNSBRUCK')
        pv1.pv1_9 = 'ARZ101^Koller^Sonja^^^OA Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='UCH')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='ÖGK')
        pv1.servicing_facility = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.admit_date_time = '20260401065500'

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
    """ Based on live/at/at-cloverleaf.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='BKH_SCHWAZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260415100000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'SAPISH20260415100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20260415100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S523478', cx_4='BKH_SCHWAZ', cx_5='PI'), CX(cx_1='5923230992', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Bauer', xpn_2='Maria', xpn_3='Sabine', xpn_5='Frau')
        pid.date_time_of_birth = '19920323'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Münchner Straße 7', xad_3='Schwaz', xad_5='6130', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43524271340^PRN^PH~+436602234561^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '5923230992^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='GYNOB', pl_2='GO201', pl_3='1', pl_4='BKH_SCHWAZ', pl_9='GYNOB')
        pv1.pv1_7 = 'ARZ200^Holzer^Petra^^^Prim.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='GYN')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ200', cwe_2='Holzer', cwe_3='Petra', cwe_6='Prim.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='BKH_SCHWAZ')
        pv1.prior_temporary_location = PL(pl_1='20260422080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Sectio caesarea elektiv')
        pv2.referral_source_code = XCN(xcn_1='3')
        pv2.special_program_code = CWE(cwe_1='20260422')
        pv2.retention_indicator = '20260426'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ÖGK', cwe_2='Österreichische Gesundheitskasse')
        in1.insurance_company_id = CX(cx_1='01')
        in1.insurance_company_name = XON(xon_1='Österreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20260101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '5923230992'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance

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
    """ Based on live/at/at-cloverleaf.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260418153000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A06', msg_3='ADT_A06')
        msh.message_control_id = 'SAPISH20260418153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A06'
        evn.recorded_date_time = '20260418153000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S634589', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='7614110478', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wagner', xpn_2='Franz', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19781104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Höttinger Gasse 31', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512562178^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7614110478^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='K401', pl_3='1', pl_4='LKI_INNSBRUCK', pl_9='KARD')
        pv1.pv1_7 = 'ARZ300^Stadler^Manfred^^^Univ.Doz.Dr.^med.'
        pv1.pv1_8 = 'ARZ301^Wimmer^Silvia^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CAR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ300', cwe_2='Stadler', cwe_3='Manfred', cwe_6='Univ.Doz.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.prior_temporary_location = PL(pl_1='20260418153000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akutes Koronarsyndrom')

        # .. assemble the full message ..
        msg = ADT_A06()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/at/at-cloverleaf.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260501090000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'SAPISH20260501090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260501090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S745690', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='4385280399', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Katharina', xpn_3='Ingrid', xpn_5='Frau')
        pid.date_time_of_birth = '19990328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Innrain 52', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512412367^PRN^PH~+436763345512^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4385280399^^^SVNR'
        pid.birth_place = 'AUT'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-cloverleaf.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260501103000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'SAPISH20260501103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260501103000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S745690', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='4385280399', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Katharina', xpn_3='Ingrid', xpn_5='Frau Mag.')
        pid.date_time_of_birth = '19990328'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Maximilianstraße 8', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512412367^PRN^PH~+436763345512^PRN^CP~^^Internet^katharina.gruber@uibk.ac.at'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4385280399^^^SVNR'
        pid.birth_place = 'AUT'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-cloverleaf.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260502140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A34', msg_3='ADT_A30')
        msh.message_control_id = 'SAPISH20260502140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A34'
        evn.recorded_date_time = '20260502140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='S998222', cx_4='LKI_INNSBRUCK', cx_5='PI')

        # .. assemble the full message ..
        msg = ADT_A30()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg

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
    """ Based on live/at/at-cloverleaf.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260402070000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'SAPISH20260402070000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20260402070000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S856701', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='6158150668', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Eder', xpn_2='Renate', xpn_3='Elfriede', xpn_5='Frau')
        pid.date_time_of_birth = '19680115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Reichenauer Straße 42', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512876543^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='N201', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ400^Pfeiffer^Helmut^^^Univ.Prof.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='NEU')
        pv1.pv1_40 = 'LKI_INNSBRUCK'
        pv1.discharge_date_time = '20260401150000'

        # .. assemble the full message ..
        msg = ADT_A09()
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
    """ Based on live/at/at-cloverleaf.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='BKH_SCHWAZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260420090000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A38', msg_3='ADT_A38')
        msh.message_control_id = 'SAPISH20260420090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A38'
        evn.recorded_date_time = '20260420090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S523478', cx_4='BKH_SCHWAZ', cx_5='PI'), CX(cx_1='5923230992', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Bauer', xpn_2='Maria', xpn_3='Sabine', xpn_5='Frau')
        pid.date_time_of_birth = '19920323'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Münchner Straße 7', xad_3='Schwaz', xad_5='6130', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='GYNOB', pl_2='GO201', pl_3='1', pl_4='BKH_SCHWAZ')
        pv1.pv1_7 = 'ARZ200^Holzer^Petra^^^Prim.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='GYN')
        pv1.pv1_40 = 'BKH_SCHWAZ'
        pv1.discharge_date_time = '20260422080000'

        # .. assemble the full message ..
        msg = ADT_A38()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-cloverleaf.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP_ISH')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260405100000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A21', msg_3='ADT_A21')
        msh.message_control_id = 'SAPISH20260405100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A21'
        evn.recorded_date_time = '20260405100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC305', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.pv1_40 = 'LKI_INNSBRUCK'
        pv1.discharge_date_time = '20260401065500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.previous_service_date = '20260405100000'
        pv2.employment_illness_related_indicator = '20260406180000'

        # .. assemble the full message ..
        msg = ADT_A21()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/at/at-cloverleaf.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_MIL')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260510080000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CERN20260510080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260510075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='C312456', cx_4='CERNER_MIL', cx_5='MR'), CX(cx_1='1796050785', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Berger', xpn_2='Florian', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19850507'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Anichstraße 20', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43512654321^PRN^PH~+436765567123^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '1796050785^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INNERE', pl_2='I301', pl_3='3', pl_4='LKI_INNSBRUCK', pl_9='INNERE')
        pv1.pv1_7 = 'ARZ500^Aigner^Christine^^^OA Dr.^med.^^^^CERNER_MIL'
        pv1.pv1_8 = 'ARZ501^Wolf^Erich^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='INT')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ500', cwe_2='Aigner', cwe_3='Christine', cwe_6='OA Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKI_INNSBRUCK')
        pv1.prior_temporary_location = PL(pl_1='20260510075500')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='Z88.0', cwe_2='Penicillinallergie', cwe_3='ICD10')
        al1.allergy_reaction_code = 'Exanthem'
        al1.al1_6 = '20190315'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.al1 = al1

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
    """ Based on live/at/at-cloverleaf.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='LABORSYSTEM')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20260401073000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CLVR20260401073000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260401001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20260401073000+0200'
        orc.orc_12 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260401065000+0200'
        obr.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260401002')
        obr_2.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Stoffwechselpanel', cwe_3='LN')
        obr_2.observation_date_time = '20260401065000+0200'
        obr_2.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260401003')
        obr_3.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Gerinnungspanel', cwe_3='LN')
        obr_3.observation_date_time = '20260401065000+0200'
        obr_3.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD20260401004')
        obr_4.universal_service_identifier = CWE(cwe_1='14937-7', cwe_2='Blutgruppe', cwe_3='LN')
        obr_4.observation_date_time = '20260401065000+0200'
        obr_4.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/at/at-cloverleaf.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABORSYSTEM')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260401090000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260401090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260401001')
        orc.filler_order_number = EI(ei_1='LAB20260401001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260401065000+0200'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001')
        obr.filler_order_number = EI(ei_1='LAB20260401001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260401065000+0200'
        obr.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        obr.filler_field_2 = '20260401085500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '3.12'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '4.30-5.70'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.5-17.5'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hämatokrit', cwe_3='LN')
        obx_4.obx_5 = '29.5'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '40.0-52.0'
        obx_4.interpretation_codes = CWE(cwe_1='LL')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Thrombozyten', cwe_3='LN')
        obx_5.obx_5 = '198'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='33762-6', cwe_2='CRP', cwe_3='LN')
        obx_6.obx_5 = '145'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '<5'
        obx_6.interpretation_codes = CWE(cwe_1='HH')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260401083000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2532-0', cwe_2='Laktatdehydrogenase', cwe_3='LN')
        obx_7.obx_5 = '485'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '135-225'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260401083000+0200'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Massiv erhöhte Entzündungsparameter. Dringend klinische Korrelation empfohlen.'

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
    """ Based on live/at/at-cloverleaf.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POCANALYSER')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260401074500+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'POC20260401074500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC301', pl_3='2', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='POC20260401001')
        orc.filler_order_number = EI(ei_1='POC20260401001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='POC20260401001')
        obr.filler_order_number = EI(ei_1='POC20260401001')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Blutgasanalyse arteriell', cwe_3='LN')
        obr.observation_date_time = '20260401074000+0200'
        obr.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        obr.filler_field_2 = '20260401074500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arteriell', cwe_3='LN')
        obx.obx_5 = '7.32'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '48'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260401074200+0200'

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
        obx_3.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bicarbonat', cwe_3='LN')
        obx_4.obx_5 = '24.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Base Excess', cwe_3='LN')
        obx_5.obx_5 = '-1.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='20563-3', cwe_2='SpO2', cwe_3='LN')
        obx_6.obx_5 = '93'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2339-0', cwe_2='Glukose (BGA)', cwe_3='LN')
        obx_7.obx_5 = '165'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '70-105'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2947-0', cwe_2='Natrium (BGA)', cwe_3='LN')
        obx_8.obx_5 = '139'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '136-145'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='6298-4', cwe_2='Kalium (BGA)', cwe_3='LN')
        obx_9.obx_5 = '4.8'
        obx_9.units = CWE(cwe_1='mmol/L')
        obx_9.reference_range = '3.5-5.1'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='2000-8', cwe_2='Calcium ionisiert', cwe_3='LN')
        obx_10.obx_5 = '1.18'
        obx_10.units = CWE(cwe_1='mmol/L')
        obx_10.reference_range = '1.15-1.29'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'NM'
        obx_11.observation_identifier = CWE(cwe_1='59032-3', cwe_2='Laktat', cwe_3='LN')
        obx_11.obx_5 = '3.2'
        obx_11.units = CWE(cwe_1='mmol/L')
        obx_11.reference_range = '0.5-2.2'
        obx_11.interpretation_codes = CWE(cwe_1='H')
        obx_11.observation_result_status = 'F'
        obx_11.date_time_of_the_observation = '20260401074200+0200'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

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
        order_observation.observation_10 = observation_10
        order_observation.observation_11 = observation_11

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
    """ Based on live/at/at-cloverleaf.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUBSYSTEM')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260411100000+0200'
        msh.message_type = MSG(msg_1='BAR', msg_2='P01', msg_3='BAR_P01')
        msh.message_control_id = 'BAR20260411100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P01'
        evn.recorded_date_time = '20260411100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC305', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. build the VISIT group ..
        visit = BarP01Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260405')
        ft1.transaction_date = DR(dr_1='20260405')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_1='12345', cwe_2='Osteosynthese Femur', cwe_3='LKF')
        ft1.ft1_9 = '1'
        ft1.insurance_amount = CP(cp_1='UCHIR')
        ft1.diagnosis_code_ft1 = CWE(cwe_1='ARZ100', cwe_2='Maier', cwe_3='Heinrich', cwe_6='Univ.Prof.Dr.', cwe_7='med.')

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260407')
        ft1_2.transaction_date = DR(dr_1='20260407')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_1='67890', cwe_2='CT Schädel nativ', cwe_3='LKF')
        ft1_2.ft1_9 = '1'
        ft1_2.insurance_amount = CP(cp_1='RAD')
        ft1_2.diagnosis_code_ft1 = CWE(cwe_1='ARZ600', cwe_2='Fischer', cwe_3='Stefan', cwe_6='Dr.', cwe_7='med.')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.0', cwe_2='Schenkelhalsfraktur', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = BAR_P01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.extra_segments = [ft1, ft1_2, dg1]

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
    """ Based on live/at/at-cloverleaf.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260402120000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RIS20260402120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC305', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='RAD20260402001')
        orc.filler_order_number = EI(ei_1='RAD20260402001R')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260402001')
        obr.filler_order_number = EI(ei_1='RAD20260402001R')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRT Kniegelenk', cwe_3='CPT')
        obr.observation_date_time = '20260402100000+0200'
        obr.obr_15 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        obr.filler_field_2 = '20260402115000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='70553', cwe_2='MRT Knie rechts', cwe_3='CPT')
        obx.obx_5 = (
            'Befund: Komplexe Meniskusläsion Innenmeniskus Hinterhorn. Vorderes Kreuzband intakt. Innenbandzerrung Grad II. Mäßiger Gelenkerguss.\\.br\\Beu'
            'rteilung: OP-Indikation zur arthroskopischen Meniskusteilresektion empfohlen.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260402114500+0200'
        obx.obx_16 = 'ARZ600^Fischer^Stefan^^^Dr.^med.'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='70553', cwe_2='MRT Befund PDF', cwe_3='CPT')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA3MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE1SVCBLbmllZ2VsZW5rIHJl'
            'Y2h0cyAtIFJhZGlvbG9naWUgTEtJIElCaykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZl'
            'dGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjUgMDAwMDAgbiAKMDAwMDAwMDEyMiAwMDAwMCBuIAow'
            'MDAwMDAwMjk2IDAwMDAwIG4gCjAwMDAwMDAzOTMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0NzYKJSVFT0Y='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260402115000+0200'

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
    """ Based on live/at/at-cloverleaf.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPCENTER')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260406160000+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MDM20260406160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260406160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S412367', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='8241010580', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Thomas', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19800105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Museumstraße 22', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCHIR', pl_2='UC305', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='OP-Bericht', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260405150000+0200'
        txa.txa_5 = 'ARZ100^Maier^Heinrich^^^Univ.Prof.Dr.^med.'
        txa.transcriptionist_code_name = XCN(xcn_1='DOC20260405001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='28570-0', cwe_2='OP-Bericht', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA4MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE9QLUJlcmljaHQgT3N0ZW9z'
            'eW50aGVzZSBGZW11ciAtIFVuZmFsbGNoaXJ1cmdpZSBMS0kpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VG'
            'b250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDY1IDAwMDAwIG4gCjAwMDAwMDAxMjIg'
            'MDAwMDAgbiAKMDAwMDAwMDI5NiAwMDAwMCBuIAowMDAwMDAwMzkzIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNDc2CiUlRU9G'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260405150000+0200'

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
    """ Based on live/at/at-cloverleaf.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHOSYSTEM')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='TK_HUB')
        msh.date_time_of_message = '20260412140000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH20260412140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='S634589', cx_4='LKI_INNSBRUCK', cx_5='PI'), CX(cx_1='7614110478', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wagner', xpn_2='Franz', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19781104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Höttinger Gasse 31', xad_3='Innsbruck', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='K401', pl_3='1', pl_4='LKI_INNSBRUCK')
        pv1.pv1_7 = 'ARZ300^Stadler^Manfred^^^Univ.Doz.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='PATH20260410001')
        orc.filler_order_number = EI(ei_1='PATH20260412001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20260410001')
        obr.filler_order_number = EI(ei_1='PATH20260412001')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Chirurgische Pathologie', cwe_3='LN')
        obr.observation_date_time = '20260410100000+0200'
        obr.obr_15 = 'ARZ300^Stadler^Manfred^^^Univ.Doz.Dr.^med.'
        obr.filler_field_2 = '20260412135000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Histologischer Befund', cwe_3='LN')
        obx.obx_5 = (
            'Makroskopie: Herzkatheter-Biopsie rechter Ventrikel, 3 Fragmente.\\.br\\Mikroskopie: Myokardgewebe mit geringgradiger interstitieller Fibrose.'
            ' Kein Hinweis auf Myokarditis. Keine Amyloidablagerungen (Kongorot negativ). Kein Hinweis auf Abstoßungsreaktion.\\.br\\Diagnose: Myokardbiops'
            'ie mit geringgradiger interstitieller Fibrose, kein spezifischer pathologischer Befund.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260412130000+0200'
        obx.obx_16 = 'ARZ700^Strobl^Bernhard^^^Univ.Prof.Dr.^med.'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Material ordnungsgemäß in Formalin fixiert eingelangt. 3 von 3 Fragmenten auswertbar.'

        # .. build NTE ..
        nte_2 = NTE()
        nte_2.set_id_nte = '2'
        nte_2.comment = 'Klinische Angabe: V.a. dilatative Kardiomyopathie. Transplantatabstoßung ausschließen.'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte
        observation.nte_2 = nte_2

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

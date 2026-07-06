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
from zato.hl7v2.v2_9.datatypes import AUI, CWE, CX, DLD, EI, HD, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA05NextOfKin, AdtA39Patient, AdtA44Patient, MdmT02CommonOrder, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, ADT_A44, MDM_T02, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, TXA
from zato.hl7v2.z_segments import ZDS

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-akh-wien.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-akh-wien.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250312084522+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'AKHMSG202503120845220001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312084500'
        evn.evn_5 = 'ADM001^Leitner^Sabine^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='7381120580', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Waehringer Guertel 18-20', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040012345^PRN^PH~+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7381120580^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1312', pl_3='A', pl_4='AKHWIEN', pl_9='INNMED1')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD^^^^AKHWIEN^^^^OAEK&2.16.840.1.113883.2.16.1.4&ISO'
        pv1.pv1_8 = 'AKH0088^Eder^Katharina^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='KAR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AKH0042', cwe_2='Koller', cwe_3='Johann', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='AKHWIEN')
        pv1.prior_temporary_location = PL(pl_1='20250312084500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akutes Koronarsyndrom')
        pv2.referral_source_code = XCN(xcn_1='2')
        pv2.special_program_code = CWE(cwe_1='20250312')
        pv2.retention_indicator = '20250319'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Gruber', xpn_2='Elisabeth', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+4316641234568', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='OEGK', cwe_2='OeGK Wien')
        in1.insurance_company_id = CX(cx_1='101')
        in1.insurance_company_name = XON(xon_1='Oesterreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20250101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '7381120580'

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='C01', cwe_2='Acetylsalicylsaeure', cwe_3='AKH')
        al1.allergy_reaction_code = 'Urtikaria'
        al1.al1_6 = '20180901'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.0', cwe_2='Akuter transmuraler Myokardinfarkt der Vorderwand', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250312'
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
    """ Based on live/at/at-akh-wien.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250415101030+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'AKHMSG202504151010300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250415101000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='SAP')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00345678', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='5192230492', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Elisabeth', xpn_3='R', xpn_5='Frau')
        pid.date_time_of_birth = '19920423'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Lazarettgasse 14', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040023456^PRN^PH~+436769876543^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '5192230492^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='POLI-NEU-3', pl_3='1', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0115^Wallner^Stefan^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='NEU')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='AKH0115', cwe_2='Wallner', cwe_3='Stefan', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='AKHWIEN')
        pv1.pending_location = PL(pl_1='20250415093000')

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
    """ Based on live/at/at-akh-wien.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250520161500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'AKHMSG202505201615000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250520161500'
        evn.evn_5 = 'ADM015^Reiter^Brigitte^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00456789', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='6403070365', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Huber', xpn_2='Wolfgang', xpn_3='M', xpn_5='Herr')
        pid.date_time_of_birth = '19650703'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Spitalgasse 23', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040034567^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6403070365^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='09C1', pl_2='0915', pl_3='B', pl_4='AKHWIEN', pl_9='CHIRALLG')
        pv1.pv1_7 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AKH0201', cwe_2='Winkler', cwe_3='Heinrich', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='SVS')
        pv1.diet_type = CWE(cwe_1='AKHWIEN')
        pv1.prior_temporary_location = PL(pl_1='20250513090000')
        pv1.current_patient_balance = '20250520161500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Gallenblasenstein mit Cholezystitis', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250513'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z87.4', cwe_2='Zustand nach Appendektomie', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20250513'
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
    """ Based on live/at/at-akh-wien.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250610093045+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'AKHMSG202506100930450001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250610093000'
        evn.evn_5 = 'ADM020^Aigner^Petra^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00567890', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='8214251178', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Bauer', xpn_2='Franz', xpn_3='R', xpn_5='Herr')
        pid.date_time_of_birth = '19781125'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Borschkegasse 8a', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436505551234^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '8214251178^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1305', pl_3='C', pl_4='AKHWIEN', pl_9='INNMED1')
        pv1.prior_patient_location = PL(pl_1='13I1', pl_2='ICU2', pl_3='1', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'
        pv1.pv1_8 = 'AKH0102^Schwarz^Renate^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='KAR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AKH0042', cwe_2='Koller', cwe_3='Johann', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='BVAEB')
        pv1.diet_type = CWE(cwe_1='AKHWIEN')
        pv1.prior_temporary_location = PL(pl_1='20250607140000')

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
    """ Based on live/at/at-akh-wien.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250722080015+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'AKHMSG202507220800150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250722080000'
        evn.evn_5 = 'ADM030^Wolf^Claudia^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00678901', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='9501141088', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Maria', xpn_3='S', xpn_5='Frau')
        pid.date_time_of_birth = '19881014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Alser Strasse 4', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040045678^PRN^PH~+436601234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '9501141088^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AUGE', pl_2='AMB-AUG-1', pl_3='2', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0310^Berger^Leopold^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='AUG')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='AKH0310', cwe_2='Berger', cwe_3='Leopold', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.discharged_to_location = DLD(dld_1='AKHWIEN')
        pv1.pending_location = PL(pl_1='20250722080000')

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
    """ Based on live/at/at-akh-wien.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250225143015+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AKHORD202502251430150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='7381120580', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Waehringer Guertel 18-20', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1312', pl_3='A', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250225001')
        orc.filler_order_number = EI(ei_1='AKHFIL20250225001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250225143000+0100'
        orc.orc_12 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250225001')
        obr.filler_order_number = EI(ei_1='AKHFIL20250225001')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT Thorax mit KM', cwe_3='AKHRAD')
        obr.observation_date_time = '20250225143000+0100'
        obr.obr_15 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'
        obr.obr_17 = 'ACC20250225001'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.obr_35 = '71260^CT Thorax mit KM^AKHRAD'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.40.0.34.1.1.99.20250225.143000.001'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [zds]

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
    """ Based on live/at/at-akh-wien.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250303071500+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AKHORD202503030715000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00345678', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='5192230492', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Elisabeth', xpn_3='R', xpn_5='Frau')
        pid.date_time_of_birth = '19920423'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1320', pl_3='B', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250303001')
        orc.filler_order_number = EI(ei_1='AKHLAB20250303001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250303071500+0100'
        orc.orc_12 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250303001')
        obr.filler_order_number = EI(ei_1='AKHLAB20250303001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basis Metabolisches Panel', cwe_3='LN')
        obr.observation_date_time = '20250303070000+0100'
        obr.obr_15 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='AKHORD20250303002')
        obr_2.filler_order_number = EI(ei_1='AKHLAB20250303002')
        obr_2.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC mit Differentialblutbild', cwe_3='LN')
        obr_2.observation_date_time = '20250303070000+0100'
        obr_2.obr_15 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/at/at-akh-wien.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250303093045+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHLAB202503030930450001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00345678', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='5192230492', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Elisabeth', xpn_3='R', xpn_5='Frau')
        pid.date_time_of_birth = '19920423'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1320', pl_3='B', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250303001')
        orc.filler_order_number = EI(ei_1='AKHLAB20250303001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250303001')
        obr.filler_order_number = EI(ei_1='AKHLAB20250303001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basis Metabolisches Panel', cwe_3='LN')
        obr.observation_date_time = '20250303070000+0100'
        obr.obr_15 = 'AKH0055^Riegler^Martin^^^Dr.^MD'
        obr.filler_field_2 = '20250303092500+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_3.obx_5 = '139'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '136-145'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_4.obx_5 = '4.5'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT (GPT)', cwe_3='LN')
        obx_5.obx_5 = '28'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '<50'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT (GOT)', cwe_3='LN')
        obx_6.obx_5 = '32'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '<50'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin gesamt', cwe_3='LN')
        obx_7.obx_5 = '0.9'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '<1.2'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250303085000+0100'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterin gesamt', cwe_3='LN')
        obx_8.obx_5 = '215'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '<200'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250303085000+0100'

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
    """ Based on live/at/at-akh-wien.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250303094500+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHLAB202503030945000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00345678', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='5192230492', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Elisabeth', xpn_3='R', xpn_5='Frau')
        pid.date_time_of_birth = '19920423'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1320', pl_3='B', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0055^Riegler^Martin^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250303002')
        orc.filler_order_number = EI(ei_1='AKHLAB20250303002')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250303002')
        obr.filler_order_number = EI(ei_1='AKHLAB20250303002')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC mit Differentialblutbild', cwe_3='LN')
        obr.observation_date_time = '20250303070000+0100'
        obr.obr_15 = 'AKH0055^Riegler^Martin^^^Dr.^MD'
        obr.filler_field_2 = '20250303094000+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
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
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '4.55'
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
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Haematokrit', cwe_3='LN')
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
        obx_5.obx_5 = '90.5'
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
        obx_6.obx_5 = '245'
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
        obx_7.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophile', cwe_3='LN')
        obx_7.obx_5 = '62'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '40-75'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='736-9', cwe_2='Lymphozyten', cwe_3='LN')
        obx_8.obx_5 = '28'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '20-45'
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
    """ Based on live/at/at-akh-wien.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250225164500+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHRAD202502251645000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='7381120580', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1312', pl_3='A', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250225001')
        orc.filler_order_number = EI(ei_1='AKHFIL20250225001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250225001')
        obr.filler_order_number = EI(ei_1='AKHFIL20250225001')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT Thorax mit KM', cwe_3='AKHRAD')
        obr.observation_date_time = '20250225143000+0100'
        obr.obr_15 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'
        obr.obr_17 = 'ACC20250225001'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.parent_result = PRL(prl_1='20250225164000+0100')
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71260', cwe_2='CT Thorax mit KM', cwe_3='AKHRAD')
        obx.obx_5 = (
            'Befund: CT Thorax mit KM\\.br\\Klinische Angabe: V.a. Pulmonalembolie\\.br\\\\.br\\Technik: Nativ- und KM-verstaerkte Spiralcomputertomographie de'
            's Thorax\\.br\\\\.br\\Befund:\\.br\\Keine Hinweise auf Pulmonalembolie. Regelrechte Darstellung der Pulmonalarterien.\\.br\\Herz normal gross, kein '
            'Perikarderguss.\\.br\\Keine mediastinale Lymphadenopathie.\\.br\\Lungenparenchym ohne fokale Verdichtungen.\\.br\\Keine Pleuraerguesse.\\.br\\\\.br\\B'
            'eurteilung: Kein Nachweis einer Pulmonalembolie.'
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
        obx_2.observation_identifier = CWE(cwe_1='71260-PDF', cwe_2='CT Thorax Befund PDF', cwe_3='AKHRAD')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4'
            'cmVmCjIwNgolJUVPRgo='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250225164000+0100'

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
    """ Based on live/at/at-akh-wien.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250801110030+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'AKHMSG202508011100300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250801110000'
        evn.evn_5 = 'ADM040^Egger^Monika^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00789012', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='4627180275', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wagner', xpn_2='Josef', xpn_3='H', xpn_5='Herr')
        pid.date_time_of_birth = '19750218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Alser Strasse 4', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436501234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '4627180275^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='P00789013', cx_4='AKHWIEN', cx_5='PI')

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
    """ Based on live/at/at-akh-wien.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250905073000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'AKHMSG202509050730000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250905073000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='SAP')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00890123', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='3175051095', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Ingrid', xpn_3='B', xpn_5='Frau')
        pid.date_time_of_birth = '19950510'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kinderspitalgasse 15', xad_3='Wien', xad_5='1090', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040056789^PRN^PH~+436761234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '3175051095^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Steiner', xpn_2='Helmut', xpn_4='Herr', xpn_5='')
        nk1.address = XAD(xad_1='+4316765432100', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'

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
    """ Based on live/at/at-akh-wien.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250410091500+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AKHORD202504100915000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00456789', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='6403070365', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Huber', xpn_2='Wolfgang', xpn_3='M', xpn_5='Herr')
        pid.date_time_of_birth = '19650703'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='09C1', pl_2='0915', pl_3='B', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250410001')
        orc.filler_order_number = EI(ei_1='AKHFIL20250410001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250410091500+0200'
        orc.orc_12 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250410001')
        obr.filler_order_number = EI(ei_1='AKHFIL20250410001')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='MRT Abdomen mit KM', cwe_3='AKHRAD')
        obr.observation_date_time = '20250410091500+0200'
        obr.obr_15 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'
        obr.obr_17 = 'ACC20250410001'
        obr.diagnostic_serv_sect_id = 'MR'
        obr.obr_35 = '74177^MRT Abdomen mit KM^AKHRAD'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.40.0.34.1.1.99.20250410.091500.001'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [zds]

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
    """ Based on live/at/at-akh-wien.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIKROBIO')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250618142030+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHMIK202506181420300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00567890', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='8214251178', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Bauer', xpn_2='Franz', xpn_3='R', xpn_5='Herr')
        pid.date_time_of_birth = '19781125'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1305', pl_3='C', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250618001')
        orc.filler_order_number = EI(ei_1='AKHMIK20250618001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250618001')
        obr.filler_order_number = EI(ei_1='AKHMIK20250618001')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Blutkultur', cwe_3='LN')
        obr.observation_date_time = '20250616080000+0200'
        obr.obr_15 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250618140000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Blutkultur', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus^Staphylococcus aureus^SNOMED'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramm', cwe_3='LN')
        obx_2.obx_5 = 'Oxacillin: resistent (R), Vancomycin: sensibel (S), Daptomycin: sensibel (S), Linezolid: sensibel (S)'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'MRSA-positiv. Isolierung empfohlen. Krankenhaushygiene wurde informiert.'

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
    """ Based on live/at/at-akh-wien.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHSYS')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250720153000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHPATH202507201530000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00456789', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='6403070365', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Huber', xpn_2='Wolfgang', xpn_3='M', xpn_5='Herr')
        pid.date_time_of_birth = '19650703'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='09C1', pl_2='0915', pl_3='B', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250720001')
        orc.filler_order_number = EI(ei_1='AKHPATH20250720001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250720001')
        obr.filler_order_number = EI(ei_1='AKHPATH20250720001')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='Pathologiebefund', cwe_3='LN')
        obr.observation_date_time = '20250715101500+0200'
        obr.obr_15 = 'AKH0201^Winkler^Heinrich^^^Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250720150000+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathologiebefund', cwe_3='LN')
        obx.obx_5 = (
            'Histologischer Befund:\\.br\\Material: Gallenblase, Cholezystektomie\\.br\\\\.br\\Makroskopisch: 8,5 cm grosse Gallenblase mit wandstaendigen Konk'
            'rementen.\\.br\\Mikroskopisch: Chronische Cholezystitis mit Schleimhautulzerationen. Kein Anhalt fuer Malignitat.\\.br\\\\.br\\Diagnose: Chronisch'
            'e kalkuloese Cholezystitis.'
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
        obx_2.observation_identifier = CWE(cwe_1='22637-3-IMG', cwe_2='Makrofoto Gallenblase', cwe_3='AKHPATH')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2f/2wBDARESEhgVGC8aGC9n'
            'QTtBZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2f/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAFRABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQD/2Q=='
        )
        obx_2.interpretation_codes = CWE(cwe_1='F')
        obx_2.observation_result_status = '20250720150000+0200'

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
    """ Based on live/at/at-akh-wien.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250830090015+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = 'AKHMSG202508300900150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250830090000'
        evn.evn_5 = 'ADM045^Haas^Gertrude^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00901234', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='2953200670', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Robert', xpn_3='A', xpn_5='Herr')
        pid.date_time_of_birth = '19700120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gaertnergasse 12', xad_3='Wien', xad_5='1030', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040067890^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '2953200670^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H3', pl_2='1345', pl_3='A', pl_4='AKHWIEN', pl_9='INNMED3')
        pv1.pv1_7 = 'AKH0170^Lang^Florian^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='IMM')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='AKH0170', cwe_2='Lang', cwe_3='Florian', cwe_6='Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='AKHWIEN')
        pv1.prior_temporary_location = PL(pl_1='20250825100000')

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
    """ Based on live/at/at-akh-wien.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EKGSYS')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250312150030+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AKHEKG202503121500300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='7381120580', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='13H1', pl_2='1312', pl_3='A', pl_4='AKHWIEN')
        pv1.pv1_7 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='AKHORD20250312EKG')
        orc.filler_order_number = EI(ei_1='AKHEKG20250312001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AKHORD20250312EKG')
        obr.filler_order_number = EI(ei_1='AKHEKG20250312001')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='12-Kanal-EKG', cwe_3='CPT')
        obr.observation_date_time = '20250312100000+0100'
        obr.obr_15 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD'
        obr.filler_field_2 = '20250312145500+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Herzfrequenz', cwe_3='LN')
        obx.obx_5 = '88'
        obx.units = CWE(cwe_1='/min')
        obx.reference_range = '60-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='8601-7', cwe_2='EKG Interpretation', cwe_3='LN')
        obx_2.obx_5 = 'Sinusrhythmus, HF 88/min. ST-Hebungen in V1-V4. STEMI anterior.'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8625-6', cwe_2='PR-Intervall', cwe_3='LN')
        obx_3.obx_5 = '160'
        obx_3.units = CWE(cwe_1='ms')
        obx_3.reference_range = '120-200'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8633-0', cwe_2='QRS-Dauer', cwe_3='LN')
        obx_4.obx_5 = '92'
        obx_4.units = CWE(cwe_1='ms')
        obx_4.reference_range = '60-120'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8634-8', cwe_2='QTc-Intervall', cwe_3='LN')
        obx_5.obx_5 = '420'
        obx_5.units = CWE(cwe_1='ms')
        obx_5.reference_range = '350-450'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'STEMI anterior - dringende Intervention empfohlen. Herzkatheterlabor verstaendigt.'

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
    """ Based on live/at/at-akh-wien.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250915141500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'AKHMSG202509151415000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250915141500'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='SAP')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='7381120580', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Neubaugasse 44', xad_3='Wien', xad_5='1070', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040012345^PRN^PH~+436641234567^PRN^CP~thomas.gruber@email.at^NET^X.400'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7381120580^^^SV-AT'
        pid.birth_place = 'AT'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-akh-wien.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250320101500+0100'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'AKHMDM202503201015000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='P00234567', cx_4='AKHWIEN', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Gruber', xpn_2='Thomas', xpn_3='W', xpn_5='Herr')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V20250312001', cx_4='AKHWIEN')
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20250320100000+0100'
        obr.placer_field_1 = 'ACC20250225001'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AR', cwe_2='Arztbrief', cwe_3='AKH')
        txa.document_content_presentation = 'TX^text^AKH'
        txa.origination_date_time = '20250320100000+0100'
        txa.txa_9 = 'AKH0042^Koller^Johann^^^Univ.Prof.Dr.^MD^^^^^^^^^AKH&2.16.840.1.113883.2.16.1.4&ISO^A'
        txa.unique_document_number = EI(ei_1='AB-2025-00234567')
        txa.unique_document_file_name = 'Arztbrief_Gruber_20250320.pdf'
        txa.document_completion_status = 'AU'
        txa.distributed_copies_code_and_name_of_recipients = XCN(xcn_1='AB-CNT-2025-001', xcn_3='AKHWIEN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDcyIDcyMCBUZCAoQXJ6dGJyaWVmIEFL'
            'SCBXaWVuKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVm'
            'CjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NiAwMDAwMCBuIAowMDAwMDAwMTI1IDAwMDAwIG4gCjAwMDAwMDAzMjkgMDAwMDAgbiAK'
            'MDAwMDAwMDQyMyAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjUyMgolJUVPRgo='
        )
        obx.interpretation_codes = CWE(cwe_1='F')
        obx.observation_result_status = '20250320100000+0100'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
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
    """ Based on live/at/at-akh-wien.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='AKHWIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKHWIEN')
        msh.date_time_of_message = '20250928133000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A47', msg_3='ADT_A44')
        msh.message_control_id = 'AKHMSG202509281330000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A47'
        evn.recorded_date_time = '20250928133000'
        evn.evn_5 = 'ADM050^Fischer^Margit^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P01012345', cx_4='AKHWIEN', cx_5='PI'), CX(cx_1='4108280590', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wimmer', xpn_2='Andreas', xpn_3='K', xpn_5='Herr')
        pid.date_time_of_birth = '19900228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Josefstaedter Strasse 77', xad_3='Wien', xad_5='1080', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4314040078901^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4108280590^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='P01012346', cx_4='AKHWIEN', cx_5='PI')

        # .. build the PATIENT group ..
        patient = AdtA44Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. assemble the full message ..
        msg = ADT_A44()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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

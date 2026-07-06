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
from zato.hl7v2.v2_9.datatypes import AUI, CWE, CX, EI, FC, HD, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA05Insurance, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A30, MDM_T02, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, DG1, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-cgm-clinical.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-cgm-clinical.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301080000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CGM20260301080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301075500'
        evn.evn_5 = 'EMP4401^Stadler^Ingrid^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43725241200^PRN^PH~+436643127890^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5831010183^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR', pl_9='CHIR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.^^^^CGMCLINICAL^^^^LANR&1.2.40.0.34.3.1.1&ISO'
        pv1.pv1_8 = 'ARZ200^Lang^Monika^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Fuchs', cwe_3='Robert', cwe_6='Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKH_STEYR')
        pv1.prior_temporary_location = PL(pl_1='20260301075500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Cholezystektomie laparoskopisch')
        pv2.referral_source_code = XCN(xcn_1='3')
        pv2.special_program_code = CWE(cwe_1='20260301')
        pv2.retention_indicator = '20260305'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Steiner', xpn_2='Gertrude', xpn_4='Frau')
        nk1.address = XAD(xad_1='+43725243100', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ÖGK', cwe_2='Österreichische Gesundheitskasse')
        in1.insurance_company_id = CX(cx_1='01')
        in1.insurance_company_name = XON(xon_1='Österreichische Gesundheitskasse')
        in1.authorization_information = AUI(aui_1='20260101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '5831010183'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301093000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CGM20260301093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260301093000'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='CGM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H'),
            XAD(xad_1='Ennskai 5', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='L'),
        ]
        pid.pid_13 = '+43725241200^PRN^PH~+436643127890^PRN^CP~^^Internet^wolfgang.steiner@gmx.at'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5831010183^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        pv1.pv1_8 = 'ARZ200^Lang^Monika^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Fuchs', cwe_3='Robert', cwe_6='Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKH_STEYR')
        pv1.prior_temporary_location = PL(pl_1='20260301075500')

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
    """ Based on live/at/at-cgm-clinical.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260305140000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CGM20260305140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260305140000'
        evn.evn_5 = 'EMP4401^Stadler^Ingrid^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43725241200^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5831010183^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        pv1.pv1_8 = 'ARZ200^Lang^Monika^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ100', cwe_2='Fuchs', cwe_3='Robert', cwe_6='Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='LKH_STEYR')
        pv1.prior_temporary_location = PL(pl_1='20260301075500')
        pv1.current_patient_balance = '20260305140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Cholelithiasis mit Cholezystitis', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260301'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='K81.0', cwe_2='Akute Cholezystitis', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20260301'
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
    """ Based on live/at/at-cgm-clinical.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260303160000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CGM20260303160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260303160000'
        evn.operator_id = XCN(xcn_1='EMP4410', xcn_2='Koller', xcn_3='Petra', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P823456', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='7193120275', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Katharina', xpn_3='Renate', xpn_5='Frau')
        pid.date_time_of_birth = '19750212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Dambergstraße 22', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43725255310^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '7193120275^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INNERE', pl_2='I205', pl_3='2', pl_4='LKH_STEYR', pl_9='INNERE')
        pv1.preadmit_number = CX(cx_1='CHIR', cx_2='C310', cx_3='1', cx_4='LKH_STEYR')
        pv1.pv1_9 = 'ARZ300^Wallner^Johann^^^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'ARZ300^Wallner^Johann^^^Dr.^med.'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='ÖGK')
        pv1.servicing_facility = CWE(cwe_1='LKH_STEYR')
        pv1.admit_date_time = '20260301120000'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.date_time_of_message = '20260410091500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CGM20260410091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260410091500'
        evn.operator_id = XCN(xcn_1='EMP5501', xcn_2='Aigner', xcn_3='Karin', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P934567', cx_4='KH_ELISABETHINEN_LINZ', cx_5='PI'), CX(cx_1='4821230990', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lechner', xpn_2='Susanne', xpn_3='Brigitte', xpn_5='Frau')
        pid.date_time_of_birth = '19900323'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mozartstraße 14', xad_3='Linz', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43732781234^PRN^PH~+436604523178^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4821230990^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='POLI-G1', pl_3='1', pl_4='KH_ELISABETHINEN_LINZ')
        pv1.pv1_7 = 'ARZ400^Reiter^Manfred^^^Univ.Prof.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='GAS')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='ARZ400', cwe_2='Reiter', cwe_3='Manfred', cwe_6='Univ.Prof.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='OUT')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='KH_ELISABETHINEN_LINZ')
        pv1.prior_temporary_location = PL(pl_1='20260410091500')

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
    """ Based on live/at/at-cgm-clinical.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260415100000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'CGM20260415100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20260415100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P145678', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='6274050688', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wimmer', xpn_2='Stefan', xpn_3='Johann', xpn_5='Herr')
        pid.date_time_of_birth = '19880506'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Grünmarkt 3', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43725262340^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6274050688^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='O401', pl_3='1', pl_4='LKH_STEYR', pl_9='ORTHO')
        pv1.pv1_7 = 'ARZ500^Kastner^Erich^^^Prim.Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='ORT')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ500', cwe_2='Kastner', cwe_3='Erich', cwe_6='Prim.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='SVS')
        pv1.diet_type = CWE(cwe_1='LKH_STEYR')
        pv1.prior_temporary_location = PL(pl_1='20260420080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Knie-TEP rechts')
        pv2.referral_source_code = XCN(xcn_1='5')
        pv2.special_program_code = CWE(cwe_1='20260420')
        pv2.retention_indicator = '20260425'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SVS', cwe_2='Sozialversicherungsanstalt der Selbständigen')
        in1.insurance_company_id = CX(cx_1='02')
        in1.insurance_company_name = XON(xon_1='Sozialversicherungsanstalt der Selbständigen')
        in1.authorization_information = AUI(aui_1='20260101')
        in1.plan_type = CWE(cwe_1='99991231')
        in1.delay_before_lr_day = '6274050688'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260318143000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A34', msg_3='ADT_A30')
        msh.message_control_id = 'CGM20260318143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A34'
        evn.recorded_date_time = '20260318143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='P998877', cx_4='LKH_STEYR', cx_5='PI')

        # .. assemble the full message ..
        msg = ADT_A30()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg

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
    """ Based on live/at/at-cgm-clinical.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.date_time_of_message = '20260501110000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'CGM20260501110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260501110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P256789', cx_4='KH_ELISABETHINEN_LINZ', cx_5='PI'), CX(cx_1='3516140795', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Elisabeth', xpn_3='Christine', xpn_5='Frau')
        pid.date_time_of_birth = '19950714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Herrenstraße 19', xad_3='Linz', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43732894321^PRN^PH~+436607712340^PRN^CP'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '3516140795^^^SVNR'
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
    """ Based on live/at/at-cgm-clinical.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KH_ELISABETHINEN_LINZ')
        msh.date_time_of_message = '20260502083000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'CGM20260502083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260502083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P256789', cx_4='KH_ELISABETHINEN_LINZ', cx_5='PI'), CX(cx_1='3516140795', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Moser', xpn_2='Elisabeth', xpn_3='Christine', xpn_5='Frau Dr.')
        pid.date_time_of_birth = '19950714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Graben 7', xad_3='Linz', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43732894321^PRN^PH~+436607712340^PRN^CP~^^Internet^elisabeth.moser@gmx.at'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '3516140795^^^SVNR'
        pid.birth_place = 'AUT'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-cgm-clinical.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260302070000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'CGM20260302070000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20260302070000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P367891', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='8462250172', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Helmut', xpn_3='Andreas', xpn_5='Herr')
        pid.date_time_of_birth = '19720125'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Haratzmüllerstraße 11', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+43725278341^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INNERE', pl_2='I201', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ300^Wallner^Johann^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='INT')
        pv1.pv1_40 = 'LKH_STEYR'
        pv1.discharge_date_time = '20260301150000'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260306083000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = 'CGM20260306083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20260306083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CHI')
        pv1.pv1_40 = 'LKH_STEYR'
        pv1.discharge_date_time = '20260301075500'

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/at/at-cgm-clinical.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='LABORSYSTEM')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301083000+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGM20260301083000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260301001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20260301083000+0100'
        orc.orc_12 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260301001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260301075000+0100'
        obr.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260301002')
        obr_2.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basisches Stoffwechselpanel', cwe_3='LN')
        obr_2.observation_date_time = '20260301075000+0100'
        obr_2.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260301003')
        obr_3.universal_service_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT (GPT)', cwe_3='LN')
        obr_3.observation_date_time = '20260301075000+0100'
        obr_3.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/at/at-cgm-clinical.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABORSYSTEM')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CGMCLINICAL')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301103000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260301103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260301001')
        orc.filler_order_number = EI(ei_1='LAB20260301001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260301075000+0100'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260301001')
        obr.filler_order_number = EI(ei_1='LAB20260301001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260301075000+0100'
        obr.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        obr.filler_field_2 = '20260301102500+0100'
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
        obx.date_time_of_the_observation = '20260301100000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '4.85'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '4.30-5.70'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260301100000+0100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx_3.obx_5 = '14.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.5-17.5'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260301100000+0100'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hämatokrit', cwe_3='LN')
        obx_4.obx_5 = '43.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '40.0-52.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260301100000+0100'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '89.1'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260301100000+0100'

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
        obx_6.date_time_of_the_observation = '20260301100000+0100'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_7.obx_5 = '5.4'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '4.0-6.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260301100000+0100'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABORSYSTEM')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CGMCLINICAL')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301110000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260301110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P823456', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='7193120275', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Katharina', xpn_3='Renate', xpn_5='Frau')
        pid.date_time_of_birth = '19750212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Dambergstraße 22', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INNERE', pl_2='I205', pl_3='2', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ300^Wallner^Johann^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260301004')
        orc.filler_order_number = EI(ei_1='LAB20260301004')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260301004')
        obr.filler_order_number = EI(ei_1='LAB20260301004')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Gerinnungspanel', cwe_3='LN')
        obr.observation_date_time = '20260301090000+0100'
        obr.obr_15 = 'ARZ300^Wallner^Johann^^^Dr.^med.'
        obr.filler_field_2 = '20260301105500+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombinzeit (Quick)', cwe_3='LN')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '70-130'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260301104000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.12'
        obx_2.reference_range = '0.85-1.15'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260301104000+0100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '26-40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260301104000+0100'

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
        obx_4.reference_range = '200-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260301104000+0100'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6012-9', cwe_2='D-Dimer', cwe_3='LN')
        obx_5.obx_5 = '0.35'
        obx_5.units = CWE(cwe_1='mg/L FEU')
        obx_5.reference_range = '<0.50'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260301104000+0100'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301084500+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CGM20260301084500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='RAD20260301001')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20260301084500+0100'
        orc.orc_12 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260301001')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Röntgen Thorax 2 Ebenen', cwe_3='CPT')
        obr.observation_date_time = '20260301080000+0100'
        obr.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        obr.parent_result = PRL(prl_2='Präoperative Kontrolle')

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
    """ Based on live/at/at-cgm-clinical.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CGMCLINICAL')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260301120000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RIS20260301120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='RAD20260301001')
        orc.filler_order_number = EI(ei_1='RAD20260301001R')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260301001')
        obr.filler_order_number = EI(ei_1='RAD20260301001R')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Röntgen Thorax 2 Ebenen', cwe_3='CPT')
        obr.observation_date_time = '20260301080000+0100'
        obr.obr_15 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        obr.filler_field_2 = '20260301115000+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71020', cwe_2='Röntgen Thorax', cwe_3='CPT')
        obx.obx_5 = (
            'Befund: Herz und Mediastinum unauffällig. Keine Infiltrate. Keine Ergüsse. Keine Stauungszeichen. Kostophrenische Winkel frei beidseits.\\.br'
            '\\Beurteilung: Altersentsprechender Normalbefund. Keine Kontraindikation für geplanten Eingriff.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260301114500+0100'
        obx.obx_16 = 'ARZ600^Holzer^Silvia^^^Dr.^med.'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='AKH_WIEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='AKH_WIEN')
        msh.date_time_of_message = '20260512143000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CGM20260512143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260512142500'
        evn.operator_id = XCN(xcn_1='EMP8801', xcn_2='Strobl', xcn_3='Claudia', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P478912', cx_4='AKH_WIEN', cx_5='PI'), CX(cx_1='2917150665', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pfeiffer&von', xpn_2='Leopold', xpn_3='Ernst', xpn_5='o.Univ.-Prof. Dr.')
        pid.date_time_of_birth = '19650115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Wipplingerstraße 25', xad_3='Wien', xad_5='1010', xad_6='AUT', xad_7='H')
        pid.pid_13 = '+4315324700^PRN^PH'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '2917150665^^^SVNR'
        pid.birth_place = 'AUT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='K501', pl_3='1', pl_4='AKH_WIEN', pl_9='KARD')
        pv1.pv1_7 = 'ARZ700^Egger^Werner^^^Univ.Prof.Dr.^med.^^^^CGMCLINICAL^^^^LANR&1.2.40.0.34.3.1.1&ISO'
        pv1.pv1_8 = 'ARZ701^Riegler^Barbara^^^OA Dr.^med.'
        pv1.consulting_doctor = XCN(xcn_1='CAR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ARZ700', cwe_2='Egger', cwe_3='Werner', cwe_6='Univ.Prof.Dr.', cwe_7='med.')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='ÖGK')
        pv1.diet_type = CWE(cwe_1='AKH_WIEN')
        pv1.prior_temporary_location = PL(pl_1='20260512142500')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='A009', cwe_2='Acetylsalicylsäure', cwe_3='LKH')
        al1.allergy_reaction_code = 'Urtikaria'
        al1.al1_6 = '20200610'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.al1 = al1

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
    """ Based on live/at/at-cgm-clinical.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABORSYSTEM')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CGMCLINICAL')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260302093000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260302093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P145678', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='6274050688', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Wimmer', xpn_2='Stefan', xpn_3='Johann', xpn_5='Herr')
        pid.date_time_of_birth = '19880506'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Grünmarkt 3', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='O401', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ500^Kastner^Erich^^^Prim.Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260302001')
        orc.filler_order_number = EI(ei_1='LAB20260302001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260302001')
        obr.filler_order_number = EI(ei_1='LAB20260302001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Basisches Stoffwechselpanel', cwe_3='LN')
        obr.observation_date_time = '20260302070000+0100'
        obr.obr_15 = 'ARZ500^Kastner^Erich^^^Prim.Dr.^med.'
        obr.filler_field_2 = '20260302092500+0100'
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
        obx.date_time_of_the_observation = '20260302090000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '0.91'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260302090000+0100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Harnstoff-N', cwe_3='LN')
        obx_3.obx_5 = '14'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260302090000+0100'

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
        obx_4.date_time_of_the_observation = '20260302090000+0100'

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
        obx_5.date_time_of_the_observation = '20260302090000+0100'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laborbefund komplett', cwe_3='LN')
        obx_6.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKExhYm9yYmVmdW5kIExLSCBT'
            'dGV5cikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgow'
            'IDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjUgMDAwMDAgbiAKMDAwMDAwMDEyMiAwMDAwMCBuIAowMDAwMDAwMjk2IDAwMDAwIG4gCjAw'
            'MDAwMDAzOTMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0NzYKJSVFT0Y='
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260302092500+0100'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CGMCLINICAL')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='ARCHIV')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260305150000+0100'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CGM20260305150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260305150000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P712345', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='5831010183', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Wolfgang', xpn_3='Martin', xpn_5='Herr')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 8', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='C312', pl_3='1', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Entlassungsbrief', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260305145000+0100'
        txa.txa_5 = 'ARZ100^Fuchs^Robert^^^Dr.^med.'
        txa.transcriptionist_code_name = XCN(xcn_1='DOC20260305001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11490-0', cwe_2='Entlassungsbrief', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA4MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEVudGxhc3N1bmdzYnJpZWYg'
            'LSBMYXBhcm9za29waXNjaGUgQ2hvbGV6eXN0ZWt0b21pZSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZv'
            'bnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjUgMDAwMDAgbiAKMDAwMDAwMDEyMiAw'
            'MDAwMCBuIAowMDAwMDAwMjk2IDAwMDAwIG4gCjAwMDAwMDAzOTMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0NzYKJSVFT0Y='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260305145000+0100'

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
    """ Based on live/at/at-cgm-clinical.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABORSYSTEM')
        msh.sending_facility = HD(hd_1='LKH_STEYR')
        msh.receiving_application = HD(hd_1='CGMCLINICAL')
        msh.receiving_facility = HD(hd_1='LKH_STEYR')
        msh.date_time_of_message = '20260304160000+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260304160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='P823456', cx_4='LKH_STEYR', cx_5='PI'), CX(cx_1='7193120275', cx_4='SVNR', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Hofer', xpn_2='Katharina', xpn_3='Renate', xpn_5='Frau')
        pid.date_time_of_birth = '19750212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Dambergstraße 22', xad_3='Steyr', xad_5='4400', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INNERE', pl_2='I205', pl_3='2', pl_4='LKH_STEYR')
        pv1.pv1_7 = 'ARZ300^Wallner^Johann^^^Dr.^med.'

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
        orc.placer_order_number = EI(ei_1='ORD20260302010')
        orc.filler_order_number = EI(ei_1='LAB20260304010')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260302010')
        obr.filler_order_number = EI(ei_1='LAB20260304010')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Bakterienkultur aerob', cwe_3='LN')
        obr.observation_date_time = '20260302100000+0100'
        obr.obr_15 = 'ARZ300^Wallner^Johann^^^Dr.^med.'
        obr.filler_field_2 = '20260304155000+0100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterienkultur aerob', cwe_3='LN')
        obx.obx_5 = 'ECOLI^Escherichia coli^SNM'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260304150000+0100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramm', cwe_3='LN')
        obx_2.obx_5 = 'Amoxicillin: R / Ciprofloxacin: S / Ceftriaxon: S / Meropenem: S / Trimethoprim-Sulfa: I'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260304150000+0100'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Klinisch relevanter Keim. Antibiotikaanpassung gemäß Antibiogramm empfohlen.'

        # .. build NTE ..
        nte_2 = NTE()
        nte_2.set_id_nte = '2'
        nte_2.nte_3 = 'Material: Mittelstrahlurin. Keimzahl >10^5 KBE/mL.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte
        observation_2.nte_2 = nte_2

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

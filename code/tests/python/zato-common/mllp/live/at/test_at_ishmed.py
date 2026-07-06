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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DR, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdrA19Insurance, AdrA19QueryResponse, AdtA01Insurance, AdtA01NextOfKin, AdtA05NextOfKin, BarP01Diagnosis, BarP01Visit, \
    MdmT02CommonOrder, MdmT02Observation, OrmO01Patient, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, \
    OruR01Visit
from zato.hl7v2.v2_9.messages import ADR_A19, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A30, ADT_A38, BAR_P01, MDM_T02, ORM_O01, ORU_R01, QRY_A19
from zato.hl7v2.v2_9.segments import DG1, EVN, FT1, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, QRD, TXA
from zato.hl7v2.z_segments import ZDS

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-ishmed.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-ishmed.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240401080512'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'ISH20240401080512001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240401080500'
        evn.operator_id = XCN(xcn_1='PFEIFFER', xcn_2='ELISABETH', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^336712~^PRN^CP^^0043^676^3918247'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='VIS20240401001', cx_4='TIROL_KLINIKEN', cx_5='VN')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GRUBER', xpn_2='MONIKA')
        nk1.address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^336713'
        nk1.contact_role = CWE(cwe_1='SPO')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='0415', pl_3='02', pl_4='LKI')
        pv1.pv1_7 = 'PFEIFFER^ELISABETH^^^DR.^^LANR^^^L'
        pv1.referring_doctor = XCN(xcn_1='FINK', xcn_2='JOHANN', xcn_5='DR.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'PFEIFFER^ELISABETH^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240401080500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20240408'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonie, nicht naeher bezeichnet', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240401080500'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK', xon_2='Oesterreichische Gesundheitskasse')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20241231'
        in1.name_of_insured = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        in1.insureds_relationship_to_patient = CWE(cwe_1='01')
        in1.insureds_date_of_birth = '19750104'
        in1.insureds_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT')
        in1.delay_before_lr_day = '4831040175'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1
        msg.insurance = insurance

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
    """ Based on live/at/at-ishmed.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240403101500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'ISH20240403101500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20240403101000'
        evn.operator_id = XCN(xcn_1='PFEIFFER', xcn_2='ELISABETH', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PNEU', pl_2='0210', pl_3='01', pl_4='LKI')
        pv1.pv1_7 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='PNEU')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240401080500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20240410'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/at/at-ishmed.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240408143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'ISH20240408143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240408142500'
        evn.operator_id = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PNEU', pl_2='0210', pl_3='01', pl_4='LKI')
        pv1.pv1_7 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='PNEU')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240401080500')
        pv1.admit_date_time = '20240408142500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonie, nicht naeher bezeichnet', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J44.1', cwe_2='COPD mit akuter Exazerbation', cwe_3='ICD-10-BMSG-2024')
        dg1_2.diagnosis_date_time = '20240402'
        dg1_2.diagnosis_type = CWE(cwe_1='W')

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
    """ Based on live/at/at-ishmed.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='KUK_LINZ')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KUK_LINZ')
        msh.date_time_of_message = '20240510093015'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'ISH20240510093015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240510093000'
        evn.operator_id = XCN(xcn_1='KASTNER', xcn_2='SUSANNE', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT044556', cx_4='KIS', cx_5='PI'), CX(cx_1='7214061288', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='LECHNER', xpn_2='STEFAN', xpn_3='ROBERT')
        pid.date_time_of_birth = '19881206'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='LANDSTRASSE 42', xad_3='LINZ', xad_4='OOE', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^732^285194~^PRN^CP^^0043^660^4527831'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='VIS20240505002', cx_4='KUK_LINZ', cx_5='VN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='0308', pl_3='01', pl_4='KUK')
        pv1.pv1_7 = 'KASTNER^SUSANNE^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.admit_source = CWE(cwe_1='R')
        pv1.pv1_17 = 'KASTNER^SUSANNE^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='KUK_LINZ')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240505140000')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/at/at-ishmed.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='KLINIKUM_KLU')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KLINIKUM_KLU')
        msh.date_time_of_message = '20240601140030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05')
        msh.message_control_id = 'ISH20240601140030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20240601140000'
        evn.operator_id = XCN(xcn_1='ORTNER', xcn_2='HELMUT', xcn_5='PRIM.DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT077889', cx_4='KIS', cx_5='PI'), CX(cx_1='8845050479', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='SCHWARZ', xpn_2='INGRID', xpn_3='RENATE')
        pid.date_time_of_birth = '19790405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='BAHNHOFSTRASSE 23', xad_3='KLAGENFURT', xad_4='K', xad_5='9020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^463^217834'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0501', pl_3='01', pl_4='KLU')
        pv1.pv1_7 = 'ORTNER^HELMUT^^^PRIM.DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='R')
        pv1.pv1_17 = 'ORTNER^HELMUT^^^PRIM.DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='KLINIKUM_KLU')
        pv1.pv1_40 = 'P'
        pv1.prior_temporary_location = PL(pl_1='20240610080000')

        # .. assemble the full message ..
        msg = ADT_A05()
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
    """ Based on live/at/at-ishmed.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240702094500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'ISH20240702094500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240702094500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='ISHMED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT012345', cx_4='KISS', cx_5='PI'), CX(cx_1='3317150793', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='HOFER', xpn_2='LUKAS', xpn_3='MARTIN')
        pid.date_time_of_birth = '19930715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='LEOPOLDSTRASSE 9', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^571408~^PRN^CP^^0043^650^2839164'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='HOFER', xpn_2='BRIGITTE')
        nk1.address = XAD(xad_1='LEOPOLDSTRASSE 9', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^571409'
        nk1.contact_role = CWE(cwe_1='MTH')

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
    """ Based on live/at/at-ishmed.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240702103000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'ISH20240702103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20240702103000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='ISHMED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT012345', cx_4='KISS', cx_5='PI'), CX(cx_1='3317150793', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='HOFER', xpn_2='LUKAS', xpn_3='MARTIN')
        pid.date_time_of_birth = '19930715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AMRASER STRASSE 22', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^571408~^PRN^CP^^0043^650^2839164'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')

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
    """ Based on live/at/at-ishmed.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240402100015'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ISH20240402100015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GRUBER', xpn_2='MONIKA')
        nk1.address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_6 = '^PRN^PH^^0043^512^336713'
        nk1.start_date = 'SPO'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PNEU', pl_2='0210', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='PNEU')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='DOPPLER', cwe_2='ANDREAS', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240401080500')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD20240402001')
        orc.filler_order_number = EI(ei_1='ORD20240402001F')
        orc.order_status = 'SC'
        orc.orc_10 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        orc.orc_12 = 'DOPPLER^ANDREAS^^^DR.^^LANR^^^L'
        orc.enterers_location = PL(pl_3='LKI')
        orc.call_back_phone_number = XTN(xtn_2='PRN', xtn_3='CP', xtn_5='0043', xtn_6='512', xtn_7='89059')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240402001')
        obr.filler_order_number = EI(ei_1='ORD20240402001F')
        obr.universal_service_identifier = CWE(cwe_1='XRAY-THOR', cwe_2='Roentgen Thorax 2 Ebenen', cwe_3='LOINC')
        obr.observation_date_time = '20240402100000'
        obr.obr_14 = 'V.a. Infiltrat rechts basal'
        obr.filler_field_1 = 'ACC20240402001'
        obr.diagnostic_serv_sect_id = '20240402100000'
        obr.obr_27 = 'R'

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.840.113619.2.55.3.4.5678.20240402100000'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [nk1, pv1, orc, obr, zds]

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
    """ Based on live/at/at-ishmed.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240402143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'RIS20240402143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PNEU', pl_2='0210', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='PNEU')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='DOPPLER', cwe_2='ANDREAS', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240401080500')

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
        orc.placer_order_number = EI(ei_1='ORD20240402001')
        orc.filler_order_number = EI(ei_1='ORD20240402001F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240402001')
        obr.filler_order_number = EI(ei_1='ORD20240402001F')
        obr.universal_service_identifier = CWE(cwe_1='XRAY-THOR', cwe_2='Roentgen Thorax 2 Ebenen', cwe_3='LOINC')
        obr.observation_date_time = '20240402100000'
        obr.filler_field_2 = 'ACC20240402001'
        obr.result_status = '20240402143000'
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='REPORT', cwe_2='Befund')
        obx.obx_5 = (
            'Roentgen Thorax in 2 Ebenen\\.br\\\\.br\\Fragestellung: V.a. Infiltrat rechts basal\\.br\\\\.br\\Befund:\\.br\\Herz normal gross und konfigurier'
            't.\\.br\\Streifige Verdichtung rechts basal, vereinbar mit Infiltrat.\\.br\\Kein Pleuraerguss. Kein Pneumothorax.\\.br\\\\.br\\Beurteilung: Pneu'
            'monisches Infiltrat rechts basal,\\.br\\klinische Kontrolle in 10 Tagen empfohlen.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='DIAG', cwe_2='Diagnose')
        obx_2.obx_5 = 'J18.9 Pneumonie, nicht naeher bezeichnet'
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
    """ Based on live/at/at-ishmed.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAURIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240402061500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'LAB20240402061500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='0415', pl_3='02', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='ELISABETH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='MED')

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
        orc.placer_order_number = EI(ei_1='LABORD002')
        orc.filler_order_number = EI(ei_1='LABORD002F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD002')
        obr.filler_order_number = EI(ei_1='LABORD002F')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Klinische Chemie', cwe_3='L')
        obr.observation_date_time = '20240402050000'
        obr.obr_15 = 'PFEIFFER^ELISABETH^^^DR.'
        obr.filler_field_2 = 'ACC20240402002'
        obr.result_status = '20240402061500'
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='GLU', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='KREA', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='GOT', cwe_2='GOT (AST)', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '0-35'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='GPT', cwe_2='GPT (ALT)', cwe_3='LN')
        obx_4.obx_5 = '32'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '0-45'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='GGT', cwe_2='Gamma-GT', cwe_3='LN')
        obx_5.obx_5 = '42'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '0-55'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='CRP', cwe_2='C-reaktives Protein', cwe_3='LN')
        obx_6.obx_5 = '48.5'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '0.0-5.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='PCT', cwe_2='Procalcitonin', cwe_3='LN')
        obx_7.obx_5 = '0.35'
        obx_7.units = CWE(cwe_1='ng/mL')
        obx_7.reference_range = '0.00-0.05'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leukozyten', cwe_3='LN')
        obx_8.obx_5 = '14.8'
        obx_8.units = CWE(cwe_1='10*3/uL')
        obx_8.reference_range = '4.0-10.0'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20240402061500'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='HGB', cwe_2='Haemoglobin', cwe_3='LN')
        obx_9.obx_5 = '14.2'
        obx_9.units = CWE(cwe_1='g/dL')
        obx_9.reference_range = '13.5-17.5'
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20240402061500'

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
    """ Based on live/at/at-ishmed.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAURIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240402062000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20240402062000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='VIS20240401001', cx_4='KISS')
        pv1.total_payments = 'V'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20240402062000'
        obr.specimen_action_code = 'F'
        obr.placer_field_1 = 'ACC20240402002'
        obr.obr_23 = 'LAB^Labor^LAB'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='LABRPT001', cwe_2='Laborbefund Klinische Chemie', cwe_4='CONT002', cwe_5='Laborbefunde', cwe_6='LABORATORY')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3'
            'MDAgVGQKKExhYm9yYmVmdW5kIEtsaW4uIENoZW1pZSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQg'
            'L0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1NiAwMDAw'
            'MCBuIAowMDAwMDAwMzM2IDAwMDAwIG4gCjAwMDAwMDA0MzUgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo1MTcKJSVFT0YK'
        )
        obx.interpretation_codes = CWE(cwe_1='LAB')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240402062000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/at/at-ishmed.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240408150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'ISH20240408150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='VIS20240401001', cx_4='KISS')
        pv1.total_payments = 'V'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20240408150000'
        obr.placer_field_1 = 'ACC20240401001'
        obr.obr_23 = 'MED^Innere Medizin^MED'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='ENTL', cwe_2='Entlassungsbrief', cwe_3='LOCAL')
        txa.document_content_presentation = 'PDF^PDF^LOCAL'
        txa.transcription_date_time = '20240408150000'
        txa.assigned_document_authenticator = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.', xcn_13='PNEU&Pneumologie&LOCAL', xcn_14='A')
        txa.placer_order_number = EI(ei_1='DOC20240408001')
        txa.document_confidentiality_status = 'Entlassungsbrief_Gruber.pdf'
        txa.document_availability_status = 'AU'
        txa.txa_29 = 'CONT003^Entlassungsbriefe^MEDICAL'
        txa.txa_30 = 'Entlassungsbrief Pneumonie'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3'
            'MDAgVGQKKEVudGxhc3N1bmdzYnJpZWYgUG5ldW1vbmllKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9u'
            'dCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTU2IDAw'
            'MDAwIG4gCjAwMDAwMDAzMzYgMDAwMDAgbiAKMDAwMDAwMDQzNiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjUxOAolJUVPRgo='
        )
        obx.interpretation_codes = CWE(cwe_1='ENTL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240408150000'

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
    """ Based on live/at/at-ishmed.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240408153000'
        msh.message_type = MSG(msg_1='BAR', msg_2='P01')
        msh.message_control_id = 'ISH20240408153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P01'
        evn.recorded_date_time = '20240408153000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PNEU', pl_2='0210', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='PNEU')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='DOPPLER', cwe_2='ANDREAS', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240401080500')
        pv1.prior_temporary_location = PL(pl_1='20240408142500')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonie, nicht naeher bezeichnet', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240401'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = BarP01Diagnosis()
        diagnosis.dg1 = dg1

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J44.1', cwe_2='COPD mit akuter Exazerbation', cwe_3='ICD-10-BMSG-2024')
        dg1_2.diagnosis_date_time = '20240402'
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build the DIAGNOSIS group ..
        diagnosis_2 = BarP01Diagnosis()
        diagnosis_2.dg1 = dg1_2

        # .. build the VISIT group ..
        visit = BarP01Visit()
        visit.pv1 = pv1
        visit.diagnosis = diagnosis
        visit.diagnosis_2 = diagnosis_2

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_batch_id = '20240402'
        ft1.transaction_date = DR(dr_1='20240402100000')
        ft1.transaction_posting_date = 'P'
        ft1.transaction_type = CWE(cwe_1='XRAY-THOR', cwe_2='Roentgen Thorax 2 Ebenen')
        ft1.ft1_8 = '1'
        ft1.health_plan_id = CWE(cwe_1='PNEU', cwe_2='0210', cwe_3='01', cwe_4='LKI')

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_batch_id = '20240404'
        ft1_2.transaction_date = DR(dr_1='20240404090000')
        ft1_2.transaction_posting_date = 'P'
        ft1_2.transaction_type = CWE(cwe_1='CT-THOR', cwe_2='CT Thorax mit KM')
        ft1_2.ft1_8 = '1'
        ft1_2.health_plan_id = CWE(cwe_1='PNEU', cwe_2='0210', cwe_3='01', cwe_4='LKI')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.insureds_group_emp_name = XON(xon_1='20240101')
        in1.plan_effective_date = '20241231'
        in1.plan_type = CWE(cwe_1='GRUBER', cwe_2='FRANZ', cwe_3='WOLFGANG')
        in1.name_of_insured = XPN(xpn_1='01')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19750104')
        in1.policy_number = '4831040175'

        # .. assemble the full message ..
        msg = BAR_P01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.extra_segments = [ft1, ft1_2, in1]

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
    """ Based on live/at/at-ishmed.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240801091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A34')
        msh.message_control_id = 'ISH20240801091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A34'
        evn.recorded_date_time = '20240801091500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='ISHMED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT012345', cx_4='KISS', cx_5='PI'), CX(cx_1='3317150793', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='HOFER', xpn_2='LUKAS', xpn_3='MARTIN')
        pid.date_time_of_birth = '19930715'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT019876', cx_4='KISS', cx_5='PI')

        # .. assemble the full message ..
        msg = ADT_A30()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg

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
    """ Based on live/at/at-ishmed.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='KLINIKUM_KLU')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='KLINIKUM_KLU')
        msh.date_time_of_message = '20240608100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A38')
        msh.message_control_id = 'ISH20240608100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A38'
        evn.recorded_date_time = '20240608100000'
        evn.operator_id = XCN(xcn_1='ORTNER', xcn_2='HELMUT', xcn_5='PRIM.DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT077889', cx_4='KIS', cx_5='PI'), CX(cx_1='8845050479', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='SCHWARZ', xpn_2='INGRID', xpn_3='RENATE')
        pid.date_time_of_birth = '19790405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='BAHNHOFSTRASSE 23', xad_3='KLAGENFURT', xad_4='K', xad_5='9020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0501', pl_3='01', pl_4='KLU')
        pv1.pv1_7 = 'ORTNER^HELMUT^^^PRIM.DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='R')
        pv1.pv1_17 = 'ORTNER^HELMUT^^^PRIM.DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='KLINIKUM_KLU')
        pv1.pv1_40 = 'P'
        pv1.prior_temporary_location = PL(pl_1='20240610080000')

        # .. assemble the full message ..
        msg = ADT_A38()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-ishmed.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAURIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240402050000'
        msh.message_type = MSG(msg_1='QRY', msg_2='A19')
        msh.message_control_id = 'QRY20240402050000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build QRD ..
        qrd = QRD()
        qrd.qrd_1 = '20240402050000'
        qrd.qrd_2 = 'R'
        qrd.qrd_3 = 'I'
        qrd.qrd_4 = 'QRY20240402050000001'
        qrd.qrd_7 = '1^RD'
        qrd.qrd_8 = 'PAT010203^^^KISS^PI'
        qrd.qrd_9 = 'DEM'

        # .. assemble the full message ..
        msg = QRY_A19()
        msg.msh = msh
        msg.qrd = qrd

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
    """ Based on live/at/at-ishmed.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='LAURIS')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240402050001'
        msh.message_type = MSG(msg_1='ADR', msg_2='A19')
        msh.message_control_id = 'ADR20240402050001001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'QRY20240402050000001'

        # .. build QRD ..
        qrd = QRD()
        qrd.qrd_1 = '20240402050000'
        qrd.qrd_2 = 'R'
        qrd.qrd_3 = 'I'
        qrd.qrd_4 = 'QRY20240402050000001'
        qrd.qrd_7 = '1^RD'
        qrd.qrd_8 = 'PAT010203^^^KISS^PI'
        qrd.qrd_9 = 'DEM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^336712~^PRN^CP^^0043^676^3918247'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GRUBER', xpn_2='MONIKA')
        nk1.address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^336713'
        nk1.contact_role = CWE(cwe_1='SPO')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='0415', pl_3='02', pl_4='LKI')
        pv1.pv1_7 = 'PFEIFFER^ELISABETH^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'PFEIFFER^ELISABETH^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240401080500')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.insureds_group_emp_name = XON(xon_1='20240101')
        in1.plan_effective_date = '20241231'
        in1.plan_type = CWE(cwe_1='GRUBER', cwe_2='FRANZ', cwe_3='WOLFGANG')
        in1.name_of_insured = XPN(xpn_1='01')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19750104')

        # .. build the INSURANCE group ..
        insurance = AdrA19Insurance()
        insurance.in1 = in1

        # .. build the QUERY_RESPONSE group ..
        query_response = AdrA19QueryResponse()
        query_response.pid = pid
        query_response.nk1 = nk1
        query_response.pv1 = pv1
        query_response.insurance = insurance

        # .. assemble the full message ..
        msg = ADR_A19()
        msg.msh = msh
        msg.msa = msa
        msg.qrd = qrd
        msg.query_response = query_response

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
    """ Based on live/at/at-ishmed.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EventServer')
        msh.sending_facility = HD(hd_1='RAD', hd_2='LKI_RADIOLOGIE', hd_3='L')
        msh.receiving_facility = HD(hd_1='ISHMED')
        msh.date_time_of_message = 'TIROL_KLINIKEN'
        msh.security = '20240402150000'
        msh.message_control_id = 'ORU^R01^ORU_R01'
        msh.processing_id = PT(pt_1='SS20240402150000001')
        msh.version_id = VID(vid_1='P')
        msh.sequence_number = '2.8.1'
        msh.continuation_pointer = '1'
        msh.principal_language_of_message = CWE(cwe_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI'), CX(cx_1='4831040175', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='A', cwe_2='austrian')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I', cwe_2='inpatient')
        pv1.visit_number = CX(cx_1='VIS20240401001', cx_4='KISS')
        pv1.service_episode_identifier = CX(cx_1='ALT20240401001', cx_4='KISS')
        pv1.pv1_55 = 'V'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'OP'
        orc.placer_order_number = EI(ei_1='ORD20240402001')
        orc.filler_order_number = EI(ei_1='ORD20240402001F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240402001')
        obr.filler_order_number = EI(ei_1='ORD20240402001F')
        obr.universal_service_identifier = CWE(cwe_1='XRAY-THOR', cwe_2='Roentgen Thorax 2 Ebenen')
        obr.observation_date_time = '20240402100000'
        obr.obr_17 = 'ACC20240402001'
        obr.filler_field_2 = '20240402150000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'RP'
        obx.observation_identifier = CWE(cwe_1='1.2.840.113619.2.55.3.4.9012.20240402100000', cwe_2='Roentgen Thorax', cwe_4='STUDY002')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'RP:2:TIROL_KLINIKEN:DICOM_STUDY:1.2.840.113619.2.55.3.4.9012.20240402100000^^^^100'
        obx.interpretation_codes = CWE(cwe_1='CR')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240402150000'
        obx.producers_id = CWE(cwe_1='RAD', cwe_2='Radiologie')

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
    """ Based on live/at/at-ishmed.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240409090000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T10', msg_3='MDM_T02')
        msh.message_control_id = 'ISH20240409090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT010203', cx_4='KISS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='GRUBER', xpn_2='FRANZ', xpn_3='WOLFGANG')
        pid.date_time_of_birth = '19750104'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='VIS20240401001', cx_4='KISS')
        pv1.total_payments = 'V'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20240409090000'
        obr.placer_field_1 = 'ACC20240401001'
        obr.obr_23 = 'MED^Innere Medizin^MED'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='ENTL', cwe_2='Entlassungsbrief korrigiert', cwe_3='LOCAL')
        txa.document_content_presentation = 'PDF^PDF^LOCAL'
        txa.transcription_date_time = '20240409090000'
        txa.assigned_document_authenticator = XCN(xcn_1='DOPPLER', xcn_2='ANDREAS', xcn_5='DR.', xcn_13='PNEU&Pneumologie&LOCAL', xcn_14='A')
        txa.placer_order_number = EI(ei_1='DOC20240408001')
        txa.document_confidentiality_status = 'Entlassungsbrief_Gruber_v2.pdf'
        txa.document_availability_status = 'AU'
        txa.txa_29 = 'CONT003^Entlassungsbriefe^MEDICAL'
        txa.txa_30 = 'Entlassungsbrief korrigiert'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'RP'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '\\E\\\\E\\lki-share01\\E\\archive\\E\\documents\\E\\Entlassungsbrief_Gruber_v2.pdf^^application^pdf'
        obx.interpretation_codes = CWE(cwe_1='ENTL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240409090000'

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
    """ Based on live/at/at-ishmed.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ISHMED')
        msh.sending_facility = HD(hd_1='SALK_SALZBURG')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_SALZBURG')
        msh.date_time_of_message = '20240920111500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13')
        msh.message_control_id = 'ISH20240920111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20240920111500'
        evn.operator_id = XCN(xcn_1='STADLER', xcn_2='WERNER', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT033221', cx_4='KIS', cx_5='PI'), CX(cx_1='6628061082', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WIMMER', xpn_2='KATHARINA', xpn_3='SUSANNE')
        pid.date_time_of_birth = '19821006'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='LINZER GASSE 27', xad_3='SALZBURG', xad_4='S', xad_5='5020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^662^814523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='0302', pl_3='01', pl_4='LKH')
        pv1.pv1_7 = 'STADLER^WERNER^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'STADLER^WERNER^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='SALK')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240915080000')
        pv1.admit_date_time = '20240920100000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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

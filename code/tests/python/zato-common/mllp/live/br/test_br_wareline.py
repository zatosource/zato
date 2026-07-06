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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DR, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA03Insurance, AdtA03Observation, AdtA05Insurance, BarP01Diagnosis, BarP01Visit, OrmO01Order, \
    OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, \
    OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, BAR_P01, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, AL1, DG1, EVN, FT1, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, RXD, RXE, RXO, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-wareline.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-wareline.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SC')
        msh.date_time_of_message = '20250320140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250320140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250320140000'
        evn.event_occurred = '20250320135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_14 = '^WPN^PH^^^^^^^^^551132001234'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='2345678', cx_4='SAO_CAMILO', cx_5='AN')
        pid.pid_32 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='401', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '12345^CASTRO^RODRIGO^HENRIQUE^^^Dr.^MD'
        pv1.pv1_9 = '12345^CASTRO^RODRIGO^HENRIQUE^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032001', cwe_4='SAO_CAMILO', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SUS')
        pv1.diet_type = CWE(cwe_1='SAO_CAMILO')
        pv1.pending_location = PL(pl_1='20250320140000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='J18.9', cwe_2='Pneumonia nao especificada', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_SP')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude - SP')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MENDES', cwe_2='RAFAEL', cwe_3='AUGUSTO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19670415')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Teodoro Sampaio 1020', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='05406-050', cwe_6='BR')
        in1.policy_number = 'SUS598765432'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MENDES', xpn_2='SANDRA', xpn_3='LUCIA')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5511987654321'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [nk1, dg1]

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
    """ Based on live/br/br-wareline.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SC')
        msh.date_time_of_message = '20250321082000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20250321082000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250321082000'
        evn.event_occurred = '20250321081500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '12345^CASTRO^RODRIGO^HENRIQUE^^^Dr.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.re_admission_indicator = CWE(cwe_1='TRN')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032001', cwe_4='SAO_CAMILO', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SUS')
        pv1.diet_type = CWE(cwe_1='SAO_CAMILO')
        pv1.pending_location = PL(pl_1='20250321082000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='J96.0', cwe_2='Insuficiencia respiratoria aguda', cwe_3='I10')

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
    """ Based on live/br/br-wareline.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_COPA_STAR', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_CS')
        msh.date_time_of_message = '20250321150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250321150000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250321150000'
        evn.event_occurred = '20250321145000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT302002', cx_4='COPA_STAR', cx_5='MR'), CX(cx_1='582.471.396-15', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BARROS', xpn_2='CLAUDIA', xpn_3='HELENA')
        pid.date_time_of_birth = '19780830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Atlantica 1702', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22021-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='205', pl_3='1', pl_6='COPA_STAR')
        pv1.pv1_7 = '32456^FRANCO^LUCIANA^BEATRIZ^^^Dra.^MD'
        pv1.pv1_9 = '32456^FRANCO^LUCIANA^BEATRIZ^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025031803', cwe_4='COPA_STAR', cwe_5='VN')
        pv1.visit_number = CX(cx_1='AMIL')
        pv1.diet_type = CWE(cwe_1='COPA_STAR')
        pv1.pending_location = PL(pl_1='20250321150000')
        pv1.discharge_date_time = '20250318100000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='K35.8', cwe_2='Apendicite aguda', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_RJ')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='BARROS', cwe_2='CLAUDIA', cwe_3='HELENA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19780830')
        in1.assignment_of_benefits = CWE(cwe_1='Av Atlantica 1702', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22021-001', cwe_6='BR')
        in1.policy_number = 'AMI6678901'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = AdtA03Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K35.8', cwe_2='Apendicite aguda, outra e a nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-wareline.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='CLINICA_EINSTEIN', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_EIN')
        msh.date_time_of_message = '20250322083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG20250322083000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250322083000'
        evn.event_occurred = '20250322082500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT403003', cx_4='EINSTEIN', cx_5='MR'), CX(cx_1='639.785.241-26', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='FREITAS', xpn_2='BRUNO', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19850712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Albert Einstein 627', xad_3='Sao Paulo', xad_4='SP', xad_5='05652-900', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432100'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='CONS03', pl_3='1', pl_6='EINSTEIN')
        pv1.pv1_7 = '42567^REZENDE^PAULA^CRISTINA^^^Dra.^MD'
        pv1.pv1_9 = '42567^REZENDE^PAULA^CRISTINA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032204', cx_4='EINSTEIN', cx_5='VN')
        pv1.financial_class = FC(fc_1='BRADESCO')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_SP')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240301'
        in1.plan_expiration_date = '20260228'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='FREITAS', cwe_2='BRUNO', cwe_3='HENRIQUE')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19850712')
        in1.assignment_of_benefits = CWE(cwe_1='Av Albert Einstein 627', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='05652-900', cwe_6='BR')
        in1.policy_number = 'BRD2234567'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

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
    """ Based on live/br/br-wareline.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS', hd_2='RS')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_MV')
        msh.date_time_of_message = '20250322100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250322100000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250322100000'
        evn.event_occurred = '20250322095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT504004', cx_4='MOINHOS', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SCHNEIDER', xpn_2='ELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19620320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987654098'
        pid.pid_14 = '^WPN^PH^^^^^^^^^555132101234'
        pid.marital_status = CWE(cwe_1='V')
        pid.patient_account_number = CX(cx_1='3456789', cx_4='MOINHOS', cx_5='AN')
        pid.pid_32 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='MOINHOS')
        pv1.pv1_7 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='MOINHOS', cx_5='VN')
        pv1.financial_class = FC(fc_1='SULAMERICA')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_4='SULAMERICA')
        in1.insurance_company_id = CX(cx_1='SULAM_RS')
        in1.insurance_company_name = XON(xon_1='SulAmerica Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SCHNEIDER', cwe_2='ELENA', cwe_3='MARIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19620320')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Ramiro Barcelos 910', cwe_3='Porto Alegre', cwe_4='RS', cwe_5='90035-001', cwe_6='BR')
        in1.policy_number = 'SUL3345678'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SCHNEIDER', xpn_2='MARCOS', xpn_3='HENRIQUE')
        nk1.relationship = CWE(cwe_1='SON')
        nk1.address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5551976543210'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [nk1]

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
    """ Based on live/br/br-wareline.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='CLINICA_FLEURY', hd_2='SP')
        msh.receiving_application = HD(hd_1='SCH_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_FLEURY')
        msh.date_time_of_message = '20250322110000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250322110000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='1')
        sch.filler_appointment_id = EI(ei_1='APT2025032200001', ei_2='WARELINE')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_1='CONSULTA CARDIOLOGIA', cwe_2='Consulta de rotina', cwe_4='60', cwe_5='min')
        sch.placer_contact_person = XCN(xcn_1='BOOKED')
        sch.placer_contact_address = XAD(xad_1='30')
        sch.placer_contact_location = PL(pl_1='min')
        sch.filler_contact_person = XCN(xcn_4='20250325093000', xcn_5='20250325100000')
        sch.sch_17 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        sch.sch_18 = '^PRN^PH^^^^^^^^^5511965432100'
        sch.filler_contact_location = PL(pl_1='Av Paulista 1000', pl_3='Sao Paulo', pl_4='SP', pl_5='01310-100', pl_6='BR')
        sch.sch_20 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        sch.entered_by_location = PL(pl_1='WARELINE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT605005', cx_4='FLEURY', cx_5='MR'), CX(cx_1='826.397.514-48', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='LOPES', xpn_2='MARIANA', xpn_3='SOUZA')
        pid.date_time_of_birth = '19900125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Pamplona 818', xad_3='Sao Paulo', xad_4='SP', xad_5='01405-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511954321087'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='CARD01', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        pv1.pv1_9 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='62789', cwe_2='ANDRADE', cwe_3='FABIO', cwe_4='CESAR', cwe_7='Dr.', cwe_8='MD')
        aig.resource_type = CWE(cwe_1='PHYSICIAN')

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AMB', pl_2='CARD01', pl_3='1', pl_6='FLEURY')
        ail.location_type_ail = CWE(cwe_1='CLINIC')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [aig, ail]

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
    """ Based on live/br/br-wareline.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='CLINICA_FLEURY', hd_2='SP')
        msh.receiving_application = HD(hd_1='SCH_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_FLEURY')
        msh.date_time_of_message = '20250323080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250323080000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='1')
        sch.filler_appointment_id = EI(ei_1='APT2025032200001', ei_2='WARELINE')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_1='CONSULTA CARDIOLOGIA', cwe_2='Consulta de rotina', cwe_4='60', cwe_5='min')
        sch.placer_contact_person = XCN(xcn_1='CANCELLED')
        sch.filler_contact_address = XAD(xad_1='62789', xad_2='ANDRADE', xad_3='FABIO', xad_4='CESAR', xad_7='Dr.', xad_8='MD')
        sch.sch_21 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        sch.parent_placer_appointment_id = EI(ei_1='WARELINE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT605005', cx_4='FLEURY', cx_5='MR'), CX(cx_1='826.397.514-48', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='LOPES', xpn_2='MARIANA', xpn_3='SOUZA')
        pid.date_time_of_birth = '19900125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Pamplona 818', xad_3='Sao Paulo', xad_4='SP', xad_5='01405-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511954321087'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='CARD01', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        pv1.pv1_9 = '62789^ANDRADE^FABIO^CESAR^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente solicitou cancelamento por motivos pessoais. Reagendar para proxima semana.'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [nte]

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
    """ Based on live/br/br-wareline.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='PHARM_RECEIVER')
        msh.receiving_facility = HD(hd_1='FARM_SC')
        msh.date_time_of_message = '20250321090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321090000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='SAO_CAMILO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100008', ei_2='SAO_CAMILO')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321093000^^R'
        orc.orc_10 = '20250321090000'
        orc.orc_11 = 'USR201^FERREIRA^LUCAS'
        orc.orc_14 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        orc.orc_19 = 'SAO_CAMILO^Hospital Sao Camilo^L'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = '50242001230^Ceftriaxona 1g IV^NDC'
        rxo.requested_give_units = CWE(cwe_1='1')
        rxo.requested_dosage_form = CWE(cwe_1='g')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='2')
        rxo.providers_administration_instructions = CWE(cwe_1='g')
        rxo.allow_substitutions = 'N'
        rxo.requested_dispense_amount = '1'
        rxo.number_of_refills = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr.administration_device = CWE(cwe_1='LA', cwe_2='Braco esquerdo', cwe_3='HL70163')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr]

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
    """ Based on live/br/br-wareline.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='PHARM_RECEIVER')
        msh.receiving_facility = HD(hd_1='FARM_SC')
        msh.date_time_of_message = '20250321093500'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MSG20250321093500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='SAO_CAMILO', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2025032100008', ei_2='SAO_CAMILO')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR202^SANTOS^AMANDA'
        orc.orc_18 = 'SAO_CAMILO^Hospital Sao Camilo^L'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^BID^HL70335'
        rxe.give_code = CWE(cwe_1='50242001230', cwe_2='Ceftriaxona 1g IV', cwe_3='NDC')
        rxe.give_amount_minimum = '1'
        rxe.give_amount_maximum = '1'
        rxe.give_units = CWE(cwe_1='g')
        rxe.give_dosage_form = CWE(cwe_1='VIAL')
        rxe.give_rate_units = CWE(cwe_1='20250321093500')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe

        # .. build RXD ..
        rxd = RXD()
        rxd.dispense_sub_id_counter = '1'
        rxd.dispense_give_code = CWE(cwe_1='50242001230', cwe_2='Ceftriaxona 1g IV', cwe_3='NDC')
        rxd.date_time_dispensed = '20250321093500'
        rxd.actual_dispense_amount = '1'
        rxd.actual_dispense_units = CWE(cwe_1='g')
        rxd.prescription_number = 'LOT2025A1234'
        rxd.number_of_refills_remaining = '20260321'
        rxd.rxd_13 = 'USR202^SANTOS^AMANDA'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr.administration_device = CWE(cwe_1='LA', cwe_2='Braco esquerdo', cwe_3='HL70163')

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxd, rxr]

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
    """ Based on live/br/br-wareline.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS', hd_2='RS')
        msh.receiving_application = HD(hd_1='SHIFT_LIS')
        msh.receiving_facility = HD(hd_1='LAB_MOINHOS')
        msh.date_time_of_message = '20250322060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322060000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT504004', cx_4='MOINHOS', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SCHNEIDER', xpn_2='ELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19620320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987654098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='MOINHOS')
        pv1.pv1_7 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='MOINHOS', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200010', ei_2='MOINHOS')
        orc.filler_order_number = EI(ei_1='FIL2025032200010', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322063000^^R'
        orc.orc_10 = '20250322060000'
        orc.orc_11 = 'USR203^PEREIRA^JULIANA'
        orc.orc_14 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        orc.orc_19 = 'MOINHOS^Hospital Moinhos de Vento^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200010', ei_2='MOINHOS')
        obr.filler_order_number = EI(ei_1='FIL2025032200010', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322063000'
        obr.obr_15 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        obr.result_status = '1^^^20250322063000^^R'

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
        obr_2.placer_order_number = EI(ei_1='ORD2025032200010', ei_2='MOINHOS')
        obr_2.filler_order_number = EI(ei_1='FIL2025032200010', ei_2='SHIFT')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr_2.observation_date_time = '20250322063000'
        obr_2.obr_15 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        obr_2.result_status = '1^^^20250322063000^^R'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/br/br-wareline.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_MOINHOS', hd_2='RS')
        msh.receiving_application = HD(hd_1='WARELINE')
        msh.receiving_facility = HD(hd_1='HOSP_MOINHOS')
        msh.date_time_of_message = '20250322090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322090000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT504004', cx_4='MOINHOS', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SCHNEIDER', xpn_2='ELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19620320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987654098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='MOINHOS')
        pv1.pv1_7 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='MOINHOS', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200010', ei_2='MOINHOS')
        orc.filler_order_number = EI(ei_1='FIL2025032200010', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR203^PEREIRA^JULIANA'
        orc.orc_18 = 'MOINHOS^Hospital Moinhos de Vento^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200010', ei_2='MOINHOS')
        obr.filler_order_number = EI(ei_1='FIL2025032200010', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr.observation_date_time = '20250322063000'
        obr.obr_14 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        obr.placer_field_1 = '20250322085900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '10.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322085900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '33.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322085900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '12800'
        obx_3.units = CWE(cwe_1='/uL')
        obx_3.reference_range = '4000-11000'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322085900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '310000'
        obx_4.units = CWE(cwe_1='/uL')
        obx_4.reference_range = '150000-400000'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322085900'

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
    """ Based on live/br/br-wareline.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAMARITANO', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SAM')
        msh.date_time_of_message = '20250323090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG20250323090000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250323090000'
        evn.event_occurred = '20250323085500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT706006', cx_4='SAMARITANO', cx_5='MR'), CX(cx_1='937.518.624-59', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CARDOSO', xpn_2='THIAGO', xpn_3='FELIPE')
        pid.date_time_of_birth = '19820925'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Conselheiro Brotero 1486', xad_3='Sao Paulo', xad_4='SP', xad_5='01232-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210854'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='OR02', pl_3='1', pl_6='SAMARITANO')
        pv1.pv1_7 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.patient_type = CWE(cwe_1='P')
        pv1.visit_number = CX(cx_1='VIS2025032512', cx_4='SAMARITANO', cx_5='VN')
        pv1.financial_class = FC(fc_1='AMIL')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_SP')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='CARDOSO', cwe_2='THIAGO', cwe_3='FELIPE')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19820925')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Conselheiro Brotero 1486', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01232-010', cwe_6='BR')
        in1.policy_number = 'AMI7789012'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M23.2', cwe_2='Lesao de menisco', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Artroscopia de joelho direito agendada para 25/03/2025. Internacao prevista D-1.'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1, nte]

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
    """ Based on live/br/br-wareline.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='MATERNIDADE_PRO_MATRE', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_PM')
        msh.date_time_of_message = '20250323220000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250323220000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250323220000'
        evn.event_occurred = '20250323215500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT807007', cx_4='PRO_MATRE', cx_5='MR'), CX(cx_1='063.527.918-50', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='ISABELA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19950718'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Humaita 275', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22261-005', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OBS', pl_2='LDR01', pl_3='1', pl_6='PRO_MATRE')
        pv1.pv1_7 = '82901^LIMA^FERNANDA^APARECIDA^^^Dra.^MD'
        pv1.pv1_9 = '82901^LIMA^FERNANDA^APARECIDA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='OBS')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032313', cwe_4='PRO_MATRE', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BRADESCO')
        pv1.diet_type = CWE(cwe_1='PRO_MATRE')
        pv1.pending_location = PL(pl_1='20250323220000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='O80', cwe_2='Parto normal espontaneo', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_RJ')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='GARCIA', cwe_2='ISABELA', cwe_3='CRISTINA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19950718')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Humaita 275', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22261-005', cwe_6='BR')
        in1.policy_number = 'BRD6678901'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GARCIA', xpn_2='MARCOS', xpn_3='EDUARDO')
        nk1.relationship = CWE(cwe_1='HUS')
        nk1.address = XAD(xad_1='Rua Humaita 275', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22261-005', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5521954321076'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Parto unico espontaneo', cwe_3='I10')
        dg1.diagnosis_date_time = '20250323'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [nk1, dg1]

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
    """ Based on live/br/br-wareline.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='MATERNIDADE_PRO_MATRE', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_PM')
        msh.date_time_of_message = '20250324012000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250324012000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250324012000'
        evn.event_occurred = '20250324011500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT807008', cx_4='PRO_MATRE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='RN DE ISABELA')
        pid.date_time_of_birth = '20250324'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Humaita 275', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22261-005', xad_6='BR')
        pid.strain = 'PAT807007'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OBS', pl_2='NUR01', pl_3='1', pl_6='PRO_MATRE')
        pv1.pv1_7 = '92012^SANTOS^PAULO^RICARDO^^^Dr.^MD'
        pv1.pv1_9 = '92012^SANTOS^PAULO^RICARDO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032414', cwe_4='PRO_MATRE', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BRADESCO')
        pv1.diet_type = CWE(cwe_1='PRO_MATRE')
        pv1.pending_location = PL(pl_1='20250324012000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='Z38.0', cwe_2='Nascido vivo em hospital', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_RJ')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='DEP')
        in1.insureds_relationship_to_patient = CWE(cwe_1='GARCIA', cwe_2='ISABELA', cwe_3='CRISTINA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19950718')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Humaita 275', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22261-005', cwe_6='BR')
        in1.policy_number = 'BRD6678901'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GARCIA', xpn_2='ISABELA', xpn_3='CRISTINA')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='Rua Humaita 275', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22261-005', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5521965432098'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [nk1]

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
    """ Based on live/br/br-wareline.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='BB_RECEIVER')
        msh.receiving_facility = HD(hd_1='BLOOD_BANK')
        msh.date_time_of_message = '20250321100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321100000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='SAO_CAMILO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100015', ei_2='SAO_CAMILO')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321103000^^S'
        orc.orc_10 = '20250321100000'
        orc.orc_11 = 'USR204^ALVES^RODRIGO'
        orc.orc_14 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        orc.orc_19 = 'SAO_CAMILO^Hospital Sao Camilo^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100015', ei_2='SAO_CAMILO')
        obr.universal_service_identifier = CWE(cwe_1='882-1', cwe_2='ABO AND RH GROUP', cwe_3='LN')
        obr.observation_date_time = '20250321103000'
        obr.obr_15 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        obr.result_status = '1^^^20250321103000^^S'

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
        obr_2.placer_order_number = EI(ei_1='ORD2025032100015', ei_2='SAO_CAMILO')
        obr_2.universal_service_identifier = CWE(cwe_1='984-5', cwe_2='CROSSMATCH', cwe_3='LN')
        obr_2.observation_date_time = '20250321103000'
        obr_2.obr_15 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        obr_2.result_status = '1^^^20250321103000^^S'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente com Hb 7.2. Reservar 2 unidades de concentrado de hemacias.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, nte]

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
    """ Based on live/br/br-wareline.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='BB_RECEIVER')
        msh.receiving_facility = HD(hd_1='BLOOD_BANK')
        msh.date_time_of_message = '20250321120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321120000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='SAO_CAMILO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100015', ei_2='SAO_CAMILO')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR204^ALVES^RODRIGO'
        orc.orc_18 = 'SAO_CAMILO^Hospital Sao Camilo^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100015', ei_2='SAO_CAMILO')
        obr.universal_service_identifier = CWE(cwe_1='882-1', cwe_2='ABO AND RH GROUP', cwe_3='LN')
        obr.observation_date_time = '20250321103000'
        obr.obr_14 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        obr.placer_field_1 = '20250321115900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='Tipo Sanguineo', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'A'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321115900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Fator Rh', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Positivo'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321115900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='984-5', cwe_2='Prova Cruzada', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Compativel'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321115900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='1250-0', cwe_2='Pesquisa de Anticorpos Irregulares', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Negativa'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321115900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Relatorio Hemoterapia', cwe_3='AUSPDI')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'WARELINE^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCA+PiA+'
            'PgplbmRvYmoKNCAwIG9iago8PCAvTGVuZ3RoIDU2ID4+CnN0cmVhbQpCVAovRjEgMTIgVGYKMTAwIDcwMCBUZAooUmVsYXRvcmlvIEhlbW90ZXJhcGlhIC0gVGlwYWdlbSBTYW5ndWlu'
            'ZWEpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZg=='
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321115900'
        obx_5.obx_16 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'

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
    """ Based on live/br/br-wareline.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS', hd_2='RS')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_MV')
        msh.date_time_of_message = '20250322110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250322110000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250322110000'
        evn.event_occurred = '20250322105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT504004', cx_4='MOINHOS', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SCHNEIDER', xpn_2='ELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19620320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987654098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='MOINHOS')
        pv1.pv1_7 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='MOINHOS', cx_5='VN')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='70618', cwe_2='Penicilina', cwe_3='NDFRT')
        al1.allergy_severity_code = CWE(cwe_1='SV')
        al1.allergy_reaction_code = 'Anafilaxia'
        al1.al1_6 = '20200315'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='FA')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='L-10315', cwe_2='Dipirona', cwe_3='ANVISA')
        al1_2.allergy_severity_code = CWE(cwe_1='MO')
        al1_2.allergy_reaction_code = 'Urticaria'
        al1_2.al1_6 = '20180610'

        # .. build AL1 ..
        al1_3 = AL1()
        al1_3.set_id_al1 = '3'
        al1_3.allergen_type_code = CWE(cwe_1='EA')
        al1_3.allergen_code_mnemonic_description = CWE(cwe_1='LATEX', cwe_2='Latex', cwe_3='LOCAL')
        al1_3.allergy_severity_code = CWE(cwe_1='MI')
        al1_3.allergy_reaction_code = 'Dermatite de contato'
        al1_3.al1_6 = '20190422'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.al1 = [al1, al1_2, al1_3]

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
    """ Based on live/br/br-wareline.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAMARITANO', hd_2='SP')
        msh.receiving_application = HD(hd_1='SCH_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SAM')
        msh.date_time_of_message = '20250323110000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250323110000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='1')
        sch.filler_appointment_id = EI(ei_1='APT2025032300001', ei_2='WARELINE')
        sch.event_reason = CWE(cwe_1='ELECTIVE')
        sch.appointment_reason = CWE(cwe_1='ARTROSCOPIA JOELHO', cwe_2='Artroscopia joelho direito', cwe_4='120', cwe_5='min')
        sch.placer_contact_person = XCN(xcn_1='BOOKED')
        sch.placer_contact_address = XAD(xad_1='60')
        sch.placer_contact_location = PL(pl_1='min')
        sch.filler_contact_person = XCN(xcn_4='20250325140000', xcn_5='20250325160000')
        sch.sch_17 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        sch.sch_18 = '^PRN^PH^^^^^^^^^5511954321065'
        sch.filler_contact_location = PL(pl_1='HOSP_SAMARITANO')
        sch.sch_20 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        sch.entered_by_location = PL(pl_1='WARELINE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT706006', cx_4='SAMARITANO', cx_5='MR'), CX(cx_1='937.518.624-59', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CARDOSO', xpn_2='THIAGO', xpn_3='FELIPE')
        pid.date_time_of_birth = '19820925'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Conselheiro Brotero 1486', xad_3='Sao Paulo', xad_4='SP', xad_5='01232-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210854'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='OR02', pl_3='1', pl_6='SAMARITANO')
        pv1.pv1_7 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '72890^FONSECA^ANTONIO^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.patient_type = CWE(cwe_1='P')
        pv1.visit_number = CX(cx_1='VIS2025032512', cx_4='SAMARITANO', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='72890', cwe_2='FONSECA', cwe_3='ANTONIO', cwe_4='CARLOS', cwe_7='Dr.', cwe_8='MD')
        aig.resource_type = CWE(cwe_1='SURGEON')

        # .. build AIG ..
        aig_2 = AIG()
        aig_2.set_id_aig = '2'
        aig_2.resource_id = CWE(cwe_1='82901', cwe_2='RIBAS', cwe_3='CARLOS', cwe_4='AUGUSTO', cwe_7='Dr.', cwe_8='MD')
        aig_2.resource_type = CWE(cwe_1='ANESTHESIOLOGIST')

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CIR', pl_2='OR02', pl_3='1', pl_6='SAMARITANO')
        ail.location_type_ail = CWE(cwe_1='OPERATING_ROOM')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente alergico a latex. Preparar sala com materiais latex-free.'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [aig, aig_2, ail, nte]

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
    """ Based on live/br/br-wareline.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS', hd_2='RS')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_MV')
        msh.date_time_of_message = '20250325100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250325100000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250325100000'
        evn.event_occurred = '20250325095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT504004', cx_4='MOINHOS', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SCHNEIDER', xpn_2='ELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19620320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Ramiro Barcelos 910', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987654098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='MOINHOS')
        pv1.pv1_7 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032005', cwe_4='MOINHOS', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SULAMERICA')
        pv1.diet_type = CWE(cwe_1='MOINHOS')
        pv1.pending_location = PL(pl_1='20250325100000')
        pv1.discharge_date_time = '20250320140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.1', cwe_2='Pneumonia lobar', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Resumo de Alta Hospitalar', cwe_3='AUSPDI')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'WARELINE^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA3OCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFJlc3VtbyBkZSBBbHRhIC0g'
            'U2NobmVpZGVyLCBFbGVuYSBNYXJpYSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iag=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250325095500'
        obx.obx_16 = '52678^SCHMIDT^HANS^CARLOS^^^Dr.^MD'

        # .. build the OBSERVATION group ..
        observation = AdtA03Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1
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
    """ Based on live/br/br-wareline.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WARELINE')
        msh.sending_facility = HD(hd_1='HOSP_SAO_CAMILO', hd_2='SP')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='SUS_SP')
        msh.date_time_of_message = '20250325140000'
        msh.message_type = MSG(msg_1='BAR', msg_2='P01', msg_3='BAR_P01')
        msh.message_control_id = 'MSG20250325140000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P01'
        evn.recorded_date_time = '20250325140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='PAT201001', cx_4='SAO_CAMILO', cx_5='MR'),
            CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF'),
            CX(cx_1='SUS598765432', cx_4='SUS', cx_5='NH'),
        ]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        pid.date_time_of_birth = '19670415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Teodoro Sampaio 1020', xad_3='Sao Paulo', xad_4='SP', xad_5='05406-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED02', pl_3='1', pl_6='SAO_CAMILO')
        pv1.pv1_7 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.pv1_9 = '22345^PEIXOTO^MARIANA^SILVA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032001', cwe_4='SAO_CAMILO', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SUS')
        pv1.diet_type = CWE(cwe_1='SAO_CAMILO')
        pv1.pending_location = PL(pl_1='20250325120000')
        pv1.discharge_date_time = '20250320140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = BarP01Diagnosis()
        diagnosis.dg1 = dg1

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J96.0', cwe_2='Insuficiencia respiratoria aguda', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250321'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

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
        ft1.transaction_id = CX(cx_1='20250320140000')
        ft1.transaction_batch_id = '20250325120000'
        ft1.transaction_date = DR(dr_1='AP')
        ft1.transaction_posting_date = '5'
        ft1.transaction_type = CWE(cwe_1='0301010048', cwe_2='DIARIA UTI ADULTO', cwe_3='SUS_SIGTAP')
        ft1.performed_by_code = XCN(xcn_1='0301010048')

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20250321090000')
        ft1_2.transaction_batch_id = '20250321090000'
        ft1_2.transaction_date = DR(dr_1='AP')
        ft1_2.transaction_posting_date = '5'
        ft1_2.transaction_type = CWE(cwe_1='0301070113', cwe_2='ANTIBIOTICOTERAPIA IV', cwe_3='SUS_SIGTAP')
        ft1_2.performed_by_code = XCN(xcn_1='0301070113')

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20250320140000')
        ft1_3.transaction_batch_id = '20250325120000'
        ft1_3.transaction_date = DR(dr_1='AP')
        ft1_3.transaction_posting_date = '1'
        ft1_3.transaction_type = CWE(cwe_1='0301010030', cwe_2='DIARIA ENF CLINICA', cwe_3='SUS_SIGTAP')
        ft1_3.performed_by_code = XCN(xcn_1='0301010030')

        # .. assemble the full message ..
        msg = BAR_P01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.extra_segments = [ft1, ft1_2, ft1_3]

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

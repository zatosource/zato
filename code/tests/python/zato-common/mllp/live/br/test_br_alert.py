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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01Observation, AdtA39Patient, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RspK21QueryResponse
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A39, ORM_O01, ORU_R01, QBP_Q21, RSP_K21
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, QAK, QPD, RCP, RXO, RXR

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-alert.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-alert.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_VILA_MARIANA', hd_2='SP')
        msh.receiving_application = HD(hd_1='PIX_MGR')
        msh.receiving_facility = HD(hd_1='MPI_SES')
        msh.date_time_of_message = '20250320193000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250320193000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_PIX', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250320193000'
        evn.event_occurred = '20250320192500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='PAT010101', cx_4='UPA_VM', cx_5='MR'),
            CX(cx_1='482.193.756-08', cx_4='BR', cx_5='CPF'),
            CX(cx_1='SUS847362195', cx_4='SUS', cx_5='NH'),
        ]
        pid.patient_name = XPN(xpn_1='GOMES', xpn_2='ROBERTO', xpn_3='FERNANDO')
        pid.date_time_of_birth = '19720415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Domingos de Morais 1840', xad_3='Sao Paulo', xad_4='SP', xad_5='04010-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511994827361'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='TRIAGE', pl_3='1', pl_6='UPA_VM')
        pv1.pv1_7 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='UPA_VM', cx_5='VN')
        pv1.financial_class = FC(fc_1='SUS')
        pv1.servicing_facility = CWE(cwe_1='UPA_VM')
        pv1.prior_temporary_location = PL(pl_1='20250320193000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='I21.9', cwe_2='Infarto agudo do miocardio nao especificado', cwe_3='I10')
        pv2.referral_source_code = XCN(xcn_1='2', xcn_2='Emergencia', xcn_3='ALERT_TRIAGE')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_SP')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='GOMES', cwe_2='ROBERTO', cwe_3='FERNANDO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19720415')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Domingos de Morais 1840', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='04010-200', cwe_6='BR')
        in1.policy_number = 'SUS847362195'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.9', cwe_2='Infarto agudo do miocardio nao especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Dor toracica nao especificada', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250320'
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [dg1, dg1_2]

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
    """ Based on live/br/br-alert.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_BARRA_FUNDA', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_UPA')
        msh.date_time_of_message = '20250320193500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG20250320193500002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250320193500'
        evn.event_occurred = '20250320193000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT020202', cx_4='UPA_BF', cx_5='MR'), CX(cx_1='315.728.064-19', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='LIMA', xpn_2='BEATRIZ', xpn_3='HELENA')
        pid.date_time_of_birth = '19651128'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Pacaembu 720', xad_3='Sao Paulo', xad_4='SP', xad_5='01234-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511983729104'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='TRIAGE', pl_3='1', pl_6='UPA_BF')
        pv1.pv1_7 = '30418^CAVALCANTI^RODRIGO^AURELIO^^^Dr.^MD'
        pv1.pv1_9 = '30418^CAVALCANTI^RODRIGO^AURELIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032002', cx_4='UPA_BF', cx_5='VN')
        pv1.financial_class = FC(fc_1='SUS')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='R10.4', cwe_2='Dor abdominal', cwe_3='I10')
        pv2.referral_source_code = XCN(xcn_1='3', xcn_2='Urgente', xcn_3='ALERT_TRIAGE')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='TRIAGE_CLASS', cwe_2='Classificacao Manchester', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '3^Urgente - Amarelo^MANCHESTER'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320193500'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='TRIAGE_DISC', cwe_2='Discriminador', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Dor abdominal intensa de inicio subito ha 6 horas'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8310-5', cwe_2='Temperatura Corporal', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '37.8'
        obx_3.units = CWE(cwe_1='Cel')
        obx_3.reference_range = '36.0-37.5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frequencia Cardiaca', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '98'
        obx_4.units = CWE(cwe_1='bpm')
        obx_4.reference_range = '60-100'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = AdtA01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8480-6', cwe_2='Pressao Arterial Sistolica', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '145'
        obx_5.units = CWE(cwe_1='mmHg')
        obx_5.reference_range = '90-140'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = AdtA01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='8462-4', cwe_2='Pressao Arterial Diastolica', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '92'
        obx_6.units = CWE(cwe_1='mmHg')
        obx_6.reference_range = '60-90'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = AdtA01Observation()
        observation_6.obx = obx_6

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5, observation_6]

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
    """ Based on live/br/br-alert.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_VICENTE', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SV')
        msh.date_time_of_message = '20250321081000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250321081000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250321081000'
        evn.event_occurred = '20250321080500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT030303', cx_4='SV_RJ', cx_5='MR'), CX(cx_1='628.491.357-24', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='GABRIEL', xpn_3='EDUARDO')
        pid.date_time_of_birth = '20180815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Voluntarios da Patria 480', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521992847163'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='PED01', pl_3='1', pl_6='SV_RJ')
        pv1.pv1_7 = '40562^CARDOSO^PATRICIA^LUCIANA^^^Dra.^MD'
        pv1.pv1_9 = '40562^CARDOSO^PATRICIA^LUCIANA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032103', cx_4='SV_RJ', cx_5='VN')
        pv1.financial_class = FC(fc_1='BRADESCO')
        pv1.servicing_facility = CWE(cwe_1='SV_RJ')
        pv1.prior_temporary_location = PL(pl_1='20250321081000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='J06.9', cwe_2='Infeccao aguda VAS', cwe_3='I10')
        pv2.referral_source_code = XCN(xcn_1='3', xcn_2='Urgente', xcn_3='ALERT_TRIAGE')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO')
        in1.insurance_company_id = CX(cx_1='BRAD_RJ')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='DEP')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MENDES', cwe_2='RICARDO', cwe_3='ALVES')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19831205')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Voluntarios da Patria 480', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22270-010', cwe_6='BR')
        in1.policy_number = 'BRAD7821469'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MENDES', xpn_2='RICARDO', xpn_3='ALVES')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='Rua Voluntarios da Patria 480', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5521992847163'

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='MENDES', xpn_2='FERNANDA', xpn_3='OLIVEIRA')
        nk1_2.relationship = CWE(cwe_1='MTH')
        nk1_2.address = XAD(xad_1='Rua Voluntarios da Patria 480', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        nk1_2.nk1_5 = '^PRN^PH^^^^^^^^^5521988273645'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J06.9', cwe_2='Infeccao aguda das vias aereas superiores', cwe_3='I10')
        dg1.diagnosis_date_time = '20250321'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [nk1, nk1_2, dg1]

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
    """ Based on live/br/br-alert.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA_CWB', hd_2='PR')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SC')
        msh.date_time_of_message = '20250321143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20250321143000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250321143000'
        evn.event_occurred = '20250321142500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT040404', cx_4='SC_CWB', cx_5='MR'), CX(cx_1='739.582.461-30', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='REIS', xpn_2='MARCOS', xpn_3='VINICIUS')
        pid.date_time_of_birth = '19821010'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Sete de Setembro 2940', xad_3='Curitiba', xad_4='PR', xad_5='80250-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541986374829'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OBS', pl_2='BED05', pl_3='1', pl_6='SC_CWB')
        pv1.pv1_7 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'
        pv1.pv1_9 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.re_admission_indicator = CWE(cwe_1='TRN')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032104', cwe_4='SC_CWB', cwe_5='VN')
        pv1.visit_number = CX(cx_1='UNIMED')
        pv1.diet_type = CWE(cwe_1='SC_CWB')
        pv1.pending_location = PL(pl_1='20250321143000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='K85.9', cwe_2='Pancreatite aguda nao especificada', cwe_3='I10')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/br/br-alert.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_VILA_MARIANA', hd_2='SP')
        msh.receiving_application = HD(hd_1='LAB_RECEIVER')
        msh.receiving_facility = HD(hd_1='LAB_UPA')
        msh.date_time_of_message = '20250320200000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250320200000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010101', cx_4='UPA_VM', cx_5='MR'), CX(cx_1='482.193.756-08', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GOMES', xpn_2='ROBERTO', xpn_3='FERNANDO')
        pid.date_time_of_birth = '19720415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Domingos de Morais 1840', xad_3='Sao Paulo', xad_4='SP', xad_5='04010-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511994827361'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED01', pl_3='1', pl_6='UPA_VM')
        pv1.pv1_7 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='UPA_VM', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='UPA_VM')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR301^DIAS^LARISSA'
        orc.orc_18 = 'UPA_VM^UPA Vila Mariana^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='UPA_VM')
        obr.universal_service_identifier = CWE(cwe_1='10839-9', cwe_2='TROPONIN I', cwe_3='LN')
        obr.observation_date_time = '20250320194000'
        obr.obr_14 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        obr.placer_field_1 = '20250320195900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='10839-9', cwe_2='Troponina I Ultrassensivel', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '2.45'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '<0.04'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320195900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2157-6', cwe_2='CK-MB', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '45.2'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '<25'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320195900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33762-6', cwe_2='NT-proBNP', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '1250'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '<125'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320195900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glicose', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '70-99'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320195900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Troponina marcadamente elevada. Protocolo de SCA ativado.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

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
    """ Based on live/br/br-alert.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_VILA_MARIANA', hd_2='SP')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_UPA')
        msh.date_time_of_message = '20250320201500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250320201500006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250320201500'
        evn.event_occurred = '20250320201000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010101', cx_4='UPA_VM', cx_5='MR'), CX(cx_1='482.193.756-08', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GOMES', xpn_2='ROBERTO', xpn_3='FERNANDO')
        pid.date_time_of_birth = '19720415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Domingos de Morais 1840', xad_3='Sao Paulo', xad_4='SP', xad_5='04010-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511994827361'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED01', pl_3='1', pl_6='UPA_VM')
        pv1.pv1_7 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='UPA_VM', cx_5='VN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='8310-5', cwe_2='Temperatura', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '36.8'
        obx.units = CWE(cwe_1='Cel')
        obx.reference_range = '36.0-37.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frequencia Cardiaca', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '88'
        obx_2.units = CWE(cwe_1='bpm')
        obx_2.reference_range = '60-100'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8480-6', cwe_2='PA Sistolica', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '130'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '90-140'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8462-4', cwe_2='PA Diastolica', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '85'
        obx_4.units = CWE(cwe_1='mmHg')
        obx_4.reference_range = '60-90'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_4 = AdtA01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9279-1', cwe_2='Frequencia Respiratoria', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '18'
        obx_5.units = CWE(cwe_1='rpm')
        obx_5.reference_range = '12-20'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_5 = AdtA01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2708-6', cwe_2='SpO2', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '96'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_6 = AdtA01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='72514-3', cwe_2='Escala de Dor (EVA)', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '3'
        obx_7.units = CWE(cwe_1='/10')
        obx_7.reference_range = '0-3'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250320201500'

        # .. build the OBSERVATION group ..
        observation_7 = AdtA01Observation()
        observation_7.obx = obx_7

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5, observation_6, observation_7]

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
    """ Based on live/br/br-alert.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_VILA_MARIANA', hd_2='SP')
        msh.receiving_application = HD(hd_1='PHARM_RECEIVER')
        msh.receiving_facility = HD(hd_1='FARM_UPA')
        msh.date_time_of_message = '20250320194500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250320194500007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010101', cx_4='UPA_VM', cx_5='MR'), CX(cx_1='482.193.756-08', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GOMES', xpn_2='ROBERTO', xpn_3='FERNANDO')
        pid.date_time_of_birth = '19720415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Domingos de Morais 1840', xad_3='Sao Paulo', xad_4='SP', xad_5='04010-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511994827361'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED01', pl_3='1', pl_6='UPA_VM')
        pv1.pv1_7 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='UPA_VM', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000007', ei_2='UPA_VM')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250320195000^^S'
        orc.orc_10 = '20250320194500'
        orc.orc_11 = 'USR302^NUNES^DANIEL'
        orc.orc_14 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        orc.orc_19 = 'UPA_VM^UPA Vila Mariana^L'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = '36987^Heparina Sodica 5000UI SC^ANVISA'
        rxo.requested_give_units = CWE(cwe_1='5000')
        rxo.requested_dosage_form = CWE(cwe_1='UI')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='1')
        rxo.allow_substitutions = 'N'
        rxo.requested_dispense_amount = '1'
        rxo.number_of_refills = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='SC', cwe_2='Subcutaneo', cwe_3='HL70162')
        rxr.administration_device = CWE(cwe_1='ABD', cwe_2='Abdomen', cwe_3='HL70163')

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='2')
        rxo_2.requested_give_amount_minimum = '12345^AAS 100mg VO^ANVISA'
        rxo_2.requested_give_units = CWE(cwe_1='100')
        rxo_2.requested_dosage_form = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='1')
        rxo_2.allow_substitutions = 'N'
        rxo_2.requested_dispense_amount = '1'
        rxo_2.number_of_refills = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. build RXO ..
        rxo_3 = RXO()
        rxo_3.requested_give_code = CWE(cwe_1='3')
        rxo_3.requested_give_amount_minimum = '67890^Clopidogrel 300mg VO^ANVISA'
        rxo_3.requested_give_units = CWE(cwe_1='300')
        rxo_3.requested_dosage_form = CWE(cwe_1='mg')
        rxo_3.providers_pharmacy_treatment_instructions = CWE(cwe_1='1')
        rxo_3.allow_substitutions = 'N'
        rxo_3.requested_dispense_amount = '1'
        rxo_3.number_of_refills = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'

        # .. build RXR ..
        rxr_3 = RXR()
        rxr_3.route = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, rxo_2, rxr_2, rxo_3, rxr_3]

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
    """ Based on live/br/br-alert.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_VICENTE', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SV')
        msh.date_time_of_message = '20250321120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250321120000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250321120000'
        evn.event_occurred = '20250321115500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT030303', cx_4='SV_RJ', cx_5='MR'), CX(cx_1='628.491.357-24', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MENDES', xpn_2='GABRIEL', xpn_3='EDUARDO')
        pid.date_time_of_birth = '20180815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Voluntarios da Patria 480', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521992847163'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='PED01', pl_3='1', pl_6='SV_RJ')
        pv1.pv1_7 = '40562^CARDOSO^PATRICIA^LUCIANA^^^Dra.^MD'
        pv1.pv1_9 = '40562^CARDOSO^PATRICIA^LUCIANA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032103', cwe_4='SV_RJ', cwe_5='VN')
        pv1.visit_number = CX(cx_1='BRADESCO')
        pv1.diet_type = CWE(cwe_1='SV_RJ')
        pv1.pending_location = PL(pl_1='20250321120000')
        pv1.discharge_date_time = '20250321081000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='J06.9', cwe_2='Infeccao aguda VAS', cwe_3='I10')
        pv2.estimated_length_of_inpatient_stay = '01^Alta melhorado^ALERT_DISP'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J06.9', cwe_2='Infeccao aguda das vias aereas superiores', cwe_3='I10')
        dg1.diagnosis_date_time = '20250321'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Prescricao de alta: Amoxicilina 50mg/kg/dia 8/8h por 7 dias. Retorno se piora.'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1
        msg.extra_segments = [nte]

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
    """ Based on live/br/br-alert.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SR')
        msh.date_time_of_message = '20250322041500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250322041500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250322041500'
        evn.event_occurred = '20250322041000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='STROKE', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032209', cx_4='SR_BA', cx_5='VN')
        pv1.financial_class = FC(fc_1='SUS')
        pv1.servicing_facility = CWE(cwe_1='SR_BA')
        pv1.prior_temporary_location = PL(pl_1='20250322041500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='I63.9', cwe_2='AVC isquemico nao especificado', cwe_3='I10')
        pv2.referral_source_code = XCN(xcn_1='1', xcn_2='Emergencia', xcn_3='ALERT_TRIAGE')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_BA')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='ALVES', cwe_2='FRANCISCO', cwe_3='GERALDO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19531122')
        in1.assignment_of_benefits = CWE(cwe_1='Av Tancredo Neves 2782', cwe_3='Salvador', cwe_4='BA', cwe_5='41820-021', cwe_6='BR')
        in1.policy_number = 'SUS562839471'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Infarto cerebral nao especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PROTOCOL', cwe_2='Protocolo AVC', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Protocolo de AVC ativado. Tempo porta: 15min. NIHSS: 12.'
        obx.observation_result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TS'
        obx_2.observation_identifier = CWE(cwe_1='ONSET_TIME', cwe_2='Inicio Sintomas', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '20250322030000'
        obx_2.observation_result_status = 'F'

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='NIHSS', cwe_2='NIHSS Score', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '12'
        obx_3.reference_range = '0-5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Janela terapeutica para trombólise. TC cranio sem contraste URGENTE.'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [dg1, obx, obx_2, obx_3, nte]

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
    """ Based on live/br/br-alert.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='UPA_VILA_MARIANA', hd_2='SP')
        msh.receiving_application = HD(hd_1='ECG_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_UPA')
        msh.date_time_of_message = '20250320195500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250320195500010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT010101', cx_4='UPA_VM', cx_5='MR'), CX(cx_1='482.193.756-08', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GOMES', xpn_2='ROBERTO', xpn_3='FERNANDO')
        pid.date_time_of_birth = '19720415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Domingos de Morais 1840', xad_3='Sao Paulo', xad_4='SP', xad_5='04010-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511994827361'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED01', pl_3='1', pl_6='UPA_VM')
        pv1.pv1_7 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='UPA_VM', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000010', ei_2='UPA_VM')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR303^ROCHA^CAMILA'
        orc.orc_18 = 'UPA_VM^UPA Vila Mariana^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000010', ei_2='UPA_VM')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='ECG 12 DERIVACOES', cwe_3='CPT4')
        obr.observation_date_time = '20250320194500'
        obr.obr_14 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'
        obr.placer_field_1 = '20250320195400'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG LAUDO', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'ECG 12 derivacoes - Ritmo sinusal. FC 88bpm. Supradesnivelamento de ST em V1-V4 e DII, DIII, aVF.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG LAUDO', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'CONCLUSAO: IAM com supra de ST anterosseptal. Indicacao de cateterismo de urgencia.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='ECG 12 Derivacoes Completo', cwe_3='AUSPDI')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'ALERT_CIS^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA4NDEgNTk1XSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCA+PiA+'
            'PgplbmRvYmoKNCAwIG9iago8PCAvTGVuZ3RoIDUyID4+CnN0cmVhbQpCVAovRjEgMTQgVGYKMTAwIDUwMCBUZAooRUNHIDEyIERlcml2YWNvZXMgLSBJQU0gU1NUKSBUagpFVAplbmRz'
            'dHJlYW0KZW5kb2Jq'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320195400'
        obx_3.obx_16 = '30245^MARTINS^FELIPE^AUGUSTO^^^Dr.^MD'

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
    """ Based on live/br/br-alert.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_INSTITUTO_PHILIPPE', hd_2='MG')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_IPP')
        msh.date_time_of_message = '20250322230000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250322230000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250322230000'
        evn.event_occurred = '20250322225500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT060606', cx_4='IPP_MG', cx_5='MR'), CX(cx_1='963.482.715-73', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BARBOSA', xpn_2='NATALIA', xpn_3='FERNANDA')
        pid.date_time_of_birth = '19890628'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Afonso Pena 1870', xad_3='Belo Horizonte', xad_4='MG', xad_5='30130-005', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531987462519'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='PSY01', pl_3='1', pl_6='IPP_MG')
        pv1.pv1_7 = '70839^VIEIRA^SERGIO^MAURICIO^^^Dr.^MD'
        pv1.pv1_9 = '70839^VIEIRA^SERGIO^MAURICIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='PSY')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032211', cx_4='IPP_MG', cx_5='VN')
        pv1.financial_class = FC(fc_1='HAPVIDA')
        pv1.servicing_facility = CWE(cwe_1='IPP_MG')
        pv1.prior_temporary_location = PL(pl_1='20250322230000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='F32.2', cwe_2='Episodio depressivo grave sem sintomas psicoticos', cwe_3='I10')
        pv2.referral_source_code = XCN(xcn_1='2', xcn_2='Emergencia', xcn_3='ALERT_TRIAGE')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='HAPVIDA', cwe_4='HAPVIDA')
        in1.insurance_company_id = CX(cx_1='HAP_MG')
        in1.insurance_company_name = XON(xon_1='Hapvida Saude')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='BARBOSA', cwe_2='NATALIA', cwe_3='FERNANDA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19890628')
        in1.assignment_of_benefits = CWE(cwe_1='Av Afonso Pena 1870', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='30130-005', cwe_6='BR')
        in1.policy_number = 'HAP4729183'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='F32.2', cwe_2='Episodio depressivo grave sem sintomas psicoticos', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='X78', cwe_2='Lesao autoprovocada intencionalmente por objeto cortante', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250322'
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BARBOSA', xpn_2='LEONARDO', xpn_3='TIAGO')
        nk1.relationship = CWE(cwe_1='BRO')
        nk1.address = XAD(xad_1='Av Afonso Pena 1870', xad_3='Belo Horizonte', xad_4='MG', xad_5='30130-005', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5531976382947'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [dg1, dg1_2, nk1]

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
    """ Based on live/br/br-alert.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SR')
        msh.date_time_of_message = '20250322050000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250322050000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250322050000'
        evn.event_occurred = '20250322045500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='STROKE', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032209', cx_4='SR_BA', cx_5='VN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='GLASGOW', cwe_2='Escala de Glasgow', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '14^E4V4M6^GLASGOW'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322050000'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='BRADEN', cwe_2='Escala de Braden', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '16'
        obx_2.reference_range = '>18'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322050000'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='FALL_RISK', cwe_2='Risco de Queda Morse', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '55^Alto Risco^MORSE'
        obx_3.reference_range = '>45'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322050000'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='NURSING_DX', cwe_2='Diagnostico de Enfermagem', cwe_3='LOCAL')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Risco de integridade da pele prejudicada relacionado a imobilidade'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = AdtA01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='NURSING_INT', cwe_2='Intervencao de Enfermagem', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Mudanca de decubito 2/2h. Colchao pneumatico. Hidratacao cutanea.'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = AdtA01Observation()
        observation_5.obx = obx_5

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5]

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
    """ Based on live/br/br-alert.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='RIS_RECEIVER')
        msh.receiving_facility = HD(hd_1='PIXEON')
        msh.date_time_of_message = '20250322042000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322042000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_SWF', ei_2='IHE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='STROKE', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032209', cx_4='SR_BA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SR_BA')
        orc.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322043000^^S'
        orc.orc_10 = '20250322042000'
        orc.orc_11 = 'USR304^ARAUJO^MATEUS'
        orc.orc_14 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        orc.orc_19 = 'SR_BA^Hospital Sao Rafael^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SR_BA')
        obr.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT HEAD WO CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250322043000'
        obr.specimen_action_code = 'I63.9^AVC isquemico^I10'
        obr.obr_16 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        obr.obr_26 = '1^^^20250322043000^^S'
        obr.escort_required = '30799-1^CT Head^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Infarto cerebral nao especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'URGENTE - Protocolo AVC. Janela <4.5h. Avaliar trombólise.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/br/br-alert.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='RIS_RECEIVER')
        msh.receiving_facility = HD(hd_1='PIXEON')
        msh.date_time_of_message = '20250322051000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322051000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='STROKE', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032209', cx_4='SR_BA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SR_BA')
        orc.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR304^ARAUJO^MATEUS'
        orc.orc_18 = 'SR_BA^Hospital Sao Rafael^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SR_BA')
        obr.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='CT HEAD WO CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250322043000'
        obr.obr_14 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        obr.placer_field_1 = '20250322050900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='70450', cwe_2='TC CRANIO LAUDO', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'TC DE CRANIO SEM CONTRASTE - URGENCIA'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='70450', cwe_2='TC CRANIO LAUDO', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Ausencia de sangramento intracraniano agudo. Sem desvio de linha media.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='70450', cwe_2='TC CRANIO LAUDO', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Hipodensidade sutil em territorio da arteria cerebral media esquerda (insular e frontal).'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='70450', cwe_2='TC CRANIO LAUDO', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'ASPECTS score: 8. Sem transformacao hemorragica.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='70450', cwe_2='TC CRANIO LAUDO', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='5')
        obx_5.obx_5 = 'CONCLUSAO: Sinais precoces de isquemia em territorio de ACM esquerda. Candidato a trombólise.'
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
    """ Based on live/br/br-alert.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SR')
        msh.date_time_of_message = '20250322054500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250322054500015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250322054500'
        evn.event_occurred = '20250322054000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='STROKE', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025032209', cx_4='SR_BA', cx_5='VN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PROCEDURE', cwe_2='Procedimento Realizado', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Trombólise IV com Alteplase (rt-PA) 0.9mg/kg. Dose total: 63mg.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322054500'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TS'
        obx_2.observation_identifier = CWE(cwe_1='BOLUS_TIME', cwe_2='Hora do Bolus', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '20250322054500'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='DOOR_NEEDLE', cwe_2='Tempo Porta-Agulha', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '52'
        obx_3.units = CWE(cwe_1='min')
        obx_3.reference_range = '<60'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322054500'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='NIHSS_POST', cwe_2='NIHSS Pos-Trombólise', cwe_3='LOCAL')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '8'
        obx_4.reference_range = '0-5'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322054500'

        # .. build the OBSERVATION group ..
        observation_4 = AdtA01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='CLINICAL_NOTE', cwe_2='Evolucao Medica', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Paciente tolerou infusao sem intercorrencias. Melhora parcial de deficit motor D. NIHSS 12->8.'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = AdtA01Observation()
        observation_5.obx = obx_5

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5]

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
    """ Based on live/br/br-alert.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SR')
        msh.date_time_of_message = '20250322060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20250322060000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250322060000'
        evn.event_occurred = '20250322055500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT050505', cx_4='SR_BA', cx_5='MR'), CX(cx_1='857.236.491-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALVES', xpn_2='FRANCISCO', xpn_3='GERALDO')
        pid.date_time_of_birth = '19531122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571983625498'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED08', pl_3='1', pl_6='SR_BA')
        pv1.pv1_7 = '60784^MONTEIRO^EDUARDO^FABIO^^^Dr.^MD'
        pv1.pv1_9 = '80921^TEIXEIRA^SIMONE^CRISTINA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.re_admission_indicator = CWE(cwe_1='TRN')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032209', cwe_4='SR_BA', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SUS')
        pv1.diet_type = CWE(cwe_1='SR_BA')
        pv1.pending_location = PL(pl_1='20250322060000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='I63.9', cwe_2='AVC isquemico - pos trombólise', cwe_3='I10')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/br/br-alert.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='PIX_MGR')
        msh.receiving_facility = HD(hd_1='MPI_SES')
        msh.date_time_of_message = '20250322070000'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22', msg_3='QBP_Q21')
        msh.message_control_id = 'MSG20250322070000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_PDQ', ei_2='IHE')

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7')
        qpd.query_tag = 'QRY2025032200001'
        qpd.qpd_3 = '@PID.5.1^PEREIRA~@PID.7^19880714~@PID.8^F~@PID.11.4^CE'

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='10', cq_2='RD')

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/br/br-alert.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIX_MGR')
        msh.sending_facility = HD(hd_1='MPI_SES')
        msh.receiving_application = HD(hd_1='ALERT_CIS')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.date_time_of_message = '20250322070001'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22', msg_3='RSP_K21')
        msh.message_control_id = 'MSG20250322070001018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_PDQ', ei_2='IHE')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG20250322070000017'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'QRY2025032200001'
        qak.query_response_status = 'OK'
        qak.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7')
        qak.hit_count_total = '3'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7')
        qpd.query_tag = 'QRY2025032200001'
        qpd.qpd_3 = '@PID.5.1^PEREIRA~@PID.7^19880714~@PID.8^F~@PID.11.4^CE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MPI001234', cx_4='MPI_SES', cx_5='PI'),
            CX(cx_1='PAT112233', cx_4='FORT', cx_5='MR'),
            CX(cx_1='624.815.937-44', cx_4='BR', cx_5='CPF'),
        ]
        pid.patient_name = XPN(xpn_1='PEREIRA', xpn_2='ISABELA', xpn_3='CAROLINA')
        pid.date_time_of_birth = '19880714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Beira Mar 1500', xad_3='Fortaleza', xad_4='CE', xad_5='60165-121', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5585991726384'
        pid.pid_33 = ''

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK21QueryResponse()
        query_response.pid = pid

        # .. build PID ..
        pid_2 = PID()
        pid_2.set_id_pid = '2'
        pid_2.patient_identifier_list = [
            CX(cx_1='MPI005678', cx_4='MPI_SES', cx_5='PI'),
            CX(cx_1='PAT445566', cx_4='FORT', cx_5='MR'),
            CX(cx_1='712.946.385-21', cx_4='BR', cx_5='CPF'),
        ]
        pid_2.patient_name = XPN(xpn_1='PEREIRA', xpn_2='MARIANA', xpn_3='TERESA')
        pid_2.date_time_of_birth = '19880318'
        pid_2.administrative_sex = CWE(cwe_1='F')
        pid_2.patient_address = XAD(xad_1='Rua Joao Cordeiro 800', xad_3='Fortaleza', xad_4='CE', xad_5='60110-300', xad_6='BR')
        pid_2.pid_13 = '^PRN^PH^^^^^^^^^5585983726491'
        pid_2.pid_33 = ''

        # .. build PID ..
        pid_3 = PID()
        pid_3.set_id_pid = '3'
        pid_3.patient_identifier_list = [
            CX(cx_1='MPI009012', cx_4='MPI_SES', cx_5='PI'),
            CX(cx_1='PAT778899', cx_4='FORT', cx_5='MR'),
            CX(cx_1='538.271.946-83', cx_4='BR', cx_5='CPF'),
        ]
        pid_3.patient_name = XPN(xpn_1='PEREIRA', xpn_2='AMANDA', xpn_3='LETICIA')
        pid_3.date_time_of_birth = '19880925'
        pid_3.administrative_sex = CWE(cwe_1='F')
        pid_3.patient_address = XAD(xad_1='Av Santos Dumont 3500', xad_3='Fortaleza', xad_4='CE', xad_5='60150-161', xad_6='BR')
        pid_3.pid_13 = '^PRN^PH^^^^^^^^^5585975849263'
        pid_3.pid_33 = ''

        # .. assemble the full message ..
        msg = RSP_K21()
        msg.msh = msh
        msg.msa = msa
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response
        msg.extra_segments = [pid_2, pid_3]

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
    """ Based on live/br/br-alert.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='PIX_MGR')
        msh.receiving_facility = HD(hd_1='MPI_SES')
        msh.date_time_of_message = '20250322140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG20250322140000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_PIX', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250322140000'
        evn.event_occurred = '20250322135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MPI001234', cx_4='MPI_SES', cx_5='PI'),
            CX(cx_1='PAT112233', cx_4='FORT', cx_5='MR'),
            CX(cx_1='624.815.937-44', cx_4='BR', cx_5='CPF'),
        ]
        pid.patient_name = XPN(xpn_1='PEREIRA', xpn_2='ISABELA', xpn_3='CAROLINA')
        pid.date_time_of_birth = '19880714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Beira Mar 1500', xad_3='Fortaleza', xad_4='CE', xad_5='60165-121', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5585991726384'
        pid.pid_33 = ''

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='PAT998877', cx_4='FORT', cx_5='MR'), CX(cx_1='MPI007890', cx_4='MPI_SES', cx_5='PI')]
        mrg.mrg_2 = 'VIS2025010102^^^FORT^VN'

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
    """ Based on live/br/br-alert.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ALERT_CIS')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA_CWB', hd_2='PR')
        msh.receiving_application = HD(hd_1='DOC_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_SC')
        msh.date_time_of_message = '20250323100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250323100000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT040404', cx_4='SC_CWB', cx_5='MR'), CX(cx_1='739.582.461-30', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='REIS', xpn_2='MARCOS', xpn_3='VINICIUS')
        pid.date_time_of_birth = '19821010'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Sete de Setembro 2940', xad_3='Curitiba', xad_4='PR', xad_5='80250-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541986374829'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='BED12', pl_3='1', pl_6='SC_CWB')
        pv1.pv1_7 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'
        pv1.pv1_9 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032104', cx_4='SC_CWB', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032300020', ei_2='SC_CWB')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR305^SOARES^JULIANA'
        orc.orc_18 = 'SC_CWB^Hospital Santa Casa de Curitiba^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032300020', ei_2='SC_CWB')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='LABORATORY REPORT', cwe_3='LN')
        obr.observation_date_time = '20250322160000'
        obr.obr_14 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'
        obr.placer_field_1 = '20250323095900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Evolucao Clinica', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Paciente evoluindo com melhora clinica. Dor abdominal em resolucao. Amilase normalizada.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Evolucao Clinica', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Dieta liquida aceita. Sem febre ha 24h. Programar alta para amanha.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='IMG', cwe_2='Termo de Consentimento Digitalizado', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'ALERT_CIS^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCACAAIADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250323095900'
        obx_3.obx_16 = '50673^FERREIRA^GUSTAVO^EMILIO^^^Dr.^MD'

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

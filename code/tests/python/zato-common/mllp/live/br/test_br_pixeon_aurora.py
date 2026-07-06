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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, IN1, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-pixeon-aurora.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-pixeon-aurora.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='SP')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250314082345'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250314082345001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_IOCM', ei_2='IHE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT834721', cx_4='SIRIO', cx_5='MR'), CX(cx_1='318.475.962-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SAMPAIO', xpn_2='MARCOS', xpn_3='ROBERTO')
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Augusta 1247 Apt 42', xad_2='Consolacao', xad_3='Sao Paulo', xad_4='SP', xad_5='01305-100', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511998765432'
        pid.pid_14 = '^WPN^PH^^^^^^^^^551132145678'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='9876543', cx_4='SIRIO', cx_5='AN')
        pid.pid_32 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT01', pl_3='1', pl_6='SIRIO')
        pv1.pv1_7 = '38456^OLIVEIRA^RICARDO^ALMEIDA^^^Dr.^MD'
        pv1.pv1_9 = '38456^OLIVEIRA^RICARDO^ALMEIDA^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031401', cx_4='SIRIO', cx_5='VN')
        pv1.diet_type = CWE(cwe_1='SIRIO')
        pv1.pending_location = PL(pl_1='20250314080000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_SP')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica Internacional')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SAMPAIO', cwe_2='MARCOS', cwe_3='ROBERTO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19780315')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Augusta 1247', cwe_2='Consolacao', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01305-100', cwe_6='BR')
        in1.policy_number = 'AMI8834562'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031400123', ei_2='SIRIO')
        orc.filler_order_number = EI(ei_1='FIL2025031400123', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250314083000^^R'
        orc.orc_10 = '20250314082345'
        orc.orc_11 = 'USR001^SOUZA^MARIANA^^^Tec.'
        orc.enterers_location = PL(pl_1='38456', pl_2='OLIVEIRA', pl_3='RICARDO', pl_4='ALMEIDA', pl_7='Dr.', pl_8='MD')
        orc.orc_18 = 'SIRIO^Hospital Sirio Libanes^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031400123', ei_2='SIRIO')
        obr.filler_order_number = EI(ei_1='FIL2025031400123', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250314083000'
        obr.obr_15 = '38456^OLIVEIRA^RICARDO^ALMEIDA^^^Dr.^MD'
        obr.result_status = '1^^^20250314083000^^R'
        obr.transport_arranged = '24727-0^CT Chest^LN'

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
    """ Based on live/br/br-pixeon-aurora.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_ALBERT_EINSTEIN', hd_2='SP')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250314093012'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250314093012002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_IOCM', ei_2='IHE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT112983', cx_4='EINSTEIN', cx_5='MR'), CX(cx_1='782.395.146-78', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='FERREIRA', xpn_2='ANA', xpn_3='CAROLINA', xpn_4='SOUZA')
        pid.date_time_of_birth = '19850522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av Paulista 1578 Sala 301', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01310-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511976543210'
        pid.pid_14 = '^WPN^PH^^^^^^^^^551130456789'
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='1123456', cx_4='EINSTEIN', cx_5='AN')
        pid.pid_32 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MR01', pl_3='1', pl_6='EINSTEIN')
        pv1.pv1_7 = '45123^MENDES^PATRICIA^LOPES^^^Dra.^MD'
        pv1.pv1_9 = '45123^MENDES^PATRICIA^LOPES^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031402', cx_4='EINSTEIN', cx_5='VN')
        pv1.diet_type = CWE(cwe_1='EINSTEIN')
        pv1.pending_location = PL(pl_1='20250314090000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_SP')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude SA')
        in1.plan_effective_date = '20240301'
        in1.plan_expiration_date = '20260228'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='FERREIRA', cwe_2='ANA', cwe_3='CAROLINA', cwe_4='SOUZA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19850522')
        in1.assignment_of_benefits = CWE(cwe_1='Av Paulista 1578', cwe_2='Bela Vista', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01310-200', cwe_6='BR')
        in1.policy_number = 'BRD4456123'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031400456', ei_2='EINSTEIN')
        orc.filler_order_number = EI(ei_1='FIL2025031400456', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250314100000^^R'
        orc.orc_10 = '20250314093012'
        orc.orc_11 = 'USR002^LIMA^PEDRO^^^Tec.'
        orc.enterers_location = PL(pl_1='45123', pl_2='MENDES', pl_3='PATRICIA', pl_4='LOPES', pl_7='Dra.', pl_8='MD')
        orc.orc_18 = 'EINSTEIN^Hospital Albert Einstein^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031400456', ei_2='EINSTEIN')
        obr.filler_order_number = EI(ei_1='FIL2025031400456', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI BRAIN W AND WO CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250314100000'
        obr.specimen_action_code = 'R50.9^Febre de origem desconhecida^I10'
        obr.obr_16 = '45123^MENDES^PATRICIA^LOPES^^^Dra.^MD'
        obr.obr_26 = '1^^^20250314100000^^R'
        obr.escort_required = '24590-2^MRI Brain^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R51', cwe_2='Cefaleia', cwe_3='I10')
        dg1.diagnosis_date_time = '20250313'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_DELBONI', hd_2='SP')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_DELBONI')
        msh.date_time_of_message = '20250314112530'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250314112530003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT556789', cx_4='DELBONI', cx_5='MR'), CX(cx_1='628.193.475-09', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MAGALHAES', xpn_2='JOAO', xpn_3='PEDRO')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Tutoia 540', xad_2='Vila Mariana', xad_3='Sao Paulo', xad_4='SP', xad_5='04007-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511987654321'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT02', pl_3='1', pl_6='DELBONI')
        pv1.pv1_7 = '52341^RIBEIRO^CARLOS^EDUARDO^^^Dr.^MD'
        pv1.pv1_9 = '52341^RIBEIRO^CARLOS^EDUARDO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031403', cx_4='DELBONI', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031400789', ei_2='DELBONI')
        orc.filler_order_number = EI(ei_1='FIL2025031400789', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_8 = '1^^^20250314090000^^R'
        orc.orc_10 = '20250314112530'
        orc.orc_11 = 'USR003^ALVES^RENATA'
        orc.orc_18 = 'DELBONI^Clinica Delboni Auriemo^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031400789', ei_2='DELBONI')
        obr.filler_order_number = EI(ei_1='FIL2025031400789', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250314090000'
        obr.obr_14 = '52341^RIBEIRO^CARLOS^EDUARDO^^^Dr.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250314112500'
        obr.filler_field_2 = 'F'
        obr.obr_23 = '1^^^20250314090000^^R'
        obr.reason_for_study = CWE(cwe_1='52341', cwe_2='RIBEIRO', cwe_3='CARLOS', cwe_4='EDUARDO', cwe_7='Dr.', cwe_8='MD')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'TOMOGRAFIA COMPUTADORIZADA DE TORAX COM CONTRASTE'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250314112500'
        obx.obx_16 = '52341^RIBEIRO^CARLOS^EDUARDO^^^Dr.^MD'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Pulmoes com transparencia preservada. Ausencia de nodulos ou massas.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST REPORT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Mediastino sem linfonodomegalias. Traqueia e bronquios fontes permeaveis.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'Coracao de dimensoes normais. Aorta toracica sem ectasias.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST REPORT', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='5')
        obx_5.obx_5 = 'CONCLUSAO: Exame tomografico do torax sem alteracoes significativas.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_BENEFICENCIA', hd_2='RJ')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_BENEF')
        msh.date_time_of_message = '20250315084512'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250315084512004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT223344', cx_4='BENEF', cx_5='MR'), CX(cx_1='739.184.526-12', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SOARES', xpn_2='MARIA', xpn_3='APARECIDA')
        pid.date_time_of_birth = '19720418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua General Severiano 159', xad_2='Botafogo', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22290-040', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521998761234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US01', pl_3='1', pl_6='BENEF')
        pv1.pv1_7 = '61234^NASCIMENTO^FERNANDA^MARIA^^^Dra.^MD'
        pv1.pv1_9 = '61234^NASCIMENTO^FERNANDA^MARIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025031504', cx_4='BENEF', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031500234', ei_2='BENEF')
        orc.filler_order_number = EI(ei_1='FIL2025031500234', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_8 = '1^^^20250315070000^^R'
        orc.orc_10 = '20250315084512'
        orc.orc_11 = 'USR004^GOMES^THIAGO'
        orc.orc_18 = 'BENEF^Hospital Beneficencia Portuguesa do Rio^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031500234', ei_2='BENEF')
        obr.filler_order_number = EI(ei_1='FIL2025031500234', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='76856', cwe_2='US PELVIS COMPLETE', cwe_3='CPT4')
        obr.observation_date_time = '20250315070000'
        obr.obr_14 = '61234^NASCIMENTO^FERNANDA^MARIA^^^Dra.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250315084500'
        obr.filler_field_2 = 'F'
        obr.obr_23 = '1^^^20250315070000^^R'
        obr.reason_for_study = CWE(cwe_1='61234', cwe_2='NASCIMENTO', cwe_3='FERNANDA', cwe_4='MARIA', cwe_7='Dra.', cwe_8='MD')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76856', cwe_2='ULTRASOUND REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'ULTRASSONOGRAFIA PELVICA - Utero em anteversoflexao de contornos regulares.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='76856', cwe_2='ULTRASOUND REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Miometrio homogeneo. Endometrio linear medindo 5mm. Ovarios de aspecto habitual.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo Completo US Pelvica', cwe_3='AUSPDI')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'PIXEON^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjA5CiUlRU9GCg=='
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250315084500'
        obx_3.obx_16 = '61234^NASCIMENTO^FERNANDA^MARIA^^^Dra.^MD'

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
    """ Based on live/br/br-pixeon-aurora.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_FEMME', hd_2='MG')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250315101500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250315101500005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT667788', cx_4='FEMME', cx_5='MR'), CX(cx_1='841.295.367-23', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='LUCIANA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19680912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Aimores 2530', xad_2='Lourdes', xad_3='Belo Horizonte', xad_4='MG', xad_5='30140-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531965432109'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MG01', pl_3='1', pl_6='FEMME')
        pv1.pv1_7 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        pv1.pv1_9 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031505', cx_4='FEMME', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_MG')
        in1.insurance_company_name = XON(xon_1='Unimed Belo Horizonte')
        in1.plan_effective_date = '20230601'
        in1.plan_expiration_date = '20260531'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='PRADO', cwe_2='LUCIANA', cwe_3='CRISTINA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19680912')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Aimores 2530', cwe_2='Lourdes', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='30140-070', cwe_6='BR')
        in1.policy_number = 'UNI7789012'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031500567', ei_2='FEMME')
        orc.filler_order_number = EI(ei_1='FIL2025031500567', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250315110000^^R'
        orc.orc_10 = '20250315101500'
        orc.orc_11 = 'USR005^ROCHA^CAMILA'
        orc.orc_14 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        orc.orc_19 = 'FEMME^Clinica Femme^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031500567', ei_2='FEMME')
        obr.filler_order_number = EI(ei_1='FIL2025031500567', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='MAMMOGRAPHY BILATERAL SCREENING', cwe_3='CPT4')
        obr.observation_date_time = '20250315110000'
        obr.specimen_action_code = 'Z12.31^Rastreamento de neoplasia maligna de mama^I10'
        obr.obr_16 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        obr.obr_26 = '1^^^20250315110000^^R'
        obr.escort_required = '24606-6^Mammography^LN'

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
    """ Based on live/br/br-pixeon-aurora.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_FEMME', hd_2='MG')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_FEMME')
        msh.date_time_of_message = '20250315143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250315143000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT667788', cx_4='FEMME', cx_5='MR'), CX(cx_1='841.295.367-23', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='LUCIANA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19680912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Aimores 2530', xad_2='Lourdes', xad_3='Belo Horizonte', xad_4='MG', xad_5='30140-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531965432109'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MG01', pl_3='1', pl_6='FEMME')
        pv1.pv1_7 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        pv1.pv1_9 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031505', cx_4='FEMME', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031500567', ei_2='FEMME')
        orc.filler_order_number = EI(ei_1='FIL2025031500567', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR005^ROCHA^CAMILA'
        orc.orc_18 = 'FEMME^Clinica Femme^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031500567', ei_2='FEMME')
        obr.filler_order_number = EI(ei_1='FIL2025031500567', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='MAMMOGRAPHY BILATERAL SCREENING', cwe_3='CPT4')
        obr.observation_date_time = '20250315110000'
        obr.obr_14 = '71234^CAMPOS^JULIANA^SANTOS^^^Dra.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250315142900'
        obr.filler_field_2 = 'F'
        obr.reason_for_study = CWE(cwe_1='71234', cwe_2='CAMPOS', cwe_3='JULIANA', cwe_4='SANTOS', cwe_7='Dra.', cwe_8='MD')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='77067', cwe_2='MAMOGRAFIA BILATERAL', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'MAMOGRAFIA DIGITAL BILATERAL - Mamas de composicao predominantemente densa (ACR D).'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='77067', cwe_2='MAMOGRAFIA BILATERAL', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Nao se observam nodulos, distorcoes arquiteturais ou microcalcificacoes suspeitas.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='77067', cwe_2='MAMOGRAFIA BILATERAL', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Regioes axilares sem linfonodomegalias.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='36625-2', cwe_2='BI-RADS ASSESSMENT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'BI-RADS 1^Negativo^ACR_BIRADS'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='77067', cwe_2='MAMOGRAFIA BILATERAL', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='4')
        obx_5.obx_5 = 'CONCLUSAO: Mamografia sem evidencias de malignidade. BI-RADS 1. Controle anual.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250316020145'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250316020145007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT998877', cx_4='SAO_RAFAEL', cx_5='MR'), CX(cx_1='952.816.473-45', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SANTANA', xpn_2='CARLOS', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19900705'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_2='Caminho das Arvores', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571954321098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED03', pl_3='1', pl_6='SAO_RAFAEL')
        pv1.pv1_7 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        pv1.pv1_9 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025031607', cx_4='SAO_RAFAEL', cx_5='VN')
        pv1.diet_type = CWE(cwe_1='SAO_RAFAEL')
        pv1.pending_location = PL(pl_1='20250316015500')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_BA')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SANTANA', cwe_2='CARLOS', cwe_3='HENRIQUE')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19900705')
        in1.assignment_of_benefits = CWE(
            cwe_1='Av Tancredo Neves 2782',
            cwe_2='Caminho das Arvores',
            cwe_3='Salvador',
            cwe_4='BA',
            cwe_5='41820-021',
            cwe_6='BR',
        )
        in1.policy_number = 'SUS198765432'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031600890', ei_2='SAO_RAFAEL')
        orc.filler_order_number = EI(ei_1='FIL2025031600890', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250316022000^^S'
        orc.orc_10 = '20250316020145'
        orc.orc_11 = 'USR006^DIAS^FELIPE'
        orc.orc_14 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        orc.orc_19 = 'SAO_RAFAEL^Hospital Sao Rafael^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031600890', ei_2='SAO_RAFAEL')
        obr.filler_order_number = EI(ei_1='FIL2025031600890', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY 2 VIEWS', cwe_3='CPT4')
        obr.observation_date_time = '20250316022000'
        obr.specimen_action_code = 'S44.0^Fratura de clavicula^I10'
        obr.obr_16 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        obr.obr_26 = '1^^^20250316022000^^S'
        obr.escort_required = '24642-1^Chest XRay^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S44.0', cwe_2='Fratura de clavicula', cwe_3='I10')
        dg1.diagnosis_date_time = '20250316'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='BA')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_SAO_RAFAEL')
        msh.date_time_of_message = '20250316031200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250316031200008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT998877', cx_4='SAO_RAFAEL', cx_5='MR'), CX(cx_1='952.816.473-45', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SANTANA', xpn_2='CARLOS', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19900705'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Tancredo Neves 2782', xad_2='Caminho das Arvores', xad_3='Salvador', xad_4='BA', xad_5='41820-021', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571954321098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='BED03', pl_3='1', pl_6='SAO_RAFAEL')
        pv1.pv1_7 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        pv1.pv1_9 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ER')
        pv1.patient_type = CWE(cwe_1='E')
        pv1.visit_number = CX(cx_1='VIS2025031607', cx_4='SAO_RAFAEL', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031600890', ei_2='SAO_RAFAEL')
        orc.filler_order_number = EI(ei_1='FIL2025031600890', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR006^DIAS^FELIPE'
        orc.orc_18 = 'SAO_RAFAEL^Hospital Sao Rafael^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031600890', ei_2='SAO_RAFAEL')
        obr.filler_order_number = EI(ei_1='FIL2025031600890', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY 2 VIEWS', cwe_3='CPT4')
        obr.observation_date_time = '20250316022000'
        obr.obr_14 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'
        obr.placer_field_1 = '20250316031100'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '82345^ANDRADE^MARCOS^VINICIUS^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'RADIOGRAFIA DE TORAX EM PA E PERFIL'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Fratura deslocada de terco medio da clavicula esquerda. Campos pulmonares limpos.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY REPORT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Area cardiaca dentro dos limites da normalidade. Seios costofrenicos livres.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='71046', cwe_2='CHEST XRAY REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'CONCLUSAO: Fratura de clavicula esquerda confirmada. Sem achados pulmonares adicionais.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_MUNICIPAL_BH', hd_2='MG')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250316091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250316091500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT445566', cx_4='HM_BH', cx_5='MR'), CX(cx_1='063.527.918-56', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='DRUMOND', xpn_2='JOSE', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19550210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua da Bahia 1200', xad_2='Centro', xad_3='Belo Horizonte', xad_4='MG', xad_5='30160-011', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531987654312'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US02', pl_3='1', pl_6='HM_BH')
        pv1.pv1_7 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031609', cx_4='HM_BH', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_MG')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude - MG')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='DRUMOND', cwe_2='JOSE', cwe_3='ANTONIO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19550210')
        in1.assignment_of_benefits = CWE(cwe_1='Rua da Bahia 1200', cwe_2='Centro', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='30160-011', cwe_6='BR')
        in1.policy_number = 'SUS298765432'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031600101', ei_2='HM_BH')
        orc.filler_order_number = EI(ei_1='FIL2025031600101', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250316100000^^R'
        orc.orc_10 = '20250316091500'
        orc.orc_11 = 'USR007^SANTOS^LARISSA'
        orc.orc_14 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        orc.orc_19 = 'HM_BH^Hospital Municipal de Belo Horizonte^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031600101', ei_2='HM_BH')
        obr.filler_order_number = EI(ei_1='FIL2025031600101', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN COMPLETE', cwe_3='CPT4')
        obr.observation_date_time = '20250316100000'
        obr.specimen_action_code = 'K80.2^Calculo de vesicula biliar^I10'
        obr.obr_16 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        obr.obr_26 = '1^^^20250316100000^^R'
        obr.escort_required = '24558-9^US Abdomen^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Calculo de vesicula biliar sem colecistite', cwe_3='I10')
        dg1.diagnosis_date_time = '20250315'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_MUNICIPAL_BH', hd_2='MG')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_HM_BH')
        msh.date_time_of_message = '20250316112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250316112000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT445566', cx_4='HM_BH', cx_5='MR'), CX(cx_1='063.527.918-56', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='DRUMOND', xpn_2='JOSE', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19550210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua da Bahia 1200', xad_2='Centro', xad_3='Belo Horizonte', xad_4='MG', xad_5='30160-011', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531987654312'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US02', pl_3='1', pl_6='HM_BH')
        pv1.pv1_7 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031609', cx_4='HM_BH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031600101', ei_2='HM_BH')
        orc.filler_order_number = EI(ei_1='FIL2025031600101', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR007^SANTOS^LARISSA'
        orc.orc_18 = 'HM_BH^Hospital Municipal de Belo Horizonte^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031600101', ei_2='HM_BH')
        obr.filler_order_number = EI(ei_1='FIL2025031600101', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN COMPLETE', cwe_3='CPT4')
        obr.observation_date_time = '20250316100000'
        obr.obr_14 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250316111900'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'ULTRASSONOGRAFIA DE ABDOMEN TOTAL - Figado de dimensoes normais e ecotextura homogenea.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Vesicula biliar com calculo unico de 12mm com sombra acustica posterior.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN REPORT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Vias biliares nao dilatadas. Pancreas, baco e rins sem alteracoes.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'CONCLUSAO: Colelitiase. Encaminhamento cirurgico recomendado.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='IMG', cwe_2='Imagem US Vesicula', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'PIXEON^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAIQAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            '9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACR0ZXh0AAAAAENvcHlyaWdodCAoYykgMTk5OCBIZXds'
            'ZXR0LVBhY2thcmQgQ29tcGFueQAAZGVzYwAAAAAAAAASc1JHQiBJRUM2MTk2Ni0yLjE'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250316111900'
        obx_5.obx_16 = '93456^MARTINS^RAFAEL^AUGUSTO^^^Dr.^MD'

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
    """ Based on live/br/br-pixeon-aurora.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_AC_CAMARGO', hd_2='SP')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250317080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250317080000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT778899', cx_4='AC_CAMARGO', cx_5='MR'), CX(cx_1='174.638.295-67', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALMEIDA', xpn_2='ROBERTO', xpn_3='CARLOS')
        pid.date_time_of_birth = '19600125'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Brigadeiro Faria Lima 3900', xad_2='Itaim Bibi', xad_3='Sao Paulo', xad_4='SP', xad_5='04538-132', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210987'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='PET01', pl_3='1', pl_6='AC_CAMARGO')
        pv1.pv1_7 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031711', cx_4='AC_CAMARGO', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_4='SULAMERICA')
        in1.insurance_company_id = CX(cx_1='SULAM_SP')
        in1.insurance_company_name = XON(xon_1='SulAmerica Saude SA')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='ALMEIDA', cwe_2='ROBERTO', cwe_3='CARLOS')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19600125')
        in1.assignment_of_benefits = CWE(
            cwe_1='Av Brigadeiro Faria Lima 3900',
            cwe_2='Itaim Bibi',
            cwe_3='Sao Paulo',
            cwe_4='SP',
            cwe_5='04538-132',
            cwe_6='BR',
        )
        in1.policy_number = 'SUL5567890'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031700345', ei_2='AC_CAMARGO')
        orc.filler_order_number = EI(ei_1='FIL2025031700345', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250317090000^^R'
        orc.orc_10 = '20250317080000'
        orc.orc_11 = 'USR008^XAVIER^BEATRIZ'
        orc.orc_14 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        orc.orc_19 = 'AC_CAMARGO^Hospital AC Camargo Cancer Center^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031700345', ei_2='AC_CAMARGO')
        obr.filler_order_number = EI(ei_1='FIL2025031700345', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET CT WHOLE BODY', cwe_3='CPT4')
        obr.observation_date_time = '20250317090000'
        obr.specimen_action_code = 'C34.1^Neoplasia maligna de lobo superior pulmao^I10'
        obr.obr_16 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        obr.obr_26 = '1^^^20250317090000^^R'
        obr.escort_required = '44136-0^PET CT^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.1', cwe_2='Neoplasia maligna do lobo superior, bronquio ou pulmao', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_AC_CAMARGO', hd_2='SP')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_AC_CAMARGO')
        msh.date_time_of_message = '20250317143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250317143000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT778899', cx_4='AC_CAMARGO', cx_5='MR'), CX(cx_1='174.638.295-67', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ALMEIDA', xpn_2='ROBERTO', xpn_3='CARLOS')
        pid.date_time_of_birth = '19600125'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Brigadeiro Faria Lima 3900', xad_2='Itaim Bibi', xad_3='Sao Paulo', xad_4='SP', xad_5='04538-132', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210987'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='PET01', pl_3='1', pl_6='AC_CAMARGO')
        pv1.pv1_7 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031711', cx_4='AC_CAMARGO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031700345', ei_2='AC_CAMARGO')
        orc.filler_order_number = EI(ei_1='FIL2025031700345', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR008^XAVIER^BEATRIZ'
        orc.orc_18 = 'AC_CAMARGO^Hospital AC Camargo Cancer Center^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031700345', ei_2='AC_CAMARGO')
        obr.filler_order_number = EI(ei_1='FIL2025031700345', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET CT WHOLE BODY', cwe_3='CPT4')
        obr.observation_date_time = '20250317090000'
        obr.obr_14 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250317142800'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '10567^TAKAHASHI^KENJI^AUGUSTO^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='78816', cwe_2='PET CT REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'PET/CT COM 18F-FDG DE CORPO INTEIRO'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='78816', cwe_2='PET CT REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Lesao hipermetabolica em lobo superior direito medindo 3.2x2.8cm com SUVmax 12.4.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='78816', cwe_2='PET CT REPORT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Linfonodo mediastinal paratraqueal direito de 1.5cm com SUVmax 5.2.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='78816', cwe_2='PET CT REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'Demais orgaos e estruturas sem captacao anomala do radiofarmaco.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='78816', cwe_2='PET CT REPORT', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='5')
        obx_5.obx_5 = 'CONCLUSAO: Lesao pulmonar hipermetabolica com linfonodo mediastinal suspeito. Estadiamento T2aN2M0.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_COPA_DOR', hd_2='RJ')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250317155000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250317155000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT334455', cx_4='COPA_DOR', cx_5='MR'), CX(cx_1='285.347.961-78', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BARBOSA', xpn_2='PATRICIA', xpn_3='HELENA')
        pid.date_time_of_birth = '19830619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Figueiredo Magalhaes 875', xad_2='Copacabana', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22031-011', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521976541230'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MR02', pl_3='1', pl_6='COPA_DOR')
        pv1.pv1_7 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        pv1.pv1_9 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031713', cx_4='COPA_DOR', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_RJ')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240601'
        in1.plan_expiration_date = '20260531'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='BARBOSA', cwe_2='PATRICIA', cwe_3='HELENA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19830619')
        in1.assignment_of_benefits = CWE(
            cwe_1='Rua Figueiredo Magalhaes 875',
            cwe_2='Copacabana',
            cwe_3='Rio de Janeiro',
            cwe_4='RJ',
            cwe_5='22031-011',
            cwe_6='BR',
        )
        in1.policy_number = 'AMI9912345'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031700678', ei_2='COPA_DOR')
        orc.filler_order_number = EI(ei_1='FIL2025031700678', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250318080000^^R'
        orc.orc_10 = '20250317155000'
        orc.orc_11 = 'USR009^MOREIRA^VANESSA'
        orc.orc_14 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        orc.orc_19 = 'COPA_DOR^Hospital Copa DOr^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031700678', ei_2='COPA_DOR')
        obr.filler_order_number = EI(ei_1='FIL2025031700678', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='75561', cwe_2='CARDIAC MRI W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250318080000'
        obr.specimen_action_code = 'I42.0^Cardiomiopatia dilatada^I10'
        obr.obr_16 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        obr.obr_26 = '1^^^20250318080000^^R'
        obr.escort_required = '24855-8^Cardiac MRI^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I42.0', cwe_2='Cardiomiopatia dilatada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250315'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_COPA_DOR', hd_2='RJ')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_COPA_DOR')
        msh.date_time_of_message = '20250318112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250318112000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT334455', cx_4='COPA_DOR', cx_5='MR'), CX(cx_1='285.347.961-78', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BARBOSA', xpn_2='PATRICIA', xpn_3='HELENA')
        pid.date_time_of_birth = '19830619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Figueiredo Magalhaes 875', xad_2='Copacabana', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22031-011', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521976541230'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MR02', pl_3='1', pl_6='COPA_DOR')
        pv1.pv1_7 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        pv1.pv1_9 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031713', cx_4='COPA_DOR', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031700678', ei_2='COPA_DOR')
        orc.filler_order_number = EI(ei_1='FIL2025031700678', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR009^MOREIRA^VANESSA'
        orc.orc_18 = 'COPA_DOR^Hospital Copa DOr^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031700678', ei_2='COPA_DOR')
        obr.filler_order_number = EI(ei_1='FIL2025031700678', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='75561', cwe_2='CARDIAC MRI W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250318080000'
        obr.obr_14 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'
        obr.obr_16 = 'DICOM^1.2.840.10008'
        obr.placer_field_1 = '20250318111900'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '20456^LEMOS^GUSTAVO^HENRIQUE^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='75561', cwe_2='CARDIAC MRI REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'RESSONANCIA MAGNETICA CARDIACA COM CONTRASTE'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10230-1', cwe_2='LVEF', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '38'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '55-70'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='10231-9', cwe_2='LVEDV', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '245'
        obx_3.units = CWE(cwe_1='mL')
        obx_3.reference_range = '56-155'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='75561', cwe_2='CARDIAC MRI REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='2')
        obx_4.obx_5 = 'Ventriculo esquerdo dilatado com hipocinesia difusa. Realce tardio mesocardico em parede lateral.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='75561', cwe_2='CARDIAC MRI REPORT', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='3')
        obx_5.obx_5 = 'CONCLUSAO: Cardiomiopatia dilatada com FEVE reduzida (38%). Padrao de realce nao isquemico.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_FLEURY', hd_2='DF')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250318140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250318140000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT112233', cx_4='FLEURY', cx_5='MR'), CX(cx_1='396.481.527-89', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CARVALHO', xpn_2='HELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19520814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='SHIS QI 17 Bloco F', xad_2='Lago Sul', xad_3='Brasilia', xad_4='DF', xad_5='71645-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5561932109876'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='DXA01', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        pv1.pv1_9 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031815', cx_4='FLEURY', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_DF')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude SA')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='CARVALHO', cwe_2='HELENA', cwe_3='MARIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19520814')
        in1.assignment_of_benefits = CWE(cwe_1='SHIS QI 17 Bloco F', cwe_2='Lago Sul', cwe_3='Brasilia', cwe_4='DF', cwe_5='71645-200', cwe_6='BR')
        in1.policy_number = 'BRD8876543'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031800123', ei_2='FLEURY')
        orc.filler_order_number = EI(ei_1='FIL2025031800123', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250318150000^^R'
        orc.orc_10 = '20250318140000'
        orc.orc_11 = 'USR010^PRADO^LUCAS'
        orc.orc_14 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        orc.orc_19 = 'FLEURY^Laboratorio Fleury^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031800123', ei_2='FLEURY')
        obr.filler_order_number = EI(ei_1='FIL2025031800123', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DEXA BONE DENSITY', cwe_3='CPT4')
        obr.observation_date_time = '20250318150000'
        obr.specimen_action_code = 'M81.0^Osteoporose pos-menopausa^I10'
        obr.obr_16 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        obr.obr_26 = '1^^^20250318150000^^R'
        obr.escort_required = '46278-8^DXA Bone Density^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M81.0', cwe_2='Osteoporose pos-menopausa com fratura patologica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_FLEURY', hd_2='DF')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_FLEURY')
        msh.date_time_of_message = '20250318162000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250318162000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT112233', cx_4='FLEURY', cx_5='MR'), CX(cx_1='396.481.527-89', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CARVALHO', xpn_2='HELENA', xpn_3='MARIA')
        pid.date_time_of_birth = '19520814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='SHIS QI 17 Bloco F', xad_2='Lago Sul', xad_3='Brasilia', xad_4='DF', xad_5='71645-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5561932109876'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='DXA01', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        pv1.pv1_9 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031815', cx_4='FLEURY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031800123', ei_2='FLEURY')
        orc.filler_order_number = EI(ei_1='FIL2025031800123', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR010^PRADO^LUCAS'
        orc.orc_18 = 'FLEURY^Laboratorio Fleury^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031800123', ei_2='FLEURY')
        obr.filler_order_number = EI(ei_1='FIL2025031800123', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DEXA BONE DENSITY', cwe_3='CPT4')
        obr.observation_date_time = '20250318150000'
        obr.obr_14 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'
        obr.placer_field_1 = '20250318161900'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '30789^DUARTE^SANDRA^LUCIA^^^Dra.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='77080', cwe_2='DENSITOMETRIA OSSEA', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'DENSITOMETRIA OSSEA POR ABSORCIOMETRIA DE RAIOS-X DE DUPLA ENERGIA (DXA)'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='46278-8', cwe_2='COLUNA LOMBAR T-SCORE', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '-2.8'
        obx_2.units = CWE(cwe_1='T-score')
        obx_2.reference_range = '-1.0 to 1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='46278-8', cwe_2='COLO FEMORAL T-SCORE', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = '-2.3'
        obx_3.units = CWE(cwe_1='T-score')
        obx_3.reference_range = '-1.0 to 1.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='46278-8', cwe_2='FEMUR TOTAL T-SCORE', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='3')
        obx_4.obx_5 = '-1.9'
        obx_4.units = CWE(cwe_1='T-score')
        obx_4.reference_range = '-1.0 to 1.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='77080', cwe_2='DENSITOMETRIA OSSEA', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='2')
        obx_5.obx_5 = 'CONCLUSAO: Osteoporose em coluna lombar (T-score -2.8) e colo femoral (T-score -2.3). Osteopenia em femur total.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_MAE_DE_DEUS', hd_2='RS')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250319083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250319083000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT556677', cx_4='MAE_DE_DEUS', cx_5='MR'), CX(cx_1='507.612.348-90', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOURA', xpn_2='ANTONIO', xpn_3='CARLOS')
        pid.date_time_of_birth = '19700301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Ipiranga 6681', xad_2='Partenon', xad_3='Porto Alegre', xad_4='RS', xad_5='90619-900', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987651234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US03', pl_3='1', pl_6='MAE_DE_DEUS')
        pv1.pv1_7 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        pv1.pv1_9 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='VAS')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031917', cx_4='MAE_DE_DEUS', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_RS')
        in1.insurance_company_name = XON(xon_1='Unimed Porto Alegre')
        in1.plan_effective_date = '20240301'
        in1.plan_expiration_date = '20260228'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MOURA', cwe_2='ANTONIO', cwe_3='CARLOS')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19700301')
        in1.assignment_of_benefits = CWE(cwe_1='Av Ipiranga 6681', cwe_2='Partenon', cwe_3='Porto Alegre', cwe_4='RS', cwe_5='90619-900', cwe_6='BR')
        in1.policy_number = 'UNI3345678'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031900456', ei_2='MAE_DE_DEUS')
        orc.filler_order_number = EI(ei_1='FIL2025031900456', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250319093000^^R'
        orc.orc_10 = '20250319083000'
        orc.orc_11 = 'USR011^FERRAZ^JULIANA'
        orc.orc_14 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        orc.orc_19 = 'MAE_DE_DEUS^Hospital Mae de Deus^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031900456', ei_2='MAE_DE_DEUS')
        obr.filler_order_number = EI(ei_1='FIL2025031900456', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER US LOWER EXTREMITY', cwe_3='CPT4')
        obr.observation_date_time = '20250319093000'
        obr.specimen_action_code = 'I73.9^Doenca vascular periferica^I10'
        obr.obr_16 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        obr.obr_26 = '1^^^20250319093000^^R'
        obr.escort_required = '24725-4^US Doppler Lower Ext^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I73.9', cwe_2='Doenca vascular periferica nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='HOSP_MAE_DE_DEUS', hd_2='RS')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_MAE_DE_DEUS')
        msh.date_time_of_message = '20250319111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250319111500018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT556677', cx_4='MAE_DE_DEUS', cx_5='MR'), CX(cx_1='507.612.348-90', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOURA', xpn_2='ANTONIO', xpn_3='CARLOS')
        pid.date_time_of_birth = '19700301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Ipiranga 6681', xad_2='Partenon', xad_3='Porto Alegre', xad_4='RS', xad_5='90619-900', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551987651234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US03', pl_3='1', pl_6='MAE_DE_DEUS')
        pv1.pv1_7 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        pv1.pv1_9 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='VAS')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031917', cx_4='MAE_DE_DEUS', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031900456', ei_2='MAE_DE_DEUS')
        orc.filler_order_number = EI(ei_1='FIL2025031900456', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR011^FERRAZ^JULIANA'
        orc.orc_18 = 'MAE_DE_DEUS^Hospital Mae de Deus^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031900456', ei_2='MAE_DE_DEUS')
        obr.filler_order_number = EI(ei_1='FIL2025031900456', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER US LOWER EXTREMITY', cwe_3='CPT4')
        obr.observation_date_time = '20250319093000'
        obr.obr_14 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'
        obr.placer_field_1 = '20250319111400'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '40123^WEBER^HANS^FREDERICO^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER REPORT', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'DOPPLER VENOSO DE MEMBROS INFERIORES'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER REPORT', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Veias femorais comuns, superficiais e profundas pervias bilateralmente com fluxo fasico.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER REPORT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Veias popliteas e tibiais com compressibilidade preservada.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER REPORT', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'Sem evidencias de trombose venosa profunda nos segmentos avaliados.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='93925', cwe_2='DOPPLER REPORT', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='5')
        obx_5.obx_5 = 'CONCLUSAO: Estudo Doppler venoso de membros inferiores sem alteracoes. Ausencia de TVP.'
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_ODONTO_PREV', hd_2='PR')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='PIXEON_PACS')
        msh.date_time_of_message = '20250319141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250319141500019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT889900', cx_4='ODONTO_PREV', cx_5='MR'), CX(cx_1='618.749.025-43', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BERNARDES', xpn_2='JULIANA', xpn_3='FERNANDA')
        pid.date_time_of_birth = '19950410'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua XV de Novembro 1234', xad_2='Centro', xad_3='Curitiba', xad_4='PR', xad_5='80060-000', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541965432101'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='PAN01', pl_3='1', pl_6='ODONTO_PREV')
        pv1.pv1_7 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        pv1.pv1_9 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        pv1.hospital_service = CWE(cwe_1='DEN')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031919', cx_4='ODONTO_PREV', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL_DENTAL')
        in1.insurance_company_id = CX(cx_1='AMIL_PR')
        in1.insurance_company_name = XON(xon_1='Amil Dental')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='BERNARDES', cwe_2='JULIANA', cwe_3='FERNANDA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19950410')
        in1.assignment_of_benefits = CWE(cwe_1='Rua XV de Novembro 1234', cwe_2='Centro', cwe_3='Curitiba', cwe_4='PR', cwe_5='80060-000', cwe_6='BR')
        in1.policy_number = 'AMD1234567'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD2025031900789', ei_2='ODONTO_PREV')
        orc.filler_order_number = EI(ei_1='FIL2025031900789', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250319150000^^R'
        orc.orc_10 = '20250319141500'
        orc.orc_11 = 'USR012^COSTA^AMANDA'
        orc.orc_14 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        orc.orc_19 = 'ODONTO_PREV^Clinica OdontoPrev Curitiba^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031900789', ei_2='ODONTO_PREV')
        obr.filler_order_number = EI(ei_1='FIL2025031900789', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='70355', cwe_2='PANORAMIC XRAY DENTAL', cwe_3='CPT4')
        obr.observation_date_time = '20250319150000'
        obr.specimen_action_code = 'K01.0^Dentes inclusos^I10'
        obr.obr_16 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        obr.obr_26 = '1^^^20250319150000^^R'
        obr.escort_required = '24604-1^XR Panoramic^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K01.0', cwe_2='Dentes inclusos e impactados', cwe_3='I10')
        dg1.diagnosis_date_time = '20250319'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/br/br-pixeon-aurora.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIXEON')
        msh.sending_facility = HD(hd_1='CLINICA_ODONTO_PREV', hd_2='PR')
        msh.receiving_application = HD(hd_1='RIS_AURORA')
        msh.receiving_facility = HD(hd_1='HIS_ODONTO')
        msh.date_time_of_message = '20250319161000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250319161000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT889900', cx_4='ODONTO_PREV', cx_5='MR'), CX(cx_1='618.749.025-43', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='BERNARDES', xpn_2='JULIANA', xpn_3='FERNANDA')
        pid.date_time_of_birth = '19950410'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua XV de Novembro 1234', xad_2='Centro', xad_3='Curitiba', xad_4='PR', xad_5='80060-000', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541965432101'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='PAN01', pl_3='1', pl_6='ODONTO_PREV')
        pv1.pv1_7 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        pv1.pv1_9 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        pv1.hospital_service = CWE(cwe_1='DEN')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025031919', cx_4='ODONTO_PREV', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025031900789', ei_2='ODONTO_PREV')
        orc.filler_order_number = EI(ei_1='FIL2025031900789', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR012^COSTA^AMANDA'
        orc.orc_18 = 'ODONTO_PREV^Clinica OdontoPrev Curitiba^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025031900789', ei_2='ODONTO_PREV')
        obr.filler_order_number = EI(ei_1='FIL2025031900789', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='70355', cwe_2='PANORAMIC XRAY DENTAL', cwe_3='CPT4')
        obr.observation_date_time = '20250319150000'
        obr.obr_14 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'
        obr.placer_field_1 = '20250319160900'
        obr.filler_field_2 = 'F'
        obr.obr_29 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='70355', cwe_2='PANORAMICA DENTAL', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'RADIOGRAFIA PANORAMICA DIGITAL'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='70355', cwe_2='PANORAMICA DENTAL', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Terceiros molares inferiores (38 e 48) inclusos em posicao mesioangular com proximidade ao canal mandibular.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='70355', cwe_2='PANORAMICA DENTAL', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Demais elementos dentarios sem alteracoes periapicais significativas.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='70355', cwe_2='PANORAMICA DENTAL', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'CONCLUSAO: Inclusao bilateral de terceiros molares inferiores. Indicada exodontia com planejamento cirurgico.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='IMG', cwe_2='Panoramica Dental', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'PIXEON^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABkAGQDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAA'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250319160900'
        obx_5.obx_16 = '50234^KATO^ROBERTO^YOSHIO^^^Dr.^CD'

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

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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CP, CWE, CX, DLD, EI, EIP, HD, MOC, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05Insurance, AdtA05NextOfKin, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-intersystems-ensemble.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-intersystems-ensemble.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='REGULACAO_ESTADUAL')
        msh.receiving_facility = HD(hd_1='SES_AM')
        msh.date_time_of_message = '20250310080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ENS20250310080001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250310080000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='ROTEADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250001', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='423.819.567-12', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CARDOSO^PEDRO^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19710330'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV DJALMA BATISTA', xad_2='1500', xad_3='APT 802', xad_4='MANAUS', xad_5='AM', xad_6='69050-010', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^991827364'
        pid.pid_14 = '^WPN^PH^^55^92^32781020'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='ENS20250001', cx_4='ENSEMBLE', cx_5='AN')
        pid.multiple_birth_indicator = 'MANAUS^AM^BR'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'LOPES^FERNANDO^DR^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='AM')
        pd1.handicap = CWE(cwe_1='10001')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CARDOSO', xpn_2='MARGARIDA', xpn_3='TERESA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^92^987261834'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO8', pl_3='A', pl_4='HOSP_FUNDACAO_HVD', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='CAR', cwe_2='Cardiologia', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250310080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='CARDOSO', aui_2='PEDRO', aui_3='HENRIQUE')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19710330')
        in1.policy_number = '7058362945781234'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I42.0', cwe_2='Cardiomiopatia dilatada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CENTRAL_LEITOS')
        msh.receiving_facility = HD(hd_1='SES_PE')
        msh.date_time_of_message = '20250312143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ENS20250312143002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312143000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='AGREGADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250002', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='538.726.491-67', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARQUES^TEREZINHA^DE^JESUS^^SRA'
        pid.date_time_of_birth = '19601215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA DO HOSPICIO', xad_2='420', xad_3='APT 305', xad_4='RECIFE', xad_5='PE', xad_6='50050-050', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^988372615'
        pid.primary_language = CWE(cwe_1='W')
        pid.religion = CWE(cwe_1='ENS20250002', cwe_4='ENSEMBLE', cwe_5='AN')
        pid.birth_place = 'RECIFE^PE^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='LEITO12', pl_3='A', pl_4='HOSP_AGAMENON_MAGALHAES', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250312143000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.in1_14 = 'MARQUES^TEREZINHA^DE^JESUS'
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19601215')
        in1.policy_number = '7062845971364892'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E10.9', cwe_2='Diabetes mellitus tipo 1 sem complicacoes', cwe_3='I10')
        dg1.diagnosis_date_time = '20250312'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertensao essencial primaria', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250312'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1, dg1_2]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_DESTINO_1')
        msh.receiving_facility = HD(hd_1='UBS_PARQUE_DEZ')
        msh.date_time_of_message = '20250315093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250315093003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250003', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='647.392.815-83', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DIAS^WAGNER^MARCELO^^^SR'
        pid.date_time_of_birth = '19660520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA RECIFE', xad_2='380', xad_3='APT 102', xad_4='MANAUS', xad_5='AM', xad_6='69057-010', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^993827465'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='SALA1', pl_4='HOSP_FUNDACAO_HVD')
        pv1.visit_number = CX(cx_1='ENS20250003', cx_4='ENSEMBLE', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='EORD20250001', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250315093000^^R'
        orc.orc_10 = '20250315093000'
        orc.orc_11 = 'RIBEIRO^DEBORA^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'AM'
        orc.enterers_location = PL(pl_1='20001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250001', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obr.observation_date_time = '20250315070000'
        obr.obr_14 = '20250315070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'RIBEIRO^DEBORA^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '20001'
        obr.filler_field_1 = 'ELAB20250001'
        obr.charge_to_practice = MOC(moc_1='20250315093000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250315093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '112'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-99'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250315093000'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='UBS_BOA_VIAGEM')
        msh.receiving_facility = HD(hd_1='SES_PE')
        msh.date_time_of_message = '20250318140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ENS20250318140004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250318140000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='DISTRIBUIDOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250002', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='538.726.491-67', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARQUES^TEREZINHA^DE^JESUS^^SRA'
        pid.date_time_of_birth = '19601215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA DO HOSPICIO', xad_2='420', xad_3='APT 305', xad_4='RECIFE', xad_5='PE', xad_6='50050-050', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^988372615'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='LEITO12', pl_3='A', pl_4='HOSP_AGAMENON_MAGALHAES', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250312143000'
        pv1.discharge_date_time = '20250318140000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.visit_description = '6'
        pv2.visit_publicity_code = CWE(cwe_1='AI')
        pv2.billing_media_code = '20250325'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E10.9', cwe_2='Diabetes mellitus tipo 1 sem complicacoes', cwe_3='I10')
        dg1.diagnosis_date_time = '20250312'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='VIGILANCIA_EPIDEMIOLOGICA')
        msh.receiving_facility = HD(hd_1='SVS_AM')
        msh.date_time_of_message = '20250320101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250320101505'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250004', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='752.493.186-54', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SOARES^CAMILA^REGINA^^^SRA'
        pid.date_time_of_birth = '19911125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV CONSTANTINO NERY', xad_2='2200', xad_3='APT 401', xad_4='MANAUS', xad_5='AM', xad_6='69020-030', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^994726183'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COLETA', pl_4='LAB_AMAZONAS_DIAG')
        pv1.visit_number = CX(cx_1='ENS20250004', cx_4='ENSEMBLE', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='EORD20250002', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250320101500^^R'
        orc.orc_10 = '20250320101500'
        orc.orc_11 = 'FERNANDES^TIAGO^DR^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'AM'
        orc.enterers_location = PL(pl_1='30001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250002', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA [Presence] in Respiratory specimen by NAA', cwe_3='LN')
        obr.observation_date_time = '20250320070000'
        obr.obr_14 = '20250320070000'
        obr.obr_15 = 'NP^Swab nasofaringeo'
        obr.obr_16 = 'FERNANDES^TIAGO^DR^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '30001'
        obr.filler_field_1 = 'ELAB20250002'
        obr.charge_to_practice = MOC(moc_1='20250320101500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA [Presence]', cwe_3='LN')
        obx.obx_5 = 'Nao detectado'
        obx.reference_range = 'Nao detectado'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320101500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo RT-PCR SARS-CoV-2', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'ENSEMBLE^AP^^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIg'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0gL0NvbnRlbnRzIDMgMCBSIC9SZXNvdXJjZXMgPDwgL0ZvbnQgPDwgL0YxIDw8IC9UeXBlIC9Gb250IC9CYXNlRm9udCAvSGVsdmV0aWNhID4+'
            'ID4+ID4+ID4+ID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbNCAwIFJdIC9Db3VudCAxID4+CmVuZG9iagolTGF1ZG8gUlQtUENSIFNBUlMtQ29WLTIgLSBO'
            'YW8gZGV0ZWN0YWRv'
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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='AGENDA_CENTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250322083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'ENS20250322083006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250322083000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='ROTEADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250005', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='864.293.751-26', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GONCALVES^RAFAEL^DOMINGOS^^^SR'
        pid.date_time_of_birth = '19790705'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV TORQUATO TAPAJOS', xad_2='4500', xad_3='APT 1102', xad_4='MANAUS', xad_5='AM', xad_6='69093-010', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^988365412'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='CONS2', pl_4='HOSP_FUNDACAO_HVD')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250322083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED MANAUS')
        in1.insurance_company_id = CX(cx_1='UNIMED_AM')
        in1.insurance_company_name = XON(xon_1='UNIMED MANAUS COOPERATIVA DE TRABALHO MEDICO')
        in1.plan_type = CWE(cwe_1='GONCALVES', cwe_2='RAFAEL', cwe_3='DOMINGOS')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19790705')
        in1.policy_deductible = CP(cp_1='0904738291056')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G35', cwe_2='Esclerose multipla', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CONSULTORIO_DR_BARROS')
        msh.receiving_facility = HD(hd_1='CLINICA_OLINDA')
        msh.date_time_of_message = '20250324110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250324110007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250006', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='973.184.625-37', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MORAES^SUELI^APARECIDA^^^SRA'
        pid.date_time_of_birth = '19761020'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA DOS NAVEGANTES', xad_2='900', xad_3='APT 502', xad_4='RECIFE', xad_5='PE', xad_6='51020-010', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^987364219'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='SALA1', pl_4='LAB_NORDESTE_DIAG')
        pv1.visit_number = CX(cx_1='ENS20250006', cx_4='ENSEMBLE', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='EORD20250003', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250324110000^^R'
        orc.orc_10 = '20250324110000'
        orc.orc_11 = 'BARROS^CLAUDIO^DR^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='40001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250003', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='24321-2', cwe_2='Basic metabolic panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250324070000'
        obr.obr_14 = '20250324070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'BARROS^CLAUDIO^DR^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '40001'
        obr.filler_field_1 = 'ELAB20250003'
        obr.charge_to_practice = MOC(moc_1='20250324110000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='Sodium [Moles/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '141'
        obx.units = CWE(cwe_1='mEq/L')
        obx.reference_range = '136-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='mEq/L')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '0.8'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.6-1.2'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '95'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '70-99'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea nitrogen [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '15'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '7-20'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250324110000'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='MPI_CENTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250326100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'ENS20250326100008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250326100000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='SINCRONIZADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250007', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='184.529.736-92', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GUIMARAES^EDUARDO^TADEU^^^SR'
        pid.date_time_of_birth = '19690615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV EFIGENIO SALES', xad_2='1850', xad_3='APT 304', xad_4='MANAUS', xad_5='AM', xad_6='69060-020', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^982617354'
        pid.pid_14 = '^NET^Internet^^eduardo.guimaraes@email.com.br'
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='ENS20250007', cx_4='ENSEMBLE', cx_5='AN')
        pid.multiple_birth_indicator = 'MANAUS^AM^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_GERAL', pl_2='CONS1', pl_4='HOSP_FUNDACAO_HVD')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GUIMARAES', xpn_2='ELOISA', xpn_3='MARTA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^92^973846152'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_AM')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='GUIMARAES', cwe_2='EDUARDO', cwe_3='TADEU')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19690615')
        in1.policy_deductible = CP(cp_1='1024738162094')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PACS_CENTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250328091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ENS20250328091509'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250008', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='295.638.471-03', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MELO^PRISCILA^ANGELICA^^^SRA'
        pid.date_time_of_birth = '19840412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA RIO PURUS', xad_2='750', xad_3='CASA 18', xad_4='MANAUS', xad_5='AM', xad_6='69060-355', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^973847265'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_RM', pl_4='HOSP_FUNDACAO_HVD')
        pv1.visit_number = CX(cx_1='ENS20250008', cx_4='ENSEMBLE', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_AM')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='MELO', cwe_2='PRISCILA', cwe_3='ANGELICA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19840412')
        in1.policy_deductible = CP(cp_1='1138465927103')

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
        orc.placer_order_number = EI(ei_1='EORD20250004', ei_2='ENSEMBLE')
        orc.orc_7 = '^^^20250328091500^^R'
        orc.date_time_of_order_event = '20250328091500'
        orc.orc_10 = 'LOPES^FERNANDO^DR^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'AM'
        orc.orc_12 = '10001'
        orc.order_effective_date_time = '20250328091500'
        orc.orc_18 = 'HOSP_FUNDACAO_HVD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250004', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='24969-8', cwe_2='MR Lumbar spine', cwe_3='LN')
        obr.observation_date_time = '20250328091500'
        obr.obr_16 = 'LOPES^FERNANDO^DR^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '10001'
        obr.filler_field_1 = 'ERAD20250001'
        obr.parent_result = PRL(prl_1='RM')
        obr.parent_results_observation_identifier = EIP(eip_2='Hernia discal L4-L5 com compressao radicular')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M51.1', cwe_2='Transtorno de disco lombar com radiculopatia', cwe_3='I10')
        dg1.diagnosis_date_time = '20250328'
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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='MEDICO_RESPONSAVEL')
        msh.receiving_facility = HD(hd_1='CLINICA_BOA_VIAGEM')
        msh.date_time_of_message = '20250330064500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250330064510'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250009', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='362.749.851-48', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'XAVIER^ANTONIO^MARCELO^^^SR'
        pid.date_time_of_birth = '19730820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA RIBEIRO DE BRITO', xad_2='1100', xad_3='APT 601', xad_4='RECIFE', xad_5='PE', xad_6='51021-310', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^976358214'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMATO', pl_2='LEITO4', pl_3='A', pl_4='HOSP_OSWALDO_CRUZ_PE', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='HEM', pl_2='Hematologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250328090000')

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
        orc.placer_order_number = EI(ei_1='EORD20250005', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250330064500^^R'
        orc.orc_10 = '20250330064500'
        orc.orc_11 = 'TAVARES^MARCELO^DR^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='50001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250005', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250330050000'
        obr.obr_14 = '20250330050000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'TAVARES^MARCELO^DR^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'ELAB20250004'
        obr.charge_to_practice = MOC(moc_1='20250330064500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '1.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250330064500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes [#/volume] in Blood', cwe_3='LN')
        obx_2.obx_5 = '2.8'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.5-5.9'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250330064500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx_3.obx_5 = '7.5'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.0-17.5'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250330064500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit [Volume Fraction] of Blood', cwe_3='LN')
        obx_4.obx_5 = '22.8'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '38.0-52.0'
        obx_4.interpretation_codes = CWE(cwe_1='LL')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250330064500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets [#/volume] in Blood', cwe_3='LN')
        obx_5.obx_5 = '18'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='LL')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250330064500'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='REGULACAO_AM')
        msh.receiving_facility = HD(hd_1='SES_AM')
        msh.date_time_of_message = '20250401153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ENS20250401153011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250401153000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='REGULADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250010', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='459.836.271-69', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CASTRO^EVANDRO^SEBASTIAO^^^SR'
        pid.date_time_of_birth = '19481105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA AUTAZ MIRIM', xad_2='580', xad_3='APT 201', xad_4='MANAUS', xad_5='AM', xad_6='69084-450', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^971827465'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO_CIR', pl_2='LEITO1', pl_4='HOSP_FUNDACAO_HVD', pl_8='UTI_NEUROCIRURGICA')
        pv1.hospital_service = CWE(cwe_1='NCR', cwe_2='Neurocirurgia', cwe_3='HL70069')
        pv1.bad_debt_recovery_amount = 'MED^LEITO5^^HOSP_REGIONAL_AM_NORTE'
        pv1.discharged_to_location = DLD(dld_1='20250330080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='TRANSFERENCIA POR NECESSIDADE DE NEUROCIRURGIA - HEMATOMA SUBDURAL')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S06.5', cwe_2='Hemorragia subdural traumatica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250330'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='VIGILANCIA')
        msh.receiving_facility = HD(hd_1='SVS_PE')
        msh.date_time_of_message = '20250403091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250403091512'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250011', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='573.184.926-50', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'VIEIRA^DANIELA^MAYRA^^^SRA'
        pid.date_time_of_birth = '19940130'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA REAL DA TORRE', xad_2='210', xad_3='APT 803', xad_4='RECIFE', xad_5='PE', xad_6='50710-901', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^965827314'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_INFECTO', pl_2='CONS1', pl_4='HOSP_OSWALDO_CRUZ_PE')
        pv1.temporary_location = PL(pl_1='INF', pl_2='Infectologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250403091500')

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
        orc.placer_order_number = EI(ei_1='EORD20250006', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250403091500^^R'
        orc.orc_10 = '20250403091500'
        orc.orc_11 = 'MOREIRA^BEATRIZ^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='60001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250006', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='5196-1', cwe_2='Dengue virus IgM Ab [Presence] in Serum', cwe_3='LN')
        obr.observation_date_time = '20250401070000'
        obr.obr_14 = '20250401070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'MOREIRA^BEATRIZ^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'ELAB20250005'
        obr.charge_to_practice = MOC(moc_1='20250403091500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='7855-0', cwe_2='Dengue virus IgM Ab [Presence] in Serum', cwe_3='LN')
        obx.obx_5 = 'Reagente'
        obx.reference_range = 'Nao reagente'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250403091500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='7854-3', cwe_2='Dengue virus IgG Ab [Presence] in Serum', cwe_3='LN')
        obx_2.obx_5 = 'Nao reagente'
        obx_2.reference_range = 'Nao reagente'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250403091500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets [#/volume] in Blood', cwe_3='LN')
        obx_3.obx_5 = '85'
        obx_3.units = CWE(cwe_1='10*3/uL')
        obx_3.reference_range = '150-400'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250403091500'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_DIAGAM')
        msh.receiving_facility = HD(hd_1='DIAGAM_MANAUS')
        msh.date_time_of_message = '20250405074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ENS20250405074513'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250012', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='684.295.137-21', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DUARTE^ROSANGELA^FATIMA^^^SRA'
        pid.date_time_of_birth = '19820605'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SAO GABRIEL', xad_2='1450', xad_3='APT 504', xad_4='MANAUS', xad_5='AM', xad_6='69053-040', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^961829374'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_REUMATO', pl_2='CONS1', pl_4='HOSP_FUNDACAO_HVD')
        pv1.temporary_location = PL(pl_1='REU', pl_2='Reumatologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250405074500')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_2='SULAMERICA SAUDE')
        in1.insurance_company_id = CX(cx_1='SULAM_AM')
        in1.insurance_company_name = XON(xon_1='SULAMERICA COMPANHIA DE SEGUROS')
        in1.plan_type = CWE(cwe_1='DUARTE', cwe_2='ROSANGELA', cwe_3='FATIMA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19820605')
        in1.policy_deductible = CP(cp_1='1273846592013')

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
        orc.placer_order_number = EI(ei_1='EORD20250007', ei_2='ENSEMBLE')
        orc.orc_7 = '^^^20250405074500^^R'
        orc.date_time_of_order_event = '20250405074500'
        orc.orc_10 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'AM'
        orc.orc_12 = '70001'
        orc.order_effective_date_time = '20250405074500'
        orc.orc_18 = 'HOSP_FUNDACAO_HVD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250007', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='5130-0', cwe_2='Anti-nuclear Ab [Presence] in Serum', cwe_3='LN')
        obr.observation_date_time = '20250405074500'
        obr.obr_16 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'ELAB20250006'
        obr.parent_result = PRL(prl_1='IMU')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='EORD20250008', ei_2='ENSEMBLE')
        orc_2.orc_7 = '^^^20250405074500^^R'
        orc_2.date_time_of_order_event = '20250405074500'
        orc_2.orc_10 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        orc_2.orc_11 = 'AM'
        orc_2.orc_12 = '70001'
        orc_2.order_effective_date_time = '20250405074500'
        orc_2.orc_18 = 'HOSP_FUNDACAO_HVD'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='EORD20250008', ei_2='ENSEMBLE')
        obr_2.universal_service_identifier = CWE(cwe_1='33935-8', cwe_2='Anti-dsDNA Ab [Units/volume] in Serum', cwe_3='LN')
        obr_2.observation_date_time = '20250405074500'
        obr_2.obr_16 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        obr_2.obr_17 = 'AM'
        obr_2.placer_field_1 = '70001'
        obr_2.filler_field_1 = 'ELAB20250007'
        obr_2.parent_result = PRL(prl_1='IMU')

        # .. build the ORDER_DETAIL group ..
        order_detail_2 = OrmO01OrderDetail()
        order_detail_2.obr = obr_2

        # .. build the ORDER group ..
        order_2 = OrmO01Order()
        order_2.orc = orc_2
        order_2.order_detail = order_detail_2

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_REUMATO')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250407143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250407143014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250012', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='684.295.137-21', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DUARTE^ROSANGELA^FATIMA^^^SRA'
        pid.date_time_of_birth = '19820605'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SAO GABRIEL', xad_2='1450', xad_3='APT 504', xad_4='MANAUS', xad_5='AM', xad_6='69053-040', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^961829374'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_REUMATO', pl_2='CONS1', pl_4='HOSP_FUNDACAO_HVD')
        pv1.temporary_location = PL(pl_1='REU', pl_2='Reumatologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250405074500')

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
        orc.placer_order_number = EI(ei_1='EORD20250007', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250407143000^^R'
        orc.orc_10 = '20250407143000'
        orc.orc_11 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'AM'
        orc.enterers_location = PL(pl_1='70001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250007', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='5130-0', cwe_2='Anti-nuclear Ab [Presence] in Serum', cwe_3='LN')
        obr.observation_date_time = '20250405074500'
        obr.obr_14 = '20250405074500'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'FONSECA^ELISA^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'ELAB20250006'
        obr.charge_to_practice = MOC(moc_1='20250407143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5130-0', cwe_2='Anti-nuclear Ab [Presence]', cwe_3='LN')
        obx.obx_5 = 'Reagente 1:640 - padrao homogeneo'
        obx.reference_range = 'Nao reagente'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250407143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Imunofluorescencia FAN HEp-2', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'ENSEMBLE^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYa HSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChM'
            'oGhYaKCgoKCgoKCgoKCgo KCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QA FAABAAAAAAAAAAAAAAAAAAAACf/EABsQAAEFA'
            'QEAAAAAAAAAAAAAAAQBAgMFBgAH/8QAFQEBAQAAAAAA AAAAAAAAAAAACP/EABkRAAIDAQAAAAAAAAAAAAAAAAECAAMRIf/aAAwDAQACEQMRAD8ASnNGQU4gLSBJ bXVub2ZsdW9yZXN'
            'jZW5jaWEgSEVwLTIgLSBQYWRyYW8gSG9tb2dlbmVv'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33935-8', cwe_2='Anti-dsDNA Ab [Units/volume]', cwe_3='LN')
        obx_3.obx_5 = '85'
        obx_3.units = CWE(cwe_1='IU/mL')
        obx_3.reference_range = '<30'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250407143000'

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

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M32.9', cwe_2='Lupus eritematoso sistemico nao especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250407'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='MPI_CENTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250408100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'ENS20250408100015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250408100000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='MPI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='ENS20250013', cx_4='ENSEMBLE', cx_5='MR'),
            CX(cx_1='795.402.681-32', cx_4='BRASIL', cx_5='CPF'),
            CX(cx_1='12839465782', cx_4='BRASIL', cx_5='CNS'),
        ]
        pid.pid_5 = 'PAIVA^GUSTAVO^RENATO^^^SR'
        pid.date_time_of_birth = '19940915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV CAMAPUA', xad_2='380', xad_3='APT 1502', xad_4='MANAUS', xad_5='AM', xad_6='69050-200', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^958276134'
        pid.pid_14 = '^NET^Internet^^gustavo.paiva@email.com.br'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='ENS20250013', cx_4='ENSEMBLE', cx_5='AN')
        pid.multiple_birth_indicator = 'MANAUS^AM^BR'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'AGUIAR^DOUGLAS^DR^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='AM')
        pd1.handicap = CWE(cwe_1='80001')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PAIVA', xpn_2='MARILENE', xpn_3='SUELY')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mae', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^92^947382615'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_AM')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='PAIVA', cwe_2='MARILENE', cwe_3='SUELY')
        in1.name_of_insured = XPN(xpn_1='DEP', xpn_2='Dependente')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19940915')
        in1.policy_deductible = CP(cp_1='1382746591023')

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.insurance = insurance

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CONSULTORIO_DRA_BORGES')
        msh.receiving_facility = HD(hd_1='CLINICA_CASA_FORTE')
        msh.date_time_of_message = '20250409153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250409153016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250014', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='864.293.752-41', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PINTO^RICARDO^OTAVIO^^^SR'
        pid.date_time_of_birth = '19770925'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ROSA E SILVA', xad_2='2300', xad_3='APT 902', xad_4='RECIFE', xad_5='PE', xad_6='52050-020', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^972658493'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='SALA2', pl_4='LAB_NORDESTE_DIAG')
        pv1.visit_number = CX(cx_1='ENS20250014', cx_4='ENSEMBLE', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='EORD20250009', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250409153000^^R'
        orc.orc_10 = '20250409153000'
        orc.orc_11 = 'BORGES^MARIANE^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='60002')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250009', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Hepatic function panel', cwe_3='LN')
        obr.observation_date_time = '20250409070000'
        obr.obr_14 = '20250409070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'BORGES^MARIANE^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '60002'
        obr.filler_field_1 = 'ELAB20250008'
        obr.charge_to_practice = MOC(moc_1='20250409153000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '125'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250409153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '98'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250409153000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Total Bilirubin [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '2.8'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.1-1.2'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250409153000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '180'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '44-147'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250409153000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2862-1', cwe_2='Albumin [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '3.2'
        obx_5.units = CWE(cwe_1='g/dL')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250409153000'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='AGENDA_CENTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_FUNDACAO_HVD')
        msh.date_time_of_message = '20250411093000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'ENS20250411093017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='EAGD20250001', ei_2='ENSEMBLE')
        sch.appointment_reason = CWE(cwe_1='CONSULTA', cwe_2='Consulta Medica')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='30')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250420100000', xcn_5='20250420103000')
        sch.sch_13 = 'LOPES^FERNANDO^DR^^^DR^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='AM')
        sch.placer_contact_location = PL(pl_1='10001')
        sch.sch_17 = 'LOPES^FERNANDO^DR^^^DR^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='AM')
        sch.filler_contact_location = PL(pl_1='10001')
        sch.parent_filler_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250005', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='864.293.751-26', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GONCALVES^RAFAEL^DOMINGOS^^^SR'
        pid.date_time_of_birth = '19790705'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV TORQUATO TAPAJOS', xad_2='4500', xad_3='APT 1102', xad_4='MANAUS', xad_5='AM', xad_6='69093-010', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^988365412'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='CONS2', pl_4='HOSP_FUNDACAO_HVD')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='NEURO_CONS2', cwe_2='Consultorio Neurologia 2', cwe_3='ENSEMBLE')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='CONS_NEURO', cwe_2='Consulta Neurologica de Retorno', cwe_3='ENSEMBLE')
        ais.start_date_time = '20250420100000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='OPERADORA_AMIL')
        msh.receiving_facility = HD(hd_1='AMIL_CENTRAL')
        msh.date_time_of_message = '20250413190000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ENS20250413190018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250413190000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='NOTIFICADOR')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250015', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='371.946.825-58', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'COELHO^IGOR^MAGNO^^^SR'
        pid.date_time_of_birth = '19761115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV DAS TORRES', xad_2='980', xad_3='APT 305', xad_4='MANAUS', xad_5='AM', xad_6='69058-901', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^61^988990011'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTOP', pl_2='LEITO3', pl_3='A', pl_4='HOSP_FUNDACAO_HVD', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='ORT', cwe_2='Ortopedia', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250413190000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_AM')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='COELHO', cwe_2='IGOR', cwe_3='MAGNO')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19761115')
        in1.insureds_date_of_birth = 'AV DAS TORRES^980^APT 305^^MANAUS^AM^69058-901'
        in1.policy_deductible = CP(cp_1='1493827465120')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S82.0', cwe_2='Fratura da patela', cwe_3='I10')
        dg1.diagnosis_date_time = '20250413'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_AMAZONIA', hd_2='7001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='BANCO_SANGUE')
        msh.receiving_facility = HD(hd_1='HEMOAM_MANAUS')
        msh.date_time_of_message = '20250415060000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENS20250415060019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250015', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='371.946.825-58', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'COELHO^IGOR^MAGNO^^^SR'
        pid.date_time_of_birth = '19761115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV DAS TORRES', xad_2='980', xad_3='APT 305', xad_4='MANAUS', xad_5='AM', xad_6='69058-901', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^988990011'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTOP', pl_2='LEITO3', pl_3='A', pl_4='HOSP_FUNDACAO_HVD', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='ORT', pl_2='Ortopedia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250413190000')

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
        orc.placer_order_number = EI(ei_1='EORD20250010', ei_2='ENSEMBLE')
        orc.orc_8 = '^^^20250415060000^^R'
        orc.orc_10 = '20250415060000'
        orc.orc_11 = 'MEDEIROS^VANESSA^DRA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'AM'
        orc.enterers_location = PL(pl_1='90001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EORD20250010', ei_2='ENSEMBLE')
        obr.universal_service_identifier = CWE(cwe_1='34532-2', cwe_2='Blood type and crossmatch panel', cwe_3='LN')
        obr.observation_date_time = '20250414200000'
        obr.obr_14 = '20250414200000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'MEDEIROS^VANESSA^DRA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '90001'
        obr.filler_field_1 = 'ELAB20250009'
        obr.charge_to_practice = MOC(moc_1='20250415060000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='883-9', cwe_2='ABO group [Type] in Blood', cwe_3='LN')
        obx.obx_5 = 'O'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250415060000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh [Type] in Blood', cwe_3='LN')
        obx_2.obx_5 = 'Positivo'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250415060000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='54365-4', cwe_2='Irregular Ab screen [Interpretation] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = 'Negativo'
        obx_3.reference_range = 'Negativo'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250415060000'

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
    """ Based on live/br/br-intersystems-ensemble.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENSEMBLE')
        msh.sending_facility = HD(hd_1='HIE_REDE_PUBLICA_PE', hd_2='7002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='UBS_AFOGADOS')
        msh.receiving_facility = HD(hd_1='SES_PE')
        msh.date_time_of_message = '20250418110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ENS20250418110020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250418110000'
        evn.operator_id = XCN(xcn_1='SISTEMA', xcn_2='ENSEMBLE', xcn_3='CONTRA_REFERENCIA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ENS20250009', cx_4='ENSEMBLE', cx_5='MR'), CX(cx_1='362.749.851-48', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'XAVIER^ANTONIO^MARCELO^^^SR'
        pid.date_time_of_birth = '19730820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA RIBEIRO DE BRITO', xad_2='1100', xad_3='APT 601', xad_4='RECIFE', xad_5='PE', xad_6='51021-310', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^976358214'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMATO', pl_2='LEITO4', pl_3='A', pl_4='HOSP_OSWALDO_CRUZ_PE', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='HEM', pl_2='Hematologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250328090000'
        pv1.discharge_date_time = '20250418110000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.visit_description = '21'
        pv2.visit_publicity_code = CWE(cwe_1='AI')
        pv2.billing_media_code = '20250425'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C91.0', cwe_2='Leucemia linfoblastica aguda', cwe_3='I10')
        dg1.diagnosis_date_time = '20250328'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='D69.6', cwe_2='Trombocitopenia nao especificada', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250330'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]

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

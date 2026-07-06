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
    RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXE, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-mv-soul.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-mv-soul.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SIRIO_LIBANES')
        msh.date_time_of_message = '20250312083045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250312083045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312083000'
        evn.operator_id = XCN(xcn_1='PEREIRA', xcn_2='MARIA', xcn_3='ENFERMEIRA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250001', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='318.475.962-04', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'OLIVEIRA^JOAO^CARLOS^^^SR'
        pid.date_time_of_birth = '19780415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA OSCAR FREIRE', xad_2='1250', xad_3='APT 42', xad_4='SAO PAULO', xad_5='SP', xad_6='01426-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^999887766'
        pid.pid_14 = '^WPN^PH^^55^11^32145678'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='PAC20250001', cx_4='MV_SOUL', cx_5='AN')
        pid.multiple_birth_indicator = 'SAO PAULO^SP^BR'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'MEDEIROS^ROBERTO^GUILHERME^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='SP')
        pd1.handicap = CWE(cwe_1='123456')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='OLIVEIRA', xpn_2='ANA', xpn_3='LUCIA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^11^998776655'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4NORTE', pl_2='401', pl_3='A', pl_4='HOSP_SIRIO_LIBANES', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='SUR', cwe_2='Cirurgica', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250312083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='COLECISTECTOMIA VIDEOLAPAROSCOPICA')
        pv2.visit_publicity_code = CWE(cwe_1='AI')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PAULISTANA')
        in1.insurance_company_id = CX(cx_1='UNIMED_SP')
        in1.insurance_company_name = XON(xon_1='UNIMED PAULISTANA')
        in1.plan_type = CWE(cwe_1='OLIVEIRA', cwe_2='JOAO', cwe_3='CARLOS')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19780415')
        in1.insureds_date_of_birth = 'RUA OSCAR FREIRE^1250^APT 42^SAO PAULO^SP^01426-001'
        in1.policy_deductible = CP(cp_1='0058901234567')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Calculo da vesicula biliar sem colecistite', cwe_3='I10')
        dg1.diagnosis_date_time = '20250312'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/br/br-mv-soul.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_MATER_DEI', hd_2='5678', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_MATER_DEI')
        msh.date_time_of_message = '20250315140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250315140000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250315140000'
        evn.operator_id = XCN(xcn_1='COSTA', xcn_2='FERNANDA', xcn_3='DE_SOUZA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250002', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='542.671.893-11', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SANTOS^MARIA^APARECIDA^^^SRA'
        pid.date_time_of_birth = '19650823'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV DO CONTORNO', xad_2='7345', xad_3='CONJ 12', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30110-100', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^997654321'
        pid.pid_14 = '^WPN^PH^^55^31^31234567'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='PAC20250002', cx_4='MV_SOUL', cx_5='AN')
        pid.multiple_birth_indicator = 'BELO HORIZONTE^MG^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5SUL', pl_2='512', pl_3='B', pl_4='HOSP_MATER_DEI', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250310093000')
        pv1.admit_date_time = '20250315140000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.visit_description = '2'
        pv2.visit_publicity_code = CWE(cwe_1='AI')
        pv2.billing_media_code = '20250322'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus tipo 2 sem complicacoes', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250310'
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
    """ Based on live/br/br-mv-soul.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_COPA_DOR', hd_2='9012', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_DASA')
        msh.receiving_facility = HD(hd_1='DASA_RJ')
        msh.date_time_of_message = '20250320091530'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250320091530003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250003', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='671.483.295-22', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'FERREIRA^PEDRO^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19900102'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='RUA VISCONDE DE PIRAJA',
            xad_2='330',
            xad_3='APT 801',
            xad_4='RIO DE JANEIRO',
            xad_5='RJ',
            xad_6='22410-003',
            xad_7='BR',
        )
        pid.pid_13 = '^PRN^PH^^55^21^998887766'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA1', pl_4='HOSP_COPA_DOR')
        pv1.visit_number = CX(cx_1='PAC20250003', cx_4='MV_SOUL', cx_5='VN')
        pv1.admit_date_time = '20250320091500'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='FERREIRA', aui_2='PEDRO', aui_3='HENRIQUE')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19900102')
        in1.policy_number = '7001234567890123'

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
        orc.placer_order_number = EI(ei_1='ORD20250001', ei_2='MV_SOUL')
        orc.orc_7 = '^^^20250320091530^^R'
        orc.date_time_of_order_event = '20250320091530'
        orc.orc_10 = 'MENDES^RICARDO^TIAGO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'RJ'
        orc.orc_12 = '54321'
        orc.order_effective_date_time = '20250320091530'
        orc.orc_18 = 'HOSP_COPA_DOR'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250001', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250320091500'
        obr.obr_16 = 'MENDES^RICARDO^TIAGO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'RJ'
        obr.placer_field_1 = '54321'
        obr.filler_field_1 = 'LAB20250001'
        obr.parent_result = PRL(prl_1='HEM')

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
        orc_2.placer_order_number = EI(ei_1='ORD20250002', ei_2='MV_SOUL')
        orc_2.orc_7 = '^^^20250320091530^^R'
        orc_2.date_time_of_order_event = '20250320091530'
        orc_2.orc_10 = 'MENDES^RICARDO^TIAGO^^^DR^^^^^^^^^CRM'
        orc_2.orc_11 = 'RJ'
        orc_2.orc_12 = '54321'
        orc_2.order_effective_date_time = '20250320091530'
        orc_2.orc_18 = 'HOSP_COPA_DOR'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD20250002', ei_2='MV_SOUL')
        obr_2.universal_service_identifier = CWE(cwe_1='24321-2', cwe_2='Basic metabolic panel - Serum or Plasma', cwe_3='LN')
        obr_2.observation_date_time = '20250320091500'
        obr_2.obr_16 = 'MENDES^RICARDO^TIAGO^^^DR^^^^^^^^^CRM'
        obr_2.obr_17 = 'RJ'
        obr_2.placer_field_1 = '54321'
        obr_2.filler_field_1 = 'LAB20250002'
        obr_2.parent_result = PRL(prl_1='BIO')

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
    """ Based on live/br/br-mv-soul.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_ERASTO_GAERTNER', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_ERASTO_GAERTNER')
        msh.date_time_of_message = '20250321143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321143000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250004', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='782.395.146-33', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'ALMEIDA^LUCAS^GABRIEL^^^SR'
        pid.date_time_of_birth = '19850617'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA MARECHAL DEODORO', xad_2='612', xad_3='LOJA 3', xad_4='CURITIBA', xad_5='PR', xad_6='80020-320', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^996543210'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA2', pl_4='HOSP_ERASTO_GAERTNER')
        pv1.visit_number = CX(cx_1='PAC20250004', cx_4='MV_SOUL', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD20250003', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250321143000^^R'
        orc.orc_10 = '20250321143000'
        orc.orc_11 = 'RIBEIRO^SOFIA^LUIZA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PR'
        orc.enterers_location = PL(pl_1='67890')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250003', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250321080000'
        obr.obr_14 = '20250321080000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'RIBEIRO^SOFIA^LUIZA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '67890'
        obr.filler_field_1 = 'LAB20250003'
        obr.charge_to_practice = MOC(moc_1='20250321143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-11.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes [#/volume] in Blood', cwe_3='LN')
        obx_2.obx_5 = '5.1'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.5-5.9'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx_3.obx_5 = '14.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.0-17.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit [Volume Fraction] of Blood', cwe_3='LN')
        obx_4.obx_5 = '44.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '38.0-52.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321143000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV [Entitic volume]', cwe_3='LN')
        obx_5.obx_5 = '86.7'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321143000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets [#/volume] in Blood', cwe_3='LN')
        obx_6.obx_5 = '245'
        obx_6.units = CWE(cwe_1='10*3/uL')
        obx_6.reference_range = '150-400'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321143000'

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
    """ Based on live/br/br-mv-soul.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_BENEFICENCIA_PORTUGUESA', hd_2='3456', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PACS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BENEFICENCIA_PORTUGUESA')
        msh.date_time_of_message = '20250322101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322101500005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250005', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='893.516.247-44', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'RIBEIRO^CAMILA^SOUZA^^^SRA'
        pid.date_time_of_birth = '19921230'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV BRASIL', xad_2='1890', xad_3='BLOCO B', xad_4='SAO PAULO', xad_5='SP', xad_6='01430-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^995432109'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_TC', pl_4='HOSP_BENEFICENCIA_PORTUGUESA')
        pv1.visit_number = CX(cx_1='PAC20250005', cx_4='MV_SOUL', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD20250004', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250322101500^^R'
        orc.orc_10 = '20250322101500'
        orc.orc_11 = 'VARGAS^MARCOS^EDUARDO^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'SP'
        orc.enterers_location = PL(pl_1='11111')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250004', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='24627-2', cwe_2='CT Chest', cwe_3='LN')
        obr.observation_date_time = '20250322090000'
        obr.obr_14 = '20250322090000'
        obr.obr_15 = 'CHEST^Torax'
        obr.obr_16 = 'VARGAS^MARCOS^EDUARDO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '11111'
        obr.filler_field_1 = 'RAD20250001'
        obr.charge_to_practice = MOC(moc_1='20250322101500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo Tomografia Torax', cwe_3='AUSPDI')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'MV_SOUL^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKJUxhdWRvIGRlIFRvbW9ncmFmaWEgQ29t'
            'cHV0YWRvcml6YWRhIGRlIFRvcmF4'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx_2.obx_5 = 'Nao foram identificadas alteracoes parenquimatosas significativas. Ausencia de derrame pleural.'
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
    """ Based on live/br/br-mv-soul.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_SAO_LUCAS_PUC', hd_2='7890', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_LUCAS_PUC')
        msh.date_time_of_message = '20250325084500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG20250325084500006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250325084500'
        evn.operator_id = XCN(xcn_1='LIMA', xcn_2='JULIANA', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250006', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='915.738.246-55', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'NASCIMENTO^RAFAEL^AUGUSTO^^^SR'
        pid.date_time_of_birth = '19750919'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV IPIRANGA', xad_2='6681', xad_3='APT 1201', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90619-900', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^994321098'
        pid.pid_14 = '^WPN^PH^^55^51^30987654'
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='PAC20250006', cx_4='MV_SOUL', cx_5='AN')
        pid.multiple_birth_indicator = 'PORTO ALEGRE^RS^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_CARDIO', pl_2='CONS1', pl_4='HOSP_SAO_LUCAS_PUC')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250325084500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_RS')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='NASCIMENTO', cwe_2='RAFAEL', cwe_3='AUGUSTO')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19750919')
        in1.insureds_date_of_birth = 'AV IPIRANGA^6681^APT 1201^PORTO ALEGRE^RS^90619-900'
        in1.policy_deductible = CP(cp_1='0012345678901')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertensao essencial primaria', cwe_3='I10')
        dg1.diagnosis_date_time = '20250325'
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
    """ Based on live/br/br-mv-soul.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_ALBERT_EINSTEIN', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_ALBERT_EINSTEIN')
        msh.date_time_of_message = '20250326153000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MSG20250326153000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250007', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='836.514.972-66', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'COSTA^BEATRIZ^FERNANDA^^^SRA'
        pid.date_time_of_birth = '19880305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV ALBERT EINSTEIN', xad_2='627', xad_3='APT 54', xad_4='SAO PAULO', xad_5='SP', xad_6='05652-900', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^993210987'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6NORTE', pl_2='601', pl_3='A', pl_4='HOSP_ALBERT_EINSTEIN', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250324100000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='PRESC20250001', ei_2='MV_SOUL')
        orc.orc_7 = '^^^20250326153000^^R'
        orc.date_time_of_order_event = '20250326153000'
        orc.orc_10 = 'RODRIGUES^FELIPE^GUSTAVO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'SP'
        orc.orc_12 = '22222'
        orc.order_effective_date_time = '20250326153000'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20250326160000^^R'
        rxe.give_code = CWE(cwe_1='49999-4000', cwe_2='Dipirona sodica 500mg/mL', cwe_3='ANVISA')
        rxe.give_amount_maximum = '1'
        rxe.give_units = CWE(cwe_1='AMP', cwe_3='HL70292')
        rxe.give_per_time_unit = '2'
        rxe.give_rate_units = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LA', cwe_2='Braco esquerdo', cwe_3='HL70163')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. assemble the full message ..
        msg = RDE_O11()
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
    """ Based on live/br/br-mv-soul.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_SAO_RAFAEL', hd_2='2345', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CENTRO_CIRURGICO')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_RAFAEL')
        msh.date_time_of_message = '20250328101500'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250328101500008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='AGD20250001', ei_2='MV_SOUL')
        sch.appointment_reason = CWE(cwe_1='CIRURGIA', cwe_2='Cirurgia Eletiva')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='60')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250402080000', xcn_5='20250402094000')
        sch.sch_13 = 'CARDOSO^RICARDO^MARCELO^^^DR^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='BA')
        sch.placer_contact_location = PL(pl_1='33333')
        sch.sch_17 = 'CARDOSO^RICARDO^MARCELO^^^DR^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='BA')
        sch.filler_contact_location = PL(pl_1='33333')
        sch.parent_filler_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250008', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='547.291.638-77', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'BARBOSA^ANTONIO^MARCOS^^^SR'
        pid.date_time_of_birth = '19700712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV TANCREDO NEVES', xad_2='148', xad_3='CASA', xad_4='SALVADOR', xad_5='BA', xad_6='41820-021', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^992109876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CC', pl_2='SALA3', pl_4='HOSP_SAO_RAFAEL')
        pv1.temporary_location = PL(pl_1='SUR', pl_2='Cirurgica', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='CC_SALA3', cwe_2='Sala Cirurgica 3', cwe_3='MV_SOUL')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='ARTRO_JOELHO', cwe_2='Artroscopia de joelho', cwe_3='MV_SOUL')
        ais.start_date_time = '20250402080000'
        ais.duration = '60'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='CARDOSO', cwe_2='RICARDO', cwe_3='MARCELO', cwe_6='DR', cwe_15='CRM')
        aig.resource_type = CWE(cwe_1='BA')
        aig.resource_group = CWE(cwe_1='33333')
        aig.resource_quantity = 'CIRURGIAO^Cirurgiao Principal'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.general_resource = general_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/br/br-mv-soul.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DAS_GRACAS', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='RIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DAS_GRACAS')
        msh.date_time_of_message = '20250401082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250401082000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250009', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='628.193.475-88', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MENDES^CAROLINA^VIEIRA^^^SRA'
        pid.date_time_of_birth = '19950428'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA ALCIDES MUNHOZ', xad_2='433', xad_3='APT 302', xad_4='CURITIBA', xad_5='PR', xad_6='80060-220', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^991098765'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_RADIO', pl_2='SALA_RM', pl_4='HOSP_NOSSA_SENHORA_DAS_GRACAS')
        pv1.visit_number = CX(cx_1='PAC20250009', cx_4='MV_SOUL', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_PR')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='MENDES', cwe_2='CAROLINA', cwe_3='VIEIRA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19950428')
        in1.policy_deductible = CP(cp_1='0123456789012')

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
        orc.placer_order_number = EI(ei_1='ORD20250005', ei_2='MV_SOUL')
        orc.orc_7 = '^^^20250401082000^^R'
        orc.date_time_of_order_event = '20250401082000'
        orc.orc_10 = 'TEIXEIRA^ANDREA^CRISTINA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'PR'
        orc.orc_12 = '44444'
        orc.order_effective_date_time = '20250401082000'
        orc.orc_18 = 'HOSP_NOSSA_SENHORA_DAS_GRACAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250005', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='24590-2', cwe_2='MR Brain', cwe_3='LN')
        obr.observation_date_time = '20250401082000'
        obr.obr_16 = 'TEIXEIRA^ANDREA^CRISTINA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '44444'
        obr.filler_field_1 = 'RAD20250002'
        obr.parent_result = PRL(prl_1='RM')
        obr.parent_results_observation_identifier = EIP(eip_2='Cefaleia cronica refrataria')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G43.9', cwe_2='Enxaqueca nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
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
    """ Based on live/br/br-mv-soul.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SIRIO_LIBANES')
        msh.date_time_of_message = '20250403112000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250403112000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250403112000'
        evn.operator_id = XCN(xcn_1='MARTINS', xcn_2='CARLA', xcn_3='ROSA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250010', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='739.184.526-99', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SOUSA^GABRIEL^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19820314'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='RUA MINISTRO RAUL FERNANDES',
            xad_2='29',
            xad_3='APT 1502',
            xad_4='RIO DE JANEIRO',
            xad_5='RJ',
            xad_6='22260-040',
            xad_7='BR',
        )
        pid.pid_13 = '^PRN^PH^^55^21^990987654'
        pid.pid_14 = '^WPN^PH^^55^21^35678901'
        pid.marital_status = CWE(cwe_1='D')
        pid.patient_account_number = CX(cx_1='PAC20250010', cx_4='MV_SOUL', cx_5='AN')
        pid.multiple_birth_indicator = 'RIO DE JANEIRO^RJ^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7NORTE', pl_2='701', pl_3='A', pl_4='HOSP_SIRIO_LIBANES', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250401080000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SOUSA', xpn_2='PATRICIA', xpn_3='LIMA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^21^989876543'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_2='SULAMERICA SAUDE')
        in1.insurance_company_id = CX(cx_1='SULAM_RJ')
        in1.insurance_company_name = XON(xon_1='SULAMERICA COMPANHIA DE SEGUROS')
        in1.plan_type = CWE(cwe_1='SOUSA', cwe_2='GABRIEL', cwe_3='HENRIQUE')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19820314')
        in1.insureds_date_of_birth = 'RUA MINISTRO RAUL FERNANDES^29^APT 1502^RIO DE JANEIRO^RJ^22260-040'
        in1.policy_deductible = CP(cp_1='0234567890123')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/br/br-mv-soul.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_PORTUGUES_RECIFE', hd_2='5678', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_PORTUGUES_RECIFE')
        msh.date_time_of_message = '20250405091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250405091000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250011', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='841.295.367-44', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'ARAUJO^FERNANDA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19880921'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV CONDE DA BOA VISTA', xad_2='800', xad_3='APT 61', xad_4='RECIFE', xad_5='PE', xad_6='50060-004', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^988765432'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA3', pl_4='HOSP_PORTUGUES_RECIFE')
        pv1.visit_number = CX(cx_1='PAC20250011', cx_4='MV_SOUL', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD20250006', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250405091000^^R'
        orc.orc_10 = '20250405091000'
        orc.orc_11 = 'LIRA^PATRICIA^EMANUELE^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='55555')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250006', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinalysis complete panel', cwe_3='LN')
        obr.observation_date_time = '20250405070000'
        obr.obr_14 = '20250405070000'
        obr.obr_15 = 'URINE^Urina jato medio'
        obr.obr_16 = 'LIRA^PATRICIA^EMANUELE^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '55555'
        obr.filler_field_1 = 'LAB20250004'
        obr.charge_to_practice = MOC(moc_1='20250405091000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance of Urine', cwe_3='LN')
        obx.obx_5 = 'Amarelo claro'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH of Urine', cwe_3='LN')
        obx_2.obx_5 = '6.0'
        obx_2.reference_range = '5.0-8.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specific gravity of Urine', cwe_3='LN')
        obx_3.obx_5 = '1.020'
        obx_3.reference_range = '1.005-1.030'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Protein [Presence] in Urine', cwe_3='LN')
        obx_4.obx_5 = 'Negativo'
        obx_4.reference_range = 'Negativo'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='25428-4', cwe_2='Glucose [Presence] in Urine', cwe_3='LN')
        obx_5.obx_5 = 'Negativo'
        obx_5.reference_range = 'Negativo'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='5821-4', cwe_2='Leukocytes [#/area] in Urine sediment', cwe_3='LN')
        obx_6.obx_5 = '3'
        obx_6.units = CWE(cwe_1='/campo')
        obx_6.reference_range = '0-5'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250405091000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='13945-1', cwe_2='Erythrocytes [#/area] in Urine sediment', cwe_3='LN')
        obx_7.obx_5 = '1'
        obx_7.units = CWE(cwe_1='/campo')
        obx_7.reference_range = '0-3'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250405091000'

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
    """ Based on live/br/br-mv-soul.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_BIOCOR', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_BIOCOR')
        msh.date_time_of_message = '20250406160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20250406160000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250406160000'
        evn.operator_id = XCN(xcn_1='NUNES', xcn_2='RODRIGO', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250012', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='415.937.286-55', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GONCALVES^RICARDO^AUGUSTO^^^SR'
        pid.date_time_of_birth = '19600530'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV DO CONTORNO', xad_2='9530', xad_3='APT 81', xad_4='NOVA LIMA', xad_5='MG', xad_6='34000-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^987654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO5', pl_4='HOSP_BIOCOR', pl_8='UTI')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.bad_debt_recovery_amount = '4NORTE^402^A^HOSP_BIOCOR'
        pv1.discharged_to_location = DLD(dld_1='20250403120000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='POS OPERATORIO CIRURGIA CARDIACA')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Doenca aterosclerotica do coracao', cwe_3='I10')
        dg1.diagnosis_date_time = '20250403'
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
    """ Based on live/br/br-mv-soul.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_PROVIDENCIA', hd_2='7890', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_FLEURY')
        msh.receiving_facility = HD(hd_1='FLEURY_DF')
        msh.date_time_of_message = '20250408074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250408074500013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250013', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='328.147.539-66', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'VIEIRA^JULIANA^APARECIDA^^^SRA'
        pid.date_time_of_birth = '19770213'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='SQS 308 BLOCO C', xad_2='APT 405', xad_4='BRASILIA', xad_5='DF', xad_6='70355-030', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^61^986543210'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTE', pl_2='503', pl_3='A', pl_4='HOSP_PROVIDENCIA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='SUR', pl_2='Cirurgica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250406090000')

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
        orc.placer_order_number = EI(ei_1='ORD20250007', ei_2='MV_SOUL')
        orc.orc_7 = '^^^20250408074500^^R'
        orc.date_time_of_order_event = '20250408074500'
        orc.orc_10 = 'MOURA^ANTONIO^FERREIRA^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'DF'
        orc.orc_12 = '66666'
        orc.order_effective_date_time = '20250408074500'
        orc.orc_18 = 'HOSP_PROVIDENCIA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250007', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin time (PT)', cwe_3='LN')
        obr.observation_date_time = '20250408074500'
        obr.obr_16 = 'MOURA^ANTONIO^FERREIRA^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'DF'
        obr.placer_field_1 = '66666'
        obr.filler_field_1 = 'LAB20250005'
        obr.parent_result = PRL(prl_1='COAG')

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
        orc_2.placer_order_number = EI(ei_1='ORD20250008', ei_2='MV_SOUL')
        orc_2.orc_7 = '^^^20250408074500^^R'
        orc_2.date_time_of_order_event = '20250408074500'
        orc_2.orc_10 = 'MOURA^ANTONIO^FERREIRA^^^DR^^^^^^^^^CRM'
        orc_2.orc_11 = 'DF'
        orc_2.orc_12 = '66666'
        orc_2.order_effective_date_time = '20250408074500'
        orc_2.orc_18 = 'HOSP_PROVIDENCIA'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD20250008', ei_2='MV_SOUL')
        obr_2.universal_service_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT in Blood by Coagulation assay', cwe_3='LN')
        obr_2.observation_date_time = '20250408074500'
        obr_2.obr_16 = 'MOURA^ANTONIO^FERREIRA^^^DR^^^^^^^^^CRM'
        obr_2.obr_17 = 'DF'
        obr_2.placer_field_1 = '66666'
        obr_2.filler_field_1 = 'LAB20250006'
        obr_2.parent_result = PRL(prl_1='COAG')

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
    """ Based on live/br/br-mv-soul.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_VITA_VOLTA_REDONDA', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_VITA_VOLTA_REDONDA')
        msh.date_time_of_message = '20250409053000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250409053000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250014', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='573.918.426-77', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MACHADO^FERNANDO^LUIZ^^^SR'
        pid.date_time_of_birth = '19550820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV BARAO DO RIO BRANCO', xad_2='980', xad_3='APT 42', xad_4='FORTALEZA', xad_5='CE', xad_6='60025-061', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^85^985432109'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO8', pl_4='HOSP_VITA_VOLTA_REDONDA', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250407180000')

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
        orc.placer_order_number = EI(ei_1='ORD20250009', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250409053000^^R'
        orc.orc_10 = '20250409053000'
        orc.orc_11 = 'CAMPOS^LUCIANA^TEODORA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'CE'
        orc.enterers_location = PL(pl_1='77777')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250009', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Gas panel - Arterial blood', cwe_3='LN')
        obr.observation_date_time = '20250409050000'
        obr.obr_14 = '20250409050000'
        obr.obr_15 = 'ABG^Sangue arterial'
        obr.obr_16 = 'CAMPOS^LUCIANA^TEODORA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'CE'
        obr.placer_field_1 = '77777'
        obr.filler_field_1 = 'LAB20250007'
        obr.charge_to_practice = MOC(moc_1='20250409053000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH of Arterial blood', cwe_3='LN')
        obx.obx_5 = '7.38'
        obx.reference_range = '7.35-7.45'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250409053000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2 Arterial blood', cwe_3='LN')
        obx_2.obx_5 = '40'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250409053000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2 Arterial blood', cwe_3='LN')
        obx_3.obx_5 = '92'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250409053000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate [Moles/volume] in Arterial blood', cwe_3='LN')
        obx_4.obx_5 = '24'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '22-26'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250409053000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2713-6', cwe_2='Base excess in Arterial blood', cwe_3='LN')
        obx_5.obx_5 = '-0.5'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250409053000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='20564-1', cwe_2='Oxygen saturation in Arterial blood', cwe_3='LN')
        obx_6.obx_5 = '97'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250409053000'

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
    """ Based on live/br/br-mv-soul.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS_DE_VENTO', hd_2='5678', hd_3='DNS')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='HOSP_MOINHOS_DE_VENTO')
        msh.date_time_of_message = '20250410100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'MSG20250410100000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250410100000'
        evn.operator_id = XCN(xcn_1='ROCHA', xcn_2='AMANDA', xcn_3='FERREIRA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='PAC20250015', cx_4='MV_SOUL', cx_5='MR'),
            CX(cx_1='698.247.351-88', cx_4='BRASIL', cx_5='CPF'),
            CX(cx_1='12345678901', cx_4='BRASIL', cx_5='CNS'),
        ]
        pid.pid_5 = 'CASTRO^RENATA^MARIA^^^SRA'
        pid.date_time_of_birth = '20000115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA RAMIRO BARCELOS', xad_2='910', xad_3='APT 203', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90035-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^984321098'
        pid.pid_14 = '^NET^Internet^^renata.castro@email.com.br'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='PAC20250015', cx_4='MV_SOUL', cx_5='AN')
        pid.multiple_birth_indicator = 'PORTO ALEGRE^RS^BR'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'OLIVEIRA^MARCIA^EDUARDA^^^DRA^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='RS')
        pd1.handicap = CWE(cwe_1='88888')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CASTRO', xpn_2='JORGE', xpn_3='LUIS')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Pai', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^51^983210987'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PORTO ALEGRE')
        in1.insurance_company_id = CX(cx_1='UNIMED_RS')
        in1.insurance_company_name = XON(xon_1='UNIMED PORTO ALEGRE')
        in1.plan_type = CWE(cwe_1='CASTRO', cwe_2='JORGE', cwe_3='LUIS')
        in1.name_of_insured = XPN(xpn_1='DEP', xpn_2='Dependente')
        in1.insureds_relationship_to_patient = CWE(cwe_1='20000115')
        in1.insureds_date_of_birth = 'RUA RAMIRO BARCELOS^910^APT 203^PORTO ALEGRE^RS^90035-001'
        in1.policy_deductible = CP(cp_1='0067890123456')

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
    """ Based on live/br/br-mv-soul.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_BANDEIRANTES', hd_2='2345', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PACS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BANDEIRANTES')
        msh.date_time_of_message = '20250412143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250412143000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250016', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='712.853.469-99', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PEREIRA^ANDRE^LUIS^^^SR'
        pid.date_time_of_birth = '19680425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA MARIA ANTONIA', xad_2='890', xad_3='APT 12', xad_4='GOIANIA', xad_5='GO', xad_6='74085-090', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^62^983109876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_RX', pl_4='HOSP_BANDEIRANTES')
        pv1.visit_number = CX(cx_1='PAC20250016', cx_4='MV_SOUL', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD20250010', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250412143000^^R'
        orc.orc_10 = '20250412143000'
        orc.orc_11 = 'ALENCAR^MARCOS^VINICIUS^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'GO'
        orc.enterers_location = PL(pl_1='99999')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250010', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='XR Chest 2 Views', cwe_3='LN')
        obr.observation_date_time = '20250412130000'
        obr.obr_14 = '20250412130000'
        obr.obr_15 = 'CHEST^Torax PA e perfil'
        obr.obr_16 = 'ALENCAR^MARCOS^VINICIUS^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'GO'
        obr.placer_field_1 = '99999'
        obr.filler_field_1 = 'RAD20250003'
        obr.charge_to_practice = MOC(moc_1='20250412143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='Radiografia Torax PA', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'MV_SOUL^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNtcwIQAABtbnRyUkdCIFhZWiAH4gADABMAEgAxADFhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAA9tYAAQAAAADTLWxjbXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACWRlc2MAAADwAAAAJGNwcnQAAAEUAAAAJGRlc2MAAAAAAAAAABxzUkdC'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx_2.obx_5 = 'Campos pulmonares sem alteracoes. Area cardiaca dentro dos limites da normalidade. Seios costofrenicos livres.'
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
    """ Based on live/br/br-mv-soul.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_PIO_XII', hd_2='7890', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PIO_XII')
        msh.date_time_of_message = '20250414091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A13')
        msh.message_control_id = 'MSG20250414091500017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250414091500'
        evn.operator_id = XCN(xcn_1='FERREIRA', xcn_2='ROBERTO', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250017', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='836.519.247-00', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DIAS^MARCOS^VINICIUS^^^SR'
        pid.date_time_of_birth = '19720808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA SARAIVA', xad_2='1234', xad_3='CASA', xad_4='MANAUS', xad_5='AM', xad_6='69010-080', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^982098765'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3SUL', pl_2='305', pl_3='A', pl_4='HOSP_PIO_XII', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250410120000')
        pv1.pending_location = PL(pl_1='20250414080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='PIORA CLINICA APOS ALTA - RETORNO A INTERNACAO')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N17.9', cwe_2='Insuficiencia renal aguda nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250414'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Insuficiencia cardiaca nao especificada', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250410'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/br/br-mv-soul.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_DOR_DA_BARRA', hd_2='3456', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_MICRO')
        msh.receiving_facility = HD(hd_1='HOSP_DOR_DA_BARRA')
        msh.date_time_of_message = '20250415220000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250415220000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250018', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='459.832.671-11', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CUNHA^PATRICIA^RODRIGUES^^^SRA'
        pid.date_time_of_birth = '19830622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV LUCIO COSTA', xad_2='4900', xad_3='APT 93', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22630-011', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^981987654'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='PS', pl_2='SALA_OBS', pl_4='HOSP_DOR_DA_BARRA', pl_8='OBSERVACAO')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250415213000')

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
        orc.placer_order_number = EI(ei_1='ORD20250011', ei_2='MV_SOUL')
        orc.orc_7 = '^^^20250415220000^^S'
        orc.date_time_of_order_event = '20250415220000'
        orc.orc_10 = 'MAGALHAES^DANIEL^FERNANDO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'RJ'
        orc.orc_12 = '10101'
        orc.order_effective_date_time = '20250415220000'
        orc.orc_18 = 'HOSP_DOR_DA_BARRA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250011', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Blood culture', cwe_3='LN')
        obr.observation_date_time = '20250415220000'
        obr.obr_16 = 'MAGALHAES^DANIEL^FERNANDO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'RJ'
        obr.placer_field_1 = '10101'
        obr.filler_field_1 = 'LAB20250008'
        obr.parent_result = PRL(prl_1='MICRO')
        obr.parent_results_observation_identifier = EIP(eip_2='Febre persistente ha 48h sem foco definido')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R50.9', cwe_2='Febre nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250415'
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
    """ Based on live/br/br-mv-soul.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_INCOR_RP', hd_2='1234', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_INCOR_RP')
        msh.date_time_of_message = '20250416041500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250416041500019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250019', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='628.314.957-22', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CARVALHO^JOSE^ROBERTO^^^SR'
        pid.date_time_of_birth = '19580110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV NOVE DE JULHO', xad_2='4500', xad_3='APT 2001', xad_4='RIBEIRAO PRETO', xad_5='SP', xad_6='14025-310', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^16^980876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='PS', pl_2='SALA_VERMELHA', pl_4='HOSP_INCOR_RP', pl_8='EMERGENCIA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250416030000')

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
        orc.placer_order_number = EI(ei_1='ORD20250012', ei_2='MV_SOUL')
        orc.orc_8 = '^^^20250416041500^^R'
        orc.orc_10 = '20250416041500'
        orc.orc_11 = 'MELO^MARCELO^TADEU^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'SP'
        orc.enterers_location = PL(pl_1='12121')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250012', ei_2='MV_SOUL')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Cardiac biomarkers panel', cwe_3='LN')
        obr.observation_date_time = '20250416031000'
        obr.obr_14 = '20250416031000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'MELO^MARCELO^TADEU^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '12121'
        obr.filler_field_1 = 'LAB20250009'
        obr.charge_to_practice = MOC(moc_1='20250416041500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '0.85'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250416041500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33959-8', cwe_2='Prothrombin time (PT) in Platelet poor plasma by Coagulation assay', cwe_3='LN')
        obx_2.obx_5 = '780'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '30-200'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250416041500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='30522-7', cwe_2='CK-MB [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '45.2'
        obx_3.units = CWE(cwe_1='ng/mL')
        obx_3.reference_range = '0.0-5.0'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250416041500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='42757-5', cwe_2='D-Dimer DDU [Mass/volume] in Platelet poor plasma', cwe_3='LN')
        obx_4.obx_5 = '0.35'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.reference_range = '0.00-0.50'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250416041500'

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
    """ Based on live/br/br-mv-soul.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MV_SOUL')
        msh.sending_facility = HD(hd_1='HOSP_NOVE_DE_JULHO', hd_2='5678', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_NOVE_DE_JULHO')
        msh.date_time_of_message = '20250418153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A11')
        msh.message_control_id = 'MSG20250418153000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20250418153000'
        evn.operator_id = XCN(xcn_1='TORRES', xcn_2='LUCIA', xcn_3='CRISTINA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC20250020', cx_4='MV_SOUL', cx_5='MR'), CX(cx_1='736.219.485-40', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'XAVIER^PRISCILA^SANTOS^^^SRA'
        pid.date_time_of_birth = '19930307'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA JOAQUIM FLORIANO', xad_2='466', xad_3='APT 44', xad_4='SAO PAULO', xad_5='SP', xad_6='04534-002', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^979765432'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_DERMA', pl_2='CONS2', pl_4='HOSP_NOVE_DE_JULHO')
        pv1.temporary_location = PL(pl_1='DER', pl_2='Dermatologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250418143000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='PACIENTE NAO COMPARECEU A CONSULTA')

        # .. assemble the full message ..
        msg = ADT_A09()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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

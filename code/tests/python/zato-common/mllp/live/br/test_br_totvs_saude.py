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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Insurance, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, \
    RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXE, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-totvs-saude.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-totvs-saude.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA_BH', hd_2='5001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CASA_BH')
        msh.date_time_of_message = '20250310142000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TOTVS20250310142001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250310142000'
        evn.operator_id = XCN(xcn_1='SOUZA', xcn_2='MARIANA', xcn_3='ENFERMEIRA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250001', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'FERREIRA^ANTONIO^JOSE^^^SR'
        pid.date_time_of_birth = '19720315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA DA BAHIA', xad_2='1234', xad_3='LOJA 3', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30160-011', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^999112233'
        pid.pid_14 = '^WPN^PH^^55^31^32114455'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='TVP20250001', cx_4='TOTVS_RM', cx_5='AN')
        pid.multiple_birth_indicator = 'BELO HORIZONTE^MG^BR'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'LIMA^CARLOS^EDUARDO^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='MG')
        pd1.handicap = CWE(cwe_1='40001')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='FERREIRA', xpn_2='LUCIA', xpn_3='MARIANA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^31^998001122'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='PS', pl_2='SALA_VERMELHA', pl_4='HOSP_SANTA_CASA_BH', pl_8='EMERGENCIA')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250310142000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='FERREIRA', aui_2='ANTONIO', aui_3='JOSE')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19720315')
        in1.policy_number = '7021234567890123'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Acidente vascular cerebral nao especificado como hemorragico ou isquemico', cwe_3='I10')
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
    """ Based on live/br/br-totvs-saude.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SAO_LUCAS', hd_2='5002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_LUCAS')
        msh.date_time_of_message = '20250318110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'TOTVS20250318110002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250318110000'
        evn.operator_id = XCN(xcn_1='ANDRADE', xcn_2='PAULO', xcn_3='HENRIQUE')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250002', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='582.471.396-15', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CORREIA^JOANA^ALMEIDA^^^SRA'
        pid.date_time_of_birth = '19850720'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV IPIRANGA', xad_2='6500', xad_3='APT 1201', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90619-900', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^997889900'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3NORTE', pl_2='305', pl_3='A', pl_4='HOSP_SAO_LUCAS', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='ORT', pl_2='Ortopedia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250312090000'
        pv1.discharge_date_time = '20250318110000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.visit_description = '5'
        pv2.visit_publicity_code = CWE(cwe_1='AI')
        pv2.billing_media_code = '20250325'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PORTO ALEGRE')
        in1.insurance_company_id = CX(cx_1='UNIMED_RS')
        in1.insurance_company_name = XON(xon_1='UNIMED PORTO ALEGRE')
        in1.plan_type = CWE(cwe_1='CORREIA', cwe_2='JOANA', cwe_3='ALMEIDA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19850720')
        in1.insureds_date_of_birth = 'AV IPIRANGA^6500^APT 1201^PORTO ALEGRE^RS^90619-900'
        in1.policy_deductible = CP(cp_1='0090123456789')

        # .. build the INSURANCE group ..
        insurance = AdtA03Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.0', cwe_2='Fratura do colo do femur', cwe_3='I10')
        dg1.diagnosis_date_time = '20250312'
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
    """ Based on live/br/br-totvs-saude.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='5003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_FLEURY')
        msh.receiving_facility = HD(hd_1='FLEURY_SP')
        msh.date_time_of_message = '20250320063000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TOTVS20250320063003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250003', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='639.785.241-26', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'OLIVEIRA^MARCOS^VINICIUS^^^SR'
        pid.date_time_of_birth = '19680514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA OSCAR FREIRE', xad_2='1250', xad_3='APT 802', xad_4='SAO PAULO', xad_5='SP', xad_6='01426-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA1', pl_4='HOSP_SIRIO_LIBANES')
        pv1.visit_number = CX(cx_1='TVP20250003', cx_4='TOTVS_RM', cx_5='VN')
        pv1.admit_date_time = '20250320063000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_SP')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='OLIVEIRA', cwe_2='MARCOS', cwe_3='VINICIUS')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19680514')
        in1.policy_deductible = CP(cp_1='0101234567890')

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
        orc.placer_order_number = EI(ei_1='TVORD20250001', ei_2='TOTVS_RM')
        orc.orc_7 = '^^^20250320063000^^R'
        orc.date_time_of_order_event = '20250320063000'
        orc.orc_10 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'SP'
        orc.orc_12 = '50001'
        orc.order_effective_date_time = '20250320063000'
        orc.orc_18 = 'HOSP_SIRIO_LIBANES'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250001', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250320063000'
        obr.obr_16 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'TVLAB20250001'
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
        orc_2.placer_order_number = EI(ei_1='TVORD20250002', ei_2='TOTVS_RM')
        orc_2.orc_7 = '^^^20250320063000^^R'
        orc_2.date_time_of_order_event = '20250320063000'
        orc_2.orc_10 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        orc_2.orc_11 = 'SP'
        orc_2.orc_12 = '50001'
        orc_2.order_effective_date_time = '20250320063000'
        orc_2.orc_18 = 'HOSP_SIRIO_LIBANES'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='TVORD20250002', ei_2='TOTVS_RM')
        obr_2.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin time (PT)', cwe_3='LN')
        obr_2.observation_date_time = '20250320063000'
        obr_2.obr_16 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        obr_2.obr_17 = 'SP'
        obr_2.placer_field_1 = '50001'
        obr_2.filler_field_1 = 'TVLAB20250002'
        obr_2.parent_result = PRL(prl_1='COAG')

        # .. build the ORDER_DETAIL group ..
        order_detail_2 = OrmO01OrderDetail()
        order_detail_2.obr = obr_2

        # .. build the ORDER group ..
        order_2 = OrmO01Order()
        order_2.orc = orc_2
        order_2.order_detail = order_detail_2

        # .. build ORC ..
        orc_3 = ORC()
        orc_3.order_control = 'NW'
        orc_3.placer_order_number = EI(ei_1='TVORD20250003', ei_2='TOTVS_RM')
        orc_3.orc_7 = '^^^20250320063000^^R'
        orc_3.date_time_of_order_event = '20250320063000'
        orc_3.orc_10 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        orc_3.orc_11 = 'SP'
        orc_3.orc_12 = '50001'
        orc_3.order_effective_date_time = '20250320063000'
        orc_3.orc_18 = 'HOSP_SIRIO_LIBANES'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='TVORD20250003', ei_2='TOTVS_RM')
        obr_3.universal_service_identifier = CWE(cwe_1='24321-2', cwe_2='Basic metabolic panel - Serum or Plasma', cwe_3='LN')
        obr_3.observation_date_time = '20250320063000'
        obr_3.obr_16 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        obr_3.obr_17 = 'SP'
        obr_3.placer_field_1 = '50001'
        obr_3.filler_field_1 = 'TVLAB20250003'
        obr_3.parent_result = PRL(prl_1='BIO')

        # .. build the ORDER_DETAIL group ..
        order_detail_3 = OrmO01OrderDetail()
        order_detail_3.obr = obr_3

        # .. build the ORDER group ..
        order_3 = OrmO01Order()
        order_3.orc = orc_3
        order_3.order_detail = order_detail_3

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2, order_3]

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
    """ Based on live/br/br-totvs-saude.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='5003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_SIRIO_LIBANES')
        msh.date_time_of_message = '20250320143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250320143004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250003', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='639.785.241-26', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'OLIVEIRA^MARCOS^VINICIUS^^^SR'
        pid.date_time_of_birth = '19680514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA OSCAR FREIRE', xad_2='1250', xad_3='APT 802', xad_4='SAO PAULO', xad_5='SP', xad_6='01426-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA1', pl_4='HOSP_SIRIO_LIBANES')
        pv1.visit_number = CX(cx_1='TVP20250003', cx_4='TOTVS_RM', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TVORD20250001', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250320143000^^R'
        orc.orc_10 = '20250320143000'
        orc.orc_11 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'SP'
        orc.enterers_location = PL(pl_1='50001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250001', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250320063000'
        obr.obr_14 = '20250320063000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'PEREIRA^FLAVIO^ANTONIO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'TVLAB20250001'
        obr.charge_to_practice = MOC(moc_1='20250320143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '8.1'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-11.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes [#/volume] in Blood', cwe_3='LN')
        obx_2.obx_5 = '4.8'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.5-5.9'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx_3.obx_5 = '14.2'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '13.0-17.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit [Volume Fraction] of Blood', cwe_3='LN')
        obx_4.obx_5 = '42.5'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '38.0-52.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320143000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets [#/volume] in Blood', cwe_3='LN')
        obx_5.obx_5 = '210'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320143000'

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
    """ Based on live/br/br-totvs-saude.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SAO_LUCAS', hd_2='5002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CENTRO_CIRURGICO')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_LUCAS')
        msh.date_time_of_message = '20250322100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'TOTVS20250322100005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TVAGD20250001', ei_2='TOTVS_RM')
        sch.appointment_reason = CWE(cwe_1='CIRURGIA', cwe_2='Cirurgia Eletiva')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='120')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250401070000', xcn_5='20250401090000')
        sch.sch_13 = 'MOREIRA^RODRIGO^FELIPE^^^DR^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='RS')
        sch.placer_contact_location = PL(pl_1='60001')
        sch.sch_17 = 'MOREIRA^RODRIGO^FELIPE^^^DR^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='RS')
        sch.filler_contact_location = PL(pl_1='60001')
        sch.parent_filler_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250004', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CAMPOS^RENATO^AUGUSTO^^^SR'
        pid.date_time_of_birth = '19550928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA SARMENTO LEITE', xad_2='800', xad_3='APT 301', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90050-170', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^995667788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CC', pl_2='SALA5', pl_4='HOSP_SAO_LUCAS')
        pv1.temporary_location = PL(pl_1='SUR', pl_2='Cirurgica', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='CC_SALA5', cwe_2='Sala Cirurgica 5', cwe_3='TOTVS_RM')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='ATQ', cwe_2='Artroplastia total de quadril', cwe_3='TOTVS_RM')
        ais.start_date_time = '20250401070000'
        ais.duration = '120'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='MOREIRA', cwe_2='RODRIGO', cwe_3='FELIPE', cwe_6='DR', cwe_15='CRM')
        aig.resource_type = CWE(cwe_1='RS')
        aig.resource_group = CWE(cwe_1='60001')
        aig.resource_quantity = 'CIRURGIAO^Cirurgiao Principal'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.general_resource = general_resource

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M16.1', cwe_2='Outras coxartroses primarias', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-totvs-saude.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_COPA_DOR', hd_2='5005', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_COPA_DOR')
        msh.date_time_of_message = '20250324080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'TOTVS20250324080006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250324080000'
        evn.operator_id = XCN(xcn_1='REIS', xcn_2='TATIANA', xcn_3='CRISTINA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250005', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='826.397.514-48', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'VARGAS^PATRICIA^FERNANDES^^^SRA'
        pid.date_time_of_birth = '19780302'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='RUA FIGUEIREDO MAGALHAES',
            xad_2='750',
            xad_3='APT 602',
            xad_4='RIO DE JANEIRO',
            xad_5='RJ',
            xad_6='22031-010',
            xad_7='BR',
        )
        pid.pid_13 = '^PRN^PH^^55^21^994556677'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_ENDO', pl_2='CONS1', pl_4='HOSP_COPA_DOR')
        pv1.temporary_location = PL(pl_1='END', pl_2='Endocrinologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250324080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_RJ')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='VARGAS', cwe_2='PATRICIA', cwe_3='FERNANDES')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19780302')
        in1.policy_deductible = CP(cp_1='0212345678901')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus tipo 2 sem complicacoes', cwe_3='I10')
        dg1.diagnosis_date_time = '20250324'
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
    """ Based on live/br/br-totvs-saude.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_REAL_PORTUGUES', hd_2='5006', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PACS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_REAL_PORTUGUES')
        msh.date_time_of_message = '20250326110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250326110007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250006', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='937.518.624-59', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MENDONCA^ROSA^VALERIA^^^SRA'
        pid.date_time_of_birth = '19550612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA DA AURORA', xad_2='1500', xad_3='APT 201', xad_4='RECIFE', xad_5='PE', xad_6='50050-145', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^993445566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_DEXA', pl_4='HOSP_REAL_PORTUGUES')
        pv1.visit_number = CX(cx_1='TVP20250006', cx_4='TOTVS_RM', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TVORD20250004', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250326110000^^R'
        orc.orc_10 = '20250326110000'
        orc.orc_11 = 'RIBEIRO^CLAUDIA^MARIA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PE'
        orc.enterers_location = PL(pl_1='70001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250004', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='38263-0', cwe_2='DXA Bone density', cwe_3='LN')
        obr.observation_date_time = '20250326090000'
        obr.obr_14 = '20250326090000'
        obr.obr_15 = 'BONE^Coluna lombar e femur'
        obr.obr_16 = 'RIBEIRO^CLAUDIA^MARIA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'TVRAD20250001'
        obr.charge_to_practice = MOC(moc_1='20250326110000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='46278-8', cwe_2='DXA Bone density L1-L4', cwe_3='LN')
        obx.obx_5 = '-2.3'
        obx.units = CWE(cwe_1='T-score')
        obx.reference_range = '>-1.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250326110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='46279-6', cwe_2='DXA Bone density Femoral neck', cwe_3='LN')
        obx_2.obx_5 = '-1.8'
        obx_2.units = CWE(cwe_1='T-score')
        obx_2.reference_range = '>-1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250326110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo Densitometria Ossea', cwe_3='AUSPDI')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'TOTVS_RM^AP^^Base64^'
            'JVBERi0xLjcKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgMTAgMCBSPj4+Pj4+CmVuZG9iagolTGF1ZG8gRGVuc2l0b21ldHJpYSBPc3NlYQ=='
        )
        obx_3.observation_result_status = 'F'

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
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M81.0', cwe_2='Osteoporose pos-menopausica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250326'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-totvs-saude.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_BASE_BRASILIA', hd_2='5007', hd_3='DNS')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_BASE_BRASILIA')
        msh.date_time_of_message = '20250327160000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'TOTVS20250327160008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250007', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='063.527.918-50', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'BARROS^JOSE^CARLOS^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='SQS 308 BLOCO C', xad_2='APT 503', xad_4='BRASILIA', xad_5='DF', xad_6='70354-070', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^61^992334455'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4SUL', pl_2='405', pl_3='B', pl_4='HOSP_BASE_BRASILIA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250325140000')

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
        orc.placer_order_number = EI(ei_1='TVPRESC20250001', ei_2='TOTVS_RM')
        orc.orc_7 = '^^^20250327160000^^R'
        orc.date_time_of_order_event = '20250327160000'
        orc.orc_10 = 'XAVIER^CARLOS^EDUARDO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'DF'
        orc.orc_12 = '40001'
        orc.order_effective_date_time = '20250327160000'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20250327180000^^R'
        rxe.give_code = CWE(cwe_1='10309-3001', cwe_2='Insulina NPH 100UI/mL', cwe_3='ANVISA')
        rxe.give_amount_maximum = '20'
        rxe.give_units = CWE(cwe_1='UI', cwe_3='HL70292')
        rxe.give_per_time_unit = '2'
        rxe.give_rate_units = CWE(cwe_1='SC', cwe_2='Subcutaneo', cwe_3='HL70162')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='SC', cwe_2='Subcutaneo', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='ABD', cwe_2='Abdomen', cwe_3='HL70163')

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
    """ Based on live/br/br-totvs-saude.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SAO_VICENTE', hd_2='5008', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CARDIO_SISTEMA')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_VICENTE')
        msh.date_time_of_message = '20250329083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TOTVS20250329083009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250008', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='174.638.295-61', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MAGALHAES^FLAVIA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA COMENDADOR ARAUJO', xad_2='432', xad_3='APT 501', xad_4='CURITIBA', xad_5='PR', xad_6='80420-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^991223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='SALA_ECG', pl_4='HOSP_SAO_VICENTE')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250329083000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_2='SULAMERICA SAUDE')
        in1.insurance_company_id = CX(cx_1='SULAM_PR')
        in1.insurance_company_name = XON(xon_1='SULAMERICA COMPANHIA DE SEGUROS')
        in1.plan_type = CWE(cwe_1='MAGALHAES', cwe_2='FLAVIA', cwe_3='CRISTINA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19700425')
        in1.policy_deductible = CP(cp_1='0323456789012')

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
        orc.placer_order_number = EI(ei_1='TVORD20250005', ei_2='TOTVS_RM')
        orc.orc_7 = '^^^20250329083000^^R'
        orc.date_time_of_order_event = '20250329083000'
        orc.orc_10 = 'CASTRO^ANDERSON^LUIZ^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'PR'
        orc.orc_12 = '80001'
        orc.order_effective_date_time = '20250329083000'
        orc.orc_18 = 'HOSP_SAO_VICENTE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250005', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='11524-6', cwe_2='ECG study', cwe_3='LN')
        obr.observation_date_time = '20250329083000'
        obr.obr_16 = 'CASTRO^ANDERSON^LUIZ^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '80001'
        obr.filler_field_1 = 'TVCARDIO20250001'
        obr.parent_result = PRL(prl_1='ECG')
        obr.parent_results_observation_identifier = EIP(eip_2='Dor toracica atipica')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Dor toracica nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250329'
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
    """ Based on live/br/br-totvs-saude.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_PORTUGUES_BA', hd_2='5009', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_PORTUGUES_BA')
        msh.date_time_of_message = '20250331094500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250331094510'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250009', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='285.749.306-72', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'TEIXEIRA^ROBERTO^MENDES^^^SR'
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV SETE DE SETEMBRO', xad_2='2200', xad_3='APT 802', xad_4='SALVADOR', xad_5='BA', xad_6='40080-002', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^990112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTE', pl_2='510', pl_3='A', pl_4='HOSP_PORTUGUES_BA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='NEF', pl_2='Nefrologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250328100000')

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
        orc.placer_order_number = EI(ei_1='TVORD20250006', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250331094500^^R'
        orc.orc_10 = '20250331094500'
        orc.orc_11 = 'FERRAZ^LUCIANA^MARIA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'BA'
        orc.enterers_location = PL(pl_1='90001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250006', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='Renal function panel', cwe_3='LN')
        obr.observation_date_time = '20250331060000'
        obr.obr_14 = '20250331060000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'FERRAZ^LUCIANA^MARIA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'BA'
        obr.placer_field_1 = '90001'
        obr.filler_field_1 = 'TVLAB20250004'
        obr.charge_to_practice = MOC(moc_1='20250331094500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '0.7-1.3'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250331094500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea nitrogen [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '68'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '7-20'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250331094500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR CKD-EPI', cwe_3='LN')
        obx_3.obx_5 = '22'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250331094500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '5.8'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '3.5-5.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250331094500'

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
    """ Based on live/br/br-totvs-saude.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_PORTUGUES_BA', hd_2='5009', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PORTUGUES_BA')
        msh.date_time_of_message = '20250331120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'TOTVS20250331120011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250331120000'
        evn.operator_id = XCN(xcn_1='GOMES', xcn_2='RAFAEL', xcn_3='EDUARDO')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250009', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='285.749.306-72', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'TEIXEIRA^ROBERTO^MENDES^^^SR'
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV SETE DE SETEMBRO', xad_2='2200', xad_3='APT 802', xad_4='SALVADOR', xad_5='BA', xad_6='40080-002', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^990112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI_NEF', pl_2='LEITO3', pl_4='HOSP_PORTUGUES_BA', pl_8='UTI')
        pv1.hospital_service = CWE(cwe_1='NEF', cwe_2='Nefrologia', cwe_3='HL70069')
        pv1.bad_debt_recovery_amount = '5NORTE^510^A^HOSP_PORTUGUES_BA'
        pv1.discharged_to_location = DLD(dld_1='20250328100000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='PIORA DA FUNCAO RENAL - INDICACAO DE HEMODIALISE DE URGENCIA')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N17.0', cwe_2='Insuficiencia renal aguda com necrose tubular', cwe_3='I10')
        dg1.diagnosis_date_time = '20250331'
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
    """ Based on live/br/br-totvs-saude.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_GETULIO_VARGAS', hd_2='5010', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_GETULIO_VARGAS')
        msh.date_time_of_message = '20250402210000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TOTVS20250402210012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250010', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='396.851.247-83', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'NUNES^ADRIANA^FONTES^^^SRA'
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV EDUARDO RIBEIRO', xad_2='800', xad_3='APT 1101', xad_4='MANAUS', xad_5='AM', xad_6='69010-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^989001122'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='PS', pl_2='SALA_AMARELA', pl_4='HOSP_GETULIO_VARGAS', pl_8='EMERGENCIA')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250402200000')

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
        orc.placer_order_number = EI(ei_1='TVORD20250007', ei_2='TOTVS_RM')
        orc.orc_7 = '^^^20250402210000^^S'
        orc.date_time_of_order_event = '20250402210000'
        orc.orc_10 = 'VIEIRA^ROBERTO^EDUARDO^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'AM'
        orc.orc_12 = '10101'
        orc.order_effective_date_time = '20250402210000'
        orc.orc_18 = 'HOSP_GETULIO_VARGAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250007', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='49581-4', cwe_2='CSF panel', cwe_3='LN')
        obr.observation_date_time = '20250402210000'
        obr.obr_16 = 'VIEIRA^ROBERTO^EDUARDO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '10101'
        obr.filler_field_1 = 'TVLAB20250005'
        obr.parent_result = PRL(prl_1='LIQ')
        obr.parent_results_observation_identifier = EIP(eip_2='Suspeita de meningite bacteriana - febre alta e rigidez de nuca')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G03.9', cwe_2='Meningite nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250402'
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
    """ Based on live/br/br-totvs-saude.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_GETULIO_VARGAS', hd_2='5010', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_GETULIO_VARGAS')
        msh.date_time_of_message = '20250403081500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250403081513'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250010', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='396.851.247-83', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'NUNES^ADRIANA^FONTES^^^SRA'
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV EDUARDO RIBEIRO', xad_2='800', xad_3='APT 1101', xad_4='MANAUS', xad_5='AM', xad_6='69010-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^989001122'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='PS', pl_2='SALA_AMARELA', pl_4='HOSP_GETULIO_VARGAS', pl_8='EMERGENCIA')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250402200000')

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
        orc.placer_order_number = EI(ei_1='TVORD20250007', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250403081500^^R'
        orc.orc_10 = '20250403081500'
        orc.orc_11 = 'VIEIRA^ROBERTO^EDUARDO^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'AM'
        orc.enterers_location = PL(pl_1='10101')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250007', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='49581-4', cwe_2='CSF panel', cwe_3='LN')
        obr.observation_date_time = '20250402210000'
        obr.obr_14 = '20250402210000'
        obr.obr_15 = 'CSF^Liquor cefalorraquidiano'
        obr.obr_16 = 'VIEIRA^ROBERTO^EDUARDO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'AM'
        obr.placer_field_1 = '10101'
        obr.filler_field_1 = 'TVLAB20250005'
        obr.charge_to_practice = MOC(moc_1='20250403081500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='26450-7', cwe_2='Leukocytes [#/volume] in CSF', cwe_3='LN')
        obx.obx_5 = '2500'
        obx.units = CWE(cwe_1='cells/uL')
        obx.reference_range = '0-5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250403081500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2342-4', cwe_2='Glucose [Mass/volume] in CSF', cwe_3='LN')
        obx_2.obx_5 = '25'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '40-70'
        obx_2.interpretation_codes = CWE(cwe_1='LL')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250403081500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2880-3', cwe_2='Protein [Mass/volume] in CSF', cwe_3='LN')
        obx_3.obx_5 = '320'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '15-45'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250403081500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obx_4.obx_5 = 'Diplococos Gram positivos aos pares'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250403081500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='IMG', cwe_2='Citologia Liquor Microscopia', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'TOTVS_RM^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYM'
            'CAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAL/8QAHRAAAQQDAQEA'
            'AAAAAAAAAAAABAIDBQYHABEhMf/aAAwDAQACEQMRAD8AZHlvc3RlcmVyIGxpcXVvciBtaWNyb3Njb3BpYQ=='
        )
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
    """ Based on live/br/br-totvs-saude.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_GETULIO_VARGAS', hd_2='5010', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_GETULIO_VARGAS')
        msh.date_time_of_message = '20250403120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'TOTVS20250403120014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250403120000'
        evn.operator_id = XCN(xcn_1='VIEIRA', xcn_2='ROBERTO', xcn_3='EDUARDO')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250010', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='396.851.247-83', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'NUNES^ADRIANA^FONTES^^^SRA'
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV EDUARDO RIBEIRO', xad_2='800', xad_3='APT 1101', xad_4='MANAUS', xad_5='AM', xad_6='69010-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^92^989001122'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='LEITO2', pl_4='HOSP_GETULIO_VARGAS', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250402200000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G00.1', cwe_2='Meningite pneumococica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250403'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='A40.3', cwe_2='Septicemia por Streptococcus pneumoniae', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250403'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/br/br-totvs-saude.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_BENEFICENCIA_PT', hd_2='5011', hd_3='DNS')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='HOSP_BENEFICENCIA_PT')
        msh.date_time_of_message = '20250404150000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S14')
        msh.message_control_id = 'TOTVS20250404150015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TVAGD20250002', ei_2='TOTVS_RM')
        sch.appointment_reason = CWE(cwe_1='CONSULTA', cwe_2='Consulta Medica')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='30')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250410090000', xcn_5='20250410093000')
        sch.sch_13 = 'TAVARES^ANDRE^LUIS^^^DR^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='GO')
        sch.placer_contact_location = PL(pl_1='80001')
        sch.sch_17 = 'TAVARES^ANDRE^LUIS^^^DR^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='GO')
        sch.filler_contact_location = PL(pl_1='80001')
        sch.parent_filler_appointment_id = EI(ei_1='CANCELLED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250011', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='407.962.358-94', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DUARTE^CELSO^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19630418'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA T-30', xad_2='1200', xad_3='APT 701', xad_4='GOIANIA', xad_5='GO', xad_6='74210-060', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^62^988990011'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='CONS1', pl_4='HOSP_BENEFICENCIA_PT')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient

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
    """ Based on live/br/br-totvs-saude.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_BAUDERER', hd_2='5012', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BAUDERER')
        msh.date_time_of_message = '20250406091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250406091016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250012', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='518.073.469-05', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'ARAUJO^TATIANA^GOMES^^^SRA'
        pid.date_time_of_birth = '19900303'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SETE', xad_2='800', xad_3='APT 203', xad_4='FORTALEZA', xad_5='CE', xad_6='60160-230', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^85^987889900'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_INFECTO', pl_2='CONS1', pl_4='HOSP_BAUDERER')
        pv1.temporary_location = PL(pl_1='INF', pl_2='Infectologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250406091000')

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
        orc.placer_order_number = EI(ei_1='TVORD20250008', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250406091000^^R'
        orc.orc_10 = '20250406091000'
        orc.orc_11 = 'MATIAS^MARCOS^FELIPE^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'CE'
        orc.enterers_location = PL(pl_1='11111')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250008', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='80383-3', cwe_2='Hepatitis panel', cwe_3='LN')
        obr.observation_date_time = '20250404070000'
        obr.obr_14 = '20250404070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'MATIAS^MARCOS^FELIPE^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'CE'
        obr.placer_field_1 = '11111'
        obr.filler_field_1 = 'TVLAB20250006'
        obr.charge_to_practice = MOC(moc_1='20250406091000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5196-1', cwe_2='HBsAg [Presence] in Serum', cwe_3='LN')
        obx.obx_5 = 'Nao reagente'
        obx.reference_range = 'Nao reagente'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250406091000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='16935-9', cwe_2='Anti-HBs [Units/volume] in Serum', cwe_3='LN')
        obx_2.obx_5 = 'Reagente (>100 mIU/mL)'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250406091000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5199-5', cwe_2='Anti-HCV [Presence] in Serum', cwe_3='LN')
        obx_3.obx_5 = 'Nao reagente'
        obx_3.reference_range = 'Nao reagente'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250406091000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='7918-6', cwe_2='HIV 1+2 Ab [Presence] in Serum', cwe_3='LN')
        obx_4.obx_5 = 'Nao reagente'
        obx_4.reference_range = 'Nao reagente'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250406091000'

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
    """ Based on live/br/br-totvs-saude.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_JULIANO_MOREIRA', hd_2='5013', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_JULIANO_MOREIRA')
        msh.date_time_of_message = '20250408023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TOTVS20250408023017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250408023000'
        evn.operator_id = XCN(xcn_1='MARTINS', xcn_2='PEDRO', xcn_3='FRANCISCO')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250013', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='629.184.570-16', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PINHEIRO^DANIEL^AUGUSTO^^^SR'
        pid.date_time_of_birth = '19850912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV EPITACIO PESSOA', xad_2='2400', xad_3='APT 201', xad_4='JOAO PESSOA', xad_5='PB', xad_6='58030-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^83^986778899'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PINHEIRO', xpn_2='MARIA', xpn_3='JOSEFINA')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mae', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^83^985667788'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PSIQ', pl_2='LEITO12', pl_4='HOSP_JULIANO_MOREIRA', pl_8='ENFERMARIA_PSIQ')
        pv1.hospital_service = CWE(cwe_1='PSI', cwe_2='Psiquiatria', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250408023000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='PINHEIRO', aui_2='DANIEL', aui_3='AUGUSTO')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19850912')
        in1.policy_number = '7031234567890456'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='F20.0', cwe_2='Esquizofrenia paranoide', cwe_3='I10')
        dg1.diagnosis_date_time = '20250408'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='F32.3', cwe_2='Episodio depressivo grave com sintomas psicoticos', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250408'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1, dg1_2]

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
    """ Based on live/br/br-totvs-saude.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_NOSSA_SENHORA_GLORIA', hd_2='5014', hd_3='DNS')
        msh.receiving_application = HD(hd_1='RIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_NOSSA_SENHORA_GLORIA')
        msh.date_time_of_message = '20250410074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TOTVS20250410074518'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250014', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='730.295.681-27', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'VASCONCELOS^MARCOS^AURELIO^^^SR'
        pid.date_time_of_birth = '19700707'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA LARANJEIRAS', xad_2='1200', xad_3='APT 901', xad_4='VITORIA', xad_5='ES', xad_6='29050-450', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^27^985556677'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_RM', pl_4='HOSP_NOSSA_SENHORA_GLORIA')
        pv1.visit_number = CX(cx_1='TVP20250014', cx_4='TOTVS_RM', cx_5='VN')
        pv1.admit_date_time = '20250410074500'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_ES')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='VASCONCELOS', cwe_2='MARCOS', cwe_3='AURELIO')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19700707')
        in1.policy_deductible = CP(cp_1='0434567890123')

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
        orc.placer_order_number = EI(ei_1='TVORD20250009', ei_2='TOTVS_RM')
        orc.orc_7 = '^^^20250410074500^^R'
        orc.date_time_of_order_event = '20250410074500'
        orc.orc_10 = 'FONSECA^RODRIGO^GABRIEL^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'ES'
        orc.orc_12 = '60001'
        orc.order_effective_date_time = '20250410074500'
        orc.orc_18 = 'HOSP_NOSSA_SENHORA_GLORIA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250009', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='24969-8', cwe_2='MR Lumbar spine', cwe_3='LN')
        obr.observation_date_time = '20250410074500'
        obr.obr_16 = 'FONSECA^RODRIGO^GABRIEL^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'ES'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'TVRAD20250002'
        obr.parent_result = PRL(prl_1='RM')
        obr.parent_results_observation_identifier = EIP(eip_2='Lombociatalgia cronica com irradiacao para MIE')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.4', cwe_2='Lumbago com ciatica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250410'
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
    """ Based on live/br/br-totvs-saude.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_SAO_VICENTE', hd_2='5008', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CARDIO_SISTEMA')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_VICENTE')
        msh.date_time_of_message = '20250411100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TOTVS20250411100019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250008', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='174.638.295-61', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MAGALHAES^FLAVIA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19700425'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA COMENDADOR ARAUJO', xad_2='432', xad_3='APT 501', xad_4='CURITIBA', xad_5='PR', xad_6='80420-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^991223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='SALA_ECG', pl_4='HOSP_SAO_VICENTE')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250411100000')

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
        orc.placer_order_number = EI(ei_1='TVORD20250005', ei_2='TOTVS_RM')
        orc.orc_8 = '^^^20250411100000^^R'
        orc.orc_10 = '20250411100000'
        orc.orc_11 = 'CASTRO^ANDERSON^LUIZ^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'PR'
        orc.enterers_location = PL(pl_1='80001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TVORD20250005', ei_2='TOTVS_RM')
        obr.universal_service_identifier = CWE(cwe_1='11524-6', cwe_2='ECG study', cwe_3='LN')
        obr.observation_date_time = '20250411093000'
        obr.obr_14 = '20250411093000'
        obr.obr_15 = 'CARDIAC^ECG 12 derivacoes'
        obr.obr_16 = 'CASTRO^ANDERSON^LUIZ^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '80001'
        obr.filler_field_1 = 'TVCARDIO20250001'
        obr.charge_to_practice = MOC(moc_1='20250411100000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='8601-7', cwe_2='ECG impression', cwe_3='LN')
        obx.obx_5 = 'Ritmo sinusal. FC 78bpm. Eixo normal. Sem alteracoes de repolarizacao. ECG dentro dos limites da normalidade.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250411100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Heart rate', cwe_3='LN')
        obx_2.obx_5 = '78'
        obx_2.units = CWE(cwe_1='bpm')
        obx_2.reference_range = '60-100'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250411100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8625-6', cwe_2='PR interval', cwe_3='LN')
        obx_3.obx_5 = '160'
        obx_3.units = CWE(cwe_1='ms')
        obx_3.reference_range = '120-200'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250411100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8633-0', cwe_2='QRS duration', cwe_3='LN')
        obx_4.obx_5 = '88'
        obx_4.units = CWE(cwe_1='ms')
        obx_4.reference_range = '60-100'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250411100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8634-8', cwe_2='QTc interval', cwe_3='LN')
        obx_5.obx_5 = '420'
        obx_5.units = CWE(cwe_1='ms')
        obx_5.reference_range = '350-440'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250411100000'

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
    """ Based on live/br/br-totvs-saude.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TOTVS_RM')
        msh.sending_facility = HD(hd_1='HOSP_PORTUGUES_BA', hd_2='5009', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PORTUGUES_BA')
        msh.date_time_of_message = '20250414060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'TOTVS20250414060020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250414060000'
        evn.operator_id = XCN(xcn_1='SOUZA', xcn_2='MARIANA', xcn_3='CRISTINA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TVP20250009', cx_4='TOTVS_RM', cx_5='MR'), CX(cx_1='285.749.306-72', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'TEIXEIRA^ROBERTO^MENDES^^^SR'
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV SETE DE SETEMBRO', xad_2='2200', xad_3='APT 802', xad_4='SALVADOR', xad_5='BA', xad_6='40080-002', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^990112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIALISE', pl_2='SALA_HD1', pl_4='HOSP_PORTUGUES_BA')
        pv1.temporary_location = PL(pl_1='NEF', pl_2='Nefrologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250414060000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='TEIXEIRA', aui_2='ROBERTO', aui_3='MENDES')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19750830')
        in1.policy_number = '7041234567890789'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.5', cwe_2='Doenca renal cronica estagio 5', cwe_3='I10')
        dg1.diagnosis_date_time = '20250414'
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

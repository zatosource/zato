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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, \
    RdeO11PatientVisit, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A06, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXE, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-philips-tasy.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-philips-tasy.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS_VENTO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_MOINHOS_VENTO')
        msh.date_time_of_message = '20250310060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TASY20250310060001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250310060000'
        evn.operator_id = XCN(xcn_1='BORGES', xcn_2='TATIANA', xcn_3='DA_CRUZ')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250001', cx_4='TASY', cx_5='MR'), CX(cx_1='478.193.625-01', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SILVA^MARCOS^ANTONIO^^^SR'
        pid.date_time_of_birth = '19650415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA PADRE CHAGAS', xad_2='300', xad_3='APT 501', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90570-080', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^999001122'
        pid.pid_14 = '^WPN^PH^^55^51^32001122'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='TP20250001', cx_4='TASY', cx_5='AN')
        pid.multiple_birth_indicator = 'PORTO ALEGRE^RS^BR'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'CARDOSO^ANDRE^MAURICIO^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='RS')
        pd1.handicap = CWE(cwe_1='20001')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SILVA', xpn_2='CLAUDIA', xpn_3='MARTINS')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^51^998877665'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO3', pl_3='A', pl_4='HOSP_MOINHOS_VENTO', pl_8='UTI')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250310060000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='SEPSE DE FOCO PULMONAR')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PORTO ALEGRE')
        in1.insurance_company_id = CX(cx_1='UNIMED_RS')
        in1.insurance_company_name = XON(xon_1='UNIMED PORTO ALEGRE')
        in1.plan_type = CWE(cwe_1='SILVA', cwe_2='MARCOS', cwe_3='ANTONIO')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19650415')
        in1.insureds_date_of_birth = 'RUA PADRE CHAGAS^300^APT 501^PORTO ALEGRE^RS^90570-080'
        in1.policy_deductible = CP(cp_1='0078901234567')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A41.9', cwe_2='Septicemia nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia nao especificada', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250310'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/br/br-philips-tasy.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BANDEIRANTES', hd_2='4002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_BANDEIRANTES')
        msh.date_time_of_message = '20250312180000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'TASY20250312180002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250312180000'
        evn.operator_id = XCN(xcn_1='RAMOS', xcn_2='PEDRO', xcn_3='GONCALVES')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250002', cx_4='TASY', cx_5='MR'), CX(cx_1='582.471.396-12', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MOREIRA^JOSE^ALVES^^^SR'
        pid.date_time_of_birth = '19400720'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV INDIANOPOLIS', xad_2='4500', xad_3='APT 301', xad_4='SAO PAULO', xad_5='SP', xad_6='04062-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^997766554'
        pid.primary_language = CWE(cwe_1='W')
        pid.religion = CWE(cwe_1='TP20250002', cwe_4='TASY', cwe_5='AN')
        pid.birth_place = 'SAO PAULO^SP^BR'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='20250312174500')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO7', pl_3='A', pl_4='HOSP_BANDEIRANTES', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.diet_type = CWE(cwe_1='20250305')
        pv1.servicing_facility = CWE(cwe_1='20250312180000')
        pv1.current_patient_balance = '20250312174500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.0', cwe_2='Infarto agudo do miocardio da parede anterior', cwe_3='I10')
        dg1.diagnosis_date_time = '20250305'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Insuficiencia cardiaca congestiva', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250310'
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
    """ Based on live/br/br-philips-tasy.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO', hd_2='4003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO')
        msh.date_time_of_message = '20250315071500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TASY20250315071503'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250003', cx_4='TASY', cx_5='MR'), CX(cx_1='639.785.241-23', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'RODRIGUES^ANA^PAULA^^^SRA'
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA TIMBIRAS', xad_2='1880', xad_3='CASA', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30140-064', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^996655443'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA1', pl_4='HOSP_BIOCOR_INSTITUTO')
        pv1.visit_number = CX(cx_1='TP20250003', cx_4='TASY', cx_5='VN')
        pv1.admit_date_time = '20250315071500'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='RODRIGUES', aui_2='ANA', aui_3='PAULA')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19750830')
        in1.policy_number = '7009876543210987'

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
        orc.placer_order_number = EI(ei_1='TORD20250001', ei_2='TASY')
        orc.orc_7 = '^^^20250315071500^^R'
        orc.date_time_of_order_event = '20250315071500'
        orc.orc_10 = 'FERNANDES^MARCOS^GABRIEL^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'MG'
        orc.orc_12 = '30001'
        orc.order_effective_date_time = '20250315071500'
        orc.orc_18 = 'HOSP_BIOCOR_INSTITUTO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250001', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250315071500'
        obr.obr_16 = 'FERNANDES^MARCOS^GABRIEL^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'MG'
        obr.placer_field_1 = '30001'
        obr.filler_field_1 = 'TLAB20250001'
        obr.parent_result = PRL(prl_1='BIO')

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
    """ Based on live/br/br-philips-tasy.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO', hd_2='4003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO')
        msh.date_time_of_message = '20250315141000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250315141004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250003', cx_4='TASY', cx_5='MR'), CX(cx_1='639.785.241-23', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'RODRIGUES^ANA^PAULA^^^SRA'
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA TIMBIRAS', xad_2='1880', xad_3='CASA', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30140-064', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^996655443'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA1', pl_4='HOSP_BIOCOR_INSTITUTO')
        pv1.visit_number = CX(cx_1='TP20250003', cx_4='TASY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TORD20250001', ei_2='TASY')
        orc.orc_8 = '^^^20250315141000^^R'
        orc.orc_10 = '20250315141000'
        orc.orc_11 = 'FERNANDES^MARCOS^GABRIEL^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'MG'
        orc.enterers_location = PL(pl_1='30001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250001', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250315071500'
        obr.obr_14 = '20250315071500'
        obr.obr_15 = 'BLOOD^Sangue venoso jejum 12h'
        obr.obr_16 = 'FERNANDES^MARCOS^GABRIEL^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'MG'
        obr.placer_field_1 = '30001'
        obr.filler_field_1 = 'TLAB20250001'
        obr.charge_to_practice = MOC(moc_1='20250315141000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '225'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250315141000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglyceride [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '180'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250315141000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250315141000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '147'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<130'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250315141000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='VLDL Cholesterol [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '36'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<30'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250315141000'

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
    """ Based on live/br/br-philips-tasy.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_AC_CAMARGO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PATOLOGIA')
        msh.receiving_facility = HD(hd_1='HOSP_AC_CAMARGO')
        msh.date_time_of_message = '20250318101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250318101505'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250004', cx_4='TASY', cx_5='MR'), CX(cx_1='715.286.039-34', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARTINS^CLAUDIA^REGINA^^^SRA'
        pid.date_time_of_birth = '19820112'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA HEITOR PENTEADO', xad_2='1234', xad_3='APT 702', xad_4='SAO PAULO', xad_5='SP', xad_6='05438-100', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^995544332'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATOLOGIA', pl_2='SALA1', pl_4='HOSP_AC_CAMARGO')
        pv1.visit_number = CX(cx_1='TP20250004', cx_4='TASY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TORD20250002', ei_2='TASY')
        orc.orc_8 = '^^^20250318101500^^R'
        orc.orc_10 = '20250318101500'
        orc.orc_11 = 'WERNECK^RENATO^DUARTE^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'SP'
        orc.enterers_location = PL(pl_1='40001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250002', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='65753-6', cwe_2='Surgical pathology study', cwe_3='LN')
        obr.observation_date_time = '20250314100000'
        obr.obr_14 = '20250314100000'
        obr.obr_15 = 'TISSUE^Tecido mamario'
        obr.obr_16 = 'WERNECK^RENATO^DUARTE^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '40001'
        obr.filler_field_1 = 'TPAT20250001'
        obr.charge_to_practice = MOC(moc_1='20250318101500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report final diagnosis', cwe_3='LN')
        obx.obx_5 = 'Carcinoma ductal invasivo grau II - margem livre'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250318101500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo Anatomopatologico Completo', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'TASY^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PiA+PgplbmRvYmoKMiAwIG9iago8PCAv'
            'VHlwZSAvUGFnZXMgL0tpZHMgWzMgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDIgMCBSIC9NZWRpYUJveCBbMCAwIDU5NSA4NDJd'
            'IC9Db250ZW50cyA0IDAgUiAvUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSAxMCAwIFI+Pj4+Pj4KZW5kb2JqCiVMYXVkbyBBbmF0b21vcGF0b2xvZ2ljbw=='
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

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C50.9', cwe_2='Neoplasia maligna da mama nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
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
    """ Based on live/br/br-philips-tasy.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_AC_CAMARGO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_AC_CAMARGO')
        msh.date_time_of_message = '20250320073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'TASY20250320073006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250320073000'
        evn.operator_id = XCN(xcn_1='LOPES', xcn_2='SIMONE', xcn_3='FERREIRA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250004', cx_4='TASY', cx_5='MR'), CX(cx_1='715.286.039-34', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARTINS^CLAUDIA^REGINA^^^SRA'
        pid.date_time_of_birth = '19820112'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA HEITOR PENTEADO', xad_2='1234', xad_3='APT 702', xad_4='SAO PAULO', xad_5='SP', xad_6='05438-100', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^995544332'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='SALA_QT1', pl_4='HOSP_AC_CAMARGO')
        pv1.temporary_location = PL(pl_1='ONC', pl_2='Oncologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250320073000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_SP')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='MARTINS', cwe_2='CLAUDIA', cwe_3='REGINA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19820112')
        in1.insureds_date_of_birth = 'RUA HEITOR PENTEADO^1234^APT 702^SAO PAULO^SP^05438-100'
        in1.policy_deductible = CP(cp_1='0034567890123')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C50.9', cwe_2='Neoplasia maligna da mama nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
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
    """ Based on live/br/br-philips-tasy.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_AC_CAMARGO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_AC_CAMARGO')
        msh.date_time_of_message = '20250320080000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'TASY20250320080007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250004', cx_4='TASY', cx_5='MR'), CX(cx_1='715.286.039-34', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARTINS^CLAUDIA^REGINA^^^SRA'
        pid.date_time_of_birth = '19820112'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA HEITOR PENTEADO', xad_2='1234', xad_3='APT 702', xad_4='SAO PAULO', xad_5='SP', xad_6='05438-100', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^995544332'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='SALA_QT1', pl_4='HOSP_AC_CAMARGO')
        pv1.temporary_location = PL(pl_1='ONC', pl_2='Oncologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250320073000')

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
        orc.placer_order_number = EI(ei_1='TPRESC20250001', ei_2='TASY')
        orc.orc_7 = '^^^20250320080000^^R'
        orc.date_time_of_order_event = '20250320080000'
        orc.orc_10 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'SP'
        orc.orc_12 = '50001'
        orc.order_effective_date_time = '20250320080000'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20250320090000^^R'
        rxe.give_code = CWE(cwe_1='10309-4001', cwe_2='Doxorrubicina 50mg', cwe_3='ANVISA')
        rxe.give_amount_maximum = '60'
        rxe.give_units = CWE(cwe_1='MG', cwe_3='HL70292')
        rxe.give_per_time_unit = '1'
        rxe.give_rate_units = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RA', cwe_2='Braco direito', cwe_3='HL70163')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='TPRESC20250002', ei_2='TASY')
        orc_2.orc_7 = '^^^20250320080000^^R'
        orc_2.date_time_of_order_event = '20250320080000'
        orc_2.orc_10 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        orc_2.orc_11 = 'SP'
        orc_2.orc_12 = '50001'
        orc_2.order_effective_date_time = '20250320080000'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20250320100000^^R'
        rxe_2.give_code = CWE(cwe_1='10309-5002', cwe_2='Ciclofosfamida 600mg', cwe_3='ANVISA')
        rxe_2.give_amount_maximum = '600'
        rxe_2.give_units = CWE(cwe_1='MG', cwe_3='HL70292')
        rxe_2.give_per_time_unit = '1'
        rxe_2.give_rate_units = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr_2.administration_site = CWE(cwe_1='RA', cwe_2='Braco direito', cwe_3='HL70163')

        # .. build the ORDER group ..
        order_2 = RdeO11Order()
        order_2.orc = orc_2
        order_2.rxe = rxe_2
        order_2.rxr = rxr_2

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/br/br-philips-tasy.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BAHIANA', hd_2='4002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='RIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BAHIANA')
        msh.date_time_of_message = '20250322091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TASY20250322091008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250005', cx_4='TASY', cx_5='MR'), CX(cx_1='826.397.514-45', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'AZEVEDO^JORGE^LUIS^^^SR'
        pid.date_time_of_birth = '19580303'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV OCEANICA', xad_2='4500', xad_3='APT 803', xad_4='SALVADOR', xad_5='BA', xad_6='40170-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^994433221'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='SALA_ECO', pl_4='HOSP_BAHIANA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250322091000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_2='SULAMERICA SAUDE')
        in1.insurance_company_id = CX(cx_1='SULAM_BA')
        in1.insurance_company_name = XON(xon_1='SULAMERICA COMPANHIA DE SEGUROS')
        in1.plan_type = CWE(cwe_1='AZEVEDO', cwe_2='JORGE', cwe_3='LUIS')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19580303')
        in1.policy_deductible = CP(cp_1='0045678901234')

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
        orc.placer_order_number = EI(ei_1='TORD20250003', ei_2='TASY')
        orc.orc_7 = '^^^20250322091000^^R'
        orc.date_time_of_order_event = '20250322091000'
        orc.orc_10 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'BA'
        orc.orc_12 = '60001'
        orc.order_effective_date_time = '20250322091000'
        orc.orc_18 = 'HOSP_BAHIANA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250003', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='34552-0', cwe_2='2D echocardiogram', cwe_3='LN')
        obr.observation_date_time = '20250322091000'
        obr.obr_16 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'BA'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'TIMG20250001'
        obr.parent_result = PRL(prl_1='US')
        obr.parent_results_observation_identifier = EIP(eip_2='Dispneia aos esforcos moderados')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Insuficiencia cardiaca nao especificada', cwe_3='I10')
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

        # .. assemble the full message ..
        msg = ORM_O01()
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
    """ Based on live/br/br-philips-tasy.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_VITORIA_APART', hd_2='4003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_VITORIA_APART')
        msh.date_time_of_message = '20250324110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250324110009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250006', cx_4='TASY', cx_5='MR'), CX(cx_1='937.518.624-56', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'FREITAS^SANDRA^MARA^^^SRA'
        pid.date_time_of_birth = '19700101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV REPUBLICA', xad_2='580', xad_3='APT 201', xad_4='VITORIA', xad_5='ES', xad_6='29055-380', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^27^993322110'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA2', pl_4='HOSP_VITORIA_APART')
        pv1.visit_number = CX(cx_1='TP20250006', cx_4='TASY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TORD20250004', ei_2='TASY')
        orc.orc_8 = '^^^20250324110000^^R'
        orc.orc_10 = '20250324110000'
        orc.orc_11 = 'PINTO^LUCIANE^TEODORA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'ES'
        orc.enterers_location = PL(pl_1='70001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250004', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid function panel', cwe_3='LN')
        obr.observation_date_time = '20250324070000'
        obr.obr_14 = '20250324070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'PINTO^LUCIANE^TEODORA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'ES'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'TLAB20250002'
        obr.charge_to_practice = MOC(moc_1='20250324110000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH [Units/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4 [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '0.7'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250324110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3 [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '2.1'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.0-4.4'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250324110000'

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
    """ Based on live/br/br-philips-tasy.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS_VENTO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_MOINHOS_VENTO')
        msh.date_time_of_message = '20250325140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'TASY20250325140010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250325140000'
        evn.operator_id = XCN(xcn_1='OLIVEIRA', xcn_2='MARIANA', xcn_3='TEODORA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250007', cx_4='TASY', cx_5='MR'), CX(cx_1='146.829.357-67', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'TEIXEIRA^PAULO^CESAR^^^SR'
        pid.date_time_of_birth = '19800707'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA LIMA E SILVA', xad_2='1234', xad_3='APT 401', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90050-100', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^992211009'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4NORTE', pl_2='401', pl_3='B', pl_4='HOSP_MOINHOS_VENTO', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='ORT', pl_2='Ortopedia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250323090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_RS')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='TEIXEIRA', cwe_2='PAULO', cwe_3='CESAR')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19800707')
        in1.insureds_date_of_birth = 'RUA LIMA E SILVA^1234^APT 401^PORTO ALEGRE^RS^90050-100'
        in1.policy_deductible = CP(cp_1='0156789012345')

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
    """ Based on live/br/br-philips-tasy.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BAHIANA', hd_2='4002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='HOSP_BAHIANA')
        msh.date_time_of_message = '20250326093000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'TASY20250326093011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TAGD20250001', ei_2='TASY')
        sch.appointment_reason = CWE(cwe_1='CONSULTA', cwe_2='Consulta Medica')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='30')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250402140000', xcn_5='20250402143000')
        sch.sch_13 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='BA')
        sch.placer_contact_location = PL(pl_1='60001')
        sch.sch_17 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='BA')
        sch.filler_contact_location = PL(pl_1='60001')
        sch.parent_filler_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250008', cx_4='TASY', cx_5='MR'), CX(cx_1='257.940.468-78', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'BARROS^MARIA^HELENA^^^SRA'
        pid.date_time_of_birth = '19650915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV ANITA GARIBALDI', xad_2='1998', xad_3='CONJ 501', xad_4='SALVADOR', xad_5='BA', xad_6='40210-450', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^991100998'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='CONS2', pl_4='HOSP_BAHIANA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='CARDIO_CONS2', cwe_2='Consultorio Cardiologia 2', cwe_3='TASY')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='CONS_CARDIO', cwe_2='Consulta Cardiologica de Retorno', cwe_3='TASY')
        ais.start_date_time = '20250402140000'
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
    """ Based on live/br/br-philips-tasy.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BAHIANA', hd_2='4002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CARDIO_SISTEMA')
        msh.receiving_facility = HD(hd_1='HOSP_BAHIANA')
        msh.date_time_of_message = '20250328153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250328153012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250008', cx_4='TASY', cx_5='MR'), CX(cx_1='257.940.468-78', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'BARROS^MARIA^HELENA^^^SRA'
        pid.date_time_of_birth = '19650915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV ANITA GARIBALDI', xad_2='1998', xad_3='CONJ 501', xad_4='SALVADOR', xad_5='BA', xad_6='40210-450', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^991100998'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='SALA_ERGO', pl_4='HOSP_BAHIANA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250328140000')

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
        orc.placer_order_number = EI(ei_1='TORD20250005', ei_2='TASY')
        orc.orc_8 = '^^^20250328153000^^R'
        orc.orc_10 = '20250328153000'
        orc.orc_11 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'BA'
        orc.enterers_location = PL(pl_1='60001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250005', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='18107-3', cwe_2='Exercise stress test study', cwe_3='LN')
        obr.observation_date_time = '20250328140000'
        obr.obr_14 = '20250328140000'
        obr.obr_15 = 'CARDIAC^Teste Ergometrico'
        obr.obr_16 = 'ALMEIDA^RICARDO^FERREIRA^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'BA'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'TCARDIO20250001'
        obr.charge_to_practice = MOC(moc_1='20250328153000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.obx_5 = 'Teste maximo. FC maxima atingida 155bpm (100% da prevista). Sem alteracoes isquemicas. Boa capacidade funcional.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250328153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='ECG Esforco Fase Recuperacao', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'TASY^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQk'
            'UDQsNFBQUFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUTGVzdGUgRXJnb21ldHJpY28gLSBGYXNlIGRlIFJlY3VwZXJhY2Fv'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Heart rate', cwe_3='LN')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='bpm')
        obx_3.reference_range = '60-100'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250328153000'

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
    """ Based on live/br/br-philips-tasy.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_MOINHOS_VENTO', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_MOINHOS_VENTO')
        msh.date_time_of_message = '20250330100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'TASY20250330100013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250330100000'
        evn.operator_id = XCN(xcn_1='REIS', xcn_2='CAROLINA', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250009', cx_4='TASY', cx_5='MR'), CX(cx_1='368.051.579-89', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'DUARTE^FRANCISCO^XAVIER^^^SR'
        pid.date_time_of_birth = '19550218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA MOSTARDEIRO', xad_2='400', xad_3='APT 1001', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90430-001', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^990099887'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SEMI', pl_2='LEITO2', pl_4='HOSP_MOINHOS_VENTO', pl_8='SEMI_INTENSIVA')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.bad_debt_recovery_amount = 'UTI^LEITO5^^HOSP_MOINHOS_VENTO'
        pv1.discharged_to_location = DLD(dld_1='20250325160000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='MELHORA CLINICA - DESMAME DE VENTILACAO MECANICA')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J96.0', cwe_2='Insuficiencia respiratoria aguda', cwe_3='I10')
        dg1.diagnosis_date_time = '20250325'
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
    """ Based on live/br/br-philips-tasy.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_HAOC', hd_2='4001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_HAOC')
        msh.date_time_of_message = '20250401081000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TASY20250401081014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250010', cx_4='TASY', cx_5='MR'), CX(cx_1='479.162.680-90', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CAMPOS^LUCIA^HELENA^^^SRA'
        pid.date_time_of_birth = '19720520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA TAMBORE', xad_2='200', xad_3='CASA', xad_4='BARUERI', xad_5='SP', xad_6='06460-070', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^989988776'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='CONS1', pl_4='HOSP_HAOC')
        pv1.temporary_location = PL(pl_1='ONC', pl_2='Oncologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250401081000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PAULISTANA')
        in1.insurance_company_id = CX(cx_1='UNIMED_SP')
        in1.insurance_company_name = XON(xon_1='UNIMED PAULISTANA')
        in1.plan_type = CWE(cwe_1='CAMPOS', cwe_2='LUCIA', cwe_3='HELENA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19720520')
        in1.policy_deductible = CP(cp_1='0089012345678')

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
        orc.placer_order_number = EI(ei_1='TORD20250006', ei_2='TASY')
        orc.orc_7 = '^^^20250401081000^^R'
        orc.date_time_of_order_event = '20250401081000'
        orc.orc_10 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'SP'
        orc.orc_12 = '50001'
        orc.order_effective_date_time = '20250401081000'
        orc.orc_18 = 'HOSP_HAOC'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250006', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='10524-7', cwe_2='CEA [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250401081000'
        obr.obr_16 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'TLAB20250003'
        obr.parent_result = PRL(prl_1='TUMOR')

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
        orc_2.placer_order_number = EI(ei_1='TORD20250007', ei_2='TASY')
        orc_2.orc_7 = '^^^20250401081000^^R'
        orc_2.date_time_of_order_event = '20250401081000'
        orc_2.orc_10 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        orc_2.orc_11 = 'SP'
        orc_2.orc_12 = '50001'
        orc_2.order_effective_date_time = '20250401081000'
        orc_2.orc_18 = 'HOSP_HAOC'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='TORD20250007', ei_2='TASY')
        obr_2.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='CA 15-3 [Units/volume] in Serum or Plasma', cwe_3='LN')
        obr_2.observation_date_time = '20250401081000'
        obr_2.obr_16 = 'MEDEIROS^PATRICIA^GUEDES^^^DRA^^^^^^^^^CRM'
        obr_2.obr_17 = 'SP'
        obr_2.placer_field_1 = '50001'
        obr_2.filler_field_1 = 'TLAB20250004'
        obr_2.parent_result = PRL(prl_1='TUMOR')

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
    """ Based on live/br/br-philips-tasy.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO', hd_2='4003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_BIOCOR_INSTITUTO')
        msh.date_time_of_message = '20250403093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250403093015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250011', cx_4='TASY', cx_5='MR'), CX(cx_1='580.273.791-01', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SOUZA^CARLOS^EDUARDO^^^SR'
        pid.date_time_of_birth = '19600805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA AIMORES', xad_2='1380', xad_3='SALA 302', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30140-070', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^988877665'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_LAB', pl_2='SALA3', pl_4='HOSP_BIOCOR_INSTITUTO')
        pv1.visit_number = CX(cx_1='TP20250011', cx_4='TASY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='TORD20250008', ei_2='TASY')
        orc.orc_8 = '^^^20250403093000^^R'
        orc.orc_10 = '20250403093000'
        orc.orc_11 = 'PINTO^LUCIANE^TEODORA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'MG'
        orc.enterers_location = PL(pl_1='70001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250008', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obr.observation_date_time = '20250403070000'
        obr.obr_14 = '20250403070000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'PINTO^LUCIANE^TEODORA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'MG'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'TLAB20250005'
        obr.charge_to_practice = MOC(moc_1='20250403093000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250403093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-99'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250403093000'

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
    """ Based on live/br/br-philips-tasy.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_FEMINA', hd_2='4004', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_FEMINA')
        msh.date_time_of_message = '20250405023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TASY20250405023016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250405023000'
        evn.operator_id = XCN(xcn_1='SANTOS', xcn_2='DEBORA', xcn_3='DA_CRUZ')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250012', cx_4='TASY', cx_5='MR'), CX(cx_1='691.384.802-02', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'KLEIN^AMANDA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19950601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SAO MANOEL', xad_2='1800', xad_3='APT 502', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90620-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^987766554'
        pid.primary_language = CWE(cwe_1='C')
        pid.religion = CWE(cwe_1='TP20250012', cwe_4='TASY', cwe_5='AN')
        pid.birth_place = 'PORTO ALEGRE^RS^BR'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='KLEIN', xpn_2='RAFAEL', xpn_3='AUGUSTO')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^51^986655443'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OBST', pl_2='SALA_PPP', pl_4='HOSP_FEMINA', pl_8='PRE_PARTO')
        pv1.hospital_service = CWE(cwe_1='OBS', cwe_2='Obstetricia', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250405023000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_2='SISTEMA UNICO DE SAUDE')
        in1.insurance_company_id = CX(cx_1='SUS_BR')
        in1.insurance_company_name = XON(xon_1='SUS - MINISTERIO DA SAUDE')
        in1.authorization_information = AUI(aui_1='KLEIN', aui_2='AMANDA', aui_3='CRISTINA')
        in1.plan_type = CWE(cwe_1='SEL', cwe_2='Titular')
        in1.name_of_insured = XPN(xpn_1='19950601')
        in1.policy_number = '7019876543210123'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Parto unico espontaneo', cwe_3='I10')
        dg1.diagnosis_date_time = '20250405'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-philips-tasy.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_INFANTIL_PEQUENO_PRINCIPE', hd_2='4003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_MICRO')
        msh.receiving_facility = HD(hd_1='HOSP_INFANTIL_PEQUENO_PRINCIPE')
        msh.date_time_of_message = '20250407141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250407141517'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250013', cx_4='TASY', cx_5='MR'), CX(cx_1='702.495.913-13', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'AMARAL^TEREZA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19680422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA DESEMBARGADOR MOTTA', xad_2='1045', xad_3='APT 101', xad_4='CURITIBA', xad_5='PR', xad_6='80250-060', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^986544332'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB_URO', pl_2='CONS1', pl_4='HOSP_INFANTIL_PEQUENO_PRINCIPE')
        pv1.temporary_location = PL(pl_1='URO', pl_2='Urologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250404090000')

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
        orc.placer_order_number = EI(ei_1='TORD20250009', ei_2='TASY')
        orc.orc_8 = '^^^20250407141500^^R'
        orc.orc_10 = '20250407141500'
        orc.orc_11 = 'NUNES^FABIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'PR'
        orc.enterers_location = PL(pl_1='80001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250009', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified in Urine by Culture', cwe_3='LN')
        obr.observation_date_time = '20250404090000'
        obr.obr_14 = '20250404090000'
        obr.obr_15 = 'URINE^Urina jato medio'
        obr.obr_16 = 'NUNES^FABIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '80001'
        obr.filler_field_1 = 'TLAB20250006'
        obr.charge_to_practice = MOC(moc_1='20250407141500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified in Urine by Culture', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250407141500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='564-5', cwe_2='Colony count [#/volume] in Urine', cwe_3='LN')
        obx_2.obx_5 = '100000'
        obx_2.units = CWE(cwe_1='UFC/mL')
        obx_2.reference_range = '<100000'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250407141500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Ciprofloxacin [Susceptibility]', cwe_3='LN')
        obx_3.obx_5 = 'Sensivel'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250407141500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Nitrofurantoin [Susceptibility]', cwe_3='LN')
        obx_4.obx_5 = 'Sensivel'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250407141500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18864-9', cwe_2='Ampicillin [Susceptibility]', cwe_3='LN')
        obx_5.obx_5 = 'Resistente'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250407141500'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Sulfamethoxazole+Trimethoprim [Susceptibility]', cwe_3='LN')
        obx_6.obx_5 = 'Resistente'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250407141500'

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
    """ Based on live/br/br-philips-tasy.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_PORTUGUES_DA_BAHIA', hd_2='4002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PORTUGUES_DA_BAHIA')
        msh.date_time_of_message = '20250409190000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A06', msg_3='ADT_A06')
        msh.message_control_id = 'TASY20250409190018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A06'
        evn.recorded_date_time = '20250409190000'
        evn.operator_id = XCN(xcn_1='ANDRADE', xcn_2='LUCAS', xcn_3='MARQUES')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250014', cx_4='TASY', cx_5='MR'), CX(cx_1='813.506.024-24', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MORAES^AUGUSTO^CESAR^^^SR'
        pid.date_time_of_birth = '19800912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV CENTENARIO', xad_2='555', xad_3='APT 901', xad_4='SALVADOR', xad_5='BA', xad_6='40300-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^71^985433221'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3NORTE', pl_2='302', pl_3='A', pl_4='HOSP_PORTUGUES_DA_BAHIA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250409190000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='INTERNACAO POR CRISE DE ASMA GRAVE - PREVIAMENTE EM CONSULTA PNEUMOLOGIA')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J45.1', cwe_2='Asma nao alergica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250409'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J96.0', cwe_2='Insuficiencia respiratoria aguda', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250409'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A06()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/br/br-philips-tasy.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_FEMINA', hd_2='4004', hd_3='DNS')
        msh.receiving_application = HD(hd_1='RIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_FEMINA')
        msh.date_time_of_message = '20250411083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TASY20250411083019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250015', cx_4='TASY', cx_5='MR'), CX(cx_1='924.617.135-35', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GODOY^LETICIA^SOUZA^^^SRA'
        pid.date_time_of_birth = '19930214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA JOAO ALFREDO', xad_2='450', xad_3='APT 301', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90050-230', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^984322110'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OBST', pl_2='CONS1', pl_4='HOSP_FEMINA')
        pv1.temporary_location = PL(pl_1='OBS', pl_2='Obstetricia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250411083000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_RS')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='GODOY', cwe_2='LETICIA', cwe_3='SOUZA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19930214')
        in1.policy_deductible = CP(cp_1='0167890123456')

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
        orc.placer_order_number = EI(ei_1='TORD20250010', ei_2='TASY')
        orc.orc_7 = '^^^20250411083000^^R'
        orc.date_time_of_order_event = '20250411083000'
        orc.orc_10 = 'SOARES^DEBORA^TADEIA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'RS'
        orc.orc_12 = '90001'
        orc.order_effective_date_time = '20250411083000'
        orc.orc_18 = 'HOSP_FEMINA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250010', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='11525-3', cwe_2='US Pelvis Fetus for pregnancy', cwe_3='LN')
        obr.observation_date_time = '20250411083000'
        obr.obr_16 = 'SOARES^DEBORA^TADEIA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'RS'
        obr.placer_field_1 = '90001'
        obr.filler_field_1 = 'TIMG20250002'
        obr.parent_result = PRL(prl_1='US')
        obr.parent_results_observation_identifier = EIP(eip_2='USG morfologica 2o trimestre - IG 22 semanas')

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
    """ Based on live/br/br-philips-tasy.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TASY')
        msh.sending_facility = HD(hd_1='HOSP_FEMINA', hd_2='4004', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_NEONATAL')
        msh.receiving_facility = HD(hd_1='HOSP_FEMINA')
        msh.date_time_of_message = '20250413100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TASY20250413100020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TP20250016', cx_4='TASY', cx_5='MR'), CX(cx_1='035.728.246-46', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'KLEIN^RN_DE_AMANDA^^^^RN'
        pid.date_time_of_birth = '20250405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SAO MANOEL', xad_2='1800', xad_3='APT 502', xad_4='PORTO ALEGRE', xad_5='RS', xad_6='90620-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^51^987766554'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEONATO', pl_2='BERCO1', pl_4='HOSP_FEMINA', pl_8='ALOJAMENTO_CONJUNTO')
        pv1.temporary_location = PL(pl_1='NEO', pl_2='Neonatologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250405060000')

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
        orc.placer_order_number = EI(ei_1='TORD20250011', ei_2='TASY')
        orc.orc_8 = '^^^20250413100000^^R'
        orc.orc_10 = '20250413100000'
        orc.orc_11 = 'OLIVEIRA^RITA^EDUARDA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'RS'
        orc.enterers_location = PL(pl_1='10001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='TORD20250011', ei_2='TASY')
        obr.universal_service_identifier = CWE(cwe_1='54094-0', cwe_2='Newborn screening panel', cwe_3='LN')
        obr.observation_date_time = '20250408080000'
        obr.obr_14 = '20250408080000'
        obr.obr_15 = 'BLOOD^Sangue capilar calcanhar'
        obr.obr_16 = 'OLIVEIRA^RITA^EDUARDA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'RS'
        obr.placer_field_1 = '10001'
        obr.filler_field_1 = 'TLAB20250007'
        obr.charge_to_practice = MOC(moc_1='20250413100000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='29575-8', cwe_2='TSH [Units/volume] in DBS', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '<10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250413100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='29571-7', cwe_2='Phenylalanine [Mass/volume] in DBS', cwe_3='LN')
        obx_2.obx_5 = '1.8'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<4.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250413100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='38478-4', cwe_2='Biotinidase [Enzymatic activity/volume] in DBS', cwe_3='LN')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='nkat/L')
        obx_3.reference_range = '>30'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250413100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='57703-8', cwe_2='Hemoglobin pattern in DBS', cwe_3='LN')
        obx_4.obx_5 = 'FA - padrao normal'
        obx_4.reference_range = 'Normal'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250413100000'

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

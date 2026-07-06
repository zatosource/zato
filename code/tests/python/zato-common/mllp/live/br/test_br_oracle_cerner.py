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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, DLD, EI, EIP, HD, MOC, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, \
    RdeO11PatientVisit, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A09, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXE, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-oracle-cerner.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-oracle-cerner.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PRO_CARDIACO', hd_2='6001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PRO_CARDIACO')
        msh.date_time_of_message = '20250310110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CML20250310110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250310110000'
        evn.operator_id = XCN(xcn_1='SANTOS', xcn_2='ANDREIA', xcn_3='MARGARIDA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='478.193.625-20', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MONTEIRO^CARLOS^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ATLANTICA', xad_2='2000', xad_3='APT 1501', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22021-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^999112233'
        pid.pid_14 = '^WPN^PH^^55^21^32114455'
        pid.marital_status = CWE(cwe_1='C')
        pid.patient_account_number = CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='AN')
        pid.multiple_birth_indicator = 'RIO DE JANEIRO^RJ^BR'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        pd1.student_indicator = CWE(cwe_1='RJ')
        pd1.handicap = CWE(cwe_1='50001')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MONTEIRO', xpn_2='HELENA', xpn_3='CRISTINA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^21^998001122'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO5', pl_3='A', pl_4='HOSP_PRO_CARDIACO', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='CAR', cwe_2='Cardiologia', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250310110000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_2='AMIL SAUDE')
        in1.insurance_company_id = CX(cx_1='AMIL_RJ')
        in1.insurance_company_name = XON(xon_1='AMIL ASSISTENCIA MEDICA INTERNACIONAL')
        in1.plan_type = CWE(cwe_1='MONTEIRO', cwe_2='CARLOS', cwe_3='HENRIQUE')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19600110')
        in1.insureds_date_of_birth = 'AV ATLANTICA^2000^APT 1501^RIO DE JANEIRO^RJ^22021-000'
        in1.policy_deductible = CP(cp_1='0501234567890')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Doenca aterosclerotica do coracao', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I20.0', cwe_2='Angina instavel', cwe_3='I10')
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
    """ Based on live/br/br-oracle-cerner.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PRO_CARDIACO', hd_2='6001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='HEMODINAMICA')
        msh.receiving_facility = HD(hd_1='HOSP_PRO_CARDIACO')
        msh.date_time_of_message = '20250311070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CML20250311070002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='478.193.625-20', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MONTEIRO^CARLOS^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ATLANTICA', xad_2='2000', xad_3='APT 1501', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22021-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^999112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO5', pl_3='A', pl_4='HOSP_PRO_CARDIACO', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250310110000')

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
        orc.placer_order_number = EI(ei_1='CORD20250001', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250311070000^^R'
        orc.date_time_of_order_event = '20250311070000'
        orc.orc_10 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'RJ'
        orc.orc_12 = '50001'
        orc.order_effective_date_time = '20250311070000'
        orc.orc_18 = 'HOSP_PRO_CARDIACO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250001', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='49565-7', cwe_2='Cardiac catheterization', cwe_3='LN')
        obr.observation_date_time = '20250311080000'
        obr.obr_16 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'RJ'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'CHEMO20250001'
        obr.parent_result = PRL(prl_1='HEMO')
        obr.parent_results_observation_identifier = EIP(eip_2='Angina instavel - avaliacao de obstrucoes coronarianas')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I20.0', cwe_2='Angina instavel', cwe_3='I10')
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
    """ Based on live/br/br-oracle-cerner.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PRO_CARDIACO', hd_2='6001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_PRO_CARDIACO')
        msh.date_time_of_message = '20250311043000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250311043003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='478.193.625-20', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MONTEIRO^CARLOS^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ATLANTICA', xad_2='2000', xad_3='APT 1501', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22021-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^999112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO5', pl_3='A', pl_4='HOSP_PRO_CARDIACO', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250310110000')

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
        orc.placer_order_number = EI(ei_1='CORD20250002', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250311043000^^R'
        orc.orc_10 = '20250311043000'
        orc.orc_11 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'RJ'
        orc.enterers_location = PL(pl_1='50001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250002', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250311040000'
        obr.obr_14 = '20250311040000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'RJ'
        obr.placer_field_1 = '50001'
        obr.filler_field_1 = 'CLAB20250001'
        obr.charge_to_practice = MOC(moc_1='20250311043000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '0.42'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310230000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = '0.68'
        obx_2.units = CWE(cwe_1='ng/mL')
        obx_2.reference_range = '0.00-0.04'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250311030000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponin T cardiac [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = '0.55'
        obx_3.units = CWE(cwe_1='ng/mL')
        obx_3.reference_range = '0.00-0.04'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250311040000'

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
    """ Based on live/br/br-oracle-cerner.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PRO_CARDIACO', hd_2='6001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_PRO_CARDIACO')
        msh.date_time_of_message = '20250313140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CML20250313140004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250313140000'
        evn.operator_id = XCN(xcn_1='AGUIAR', xcn_2='MARCIA', xcn_3='EDUARDA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='478.193.625-20', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MONTEIRO^CARLOS^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ATLANTICA', xad_2='2000', xad_3='APT 1501', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22021-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^999112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO5', pl_3='A', pl_4='HOSP_PRO_CARDIACO', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250310110000'
        pv1.discharge_date_time = '20250313140000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.visit_description = '3'
        pv2.visit_publicity_code = CWE(cwe_1='AI')
        pv2.billing_media_code = '20250320'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Doenca aterosclerotica do coracao', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z95.1', cwe_2='Presenca de enxerto de ponte de arteria coronaria', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250311'
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
    """ Based on live/br/br-oracle-cerner.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PRO_CARDIACO', hd_2='6001', hd_3='DNS')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_PRO_CARDIACO')
        msh.date_time_of_message = '20250311180000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CML20250311180005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250001', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='478.193.625-20', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MONTEIRO^CARLOS^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19600110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ATLANTICA', xad_2='2000', xad_3='APT 1501', xad_4='RIO DE JANEIRO', xad_5='RJ', xad_6='22021-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^21^999112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='LEITO5', pl_3='A', pl_4='HOSP_PRO_CARDIACO', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250310110000')

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
        orc.placer_order_number = EI(ei_1='CPRESC20250001', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250311180000^^R'
        orc.date_time_of_order_event = '20250311180000'
        orc.orc_10 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'RJ'
        orc.orc_12 = '50001'
        orc.order_effective_date_time = '20250311180000'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20250311200000^^R'
        rxe.give_code = CWE(cwe_1='10309-6001', cwe_2='Clopidogrel 75mg', cwe_3='ANVISA')
        rxe.give_amount_maximum = '1'
        rxe.give_units = CWE(cwe_1='COMP', cwe_3='HL70292')
        rxe.give_per_time_unit = '1'
        rxe.give_rate_units = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='CPRESC20250002', ei_2='CERNER_ML')
        orc_2.orc_7 = '^^^20250311180000^^R'
        orc_2.date_time_of_order_event = '20250311180000'
        orc_2.orc_10 = 'BARROS^FLAVIO^ALEXANDRE^^^DR^^^^^^^^^CRM'
        orc_2.orc_11 = 'RJ'
        orc_2.orc_12 = '50001'
        orc_2.order_effective_date_time = '20250311180000'

        # .. build RXE ..
        rxe_2 = RXE()
        rxe_2.rxe_1 = '^^^20250311200000^^R'
        rxe_2.give_code = CWE(cwe_1='10309-6002', cwe_2='Acido acetilsalicilico 100mg', cwe_3='ANVISA')
        rxe_2.give_amount_maximum = '1'
        rxe_2.give_units = CWE(cwe_1='COMP', cwe_3='HL70292')
        rxe_2.give_per_time_unit = '1'
        rxe_2.give_rate_units = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

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
    """ Based on live/br/br-oracle-cerner.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_VILA_DA_SERRA', hd_2='6002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_VILA_DA_SERRA')
        msh.date_time_of_message = '20250315080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'CML20250315080006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250315080000'
        evn.operator_id = XCN(xcn_1='OLIVEIRA', xcn_2='RENATA', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250002', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='615.927.348-41', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CAVALCANTE^FERNANDA^LUCIA^^^SRA'
        pid.date_time_of_birth = '19850222'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='RUA SANTA RITA DURAO', xad_2='800', xad_3='APT 303', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30140-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^997889900'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='FISIO', pl_2='SALA1', pl_4='HOSP_VILA_DA_SERRA')
        pv1.temporary_location = PL(pl_1='REH', pl_2='Reabilitacao', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250315080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_2='BRADESCO SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_MG')
        in1.insurance_company_name = XON(xon_1='BRADESCO SAUDE SA')
        in1.plan_type = CWE(cwe_1='CAVALCANTE', cwe_2='FERNANDA', cwe_3='LUCIA')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19850222')
        in1.policy_deductible = CP(cp_1='0612345678901')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Dor lombar baixa', cwe_3='I10')
        dg1.diagnosis_date_time = '20250315'
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
    """ Based on live/br/br-oracle-cerner.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB', hd_2='6003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_MICRO')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB')
        msh.date_time_of_message = '20250318214500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CML20250318214507'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250003', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='728.061.594-52', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PERES^AUGUSTO^CEZAR^^^SR'
        pid.date_time_of_birth = '19480505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV BATEL', xad_2='1230', xad_3='APT 1001', xad_4='CURITIBA', xad_5='PR', xad_6='80420-090', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO10', pl_3='A', pl_4='HOSP_SANTA_CRUZ_CWB', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250315160000')

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
        orc.placer_order_number = EI(ei_1='CORD20250003', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250318214500^^S'
        orc.date_time_of_order_event = '20250318214500'
        orc.orc_10 = 'ALMEIDA^PATRICIA^MARTA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'PR'
        orc.orc_12 = '60001'
        orc.order_effective_date_time = '20250318214500'
        orc.orc_18 = 'HOSP_SANTA_CRUZ_CWB'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250003', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='43409-2', cwe_2='Bacteria identified in Bronchoalveolar lavage by Culture', cwe_3='LN')
        obr.observation_date_time = '20250318214500'
        obr.obr_16 = 'ALMEIDA^PATRICIA^MARTA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'CLAB20250002'
        obr.parent_result = PRL(prl_1='MICRO')
        obr.parent_results_observation_identifier = EIP(eip_2='PAV - cultura quantitativa de LBA')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J95.851', cwe_2='Pneumonia associada a ventilacao mecanica', cwe_3='I10')
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
    """ Based on live/br/br-oracle-cerner.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB', hd_2='6003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_MICRO')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB')
        msh.date_time_of_message = '20250321091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250321091008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250003', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='728.061.594-52', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PERES^AUGUSTO^CEZAR^^^SR'
        pid.date_time_of_birth = '19480505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV BATEL', xad_2='1230', xad_3='APT 1001', xad_4='CURITIBA', xad_5='PR', xad_6='80420-090', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO10', pl_3='A', pl_4='HOSP_SANTA_CRUZ_CWB', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250315160000')

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
        orc.placer_order_number = EI(ei_1='CORD20250003', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250321091000^^R'
        orc.orc_10 = '20250321091000'
        orc.orc_11 = 'ALMEIDA^PATRICIA^MARTA^^^DRA^^^^^^^^^CRM'
        orc.orc_12 = 'PR'
        orc.enterers_location = PL(pl_1='60001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250003', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='43409-2', cwe_2='Bacteria identified in Bronchoalveolar lavage by Culture', cwe_3='LN')
        obr.observation_date_time = '20250318214500'
        obr.obr_14 = '20250318214500'
        obr.obr_15 = 'BAL^Lavado broncoalveolar'
        obr.obr_16 = 'ALMEIDA^PATRICIA^MARTA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PR'
        obr.placer_field_1 = '60001'
        obr.filler_field_1 = 'CLAB20250002'
        obr.charge_to_practice = MOC(moc_1='20250321091000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='43409-2', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Pseudomonas aeruginosa - >10^5 UFC/mL'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321091000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Piperacillin+Tazobactam [Susceptibility]', cwe_3='LN')
        obx_2.obx_5 = 'Sensivel'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321091000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem [Susceptibility]', cwe_3='LN')
        obx_3.obx_5 = 'Sensivel'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321091000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18868-0', cwe_2='Amikacin [Susceptibility]', cwe_3='LN')
        obx_4.obx_5 = 'Sensivel'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321091000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18886-2', cwe_2='Ceftazidime [Susceptibility]', cwe_3='LN')
        obx_5.obx_5 = 'Intermediario'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321091000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18908-4', cwe_2='Ciprofloxacin [Susceptibility]', cwe_3='LN')
        obx_6.obx_5 = 'Resistente'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321091000'

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
    """ Based on live/br/br-oracle-cerner.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_PAULA', hd_2='6004', hd_3='DNS')
        msh.receiving_application = HD(hd_1='PACS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_PAULA')
        msh.date_time_of_message = '20250323143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250323143009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250004', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='539.628.471-63', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'SOUZA^MARIANA^CRISTINA^^^SRA'
        pid.date_time_of_birth = '19780614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='RUA DR ALCEU DE CAMPOS RODRIGUES',
            xad_2='230',
            xad_3='APT 502',
            xad_4='SAO PAULO',
            xad_5='SP',
            xad_6='04544-000',
            xad_7='BR',
        )
        pid.pid_13 = '^PRN^PH^^55^11^995667788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIO', pl_2='SALA_TC', pl_4='HOSP_SANTA_PAULA')
        pv1.visit_number = CX(cx_1='CRN20250004', cx_4='CERNER_ML', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='CORD20250004', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250323143000^^R'
        orc.orc_10 = '20250323143000'
        orc.orc_11 = 'FERREIRA^ANDRE^GUSTAVO^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'SP'
        orc.enterers_location = PL(pl_1='70001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250004', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='24725-4', cwe_2='CT Abdomen', cwe_3='LN')
        obr.observation_date_time = '20250323110000'
        obr.obr_14 = '20250323110000'
        obr.obr_15 = 'ABD^Abdome total com contraste'
        obr.obr_16 = 'FERREIRA^ANDRE^GUSTAVO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'SP'
        obr.placer_field_1 = '70001'
        obr.filler_field_1 = 'CRAD20250001'
        obr.charge_to_practice = MOC(moc_1='20250323143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.obx_5 = 'Figado com dimensoes normais. Formacao nodular hipodensa de 2.3cm no segmento VI hepatico, sugestiva de hemangioma.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250323143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo Tomografia Abdome', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'CERNER_ML^AP^^Base64^'
            'JVBERi0xLjYKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSIC9NZXRhZGF0YSA1IDAgUiA+PgplbmRvYmoKMiAwIG9iago8PCAvVHlwZSAvUGFn'
            'ZXMgL0tpZHMgWzMgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDIgMCBSIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db250ZW50'
            'cyA0IDAgUiAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iago0IDAgb2JqCjw8IC9MZW5ndGggNDQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihMYXVkbyBUb21vZ3Jh'
            'ZmlhIEFiZG9tZSkgVGoKRVQKZW5kc3RyZWFt'
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
        dg1.diagnosis_code_dg1 = CWE(cwe_1='D18.0', cwe_2='Hemangioma hepatico', cwe_3='I10')
        dg1.diagnosis_date_time = '20250323'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [dg1]

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
    """ Based on live/br/br-oracle-cerner.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DE_LOURDES', hd_2='6005', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DE_LOURDES')
        msh.date_time_of_message = '20250325093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'CML20250325093010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250325093000'
        evn.operator_id = XCN(xcn_1='LIMA', xcn_2='MARCOS', xcn_3='GUEDES')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250005', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='864.297.531-74', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CARDOSO^RODRIGO^ALVES^^^SR'
        pid.date_time_of_birth = '19750320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV CONSELHEIRO AGUIAR', xad_2='4500', xad_3='APT 801', xad_4='RECIFE', xad_5='PE', xad_6='51111-031', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^994556677'
        pid.pid_14 = '^NET^Internet^^rodrigo.cardoso@email.com.br'
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='CRN20250005', cx_4='CERNER_ML', cx_5='AN')
        pid.multiple_birth_indicator = 'RECIFE^PE^BR'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6NORTE', pl_2='605', pl_3='A', pl_4='HOSP_NOSSA_SENHORA_DE_LOURDES', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250322150000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='CARDOSO', xpn_2='ANA', xpn_3='PAULA')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Conjuge', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^81^993445566'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/br/br-oracle-cerner.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DE_LOURDES', hd_2='6005', hd_3='DNS')
        msh.receiving_application = HD(hd_1='RIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_NOSSA_SENHORA_DE_LOURDES')
        msh.date_time_of_message = '20250326081000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CML20250326081011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250005', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='864.297.531-74', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'CARDOSO^RODRIGO^ALVES^^^SR'
        pid.date_time_of_birth = '19750320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV CONSELHEIRO AGUIAR', xad_2='4500', xad_3='APT 801', xad_4='RECIFE', xad_5='PE', xad_6='51111-031', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^81^994556677'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6NORTE', pl_2='605', pl_3='A', pl_4='HOSP_NOSSA_SENHORA_DE_LOURDES', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='NEU', pl_2='Neurologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250322150000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_2='SULAMERICA SAUDE')
        in1.insurance_company_id = CX(cx_1='SULAM_PE')
        in1.insurance_company_name = XON(xon_1='SULAMERICA COMPANHIA DE SEGUROS')
        in1.plan_type = CWE(cwe_1='CARDOSO', cwe_2='RODRIGO', cwe_3='ALVES')
        in1.name_of_insured = XPN(xpn_1='SEL', xpn_2='Titular')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19750320')
        in1.policy_deductible = CP(cp_1='0723456789012')

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
        orc.placer_order_number = EI(ei_1='CORD20250005', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250326081000^^R'
        orc.date_time_of_order_event = '20250326081000'
        orc.orc_10 = 'MENDES^LUIZA^TADEIA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'PE'
        orc.orc_12 = '80001'
        orc.order_effective_date_time = '20250326081000'
        orc.orc_18 = 'HOSP_NOSSA_SENHORA_DE_LOURDES'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250005', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='24590-2', cwe_2='MR Brain', cwe_3='LN')
        obr.observation_date_time = '20250326081000'
        obr.obr_16 = 'MENDES^LUIZA^TADEIA^^^DRA^^^^^^^^^CRM'
        obr.obr_17 = 'PE'
        obr.placer_field_1 = '80001'
        obr.filler_field_1 = 'CRAD20250002'
        obr.parent_result = PRL(prl_1='RM')
        obr.parent_results_observation_identifier = EIP(eip_2='Deficit motor progressivo em MSD - investigacao de lesao expansiva')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G93.9', cwe_2='Transtorno nao especificado do encefalo', cwe_3='I10')
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
    """ Based on live/br/br-oracle-cerner.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_AVENIDA', hd_2='6006', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_AVENIDA')
        msh.date_time_of_message = '20250327060000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250327060012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250006', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='732.184.965-85', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'FERNANDES^LUCIA^MARIA^^^SRA'
        pid.date_time_of_birth = '19650818'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='AV NOSSA SENHORA DOS NAVEGANTES',
            xad_2='1200',
            xad_3='APT 901',
            xad_4='VITORIA',
            xad_5='ES',
            xad_6='29050-335',
            xad_7='BR',
        )
        pid.pid_13 = '^PRN^PH^^55^27^993334455'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3SUL', pl_2='310', pl_3='B', pl_4='HOSP_AVENIDA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250325090000')

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
        orc.placer_order_number = EI(ei_1='CORD20250006', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250327060000^^R'
        orc.orc_10 = '20250327060000'
        orc.orc_11 = 'VIEIRA^CARLOS^ROBERTO^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'ES'
        orc.enterers_location = PL(pl_1='90001')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250006', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='24321-2', cwe_2='Basic metabolic panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20250327050000'
        obr.obr_14 = '20250327050000'
        obr.obr_15 = 'BLOOD^Sangue venoso'
        obr.obr_16 = 'VIEIRA^CARLOS^ROBERTO^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'ES'
        obr.placer_field_1 = '90001'
        obr.filler_field_1 = 'CLAB20250003'
        obr.charge_to_practice = MOC(moc_1='20250327060000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='Sodium [Moles/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='mEq/L')
        obx.reference_range = '136-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250327060000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '4.2'
        obx_2.units = CWE(cwe_1='mEq/L')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250327060000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '102'
        obx_3.units = CWE(cwe_1='mEq/L')
        obx_3.reference_range = '98-106'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250327060000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2028-9', cwe_2='CO2 [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '24'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '22-29'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250327060000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '98'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '70-99'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250327060000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_6.obx_5 = '0.9'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '0.7-1.3'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250327060000'

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
    """ Based on live/br/br-oracle-cerner.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SAO_DOMINGOS', hd_2='6007', hd_3='DNS')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='HOSP_SAO_DOMINGOS')
        msh.date_time_of_message = '20250328100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CML20250328100013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CAGD20250001', ei_2='CERNER_ML')
        sch.appointment_reason = CWE(cwe_1='PROCEDIMENTO', cwe_2='Procedimento Eletivo')
        sch.appointment_type = CWE(cwe_1='NORMAL', cwe_2='Normal')
        sch.appointment_duration_units = CNE(cne_1='45')
        sch.sch_11 = 'MIN'
        sch.placer_contact_person = XCN(xcn_4='20250405070000', xcn_5='20250405074500')
        sch.sch_13 = 'LIRA^SANDRA^DOS_REIS^^^DRA^^^^^^^^^CRM'
        sch.placer_contact_address = XAD(xad_1='MA')
        sch.placer_contact_location = PL(pl_1='10101')
        sch.sch_17 = 'LIRA^SANDRA^DOS_REIS^^^DRA^^^^^^^^^CRM'
        sch.filler_contact_address = XAD(xad_1='MA')
        sch.filler_contact_location = PL(pl_1='10101')
        sch.parent_filler_appointment_id = EI(ei_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250007', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='819.453.276-96', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'RODRIGUES^PAULO^ROBERTO^^^SR'
        pid.date_time_of_birth = '19680920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV LITORANEA', xad_2='120', xad_3='APT 604', xad_4='SAO LUIS', xad_5='MA', xad_6='65071-380', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^98^992223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='SALA2', pl_4='HOSP_SAO_DOMINGOS')
        pv1.temporary_location = PL(pl_1='GAS', pl_2='Gastroenterologia', pl_3='HL70069')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='ENDO_SALA2', cwe_2='Sala Endoscopia 2', cwe_3='CERNER_ML')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='EDA', cwe_2='Endoscopia Digestiva Alta', cwe_3='CERNER_ML')
        ais.start_date_time = '20250405070000'
        ais.duration = '45'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K21.0', cwe_2='Doenca do refluxo gastroesofagico com esofagite', cwe_3='I10')
        dg1.diagnosis_date_time = '20250328'
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
    """ Based on live/br/br-oracle-cerner.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB', hd_2='6003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB')
        msh.date_time_of_message = '20250330110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CML20250330110014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250330110000'
        evn.operator_id = XCN(xcn_1='SANTOS', xcn_2='ANDREIA', xcn_3='MARGARIDA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250003', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='728.061.594-52', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PERES^AUGUSTO^CEZAR^^^SR'
        pid.date_time_of_birth = '19480505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV BATEL', xad_2='1230', xad_3='APT 1001', xad_4='CURITIBA', xad_5='PR', xad_6='80420-090', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTE', pl_2='505', pl_3='A', pl_4='HOSP_SANTA_CRUZ_CWB', pl_8='ENFERMARIA')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Clinica Medica', cwe_3='HL70069')
        pv1.bad_debt_recovery_amount = 'UTI^LEITO10^^HOSP_SANTA_CRUZ_CWB'
        pv1.discharged_to_location = DLD(dld_1='20250315160000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='EXTUBACAO BEM SUCEDIDA - DESMAME VENTILATORIO COMPLETO')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J95.851', cwe_2='Pneumonia associada a ventilacao mecanica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
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
    """ Based on live/br/br-oracle-cerner.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PROVIDENCIA', hd_2='6008', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LIS_INTERNO')
        msh.receiving_facility = HD(hd_1='HOSP_PROVIDENCIA')
        msh.date_time_of_message = '20250401053000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250401053015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250008', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='961.382.475-07', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARTINS^JORGE^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19550715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='SQN 411 BLOCO E', xad_2='APT 201', xad_4='BRASILIA', xad_5='DF', xad_6='70866-060', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^61^991112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO2', pl_3='A', pl_4='HOSP_PROVIDENCIA', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250330200000')

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
        orc.placer_order_number = EI(ei_1='CORD20250007', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250401053000^^R'
        orc.orc_10 = '20250401053000'
        orc.orc_11 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'DF'
        orc.enterers_location = PL(pl_1='11111')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250007', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='Gas panel - Venous blood', cwe_3='LN')
        obr.observation_date_time = '20250401050000'
        obr.obr_14 = '20250401050000'
        obr.obr_15 = 'BLOOD^Sangue venoso central'
        obr.obr_16 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'DF'
        obr.placer_field_1 = '11111'
        obr.filler_field_1 = 'CLAB20250004'
        obr.charge_to_practice = MOC(moc_1='20250401053000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2746-6', cwe_2='pH of Venous blood', cwe_3='LN')
        obx.obx_5 = '7.32'
        obx.reference_range = '7.31-7.41'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250401053000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2021-4', cwe_2='pCO2 Venous blood', cwe_3='LN')
        obx_2.obx_5 = '48'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '41-51'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250401053000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2705-2', cwe_2='pO2 Venous blood', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '35-40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250401053000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1961-2', cwe_2='Bicarbonate [Moles/volume] in Venous blood', cwe_3='LN')
        obx_4.obx_5 = '22'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '22-26'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250401053000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='11556-8', cwe_2='Oxygen saturation in Venous blood', cwe_3='LN')
        obx_5.obx_5 = '68'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '60-80'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250401053000'

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
    """ Based on live/br/br-oracle-cerner.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_PROVIDENCIA', hd_2='6008', hd_3='DNS')
        msh.receiving_application = HD(hd_1='LAB_DASA')
        msh.receiving_facility = HD(hd_1='DASA_DF')
        msh.date_time_of_message = '20250402060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CML20250402060016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250008', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='961.382.475-07', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'MARTINS^JORGE^HENRIQUE^^^SR'
        pid.date_time_of_birth = '19550715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='SQN 411 BLOCO E', xad_2='APT 201', xad_4='BRASILIA', xad_5='DF', xad_6='70866-060', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^61^991112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='LEITO2', pl_3='A', pl_4='HOSP_PROVIDENCIA', pl_8='UTI')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250330200000')

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
        orc.placer_order_number = EI(ei_1='CORD20250008', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250402060000^^R'
        orc.date_time_of_order_event = '20250402060000'
        orc.orc_10 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        orc.orc_11 = 'DF'
        orc.orc_12 = '11111'
        orc.order_effective_date_time = '20250402060000'
        orc.orc_18 = 'HOSP_PROVIDENCIA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250008', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20250402060000'
        obr.obr_16 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'DF'
        obr.placer_field_1 = '11111'
        obr.filler_field_1 = 'CLAB20250005'
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
        orc_2.placer_order_number = EI(ei_1='CORD20250009', ei_2='CERNER_ML')
        orc_2.orc_7 = '^^^20250402060000^^R'
        orc_2.date_time_of_order_event = '20250402060000'
        orc_2.orc_10 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        orc_2.orc_11 = 'DF'
        orc_2.orc_12 = '11111'
        orc_2.order_effective_date_time = '20250402060000'
        orc_2.orc_18 = 'HOSP_PROVIDENCIA'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='CORD20250009', ei_2='CERNER_ML')
        obr_2.universal_service_identifier = CWE(cwe_1='1988-5', cwe_2='C reactive protein [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obr_2.observation_date_time = '20250402060000'
        obr_2.obr_16 = 'SANTANA^FLAVIO^DOS_REIS^^^DR^^^^^^^^^CRM'
        obr_2.obr_17 = 'DF'
        obr_2.placer_field_1 = '11111'
        obr_2.filler_field_1 = 'CLAB20250006'
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
    """ Based on live/br/br-oracle-cerner.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_INCOR_GO', hd_2='6009', hd_3='DNS')
        msh.receiving_application = HD(hd_1='CARDIO_SISTEMA')
        msh.receiving_facility = HD(hd_1='HOSP_INCOR_GO')
        msh.date_time_of_message = '20250404153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CML20250404153017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250009', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='284.516.937-18', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'XAVIER^BEATRIZ^HELENA^^^SRA'
        pid.date_time_of_birth = '19700310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV T-9', xad_2='500', xad_3='APT 1201', xad_4='GOIANIA', xad_5='GO', xad_6='74230-110', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^62^990001122'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='SALA_ECO', pl_4='HOSP_INCOR_GO')
        pv1.temporary_location = PL(pl_1='CAR', pl_2='Cardiologia', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250404140000')

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
        orc.placer_order_number = EI(ei_1='CORD20250010', ei_2='CERNER_ML')
        orc.orc_8 = '^^^20250404153000^^R'
        orc.orc_10 = '20250404153000'
        orc.orc_11 = 'SILVEIRA^MARCO^TADEU^^^DR^^^^^^^^^CRM'
        orc.orc_12 = 'GO'
        orc.enterers_location = PL(pl_1='12121')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD20250010', ei_2='CERNER_ML')
        obr.universal_service_identifier = CWE(cwe_1='34552-0', cwe_2='2D echocardiogram', cwe_3='LN')
        obr.observation_date_time = '20250404140000'
        obr.obr_14 = '20250404140000'
        obr.obr_15 = 'CARDIAC^Ecocardiograma transtoracico'
        obr.obr_16 = 'SILVEIRA^MARCO^TADEU^^^DR^^^^^^^^^CRM'
        obr.obr_17 = 'GO'
        obr.placer_field_1 = '12121'
        obr.filler_field_1 = 'CCARDIO20250001'
        obr.charge_to_practice = MOC(moc_1='20250404153000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.obx_5 = 'FE 62%. Camaras cardiacas com dimensoes normais. Valvas sem alteracoes significativas. Funcao diastolica preservada.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250404153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10230-1', cwe_2='LVEF [Fraction]', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '55-70'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250404153000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecocardiograma Apical 4 Camaras', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'CERNER_ML^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZ WiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAQAA9tYAAQAAAADTLWqA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC2Rlc2MAAABkAAAALmNw cnQAAAB4AAAAKHd0cHQAAABgAAAAFHJYWVoAA'
            'ACYAAAAFGdYWVoAAACsAAAAFGJYWVoAAADAAAAAFHJU UkMAAADUAAAAKGdUUkMAAADUAAAAKGJUUkMAAADUAAAAKA=='
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
    """ Based on live/br/br-oracle-cerner.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SABARA', hd_2='6010', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_SABARA')
        msh.date_time_of_message = '20250406230000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CML20250406230018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250406230000'
        evn.operator_id = XCN(xcn_1='OLIVEIRA', xcn_2='RENATA', xcn_3='DA_SILVA')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250010', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='157.038.629-29', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'GOMES^LUCAS^^^^SR'
        pid.date_time_of_birth = '20231015'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA MUNIZ DE SOUZA', xad_2='820', xad_3='APT 402', xad_4='SAO PAULO', xad_5='SP', xad_6='01534-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^11^989112233'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GOMES', xpn_2='PATRICIA', xpn_3='MARIA')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mae', cwe_3='HL70063')
        nk1.nk1_5 = '^PRN^PH^^55^11^989112233'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='GOMES', xpn_2='RAFAEL', xpn_3='HENRIQUE')
        nk1_2.relationship = CWE(cwe_1='FTH', cwe_2='Pai', cwe_3='HL70063')
        nk1_2.nk1_5 = '^PRN^PH^^55^11^988001122'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='LEITO3', pl_3='A', pl_4='HOSP_SABARA', pl_8='PEDIATRIA')
        pv1.hospital_service = CWE(cwe_1='PED', cwe_2='Pediatria', cwe_3='HL70069')
        pv1.vip_indicator = CWE(cwe_1='ADM', cwe_2='Administrativa', cwe_3='HL70007')
        pv1.prior_temporary_location = PL(pl_1='20250406230000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_2='UNIMED PAULISTANA')
        in1.insurance_company_id = CX(cx_1='UNIMED_SP')
        in1.insurance_company_name = XON(xon_1='UNIMED PAULISTANA')
        in1.plan_type = CWE(cwe_1='GOMES', cwe_2='RAFAEL', cwe_3='HENRIQUE')
        in1.name_of_insured = XPN(xpn_1='DEP', xpn_2='Dependente')
        in1.insureds_relationship_to_patient = CWE(cwe_1='20231015')
        in1.policy_deductible = CP(cp_1='0834567890123')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J21.0', cwe_2='Bronquiolite aguda devida a virus sincicial respiratorio', cwe_3='I10')
        dg1.diagnosis_date_time = '20250406'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
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
    """ Based on live/br/br-oracle-cerner.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB', hd_2='6003', hd_3='DNS')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CRUZ_CWB')
        msh.date_time_of_message = '20250408080000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'CML20250408080019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250003', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='728.061.594-52', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'PERES^AUGUSTO^CEZAR^^^SR'
        pid.date_time_of_birth = '19480505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV BATEL', xad_2='1230', xad_3='APT 1001', xad_4='CURITIBA', xad_5='PR', xad_6='80420-090', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^41^996778899'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5NORTE', pl_2='505', pl_3='A', pl_4='HOSP_SANTA_CRUZ_CWB', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.account_status = CWE(cwe_1='20250315160000')

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
        orc.placer_order_number = EI(ei_1='CPRESC20250003', ei_2='CERNER_ML')
        orc.orc_7 = '^^^20250408080000^^R'
        orc.date_time_of_order_event = '20250408080000'
        orc.orc_10 = 'ALMEIDA^PATRICIA^MARTA^^^DRA^^^^^^^^^CRM'
        orc.orc_11 = 'PR'
        orc.orc_12 = '60001'
        orc.order_effective_date_time = '20250408080000'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20250408100000^20250422100000^R'
        rxe.give_code = CWE(cwe_1='10309-7001', cwe_2='Meropenem 1g', cwe_3='ANVISA')
        rxe.give_amount_maximum = '1'
        rxe.give_units = CWE(cwe_1='G', cwe_3='HL70292')
        rxe.give_per_time_unit = '3'
        rxe.give_rate_units = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='CVC', cwe_2='Cateter venoso central', cwe_3='HL70163')

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
    """ Based on live/br/br-oracle-cerner.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER_ML')
        msh.sending_facility = HD(hd_1='HOSP_VILA_DA_SERRA', hd_2='6002', hd_3='DNS')
        msh.receiving_application = HD(hd_1='SISTEMA_LEITOS')
        msh.receiving_facility = HD(hd_1='HOSP_VILA_DA_SERRA')
        msh.date_time_of_message = '20250410160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A11')
        msh.message_control_id = 'CML20250410160020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_BR_PAM')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20250410160000'
        evn.operator_id = XCN(xcn_1='LIMA', xcn_2='MARCOS', xcn_3='GUEDES')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='CRN20250011', cx_4='CERNER_ML', cx_5='MR'), CX(cx_1='328.574.190-30', cx_4='BRASIL', cx_5='CPF')]
        pid.pid_5 = 'BARBOSA^ANDRE^LUIZ^^^SR'
        pid.date_time_of_birth = '19800925'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RUA DO OURO', xad_2='150', xad_3='APT 305', xad_4='BELO HORIZONTE', xad_5='MG', xad_6='30220-000', xad_7='BR')
        pid.pid_13 = '^PRN^PH^^55^31^988990011'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4NORTE', pl_2='401', pl_3='A', pl_4='HOSP_VILA_DA_SERRA', pl_8='ENFERMARIA')
        pv1.temporary_location = PL(pl_1='MED', pl_2='Clinica Medica', pl_3='HL70069')
        pv1.admitting_doctor = XCN(xcn_1='ADM', xcn_2='Administrativa', xcn_3='HL70007')
        pv1.admit_date_time = '20250410143000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='INTERNACAO REGISTRADA EM PRONTUARIO ERRADO - CANCELAMENTO ADMINISTRATIVO')

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

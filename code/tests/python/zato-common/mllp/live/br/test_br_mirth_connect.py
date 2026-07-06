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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, AL1, DG1, EVN, IN1, IN2, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, RXO, RXR, SCH, TXA
from zato.hl7v2.z_segments import ZAU

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-mirth-connect.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-mirth-connect.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_FELICIO_ROCHO', hd_2='MG')
        msh.receiving_application = HD(hd_1='MULTI_DEST')
        msh.receiving_facility = HD(hd_1='LAB_RAD_PHARM')
        msh.date_time_of_message = '20250320100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250320100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250320100000'
        evn.event_occurred = '20250320095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT901001', cx_4='FRO', cx_5='MR'), CX(cx_1='318.472.965-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOREIRA', xpn_2='ANDERSON', xpn_3='LUIZ')
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998765432'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='501', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032001', cwe_4='FRO', cwe_5='VN')
        pv1.visit_number = CX(cx_1='UNIMED')
        pv1.diet_type = CWE(cwe_1='FRO')
        pv1.pending_location = PL(pl_1='20250320100000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='I10', cwe_2='Hipertensao arterial essencial', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_BH')
        in1.insurance_company_name = XON(xon_1='Unimed Belo Horizonte')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MOREIRA', cwe_2='ANDERSON', cwe_3='LUIZ')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19780514')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Sapucai 471', cwe_2='Bairro Floresta', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='31015-010', cwe_6='BR')
        in1.policy_number = 'UNI1234567'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MOREIRA', xpn_2='SANDRA', xpn_3='FERREIRA')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        nk1.nk1_5 = '^PRN^PH^^^^^^^^^5531987654321'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertensao essencial (primaria)', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus tipo 2 sem complicacoes', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250320'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [nk1, dg1, dg1_2]

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
    """ Based on live/br/br-mirth-connect.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_FELICIO_ROCHO', hd_2='MG')
        msh.receiving_application = HD(hd_1='BILLING_SUS')
        msh.receiving_facility = HD(hd_1='FAT_FRO')
        msh.date_time_of_message = '20250325140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20250325140000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250325140000'
        evn.event_occurred = '20250325135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='PAT901001', cx_4='FRO', cx_5='MR'),
            CX(cx_1='318.472.965-04', cx_4='BR', cx_5='CPF'),
            CX(cx_1='SUS898465237819004', cx_4='SUS', cx_5='NH'),
        ]
        pid.patient_name = XPN(xpn_1='MOREIRA', xpn_2='ANDERSON', xpn_3='LUIZ')
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998765432'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='501', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032001', cwe_4='FRO', cwe_5='VN')
        pv1.visit_number = CX(cx_1='UNIMED')
        pv1.diet_type = CWE(cwe_1='FRO')
        pv1.pending_location = PL(pl_1='20250325140000')
        pv1.discharge_date_time = '20250320100000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertensao essencial', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Insuficiencia cardiaca congestiva', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250322'
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
    """ Based on live/br/br-mirth-connect.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA_POA', hd_2='RS')
        msh.receiving_application = HD(hd_1='SHIFT_LIS')
        msh.receiving_facility = HD(hd_1='LAB_SCP')
        msh.date_time_of_message = '20250321060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321060000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT802002', cx_4='SCP', cx_5='MR'), CX(cx_1='462.197.583-21', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GUEDES', xpn_2='FABIO', xpn_3='ROBERTO')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Independencia 75', xad_2='Bairro Independencia', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='SCP')
        pv1.pv1_7 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.pv1_9 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='SCP', cx_5='VN')
        pv1.financial_class = FC(fc_1='SUS')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        orc.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321063000^^R'
        orc.orc_10 = '20250321060000'
        orc.orc_11 = 'USR401^MENDES^LUCAS'
        orc.orc_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        orc.orc_19 = 'SCP^Santa Casa de Porto Alegre^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr.observation_date_time = '20250321063000'
        obr.obr_15 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr.result_status = '1^^^20250321063000^^R'

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
        obr_2.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr_2.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr_2.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obr_2.observation_date_time = '20250321063000'
        obr_2.obr_15 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr_2.result_status = '1^^^20250321063000^^R'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr_3.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr_3.universal_service_identifier = CWE(cwe_1='2951-2', cwe_2='SODIUM', cwe_3='LN')
        obr_3.observation_date_time = '20250321063000'
        obr_3.obr_15 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr_3.result_status = '1^^^20250321063000^^R'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/br/br-mirth-connect.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='LAB_SCP', hd_2='RS')
        msh.receiving_application = HD(hd_1='HIS_SCP')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CASA_POA')
        msh.date_time_of_message = '20250321093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321093000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT802002', cx_4='SCP', cx_5='MR'), CX(cx_1='462.197.583-21', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GUEDES', xpn_2='FABIO', xpn_3='ROBERTO')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Independencia 75', xad_2='Bairro Independencia', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='SCP')
        pv1.pv1_7 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.pv1_9 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='SCP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        orc.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR401^MENDES^LUCAS'
        orc.orc_18 = 'SCP^Santa Casa de Porto Alegre^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr.observation_date_time = '20250321063000'
        obr.obr_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr.placer_field_1 = '20250321092900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '9.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321092900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '30.5'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321092900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '14500'
        obx_3.units = CWE(cwe_1='/uL')
        obx_3.reference_range = '4000-11000'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321092900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '180000'
        obx_4.units = CWE(cwe_1='/uL')
        obx_4.reference_range = '150000-400000'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321092900'

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

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr_2.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr_2.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obr_2.observation_date_time = '20250321063000'
        obr_2.obr_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr_2.placer_field_1 = '20250321092900'
        obr_2.filler_field_2 = 'F'

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '2.3'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '0.7-1.3'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321092900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_5

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr_3.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr_3.universal_service_identifier = CWE(cwe_1='2951-2', cwe_2='SODIUM', cwe_3='LN')
        obr_3.observation_date_time = '20250321063000'
        obr_3.obr_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr_3.placer_field_1 = '20250321092900'
        obr_3.filler_field_2 = 'F'

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '132'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '136-145'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321092900'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation_3 = OruR01OrderObservation()
        order_observation_3.obr = obr_3
        order_observation_3.observation = observation_6

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation
        patient_result.order_observation_2 = order_observation_2
        patient_result.order_observation_3 = order_observation_3

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
    """ Based on live/br/br-mirth-connect.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='SP')
        msh.receiving_application = HD(hd_1='PIXEON_PACS')
        msh.receiving_facility = HD(hd_1='RIS_SIR')
        msh.date_time_of_message = '20250321100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321100000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT703003', cx_4='SIR', cx_5='MR'), CX(cx_1='287.546.193-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='RENATA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19820310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Adma Jafet 91', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_6='SIR')
        pv1.pv1_7 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.pv1_9 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SIR', cx_5='VN')
        pv1.financial_class = FC(fc_1='AMIL')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100005', ei_2='SIR')
        orc.filler_order_number = EI(ei_1='FIL2025032100005', ei_2='PIXEON')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321110000^^R'
        orc.orc_10 = '20250321100000'
        orc.orc_11 = 'USR402^SIQUEIRA^BEATRIZ'
        orc.orc_14 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        orc.orc_19 = 'SIR^Hospital Sirio Libanes^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100005', ei_2='SIR')
        obr.filler_order_number = EI(ei_1='FIL2025032100005', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250321110000'
        obr.specimen_action_code = 'J18.1^Pneumonia lobar^I10'
        obr.obr_16 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        obr.obr_26 = '1^^^20250321110000^^R'
        obr.escort_required = '24727-0^CT Chest^LN'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.1', cwe_2='Pneumonia lobar nao especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250320'
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
    """ Based on live/br/br-mirth-connect.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='PIXEON_PACS', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_SIR')
        msh.receiving_facility = HD(hd_1='HOSP_SIRIO_LIBANES')
        msh.date_time_of_message = '20250321140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321140000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT703003', cx_4='SIR', cx_5='MR'), CX(cx_1='287.546.193-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='RENATA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19820310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Adma Jafet 91', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_6='SIR')
        pv1.pv1_7 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.pv1_9 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SIR', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100005', ei_2='SIR')
        orc.filler_order_number = EI(ei_1='FIL2025032100005', ei_2='PIXEON')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR402^SIQUEIRA^BEATRIZ'
        orc.orc_18 = 'SIR^Hospital Sirio Libanes^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100005', ei_2='SIR')
        obr.filler_order_number = EI(ei_1='FIL2025032100005', ei_2='PIXEON')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT CHEST W CONTRAST', cwe_3='CPT4')
        obr.observation_date_time = '20250321110000'
        obr.obr_14 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        obr.placer_field_1 = '20250321135900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71260', cwe_2='TC TORAX LAUDO', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'TC DE TORAX COM CONTRASTE - Consolidacao em lobo inferior esquerdo com broncograma aereo.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='71260', cwe_2='TC TORAX LAUDO', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Pequeno derrame pleural esquerdo. Sem evidencias de embolismo pulmonar.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='71260', cwe_2='TC TORAX LAUDO', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'CONCLUSAO: Pneumonia lobar em base esquerda com derrame pleural laminar.'
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
    """ Based on live/br/br-mirth-connect.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='CLINICA_DASA_BARRA', hd_2='RJ')
        msh.receiving_application = HD(hd_1='SCH_MULTI')
        msh.receiving_facility = HD(hd_1='RIS_RAD_HIS')
        msh.date_time_of_message = '20250322090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250322090000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='1')
        sch.filler_appointment_id = EI(ei_1='APT2025032200007', ei_2='MIRTH')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_1='RM COLUNA', cwe_2='Ressonancia de Coluna Lombar', cwe_4='45', cwe_5='min')
        sch.placer_contact_person = XCN(xcn_1='BOOKED')
        sch.placer_contact_address = XAD(xad_1='15')
        sch.placer_contact_location = PL(pl_1='min')
        sch.filler_contact_person = XCN(xcn_4='20250324140000', xcn_5='20250324144500')
        sch.sch_17 = '40567^MOREIRA^CARLOS^EDUARDO^^^Dr.^MD'
        sch.sch_18 = '^PRN^PH^^^^^^^^^5521976543210'
        sch.filler_contact_location = PL(pl_1='DASA_BARRA')
        sch.sch_20 = '40567^MOREIRA^CARLOS^EDUARDO^^^Dr.^MD'
        sch.entered_by_location = PL(pl_1='MIRTH')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT604004', cx_4='DASA', cx_5='MR'), CX(cx_1='574.298.316-65', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CASTRO', xpn_2='JORGE', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19720618'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenida das Americas 4666', xad_2='Barra da Tijuca', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22640-102', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521987654321'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MR01', pl_3='1', pl_6='DASA')
        pv1.pv1_7 = '40567^MOREIRA^CARLOS^EDUARDO^^^Dr.^MD'
        pv1.pv1_9 = '40567^MOREIRA^CARLOS^EDUARDO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_RJ')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='CASTRO', cwe_2='JORGE', cwe_3='ANTONIO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19720618')
        in1.assignment_of_benefits = CWE(
            cwe_1='Avenida das Americas 4666',
            cwe_2='Barra da Tijuca',
            cwe_3='Rio de Janeiro',
            cwe_4='RJ',
            cwe_5='22640-102',
            cwe_6='BR',
        )
        in1.policy_number = 'AMI4456789'
        in1.insureds_administrative_sex = CWE(cwe_1='M')

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='40567', cwe_2='MOREIRA', cwe_3='CARLOS', cwe_4='EDUARDO', cwe_7='Dr.', cwe_8='MD')
        aig.resource_type = CWE(cwe_1='RADIOLOGIST')

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='RAD', pl_2='MR01', pl_3='1', pl_6='DASA')
        ail.location_type_ail = CWE(cwe_1='MRI_SUITE')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [in1, aig, ail]

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
    """ Based on live/br/br-mirth-connect.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_FELICIO_ROCHO', hd_2='MG')
        msh.receiving_application = HD(hd_1='DOC_REPO')
        msh.receiving_facility = HD(hd_1='REPOSITORY')
        msh.date_time_of_message = '20250322160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20250322160000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250322160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT901001', cx_4='FRO', cx_5='MR'), CX(cx_1='318.472.965-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOREIRA', xpn_2='ANDERSON', xpn_3='LUIZ')
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998765432'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='501', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='FRO', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Sumario de Alta', cwe_3='HL7')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250322155500'
        txa.origination_date_time = '20250322160000'
        txa.transcriptionist_code_name = XCN(xcn_1='DOC2025032200001', xcn_2='FRO')
        txa.txa_13 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Sumario de Alta Hospitalar', cwe_3='AUSPDI')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'MIRTH^AP^^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJd'
            'IC9Db3VudCAxID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBSIC9SZXNvdXJj'
            'ZXMgPDwgL0ZvbnQgPDwgL0YxIDUgMCBSID4+ID4+ID4+CmVuZG9iago0IDAgb2JqCjw8IC9MZW5ndGggODEgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihTdW1hcmlv'
            'IGRlIEFsdGEgLSBNb3JlaXJhLCBBbmRlcnNvbiBMdWl6KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCg=='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322160000'
        obx.obx_16 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'

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
    """ Based on live/br/br-mirth-connect.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='LAB_SCP', hd_2='RS')
        msh.receiving_application = HD(hd_1='ALERT_PHYSICIAN')
        msh.receiving_facility = HD(hd_1='DR_GAZETA')
        msh.date_time_of_message = '20250321094500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321094500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT802002', cx_4='SCP', cx_5='MR'), CX(cx_1='462.197.583-21', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GUEDES', xpn_2='FABIO', xpn_3='ROBERTO')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Independencia 75', xad_2='Bairro Independencia', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='SCP')
        pv1.pv1_7 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.pv1_9 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='SCP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        orc.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR401^MENDES^LUCAS'
        orc.orc_18 = 'SCP^Santa Casa de Porto Alegre^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100003', ei_2='SCP')
        obr.filler_order_number = EI(ei_1='FIL2025032100003', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obr.observation_date_time = '20250321063000'
        obr.obr_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr.placer_field_1 = '20250321092900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '2.3'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '0.7-1.3'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321092900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'VALOR CRITICO: Creatinina 2.3 mg/dL. Comunicado a Dra. GAZETA, Patricia Marta em 21/03/2025 09:45.'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

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
    """ Based on live/br/br-mirth-connect.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='SP')
        msh.receiving_application = HD(hd_1='INS_VERIFY')
        msh.receiving_facility = HD(hd_1='AMIL_ELIG')
        msh.date_time_of_message = '20250321101500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250321101500010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250321101500'
        evn.event_occurred = '20250321101000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT703003', cx_4='SIR', cx_5='MR'), CX(cx_1='287.546.193-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='RENATA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19820310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Adma Jafet 91', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_6='SIR')
        pv1.pv1_7 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.pv1_9 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SIR', cx_5='VN')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_SP')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='PRADO', cwe_2='RENATA', cwe_3='CRISTINA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19820310')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Adma Jafet 91', cwe_2='Bela Vista', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01308-050', cwe_6='BR')
        in1.report_of_eligibility_date = 'Y'
        in1.policy_number = 'AMI5567890'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build IN2 ..
        in2 = IN2()
        in2.primary_language = CWE(cwe_1='Y', cwe_2='Elegivel', cwe_3='HL70136')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

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
    """ Based on live/br/br-mirth-connect.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_FELICIO_ROCHO', hd_2='MG')
        msh.receiving_application = HD(hd_1='PHARM_SYS')
        msh.receiving_facility = HD(hd_1='FARM_FRO')
        msh.date_time_of_message = '20250322080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322080000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT901001', cx_4='FRO', cx_5='MR'), CX(cx_1='318.472.965-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOREIRA', xpn_2='ANDERSON', xpn_3='LUIZ')
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998765432'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='501', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='FRO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200011', ei_2='FRO')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322083000^^R'
        orc.orc_10 = '20250322080000'
        orc.orc_11 = 'USR403^DIAS^FERNANDA'
        orc.orc_14 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        orc.orc_19 = 'FRO^Hospital Felicio Rocho^L'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = '44567^Furosemida 40mg IV^ANVISA'
        rxo.requested_give_units = CWE(cwe_1='40')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='2')
        rxo.allow_substitutions = 'N'
        rxo.requested_dispense_amount = '1'
        rxo.number_of_refills = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenoso', cwe_3='HL70162')

        # .. build RXO ..
        rxo_2 = RXO()
        rxo_2.requested_give_code = CWE(cwe_1='2')
        rxo_2.requested_give_amount_minimum = '55678^Captopril 25mg VO^ANVISA'
        rxo_2.requested_give_units = CWE(cwe_1='25')
        rxo_2.requested_dosage_form = CWE(cwe_1='mg')
        rxo_2.providers_pharmacy_treatment_instructions = CWE(cwe_1='3')
        rxo_2.allow_substitutions = 'N'
        rxo_2.requested_dispense_amount = '1'
        rxo_2.number_of_refills = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'

        # .. build RXR ..
        rxr_2 = RXR()
        rxr_2.route = CWE(cwe_1='PO', cwe_2='Via Oral', cwe_3='HL70162')

        # .. build RXO ..
        rxo_3 = RXO()
        rxo_3.requested_give_code = CWE(cwe_1='3')
        rxo_3.requested_give_amount_minimum = '66789^Metformina 850mg VO^ANVISA'
        rxo_3.requested_give_units = CWE(cwe_1='850')
        rxo_3.requested_dosage_form = CWE(cwe_1='mg')
        rxo_3.providers_pharmacy_treatment_instructions = CWE(cwe_1='2')
        rxo_3.allow_substitutions = 'N'
        rxo_3.requested_dispense_amount = '1'
        rxo_3.number_of_refills = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'

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
    """ Based on live/br/br-mirth-connect.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='LEGACY_SYS', hd_2='MG')
        msh.receiving_application = HD(hd_1='HIS_FRO')
        msh.receiving_facility = HD(hd_1='HOSP_FELICIO_ROCHO')
        msh.date_time_of_message = '20250322120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322120000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT505005', cx_4='FRO', cx_5='MR'), CX(cx_1='739.184.526-87', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='CAMARGO', xpn_2='MARCELO', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19700220'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Goitacazes 1320', xad_2='Centro', xad_3='Belo Horizonte', xad_4='MG', xad_5='30190-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL01', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032212', cx_4='FRO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200012', ei_2='FRO')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR404^PINTO^RODRIGO'
        orc.orc_18 = 'FRO^Hospital Felicio Rocho^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200012', ei_2='FRO')
        obr.universal_service_identifier = CWE(cwe_1='30313-1', cwe_2='HGB', cwe_3='LN')
        obr.observation_date_time = '20250322080000'
        obr.obr_14 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        obr.placer_field_1 = '20250322115900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '14.5'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.5-17.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322115900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '43.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '40.0-54.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322115900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='787-2', cwe_2='VCM', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '88.5'
        obx_3.units = CWE(cwe_1='fL')
        obx_3.reference_range = '80.0-100.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322115900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='786-4', cwe_2='HCM', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '29.8'
        obx_4.units = CWE(cwe_1='pg')
        obx_4.reference_range = '27.0-33.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322115900'

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
    """ Based on live/br/br-mirth-connect.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='CLINICA_DASA_BARRA', hd_2='RJ')
        msh.receiving_application = HD(hd_1='ADT_RECEIVER')
        msh.receiving_facility = HD(hd_1='HIS_DASA')
        msh.date_time_of_message = '20250323080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG20250323080000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250323080000'
        evn.event_occurred = '20250323075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT606006', cx_4='DASA', cx_5='MR'), CX(cx_1='628.473.591-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='ARANTES', xpn_2='FERNANDA', xpn_3='LUCIA')
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Barata Ribeiro 490', xad_2='Copacabana', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22040-002', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521954321076'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='CONS05', pl_3='1', pl_6='DASA')
        pv1.pv1_7 = '50678^LIMA^RODRIGO^CARLOS^^^Dr.^MD'
        pv1.pv1_9 = '50678^LIMA^RODRIGO^CARLOS^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='GYN')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032313', cx_4='DASA', cx_5='VN')
        pv1.financial_class = FC(fc_1='BRADESCO')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_RJ')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='ARANTES', cwe_2='FERNANDA', cwe_3='LUCIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19880915')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Barata Ribeiro 490', cwe_2='Copacabana', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22040-002', cwe_6='BR')
        in1.policy_number = 'BRD3345678'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build IN2 ..
        in2 = IN2()
        in2.primary_language = CWE(cwe_1='Y', cwe_2='Autorizado', cwe_3='HL70136')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

        # .. build ZAU ..
        zau = ZAU()
        zau.zau_1 = '1'
        zau.zau_2 = 'TISS2025032300001'
        zau.zau_3 = '20250323'
        zau.zau_4 = '20250324'
        zau.zau_5 = '76830^US TRANSVAGINAL^CPT4'
        zau.zau_6 = '1'
        zau.zau_7 = 'AUTORIZADO'
        zau.zau_8 = 'BRADESCO_RJ'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [zau]

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
    """ Based on live/br/br-mirth-connect.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='LAB_PATOLOGIA', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_SIR')
        msh.receiving_facility = HD(hd_1='HOSP_SIRIO_LIBANES')
        msh.date_time_of_message = '20250323140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250323140000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT703003', cx_4='SIR', cx_5='MR'), CX(cx_1='287.546.193-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='RENATA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19820310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Adma Jafet 91', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_6='SIR')
        pv1.pv1_7 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.pv1_9 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SIR', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032300014', ei_2='SIR')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR405^AMARAL^THIAGO'
        orc.orc_18 = 'SIR^Hospital Sirio Libanes^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032300014', ei_2='SIR')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='SURGICAL PATHOLOGY', cwe_3='CPT4')
        obr.observation_date_time = '20250321160000'
        obr.obr_14 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        obr.placer_field_1 = '20250323135900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='88305', cwe_2='ANATOMIA PATOLOGICA', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'MATERIAL: Biopsia pulmonar transbronquica - Lobo inferior esquerdo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='88305', cwe_2='ANATOMIA PATOLOGICA', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'MACROSCOPIA: Tres fragmentos pardacentos medindo 0.2 a 0.4cm.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='88305', cwe_2='ANATOMIA PATOLOGICA', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'MICROSCOPIA: Processo inflamatorio agudo com exsudato neutrofilico intra-alveolar.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='88305', cwe_2='ANATOMIA PATOLOGICA', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'CONCLUSAO: Pneumonia bacteriana aguda. Ausencia de sinais de malignidade.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='IMG', cwe_2='Lamina Histopatologica Digitalizada', cwe_3='LOCAL')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'MIRTH^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNtcwIQAABtbnRyUkdCIFhZWiAH3AABABkAAwApADlhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'APbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKZGVzYwAAAPwAAABeY3BydAAAAVwAAAALd3RwdAAAAWgAAAAUYmtwdAAA'
            'AXwAAAAUclhZWgAAAZAAAAAUZ1hZWgAAAaQAAAAUYlhZWgAAAbgAAAAUZG1uZAAAAcwAAACkZG1kZAAAAnAAAABo'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250323135900'
        obx_5.obx_16 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'

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
    """ Based on live/br/br-mirth-connect.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_BAHIANA', hd_2='BA')
        msh.receiving_application = HD(hd_1='ADT_ENRICHED')
        msh.receiving_facility = HD(hd_1='MULTI_DEST')
        msh.date_time_of_message = '20250323160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20250323160000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250323160000'
        evn.event_occurred = '20250323155500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT707007', cx_4='BAH', cx_5='MR'), CX(cx_1='836.275.149-30', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SOARES', xpn_2='DANIELA', xpn_3='MARIA')
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Frei Henrique 8', xad_2='Nazare', xad_3='Salvador', xad_4='BA', xad_5='40050-420', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571943210765'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='105', pl_3='1', pl_6='BAH')
        pv1.pv1_7 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        pv1.pv1_9 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032315', cwe_4='BAH', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SULAMERICA')
        pv1.diet_type = CWE(cwe_1='BAH')
        pv1.pending_location = PL(pl_1='20250323160000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='N18.3', cwe_2='Doenca renal cronica estagio 3', cwe_3='I10')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_4='SULAMERICA')
        in1.insurance_company_id = CX(cx_1='SULAM_BA')
        in1.insurance_company_name = XON(xon_1='SulAmerica Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SOARES', cwe_2='DANIELA', cwe_3='MARIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19750830')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Frei Henrique 8', cwe_2='Nazare', cwe_3='Salvador', cwe_4='BA', cwe_5='40050-420', cwe_6='BR')
        in1.policy_number = 'SUL4456789'
        in1.insureds_administrative_sex = CWE(cwe_1='F')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='91936005', cwe_2='Penicilina', cwe_3='SNOMED')
        al1.allergy_severity_code = CWE(cwe_1='SV')
        al1.allergy_reaction_code = 'Choque anafilatico'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='FA')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='387207008', cwe_2='Ibuprofeno', cwe_3='SNOMED')
        al1_2.allergy_severity_code = CWE(cwe_1='MO')
        al1_2.allergy_reaction_code = 'Broncoespasmo'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.3', cwe_2='Doenca renal cronica estagio 3', cwe_3='I10')
        dg1.diagnosis_date_time = '20250315'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E11.4', cwe_2='DM2 com complicacoes neurologicas', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250320'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance
        msg.extra_segments = [al1, al1_2, dg1, dg1_2]

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
    """ Based on live/br/br-mirth-connect.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='LAB_SCP', hd_2='RS')
        msh.receiving_application = HD(hd_1='HIS_SCP')
        msh.receiving_facility = HD(hd_1='HOSP_SANTA_CASA_POA')
        msh.date_time_of_message = '20250323180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250323180000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT802002', cx_4='SCP', cx_5='MR'), CX(cx_1='462.197.583-21', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GUEDES', xpn_2='FABIO', xpn_3='ROBERTO')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Independencia 75', xad_2='Bairro Independencia', xad_3='Porto Alegre', xad_4='RS', xad_5='90035-070', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='1', pl_6='SCP')
        pv1.pv1_7 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.pv1_9 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='SCP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100016', ei_2='SCP')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR401^MENDES^LUCAS'
        orc.orc_18 = 'SCP^Santa Casa de Porto Alegre^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100016', ei_2='SCP')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='URINE CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250321100000'
        obr.obr_14 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        obr.placer_field_1 = '20250323175900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='87040', cwe_2='Urocultura', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'POSITIVA - Escherichia coli > 100.000 UFC/mL'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250323175900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Ampicilina', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'R'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250323175900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Ciprofloxacina', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250323175900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Sulfametoxazol-Trimetoprim', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'R'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250323175900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18955-5', cwe_2='Nitrofurantoina', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'S'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250323175900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18944-9', cwe_2='Gentamicina', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'S'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250323175900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'E. coli multirresistente (ESBL negativa). Sensivel a quinolonas e aminoglicosideos.'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6
        observation_6.nte = nte

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
    """ Based on live/br/br-mirth-connect.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_BAHIANA', hd_2='BA')
        msh.receiving_application = HD(hd_1='SCH_MULTI')
        msh.receiving_facility = HD(hd_1='CC_FARM_ANES')
        msh.date_time_of_message = '20250324090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250324090000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='1')
        sch.filler_appointment_id = EI(ei_1='APT2025032400001', ei_2='MIRTH')
        sch.event_reason = CWE(cwe_1='ELECTIVE')
        sch.appointment_reason = CWE(cwe_1='NEFRECTOMIA', cwe_2='Nefrectomia parcial videolaparoscopica', cwe_4='180', cwe_5='min')
        sch.placer_contact_person = XCN(xcn_1='BOOKED')
        sch.placer_contact_address = XAD(xad_1='60')
        sch.placer_contact_location = PL(pl_1='min')
        sch.filler_contact_person = XCN(xcn_4='20250327080000', xcn_5='20250327110000')
        sch.sch_17 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        sch.sch_18 = '^PRN^PH^^^^^^^^^5571943210765'
        sch.filler_contact_location = PL(pl_1='HOSP_BAHIANA')
        sch.sch_20 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        sch.entered_by_location = PL(pl_1='MIRTH')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT707007', cx_4='BAH', cx_5='MR'), CX(cx_1='836.275.149-30', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SOARES', xpn_2='DANIELA', xpn_3='MARIA')
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Frei Henrique 8', xad_2='Nazare', xad_3='Salvador', xad_4='BA', xad_5='40050-420', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5571943210765'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='OR01', pl_3='1', pl_6='BAH')
        pv1.pv1_7 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        pv1.pv1_9 = '60789^FONSECA^LUCAS^GUILHERME^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='URO')
        pv1.patient_type = CWE(cwe_1='P')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='60789', cwe_2='FONSECA', cwe_3='LUCAS', cwe_4='GUILHERME', cwe_7='Dr.', cwe_8='MD')
        aig.resource_type = CWE(cwe_1='SURGEON')

        # .. build AIG ..
        aig_2 = AIG()
        aig_2.set_id_aig = '2'
        aig_2.resource_id = CWE(cwe_1='70890', cwe_2='ANDRADE', cwe_3='CLAUDIA', cwe_4='TERESA', cwe_7='Dra.', cwe_8='MD')
        aig_2.resource_type = CWE(cwe_1='ANESTHESIOLOGIST')

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CIR', pl_2='OR01', pl_3='1', pl_6='BAH')
        ail.location_type_ail = CWE(cwe_1='OPERATING_ROOM')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente alergica a penicilina e ibuprofeno. DRC estagio 3 - ajustar doses anestesicas.'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [aig, aig_2, ail, nte]

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
    """ Based on live/br/br-mirth-connect.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_FELICIO_ROCHO', hd_2='MG')
        msh.receiving_application = HD(hd_1='CARDIO_SYS')
        msh.receiving_facility = HD(hd_1='HIS_FRO')
        msh.date_time_of_message = '20250324100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250324100000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT901001', cx_4='FRO', cx_5='MR'), CX(cx_1='318.472.965-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MOREIRA', xpn_2='ANDERSON', xpn_3='LUIZ')
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Sapucai 471', xad_2='Bairro Floresta', xad_3='Belo Horizonte', xad_4='MG', xad_5='31015-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998765432'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='501', pl_3='1', pl_6='FRO')
        pv1.pv1_7 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='FRO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032400018', ei_2='FRO')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR406^PEIXOTO^MARCOS'
        orc.orc_18 = 'FRO^Hospital Felicio Rocho^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032400018', ei_2='FRO')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='ECG 12 DERIVACOES', cwe_3='CPT4')
        obr.observation_date_time = '20250324093000'
        obr.obr_14 = '10234^OLIVEIRA^HENRIQUE^AUGUSTO^^^Dr.^MD'
        obr.placer_field_1 = '20250324095900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG LAUDO', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'ECG 12 derivacoes - Ritmo sinusal. FC 72bpm. Eixo eletrico normal.'
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
        obx_2.obx_5 = 'Intervalo PR 0.18s. QRS 0.08s. QTc 0.42s.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG LAUDO', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Sobrecarga ventricular esquerda (criterios de Sokolow-Lyon positivos).'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG LAUDO', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'CONCLUSAO: SVE. Compativel com hipertensao arterial de longa data.'
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
    """ Based on live/br/br-mirth-connect.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA_POA', hd_2='RS')
        msh.receiving_application = HD(hd_1='SIM_RECEIVER')
        msh.receiving_facility = HD(hd_1='SES_RS')
        msh.date_time_of_message = '20250324200000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG20250324200000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250324200000'
        evn.event_occurred = '20250324195500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT808008', cx_4='SCP', cx_5='MR'), CX(cx_1='415.872.639-50', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='TEIXEIRA', xpn_2='ANTONIO', xpn_3='JOSE')
        pid.date_time_of_birth = '19450318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua dos Andradas 1234', xad_2='Centro Historico', xad_3='Porto Alegre', xad_4='RS', xad_5='90020-008', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551998765098'
        pid.pid_19 = '20250324193000'
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='BED06', pl_3='1', pl_6='SCP')
        pv1.pv1_7 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.pv1_9 = '20345^GAZETA^PATRICIA^MARTA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032208', cwe_4='SCP', cwe_5='VN')
        pv1.visit_number = CX(cx_1='SUS')
        pv1.diet_type = CWE(cwe_1='SCP')
        pv1.pending_location = PL(pl_1='20250324193000')
        pv1.discharge_date_time = '20250322140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.0', cwe_2='Infarto agudo do miocardio, parede anterior', cwe_3='I10')
        dg1.diagnosis_date_time = '20250322'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I50.1', cwe_2='Insuficiencia ventricular esquerda', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250323'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_3 = DG1()
        dg1_3.set_id_dg1 = '3'
        dg1_3.diagnosis_code_dg1 = CWE(cwe_1='I46.9', cwe_2='Parada cardiaca nao especificada', cwe_3='I10')
        dg1_3.diagnosis_date_time = '20250324'
        dg1_3.diagnosis_type = CWE(cwe_1='A')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TS'
        obx.observation_identifier = CWE(cwe_1='DEATH_TIME', cwe_2='Hora do Obito', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '20250324193000'
        obx.observation_result_status = 'F'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='DEATH_CAUSE', cwe_2='Causa do Obito', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'I46.9^Parada cardiaca^I10'
        obx_2.observation_result_status = 'F'

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='DEATH_CERT', cwe_2='Declaracao de Obito', cwe_3='LOCAL')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'DO numero RS-2025-0032145. Causa basica: IAM anterior (I21.0).'
        obx_3.observation_result_status = 'F'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2, dg1_3]
        msg.extra_segments = [obx, obx_2, obx_3]

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
    """ Based on live/br/br-mirth-connect.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='HOSP_SIRIO_LIBANES', hd_2='SP')
        msh.receiving_application = HD(hd_1='DOC_REPO')
        msh.receiving_facility = HD(hd_1='REPOSITORY')
        msh.date_time_of_message = '20250325100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250325100000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT703003', cx_4='SIR', cx_5='MR'), CX(cx_1='287.546.193-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='PRADO', xpn_2='RENATA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19820310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Adma Jafet 91', xad_2='Bela Vista', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511965432098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_6='SIR')
        pv1.pv1_7 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.pv1_9 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='DIS')
        pv1.admitting_doctor = XCN(xcn_1='7')
        pv1.patient_type = CWE(cwe_1='VIS2025032005', cwe_4='SIR', cwe_5='VN')
        pv1.visit_number = CX(cx_1='AMIL')
        pv1.diet_type = CWE(cwe_1='SIR')
        pv1.pending_location = PL(pl_1='20250325100000')
        pv1.discharge_date_time = '20250320140000'

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
        orc.placer_order_number = EI(ei_1='ORD2025032500020', ei_2='SIR')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR407^GONCALVES^PAULO'
        orc.orc_18 = 'SIR^Hospital Sirio Libanes^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032500020', ei_2='SIR')
        obr.universal_service_identifier = CWE(cwe_1='34133-9', cwe_2='SUMMARIZATION OF EPISODE NOTE', cwe_3='LN')
        obr.observation_date_time = '20250320140000'
        obr.obr_14 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'
        obr.placer_field_1 = '20250325095900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='34133-9', cwe_2='RESUMO DE ALTA', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Internacao por pneumonia lobar em base esquerda. Tratamento com Ceftriaxona 14 dias.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='34133-9', cwe_2='RESUMO DE ALTA', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Evolucao favoravel com resolucao clinica e radiologica. Alta em bom estado geral.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='34133-9', cwe_2='RESUMO DE ALTA', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Prescricao de alta: Amoxicilina+Clavulanato 875mg 12/12h por 7 dias.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Sumario Alta Completo', cwe_3='AUSPDI')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = (
            'MIRTH^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMDUgPj4Kc3RyZWFtCkJUCi9GMSAxMCBUZgoxMDAgNzUwIFRkCihTdW1hcmlvIGRlIEFsdGEg'
            'Q29tcGxldG8pIFRqCjEwMCA3MzAgVGQKKFBhY2llbnRlOiBQcmFkbywgUmVuYXRhIENyaXN0aW5hKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCg=='
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250325095900'
        obx_4.obx_16 = '30456^VASCONCELOS^ANDRE^TADEU^^^Dr.^MD'

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

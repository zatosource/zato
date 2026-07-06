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
from zato.hl7v2.v2_9.segments import IN1, MSH, NTE, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('br', 'br-shift.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/br/br-shift.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_HERMES_PARDINI', hd_2='MG')
        msh.receiving_application = HD(hd_1='HIS_PARDINI')
        msh.receiving_facility = HD(hd_1='HOSP_PARDINI')
        msh.date_time_of_message = '20250320070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250320070000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT100201', cx_4='PARDINI', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SOUZA', xpn_2='FERNANDA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19880614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Espirito Santo 1200', xad_3='Belo Horizonte', xad_4='MG', xad_5='30160-031', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998871234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL01', pl_3='1', pl_6='PARDINI')
        pv1.pv1_7 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        pv1.pv1_9 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='PARDINI', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_MG')
        in1.insurance_company_name = XON(xon_1='Unimed Belo Horizonte')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SOUZA', cwe_2='FERNANDA', cwe_3='CRISTINA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19880614')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Espirito Santo 1200', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='30160-031', cwe_6='BR')
        in1.policy_number = 'UNI4456789'
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
        orc.placer_order_number = EI(ei_1='ORD2025032000001', ei_2='PARDINI')
        orc.filler_order_number = EI(ei_1='FIL2025032000001', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250320071500^^R'
        orc.orc_10 = '20250320070000'
        orc.orc_11 = 'USR101^LIMA^CARLA'
        orc.orc_14 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        orc.orc_19 = 'PARDINI^Laboratorio Hermes Pardini^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000001', ei_2='PARDINI')
        obr.filler_order_number = EI(ei_1='FIL2025032000001', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr.observation_date_time = '20250320071500'
        obr.obr_15 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        obr.result_status = '1^^^20250320071500^^R'

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
    """ Based on live/br/br-shift.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_HERMES_PARDINI', hd_2='MG')
        msh.receiving_application = HD(hd_1='HIS_PARDINI')
        msh.receiving_facility = HD(hd_1='HOSP_PARDINI')
        msh.date_time_of_message = '20250320091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250320091500002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT100201', cx_4='PARDINI', cx_5='MR'), CX(cx_1='478.193.625-04', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SOUZA', xpn_2='FERNANDA', xpn_3='CRISTINA')
        pid.date_time_of_birth = '19880614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Espirito Santo 1200', xad_3='Belo Horizonte', xad_4='MG', xad_5='30160-031', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531998871234'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL01', pl_3='1', pl_6='PARDINI')
        pv1.pv1_7 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        pv1.pv1_9 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032001', cx_4='PARDINI', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000001', ei_2='PARDINI')
        orc.filler_order_number = EI(ei_1='FIL2025032000001', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR101^LIMA^CARLA'
        orc.orc_18 = 'PARDINI^Laboratorio Hermes Pardini^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000001', ei_2='PARDINI')
        obr.filler_order_number = EI(ei_1='FIL2025032000001', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL', cwe_3='LN')
        obr.observation_date_time = '20250320071500'
        obr.obr_14 = '60123^BASTOS^MARINA^LUCIA^^^Dra.^MD'
        obr.placer_field_1 = '20250320091400'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '13.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '39.8'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '4.52'
        obx_3.units = CWE(cwe_1='10*6/uL')
        obx_3.reference_range = '4.0-5.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '7200'
        obx_4.units = CWE(cwe_1='/uL')
        obx_4.reference_range = '4000-11000'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '245000'
        obx_5.units = CWE(cwe_1='/uL')
        obx_5.reference_range = '150000-400000'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrofilos', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '58'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40-70'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='736-9', cwe_2='Linfocitos', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '32'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '20-40'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5905-5', cwe_2='Monocitos', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '7'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '2-10'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250320091400'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/br/br-shift.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_FLEURY', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_FLEURY')
        msh.receiving_facility = HD(hd_1='HOSP_FLEURY')
        msh.date_time_of_message = '20250320080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250320080000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT200302', cx_4='FLEURY', cx_5='MR'), CX(cx_1='582.471.396-15', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='RIBEIRO', xpn_2='MARCOS', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19750923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Ibirapuera 2907', xad_3='Sao Paulo', xad_4='SP', xad_5='04029-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511976543098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL02', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        pv1.pv1_9 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='FLEURY', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SULAMERICA', cwe_4='SULAMERICA')
        in1.insurance_company_id = CX(cx_1='SULAM_SP')
        in1.insurance_company_name = XON(xon_1='SulAmerica Saude')
        in1.plan_effective_date = '20240601'
        in1.plan_expiration_date = '20260531'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='RIBEIRO', cwe_2='MARCOS', cwe_3='ANTONIO')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19750923')
        in1.assignment_of_benefits = CWE(cwe_1='Av Ibirapuera 2907', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='04029-200', cwe_6='BR')
        in1.policy_number = 'SUL7789012'
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
        orc.placer_order_number = EI(ei_1='ORD2025032000003', ei_2='FLEURY')
        orc.filler_order_number = EI(ei_1='FIL2025032000003', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250320081500^^R'
        orc.orc_10 = '20250320080000'
        orc.orc_11 = 'USR102^ARAUJO^PATRICIA'
        orc.orc_14 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        orc.orc_19 = 'FLEURY^Laboratorio Fleury^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000003', ei_2='FLEURY')
        obr.filler_order_number = EI(ei_1='FIL2025032000003', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='LN')
        obr.observation_date_time = '20250320081500'
        obr.obr_15 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        obr.result_status = '1^^^20250320081500^^R'

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
    """ Based on live/br/br-shift.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_FLEURY', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_FLEURY')
        msh.receiving_facility = HD(hd_1='HOSP_FLEURY')
        msh.date_time_of_message = '20250320103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250320103000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT200302', cx_4='FLEURY', cx_5='MR'), CX(cx_1='582.471.396-15', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='RIBEIRO', xpn_2='MARCOS', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19750923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av Ibirapuera 2907', xad_3='Sao Paulo', xad_4='SP', xad_5='04029-200', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511976543098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL02', pl_3='1', pl_6='FLEURY')
        pv1.pv1_7 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        pv1.pv1_9 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032003', cx_4='FLEURY', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000003', ei_2='FLEURY')
        orc.filler_order_number = EI(ei_1='FIL2025032000003', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR102^ARAUJO^PATRICIA'
        orc.orc_18 = 'FLEURY^Laboratorio Fleury^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000003', ei_2='FLEURY')
        obr.filler_order_number = EI(ei_1='FIL2025032000003', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='LN')
        obr.observation_date_time = '20250320081500'
        obr.obr_14 = '70234^CARVALHO^RENATA^SOUZA^^^Dra.^MD'
        obr.placer_field_1 = '20250320102900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glicose', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-99'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureia', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '15-45'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassio', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '4.3'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (TGP)', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '28'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '7-56'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (TGO)', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '10-40'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Proteina Total', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '7.1'
        obx_8.units = CWE(cwe_1='g/dL')
        obx_8.reference_range = '6.0-8.3'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250320102900'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/br/br-shift.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_SABIN', hd_2='DF')
        msh.receiving_application = HD(hd_1='HIS_SABIN')
        msh.receiving_facility = HD(hd_1='HOSP_SABIN')
        msh.date_time_of_message = '20250320063000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250320063000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT300403', cx_4='SABIN', cx_5='MR'), CX(cx_1='639.785.241-26', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GONCALVES', xpn_2='PATRICIA', xpn_3='MARIA')
        pid.date_time_of_birth = '19820417'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='SQS 308 Bloco A Apt 302', xad_3='Brasilia', xad_4='DF', xad_5='70356-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5561987654321'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL03', pl_3='1', pl_6='SABIN')
        pv1.pv1_7 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        pv1.pv1_9 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SABIN', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_DF')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='GONCALVES', cwe_2='PATRICIA', cwe_3='MARIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19820417')
        in1.assignment_of_benefits = CWE(cwe_1='SQS 308 Bloco A', cwe_3='Brasilia', cwe_4='DF', cwe_5='70356-010', cwe_6='BR')
        in1.policy_number = 'AMI2234567'
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
        orc.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='SABIN')
        orc.filler_order_number = EI(ei_1='FIL2025032000005', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250320064500^^R'
        orc.orc_10 = '20250320063000'
        orc.orc_11 = 'USR103^MONTEIRO^RAFAEL'
        orc.orc_14 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        orc.orc_19 = 'SABIN^Laboratorio Sabin^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='SABIN')
        obr.filler_order_number = EI(ei_1='FIL2025032000005', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='LIPID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250320064500'
        obr.specimen_action_code = 'E78.5^Hiperlipidemia nao especificada^I10'
        obr.obr_16 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        obr.obr_26 = '1^^^20250320064500^^R'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Jejum de 12 horas confirmado pela paciente.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_SABIN', hd_2='DF')
        msh.receiving_application = HD(hd_1='HIS_SABIN')
        msh.receiving_facility = HD(hd_1='HOSP_SABIN')
        msh.date_time_of_message = '20250320093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250320093000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT300403', cx_4='SABIN', cx_5='MR'), CX(cx_1='639.785.241-26', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='GONCALVES', xpn_2='PATRICIA', xpn_3='MARIA')
        pid.date_time_of_birth = '19820417'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='SQS 308 Bloco A Apt 302', xad_3='Brasilia', xad_4='DF', xad_5='70356-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5561987654321'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL03', pl_3='1', pl_6='SABIN')
        pv1.pv1_7 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        pv1.pv1_9 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='LAB')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032005', cx_4='SABIN', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='SABIN')
        orc.filler_order_number = EI(ei_1='FIL2025032000005', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR103^MONTEIRO^RAFAEL'
        orc.orc_18 = 'SABIN^Laboratorio Sabin^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032000005', ei_2='SABIN')
        obr.filler_order_number = EI(ei_1='FIL2025032000005', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='LIPID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250320064500'
        obr.obr_14 = '80345^PIRES^ANTONIO^JOSE^^^Dr.^MD'
        obr.placer_field_1 = '20250320092900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol Total', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '248'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320092900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglicerides', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '195'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320092900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Colesterol', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320092900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Colesterol Calculado', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '167'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<130'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320092900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='VLDL Colesterol', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '39'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<30'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320092900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Risco cardiovascular elevado conforme Diretriz Brasileira de Dislipidemias (SBC 2017).'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_ALVARO', hd_2='PR')
        msh.receiving_application = HD(hd_1='HIS_ALVARO')
        msh.receiving_facility = HD(hd_1='HOSP_ALVARO')
        msh.date_time_of_message = '20250321070500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321070500007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT400504', cx_4='ALVARO', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MACHADO', xpn_2='CAROLINA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19910830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Marechal Deodoro 630', xad_3='Curitiba', xad_4='PR', xad_5='80010-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL04', pl_3='1', pl_6='ALVARO')
        pv1.pv1_7 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        pv1.pv1_9 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032107', cx_4='ALVARO', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_PR')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240301'
        in1.plan_expiration_date = '20260228'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MACHADO', cwe_2='CAROLINA', cwe_3='BEATRIZ')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19910830')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Marechal Deodoro 630', cwe_3='Curitiba', cwe_4='PR', cwe_5='80010-010', cwe_6='BR')
        in1.policy_number = 'BRD5567890'
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
        orc.placer_order_number = EI(ei_1='ORD2025032100007', ei_2='ALVARO')
        orc.filler_order_number = EI(ei_1='FIL2025032100007', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321072000^^R'
        orc.orc_10 = '20250321070500'
        orc.orc_11 = 'USR104^VIEIRA^MARCOS'
        orc.orc_14 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        orc.orc_19 = 'ALVARO^Laboratorio Alvaro^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100007', ei_2='ALVARO')
        obr.filler_order_number = EI(ei_1='FIL2025032100007', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='THYROID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250321072000'
        obr.specimen_action_code = 'E03.9^Hipotireoidismo nao especificado^I10'
        obr.obr_16 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        obr.obr_26 = '1^^^20250321072000^^R'

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
    """ Based on live/br/br-shift.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_ALVARO', hd_2='PR')
        msh.receiving_application = HD(hd_1='HIS_ALVARO')
        msh.receiving_facility = HD(hd_1='HOSP_ALVARO')
        msh.date_time_of_message = '20250321101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321101500008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT400504', cx_4='ALVARO', cx_5='MR'), CX(cx_1='715.286.039-37', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MACHADO', xpn_2='CAROLINA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19910830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Marechal Deodoro 630', xad_3='Curitiba', xad_4='PR', xad_5='80010-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5541976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL04', pl_3='1', pl_6='ALVARO')
        pv1.pv1_7 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        pv1.pv1_9 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032107', cx_4='ALVARO', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100007', ei_2='ALVARO')
        orc.filler_order_number = EI(ei_1='FIL2025032100007', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR104^VIEIRA^MARCOS'
        orc.orc_18 = 'ALVARO^Laboratorio Alvaro^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100007', ei_2='ALVARO')
        obr.filler_order_number = EI(ei_1='FIL2025032100007', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='THYROID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250321072000'
        obr.obr_14 = '90456^FERREIRA^CLAUDIA^HELENA^^^Dra.^MD'
        obr.placer_field_1 = '20250321101400'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '8.7'
        obx.units = CWE(cwe_1='mUI/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321101400'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='T4 Livre', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '0.7'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321101400'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='T3 Total', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '82'
        obx_3.units = CWE(cwe_1='ng/dL')
        obx_3.reference_range = '80-200'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321101400'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5385-0', cwe_2='Anti-TPO', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '342'
        obx_4.units = CWE(cwe_1='UI/mL')
        obx_4.reference_range = '<35'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321101400'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Perfil compativel com hipotireoidismo primario autoimune (Tireoidite de Hashimoto).'

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
    """ Based on live/br/br-shift.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DB_PATOLOGIA', hd_2='RJ')
        msh.receiving_application = HD(hd_1='HIS_DB')
        msh.receiving_facility = HD(hd_1='HOSP_DB')
        msh.date_time_of_message = '20250321080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321080000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT500605', cx_4='DB', cx_5='MR'), CX(cx_1='826.397.514-48', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='LIMA', xpn_2='PEDRO', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19650215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Voluntarios da Patria 190', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521965432109'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL05', pl_3='1', pl_6='DB')
        pv1.pv1_7 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        pv1.pv1_9 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='URO')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032109', cx_4='DB', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_RJ')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude - RJ')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='LIMA', cwe_2='PEDRO', cwe_3='HENRIQUE')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19650215')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Voluntarios da Patria 190', cwe_3='Rio de Janeiro', cwe_4='RJ', cwe_5='22270-010', cwe_6='BR')
        in1.policy_number = 'SUS398765432'
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
        orc.placer_order_number = EI(ei_1='ORD2025032100009', ei_2='DB')
        orc.filler_order_number = EI(ei_1='FIL2025032100009', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321083000^^R'
        orc.orc_10 = '20250321080000'
        orc.orc_11 = 'USR105^SANTOS^GABRIELA'
        orc.orc_14 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        orc.orc_19 = 'DB^Laboratorio DB Patologia^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100009', ei_2='DB')
        obr.filler_order_number = EI(ei_1='FIL2025032100009', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='URINALYSIS COMPLETE', cwe_3='LN')
        obr.observation_date_time = '20250321083000'
        obr.specimen_action_code = 'N39.0^Infeccao do trato urinario^I10'
        obr.obr_16 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        obr.obr_26 = '1^^^20250321083000^^R'

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
    """ Based on live/br/br-shift.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DB_PATOLOGIA', hd_2='RJ')
        msh.receiving_application = HD(hd_1='HIS_DB')
        msh.receiving_facility = HD(hd_1='HOSP_DB')
        msh.date_time_of_message = '20250321100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250321100000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT500605', cx_4='DB', cx_5='MR'), CX(cx_1='826.397.514-48', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='LIMA', xpn_2='PEDRO', xpn_3='HENRIQUE')
        pid.date_time_of_birth = '19650215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Voluntarios da Patria 190', xad_3='Rio de Janeiro', xad_4='RJ', xad_5='22270-010', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5521965432109'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL05', pl_3='1', pl_6='DB')
        pv1.pv1_7 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        pv1.pv1_9 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='URO')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032109', cx_4='DB', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100009', ei_2='DB')
        orc.filler_order_number = EI(ei_1='FIL2025032100009', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR105^SANTOS^GABRIELA'
        orc.orc_18 = 'DB^Laboratorio DB Patologia^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100009', ei_2='DB')
        obr.filler_order_number = EI(ei_1='FIL2025032100009', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='URINALYSIS COMPLETE', cwe_3='LN')
        obr.observation_date_time = '20250321083000'
        obr.obr_14 = '11234^MONTEIRO^RICARDO^SOUZA^^^Dr.^MD'
        obr.placer_field_1 = '20250321095900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Cor', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Amarelo citrino'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Aspecto', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Turvo'
        obx_2.reference_range = 'Limpido'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '6.0'
        obx_3.reference_range = '5.0-7.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Densidade', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '1.025'
        obx_4.reference_range = '1.005-1.030'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Proteinas', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Tracos'
        obx_5.reference_range = 'Negativo'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='5821-4', cwe_2='Leucocitos', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '85'
        obx_6.units = CWE(cwe_1='/campo')
        obx_6.reference_range = '<5'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5808-1', cwe_2='Hemácias', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '12'
        obx_7.units = CWE(cwe_1='/campo')
        obx_7.reference_range = '<3'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250321095900'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='5769-5', cwe_2='Bacterias', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = 'Numerosas'
        obx_8.reference_range = 'Ausentes'
        obx_8.interpretation_codes = CWE(cwe_1='A')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250321095900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Achados compativeis com infeccao do trato urinario. Recomenda-se urocultura.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='HOSP_ISRAELITA', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_ISRAELITA')
        msh.receiving_facility = HD(hd_1='LAB_ISRAELITA')
        msh.date_time_of_message = '20250321160000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250321160000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT600706', cx_4='ISRAELITA', cx_5='MR'), CX(cx_1='937.518.624-59', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='TEIXEIRA', xpn_2='AMANDA', xpn_3='LUCIA')
        pid.date_time_of_birth = '19790522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Dona Adma Jafet 74', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511954321076'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='BED12', pl_3='1', pl_6='ISRAELITA')
        pv1.pv1_7 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032111', cx_4='ISRAELITA', cx_5='VN')
        pv1.diet_type = CWE(cwe_1='ISRAELITA')
        pv1.pending_location = PL(pl_1='20250321140000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='AMIL', cwe_4='AMIL')
        in1.insurance_company_id = CX(cx_1='AMIL_SP')
        in1.insurance_company_name = XON(xon_1='Amil Assistencia Medica')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='TEIXEIRA', cwe_2='AMANDA', cwe_3='LUCIA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19790522')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Dona Adma Jafet 74', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01308-050', cwe_6='BR')
        in1.policy_number = 'AMI3345678'
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
        orc.placer_order_number = EI(ei_1='ORD2025032100011', ei_2='ISRAELITA')
        orc.filler_order_number = EI(ei_1='FIL2025032100011', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250321161500^^S'
        orc.orc_10 = '20250321160000'
        orc.orc_11 = 'USR106^PEREIRA^DANIEL'
        orc.orc_14 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        orc.orc_19 = 'ISRAELITA^Hospital Israelita Albert Einstein^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100011', ei_2='ISRAELITA')
        obr.filler_order_number = EI(ei_1='FIL2025032100011', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='BLOOD CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250321161500'
        obr.specimen_action_code = 'A41.9^Septicemia nao especificada^I10'
        obr.obr_16 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        obr.obr_26 = '1^^^20250321161500^^S'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente com febre persistente ha 48h, uso de antibiotico previo (Ceftriaxona). Coletar 2 amostras.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='HOSP_ISRAELITA', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_ISRAELITA')
        msh.receiving_facility = HD(hd_1='LAB_ISRAELITA')
        msh.date_time_of_message = '20250323140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250323140000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT600706', cx_4='ISRAELITA', cx_5='MR'), CX(cx_1='937.518.624-59', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='TEIXEIRA', xpn_2='AMANDA', xpn_3='LUCIA')
        pid.date_time_of_birth = '19790522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Dona Adma Jafet 74', xad_3='Sao Paulo', xad_4='SP', xad_5='01308-050', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511954321076'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='BED12', pl_3='1', pl_6='ISRAELITA')
        pv1.pv1_7 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        pv1.pv1_9 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032111', cx_4='ISRAELITA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032100011', ei_2='ISRAELITA')
        orc.filler_order_number = EI(ei_1='FIL2025032100011', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR106^PEREIRA^DANIEL'
        orc.orc_18 = 'ISRAELITA^Hospital Israelita Albert Einstein^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032100011', ei_2='ISRAELITA')
        obr.filler_order_number = EI(ei_1='FIL2025032100011', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='BLOOD CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250321161500'
        obr.obr_14 = '21345^SANTOS^MARCELO^AUGUSTO^^^Dr.^MD'
        obr.placer_field_1 = '20250323135900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultura', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'POSITIVA'
        obx.reference_range = 'Negativa'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='634-6', cwe_2='Organismo Identificado', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Staphylococcus aureus'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Oxacilina', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomicina', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'S'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18878-7', cwe_2='Ciprofloxacina', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'R'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18862-1', cwe_2='Clindamicina', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'S'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Sulfametoxazol-Trimetoprim', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = 'S'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250323135900'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='18865-4', cwe_2='Eritromicina', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = 'R'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250323135900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'MSSA identificado. Sensivel a oxacilina, desescalonar antibioticoterapia.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA', hd_2='RS')
        msh.receiving_application = HD(hd_1='HIS_SC')
        msh.receiving_facility = HD(hd_1='LAB_SC')
        msh.date_time_of_message = '20250322060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322060000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT700807', cx_4='SANTA_CASA', cx_5='MR'), CX(cx_1='063.527.918-50', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='AZEVEDO', xpn_2='RICARDO', xpn_3='JORGE')
        pid.date_time_of_birth = '19580112'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Duque de Caxias 1560', xad_3='Porto Alegre', xad_4='RS', xad_5='90010-280', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551954321098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='BED04', pl_3='1', pl_6='SANTA_CASA')
        pv1.pv1_7 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        pv1.pv1_9 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032213', cx_4='SANTA_CASA', cx_5='VN')
        pv1.diet_type = CWE(cwe_1='SANTA_CASA')
        pv1.pending_location = PL(pl_1='20250321200000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SUS', cwe_4='SUS')
        in1.insurance_company_id = CX(cx_1='SUS_RS')
        in1.insurance_company_name = XON(xon_1='Sistema Unico de Saude - RS')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '20251231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='AZEVEDO', cwe_2='RICARDO', cwe_3='JORGE')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19580112')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Duque de Caxias 1560', cwe_3='Porto Alegre', cwe_4='RS', cwe_5='90010-280', cwe_6='BR')
        in1.policy_number = 'SUS498765432'
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
        orc.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SANTA_CASA')
        orc.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322063000^^S'
        orc.orc_10 = '20250322060000'
        orc.orc_11 = 'USR107^ROSA^TATIANA'
        orc.orc_14 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        orc.orc_19 = 'SANTA_CASA^Santa Casa de Misericordia de Porto Alegre^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SANTA_CASA')
        obr.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24589-4', cwe_2='COAGULATION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322063000'
        obr.obr_15 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        obr.result_status = '1^^^20250322063000^^S'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Pre-operatorio de colecistectomia. Cirurgia agendada para 22/03/2025 14h.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='HOSP_SANTA_CASA', hd_2='RS')
        msh.receiving_application = HD(hd_1='HIS_SC')
        msh.receiving_facility = HD(hd_1='LAB_SC')
        msh.date_time_of_message = '20250322080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322080000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT700807', cx_4='SANTA_CASA', cx_5='MR'), CX(cx_1='063.527.918-50', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='AZEVEDO', xpn_2='RICARDO', xpn_3='JORGE')
        pid.date_time_of_birth = '19580112'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Duque de Caxias 1560', xad_3='Porto Alegre', xad_4='RS', xad_5='90010-280', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5551954321098'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='BED04', pl_3='1', pl_6='SANTA_CASA')
        pv1.pv1_7 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        pv1.pv1_9 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='VIS2025032213', cx_4='SANTA_CASA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SANTA_CASA')
        orc.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR107^ROSA^TATIANA'
        orc.orc_18 = 'SANTA_CASA^Santa Casa de Misericordia de Porto Alegre^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200013', ei_2='SANTA_CASA')
        obr.filler_order_number = EI(ei_1='FIL2025032200013', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24589-4', cwe_2='COAGULATION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322063000'
        obr.obr_14 = '31456^NUNES^JORGE^ALBERTO^^^Dr.^MD'
        obr.placer_field_1 = '20250322075900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Tempo de Protrombina (TP)', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '10.0-14.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322075900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.8-1.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322075900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='TTPa', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25-35'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322075900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogenio', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '285'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322075900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '198000'
        obx_5.units = CWE(cwe_1='/uL')
        obx_5.reference_range = '150000-400000'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250322075900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Coagulograma dentro da normalidade. Paciente apto para procedimento cirurgico.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DIAGNOSTICOS_AMERICA', hd_2='SC')
        msh.receiving_application = HD(hd_1='HIS_DA')
        msh.receiving_facility = HD(hd_1='LAB_DA')
        msh.date_time_of_message = '20250322070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322070000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT800908', cx_4='DA', cx_5='MR'), CX(cx_1='174.638.295-61', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SILVEIRA', xpn_2='MARCOS', xpn_3='VINICIUS')
        pid.date_time_of_birth = '19700620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Felipe Schmidt 515', xad_3='Florianopolis', xad_4='SC', xad_5='88010-000', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5548976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL06', pl_3='1', pl_6='DA')
        pv1.pv1_7 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        pv1.pv1_9 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032215', cx_4='DA', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_SC')
        in1.insurance_company_name = XON(xon_1='Unimed Florianopolis')
        in1.plan_effective_date = '20240601'
        in1.plan_expiration_date = '20260531'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SILVEIRA', cwe_2='MARCOS', cwe_3='VINICIUS')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19700620')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Felipe Schmidt 515', cwe_3='Florianopolis', cwe_4='SC', cwe_5='88010-000', cwe_6='BR')
        in1.policy_number = 'UNI8890123'
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
        orc.placer_order_number = EI(ei_1='ORD2025032200015', ei_2='DA')
        orc.filler_order_number = EI(ei_1='FIL2025032200015', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322073000^^R'
        orc.orc_10 = '20250322070000'
        orc.orc_11 = 'USR108^COSTA^RODRIGO'
        orc.orc_14 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        orc.orc_19 = 'DA^Diagnosticos da America^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200015', ei_2='DA')
        obr.filler_order_number = EI(ei_1='FIL2025032200015', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obr.observation_date_time = '20250322073000'
        obr.specimen_action_code = 'E11.9^Diabetes mellitus tipo 2^I10'
        obr.obr_16 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        obr.obr_26 = '1^^^20250322073000^^R'

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
    """ Based on live/br/br-shift.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DIAGNOSTICOS_AMERICA', hd_2='SC')
        msh.receiving_application = HD(hd_1='HIS_DA')
        msh.receiving_facility = HD(hd_1='LAB_DA')
        msh.date_time_of_message = '20250322100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322100000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT800908', cx_4='DA', cx_5='MR'), CX(cx_1='174.638.295-61', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='SILVEIRA', xpn_2='MARCOS', xpn_3='VINICIUS')
        pid.date_time_of_birth = '19700620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Felipe Schmidt 515', xad_3='Florianopolis', xad_4='SC', xad_5='88010-000', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5548976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL06', pl_3='1', pl_6='DA')
        pv1.pv1_7 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        pv1.pv1_9 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032215', cx_4='DA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200015', ei_2='DA')
        orc.filler_order_number = EI(ei_1='FIL2025032200015', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR108^COSTA^RODRIGO'
        orc.orc_18 = 'DA^Diagnosticos da America^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200015', ei_2='DA')
        obr.filler_order_number = EI(ei_1='FIL2025032200015', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obr.observation_date_time = '20250322073000'
        obr.obr_14 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'
        obr.placer_field_1 = '20250322095900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina Glicada (HbA1c)', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322095900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glicemia de Jejum', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '156'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-99'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322095900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='4548-4', cwe_2='INTERPRETACAO', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Controle glicemico inadequado. Meta HbA1c <7% nao atingida.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo HbA1c Completo', cwe_3='AUSPDI')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = (
            'SHIFT_LIS^AP^^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJd'
            'IC9Db3VudCAxID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBSIC9SZXNvdXJj'
            'ZXMgPDwgPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKExhdWRvIEhiQTFjKSBUagpFVAplbmRzdHJlYW0K'
            'ZW5kb2Jq'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322095900'
        obx_4.obx_16 = '41567^ZIMMERMANN^CLAUDIA^MARIA^^^Dra.^MD'

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
    """ Based on live/br/br-shift.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_HERMES_PARDINI', hd_2='MG')
        msh.receiving_application = HD(hd_1='HIS_PARDINI')
        msh.receiving_facility = HD(hd_1='HOSP_PARDINI')
        msh.date_time_of_message = '20250322080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250322080000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT900109', cx_4='PARDINI', cx_5='MR'), CX(cx_1='285.749.306-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='NOGUEIRA', xpn_2='CAMILA', xpn_3='SOUZA')
        pid.date_time_of_birth = '19930305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Sergipe 475', xad_3='Belo Horizonte', xad_4='MG', xad_5='30130-170', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL07', pl_3='1', pl_6='PARDINI')
        pv1.pv1_7 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        pv1.pv1_9 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='OBS')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032217', cx_4='PARDINI', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UNIMED', cwe_4='UNIMED')
        in1.insurance_company_id = CX(cx_1='UNIMED_MG')
        in1.insurance_company_name = XON(xon_1='Unimed Belo Horizonte')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='NOGUEIRA', cwe_2='CAMILA', cwe_3='SOUZA')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19930305')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Sergipe 475', cwe_3='Belo Horizonte', cwe_4='MG', cwe_5='30130-170', cwe_6='BR')
        in1.policy_number = 'UNI9901234'
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
        orc.placer_order_number = EI(ei_1='ORD2025032200017', ei_2='PARDINI')
        orc.filler_order_number = EI(ei_1='FIL2025032200017', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250322083000^^R'
        orc.orc_10 = '20250322080000'
        orc.orc_11 = 'USR109^BARROS^JULIANA'
        orc.orc_14 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        orc.orc_19 = 'PARDINI^Laboratorio Hermes Pardini^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200017', ei_2='PARDINI')
        obr.filler_order_number = EI(ei_1='FIL2025032200017', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24110-9', cwe_2='PRENATAL SEROLOGY PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322083000'
        obr.specimen_action_code = 'Z34.0^Supervisao de primeira gravidez normal^I10'
        obr.obr_16 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        obr.obr_26 = '1^^^20250322083000^^R'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Pre-natal primeiro trimestre. IG 10 semanas.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_HERMES_PARDINI', hd_2='MG')
        msh.receiving_application = HD(hd_1='HIS_PARDINI')
        msh.receiving_facility = HD(hd_1='HOSP_PARDINI')
        msh.date_time_of_message = '20250322140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250322140000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT900109', cx_4='PARDINI', cx_5='MR'), CX(cx_1='285.749.306-72', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='NOGUEIRA', xpn_2='CAMILA', xpn_3='SOUZA')
        pid.date_time_of_birth = '19930305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rua Sergipe 475', xad_3='Belo Horizonte', xad_4='MG', xad_5='30130-170', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5531976543210'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL07', pl_3='1', pl_6='PARDINI')
        pv1.pv1_7 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        pv1.pv1_9 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='OBS')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032217', cx_4='PARDINI', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032200017', ei_2='PARDINI')
        orc.filler_order_number = EI(ei_1='FIL2025032200017', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR109^BARROS^JULIANA'
        orc.orc_18 = 'PARDINI^Laboratorio Hermes Pardini^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032200017', ei_2='PARDINI')
        obr.filler_order_number = EI(ei_1='FIL2025032200017', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='24110-9', cwe_2='PRENATAL SEROLOGY PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322083000'
        obr.obr_14 = '51678^ALVES^SANDRA^MARIA^^^Dra.^MD'
        obr.placer_field_1 = '20250322135900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5196-1', cwe_2='HIV 1+2 Anticorpos', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Nao Reagente'
        obx.reference_range = 'Nao Reagente'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5292-8', cwe_2='VDRL', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Nao Reagente'
        obx_2.reference_range = 'Nao Reagente'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5195-3', cwe_2='HBsAg', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Nao Reagente'
        obx_3.reference_range = 'Nao Reagente'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='16128-1', cwe_2='Anti-HCV', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Nao Reagente'
        obx_4.reference_range = 'Nao Reagente'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5334-8', cwe_2='Toxoplasma IgG', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Reagente (145 UI/mL)'
        obx_5.reference_range = 'Nao Reagente'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5335-5', cwe_2='Toxoplasma IgM', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'Nao Reagente'
        obx_6.reference_range = 'Nao Reagente'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='5132-6', cwe_2='Rubeola IgG', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = 'Reagente (89 UI/mL)'
        obx_7.reference_range = 'Nao Reagente'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250322135900'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='5133-4', cwe_2='Rubeola IgM', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = 'Nao Reagente'
        obx_8.reference_range = 'Nao Reagente'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250322135900'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sorologias pre-natais sem evidencia de infeccao aguda. Imunidade previa para toxoplasmose e rubeola.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DIAGNOSTICOS_AMERICA', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_DA')
        msh.receiving_facility = HD(hd_1='LAB_DA')
        msh.date_time_of_message = '20250323070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20250323070000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT101210', cx_4='DA', cx_5='MR'), CX(cx_1='396.851.247-83', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MARTINS', xpn_2='LUCAS', xpn_3='GABRIEL')
        pid.date_time_of_birth = '19880920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Haddock Lobo 595', xad_3='Sao Paulo', xad_4='SP', xad_5='01414-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210965'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL08', pl_3='1', pl_6='DA')
        pv1.pv1_7 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        pv1.pv1_9 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032319', cx_4='DA', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BRADESCO', cwe_4='BRADESCO_SAUDE')
        in1.insurance_company_id = CX(cx_1='BRADESCO_SP')
        in1.insurance_company_name = XON(xon_1='Bradesco Saude')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20261231'
        in1.name_of_insured = XPN(xpn_1='IND')
        in1.insureds_relationship_to_patient = CWE(cwe_1='MARTINS', cwe_2='LUCAS', cwe_3='GABRIEL')
        in1.insureds_date_of_birth = 'SEL'
        in1.insureds_address = XAD(xad_1='19880920')
        in1.assignment_of_benefits = CWE(cwe_1='Rua Haddock Lobo 595', cwe_3='Sao Paulo', cwe_4='SP', cwe_5='01414-001', cwe_6='BR')
        in1.policy_number = 'BRD1123456'
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
        orc.placer_order_number = EI(ei_1='ORD2025032300019', ei_2='DA')
        orc.filler_order_number = EI(ei_1='FIL2025032300019', ei_2='SHIFT')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20250323073000^^S'
        orc.orc_10 = '20250323070000'
        orc.orc_11 = 'USR110^OLIVEIRA^FERNANDO'
        orc.orc_14 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        orc.orc_19 = 'DA^Diagnosticos da America^L'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032300019', ei_2='DA')
        obr.filler_order_number = EI(ei_1='FIL2025032300019', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-COV-2 RNA NAA+PROBE', cwe_3='LN')
        obr.observation_date_time = '20250323073000'
        obr.specimen_action_code = 'U07.1^COVID-19 virus identificado^I10'
        obr.obr_16 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        obr.obr_26 = '1^^^20250323073000^^S'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sintomas ha 3 dias: febre, tosse seca, mialgia. Contato domiciliar positivo.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/br/br-shift.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SHIFT_LIS')
        msh.sending_facility = HD(hd_1='LAB_DIAGNOSTICOS_AMERICA', hd_2='SP')
        msh.receiving_application = HD(hd_1='HIS_DA')
        msh.receiving_facility = HD(hd_1='LAB_DA')
        msh.date_time_of_message = '20250323160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20250323160000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT101210', cx_4='DA', cx_5='MR'), CX(cx_1='396.851.247-83', cx_4='BR', cx_5='CPF')]
        pid.patient_name = XPN(xpn_1='MARTINS', xpn_2='LUCAS', xpn_3='GABRIEL')
        pid.date_time_of_birth = '19880920'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rua Haddock Lobo 595', xad_3='Sao Paulo', xad_4='SP', xad_5='01414-001', xad_6='BR')
        pid.pid_13 = '^PRN^PH^^^^^^^^^5511943210965'
        pid.pid_33 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='COL08', pl_3='1', pl_6='DA')
        pv1.pv1_7 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        pv1.pv1_9 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.patient_type = CWE(cwe_1='V')
        pv1.visit_number = CX(cx_1='VIS2025032319', cx_4='DA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD2025032300019', ei_2='DA')
        orc.filler_order_number = EI(ei_1='FIL2025032300019', ei_2='SHIFT')
        orc.order_status = 'CM'
        orc.orc_11 = 'USR110^OLIVEIRA^FERNANDO'
        orc.orc_18 = 'DA^Diagnosticos da America^L'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2025032300019', ei_2='DA')
        obr.filler_order_number = EI(ei_1='FIL2025032300019', ei_2='SHIFT')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-COV-2 RNA NAA+PROBE', cwe_3='LN')
        obr.observation_date_time = '20250323073000'
        obr.obr_14 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'
        obr.placer_field_1 = '20250323155900'
        obr.filler_field_2 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA RT-PCR', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'DETECTADO'
        obx.reference_range = 'Nao Detectado'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250323155900'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='94745-7', cwe_2='Ct Gene N', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '22.3'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250323155900'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='94746-5', cwe_2='Ct Gene RdRp', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '24.1'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250323155900'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='94500-6', cwe_2='INTERPRETACAO', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Resultado DETECTADO para SARS-CoV-2 por RT-PCR em tempo real. Carga viral moderada-alta (Ct <25).'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laudo RT-PCR COVID-19', cwe_3='AUSPDI')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'SHIFT_LIS^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCA+PiA+'
            'PgplbmRvYmoKNCAwIG9iago8PCAvTGVuZ3RoIDUyID4+CnN0cmVhbQpCVAovRjEgMTIgVGYKMTAwIDcwMCBUZAooTGF1ZG8gQ09WSUQtMTkgUlQtUENSKSBUagpFVAplbmRzdHJlYW0K'
            'ZW5kb2Jq'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250323155900'
        obx_5.obx_16 = '61789^BORGES^FLAVIA^CRISTINA^^^Dra.^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Notificacao compulsoria realizada ao SIVEP-Gripe conforme Portaria MS 1.102/2022.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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

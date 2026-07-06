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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A03, ADT_A05, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MSA, MSH, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-winmedicalc.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-winmedicalc.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250420070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0012286265', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svoboda', xpn_2='Bedřich')
        pid.date_time_of_birth = '20001228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 135', xad_3='Šumperk', xad_5='787 01', xad_6='CZ')
        pid.pid_13 = '+420646313122'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70001', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '0012286265'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='101', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='INT')

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
        orc.placer_order_number = EI(ei_1='WORD001')
        orc.orc_12 = '50001^Hájek^Bohumil^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Biochemie', cwe_3='LN')
        obr.observation_date_time = '20250420060000'
        obr.results_rpt_status_chng_date_time = '20250420070000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx.obx_5 = '6.1'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.6'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '7.2'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.8-7.2'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodík', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6298-4', cwe_2='Draslík', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='CRP', cwe_3='LN')
        obx_6.obx_5 = '3.2'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '<5.0'
        obx_6.observation_result_status = 'F'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250420073000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0012286265', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svoboda', xpn_2='Bedřich')
        pid.date_time_of_birth = '20001228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 135', xad_3='Šumperk', xad_5='787 01', xad_6='CZ')
        pid.pid_13 = '+420646313122'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70001', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '0012286265'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='101', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='INT')

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
        orc.placer_order_number = EI(ei_1='WORD002')
        orc.orc_12 = '50001^Hájek^Bohumil^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD002')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Krevní obraz', cwe_3='LN')
        obr.observation_date_time = '20250420060000'
        obr.results_rpt_status_chng_date_time = '20250420073000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyty', cwe_3='LN')
        obx_2.obx_5 = '4.52'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '4.0-5.8'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '138'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-170'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_4.obx_5 = '0.41'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.39-0.50'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_5.obx_5 = '312'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='751-8', cwe_2='Neutrofily', cwe_3='LN')
        obx_6.obx_5 = '78.5'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40-70'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_7.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
        )
        obx_7.observation_result_status = 'F'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250420080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7656064365', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svobodová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19760606'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hrnčířská 77', xad_3='Náchod', xad_5='547 01', xad_6='CZ')
        pid.pid_13 = '+420677567854'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70002', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '7656064365'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='INT')

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
        orc.placer_order_number = EI(ei_1='WORD003')
        orc.orc_12 = '50002^Hrubá^Věra^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD003')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipidový profil', cwe_3='LN')
        obr.observation_date_time = '20250420070000'
        obr.results_rpt_status_chng_date_time = '20250420080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Celkový cholesterol', cwe_3='LN')
        obx.obx_5 = '6.5'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL cholesterol', cwe_3='LN')
        obx_2.obx_5 = '4.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<3.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2571-8', cwe_2='HDL cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglyceridy', cwe_3='LN')
        obx_4.obx_5 = '2.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<1.7'
        obx_4.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250421090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5556018627', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Králová', xpn_2='Lucie')
        pid.date_time_of_birth = '19550601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Čankovská 146', xad_3='Brno', xad_5='602 00', xad_6='CZ')
        pid.pid_13 = '+420730770032'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70003', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '5556018627'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IMUN', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='IMUN')

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
        orc.placer_order_number = EI(ei_1='WORD004')
        orc.orc_12 = '50003^Kučerová^Eliška^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD004')
        obr.universal_service_identifier = CWE(cwe_1='5130-0', cwe_2='Imunoglobuliny', cwe_3='LN')
        obr.observation_date_time = '20250421080000'
        obr.results_rpt_status_chng_date_time = '20250421090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2458-8', cwe_2='IgA', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '0.7-4.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2462-0', cwe_2='IgG', cwe_3='LN')
        obx_2.obx_5 = '12.5'
        obx_2.units = CWE(cwe_1='g/L')
        obx_2.reference_range = '7.0-16.0'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2466-1', cwe_2='IgM', cwe_3='LN')
        obx_3.obx_5 = '1.2'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '0.4-2.3'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='19113-0', cwe_2='IgE celkové', cwe_3='LN')
        obx_4.obx_5 = '85'
        obx_4.units = CWE(cwe_1='kU/L')
        obx_4.reference_range = '<100'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250421160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'WM00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250421160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250421160000')
        pv1.diet_type = CWE(cwe_1='NEM_TABOR')
        pv1.pending_location = PL(pl_1='20250421160000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111')
        in1.insurance_company_id = CX(cx_1='VZP', cx_2='Všeobecná zdravotní pojišťovna')
        in1.delay_before_lr_day = '111'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'K80.2'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Kámen žlučníku bez cholecystitidy', cwe_3='ICD10CZ')
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250421163000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WM00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD005')
        orc.orc_7 = '^^^20250422060000^^S'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD005')
        obr.universal_service_identifier = CWE(cwe_1='PRE_OP', cwe_2='Předoperační panel', cwe_3='LOCAL')
        obr.observation_date_time = '20250421163000'
        obr.obr_16 = '50004^Urban^Zdeněk^MUDr.'
        obr.obr_27 = '1^^^20250422060000^^S'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250422080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD005')
        orc.orc_12 = '50004^Urban^Zdeněk^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD005')
        obr.universal_service_identifier = CWE(cwe_1='PRE_OP', cwe_2='Předoperační panel', cwe_3='LOCAL')
        obr.observation_date_time = '20250422060000'
        obr.results_rpt_status_chng_date_time = '20250422080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Protrombinový čas', cwe_3='LN')
        obx.obx_5 = '13.1'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-15.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_2.obx_5 = '30.2'
        obx_2.units = CWE(cwe_1='s')
        obx_2.reference_range = '25.0-36.0'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_3.obx_5 = '1.05'
        obx_3.reference_range = '0.8-1.2'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_4.obx_5 = '142'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '130-170'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx_5.obx_5 = '5.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.9-5.6'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_6.obx_5 = '102'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '62-106'
        obx_6.observation_result_status = 'F'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250421163500'
        msh.message_type = MSG(msg_1='ACK')
        msh.message_control_id = 'WM00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'WM00006'
        msa.msa_4 = ''

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250422090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD006')
        orc.orc_12 = '50004^Urban^Zdeněk^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD006')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='Moč chemicky', cwe_3='LN')
        obr.observation_date_time = '20250422060000'
        obr.results_rpt_status_chng_date_time = '20250422090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='pH moči', cwe_3='LN')
        obx.obx_5 = '5.5'
        obx.reference_range = '5.0-7.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specifická hmotnost', cwe_3='LN')
        obx_2.obx_5 = '1.022'
        obx_2.reference_range = '1.005-1.030'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Glukóza v moči', cwe_3='LN')
        obx_3.obx_5 = 'Negativní'
        obx_3.reference_range = 'Negativní'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein v moči', cwe_3='LN')
        obx_4.obx_5 = 'Negativní'
        obx_4.reference_range = 'Negativní'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5799-2', cwe_2='Leukocyty v moči', cwe_3='LN')
        obx_5.obx_5 = 'Negativní'
        obx_5.reference_range = 'Negativní'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250422093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD007')
        orc.orc_12 = '50005^Kolář^Pavel^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD007')
        obr.universal_service_identifier = CWE(cwe_1='882-1', cwe_2='Krevní skupina', cwe_3='LN')
        obr.observation_date_time = '20250422060000'
        obr.results_rpt_status_chng_date_time = '20250422093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO skupina', cwe_3='LN')
        obx.obx_5 = 'A'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh faktor', cwe_3='LN')
        obx_2.obx_5 = 'Pozitivní'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='1018-1', cwe_2='Screening protilátek', cwe_3='LN')
        obx_3.obx_5 = 'Negativní'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250425100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'WM00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250425100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6402168565', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Polák', xpn_2='Štěpán')
        pid.date_time_of_birth = '19640216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 2', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420615409844'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70004', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6402168565'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='CHIR')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250421160000')
        pv1.diet_type = CWE(cwe_1='NEM_TABOR')
        pv1.pending_location = PL(pl_1='20250425100000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'K80.2'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Kámen žlučníku bez cholecystitidy', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250422110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WM00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6401204206', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Černý', xpn_2='Roman')
        pid.date_time_of_birth = '19640120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 105', xad_3='České Budějovice', xad_5='370 01', xad_6='CZ')
        pid.pid_13 = '+420795571158'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70005', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6401204206'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='202', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD008')
        orc.orc_7 = '^^^20250423120000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD008')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Kultivace z rány', cwe_3='CPT')
        obr.observation_date_time = '20250422110000'
        obr.obr_16 = '50006^Pokorná^Monika^MUDr.'
        obr.obr_27 = '1^^^20250423120000^^R'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250424140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6401204206', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Černý', xpn_2='Roman')
        pid.date_time_of_birth = '19640120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 105', xad_3='České Budějovice', xad_5='370 01', xad_6='CZ')
        pid.pid_13 = '+420795571158'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70005', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6401204206'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='202', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD008')
        orc.orc_12 = '50006^Pokorná^Monika^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD008')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Kultivace z rány', cwe_3='CPT')
        obr.observation_date_time = '20250422110000'
        obr.results_rpt_status_chng_date_time = '20250424140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterie identifikace', cwe_3='LN')
        obx.obx_5 = 'Pseudomonas aeruginosa'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Citlivost ATB', cwe_3='LN')
        obx_2.obx_5 = 'Piperacilin/Tazobaktam-S; Meropenem-S; Ciprofloxacin-R; Gentamicin-S; Ceftazidim-S'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250425100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5556018627', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Králová', xpn_2='Lucie')
        pid.date_time_of_birth = '19550601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Čankovská 146', xad_3='Brno', xad_5='602 00', xad_6='CZ')
        pid.pid_13 = '+420730770032'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70003', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '5556018627'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IMUN', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='IMUN')

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
        orc.placer_order_number = EI(ei_1='WORD009')
        orc.orc_12 = '50003^Kučerová^Eliška^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD009')
        obr.universal_service_identifier = CWE(cwe_1='83036-9', cwe_2='Štítná žláza', cwe_3='LN')
        obr.observation_date_time = '20250425080000'
        obr.results_rpt_status_chng_date_time = '20250425100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '0.15'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Volný T4', cwe_3='LN')
        obx_2.obx_5 = '28.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Volný T3', cwe_3='LN')
        obx_3.obx_5 = '9.2'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250425110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'WM00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250425110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7656064365', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svobodová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19760606'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hrnčířská 77', xad_3='Náchod', xad_5='547 01', xad_6='CZ')
        pid.pid_13 = '+420677567854'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70002', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '7656064365'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='INT')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250426090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0012286265', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svoboda', xpn_2='Bedřich')
        pid.date_time_of_birth = '20001228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 135', xad_3='Šumperk', xad_5='787 01', xad_6='CZ')
        pid.pid_13 = '+420646313122'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70001', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '0012286265'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='101', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='INT')

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
        orc.placer_order_number = EI(ei_1='WORD010')
        orc.orc_12 = '50001^Hájek^Bohumil^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD010')
        obr.universal_service_identifier = CWE(cwe_1='5196-1', cwe_2='Hepatitidy panel', cwe_3='LN')
        obr.observation_date_time = '20250426070000'
        obr.results_rpt_status_chng_date_time = '20250426090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='5195-3', cwe_2='HBsAg', cwe_3='LN')
        obx.obx_5 = 'Negativní'
        obx.reference_range = 'Negativní'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='16933-4', cwe_2='Anti-HBs', cwe_3='LN')
        obx_2.obx_5 = 'Pozitivní'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='5199-5', cwe_2='Anti-HCV', cwe_3='LN')
        obx_3.obx_5 = 'Negativní'
        obx_3.reference_range = 'Negativní'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='7905-3', cwe_2='HIV Ag/Ab combo', cwe_3='LN')
        obx_4.obx_5 = 'Negativní'
        obx_4.reference_range = 'Negativní'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250426100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'WM00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT005')
        sch.event_reason = CWE(cwe_1='ODBER', cwe_2='Odběr krve')
        sch.sch_9 = '5'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^5^20250428063000^20250428063500'
        sch.filler_contact_person = XCN(xcn_1='50001', xcn_2='Hájek', xcn_3='Bohumil', xcn_4='MUDr.')
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7656064365', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svobodová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19760606'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hrnčířská 77', xad_3='Náchod', xad_5='547 01', xad_6='CZ')
        pid.pid_13 = '+420677567854'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70002', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '7656064365'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='INT')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='PHLEBOTOMY', cwe_2='Odběr krve')
        ais.start_date_time_offset = '20250428063000'
        ais.start_date_time_offset_units = CNE(cne_1='5')
        ais.duration = 'min'

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='WINMED')
        msh.receiving_facility = HD(hd_1='LAB_NEMTAB')
        msh.date_time_of_message = '20250427080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'WM00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250427080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7310192503', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pokorný', xpn_2='Vojtěch')
        pid.date_time_of_birth = '19731019'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Sokolská 188', xad_3='Znojmo', xad_5='669 02', xad_6='CZ')
        pid.pid_13 = '+420775897898'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='70006', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '7310192503'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/cz/cz-winmedicalc.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250428100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7656064365', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Svobodová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19760606'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hrnčířská 77', xad_3='Náchod', xad_5='547 01', xad_6='CZ')
        pid.pid_13 = '+420677567854'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70002', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '7656064365'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='INT')

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
        orc.placer_order_number = EI(ei_1='WORD011')
        orc.orc_12 = '50002^Hrubá^Věra^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD011')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20250428063000'
        obr.results_rpt_status_chng_date_time = '20250428100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '45'
        obx.units = CWE(cwe_1='mmol/mol')
        obx.reference_range = '<42'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx_2.obx_5 = '7.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.9-5.6'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-winmedicalc.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WINMED')
        msh.sending_facility = HD(hd_1='LAB_NEMTAB')
        msh.receiving_application = HD(hd_1='NIS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250429090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'WM00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6401204206', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Černý', xpn_2='Roman')
        pid.date_time_of_birth = '19640120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 105', xad_3='České Budějovice', xad_5='370 01', xad_6='CZ')
        pid.pid_13 = '+420795571158'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='70005', cx_4='NEM_TABOR', cx_5='VN')
        pid.pid_19 = '6401204206'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='202', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='WORD012')
        orc.orc_12 = '50006^Pokorná^Monika^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WORD012')
        obr.universal_service_identifier = CWE(cwe_1='TM', cwe_2='Tumorové markery', cwe_3='LOCAL')
        obr.observation_date_time = '20250429070000'
        obr.results_rpt_status_chng_date_time = '20250429090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2039-6', cwe_2='CEA', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '<5.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10886-0', cwe_2='CA 19-9', cwe_3='LN')
        obx_2.obx_5 = '18.5'
        obx_2.units = CWE(cwe_1='kU/L')
        obx_2.reference_range = '<37'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='19540-4', cwe_2='PSA celkový', cwe_3='LN')
        obx_3.obx_5 = '2.8'
        obx_3.units = CWE(cwe_1='ug/L')
        obx_3.reference_range = '<4.0'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
        )
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

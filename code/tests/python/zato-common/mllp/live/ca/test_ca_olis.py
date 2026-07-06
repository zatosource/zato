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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult
from zato.hl7v2.v2_9.messages import ORU_R01
from zato.hl7v2.v2_9.segments import MSH, NTE, OBR, OBX, ORC, PID

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-olis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-olis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='TORONTO_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Amrit', xpn_3='Kaur')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='300 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7891234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100001')
        orc.filler_order_number = EI(ei_1='OL200001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509070000'
        orc.orc_12 = '88901^Martinez^Carlos^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100001')
        obr.filler_order_number = EI(ei_1='OL200001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20260509064500'
        obr.obr_16 = '88901^Martinez^Carlos^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '125'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx_2.obx_5 = '6.8'
        obx_2.units = CWE(cwe_1='x10E9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_3.obx_5 = '4.22'
        obx_3.units = CWE(cwe_1='x10E12/L')
        obx_3.reference_range = '3.80-5.20'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_4.obx_5 = '86.3'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80.0-100.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_5.obx_5 = '198'
        obx_5.units = CWE(cwe_1='x10E9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophils', cwe_3='LN')
        obx_6.obx_5 = '3.9'
        obx_6.units = CWE(cwe_1='x10E9/L')
        obx_6.reference_range = '2.0-7.5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymphocytes', cwe_3='LN')
        obx_7.obx_5 = '2.1'
        obx_7.units = CWE(cwe_1='x10E9/L')
        obx_7.reference_range = '1.0-4.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='742-7', cwe_2='Monocytes', cwe_3='LN')
        obx_8.obx_5 = '0.5'
        obx_8.units = CWE(cwe_1='x10E9/L')
        obx_8.reference_range = '0.2-1.0'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

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
    """ Based on live/ca/ca-olis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9876543210', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1="O'Brien", xpn_2='Seamus', xpn_3='Patrick')
        pid.date_time_of_birth = '19780105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Charles St E', xad_3='Toronto', xad_4='ON', xad_5='M4Y 1S2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^9251234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100002')
        orc.filler_order_number = EI(ei_1='OL200002')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509073000'
        orc.orc_12 = '99012^Kim^Grace^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100002')
        obr.filler_order_number = EI(ei_1='OL200002')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20260509070000'
        obr.obr_16 = '99012^Kim^Grace^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '88'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '5.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_4.obx_5 = '2.42'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '2.10-2.55'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_5.obx_5 = '141'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_6.obx_5 = '4.0'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_7.obx_5 = '103'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '98-107'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate', cwe_3='LN')
        obx_8.obx_5 = '25'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '22-29'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_9.obx_5 = '22'
        obx_9.units = CWE(cwe_1='U/L')
        obx_9.reference_range = '7-56'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_10.obx_5 = '19'
        obx_10.units = CWE(cwe_1='U/L')
        obx_10.reference_range = '10-40'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

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
        order_observation.observation_9 = observation_9
        order_observation.observation_10 = observation_10

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
    """ Based on live/ca/ca-olis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='DYNACARE_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Ravi', xpn_3='Kumar')
        pid.date_time_of_birth = '19880912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='150 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1G9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^905^5289876'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100003')
        orc.filler_order_number = EI(ei_1='OL200003')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_12 = '77123^Anderson^Michael^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100003')
        obr.filler_order_number = EI(ei_1='OL200003')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinalysis complete', cwe_3='LN')
        obr.observation_date_time = '20260509084500'
        obr.obr_16 = '77123^Anderson^Michael^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx.obx_5 = 'Hazy^^L'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx_2.obx_5 = 'Amber^^L'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '5.5'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specific gravity', cwe_3='LN')
        obx_4.obx_5 = '1.025'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucose UA', cwe_3='LN')
        obx_5.obx_5 = 'Negative^^L'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein UA', cwe_3='LN')
        obx_6.obx_5 = 'Trace^^L'
        obx_6.reference_range = 'Negative'
        obx_6.interpretation_codes = CWE(cwe_1='A')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CWE'
        obx_7.observation_identifier = CWE(cwe_1='20405-7', cwe_2='Leukocyte esterase', cwe_3='LN')
        obx_7.obx_5 = '1+^^L'
        obx_7.reference_range = 'Negative'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CWE'
        obx_8.observation_identifier = CWE(cwe_1='5802-4', cwe_2='Nitrite', cwe_3='LN')
        obx_8.obx_5 = 'Positive^^L'
        obx_8.reference_range = 'Negative'
        obx_8.interpretation_codes = CWE(cwe_1='A')
        obx_8.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Suggest urine culture to rule out UTI.'

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
    """ Based on live/ca/ca-olis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='TORONTO_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Ravi', xpn_3='Kumar')
        pid.date_time_of_birth = '19880912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='150 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1G9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^905^5289876'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100004')
        orc.filler_order_number = EI(ei_1='OL200004')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_12 = '77123^Anderson^Michael^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100004')
        obr.filler_order_number = EI(ei_1='OL200004')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine culture', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_16 = '77123^Anderson^Michael^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='564-5', cwe_2='Colony count', cwe_3='LN')
        obx_2.obx_5 = 'Greater than 100,000 CFU/mL'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Susceptibility Ampicillin', cwe_3='LN')
        obx_3.obx_5 = 'Resistant'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18945-6', cwe_2='Susceptibility Ciprofloxacin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Susceptibility Nitrofurantoin', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Susceptibility TMP-SMX', cwe_3='LN')
        obx_6.obx_5 = 'Resistant'
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
    """ Based on live/ca/ca-olis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Williams', xpn_2='David', xpn_3='Anthony')
        pid.date_time_of_birth = '19550718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Dunlop St W', xad_3='Barrie', xad_4='ON', xad_5='L4N 1A4', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^705^7251234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100005')
        orc.filler_order_number = EI(ei_1='OL200005')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510060000'
        orc.orc_12 = '66234^Wright^Patricia^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100005')
        obr.filler_order_number = EI(ei_1='OL200005')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid panel', cwe_3='LN')
        obr.observation_date_time = '20260510055000'
        obr.obr_16 = '66234^Wright^Patricia^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510073000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterol total', cwe_3='LN')
        obx.obx_5 = '6.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '0.0-5.2'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '2.1'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '0.0-1.7'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '1.0-999.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol calculated', cwe_3='LN')
        obx_4.obx_5 = '4.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '0.0-3.4'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Total/HDL ratio', cwe_3='LN')
        obx_5.obx_5 = '5.6'
        obx_5.reference_range = '0.0-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ca/ca-olis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='DYNACARE_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Williams', xpn_2='David', xpn_3='Anthony')
        pid.date_time_of_birth = '19550718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Dunlop St W', xad_3='Barrie', xad_4='ON', xad_5='L4N 1A4', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^705^7251234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100006')
        orc.filler_order_number = EI(ei_1='OL200006')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510060000'
        orc.orc_12 = '66234^Wright^Patricia^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100006')
        obr.filler_order_number = EI(ei_1='OL200006')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20260510055000'
        obr.obr_16 = '66234^Wright^Patricia^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c IFCC', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '20-42'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Above target. Consider intensification of diabetes management.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
    """ Based on live/ca/ca-olis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Amrit', xpn_3='Kaur')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='300 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7891234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100007')
        orc.filler_order_number = EI(ei_1='OL200007')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510080000'
        orc.orc_12 = '88901^Martinez^Carlos^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100007')
        obr.filler_order_number = EI(ei_1='OL200007')
        obr.universal_service_identifier = CWE(cwe_1='34896-2', cwe_2='Thyroid panel', cwe_3='LN')
        obr.observation_date_time = '20260510074500'
        obr.obr_16 = '88901^Martinez^Carlos^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '2.4'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '15.8'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-olis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='MT_SINAI_LAB')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7654321098', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Chen', xpn_2='Mei', xpn_3='Lin')
        pid.date_time_of_birth = '19920601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='52 Gerrard St E', xad_3='Toronto', xad_4='ON', xad_5='M5B 1G3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^5551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100008')
        orc.filler_order_number = EI(ei_1='OL200008')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510090000'
        orc.orc_12 = '44567^Hughes^Jennifer^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100008')
        obr.filler_order_number = EI(ei_1='OL200008')
        obr.universal_service_identifier = CWE(cwe_1='21482-5', cwe_2='Enhanced FTS', cwe_3='LN')
        obr.observation_date_time = '20260510084500'
        obr.obr_16 = '44567^Hughes^Jennifer^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='33629-2', cwe_2='AFP MoM', cwe_3='LN')
        obx.obx_5 = '1.02'
        obx.units = CWE(cwe_1='MoM')
        obx.reference_range = '0.50-2.50'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='19080-1', cwe_2='hCG', cwe_3='LN')
        obx_2.obx_5 = '45000'
        obx_2.units = CWE(cwe_1='IU/L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='49246-2', cwe_2='PAPP-A MoM', cwe_3='LN')
        obx_3.obx_5 = '0.85'
        obx_3.units = CWE(cwe_1='MoM')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='99999-9', cwe_2='Risk assessment', cwe_3='LOCAL')
        obx_4.obx_5 = 'Down syndrome risk: 1 in 8500 (screen negative). Trisomy 18 risk: 1 in 25000 (screen negative).'
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
    """ Based on live/ca/ca-olis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='PHO_LAB')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fernandez', xpn_2='Maria', xpn_3='Elena')
        pid.date_time_of_birth = '19750314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='200 King St W', xad_3='Kitchener', xad_4='ON', xad_5='N2G 4V2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^5789012'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100009')
        orc.filler_order_number = EI(ei_1='OL200009')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '55678^Brown^Thomas^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100009')
        obr.filler_order_number = EI(ei_1='OL200009')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA NAA', cwe_3='LN')
        obr.observation_date_time = '20260509074500'
        obr.obr_16 = '55678^Brown^Thomas^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA', cwe_3='LN')
        obx.obx_5 = '260415000^Not detected^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

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
    """ Based on live/ca/ca-olis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='OTTAWA_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8765432109', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lebrun', xpn_2='Jacques', xpn_3='Henri')
        pid.date_time_of_birth = '19450822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='101 Rideau St', xad_3='Ottawa', xad_4='ON', xad_5='K1N 5X1', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^613^5551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100010')
        orc.filler_order_number = EI(ei_1='OL200010')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509140000'
        orc.orc_12 = '33789^Nguyen^Thanh^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100010')
        obr.filler_order_number = EI(ei_1='OL200010')
        obr.universal_service_identifier = CWE(cwe_1='87040-2', cwe_2='Blood culture', cwe_3='LN')
        obr.observation_date_time = '20260509134500'
        obr.obr_16 = '33789^Nguyen^Thanh^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '3092008^Staphylococcus aureus^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Susceptibility Oxacillin', cwe_3='LN')
        obx_2.obx_5 = 'Susceptible (MSSA)'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18964-7', cwe_2='Susceptibility Vancomycin', cwe_3='LN')
        obx_3.obx_5 = 'Susceptible MIC 1 ug/mL'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18878-9', cwe_2='Susceptibility Clindamycin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18886-2', cwe_2='Susceptibility Doxycycline', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
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
    """ Based on live/ca/ca-olis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='TORONTO_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8765432109', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lebrun', xpn_2='Jacques', xpn_3='Henri')
        pid.date_time_of_birth = '19450822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='101 Rideau St', xad_3='Ottawa', xad_4='ON', xad_5='K1N 5X1', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^613^5551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100011')
        orc.filler_order_number = EI(ei_1='OL200011')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510070000'
        orc.orc_12 = '33789^Nguyen^Thanh^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100011')
        obr.filler_order_number = EI(ei_1='OL200011')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Coagulation panel', cwe_3='LN')
        obr.observation_date_time = '20260510064500'
        obr.obr_16 = '33789^Nguyen^Thanh^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '2.3'
        obx_2.reference_range = '0.9-1.1'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '32.0'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25.0-35.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-olis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Amrit', xpn_3='Kaur')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='300 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7891234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100012')
        orc.filler_order_number = EI(ei_1='OL200012')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511070000'
        orc.orc_12 = '88901^Martinez^Carlos^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100012')
        obr.filler_order_number = EI(ei_1='OL200012')
        obr.universal_service_identifier = CWE(cwe_1='2500-7', cwe_2='Iron panel', cwe_3='LN')
        obr.observation_date_time = '20260511064500'
        obr.obr_16 = '88901^Martinez^Carlos^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Iron', cwe_3='LN')
        obx.obx_5 = '8'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '9-30'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2502-3', cwe_2='Transferrin saturation', cwe_3='LN')
        obx_2.obx_5 = '12'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '20-50'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_3.obx_5 = '10'
        obx_3.units = CWE(cwe_1='ug/L')
        obx_3.reference_range = '12-150'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3034-6', cwe_2='TIBC', cwe_3='LN')
        obx_4.obx_5 = '78'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '45-72'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Iron deficiency pattern. Correlate clinically.'

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
    """ Based on live/ca/ca-olis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='DYNACARE_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9876543210', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1="O'Brien", xpn_2='Seamus', xpn_3='Patrick')
        pid.date_time_of_birth = '19780105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Charles St E', xad_3='Toronto', xad_4='ON', xad_5='M4Y 1S2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^9251234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100013')
        orc.filler_order_number = EI(ei_1='OL200013')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510073000'
        orc.orc_12 = '99012^Kim^Grace^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100013')
        obr.filler_order_number = EI(ei_1='OL200013')
        obr.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obr.observation_date_time = '20260510070000'
        obr.obr_16 = '99012^Kim^Grace^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obx.obx_5 = '1.8'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '0.0-4.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

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
    """ Based on live/ca/ca-olis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='PHO_LAB')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fernandez', xpn_2='Maria', xpn_3='Elena')
        pid.date_time_of_birth = '19750314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='200 King St W', xad_3='Kitchener', xad_4='ON', xad_5='N2G 4V2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^5789012'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100014')
        orc.filler_order_number = EI(ei_1='OL200014')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511080000'
        orc.orc_12 = '55678^Brown^Thomas^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100014')
        obr.filler_order_number = EI(ei_1='OL200014')
        obr.universal_service_identifier = CWE(cwe_1='24360-0', cwe_2='Hepatitis B panel', cwe_3='LN')
        obr.observation_date_time = '20260511074500'
        obr.obr_16 = '55678^Brown^Thomas^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='5195-3', cwe_2='HBsAg', cwe_3='LN')
        obx.obx_5 = '260385009^Negative^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='16935-9', cwe_2='Anti-HBs', cwe_3='LN')
        obx_2.obx_5 = '260373001^Positive^SCT'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='16935-9', cwe_2='Anti-HBs quantitative', cwe_3='LN')
        obx_3.obx_5 = '450'
        obx_3.units = CWE(cwe_1='mIU/mL')
        obx_3.reference_range = '10-999'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='22322-2', cwe_2='Anti-HBc total', cwe_3='LN')
        obx_4.obx_5 = '260385009^Negative^SCT'
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
    """ Based on live/ca/ca-olis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260510160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Amrit', xpn_3='Kaur')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='300 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7891234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100015')
        orc.filler_order_number = EI(ei_1='OL200015')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510080000'
        orc.orc_12 = '88901^Martinez^Carlos^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100015')
        obr.filler_order_number = EI(ei_1='OL200015')
        obr.universal_service_identifier = CWE(cwe_1='1989-3', cwe_2='25-Hydroxyvitamin D', cwe_3='LN')
        obr.observation_date_time = '20260510074500'
        obr.obr_16 = '88901^Martinez^Carlos^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='25-OH Vitamin D', cwe_3='LN')
        obx.obx_5 = '42'
        obx.units = CWE(cwe_1='nmol/L')
        obx.reference_range = '75-250'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Insufficiency. Supplementation recommended.'

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
    """ Based on live/ca/ca-olis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='CML_HEALTHCARE')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fernandez', xpn_2='Maria', xpn_3='Elena')
        pid.date_time_of_birth = '19750314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='200 King St W', xad_3='Kitchener', xad_4='ON', xad_5='N2G 4V2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^5789012'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100016')
        orc.filler_order_number = EI(ei_1='OL200016')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510100000'
        orc.orc_12 = '55678^Brown^Thomas^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100016')
        obr.filler_order_number = EI(ei_1='OL200016')
        obr.universal_service_identifier = CWE(cwe_1='10524-7', cwe_2='Cytology cervical', cwe_3='LN')
        obr.observation_date_time = '20260510094500'
        obr.obr_16 = '55678^Brown^Thomas^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='10524-7', cwe_2='Cervical cytology', cwe_3='LN')
        obx.obx_5 = '373887005^Negative for intraepithelial lesion or malignancy^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Cytology Report', cwe_3='CML')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEP'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0K'
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
    """ Based on live/ca/ca-olis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='TORONTO_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260511170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Ravi', xpn_3='Kumar')
        pid.date_time_of_birth = '19880912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='150 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1G9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^905^5289876'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100017')
        orc.filler_order_number = EI(ei_1='OL200017')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511090000'
        orc.orc_12 = '77123^Anderson^Michael^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100017')
        obr.filler_order_number = EI(ei_1='OL200017')
        obr.universal_service_identifier = CWE(cwe_1='31017-7', cwe_2='tTG IgA', cwe_3='LN')
        obr.observation_date_time = '20260511084500'
        obr.obr_16 = '77123^Anderson^Michael^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='31017-7', cwe_2='tTG IgA', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='U/mL')
        obx.reference_range = '0.0-20.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2458-8', cwe_2='IgA total', cwe_3='LN')
        obx_2.obx_5 = '2.5'
        obx_2.units = CWE(cwe_1='g/L')
        obx_2.reference_range = '0.7-4.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-olis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='OTTAWA_GEN')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260512020000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8765432109', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lebrun', xpn_2='Jacques', xpn_3='Henri')
        pid.date_time_of_birth = '19450822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='101 Rideau St', xad_3='Ottawa', xad_4='ON', xad_5='K1N 5X1', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^613^5551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100018')
        orc.filler_order_number = EI(ei_1='OL200018')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512010000'
        orc.orc_12 = '33789^Nguyen^Thanh^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100018')
        obr.filler_order_number = EI(ei_1='OL200018')
        obr.universal_service_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I hs', cwe_3='LN')
        obr.observation_date_time = '20260512005000'
        obr.obr_16 = '33789^Nguyen^Thanh^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512015000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='hs-Troponin I', cwe_3='LN')
        obx.obx_5 = '256'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '0-26'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Critical value. Physician notified 0155h.'

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
    """ Based on live/ca/ca-olis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='UHN_PATH_LAB')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260512100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9876543210', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1="O'Brien", xpn_2='Seamus', xpn_3='Patrick')
        pid.date_time_of_birth = '19780105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Charles St E', xad_3='Toronto', xad_4='ON', xad_5='M4Y 1S2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^9251234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100019')
        orc.filler_order_number = EI(ei_1='OL200019')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510140000'
        orc.orc_12 = '99012^Kim^Grace^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100019')
        obr.filler_order_number = EI(ei_1='OL200019')
        obr.universal_service_identifier = CWE(cwe_1='88305-8', cwe_2='Surgical pathology', cwe_3='LN')
        obr.observation_date_time = '20260510134500'
        obr.obr_16 = '99012^Kim^Grace^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='88305-8', cwe_2='Path interpretation', cwe_3='LN')
        obx.obx_5 = 'Colon biopsy: Tubular adenoma with low-grade dysplasia. Margins clear. No invasive carcinoma.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Histopathology Slide', cwe_3='UHN')
        obx_2.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgo'
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
    """ Based on live/ca/ca-olis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS_LIS')
        msh.sending_facility = HD(hd_1='DYNACARE_ON')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ON_EHIS')
        msh.date_time_of_message = '20260512130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Ravi', xpn_3='Kumar')
        pid.date_time_of_birth = '19880912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='150 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1G9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^905^5289876'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='OL100020')
        orc.filler_order_number = EI(ei_1='OL200020')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512080000'
        orc.orc_12 = '77123^Anderson^Michael^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='OL100020')
        obr.filler_order_number = EI(ei_1='OL200020')
        obr.universal_service_identifier = CWE(cwe_1='3393-5', cwe_2='Urine drug screen', cwe_3='LN')
        obr.observation_date_time = '20260512074500'
        obr.obr_16 = '77123^Anderson^Michael^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512123000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='3397-6', cwe_2='Cocaine metabolites', cwe_3='LN')
        obx.obx_5 = '260385009^Negative^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='3426-3', cwe_2='Opiates', cwe_3='LN')
        obx_2.obx_5 = '260385009^Negative^SCT'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='3416-4', cwe_2='THC', cwe_3='LN')
        obx_3.obx_5 = '260385009^Negative^SCT'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='3390-1', cwe_2='Benzodiazepines', cwe_3='LN')
        obx_4.obx_5 = '260385009^Negative^SCT'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='3349-7', cwe_2='Amphetamines', cwe_3='LN')
        obx_5.obx_5 = '260385009^Negative^SCT'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='19659-2', cwe_2='Fentanyl', cwe_3='LN')
        obx_6.obx_5 = '260385009^Negative^SCT'
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

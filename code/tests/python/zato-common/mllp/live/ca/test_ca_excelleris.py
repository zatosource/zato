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

_md_path = md_path_for('ca', 'ca-excelleris.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-excelleris.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100001')
        orc.filler_order_number = EI(ei_1='EX200001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509064500'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100001')
        obr.filler_order_number = EI(ei_1='EX200001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20260509062000'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '138'
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
        obx_2.obx_5 = '7.5'
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
        obx_3.obx_5 = '4.55'
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
        obx_4.obx_5 = '89.2'
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
        obx_5.obx_5 = '267'
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
        obx_6.obx_5 = '4.2'
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
        obx_7.obx_5 = '2.5'
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
        obx_8.obx_5 = '0.6'
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
    """ Based on live/ca/ca-excelleris.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5283716094', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Yamamoto', xpn_2='Kenji', xpn_3='Ryo')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='1450 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6G 1B9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^4827193'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100002')
        orc.filler_order_number = EI(ei_1='EX200002')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509070000'
        orc.orc_12 = '56723^Andersson^Linnea^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100002')
        obr.filler_order_number = EI(ei_1='EX200002')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20260509063000'
        obr.obr_16 = '56723^Andersson^Linnea^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.4'
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
        obx_2.obx_5 = '95'
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
        obx_3.obx_5 = '6.2'
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
        obx_4.obx_5 = '2.38'
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
        obx_5.obx_5 = '139'
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
        obx_6.obx_5 = '4.3'
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
        obx_7.obx_5 = '101'
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
        obx_8.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_8.obx_5 = '35'
        obx_8.units = CWE(cwe_1='U/L')
        obx_8.reference_range = '7-56'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_9.obx_5 = '28'
        obx_9.units = CWE(cwe_1='U/L')
        obx_9.reference_range = '10-40'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
    """ Based on live/ca/ca-excelleris.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100003')
        orc.filler_order_number = EI(ei_1='EX200003')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509070000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100003')
        obr.filler_order_number = EI(ei_1='EX200003')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid panel', cwe_3='LN')
        obr.observation_date_time = '20260509063000'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterol total', cwe_3='LN')
        obx.obx_5 = '5.1'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '0.0-5.2'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '1.4'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '0.0-1.7'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.6'
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
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '2.9'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '0.0-3.4'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Total/HDL ratio', cwe_3='LN')
        obx_5.obx_5 = '3.2'
        obx_5.reference_range = '0.0-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-excelleris.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260510083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5283716094', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Yamamoto', xpn_2='Kenji', xpn_3='Ryo')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='1450 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6G 1B9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^4827193'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100004')
        orc.filler_order_number = EI(ei_1='EX200004')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510063000'
        orc.orc_12 = '56723^Andersson^Linnea^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100004')
        obr.filler_order_number = EI(ei_1='EX200004')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20260510060000'
        obr.obr_16 = '56723^Andersson^Linnea^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx.obx_5 = '6.2'
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
        obx_2.obx_5 = '44'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '20-42'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'At risk. Repeat in 3-6 months. Lifestyle counseling recommended.'

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
    """ Based on live/ca/ca-excelleris.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260510110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100005')
        orc.filler_order_number = EI(ei_1='EX200005')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510070000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100005')
        obr.filler_order_number = EI(ei_1='EX200005')
        obr.universal_service_identifier = CWE(cwe_1='34896-2', cwe_2='Thyroid panel', cwe_3='LN')
        obr.observation_date_time = '20260510064500'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '1.8'
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
        obx_2.obx_5 = '14.5'
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
    """ Based on live/ca/ca-excelleris.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260510140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7148293051', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Brar', xpn_2='Gurpreet', xpn_3='Singh')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7820 Granville St', xad_3='Vancouver', xad_4='BC', xad_5='V6P 4Z3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^3274182'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100006')
        orc.filler_order_number = EI(ei_1='EX200006')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510070000'
        orc.orc_12 = '78234^Schmidt^Hans^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100006')
        obr.filler_order_number = EI(ei_1='EX200006')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='Renal function panel', cwe_3='LN')
        obr.observation_date_time = '20260510063000'
        obr.obr_16 = '78234^Schmidt^Hans^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx.obx_5 = '155'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '62-115'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_2.obx_5 = '38'
        obx_2.units = CWE(cwe_1='mL/min/1.73m2')
        obx_2.reference_range = '60-999'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '12.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '137'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '5.3'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='14959-1', cwe_2='Urine ACR', cwe_3='LN')
        obx_6.obx_5 = '18.5'
        obx_6.units = CWE(cwe_1='mg/mmol')
        obx_6.reference_range = '0.0-2.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'CKD Stage 3b. Nephrology referral recommended.'

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
    """ Based on live/ca/ca-excelleris.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5283716094', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Yamamoto', xpn_2='Kenji', xpn_3='Ryo')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='1450 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6G 1B9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^4827193'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100007')
        orc.filler_order_number = EI(ei_1='EX200007')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511063000'
        orc.orc_12 = '56723^Andersson^Linnea^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100007')
        obr.filler_order_number = EI(ei_1='EX200007')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Hepatic function panel', cwe_3='LN')
        obr.observation_date_time = '20260511060000'
        obr.obr_16 = '56723^Andersson^Linnea^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '42'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '38'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin total', cwe_3='LN')
        obx_3.obx_5 = '15'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '3-21'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline phosphatase', cwe_3='LN')
        obx_4.obx_5 = '95'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '44-147'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total protein', cwe_3='LN')
        obx_5.obx_5 = '72'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '60-80'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '42'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-50'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2324-2', cwe_2='GGT', cwe_3='LN')
        obx_7.obx_5 = '68'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '8-61'
        obx_7.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ca/ca-excelleris.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7148293051', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Brar', xpn_2='Gurpreet', xpn_3='Singh')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7820 Granville St', xad_3='Vancouver', xad_4='BC', xad_5='V6P 4Z3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^3274182'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100008')
        orc.filler_order_number = EI(ei_1='EX200008')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511070000'
        orc.orc_12 = '78234^Schmidt^Hans^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100008')
        obr.filler_order_number = EI(ei_1='EX200008')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinalysis complete', cwe_3='LN')
        obr.observation_date_time = '20260511064500'
        obr.obr_16 = '78234^Schmidt^Hans^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx.obx_5 = 'Clear^^L'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx_2.obx_5 = 'Yellow^^L'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '6.5'
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
        obx_4.obx_5 = '1.018'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='14959-1', cwe_2='Protein/Creatinine ratio', cwe_3='LN')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='mg/mmol')
        obx_5.reference_range = '0-15'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucose UA', cwe_3='LN')
        obx_6.obx_5 = 'Negative^^L'
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
    """ Based on live/ca/ca-excelleris.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6294817503', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Donovan', xpn_2='Olivia', xpn_3='Grace')
        pid.date_time_of_birth = '19961014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='543 Davie St', xad_3='Vancouver', xad_4='BC', xad_5='V6B 2G6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^2718394'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100009')
        orc.filler_order_number = EI(ei_1='EX200009')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510100000'
        orc.orc_12 = '23489^Hamilton^Connor^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100009')
        obr.filler_order_number = EI(ei_1='EX200009')
        obr.universal_service_identifier = CWE(cwe_1='36902-5', cwe_2='CT/GC NAAT', cwe_3='LN')
        obr.observation_date_time = '20260510094500'
        obr.obr_16 = '23489^Hamilton^Connor^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='21613-5', cwe_2='Chlamydia trachomatis NAAT', cwe_3='LN')
        obx.obx_5 = '260385009^Not detected^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='21415-5', cwe_2='Neisseria gonorrhoeae NAAT', cwe_3='LN')
        obx_2.obx_5 = '260385009^Not detected^SCT'
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
    """ Based on live/ca/ca-excelleris.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100010')
        orc.filler_order_number = EI(ei_1='EX200010')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511080000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100010')
        obr.filler_order_number = EI(ei_1='EX200010')
        obr.universal_service_identifier = CWE(cwe_1='2500-7', cwe_2='Iron panel', cwe_3='LN')
        obr.observation_date_time = '20260511074500'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Iron', cwe_3='LN')
        obx.obx_5 = '15'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '9-30'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2502-3', cwe_2='Transferrin saturation', cwe_3='LN')
        obx_2.obx_5 = '28'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '20-50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_3.obx_5 = '45'
        obx_3.units = CWE(cwe_1='ug/L')
        obx_3.reference_range = '12-150'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3034-6', cwe_2='TIBC', cwe_3='LN')
        obx_4.obx_5 = '55'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '45-72'
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
    """ Based on live/ca/ca-excelleris.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5283716094', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Yamamoto', xpn_2='Kenji', xpn_3='Ryo')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='1450 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6G 1B9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^4827193'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100011')
        orc.filler_order_number = EI(ei_1='EX200011')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512063000'
        orc.orc_12 = '56723^Andersson^Linnea^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100011')
        obr.filler_order_number = EI(ei_1='EX200011')
        obr.universal_service_identifier = CWE(cwe_1='1989-3', cwe_2='25-Hydroxyvitamin D', cwe_3='LN')
        obr.observation_date_time = '20260512060000'
        obr.obr_16 = '56723^Andersson^Linnea^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='25-OH Vitamin D', cwe_3='LN')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='nmol/L')
        obx.reference_range = '75-250'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Insufficiency. Supplement with 1000 IU daily, recheck in 3 months.'

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
    """ Based on live/ca/ca-excelleris.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7148293051', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Brar', xpn_2='Gurpreet', xpn_3='Singh')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7820 Granville St', xad_3='Vancouver', xad_4='BC', xad_5='V6P 4Z3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^3274182'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100012')
        orc.filler_order_number = EI(ei_1='EX200012')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512063000'
        orc.orc_12 = '78234^Schmidt^Hans^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100012')
        obr.filler_order_number = EI(ei_1='EX200012')
        obr.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obr.observation_date_time = '20260512060000'
        obr.obr_16 = '78234^Schmidt^Hans^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA total', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '0.0-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='19197-3', cwe_2='PSA free', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='ug/L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='12841-3', cwe_2='Free/Total PSA ratio', cwe_3='LN')
        obx_3.obx_5 = '15.5'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>25'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Elevated PSA with low free/total ratio. Urology referral recommended.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/ca/ca-excelleris.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6294817503', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Donovan', xpn_2='Olivia', xpn_3='Grace')
        pid.date_time_of_birth = '19961014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='543 Davie St', xad_3='Vancouver', xad_4='BC', xad_5='V6B 2G6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^2718394'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100013')
        orc.filler_order_number = EI(ei_1='EX200013')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510130000'
        orc.orc_12 = '23489^Hamilton^Connor^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100013')
        obr.filler_order_number = EI(ei_1='EX200013')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine culture', cwe_3='LN')
        obr.observation_date_time = '20260510124500'
        obr.obr_16 = '23489^Hamilton^Connor^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512133000'
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
        obx_3.observation_identifier = CWE(cwe_1='18945-6', cwe_2='Susceptibility Ciprofloxacin', cwe_3='LN')
        obx_3.obx_5 = 'Susceptible'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Susceptibility Nitrofurantoin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Susceptibility TMP-SMX', cwe_3='LN')
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
    """ Based on live/ca/ca-excelleris.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100014')
        orc.filler_order_number = EI(ei_1='EX200014')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512080000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100014')
        obr.filler_order_number = EI(ei_1='EX200014')
        obr.universal_service_identifier = CWE(cwe_1='31017-7', cwe_2='tTG IgA', cwe_3='LN')
        obr.observation_date_time = '20260512074500'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='31017-7', cwe_2='tTG IgA', cwe_3='LN')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='U/mL')
        obx.reference_range = '0.0-20.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2458-8', cwe_2='IgA total', cwe_3='LN')
        obx_2.obx_5 = '3.2'
        obx_2.units = CWE(cwe_1='g/L')
        obx_2.reference_range = '0.7-4.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Strongly positive tTG-IgA. Celiac disease likely. Gastroenterology referral for biopsy.'

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
    """ Based on live/ca/ca-excelleris.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7148293051', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Brar', xpn_2='Gurpreet', xpn_3='Singh')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7820 Granville St', xad_3='Vancouver', xad_4='BC', xad_5='V6P 4Z3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^3274182'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100015')
        orc.filler_order_number = EI(ei_1='EX200015')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512080000'
        orc.orc_12 = '78234^Schmidt^Hans^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100015')
        obr.filler_order_number = EI(ei_1='EX200015')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Coagulation panel', cwe_3='LN')
        obr.observation_date_time = '20260512074500'
        obr.obr_16 = '78234^Schmidt^Hans^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.0'
        obx_2.reference_range = '0.9-1.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '29.5'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25.0-35.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-excelleris.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5283716094', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Yamamoto', xpn_2='Kenji', xpn_3='Ryo')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='1450 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6G 1B9', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^4827193'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100016')
        orc.filler_order_number = EI(ei_1='EX200016')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511130000'
        orc.orc_12 = '56723^Andersson^Linnea^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100016')
        obr.filler_order_number = EI(ei_1='EX200016')
        obr.universal_service_identifier = CWE(cwe_1='71020-2', cwe_2='Chest X-ray', cwe_3='LN')
        obr.observation_date_time = '20260511124500'
        obr.obr_16 = '56723^Andersson^Linnea^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Chest X-ray Report', cwe_3='EXCELLERIS')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0K'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='71020-2', cwe_2='CXR Impression', cwe_3='LN')
        obx_2.obx_5 = 'Heart size normal. Lungs clear bilaterally. No pleural effusion or pneumothorax. No acute cardiopulmonary abnormality.'
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
    """ Based on live/ca/ca-excelleris.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100017')
        orc.filler_order_number = EI(ei_1='EX200017')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512080000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100017')
        obr.filler_order_number = EI(ei_1='EX200017')
        obr.universal_service_identifier = CWE(cwe_1='2132-9', cwe_2='Vitamin B12', cwe_3='LN')
        obr.observation_date_time = '20260512074500'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2132-9', cwe_2='Vitamin B12', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='pmol/L')
        obx.reference_range = '138-652'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2284-8', cwe_2='Folate', cwe_3='LN')
        obx_2.obx_5 = '28'
        obx_2.units = CWE(cwe_1='nmol/L')
        obx_2.reference_range = '7-45'
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
    """ Based on live/ca/ca-excelleris.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6294817503', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Donovan', xpn_2='Olivia', xpn_3='Grace')
        pid.date_time_of_birth = '19961014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='543 Davie St', xad_3='Vancouver', xad_4='BC', xad_5='V6B 2G6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^2718394'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100018')
        orc.filler_order_number = EI(ei_1='EX200018')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512090000'
        orc.orc_12 = '23489^Hamilton^Connor^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100018')
        obr.filler_order_number = EI(ei_1='EX200018')
        obr.universal_service_identifier = CWE(cwe_1='22461-8', cwe_2='Syphilis serology', cwe_3='LN')
        obr.observation_date_time = '20260512084500'
        obr.obr_16 = '23489^Hamilton^Connor^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512173000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='22461-8', cwe_2='Syphilis EIA', cwe_3='LN')
        obx.obx_5 = '260385009^Non-reactive^SCT'
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
    """ Based on live/ca/ca-excelleris.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PLIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512190000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4129865037', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Hannah', xpn_3='Rose')
        pid.date_time_of_birth = '19720519'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2847 West 4th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6K 1R6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^7382514'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100019')
        orc.filler_order_number = EI(ei_1='EX200019')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512100000'
        orc.orc_12 = '34521^Patel^Amrita^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100019')
        obr.filler_order_number = EI(ei_1='EX200019')
        obr.universal_service_identifier = CWE(cwe_1='38269-7', cwe_2='DEXA scan', cwe_3='LN')
        obr.observation_date_time = '20260512094500'
        obr.obr_16 = '34521^Patel^Amrita^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512183000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='38265-5', cwe_2='Lumbar spine T-score', cwe_3='LN')
        obx.obx_5 = '-1.8'
        obx.reference_range = '>-1.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='38267-1', cwe_2='Femoral neck T-score', cwe_3='LN')
        obx_2.obx_5 = '-2.2'
        obx_2.reference_range = '>-1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='IMG', cwe_2='DEXA Scan Image', cwe_3='EXCELLERIS')
        obx_3.obx_5 = (
            '^IM^TIFF^Base64^'
            'SUkqAAgAAAAIAAABAwABAAAAgAcAAAEBAwABAAAAXAUAAAIBAwABAAAAAQAAAwEDAAEAAAABAAAABgEDAAEAAAACAAAAEQEEAAEAAAAIAAAAFQEDAAEAAAABAAAAFgEDAAEAAAAB'
        )
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Osteopenia bilateral. T-score femoral neck -2.2 approaches osteoporosis threshold.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/ca/ca-excelleris.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EXCELLERIS')
        msh.sending_facility = HD(hd_1='BC_BIO_AGENCY')
        msh.receiving_application = HD(hd_1='EMR_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512200000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EX000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6294817503', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Donovan', xpn_2='Olivia', xpn_3='Grace')
        pid.date_time_of_birth = '19961014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='543 Davie St', xad_3='Vancouver', xad_4='BC', xad_5='V6B 2G6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^2718394'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='EX100020')
        orc.filler_order_number = EI(ei_1='EX200020')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511100000'
        orc.orc_12 = '23489^Hamilton^Connor^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='EX100020')
        obr.filler_order_number = EI(ei_1='EX200020')
        obr.universal_service_identifier = CWE(cwe_1='10524-7', cwe_2='Cytology cervical', cwe_3='LN')
        obr.observation_date_time = '20260511094500'
        obr.obr_16 = '23489^Hamilton^Connor^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512193000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='10524-7', cwe_2='Cervical cytology', cwe_3='LN')
        obx.obx_5 = '373887005^NILM^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Cytology Slide Image', cwe_3='EXCELLERIS')
        obx_2.obx_5 = (
            '^IM^PNG^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAJ0lEQVQ4y2P8z8BQz0AEYBxVMKoABTASawATNYwYVTCqgHoKRhUAAACXJgYBbc0tLgAA'
            'AABJRU5ErkJggg=='
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

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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, HD, MSG, OG, PL, PT, VID, XCN, XPN
from zato.hl7v2.v2_9.groups import OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RgvO15Give, RgvO15Observation, \
    RgvO15Order, RgvO15Patient
from zato.hl7v2.v2_9.messages import ACK, ORU_R01, RGV_O15, RRG_O16
from zato.hl7v2.v2_9.segments import ERR, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, RXG, RXR

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-philips-intellibridge.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS_C')
        msh.sending_facility = HD(hd_1='Philips')
        msh.date_time_of_message = '20150122182658+0000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HP0122182658686QQ000CND119C0WS61'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009001', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van Dijk', xpn_2='Cornelia', xpn_3='""', xpn_7='L')
        pid.date_time_of_birth = '19610101'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HO Surgery', pl_2='OR', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='201512218265601')
        obr.universal_service_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obr.observation_date_time = '20150122182656'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='e86c094ff751-4acf-92b2-38f11c1f6f57-Device')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='70686', cwe_2='MDC_DEV_PRESS_BLD_NONINV_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'
        obx_2.equipment_instance_identifier = EI(ei_1='0600dc750001')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70675', cwe_2='MDC_DEV_PULS_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='150021', cwe_2='MDC_PRESS_BLD_NONINV_SYS', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.5')
        obx_4.obx_5 = '117'
        obx_4.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_4.reference_range = '90-160'
        obx_4.observation_result_status = 'X'
        obx_4.date_time_of_the_observation = '20150122115000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='150022', cwe_2='MDC_PRESS_BLD_NONINV_DIA', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.6')
        obx_5.obx_5 = '82'
        obx_5.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_5.observation_result_status = 'X'
        obx_5.date_time_of_the_observation = '20150122115000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='150023', cwe_2='MDC_PRESS_BLD_NONINV_MEAN', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.7')
        obx_6.obx_5 = '90'
        obx_6.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_6.observation_result_status = 'X'
        obx_6.date_time_of_the_observation = '20150122115000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='4262', cwe_2='MDC_DEV_ECG_VMD', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.2.0.0')
        obx_7.observation_result_status = 'X'
        obx_7.equipment_instance_identifier = EI(ei_1='0600dc750001')

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='4263', cwe_2='MDC_DEV_ECG_CHAN', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.2.1.0')
        obx_8.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='147842', cwe_2='MDC_ECG_CARD_BEAT_RATE', cwe_3='MDC')
        obx_9.observation_sub_id = OG(og_1='1.2.1.1')
        obx_9.obx_5 = '80'
        obx_9.units = CWE(cwe_1='264864', cwe_2='MDC_DIM_BEAT_PER_MIN', cwe_3='MDC')
        obx_9.reference_range = '50-120'
        obx_9.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='147232', cwe_2='MDC_ECG_TIME_PD_QT_GL', cwe_3='MDC')
        obx_10.observation_sub_id = OG(og_1='1.2.1.14')
        obx_10.obx_5 = '360'
        obx_10.units = CWE(cwe_1='264338', cwe_2='MDC_DIM_MILLI_SEC', cwe_3='MDC')
        obx_10.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'NM'
        obx_11.observation_identifier = CWE(cwe_1='147236', cwe_2='MDC_ECG_TIME_PD_QTc', cwe_3='MDC')
        obx_11.observation_sub_id = OG(og_1='1.2.1.15')
        obx_11.obx_5 = '416'
        obx_11.units = CWE(cwe_1='264338', cwe_2='MDC_DIM_MILLI_SEC', cwe_3='MDC')
        obx_11.reference_range = '<500'
        obx_11.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'NM'
        obx_12.observation_identifier = CWE(cwe_1='151562', cwe_2='MDC_RESP_RATE', cwe_3='MDC')
        obx_12.observation_sub_id = OG(og_1='1.2.1.19')
        obx_12.obx_5 = '30'
        obx_12.units = CWE(cwe_1='264928', cwe_2='MDC_DIM_RESP_PER_MIN', cwe_3='MDC')
        obx_12.reference_range = '8-45'
        obx_12.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '13'
        obx_13.value_type = 'ST'
        obx_13.observation_identifier = CWE(cwe_1='184327', cwe_2='MDC_ECG_STAT_RHY', cwe_3='MDC')
        obx_13.observation_sub_id = OG(og_1='1.2.1.21')
        obx_13.obx_5 = 'MDC_ECG_SINUS_RHY'
        obx_13.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '14'
        obx_14.value_type = 'ST'
        obx_14.observation_identifier = CWE(cwe_1='69642', cwe_2='MDC_DEV_ANALY_SAT_O2_VMD', cwe_3='MDC')
        obx_14.observation_sub_id = OG(og_1='1.3.0.0')
        obx_14.observation_result_status = 'X'
        obx_14.equipment_instance_identifier = EI(ei_1='0600dc750001')

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_14

        # .. build OBX ..
        obx_15 = OBX()
        obx_15.set_id_obx = '15'
        obx_15.value_type = 'ST'
        obx_15.observation_identifier = CWE(cwe_1='70771', cwe_2='MDC_DEV_ANALY_PERF_REL_CHAN', cwe_3='MDC')
        obx_15.observation_sub_id = OG(og_1='1.3.1.0')
        obx_15.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_15 = OruR01Observation()
        observation_15.obx = obx_15

        # .. build OBX ..
        obx_16 = OBX()
        obx_16.set_id_obx = '16'
        obx_16.value_type = 'NM'
        obx_16.observation_identifier = CWE(cwe_1='150456', cwe_2='MDC_PULS_OXIM_SAT_O2', cwe_3='MDC')
        obx_16.observation_sub_id = OG(og_1='1.3.1.1')
        obx_16.obx_5 = '99'
        obx_16.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_16.reference_range = '90-100'
        obx_16.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_16 = OruR01Observation()
        observation_16.obx = obx_16

        # .. build OBX ..
        obx_17 = OBX()
        obx_17.set_id_obx = '17'
        obx_17.value_type = 'NM'
        obx_17.observation_identifier = CWE(cwe_1='150448', cwe_2='MDC_PULS_OXIM_PERF_REL', cwe_3='MDC')
        obx_17.observation_sub_id = OG(og_1='1.3.1.3')
        obx_17.obx_5 = '3.9'
        obx_17.units = CWE(cwe_1='262656', cwe_2='MDC_DIM_DIMLESS', cwe_3='MDC')
        obx_17.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_17 = OruR01Observation()
        observation_17.obx = obx_17

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12
        order_observation.observation_13 = observation_13
        order_observation.observation_14 = observation_14
        order_observation.observation_15 = observation_15
        order_observation.observation_16 = observation_16
        order_observation.observation_17 = observation_17

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACME_Gateway', hd_2='080019FFFE3ED02D', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='ACME Healthcare')
        msh.date_time_of_message = '20110602050000+0000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '0104ef190d604db188c3'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='PCD_DEC_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='A', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Willem', xpn_7='L')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='U')
        pv1.assigned_patient_location = PL(pl_1='COLWELL', pl_3='SOLAR')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='080019FFFE3ED02D20110602045842', ei_2='ACME_Gateway', ei_3='080019FFFE3ED02D', ei_4='EUI64')
        obr.filler_order_number = EI(ei_1='080019FFFE3ED02D20110602045842', ei_2='ACME_Gateway', ei_3='080019FFFE3ED02D', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='182777000', cwe_2='monitoring of patient', cwe_3='SCT')
        obr.observation_date_time = '20110602045842+0000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.observation_identifier = CWE(cwe_1='70686', cwe_2='MDC_DEV_PRESS_BLD_NONINV_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.16.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.observation_identifier = CWE(cwe_1='70687', cwe_2='MDC_DEV_PRESS_BLD_NONINV_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.16.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20110602045842'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='150021', cwe_2='MDC_PRESS_BLD_NONINV_SYS', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.16.1.1')
        obx_4.obx_5 = '111'
        obx_4.units = CWE(cwe_1='mm[Hg]', cwe_2='mm[Hg]', cwe_3='UCUM')
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20110602045842'
        obx_4.equipment_instance_identifier = EI(ei_1='080019FFFE3ED02D172.16.172.135', ei_2='GATEWAY_ACME')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='150022', cwe_2='MDC_PRESS_BLD_NONINV_DIA', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.16.1.2')
        obx_5.obx_5 = '60'
        obx_5.units = CWE(cwe_1='mm[Hg]', cwe_2='mm[Hg]', cwe_3='UCUM')
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20110602045842'
        obx_5.equipment_instance_identifier = EI(ei_1='080019FFFE3ED02D172.16.172.135', ei_2='GATEWAY_ACME')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='150023', cwe_2='MDC_PRESS_BLD_NONINV_MEAN', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.16.1.3')
        obx_6.obx_5 = '80'
        obx_6.units = CWE(cwe_1='mm[Hg]', cwe_2='mm[Hg]', cwe_3='UCUM')
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20110602045842'
        obx_6.equipment_instance_identifier = EI(ei_1='080019FFFE3ED02D172.16.172.135', ei_2='GATEWAY_ACME')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='149546', cwe_2='MDC_PULS_RATE_NON_INV', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.16.1.4')
        obx_7.obx_5 = '63'
        obx_7.units = CWE(cwe_1='{beat}/min', cwe_2='{beat}/min', cwe_3='UCUM')
        obx_7.observation_result_status = 'R'
        obx_7.date_time_of_the_observation = '20110602045842'
        obx_7.equipment_instance_identifier = EI(ei_1='080019FFFE3ED02D172.16.172.135', ei_2='GATEWAY_ACME')

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IOPVENDOR', hd_2='1234560000000001', hd_3='EUI64')
        msh.sending_facility = HD(hd_1='IOPVENDOR')
        msh.receiving_application = HD(hd_1='IOCVENDOR', hd_2='6543210000000001', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='IOCVENDOR')
        msh.date_time_of_message = '20080101123456-0600'
        msh.message_type = MSG(msg_1='RGV', msg_2='O15', msg_3='RGV_O15')
        msh.message_control_id = '1'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO659')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_PIV_001')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='98765', cx_4='IHE', cx_5='PI')
        pid.patient_name = XPN(xpn_1='de Vries', xpn_2='Pieter', xpn_7='L')
        pid.date_time_of_birth = '19660101000000-0600'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = RgvO15Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='12345')
        orc.date_time_of_order_event = '20080101123446-0600'
        orc.orc_19 = 'N0001'

        # .. build RXG ..
        rxg = RXG()
        rxg.give_sub_id_counter = '1'
        rxg.give_code = CWE(cwe_1='1234', cwe_2='Dopamine')
        rxg.give_amount_minimum = '250'
        rxg.give_units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')
        rxg.give_rate_amount = '10'
        rxg.give_rate_units = CWE(cwe_1='3475', cwe_2='ug/kg/min', cwe_3='UCUM', cwe_4='265619', cwe_5='MDC_DIM_MICRO_G_PER_KG_PER_MIN', cwe_6='MDC')
        rxg.give_strength = '400'
        rxg.give_strength_units = CWE(cwe_1='1746', cwe_2='mg', cwe_3='UCUM', cwe_4='263890', cwe_5='MDC_DIM_MILLI_G', cwe_6='MDC')
        rxg.give_drug_strength_volume = '250'
        rxg.give_drug_strength_volume_units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_2='IV', cwe_3='HL70162')
        rxr.administration_device = CWE(cwe_2='IVP', cwe_3='HL70164')
        rxr.administration_method = CWE(cwe_2='IV', cwe_3='HL70165')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='69986', cwe_2='MDC_DEV_PUMP_INFUS_VMD', cwe_3='MDC')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='A0001', ei_3='6543210000000001', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = RgvO15Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='68063', cwe_2='MDC_ATTR_PT_WEIGHT', cwe_3='MDC')
        obx_2.obx_5 = '85.0'
        obx_2.units = CWE(cwe_1='kg', cwe_2='kg', cwe_3='UCUM', cwe_4='263875', cwe_5='MDC_DIM_KILO_G', cwe_6='MDC')

        # .. build the OBSERVATION group ..
        observation_2 = RgvO15Observation()
        observation_2.obx = obx_2

        # .. build the GIVE group ..
        give = RgvO15Give()
        give.rxg = rxg
        give.rxr = rxr
        give.observation = observation
        give.observation_2 = observation_2

        # .. build the ORDER group ..
        order = RgvO15Order()
        order.orc = orc
        order.give = give

        # .. assemble the full message ..
        msg = RGV_O15()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IOPVENDOR', hd_2='1234560000000001', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='IOPVENDOR')
        msh.receiving_application = HD(hd_1='IOCVENDOR', hd_2='6543210000000001', hd_3='EUI64')
        msh.receiving_facility = HD(hd_1='IOCVENDOR')
        msh.date_time_of_message = '20080101123456-0600'
        msh.message_type = MSG(msg_1='RGV', msg_2='O15', msg_3='RGV_O15')
        msh.message_control_id = '2'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO659')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_PIV_001')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='98765', cx_4='IHE', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Jan', xpn_7='L')
        pid.date_time_of_birth = '19660101000000-0600'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = RgvO15Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='12345')
        orc.date_time_of_order_event = '20080101123446-0600'
        orc.orc_19 = 'N0001'

        # .. build RXG ..
        rxg = RXG()
        rxg.give_sub_id_counter = '1'
        rxg.give_code = CWE(cwe_1='5678', cwe_2='Normal Saline')
        rxg.give_amount_minimum = '500'
        rxg.give_units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')
        rxg.give_rate_units = CWE(cwe_1='13.3')
        rxg.give_strength = '3122^mL/h^UCUM^265266^MDC_DIM_MILLI_L_PER_HR^MDC'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_2='IV', cwe_3='HL70162')
        rxr.administration_device = CWE(cwe_2='IVP', cwe_3='HL70164')
        rxr.administration_method = CWE(cwe_2='IV', cwe_3='HL70165')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='69986', cwe_2='MDC_DEV_PUMP_INFUS_VMD', cwe_3='MDC')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='A0001', ei_3='6543210000000001', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = RgvO15Observation()
        observation.obx = obx

        # .. build the GIVE group ..
        give = RgvO15Give()
        give.rxg = rxg
        give.rxr = rxr
        give.observation = observation

        # .. build the ORDER group ..
        order = RgvO15Order()
        order.orc = orc
        order.give = give

        # .. assemble the full message ..
        msg = RGV_O15()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IOCVENDOR', hd_2='6543210000000001', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='IOCVENDOR')
        msh.receiving_application = HD(hd_1='IOPVENDOR', hd_2='1234560000000001', hd_3='EUI64')
        msh.receiving_facility = HD(hd_1='IOPVENDOR')
        msh.date_time_of_message = '20080101123456-0600'
        msh.message_type = MSG(msg_1='ACK', msg_2='O15', msg_3='ACK')
        msh.message_control_id = '1'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO659')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_PIV_001')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = '1'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IOCVENDOR', hd_2='6543210000000001', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='IOCVENDOR')
        msh.receiving_application = HD(hd_1='IOPVENDOR', hd_2='1234560000000001', hd_3='EUI64')
        msh.receiving_facility = HD(hd_1='IOPVENDOR')
        msh.date_time_of_message = '20080101123456-0600'
        msh.message_type = MSG(msg_1='RRG', msg_2='O16', msg_3='RRG_O16')
        msh.message_control_id = '1'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO659')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_PIV_001')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = '1'

        # .. assemble the full message ..
        msg = RRG_O16()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IOCVENDOR', hd_2='6543210000000001', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='IOCVENDOR')
        msh.receiving_application = HD(hd_1='IOPVENDOR', hd_2='1234560000000001', hd_3='EUI64')
        msh.receiving_facility = HD(hd_1='IOPVENDOR')
        msh.date_time_of_message = '20080101123456-0600'
        msh.message_type = MSG(msg_1='RRG', msg_2='O16', msg_3='RRG_O16')
        msh.message_control_id = '102'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO659')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_PIV_001')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AR'
        msa.message_control_id = '2'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='207', cwe_2='Application internal error')
        err.severity = 'F'
        err.application_error_code = CWE(cwe_1='9010', cwe_2='Unable to match medication to drug library')

        # .. assemble the full message ..
        msg = RRG_O16()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MINDRAY_EGATEWAY', hd_2='00A037EB2175780F', hd_3='EUI64')
        msh.sending_facility = HD(hd_1='MINDRAY')
        msh.receiving_application = HD(hd_1='AM_PHILIPS_IEM', hd_2='00095CFFFE741952', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='PHILIPS')
        msh.date_time_of_message = '20120111150457-0600'
        msh.message_type = MSG(msg_1='ORU', msg_2='R40', msg_3='ORU_R40')
        msh.message_control_id = '1'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_ACM_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.4.4.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009001', cx_4='Hospital', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Geert', xpn_7='L')
        pid.date_time_of_birth = '18991230'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HO Surgery', pl_2='OR', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='1', ei_2='MINDRAY_EGATEWAY', ei_3='00A037EB2175780F', ei_4='EUI64')
        obr.filler_order_number = EI(ei_1='1', ei_2='MINDRAY_EGATEWAY', ei_3='00A037EB2175780F', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obr.observation_date_time = '20120111150457-0600'
        obr.parent_results_observation_identifier = EIP(eip_2='1&MINDRAY_EGATEWAY&00A037EB2175780F&EUI-64')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='196670', cwe_2='MDC_EVT_LO', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.3.1.150456.1')
        obx.obx_5 = 'Low SpO2'
        obx.interpretation_codes = [CWE(cwe_1='L'), CWE(cwe_1='PM'), CWE(cwe_1='SP')]
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20120111150457-0600'
        obx.equipment_instance_identifier = EI(ei_1='F1519EFX', ei_2='SHENZHEN_DEVICE', ei_3='mindray.com', ei_4='DNS')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='150456', cwe_2='MDC_PULS_OXIM_SAT_O2', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.3.1.150456.2')
        obx_2.obx_5 = '88'
        obx_2.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_2.reference_range = '90-96'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20120111150457-0600'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='68481', cwe_2='MDC_ATTR_EVENT_PHASE', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.3.1.150456.3')
        obx_3.obx_5 = 'start'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='68482', cwe_2='MDC_ATTR_ALARM_STATE', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.3.1.150456.4')
        obx_4.obx_5 = 'active'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='68483', cwe_2='MDC_ATTR_ALARM_INACTIVATION_STATE')
        obx_5.observation_sub_id = OG(og_1='1.3.1.150456.5')
        obx_5.obx_5 = 'enabled'
        obx_5.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_BBRAUN', hd_2='0012211839000001', hd_3='EUI64')
        msh.sending_facility = HD(hd_1='BBRAUN')
        msh.receiving_application = HD(hd_1='AM_Philips_IEM', hd_2='00095CFFFE741952', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='Philips')
        msh.date_time_of_message = '20120109175417-0600'
        msh.message_type = MSG(msg_1='ORU', msg_2='R40', msg_3='ORU_R40')
        msh.message_control_id = '6346172845752460251'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_ACM_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.4.4.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009003', cx_4='AA1', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Anneke', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='de Boer', xpn_7='L')
        pid.date_time_of_birth = '19610301000000-0600'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HO 3 West ICU', pl_2='10', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='634617284575713662', ei_2='PAT_DEVICE_BBRAUN', ei_3='0012211839000001', ei_4='EUI64')
        obr.filler_order_number = EI(ei_1='E0001_27', ei_2='PAT_DEVICE_BBRAUN', ei_3='0012211839000001', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obr.observation_date_time = '20120109175417-0600'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0.1')
        obx.obx_5 = '196940^MDC_EVT_FLUID_LINE_OCCL^MDC^^^^^^Occlusion'
        obx.interpretation_codes = CWE(cwe_1='ST')
        obx.observation_result_status = 'F'
        obx.equipment_instance_identifier = EI(ei_1='P6013', ei_3='0012210000000000', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='68480', cwe_2='MDC_ATTR_ALERT_SOURCE', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.0.0.0.2')
        obx_2.obx_5 = '69985^MDC_DEV_PUMP_INFUS_MDS^MDC'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20120109175417-0600'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='68481', cwe_2='MDC_ATTR_EVENT_PHASE', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.0.0.0.3')
        obx_3.obx_5 = 'start'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='68482', cwe_2='MDC_ATTR_ALARM_STATE', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.0.0.0.4')
        obx_4.obx_5 = 'active'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='68483', cwe_2='MDC_ATTR_ALARM_INACTIVATION_STATE')
        obx_5.observation_sub_id = OG(og_1='1.0.0.0.5')
        obx_5.obx_5 = 'enabled'
        obx_5.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_BBRAUN', hd_2='0012211839000001', hd_3='EUI64')
        msh.sending_facility = HD(hd_1='BBRAUN')
        msh.receiving_application = HD(hd_1='AM_Philips_IEM', hd_2='00095CFFFE741952', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='Philips')
        msh.date_time_of_message = '20120109175426-0600'
        msh.message_type = MSG(msg_1='ORU', msg_2='R40', msg_3='ORU_R40')
        msh.message_control_id = '6346172846620706282'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_ACM_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.4.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009003', cx_4='AA1', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Anneke', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='de Boer', xpn_7='L')
        pid.date_time_of_birth = '19610301000000-0600'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HO 3 West ICU', pl_2='10', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='634617284662070628', ei_2='PAT_DEVICE_BBRAUN', ei_3='0012211839000001', ei_4='EUI64')
        obr.filler_order_number = EI(ei_1='E0001_34', ei_2='PAT_DEVICE_BBRAUN', ei_3='0012211839000001', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obr.observation_date_time = '20120109175426-0600'
        obr.parent_results_observation_identifier = EIP(eip_2='E0001_27&PAT_DEVICE_BBRAUN&0012211839000001&EUI-64')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0.1')
        obx.obx_5 = '196940^MDC_EVT_FLUID_LINE_OCCL^MDC^^^^^^Occlusion'
        obx.interpretation_codes = CWE(cwe_1='ST')
        obx.observation_result_status = 'F'
        obx.equipment_instance_identifier = EI(ei_1='P6013', ei_3='0012210000000000', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='68480', cwe_2='MDC_ATTR_ALERT_SOURCE', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.0.0.0.2')
        obx_2.obx_5 = '69985^MDC_DEV_PUMP_INFUS_MDS^MDC'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20120109175426-0600'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='68481', cwe_2='MDC_ATTR_EVENT_PHASE', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.0.0.0.3')
        obx_3.obx_5 = 'end'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='68482', cwe_2='MDC_ATTR_ALARM_STATE', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.0.0.0.4')
        obx_4.obx_5 = 'inactive'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='68483', cwe_2='MDC_ATTR_ALARM_INACTIVATION_STATE')
        obx_5.observation_sub_id = OG(og_1='1.0.0.0.5')
        obx_5.obx_5 = 'enabled'
        obx_5.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CONTENT_CONSUMER_LIVEDATA')
        msh.sending_facility = HD(hd_1='LIVEDATA')
        msh.receiving_application = HD(hd_1='AM_Philips_IEM')
        msh.receiving_facility = HD(hd_1='Philips')
        msh.date_time_of_message = '20120109175426-0600'
        msh.message_type = MSG(msg_1='ORU', msg_2='R40', msg_3='ORU_R40')
        msh.message_control_id = '1233532926265-02'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='EN', cwe_2='English', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_ACM_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.4.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009003', cx_4='AA1', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Anneke', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='de Boer', xpn_7='L')
        pid.date_time_of_birth = '19610301000000-0600'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HO 3 West ICU', pl_2='10', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='12345-2', ei_2='LIVEDATA')
        obr.universal_service_identifier = CWE(cwe_1='196616', cwe_2='MDC_EVT_ALARM', cwe_3='MDC')
        obr.observation_date_time = '20120109175426-0600'
        obr.obr_17 = '8664693239'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='0', cwe_2='MDCX_DOCUMENTATION_ERROR', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='2.1.2.1.1')
        obx.obx_5 = 'Timeout not documented'
        obx.interpretation_codes = [CWE(cwe_1='SA'), CWE(cwe_1='PM')]
        obx.observation_result_status = 'R'
        obx.user_defined_access_checks = '20120109175426-0600'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='684800', cwe_2='MDC_ATTR_ALERT_SOURCE', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.0.0.0.2')
        obx_2.obx_5 = 'Procedure not documented on time'
        obx_2.interpretation_codes = [CWE(cwe_1='SA'), CWE(cwe_1='PM')]
        obx_2.observation_result_status = 'R'
        obx_2.user_defined_access_checks = '20120109175426-0600'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='684810', cwe_2='MDC_ATTR_EVENT_PHASE', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='2.1.2.1.3')
        obx_3.obx_5 = 'start'
        obx_3.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='684820', cwe_2='MDC_ATTR_ALARM_STATE', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='2.1.2.1.4')
        obx_4.obx_5 = 'active'
        obx_4.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AcmeInc', hd_2='ACDE48234567ABCD', hd_3='EUI64')
        msh.date_time_of_message = '20090713090030+0500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSGID1234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.message_profile_identifier = EI(ei_1='IHE PCD ORU-R01 2006', ei_2='HL7', ei_3='2.16.840.1.113883.9.n.m', ei_4='HL7')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='789567', cx_4='Imaginary Hospital', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Brouwer', xpn_2='Hendrik', xpn_3='Adriaan', xpn_7='L', xpn_8='A')
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AB12345', ei_2='AcmeAHDInc', ei_3='ACDE48234567ABCD', ei_4='EUI-64')
        obr.filler_order_number = EI(ei_1='CD12345', ei_2='AcmeAHDInc', ei_3='ACDE48234567ABCD', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='528391', cwe_2='MDC_DEV_SPEC_PROFILE_BP', cwe_3='MDC')
        obr.observation_date_time = '20090813095715+0500'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='528391', cwe_2='MDC_DEV_SPEC_PROFILE_BP', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1')
        obx.observation_result_status = 'R'
        obx.equipment_instance_identifier = EI(ei_1='0123456789ABCDEF', ei_2='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.observation_identifier = CWE(cwe_1='150020', cwe_2='MDC_PRESS_BLD_NONINV', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.0.1')
        obx_2.nature_of_abnormal_test = 'R'
        obx_2.user_defined_access_checks = '20090813095715+0500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='150021', cwe_2='MDC_PRESS_BLD_NONINV_SYS', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.0.1.1')
        obx_3.obx_5 = '120'
        obx_3.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_3.nature_of_abnormal_test = 'R'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='150022', cwe_2='MDC_PRESS_BLD_NONINV_DIA', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.0.1.2')
        obx_4.obx_5 = '80'
        obx_4.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_4.nature_of_abnormal_test = 'R'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='150023', cwe_2='MDC_PRESS_BLD_NONINV_MEAN', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.0.1.3')
        obx_5.obx_5 = '100'
        obx_5.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_5.nature_of_abnormal_test = 'R'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Stepstone')
        msh.receiving_application = HD(hd_1='AcmeInc', hd_2='ACDE48234567ABCD', hd_3='EUI64')
        msh.date_time_of_message = '20090726095731+0500'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'AMSGID1234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.msh_13 = ''

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSGID1234'
        msa.msa_3 = 'Message Accepted'
        msa.msa_4 = ''

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PUMPVENDOR', hd_2='9999990000000000', hd_3='EUI64')
        msh.sending_facility = HD(hd_1='PUMPVENDOR')
        msh.receiving_application = HD(hd_1='DOC_VENDOR')
        msh.receiving_facility = HD(hd_1='DOC_VENDOR')
        msh.date_time_of_message = '20151015132107-0500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R42', msg_3='ORU_R01')
        msh.message_control_id = '6358051206735492253'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.principal_language_of_message = CWE(cwe_1='en', cwe_2='English', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_010', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.4.10', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HO2009002', cx_4='IHE', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Dekker', xpn_2='Thijs', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='van der Laan', xpn_7='L')
        pid.date_time_of_birth = '19610201000000-0600'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.identity_unknown_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3 West ICU', pl_2='3002', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='AB12345', ei_2='PCD-03')
        obr.filler_order_number = EI(ei_1='CD12345', ei_2='HL7', ei_3='ACDE48234567ABCD', ei_4='EUI64')
        obr.universal_service_identifier = CWE(cwe_1='2222', cwe_2='Dopamine')
        obr.observation_date_time = '20151015132106-0500'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='70049', cwe_2='MDC_DEV_PUMP_INFUS_LVP_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.responsible_observer = XCN(xcn_1='N0002')
        obx.equipment_instance_identifier = EI(ei_1='E0002', ei_3='0012210000000000', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='184517', cwe_2='MDC_PUMP_DRUG_LIBRARY_VERSION', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.0.0.1')
        obx_2.obx_5 = 'DL1'
        obx_2.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='68487', cwe_2='MDC_ATTR_EVT_COND', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.0.0.2')
        obx_3.obx_5 = '197288^MDC_EVT_PUMP_DELIV_START^MDC'
        obx_3.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='68488', cwe_2='MDC_ATTR_EVT_SOURCE', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.0.0.3')
        obx_4.obx_5 = '1.1.2.0'
        obx_4.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.observation_identifier = CWE(cwe_1='70050', cwe_2='MDC_DEV_PUMP_INFUS_LVP_VMD', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.0.0')
        obx_5.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.observation_identifier = CWE(cwe_1='70067', cwe_2='MDC_DEV_PUMP_DELIVERY_INFO', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.0')
        obx_6.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CWE'
        obx_7.observation_identifier = CWE(cwe_1='184519', cwe_2='MDC_PUMP_INFUSING_STATUS', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.1.1.1')
        obx_7.obx_5 = '^pump-status-infusing'
        obx_7.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='158014', cwe_2='MDC_FLOW_FLUID_PUMP_CURRENT', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.1.1.2')
        obx_8.obx_5 = '15.4'
        obx_8.units = CWE(cwe_1='265266', cwe_2='MDC_DIM_MILLI_L_PER_HR', cwe_3='MDC', cwe_4='mL/h', cwe_5='mL/h', cwe_6='UCUM')
        obx_8.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'CWE'
        obx_9.observation_identifier = CWE(cwe_1='158016', cwe_2='MDC_DEV_PUMP_ACTIVE_SOURCES', cwe_3='MDC')
        obx_9.observation_sub_id = OG(og_1='1.1.1.3')
        obx_9.obx_5 = '^pump-source-info-primary'
        obx_9.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.observation_identifier = CWE(cwe_1='70071', cwe_2='MDC_DEV_PUMP_INFUSATE_SOURCE_PRIMARY', cwe_3='MDC')
        obx_10.observation_sub_id = OG(og_1='1.1.2.0')
        obx_10.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'CWE'
        obx_11.observation_identifier = CWE(cwe_1='158005', cwe_2='MDC_DEV_PUMP_CURRENT_DELIVERY_STATUS', cwe_3='MDC')
        obx_11.observation_sub_id = OG(og_1='1.1.2.1')
        obx_11.obx_5 = '^pump-delivery-status-delivering'
        obx_11.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'CWE'
        obx_12.observation_identifier = CWE(cwe_1='158008', cwe_2='MDC_DEV_PUMP_PROGRAM_DELIVERY_MODE', cwe_3='MDC')
        obx_12.observation_sub_id = OG(og_1='1.1.2.2')
        obx_12.obx_5 = '^pump-program-delivery-mode-continuous'
        obx_12.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '13'
        obx_13.value_type = 'ST'
        obx_13.observation_identifier = CWE(cwe_1='158012', cwe_2='MDC_DEV_PUMP_SOURCE_CHANNEL_LABEL', cwe_3='MDC')
        obx_13.observation_sub_id = OG(og_1='1.1.2.3')
        obx_13.obx_5 = 'Primary'
        obx_13.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '14'
        obx_14.value_type = 'NM'
        obx_14.observation_identifier = CWE(cwe_1='157784', cwe_2='MDC_FLOW_FLUID_PUMP', cwe_3='MDC')
        obx_14.observation_sub_id = OG(og_1='1.1.2.4')
        obx_14.obx_5 = '15.4'
        obx_14.units = CWE(cwe_1='265266', cwe_2='MDC_DIM_MILLI_L_PER_HR', cwe_3='MDC', cwe_4='mL/h', cwe_5='mL/h', cwe_6='UCUM')
        obx_14.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_14

        # .. build OBX ..
        obx_15 = OBX()
        obx_15.set_id_obx = '15'
        obx_15.value_type = 'NM'
        obx_15.observation_identifier = CWE(cwe_1='157924', cwe_2='MDC_RATE_DOSE', cwe_3='MDC')
        obx_15.observation_sub_id = OG(og_1='1.1.2.5')
        obx_15.obx_5 = '5.00'
        obx_15.units = CWE(cwe_1='265619', cwe_2='MDC_DIM_MICRO_G_PER_KG_PER_MIN', cwe_3='MDC', cwe_4='ug/kg/min', cwe_5='ug/kg/min', cwe_6='UCUM')
        obx_15.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_15 = OruR01Observation()
        observation_15.obx = obx_15

        # .. build OBX ..
        obx_16 = OBX()
        obx_16.set_id_obx = '16'
        obx_16.value_type = 'NM'
        obx_16.observation_identifier = CWE(cwe_1='157884', cwe_2='MDC_VOL_FLUID_TBI', cwe_3='MDC')
        obx_16.observation_sub_id = OG(og_1='1.1.2.6')
        obx_16.obx_5 = '250.0'
        obx_16.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')
        obx_16.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_16 = OruR01Observation()
        observation_16.obx = obx_16

        # .. build OBX ..
        obx_17 = OBX()
        obx_17.set_id_obx = '17'
        obx_17.value_type = 'NM'
        obx_17.observation_identifier = CWE(cwe_1='157993', cwe_2='MDC_VOL_FLUID_DELIV_TOTAL', cwe_3='MDC')
        obx_17.observation_sub_id = OG(og_1='1.1.2.7')
        obx_17.obx_5 = '0.0'
        obx_17.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')
        obx_17.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_17 = OruR01Observation()
        observation_17.obx = obx_17

        # .. build OBX ..
        obx_18 = OBX()
        obx_18.set_id_obx = '18'
        obx_18.value_type = 'NM'
        obx_18.observation_identifier = CWE(cwe_1='157872', cwe_2='MDC_VOL_FLUID_TBI_REMAIN', cwe_3='MDC')
        obx_18.observation_sub_id = OG(og_1='1.1.2.8')
        obx_18.obx_5 = '250.0'
        obx_18.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC', cwe_4='mL', cwe_5='mL', cwe_6='UCUM')
        obx_18.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_18 = OruR01Observation()
        observation_18.obx = obx_18

        # .. build OBX ..
        obx_19 = OBX()
        obx_19.set_id_obx = '19'
        obx_19.value_type = 'NM'
        obx_19.observation_identifier = CWE(cwe_1='157916', cwe_2='MDC_TIME_PD_REMAIN', cwe_3='MDC')
        obx_19.observation_sub_id = OG(og_1='1.1.2.9')
        obx_19.obx_5 = '974'
        obx_19.units = CWE(cwe_1='264352', cwe_2='MDC_DIM_MIN', cwe_3='MDC', cwe_4='min', cwe_5='min', cwe_6='UCUM')
        obx_19.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_19 = OruR01Observation()
        observation_19.obx = obx_19

        # .. build OBX ..
        obx_20 = OBX()
        obx_20.set_id_obx = '20'
        obx_20.value_type = 'ST'
        obx_20.observation_identifier = CWE(cwe_1='184514', cwe_2='MDC_DRUG_NAME_LABEL', cwe_3='MDC')
        obx_20.observation_sub_id = OG(og_1='1.1.2.10')
        obx_20.obx_5 = 'Dopamine'
        obx_20.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_20 = OruR01Observation()
        observation_20.obx = obx_20

        # .. build OBX ..
        obx_21 = OBX()
        obx_21.set_id_obx = '21'
        obx_21.value_type = 'NM'
        obx_21.observation_identifier = CWE(cwe_1='157760', cwe_2='MDC_CONC_DRUG', cwe_3='MDC')
        obx_21.observation_sub_id = OG(og_1='1.1.2.11')
        obx_21.obx_5 = '1.6'
        obx_21.units = CWE(cwe_1='264306', cwe_2='MDC_DIM_MILLI_G_PER_ML', cwe_3='MDC', cwe_4='mg/mL', cwe_5='mg/mL', cwe_6='UCUM')
        obx_21.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_21 = OruR01Observation()
        observation_21.obx = obx_21

        # .. build OBX ..
        obx_22 = OBX()
        obx_22.set_id_obx = '22'
        obx_22.value_type = 'ST'
        obx_22.observation_identifier = CWE(cwe_1='184516', cwe_2='MDC_PUMP_DRUG_LIBRARY_CARE_AREA', cwe_3='MDC')
        obx_22.observation_sub_id = OG(og_1='1.1.2.12')
        obx_22.obx_5 = 'Crit Care'
        obx_22.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_22 = OruR01Observation()
        observation_22.obx = obx_22

        # .. build OBX ..
        obx_23 = OBX()
        obx_23.set_id_obx = '23'
        obx_23.value_type = 'NM'
        obx_23.observation_identifier = CWE(cwe_1='68063', cwe_2='MDC_ATTR_PT_WEIGHT', cwe_3='MDC')
        obx_23.observation_sub_id = OG(og_1='1.1.2.13')
        obx_23.obx_5 = '82.0'
        obx_23.units = CWE(cwe_1='263875', cwe_2='MDC_DIM_KILO_G', cwe_3='MDC', cwe_4='kg', cwe_5='kg', cwe_6='UCUM')
        obx_23.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_23 = OruR01Observation()
        observation_23.obx = obx_23

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12
        order_observation.observation_13 = observation_13
        order_observation.observation_14 = observation_14
        order_observation.observation_15 = observation_15
        order_observation.observation_16 = observation_16
        order_observation.observation_17 = observation_17
        order_observation.observation_18 = observation_18
        order_observation.observation_19 = observation_19
        order_observation.observation_20 = observation_20
        order_observation.observation_21 = observation_21
        order_observation.observation_22 = observation_22
        order_observation.observation_23 = observation_23

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9143B2E', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_UMCU', hd_2='00095CFFFE800001', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20260509143000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'UMCU20260509143001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260001', cx_4='UMCU', cx_5='PI')
        pid.pid_5 = 'van der Berg^Hendrik^J^^^Dhr.'
        pid.date_time_of_birth = '19550818'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 7')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='UMCU20260509143001')
        obr.universal_service_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obr.observation_date_time = '20260509143000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='MP70_IC07', ei_3='00A0C9143B2E', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='70668', cwe_2='MDC_DEV_PRESS_BLD_ART_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70669', cwe_2='MDC_DEV_PRESS_BLD_ART_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='150017', cwe_2='MDC_PRESS_BLD_ART_SYS', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.1')
        obx_4.obx_5 = '128'
        obx_4.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_4.reference_range = '90-140'
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='150018', cwe_2='MDC_PRESS_BLD_ART_DIA', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.2')
        obx_5.obx_5 = '72'
        obx_5.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_5.reference_range = '60-90'
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='150019', cwe_2='MDC_PRESS_BLD_ART_MEAN', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.3')
        obx_6.obx_5 = '91'
        obx_6.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_6.reference_range = '70-105'
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='70672', cwe_2='MDC_DEV_PRESS_BLD_VEN_VMD', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.2.0.0')
        obx_7.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='70673', cwe_2='MDC_DEV_PRESS_BLD_VEN_CHAN', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.2.1.0')
        obx_8.observation_result_status = 'X'
        obx_8.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='150037', cwe_2='MDC_PRESS_BLD_VEN_CENT_MEAN', cwe_3='MDC')
        obx_9.observation_sub_id = OG(og_1='1.2.1.1')
        obx_9.obx_5 = '8'
        obx_9.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_9.reference_range = '2-12'
        obx_9.observation_result_status = 'R'
        obx_9.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'ST'
        obx_10.observation_identifier = CWE(cwe_1='70692', cwe_2='MDC_DEV_TEMP_VMD', cwe_3='MDC')
        obx_10.observation_sub_id = OG(og_1='1.3.0.0')
        obx_10.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'ST'
        obx_11.observation_identifier = CWE(cwe_1='70693', cwe_2='MDC_DEV_TEMP_CHAN', cwe_3='MDC')
        obx_11.observation_sub_id = OG(og_1='1.3.1.0')
        obx_11.observation_result_status = 'X'
        obx_11.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'NM'
        obx_12.observation_identifier = CWE(cwe_1='150368', cwe_2='MDC_TEMP', cwe_3='MDC')
        obx_12.observation_sub_id = OG(og_1='1.3.1.1')
        obx_12.obx_5 = '37.2'
        obx_12.units = CWE(cwe_1='266400', cwe_2='MDC_DIM_DEGC', cwe_3='MDC')
        obx_12.reference_range = '36.0-38.0'
        obx_12.observation_result_status = 'R'
        obx_12.date_time_of_the_observation = '20260509143000+0200'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12

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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9143C44', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_ERASMUS', hd_2='00095CFFFE800002', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='ERASMUS')
        msh.date_time_of_message = '20260509150000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EMC20260509150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260002', cx_4='ERASMUS', cx_5='PI')
        pid.pid_5 = 'de Groot^Sophia^M^^^Mevr.'
        pid.date_time_of_birth = '19720411'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 3')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='EMC20260509150001')
        obr.universal_service_identifier = CWE(cwe_1='70753', cwe_2='MDC_DEV_VENT_MDS', cwe_3='MDC')
        obr.observation_date_time = '20260509150000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='70753', cwe_2='MDC_DEV_VENT_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='V680_IC03', ei_3='00A0C9143C44', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='70754', cwe_2='MDC_DEV_VENT_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70755', cwe_2='MDC_DEV_VENT_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='151708', cwe_2='MDC_VENT_RESP_RATE_SETTING', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.1')
        obx_4.obx_5 = '14'
        obx_4.units = CWE(cwe_1='264928', cwe_2='MDC_DIM_RESP_PER_MIN', cwe_3='MDC')
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='151562', cwe_2='MDC_RESP_RATE', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.2')
        obx_5.obx_5 = '16'
        obx_5.units = CWE(cwe_1='264928', cwe_2='MDC_DIM_RESP_PER_MIN', cwe_3='MDC')
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='151716', cwe_2='MDC_VENT_VOL_TIDAL_SETTING', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.3')
        obx_6.obx_5 = '450'
        obx_6.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC')
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='151868', cwe_2='MDC_VOL_MINUTE_AWAY', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.1.1.4')
        obx_7.obx_5 = '7.2'
        obx_7.units = CWE(cwe_1='263808', cwe_2='MDC_DIM_L_PER_MIN', cwe_3='MDC')
        obx_7.observation_result_status = 'R'
        obx_7.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='151832', cwe_2='MDC_VENT_PRESS_AWAY_INSP_PEAK', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.1.1.5')
        obx_8.obx_5 = '22'
        obx_8.units = CWE(cwe_1='266016', cwe_2='MDC_DIM_MMHG', cwe_3='MDC')
        obx_8.observation_result_status = 'R'
        obx_8.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='151976', cwe_2='MDC_VENT_PRESS_AWAY_END_EXP_POS', cwe_3='MDC')
        obx_9.observation_sub_id = OG(og_1='1.1.1.6')
        obx_9.obx_5 = '5'
        obx_9.units = CWE(cwe_1='266048', cwe_2='MDC_DIM_CM_H2O', cwe_3='MDC')
        obx_9.observation_result_status = 'R'
        obx_9.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='152004', cwe_2='MDC_VENT_CONC_AWAY_O2', cwe_3='MDC')
        obx_10.observation_sub_id = OG(og_1='1.1.1.7')
        obx_10.obx_5 = '40'
        obx_10.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_10.observation_result_status = 'R'
        obx_10.date_time_of_the_observation = '20260509150000+0200'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9144D55', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_AMC', hd_2='00095CFFFE800003', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='AMC')
        msh.date_time_of_message = '20260509153000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AMC20260509153001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260003', cx_4='AMC', cx_5='PI')
        pid.pid_5 = 'Bakker^Pieter^W^^^Dhr.'
        pid.date_time_of_birth = '19630927'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CCU', pl_2='Cardiac Care Unit', pl_3='Bed 2')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='AMC20260509153001')
        obr.universal_service_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obr.observation_date_time = '20260509153000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='MP70_CCU02', ei_3='00A0C9144D55', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='70678', cwe_2='MDC_DEV_CARD_OUTPUT_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70679', cwe_2='MDC_DEV_CARD_OUTPUT_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='149772', cwe_2='MDC_OUTPUT_CARD', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.1')
        obx_4.obx_5 = '5.2'
        obx_4.units = CWE(cwe_1='265280', cwe_2='MDC_DIM_L_PER_MIN', cwe_3='MDC')
        obx_4.reference_range = '4.0-8.0'
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='149776', cwe_2='MDC_OUTPUT_CARD_INDEX', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.2')
        obx_5.obx_5 = '2.8'
        obx_5.units = CWE(cwe_1='265280', cwe_2='MDC_DIM_L_PER_MIN', cwe_3='MDC')
        obx_5.reference_range = '2.5-4.0'
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='150064', cwe_2='MDC_TEMP_BLD', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.3')
        obx_6.obx_5 = '36.8'
        obx_6.units = CWE(cwe_1='266400', cwe_2='MDC_DIM_DEGC', cwe_3='MDC')
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='149760', cwe_2='MDC_VOL_BLD_STROKE', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.1.1.4')
        obx_7.obx_5 = '65'
        obx_7.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC')
        obx_7.reference_range = '60-100'
        obx_7.observation_result_status = 'R'
        obx_7.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='149764', cwe_2='MDC_VOL_BLD_STROKE_INDEX', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.1.1.5')
        obx_8.obx_5 = '35'
        obx_8.units = CWE(cwe_1='263762', cwe_2='MDC_DIM_MILLI_L', cwe_3='MDC')
        obx_8.reference_range = '33-47'
        obx_8.observation_result_status = 'R'
        obx_8.date_time_of_the_observation = '20260509153000+0200'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9145E66', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_CATHARINA', hd_2='00095CFFFE800004', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='CATHARINA')
        msh.date_time_of_message = '20260509160000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CZE20260509160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260004', cx_4='CATHARINA', cx_5='PI')
        pid.pid_5 = 'Vermeer^Cornelia^A^^^Mevr.'
        pid.date_time_of_birth = '19810216'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OK', pl_2='Operatiekamer', pl_3='1')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='CZE20260509160001')
        obr.universal_service_identifier = CWE(cwe_1='70729', cwe_2='MDC_DEV_ANALY_CONC_GAS_MULTI_PARAM_MDS', cwe_3='MDC')
        obr.observation_date_time = '20260509160000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='70729', cwe_2='MDC_DEV_ANALY_CONC_GAS_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='GAS_OK01', ei_3='00A0C9145E66', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='70730', cwe_2='MDC_DEV_ANALY_CONC_GAS_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70731', cwe_2='MDC_DEV_ANALY_CONC_GAS_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='152004', cwe_2='MDC_VENT_CONC_AWAY_O2', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.1')
        obx_4.obx_5 = '35'
        obx_4.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='152108', cwe_2='MDC_VENT_CONC_AWAY_CO2_ET', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.2')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='153604', cwe_2='MDC_CONC_AWAY_DESFL_ET', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.3')
        obx_6.obx_5 = '5.8'
        obx_6.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='153640', cwe_2='MDC_CONC_AWAY_DESFL_INSP', cwe_3='MDC')
        obx_7.observation_sub_id = OG(og_1='1.1.1.4')
        obx_7.obx_5 = '6.0'
        obx_7.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_7.observation_result_status = 'R'
        obx_7.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='152048', cwe_2='MDC_CONC_AWAY_N2O_ET', cwe_3='MDC')
        obx_8.observation_sub_id = OG(og_1='1.1.1.5')
        obx_8.obx_5 = '0'
        obx_8.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_8.observation_result_status = 'R'
        obx_8.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='153632', cwe_2='MDC_CONC_AWAY_AGENT_ET', cwe_3='MDC')
        obx_9.observation_sub_id = OG(og_1='1.1.1.6')
        obx_9.obx_5 = '1.1'
        obx_9.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_9.observation_result_status = 'R'
        obx_9.date_time_of_the_observation = '20260509160000+0200'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9146F77', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_RADBOUD', hd_2='00095CFFFE800005', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='RADBOUDUMC')
        msh.date_time_of_message = '20260509163000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RBD20260509163001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260005', cx_4='RADBOUD', cx_5='PI')
        pid.pid_5 = 'Willems^Gerardus^H^^^Dhr.'
        pid.date_time_of_birth = '19470305'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CCU', pl_2='Cardiac Care Unit', pl_3='Bed 5')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='RBD20260509163001')
        obr.universal_service_identifier = CWE(cwe_1='4262', cwe_2='MDC_DEV_ECG_VMD', cwe_3='MDC')
        obr.observation_date_time = '20260509163000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='4262', cwe_2='MDC_DEV_ECG_VMD', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='TC50_CCU05', ei_3='00A0C9146F77', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='147842', cwe_2='MDC_ECG_CARD_BEAT_RATE', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.1.1')
        obx_2.obx_5 = '72'
        obx_2.units = CWE(cwe_1='264864', cwe_2='MDC_DIM_BEAT_PER_MIN', cwe_3='MDC')
        obx_2.reference_range = '50-100'
        obx_2.observation_result_status = 'R'
        obx_2.date_time_of_the_observation = '20260509163000+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='147232', cwe_2='MDC_ECG_TIME_PD_QT_GL', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.2')
        obx_3.obx_5 = '380'
        obx_3.units = CWE(cwe_1='264338', cwe_2='MDC_DIM_MILLI_SEC', cwe_3='MDC')
        obx_3.observation_result_status = 'R'
        obx_3.date_time_of_the_observation = '20260509163000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='147236', cwe_2='MDC_ECG_TIME_PD_QTc', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.3')
        obx_4.obx_5 = '410'
        obx_4.units = CWE(cwe_1='264338', cwe_2='MDC_DIM_MILLI_SEC', cwe_3='MDC')
        obx_4.reference_range = '<500'
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509163000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='184327', cwe_2='MDC_ECG_STAT_RHY', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.4')
        obx_5.obx_5 = 'MDC_ECG_SINUS_RHY'
        obx_5.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='18745-0', cwe_2='Cardiac electrophysiology report', cwe_3='LN')
        obx_6.obx_5 = (
            'Philips^Application^PDF^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxNDUgPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihQaGlsaXBzIDEy'
            'LUxlYWQgRUNHIFJlcG9ydCkgVGoKMTAwIDY4MCBUZAooUGF0aWVudDogV2lsbGVtcywgRy5ILikgVGoKMTAwIDY2MCBUZAooSFI6IDcyIGJwbSB8IFFUYzogNDEwIG1zKSBUagoxMDAg'
            'NjQwIFRkCihTaW51cyBSaHl0aG0sIE5vcm1hbCBFQ0cpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250'
            'IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY2IDAwMDAwIG4gCjAwMDAwMDAxMjUgMDAw'
            'MDAgbiAKMDAwMDAwMDMwMiAwMDAwMCBuIAowMDAwMDAwNDk5IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTg4CiUlRU9GCg=='
        )
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-philips-intellibridge.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT_DEVICE_PHILIPS', hd_2='00A0C9147A88', hd_3='EUI-64')
        msh.sending_facility = HD(hd_1='Philips')
        msh.receiving_application = HD(hd_1='IBE_LUMC', hd_2='00095CFFFE800006', hd_3='EUI-64')
        msh.receiving_facility = HD(hd_1='LUMC')
        msh.date_time_of_message = '20260509170000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LUMC20260509170001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL', cwe_2='Dutch', cwe_3='ISO639')
        msh.message_profile_identifier = EI(ei_1='IHE_PCD_001', ei_2='IHE PCD', ei_3='1.3.6.1.4.1.19376.1.6.1.1.1', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT20260006', cx_4='LUMC', cx_5='PI')
        pid.pid_5 = 'Dijkstra^Aaltje^W^^^Mevr.'
        pid.date_time_of_birth = '19580611'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 9')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='LUMC20260509170001')
        obr.universal_service_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obr.observation_date_time = '20260509170000+0200'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='69965', cwe_2='MDC_DEV_MON_PHYSIO_MULTI_PARAM_MDS', cwe_3='MDC')
        obx.observation_sub_id = OG(og_1='1.0.0.0')
        obx.observation_result_status = 'X'
        obx.equipment_instance_identifier = EI(ei_1='MX800_IC09', ei_3='00A0C9147A88', ei_4='EUI-64')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='69642', cwe_2='MDC_DEV_ANALY_SAT_O2_VMD', cwe_3='MDC')
        obx_2.observation_sub_id = OG(og_1='1.1.0.0')
        obx_2.observation_result_status = 'X'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='70771', cwe_2='MDC_DEV_ANALY_PERF_REL_CHAN', cwe_3='MDC')
        obx_3.observation_sub_id = OG(og_1='1.1.1.0')
        obx_3.observation_result_status = 'X'
        obx_3.date_time_of_the_observation = '20260509170000+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='150456', cwe_2='MDC_PULS_OXIM_SAT_O2', cwe_3='MDC')
        obx_4.observation_sub_id = OG(og_1='1.1.1.1')
        obx_4.obx_5 = '94'
        obx_4.units = CWE(cwe_1='262688', cwe_2='MDC_DIM_PERCENT', cwe_3='MDC')
        obx_4.reference_range = '90-100'
        obx_4.observation_result_status = 'R'
        obx_4.date_time_of_the_observation = '20260509170000+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='149530', cwe_2='MDC_PULS_OXIM_PULS_RATE', cwe_3='MDC')
        obx_5.observation_sub_id = OG(og_1='1.1.1.2')
        obx_5.obx_5 = '88'
        obx_5.units = CWE(cwe_1='264864', cwe_2='MDC_DIM_BEAT_PER_MIN', cwe_3='MDC')
        obx_5.reference_range = '50-120'
        obx_5.observation_result_status = 'R'
        obx_5.date_time_of_the_observation = '20260509170000+0200'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='150448', cwe_2='MDC_PULS_OXIM_PERF_REL', cwe_3='MDC')
        obx_6.observation_sub_id = OG(og_1='1.1.1.3')
        obx_6.obx_5 = '2.1'
        obx_6.units = CWE(cwe_1='262656', cwe_2='MDC_DIM_DIMLESS', cwe_3='MDC')
        obx_6.observation_result_status = 'R'
        obx_6.date_time_of_the_observation = '20260509170000+0200'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='IMGHL7', cwe_2='SpO2 trend screenshot', cwe_3='L')
        obx_7.obx_5 = (
            'Philips^Image^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBX/2wBDAQMEBAUEBQkFBQk'
            'VDQsNFRUVFRUVFRUV FQUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRX/wAARCAAoACgDASIAAhEBAxEB/8QA HwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/'
            '8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR BRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdI SUpTVFVWV1hZWmNkZWZnaGlqc3R'
            '1dnd4eXp/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJ Cgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVi ctEKFiQ04SXxF'
            'xgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqC g4SFhoeIiYqSk5SVlpeYmZqio6SlpqeoqaqyS7O0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk'
            ' 5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD7looooAKKKKACiiigD//Z'
        )
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'SpO2 saturatietrend 6 uur, patient Dijkstra A.W., IC bed 9, LUMC.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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

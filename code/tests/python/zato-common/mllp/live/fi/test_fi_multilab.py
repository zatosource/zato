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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DR, EI, EIP, HD, MSG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import MSH, NTE, OBR, OBX, ORC, PID, PV1, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-multilab.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-multilab.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='ANALYZER_1')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 10', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234601'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI1', pl_3='Vastaanottohuone 3', pl_5='SHP_A')
        pv1.pv1_7 = 'DR1000^Korhonen^Satu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI1000001')

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
        orc.placer_order_number = EI(ei_1='ORD1000001', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'DR1000^Korhonen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000001', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='LAB_A')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = 'DR1000^Korhonen^Satu^^^LL^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000001', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Seerumi', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509075500')
        spm.specimen_collection_date_time = DR(dr_1='20260509075500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='ANALYZER_2')
        msh.date_time_of_message = '20260509081000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000002', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='050390-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Anna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19900305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 22', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876557'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI2', pl_3='Vastaanottohuone 5', pl_5='SHP_A')
        pv1.pv1_7 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI1000002')

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
        orc.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509081000^^R'
        orc.date_time_of_order_event = '20260509081000'
        orc.orc_10 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='LAB_A')
        obr.observation_date_time = '20260509081000'
        obr.obr_15 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='2085', cwe_2='P-ALAT', cwe_3='LAB_A')
        obr_2.observation_date_time = '20260509081000'
        obr_2.obr_15 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        obr_3.universal_service_identifier = CWE(cwe_1='1920-8', cwe_2='P-ASAT', cwe_3='LAB_A')
        obr_3.observation_date_time = '20260509081000'
        obr_3.obr_15 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        obr_4.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='LAB_A')
        obr_4.observation_date_time = '20260509081000'
        obr_4.obr_15 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000002', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Seerumi', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509080500')
        spm.specimen_collection_date_time = DR(dr_1='20260509080500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4, spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='ANALYZER_1')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 10', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234601'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000001', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000001', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509090000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000001', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000001', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='LAB_A')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1000^Korhonen^Satu^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx.obx_5 = '5.4'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-6.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509090000'

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
    """ Based on live/fi/fi-multilab.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='ANALYZER_2')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000002', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='050390-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Anna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19900305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 22', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876557'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000002', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509081000^^R'
        orc.date_time_of_order_event = '20260509100000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000002', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000002', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='LAB_A')
        obr.observation_date_time = '20260509082500'
        obr.obr_14 = '20260509082500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1001^Mäkinen^Jukka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '50-90'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1742-6', cwe_2='P-ALAT', cwe_3='LN')
        obx_2.obx_5 = '25'
        obx_2.units = CWE(cwe_1='U/l')
        obx_2.reference_range = '<40'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1920-8', cwe_2='P-ASAT', cwe_3='LN')
        obx_3.obx_5 = '22'
        obx_3.units = CWE(cwe_1='U/l')
        obx_3.reference_range = '<35'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='LAB_A')
        obx_4.obx_5 = '2'
        obx_4.units = CWE(cwe_1='mg/l')
        obx_4.reference_range = '<3'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509100000'

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
    """ Based on live/fi/fi-multilab.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='MULTILAB')
        msh.receiving_facility = HD(hd_1='HEMA_ANALYZER')
        msh.date_time_of_message = '20260509082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000003', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 44', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654339'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS1', pl_3='Huone 312', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR1002^Laine^Elina^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000001')

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
        orc.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509082000^^R'
        orc.date_time_of_order_event = '20260509082000'
        orc.orc_10 = 'DR1002^Laine^Elina^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_B')
        obr.observation_date_time = '20260509082000'
        obr.obr_15 = 'DR1002^Laine^Elina^^^LL^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000003', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='EDTA', cwe_2='EDTA-kokoveri', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509081500')
        spm.specimen_collection_date_time = DR(dr_1='20260509081500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MULTILAB')
        msh.sending_facility = HD(hd_1='HEMA_ANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000003', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 44', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654339'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000003', ei_2='MULTILAB')
        orc.orc_7 = '^^^20260509082000^^R'
        orc.date_time_of_order_event = '20260509093000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000003', ei_2='MULTILAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_B')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR1002^Laine^Elina^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='LAB_B')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2171', cwe_2='B-Eryt', cwe_3='LAB_B')
        obx_2.obx_5 = '4.65'
        obx_2.units = CWE(cwe_1='10E12/l')
        obx_2.reference_range = '4.25-5.70'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='LAB_B')
        obx_3.obx_5 = '148'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '134-167'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4679', cwe_2='B-HKR', cwe_3='LAB_B')
        obx_4.obx_5 = '0.43'
        obx_4.units = CWE(cwe_1='osuus')
        obx_4.reference_range = '0.39-0.50'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='LAB_B')
        obx_5.obx_5 = '225'
        obx_5.units = CWE(cwe_1='10E9/l')
        obx_5.reference_range = '150-360'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='787-2', cwe_2='B-MCV', cwe_3='LAB_B')
        obx_6.obx_5 = '92'
        obx_6.units = CWE(cwe_1='fl')
        obx_6.reference_range = '82-98'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='785-6', cwe_2='B-MCH', cwe_3='LAB_B')
        obx_7.obx_5 = '31.8'
        obx_7.units = CWE(cwe_1='pg')
        obx_7.reference_range = '27.0-33.0'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509093000'

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
    """ Based on live/fi/fi-multilab.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='IMMUNOANALYZER')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000004', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='200170-234D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Saarinen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puijonkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234602'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_C', pl_2='PPKL', pl_3='Triage 1', pl_5='SHP_C')
        pv1.pv1_7 = 'DR1003^Tuominen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI1000003')

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
        orc.placer_order_number = EI(ei_1='ORD1000004', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509091500^^S'
        orc.date_time_of_order_event = '20260509091500'
        orc.orc_10 = 'DR1003^Tuominen^Matti^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000004', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='LAB_C')
        obr.observation_date_time = '20260509091500'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR1003^Tuominen^Matti^^^LL^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000004', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Seerumi', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509091000')
        spm.specimen_collection_date_time = DR(dr_1='20260509091000')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='IMMUNOANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509101000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000004', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='200170-234D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Saarinen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puijonkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234602'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000004', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000004', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509091500^^S'
        orc.date_time_of_order_event = '20260509101000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000004', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000004', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='LAB_C')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1003^Tuominen^Matti^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509101000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='P-TnT', cwe_3='LN')
        obx.obx_5 = '425'
        obx.units = CWE(cwe_1='ng/l')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509101000'

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
    """ Based on live/fi/fi-multilab.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='MULTILAB')
        msh.receiving_facility = HD(hd_1='COAG_ANALYZER')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000005', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='120470-567E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Järvinen', xpn_2='Raili', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19700412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 22', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0407766556'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='KIR2', pl_3='Huone 210', pl_4='Vuode 2', pl_5='SHP_B')
        pv1.pv1_7 = 'DR1004^Aalto^Mikko^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000002')

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
        orc.placer_order_number = EI(ei_1='ORD1000005', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_10 = 'DR1004^Aalto^Mikko^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000005', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='5902', cwe_2='P-TT-INR', cwe_3='LAB_B')
        obr.observation_date_time = '20260509083000'
        obr.obr_15 = 'DR1004^Aalto^Mikko^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD1000005', ei_2='LIS_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='3173-2', cwe_2='P-APTT', cwe_3='LAB_B')
        obr_2.observation_date_time = '20260509083000'
        obr_2.obr_15 = 'DR1004^Aalto^Mikko^^^LL^Lääkäri'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000005', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='CIT', cwe_2='Sitraattiplasma', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509082500')
        spm.specimen_collection_date_time = DR(dr_1='20260509082500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MULTILAB')
        msh.sending_facility = HD(hd_1='COAG_ANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000005', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='120470-567E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Järvinen', xpn_2='Raili', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19700412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 22', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0407766556'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000005', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000005', ei_2='MULTILAB')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509100000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000005', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000005', ei_2='MULTILAB')
        obr.universal_service_identifier = CWE(cwe_1='5902', cwe_2='P-TT-INR', cwe_3='LAB_B')
        obr.observation_date_time = '20260509084000'
        obr.obr_14 = '20260509084000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1004^Aalto^Mikko^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='P-TT-INR', cwe_3='LN')
        obx.obx_5 = '1.1'
        obx.reference_range = '0.9-1.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3173-2', cwe_2='P-APTT', cwe_3='LN')
        obx_2.obx_5 = '30'
        obx_2.units = CWE(cwe_1='s')
        obx_2.reference_range = '23-33'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509100000'

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
    """ Based on live/fi/fi-multilab.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='BGA_ANALYZER')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000006', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='100740+789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Erkki', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19400710'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tehtaankatu 3', xad_3='Helsinki', xad_5='00140', xad_6='FIN')
        pid.pid_13 = '^^PH^0913456792'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='TEHO', pl_3='Paikka 3', pl_5='SHP_A')
        pv1.pv1_7 = 'DR1005^Salonen^Ari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000003')

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
        orc.placer_order_number = EI(ei_1='ORD1000006', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509085000^^S'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_10 = 'DR1005^Salonen^Ari^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000006', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='aB-Verikaasuanalyysi', cwe_3='LN')
        obr.observation_date_time = '20260509085000'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR1005^Salonen^Ari^^^LL^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000006', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='ART', cwe_2='Valtimoveri', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509084500')
        spm.specimen_collection_date_time = DR(dr_1='20260509084500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='BGA_ANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000006', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='100740+789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Erkki', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19400710'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tehtaankatu 3', xad_3='Helsinki', xad_5='00140', xad_6='FIN')
        pid.pid_13 = '^^PH^0913456792'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000006', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000006', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509085000^^S'
        orc.date_time_of_order_event = '20260509090000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000006', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000006', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='aB-Verikaasuanalyysi', cwe_3='LN')
        obr.observation_date_time = '20260509085500'
        obr.obr_14 = '20260509085500'
        obr.obr_15 = '^^aB'
        obr.obr_16 = 'DR1005^Salonen^Ari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='aB-pH', cwe_3='LN')
        obx.obx_5 = '7.35'
        obx.reference_range = '7.35-7.45'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='aB-pCO2', cwe_3='LN')
        obx_2.obx_5 = '6.8'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='aB-pO2', cwe_3='LN')
        obx_3.obx_5 = '9.5'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '11.0-14.4'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='aB-HCO3', cwe_3='LN')
        obx_4.obx_5 = '28.0'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='aB-BE', cwe_3='LN')
        obx_5.obx_5 = '3.2'
        obx_5.units = CWE(cwe_1='mmol/l')
        obx_5.reference_range = '-2.5-2.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='aB-SatO2', cwe_3='LN')
        obx_6.obx_5 = '91'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2524-7', cwe_2='aB-Laktaatti', cwe_3='LN')
        obx_7.obx_5 = '3.5'
        obx_7.units = CWE(cwe_1='mmol/l')
        obx_7.reference_range = '0.5-2.2'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509090000'

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
    """ Based on live/fi/fi-multilab.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='ANALYZER_1')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='QC_NORMAL', cx_4='LAB_A', cx_5='QC')
        pid.patient_name = XPN(xpn_1='QC', xpn_2='Normal Level 1')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='QC_ORD001', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='QC_RES001', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509070000^^R'
        orc.date_time_of_order_event = '20260509070000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QC_ORD001', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='QC_RES001', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='LAB_A')
        obr.observation_date_time = '20260509065500'
        obr.obr_14 = '20260509065500'
        obr.obr_15 = '^^QC'
        obr.results_rpt_status_chng_date_time = '20260509070000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx.obx_5 = '5.0'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.5-5.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509070000'

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
    """ Based on live/fi/fi-multilab.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='IMMUNOANALYZER')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000007', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='220578-123G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Toivonen', xpn_2='Elina', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19780522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Runeberginkatu 40', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234603'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='SHP_A')
        pv1.pv1_7 = 'DR1006^Virtanen^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI1000004')

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
        orc.placer_order_number = EI(ei_1='ORD1000007', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_10 = 'DR1006^Virtanen^Kirsi^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000007', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4832', cwe_2='S-TSH', cwe_3='LAB_A')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = 'DR1006^Virtanen^Kirsi^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD1000007', ei_2='LIS_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='3024-7', cwe_2='S-T4V', cwe_3='LAB_A')
        obr_2.observation_date_time = '20260509090000'
        obr_2.obr_15 = 'DR1006^Virtanen^Kirsi^^^LL^Lääkäri'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000007', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Seerumi', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509085500')
        spm.specimen_collection_date_time = DR(dr_1='20260509085500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, spm]

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
    """ Based on live/fi/fi-multilab.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='IMMUNOANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000007', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='220578-123G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Toivonen', xpn_2='Elina', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19780522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Runeberginkatu 40', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234603'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000007', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000007', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509110000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000007', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000007', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='4832', cwe_2='S-TSH', cwe_3='LAB_A')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1006^Virtanen^Kirsi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='S-TSH', cwe_3='LN')
        obx.obx_5 = '0.15'
        obx.units = CWE(cwe_1='mU/l')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='S-T4V', cwe_3='LN')
        obx_2.obx_5 = '28.5'
        obx_2.units = CWE(cwe_1='pmol/l')
        obx_2.reference_range = '11.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509110000'

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
    """ Based on live/fi/fi-multilab.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FLEXLAB')
        msh.sending_facility = HD(hd_1='ANALYZER_2')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000008', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='080855+234H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Eino', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19550808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puistokatu 12', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0333456789'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000008', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000008', ei_2='FLEXLAB')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509120000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000008', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000008', ei_2='FLEXLAB')
        obr.universal_service_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LAB_B')
        obr.observation_date_time = '20260509101500'
        obr.obr_14 = '20260509101500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1007^Heikkinen^Risto^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509120000'
        obr.result_status = 'P'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx.obx_5 = '6.2'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '3.5-5.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'P'
        obx.date_time_of_the_observation = '20260509120000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Delta-tarkistushälytys: Kalium noussut merkittävästi edellisestä arvosta 4.1 mmol/l.'

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
    """ Based on live/fi/fi-multilab.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MULTILAB')
        msh.sending_facility = HD(hd_1='HEMA_ANALYZER')
        msh.receiving_application = HD(hd_1='LIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_CENTRAL')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000009', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='040490-567J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Pulkkinen', xpn_2='Mari', xpn_3='Johanna', xpn_5='Rouva')
        pid.date_time_of_birth = '19900404'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 25', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234582'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD1000009', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000009', ei_2='MULTILAB')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509113000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000009', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000009', ei_2='MULTILAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_C')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR1008^Lahtinen^Olli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509113000'
        obr.result_status = 'P'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='LAB_C')
        obx.obx_5 = '2.1'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'P'
        obx.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='LAB_C')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '117-155'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'P'
        obx_2.date_time_of_the_observation = '20260509113000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='LAB_C')
        obx_3.obx_5 = '45'
        obx_3.units = CWE(cwe_1='10E9/l')
        obx_3.reference_range = '150-360'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'P'
        obx_3.date_time_of_the_observation = '20260509113000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Laitehälytys: Fragmenttisitosoleja havaittu. Suositellaan mikroskooppikontrollia.'

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
    """ Based on live/fi/fi-multilab.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000010', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='010245+890K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuomi', xpn_2='Helmi', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19450201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unioninkatu 15', xad_3='Helsinki', xad_5='00130', xad_6='FIN')
        pid.pid_13 = '^^PH^0914567891'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='GER1', pl_3='Huone 605', pl_4='Vuode 2', pl_5='SHP_A')
        pv1.pv1_7 = 'DR1009^Virtanen^Kari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000004')

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
        orc.placer_order_number = EI(ei_1='ORD1000010', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000010', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509070000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000010', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000010', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Laaja metabolinen paneeli', cwe_3='LN')
        obr.observation_date_time = '20260509072000'
        obr.obr_14 = '20260509072000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR1009^Virtanen^Kari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '140'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx_2.obx_5 = '4.0'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='fP-Krea', cwe_3='LN')
        obx_3.obx_5 = '95'
        obx_3.units = CWE(cwe_1='umol/l')
        obx_3.reference_range = '50-90'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx_4.obx_5 = '7.2'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '4.0-6.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laboratorioraportti', cwe_3='L')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-multilab.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MLAB000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000003', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 44', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654339'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS1', pl_3='Huone 312', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR1002^Laine^Elina^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000001')

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
        orc.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES1000011', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509082000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000003', ei_2='LIS_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES1000011', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_B')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR1002^Laine^Elina^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='LAB_B')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='LAB_B')
        obx_2.obx_5 = '148'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '134-167'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='LAB_B')
        obx_3.obx_5 = '225'
        obx_3.units = CWE(cwe_1='10E9/l')
        obx_3.reference_range = '150-360'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Kumulatiivinen raportti', cwe_3='L')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iagoK'
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/fi/fi-multilab.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_CENTRAL')
        msh.receiving_application = HD(hd_1='FLEXLAB')
        msh.receiving_facility = HD(hd_1='ANALYZER_2')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MLAB000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT1000008', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='080855+234H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Eino', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19550808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puistokatu 12', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0333456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS2', pl_3='Huone 505', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR1007^Heikkinen^Risto^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO1000005')

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
        orc.placer_order_number = EI(ei_1='ORD1000011', ei_2='LIS_SYSTEM')
        orc.orc_7 = '^^^20260509130000^^S'
        orc.date_time_of_order_event = '20260509130000'
        orc.orc_10 = 'DR1007^Heikkinen^Risto^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1000011', ei_2='LIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LAB_B')
        obr.observation_date_time = '20260509130000'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR1007^Heikkinen^Risto^^^LL^Lääkäri'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Uusintamääritys hemolyysiepäilyn vuoksi. Uusi näyte otettu.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000011', eip_2='LIS_SYSTEM')
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Seerumi', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509125500')
        spm.specimen_collection_date_time = DR(dr_1='20260509125500')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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

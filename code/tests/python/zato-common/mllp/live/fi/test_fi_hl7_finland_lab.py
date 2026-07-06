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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import MSH, OBR, OBX, ORC, PID, PV1, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-hl7-finland-lab.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_A')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 10', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234593'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI1', pl_3='Vastaanottohuone 3', pl_5='SHP_A')
        pv1.pv1_7 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800001')

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
        orc.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='LAB_A')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='LAB_A')
        obr_2.observation_date_time = '20260509080000'
        obr_2.obr_15 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr_3.universal_service_identifier = CWE(cwe_1='2085', cwe_2='P-ALAT', cwe_3='LAB_A')
        obr_3.observation_date_time = '20260509080000'
        obr_3.obr_15 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr_4.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='LAB_A')
        obr_4.observation_date_time = '20260509080000'
        obr_4.obr_15 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr_5 = OBR()
        obr_5.set_id_obr = '5'
        obr_5.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr_5.universal_service_identifier = CWE(cwe_1='4832', cwe_2='S-TSH', cwe_3='LAB_A')
        obr_5.observation_date_time = '20260509080000'
        obr_5.obr_15 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4, obr_5]

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 10', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234593'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI1', pl_3='Vastaanottohuone 3', pl_5='SHP_A')
        pv1.pv1_7 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800001')

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
        orc.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800001', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800001', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800001', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='LAB_A')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR800^Korhonen^Satu^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx.obx_5 = '5.6'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-6.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx_2.obx_5 = '75'
        obx_2.units = CWE(cwe_1='umol/l')
        obx_2.reference_range = '50-90'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1742-6', cwe_2='P-ALAT', cwe_3='LN')
        obx_3.obx_5 = '30'
        obx_3.units = CWE(cwe_1='U/l')
        obx_3.reference_range = '<40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='LAB_A')
        obx_4.obx_5 = '1'
        obx_4.units = CWE(cwe_1='mg/l')
        obx_4.reference_range = '<3'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3016-3', cwe_2='S-TSH', cwe_3='LN')
        obx_5.obx_5 = '2.8'
        obx_5.units = CWE(cwe_1='mU/l')
        obx_5.reference_range = '0.27-4.20'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_B')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_B')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800002', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Kaarina', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hämeenkatu 20', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876555'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS1', pl_3='Huone 305', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800001')

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
        orc.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_10 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_B')
        obr.observation_date_time = '20260509083000'
        obr.obr_15 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='3002', cwe_2='B-Diffi', cwe_3='LAB_B')
        obr_2.observation_date_time = '20260509083000'
        obr_2.obr_15 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        obr_3.universal_service_identifier = CWE(cwe_1='5902', cwe_2='P-TT-INR', cwe_3='LAB_B')
        obr_3.observation_date_time = '20260509083000'
        obr_3.obr_15 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800002', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Kaarina', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hämeenkatu 20', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876555'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS1', pl_3='Huone 305', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800001')

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
        orc.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800002', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800002', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='LAB_B')
        obr.observation_date_time = '20260509084500'
        obr.obr_14 = '20260509084500'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='LAB_B')
        obx.obx_5 = '8.1'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2171', cwe_2='B-Eryt', cwe_3='LAB_B')
        obx_2.obx_5 = '4.10'
        obx_2.units = CWE(cwe_1='10E12/l')
        obx_2.reference_range = '3.90-5.20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='LAB_B')
        obx_3.obx_5 = '125'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '117-155'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4679', cwe_2='B-HKR', cwe_3='LAB_B')
        obx_4.obx_5 = '0.38'
        obx_4.units = CWE(cwe_1='osuus')
        obx_4.reference_range = '0.35-0.46'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='LAB_B')
        obx_5.obx_5 = '195'
        obx_5.units = CWE(cwe_1='10E9/l')
        obx_5.reference_range = '150-360'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='B-Neutro', cwe_3='LAB_B')
        obx_6.obx_5 = '60'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40-75'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='736-9', cwe_2='B-Lymfo', cwe_3='LAB_B')
        obx_7.obx_5 = '30'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '20-45'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5905-5', cwe_2='B-Mono', cwe_3='LAB_B')
        obx_8.obx_5 = '7'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '2-10'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='713-8', cwe_2='B-Eosino', cwe_3='LAB_B')
        obx_9.obx_5 = '2'
        obx_9.units = CWE(cwe_1='%')
        obx_9.reference_range = '1-6'
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='706-2', cwe_2='B-Baso', cwe_3='LAB_B')
        obx_10.obx_5 = '1'
        obx_10.units = CWE(cwe_1='%')
        obx_10.reference_range = '0-2'
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20260509143000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_C')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_C')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800003', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='080855+890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Eino', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19550808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kauppakatu 5', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0171234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_C', pl_2='INF1', pl_3='Huone 401', pl_4='Vuode 1', pl_5='SHP_C')
        pv1.pv1_7 = 'DR802^Hämäläinen^Minna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800002')

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
        orc.placer_order_number = EI(ei_1='ORD800003', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_10 = 'DR802^Hämäläinen^Minna^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800003', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='LAB_C')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = 'DR802^Hämäläinen^Minna^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_C')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_C')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800003', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='080855+890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Eino', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19550808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kauppakatu 5', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0171234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_C', pl_2='INF1', pl_3='Huone 401', pl_4='Vuode 1', pl_5='SHP_C')
        pv1.pv1_7 = 'DR802^Hämäläinen^Minna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800002')

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
        orc.placer_order_number = EI(ei_1='ORD800003', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800003', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260511160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800003', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800003', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='LAB_C')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^PU'
        obr.obr_16 = 'DR802^Hämäläinen^Minna^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260511160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='LAB_C')
        obx.obx_5 = 'KPNE^Klebsiella pneumoniae^LAB_C'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='ABRES', cwe_2='Herkkyys', cwe_3='LAB_C')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Ampisilliini R, Kefuroksiimi S, Siprofloksasiini S, Meropeneemi S, Gentamysiini S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260511160000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_D')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_D_VP')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800004', cx_4='HOSP_D', cx_5='MR'), CX(cx_1='250195-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Tiina', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19950125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Isokatu 30', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234578'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_D', pl_2='SYN1', pl_3='Huone 102', pl_4='Vuode 1', pl_5='SHP_D')
        pv1.pv1_7 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800003')

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
        orc.placer_order_number = EI(ei_1='ORD800004', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800004', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1305', cwe_2='E-ABORh', cwe_3='LAB_D_VP')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD800004', ei_2='EHR_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='SOPIVUUS', cwe_2='E-X-koe', cwe_3='LAB_D_VP')
        obr_2.observation_date_time = '20260509100000'
        obr_2.obr_15 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_D_VP')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_D')
        msh.date_time_of_message = '20260509133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800004', cx_4='HOSP_D', cx_5='MR'), CX(cx_1='250195-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Tiina', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19950125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Isokatu 30', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234578'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_D', pl_2='SYN1', pl_3='Huone 102', pl_4='Vuode 1', pl_5='SHP_D')
        pv1.pv1_7 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800003')

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
        orc.placer_order_number = EI(ei_1='ORD800004', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800004', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509133000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800004', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800004', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1305', cwe_2='E-ABORh', cwe_3='LAB_D_VP')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR803^Lehtonen^Anneli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='E-ABO', cwe_3='LN')
        obx.obx_5 = 'O^Veriryhmä O^LAB_D_VP'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='E-Rh', cwe_3='LN')
        obx_2.obx_5 = 'POS^Rh positiivinen^LAB_D_VP'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='SOPIVUUS', cwe_2='E-X-koe', cwe_3='LAB_D_VP')
        obx_3.obx_5 = 'NEG^Sopivuuskoe negatiivinen^LAB_D_VP'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509133000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509144000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800005', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='030488-456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heikkinen', xpn_2='Laura', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19880403'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Aleksanterinkatu 15', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234594'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI2', pl_3='Vastaanottohuone 5', pl_5='SHP_A')
        pv1.pv1_7 = 'DR804^Järvinen^Olli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800002')

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
        orc.placer_order_number = EI(ei_1='ORD800005', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800005', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509144000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800005', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800005', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='2930', cwe_2='U-KemSeul', cwe_3='LAB_A')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^U'
        obr.obr_16 = 'DR804^Järvinen^Olli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509144000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='U-Väri', cwe_3='LN')
        obx.obx_5 = 'Keltainen'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2756-5', cwe_2='U-pH', cwe_3='LN')
        obx_2.obx_5 = '5.5'
        obx_2.reference_range = '5.0-8.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='20454-5', cwe_2='U-Prot', cwe_3='LN')
        obx_3.obx_5 = 'Neg'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5792-7', cwe_2='U-Gluk', cwe_3='LN')
        obx_4.obx_5 = 'Neg'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5811-5', cwe_2='U-OmPaino', cwe_3='LN')
        obx_5.obx_5 = '1.020'
        obx_5.reference_range = '1.005-1.030'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='20408-1', cwe_2='U-Leuk', cwe_3='LN')
        obx_6.obx_5 = 'Neg'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509144000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='20405-7', cwe_2='U-Erit', cwe_3='LN')
        obx_7.obx_5 = 'Neg'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509144000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800006', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='100740+789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Erkki', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19400710'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pirkankatu 42', xad_3='Tampere', xad_5='33230', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345680'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='TEHO', pl_3='Paikka 5', pl_5='SHP_B')
        pv1.pv1_7 = 'DR805^Salonen^Ari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800004')

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
        orc.placer_order_number = EI(ei_1='ORD800006', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800006', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509093000^^S'
        orc.date_time_of_order_event = '20260509103000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800006', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800006', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='aB-Verikaasuanalyysi', cwe_3='LN')
        obr.observation_date_time = '20260509094000'
        obr.obr_14 = '20260509094000'
        obr.obr_15 = '^^aB'
        obr.obr_16 = 'DR805^Salonen^Ari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='aB-pH', cwe_3='LN')
        obx.obx_5 = '7.41'
        obx.reference_range = '7.35-7.45'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='aB-pCO2', cwe_3='LN')
        obx_2.obx_5 = '5.3'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='aB-pO2', cwe_3='LN')
        obx_3.obx_5 = '12.1'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '11.0-14.4'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='aB-HCO3', cwe_3='LN')
        obx_4.obx_5 = '24.5'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '22.0-26.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='aB-BE', cwe_3='LN')
        obx_5.obx_5 = '0.5'
        obx_5.units = CWE(cwe_1='mmol/l')
        obx_5.reference_range = '-2.5-2.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='aB-SatO2', cwe_3='LN')
        obx_6.obx_5 = '97'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509103000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_E')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_E')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800007', cx_4='HOSP_E', cx_5='MR'), CX(cx_1='200170-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Saarinen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 8', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234595'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_E', pl_2='PPKL', pl_3='Triage 1', pl_5='SHP_E')
        pv1.pv1_7 = 'DR806^Aalto^Timo^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800003')

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
        orc.placer_order_number = EI(ei_1='ORD800007', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509091500^^S'
        orc.date_time_of_order_event = '20260509091500'
        orc.orc_10 = 'DR806^Aalto^Timo^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800007', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='LAB_E')
        obr.observation_date_time = '20260509091500'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR806^Aalto^Timo^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD800007', ei_2='EHR_SYSTEM')
        obr_2.universal_service_identifier = CWE(cwe_1='33762-6', cwe_2='P-NTproBNP', cwe_3='LAB_E')
        obr_2.observation_date_time = '20260509091500'
        obr_2.relevant_clinical_information = CWE(cwe_1='S')
        obr_2.obr_15 = 'DR806^Aalto^Timo^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_E')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_E')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800007', cx_4='HOSP_E', cx_5='MR'), CX(cx_1='200170-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Saarinen', xpn_2='Pekka', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19700120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 8', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234595'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_E', pl_2='PPKL', pl_3='Triage 1', pl_5='SHP_E')
        pv1.pv1_7 = 'DR806^Aalto^Timo^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800003')

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
        orc.placer_order_number = EI(ei_1='ORD800007', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800007', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509091500^^S'
        orc.date_time_of_order_event = '20260509110000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800007', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800007', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='LAB_E')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR806^Aalto^Timo^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='P-TnT', cwe_3='LN')
        obx.obx_5 = '180'
        obx.units = CWE(cwe_1='ng/l')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33762-6', cwe_2='P-NTproBNP', cwe_3='LN')
        obx_2.obx_5 = '850'
        obx_2.units = CWE(cwe_1='ng/l')
        obx_2.reference_range = '<125'
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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800002', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Kaarina', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hämeenkatu 20', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876555'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='SIS1', pl_3='Huone 305', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800001')

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
        orc.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800008', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800002', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800008', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='5902', cwe_2='P-TT-INR', cwe_3='LAB_B')
        obr.observation_date_time = '20260509084500'
        obr.obr_14 = '20260509084500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR801^Mäkinen^Harri^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='P-TT-INR', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.reference_range = '0.9-1.2'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3173-2', cwe_2='P-APTT', cwe_3='LN')
        obx_2.obx_5 = '35'
        obx_2.units = CWE(cwe_1='s')
        obx_2.reference_range = '23-33'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3255-7', cwe_2='P-Fibrino', cwe_3='LN')
        obx_3.obx_5 = '4.5'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '1.7-4.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509152000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800008', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='280465-345H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lahtinen', xpn_2='Markku', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19650228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulevardi 10', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654335'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='SHP_A')
        pv1.pv1_7 = 'DR807^Tuominen^Leena^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800004')

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
        orc.placer_order_number = EI(ei_1='ORD800008', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800009', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509152000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800008', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800009', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='4600', cwe_2='fP-Kol', cwe_3='LAB_A')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR807^Tuominen^Leena^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509152000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='fP-Kol', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '<5.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='fP-Kol-HDL', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '>1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2089-1', cwe_2='fP-Kol-LDL', cwe_3='LN')
        obx_3.obx_5 = '5.1'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '<3.0'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509152000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2571-1', cwe_2='fP-Trigly', cwe_3='LN')
        obx_4.obx_5 = '2.6'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '<1.7'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509152000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800009', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='010245+678J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuomi', xpn_2='Helmi', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19450201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 55', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0913456790'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='GER1', pl_3='Huone 602', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR808^Virtanen^Kari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800005')

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
        orc.placer_order_number = EI(ei_1='ORD800009', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800010', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509070000^^R'
        orc.date_time_of_order_event = '20260509163000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800009', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800010', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Laaja metabolinen paneeli', cwe_3='LN')
        obr.observation_date_time = '20260509072000'
        obr.obr_14 = '20260509072000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR808^Virtanen^Kari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '136'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='fP-Krea', cwe_3='LN')
        obx_3.obx_5 = '118'
        obx_3.units = CWE(cwe_1='umol/l')
        obx_3.reference_range = '50-90'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx_4.obx_5 = '6.8'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '4.0-6.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Kumulatiivinen laboratorioraportti', cwe_3='L')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKPj4K'
        )
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509163000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_B')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_B')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800010', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='050572-901K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korpi', xpn_2='Ilkka', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19720505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Teiskontie 33', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234579'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='NEUR1', pl_3='Huone 312', pl_4='Vuode 2', pl_5='SHP_B')
        pv1.pv1_7 = 'DR809^Rantanen^Kari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800006')

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
        orc.placer_order_number = EI(ei_1='ORD800010', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR809^Rantanen^Kari^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800010', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='3084-1', cwe_2='S-Valproaatti', cwe_3='LN')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR809^Rantanen^Kari^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800010', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='050572-901K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korpi', xpn_2='Ilkka', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19720505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Teiskontie 33', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234579'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='NEUR1', pl_3='Huone 312', pl_4='Vuode 2', pl_5='SHP_B')
        pv1.pv1_7 = 'DR809^Rantanen^Kari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800006')

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
        orc.placer_order_number = EI(ei_1='ORD800010', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800011', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800010', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800011', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='3084-1', cwe_2='S-Valproaatti', cwe_3='LN')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR809^Rantanen^Kari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3084-1', cwe_2='S-Valproaatti', cwe_3='LN')
        obx.obx_5 = '450'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '350-700'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_F_PAT')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_F')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800011', cx_4='HOSP_F', cx_5='MR'), CX(cx_1='220378-234L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Salminen', xpn_2='Mirja', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Eerikinkatu 8', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234596'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_F', pl_2='POLI4', pl_3='Vastaanottohuone 2', pl_5='SHP_F')
        pv1.pv1_7 = 'DR810^Koivunen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800005')

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
        orc.placer_order_number = EI(ei_1='ORD800011', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800012', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260506100000^^R'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800011', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800012', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='60570-9', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20260506102000'
        obr.obr_14 = '20260506102000'
        obr.obr_15 = '^^Biopsia'
        obr.obr_16 = 'DR810^Koivunen^Matti^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report text', cwe_3='LN')
        obx.obx_5 = 'Ihobiopsian histologinen tutkimus: Basaliooma, nodulaarinen tyyppi. Leikkausmarginaalit puhtaat.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Patologian lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoy'
            'IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCj4+CmVuZG9iagoK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509170000'

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='LAB_SYSTEM')
        msh.receiving_facility = HD(hd_1='LAB_A')
        msh.date_time_of_message = '20260509094000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'FI_LAB000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800012', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='110690-567M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kettunen', xpn_2='Janne', xpn_3='Mikael', xpn_5='Herra')
        pid.date_time_of_birth = '19900611'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Runeberginkatu 30', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654336'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='KIR1', pl_3='Huone 208', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR811^Leppänen^Satu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO800007')

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
        orc.placer_order_number = EI(ei_1='ORD800012', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509094000^^R'
        orc.date_time_of_order_event = '20260509094000'
        orc.orc_10 = 'DR811^Leppänen^Satu^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800012', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Dr-BaktVi', cwe_3='LAB_A')
        obr.observation_date_time = '20260509094000'
        obr.obr_15 = 'DR811^Leppänen^Satu^^^LL^Lääkäri'

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
        spm.spm_3 = 'DR^Dreeni^LAB_A'
        spm.specimen_handling_code = CWE(cwe_1='20260509094000')
        spm.specimen_risk_code = CWE(cwe_1='20260509094000')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm]

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
    """ Based on live/fi/fi-hl7-finland-lab.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYSTEM')
        msh.sending_facility = HD(hd_1='LAB_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FI_LAB000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800013', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='040575-890N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Järvinen', xpn_2='Riitta', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19750504'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tehtaankatu 20', xad_3='Helsinki', xad_5='00140', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234597'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='POLI5', pl_3='Vastaanottohuone 9', pl_5='SHP_A')
        pv1.pv1_7 = 'DR812^Kinnunen^Ville^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI800006')

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
        orc.placer_order_number = EI(ei_1='ORD800013', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES800013', ei_2='LAB_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800013', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES800013', ei_2='LAB_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='U-BaktVi', cwe_3='LAB_A')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^U'
        obr.obr_16 = 'DR812^Kinnunen^Ville^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='1155', cwe_2='U-BaktVi', cwe_3='LAB_A')
        obx.obx_5 = 'ECOL^Escherichia coli^LAB_A'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='BAKT_MAARA', cwe_2='Bakteerimäärä', cwe_3='LAB_A')
        obx_2.obx_5 = '100000'
        obx_2.units = CWE(cwe_1='pmy/ml')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='ABRES', cwe_2='Herkkyys', cwe_3='LAB_A')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Nitrofurantoiini S, Trimetopriimi S, Siprofloksasiini S, Ampisilliini R'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

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

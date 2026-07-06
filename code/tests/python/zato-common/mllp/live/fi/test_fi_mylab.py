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
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-mylab.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-mylab.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MYLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200001', cx_4='TAYS', cx_5='MR'), CX(cx_1='150975-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Marko', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19750915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 12', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234501'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SISÄ1', pl_3='Vastaanottohuone 3', pl_5='PSHP')
        pv1.pv1_7 = 'DR200^Korhonen^Sirkka^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200001', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'DR200^Korhonen^Sirkka^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200001', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = 'DR200^Korhonen^Sirkka^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-mylab.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MYLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200002', cx_4='TAYS', cx_5='MR'), CX(cx_1='220880-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Kaija', xpn_3='Elina', xpn_5='Rouva')
        pid.date_time_of_birth = '19800822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 45', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876544'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SISÄ2', pl_3='Vastaanottohuone 5', pl_5='PSHP')
        pv1.pv1_7 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_10 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509083000'
        obr.obr_15 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        obr_2.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='PSHP_LAB')
        obr_2.observation_date_time = '20260509083000'
        obr_2.obr_15 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        obr_3.universal_service_identifier = CWE(cwe_1='2085', cwe_2='P-ALAT', cwe_3='PSHP_LAB')
        obr_3.observation_date_time = '20260509083000'
        obr_3.obr_15 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        obr_4.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='PSHP_LAB')
        obr_4.observation_date_time = '20260509083000'
        obr_4.obr_15 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/fi/fi-mylab.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200001', cx_4='TAYS', cx_5='MR'), CX(cx_1='150975-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Marko', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19750915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 12', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234501'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SISÄ1', pl_3='Vastaanottohuone 3', pl_5='PSHP')
        pv1.pv1_7 = 'DR200^Korhonen^Sirkka^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200001', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200001', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509120000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200001', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200001', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR200^Korhonen^Sirkka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509120000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='PSHP_LAB')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2171', cwe_2='B-Eryt', cwe_3='PSHP_LAB')
        obx_2.obx_5 = '4.52'
        obx_2.units = CWE(cwe_1='10E12/l')
        obx_2.reference_range = '4.25-5.70'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='PSHP_LAB')
        obx_3.obx_5 = '142'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '134-167'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='PSHP_LAB')
        obx_4.obx_5 = '212'
        obx_4.units = CWE(cwe_1='10E9/l')
        obx_4.reference_range = '150-360'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4679', cwe_2='B-HKR', cwe_3='PSHP_LAB')
        obx_5.obx_5 = '0.42'
        obx_5.units = CWE(cwe_1='osuus')
        obx_5.reference_range = '0.39-0.50'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509120000'

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
    """ Based on live/fi/fi-mylab.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200002', cx_4='TAYS', cx_5='MR'), CX(cx_1='220880-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Kaija', xpn_3='Elina', xpn_5='Rouva')
        pid.date_time_of_birth = '19800822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 45', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876544'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SISÄ2', pl_3='Vastaanottohuone 5', pl_5='PSHP')
        pv1.pv1_7 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200002', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509130000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200002', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200002', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509084000'
        obr.obr_14 = '20260509084000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR201^Mäkinen^Jukka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-6.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

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
    """ Based on live/fi/fi-mylab.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200003', cx_4='TAYS', cx_5='MR'), CX(cx_1='081165-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Pekka', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19651108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pirkankatu 28', xad_3='Tampere', xad_5='33230', xad_6='FIN')
        pid.pid_13 = '^^PH^0331234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='GAS1', pl_3='Huone 402', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR202^Hämäläinen^Laura^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200001')

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
        orc.placer_order_number = EI(ei_1='ORD200003', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200003', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509070000^^R'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200003', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200003', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='2085', cwe_2='P-ALAT', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509072000'
        obr.obr_14 = '20260509072000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR202^Hämäläinen^Laura^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='P-ALAT', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='U/l')
        obx.reference_range = '<40'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='P-ASAT', cwe_3='LN')
        obx_2.obx_5 = '142'
        obx_2.units = CWE(cwe_1='U/l')
        obx_2.reference_range = '<35'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2324-2', cwe_2='P-GT', cwe_3='LN')
        obx_3.obx_5 = '220'
        obx_3.units = CWE(cwe_1='U/l')
        obx_3.reference_range = '<60'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-mylab.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200004', cx_4='TAYS', cx_5='MR'), CX(cx_1='040592-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heikkinen', xpn_2='Satu', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19920504'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Teiskontie 55', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654322'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='ENDO1', pl_3='Vastaanottohuone 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR203^Järvinen^Tommi^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200004', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200004', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200004', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200004', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='4832', cwe_2='S-TSH', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR203^Järvinen^Tommi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='S-TSH', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='mU/l')
        obx.reference_range = '0.27-4.20'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='S-T4V', cwe_3='LN')
        obx_2.obx_5 = '15.8'
        obx_2.units = CWE(cwe_1='pmol/l')
        obx_2.reference_range = '11.0-22.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='S-T3V', cwe_3='LN')
        obx_3.obx_5 = '5.1'
        obx_3.units = CWE(cwe_1='pmol/l')
        obx_3.reference_range = '3.1-6.8'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509143000'

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
    """ Based on live/fi/fi-mylab.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509102000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MYLAB000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200005', cx_4='TAYS', cx_5='MR'), CX(cx_1='300345+678E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Pentti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19450330'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Näsilinnankatu 8', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0339876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI200002')

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
        orc.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509102000^^S'
        orc.date_time_of_order_event = '20260509102000'
        orc.orc_10 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509102000'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        obr_2.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='PSHP_LAB')
        obr_2.observation_date_time = '20260509102000'
        obr_2.relevant_clinical_information = CWE(cwe_1='S')
        obr_2.obr_15 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        obr_3.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='PSHP_LAB')
        obr_3.observation_date_time = '20260509102000'
        obr_3.relevant_clinical_information = CWE(cwe_1='S')
        obr_3.obr_15 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/fi/fi-mylab.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200005', cx_4='TAYS', cx_5='MR'), CX(cx_1='300345+678E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Pentti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19450330'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Näsilinnankatu 8', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0339876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI200002')

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
        orc.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200005', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509102000^^S'
        orc.date_time_of_order_event = '20260509112000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200005', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200005', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509103000'
        obr.obr_14 = '20260509103000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR204^Lehtonen^Anneli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='P-TnT', cwe_3='LN')
        obx.obx_5 = '245'
        obx.units = CWE(cwe_1='ng/l')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509112000'

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
    """ Based on live/fi/fi-mylab.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200006', cx_4='TAYS', cx_5='MR'), CX(cx_1='120470-901F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Järvinen', xpn_2='Raili', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19700412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hallituskatu 19', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0407766554'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='KIR2', pl_3='Huone 312', pl_4='Vuode 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR205^Aalto^Mikko^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200002')

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
        orc.placer_order_number = EI(ei_1='ORD200006', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200006', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200006', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200006', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='5902', cwe_2='P-TT-INR', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR205^Aalto^Mikko^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='P-TT-INR', cwe_3='LN')
        obx.obx_5 = '1.1'
        obx.reference_range = '0.9-1.2'
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
        obx_2.obx_5 = '32'
        obx_2.units = CWE(cwe_1='s')
        obx_2.reference_range = '23-33'
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
        obx_3.obx_5 = '3.2'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '1.7-4.0'
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
    """ Based on live/fi/fi-mylab.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509151000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200007', cx_4='TAYS', cx_5='MR'), CX(cx_1='190685-345G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Salminen', xpn_2='Tuula', xpn_3='Maarit', xpn_5='Rouva')
        pid.date_time_of_birth = '19850619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tammelankatu 22', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0401133445'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='DIAB1', pl_3='Vastaanottohuone 4', pl_5='PSHP')
        pv1.pv1_7 = 'DR206^Nurmi^Elina^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200007', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200007', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509151000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200007', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200007', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='4480', cwe_2='B-HbA1c', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR206^Nurmi^Elina^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509151000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='B-HbA1c', cwe_3='LN')
        obx.obx_5 = '48'
        obx.units = CWE(cwe_1='mmol/mol')
        obx.reference_range = '<42'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509151000'

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
    """ Based on live/fi/fi-mylab.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MYLAB000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200008', cx_4='TAYS', cx_5='MR'), CX(cx_1='051050+456H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Erkki', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19501005'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puistokatu 7', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='INF1', pl_3='Huone 501', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR207^Toivonen^Riitta^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200003')

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
        orc.placer_order_number = EI(ei_1='ORD200008', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR207^Toivonen^Riitta^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200008', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR207^Toivonen^Riitta^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-mylab.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200008', cx_4='TAYS', cx_5='MR'), CX(cx_1='051050+456H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Erkki', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19501005'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puistokatu 7', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='INF1', pl_3='Huone 501', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR207^Toivonen^Riitta^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200003')

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
        orc.placer_order_number = EI(ei_1='ORD200008', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200008', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260511160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200008', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200008', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^PU'
        obr.obr_16 = 'DR207^Toivonen^Riitta^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260511160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='PSHP_LAB')
        obx.obx_5 = 'ECOL^Escherichia coli^PSHP_LAB'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260511160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='ABRES', cwe_2='Herkkyys', cwe_3='PSHP_LAB')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Ampisilliini R, Kefuroksiimi S, Siprofloksasiini S, Meropeneemi S'
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
    """ Based on live/fi/fi-mylab.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509152000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200009', cx_4='TAYS', cx_5='MR'), CX(cx_1='280372-789J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laaksonen', xpn_2='Harri', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19720328'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Verkatehtaankatu 3', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876545'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SISÄ3', pl_3='Vastaanottohuone 6', pl_5='PSHP')
        pv1.pv1_7 = 'DR208^Rantanen^Kirsti^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200009', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200009', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509152000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200009', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200009', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='4600', cwe_2='fP-Kol', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509081500'
        obr.obr_14 = '20260509081500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR208^Rantanen^Kirsti^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509152000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='fP-Kol', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '<5.0'
        obx.interpretation_codes = CWE(cwe_1='H')
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
        obx_2.obx_5 = '1.3'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '>1.0'
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
        obx_3.obx_5 = '3.8'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '<3.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
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
        obx_4.obx_5 = '1.5'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '<1.7'
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
    """ Based on live/fi/fi-mylab.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200010', cx_4='TAYS', cx_5='MR'), CX(cx_1='170288-012K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rinne', xpn_2='Sanna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19880217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Laukontori 4', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234569'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='NEUR1', pl_3='Vastaanottohuone 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR209^Kallio^Jari^^^LL^Lääkäri'

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
        orc.placer_order_number = EI(ei_1='ORD200010', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200010', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509153000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200010', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200010', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='2930', cwe_2='U-KemSeul', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^U'
        obr.obr_16 = 'DR209^Kallio^Jari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='U-Väri', cwe_3='LN')
        obx.obx_5 = 'Keltainen'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2756-5', cwe_2='U-pH', cwe_3='LN')
        obx_2.obx_5 = '6.0'
        obx_2.reference_range = '5.0-8.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

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
        obx_3.date_time_of_the_observation = '20260509153000'

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
        obx_4.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='20408-1', cwe_2='U-Leuk', cwe_3='LN')
        obx_5.obx_5 = 'Neg'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509153000'

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
    """ Based on live/fi/fi-mylab.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200011', cx_4='TAYS', cx_5='MR'), CX(cx_1='090655+234L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuominen', xpn_2='Veikko', xpn_3='Matti', xpn_5='Herra')
        pid.date_time_of_birth = '19550609'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Aleksanterinkatu 31', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^PH^0334567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='HEM1', pl_3='Huone 210', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR210^Virtanen^Olli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200004')

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
        orc.placer_order_number = EI(ei_1='ORD200011', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200011', ei_2='MYLAB')
        orc.orc_7 = '^^^20260508100000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200011', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200011', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='3002', cwe_2='B-Diffi', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260508101500'
        obr.obr_14 = '20260508101500'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR210^Virtanen^Olli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='770-8', cwe_2='B-Neutro', cwe_3='LN')
        obx.obx_5 = '62'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '40-75'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='736-9', cwe_2='B-Lymfo', cwe_3='LN')
        obx_2.obx_5 = '28'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '20-45'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5905-5', cwe_2='B-Mono', cwe_3='LN')
        obx_3.obx_5 = '7'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '2-10'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='713-8', cwe_2='B-Eosino', cwe_3='LN')
        obx_4.obx_5 = '2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '1-6'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='706-2', cwe_2='B-Baso', cwe_3='LN')
        obx_5.obx_5 = '1'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '0-2'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laboratorioraportti', cwe_3='L')
        obx_6.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgo+Pgpl'
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/fi/fi-mylab.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MYLAB000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200012', cx_4='TAYS', cx_5='MR'), CX(cx_1='250195-567M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Ahonen', xpn_2='Tiina', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19950125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 10', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SYN1', pl_3='Huone 105', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR211^Laine^Mirja^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200005')

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
        orc.placer_order_number = EI(ei_1='ORD200012', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR211^Laine^Mirja^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200012', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='1305', cwe_2='E-ABORh', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR211^Laine^Mirja^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-mylab.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200012', cx_4='TAYS', cx_5='MR'), CX(cx_1='250195-567M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Ahonen', xpn_2='Tiina', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19950125'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 10', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='SYN1', pl_3='Huone 105', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR211^Laine^Mirja^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200005')

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
        orc.placer_order_number = EI(ei_1='ORD200012', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200012', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200012', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200012', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='1305', cwe_2='E-ABORh', cwe_3='PSHP_LAB')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR211^Laine^Mirja^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='E-ABO', cwe_3='LN')
        obx.obx_5 = 'A^Veriryhmä A^PSHP_LAB'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='E-Rh', cwe_3='LN')
        obx_2.obx_5 = 'POS^Rh positiivinen^PSHP_LAB'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-mylab.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MYLAB')
        msh.sending_facility = HD(hd_1='TAYS_LAB')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MYLAB000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200013', cx_4='TAYS', cx_5='MR'), CX(cx_1='011242+890N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivisto', xpn_2='Helmi', xpn_3='Annikki', xpn_5='Rouva')
        pid.date_time_of_birth = '19420112'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Keskustori 1', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^PH^0335678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='GER1', pl_3='Huone 601', pl_4='Vuode 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR212^Salonen^Eeva^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200006')

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
        orc.placer_order_number = EI(ei_1='ORD200013', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES200013', ei_2='MYLAB')
        orc.orc_7 = '^^^20260509070000^^R'
        orc.date_time_of_order_event = '20260509163000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200013', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES200013', ei_2='MYLAB')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Laaja metabolinen paneeli', cwe_3='LN')
        obr.observation_date_time = '20260509072000'
        obr.obr_14 = '20260509072000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR212^Salonen^Eeva^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
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
        obx_2.obx_5 = '4.8'
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
        obx_3.obx_5 = '105'
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
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Kumulatiivinen raportti', cwe_3='L')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iagoKMw=='
        )
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509163000'

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
    """ Based on live/fi/fi-mylab.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260509074500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MYLAB000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509074500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200014', cx_4='TAYS', cx_5='MR'), CX(cx_1='010300-123P', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hakala', xpn_2='Juuso', xpn_3='Matias', xpn_5='Herra')
        pid.date_time_of_birth = '20000301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Itsenäisyydenkatu 18', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234570'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='ORT1', pl_3='Huone 220', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR213^Kinnunen^Hannu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200007')
        pv1.pending_location = PL(pl_1='20260509074500')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/fi/fi-mylab.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='MYLAB')
        msh.receiving_facility = HD(hd_1='TAYS_LAB')
        msh.date_time_of_message = '20260514150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'MYLAB000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260514150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT200014', cx_4='TAYS', cx_5='MR'), CX(cx_1='010300-123P', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hakala', xpn_2='Juuso', xpn_3='Matias', xpn_5='Herra')
        pid.date_time_of_birth = '20000301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Itsenäisyydenkatu 18', xad_3='Tampere', xad_5='33500', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234570'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='ORT1', pl_3='Huone 220', pl_4='Vuode 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR213^Kinnunen^Hannu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO200007')
        pv1.pending_location = PL(pl_1='20260509074500')
        pv1.prior_temporary_location = PL(pl_1='20260514150000')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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

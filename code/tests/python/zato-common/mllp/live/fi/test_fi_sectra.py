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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-sectra.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-sectra.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='TAYS_RAD')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600001', cx_4='TAYS', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hakkarainen', xpn_2='Jorma', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 55', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR600^Niemi^Satu^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600001')

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
        orc.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'DR600^Niemi^Satu^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = 'DR600^Niemi^Satu^^^LKT^Lääkäri'
        obr.result_status = 'HENGENAHDISTUS^Hengenahdistus ja yskä'

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
    """ Based on live/fi/fi-sectra.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='TAYS_RAD')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600002', cx_4='TAYS', cx_5='MR'), CX(cx_1='051245+567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Savinainen', xpn_2='Helmi', xpn_3='Annikki', xpn_5='Rouva')
        pid.date_time_of_birth = '19450512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 18', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345679'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR601^Mäntylä^Harri^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600002')

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
        orc.placer_order_number = EI(ei_1='ORD600002', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR601^Mäntylä^Harri^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600002', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='CT pää natiivi', cwe_3='RADLEX')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR601^Mäntylä^Harri^^^LKT^Lääkäri'
        obr.result_status = 'CVA^Äkillinen toispuoleinen heikkous'

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
    """ Based on live/fi/fi-sectra.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_JORVI')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='HUS_RAD')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600003', cx_4='HUS', cx_5='MR'), CX(cx_1='180295-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Olli', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19950218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leppävaarankatu 30', xad_3='Espoo', xad_5='02600', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234574'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JORV', pl_2='ORTPOLI', pl_3='Vastaanottohuone 4', pl_5='HUS')
        pv1.pv1_7 = 'DR602^Korhonen^Antti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600003')

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
        orc.placer_order_number = EI(ei_1='ORD600003', ei_2='APOTTI')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR602^Korhonen^Antti^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600003', ei_2='APOTTI')
        obr.universal_service_identifier = CWE(cwe_1='36109-7', cwe_2='MRI polvi', cwe_3='RADLEX')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR602^Korhonen^Antti^^^LKT^Lääkäri'
        obr.result_status = 'POLVIKIPU^Oikean polven kipu ja turvotus'

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
    """ Based on live/fi/fi-sectra.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='TAYS_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600001', cx_4='TAYS', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hakkarainen', xpn_2='Jorma', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 55', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR600^Niemi^Satu^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600001')

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
        orc.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES600001', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509110000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES600001', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^Thorax'
        obr.obr_16 = 'DR603^Ikäheimo^Reijo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Keuhkokentissä ei infiltraatteja. Sydämen koko normaali. Keuhkovaltimot normaalit. Ei pleuranestettä. Tukiluusto normaalirakenteinen.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

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
    """ Based on live/fi/fi-sectra.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='TAYS_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600002', cx_4='TAYS', cx_5='MR'), CX(cx_1='051245+567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Savinainen', xpn_2='Helmi', xpn_3='Annikki', xpn_5='Rouva')
        pid.date_time_of_birth = '19450512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Satakunnankatu 18', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345679'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR601^Mäntylä^Harri^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600002')

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
        orc.placer_order_number = EI(ei_1='ORD600002', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES600002', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509120000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600002', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES600002', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='CT pää natiivi', cwe_3='RADLEX')
        obr.observation_date_time = '20260509095000'
        obr.obr_14 = '20260509095000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR604^Koskinen^Marja^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509120000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Pään natiivi-TT: Vasemman keskimmäisen aivovaltimon suonitusalueella ei tuoretta infarktia tai verenvuotoa. Vanhat lakunaariset infarktit ba'
            'saaliganglioissa bilateraalisesti. Ventrikulaarinen järjestelmä normaali.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='TT-lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509120000'

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
    """ Based on live/fi/fi-sectra.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='HUS_RAD')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_JORVI')
        msh.date_time_of_message = '20260512150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600003', cx_4='HUS', cx_5='MR'), CX(cx_1='180295-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Olli', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19950218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leppävaarankatu 30', xad_3='Espoo', xad_5='02600', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234574'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JORV', pl_2='ORTPOLI', pl_3='Vastaanottohuone 4', pl_5='HUS')
        pv1.pv1_7 = 'DR602^Korhonen^Antti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600003')

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
        orc.placer_order_number = EI(ei_1='ORD600003', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES600003', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260512150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600003', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES600003', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='36109-7', cwe_2='MRI polvi', cwe_3='RADLEX')
        obr.observation_date_time = '20260511090000'
        obr.obr_14 = '20260511090000'
        obr.obr_15 = '^^MRI'
        obr.obr_16 = 'DR605^Paavola^Timo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260512150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Oikean polven MRI: Mediaalisen menisin posteriorisen sarven horisontaalinen repeämä. Eturistiside ehjä. Lateraalinen meniski normaali. Nivel'
            'pinnassa ei rustodefektejä. Pieni nivelnesteen lisääntyminen.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='MRI-lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoy'
            'IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagoK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260512150000'

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
    """ Based on live/fi/fi-sectra.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TYKS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='VSSHP_RAD')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600004', cx_4='TYKS', cx_5='MR'), CX(cx_1='220470-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lehtinen', xpn_2='Matti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19700422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Linnankatu 45', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234585'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI2', pl_3='Vastaanottohuone 3', pl_5='VSSHP')
        pv1.pv1_7 = 'DR606^Hakala^Sanna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600004')

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
        orc.placer_order_number = EI(ei_1='ORD600004', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509093000^^R'
        orc.date_time_of_order_event = '20260509093000'
        orc.orc_10 = 'DR606^Hakala^Sanna^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600004', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='76830-1', cwe_2='UÄ vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509093000'
        obr.obr_15 = 'DR606^Hakala^Sanna^^^LKT^Lääkäri'
        obr.result_status = 'VATSAKIPU^Ylävatsavaivat'

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
    """ Based on live/fi/fi-sectra.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='VSSHP_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TYKS')
        msh.date_time_of_message = '20260509133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600004', cx_4='TYKS', cx_5='MR'), CX(cx_1='220470-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lehtinen', xpn_2='Matti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19700422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Linnankatu 45', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234585'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TYKS', pl_2='POLI2', pl_3='Vastaanottohuone 3', pl_5='VSSHP')
        pv1.pv1_7 = 'DR606^Hakala^Sanna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600004')

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
        orc.placer_order_number = EI(ei_1='ORD600004', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES600004', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509093000^^R'
        orc.date_time_of_order_event = '20260509133000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600004', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES600004', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='76830-1', cwe_2='UÄ vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509110000'
        obr.obr_14 = '20260509110000'
        obr.obr_15 = '^^UÄ'
        obr.obr_16 = 'DR607^Mattila^Kaisa^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Vatsan UÄ: Maksa normaalikokoinenn, tasainen. Sappirakko normaali, ei sappikiviä. Haima ja perna normaalit. Munuaiset symmetriset, ei hydron'
            'efroosia. Aortta normaalikaliiperinen.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509133000'

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
    """ Based on live/fi/fi-sectra.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='OYS_RAD')
        msh.date_time_of_message = '20260509102000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600005', cx_4='OYS', cx_5='MR'), CX(cx_1='300665-456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karhu', xpn_2='Risto', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19650630'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaaninkatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654331'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='KEUH1', pl_3='Huone 204', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR608^Tolonen^Markku^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO600001')

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
        orc.placer_order_number = EI(ei_1='ORD600005', ei_2='OMNI360')
        orc.orc_7 = '^^^20260509102000^^R'
        orc.date_time_of_order_event = '20260509102000'
        orc.orc_10 = 'DR608^Tolonen^Markku^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600005', ei_2='OMNI360')
        obr.universal_service_identifier = CWE(cwe_1='71275-2', cwe_2='CT thorax varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509102000'
        obr.obr_15 = 'DR608^Tolonen^Markku^^^LKT^Lääkäri'
        obr.result_status = 'KEUHKOSYÖPÄEPÄILY^Keuhkomuutos rtg:ssa'

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
    """ Based on live/fi/fi-sectra.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='OYS_RAD')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600005', cx_4='OYS', cx_5='MR'), CX(cx_1='300665-456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karhu', xpn_2='Risto', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19650630'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaaninkatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654331'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='KEUH1', pl_3='Huone 204', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR608^Tolonen^Markku^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO600001')

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
        orc.placer_order_number = EI(ei_1='ORD600005', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES600005', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509102000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600005', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES600005', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71275-2', cwe_2='CT thorax varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509130000'
        obr.obr_14 = '20260509130000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR609^Mikkonen^Pasi^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Thoraxin varjoaine-TT: Oikean yläkeuhkon apikaaliosassa 28mm spikuloitunut tuumori. Mediastinaaliset imusolmukkeet ei suurentuneet. Ei pleur'
            'anestettä. Suositellaan PET-TT-tutkimusta.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/fi/fi-sectra.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='TAYS_RAD')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600006', cx_4='TAYS', cx_5='MR'), CX(cx_1='130370-789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kärkkäinen', xpn_2='Marja', xpn_3='Liisa', xpn_5='Rouva')
        pid.date_time_of_birth = '19700313'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Puutarhakatu 22', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234586'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='RADPOLI', pl_3='Mammografiahuone 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR610^Aho^Kristiina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600005')

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
        orc.placer_order_number = EI(ei_1='ORD600006', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR610^Aho^Kristiina^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600006', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='Mammografia bilat', cwe_3='RADLEX')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR610^Aho^Kristiina^^^LKT^Lääkäri'
        obr.result_status = 'SEULONTA^Rintasyöpäseulonta'

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
    """ Based on live/fi/fi-sectra.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='TAYS_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000021'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600006', cx_4='TAYS', cx_5='MR'), CX(cx_1='130370-789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kärkkäinen', xpn_2='Marja', xpn_3='Liisa', xpn_5='Rouva')
        pid.date_time_of_birth = '19700313'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Puutarhakatu 22', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234586'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='RADPOLI', pl_3='Mammografiahuone 1', pl_5='PSHP')
        pv1.pv1_7 = 'DR610^Aho^Kristiina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600005')

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
        orc.placer_order_number = EI(ei_1='ORD600006', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES600006', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600006', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES600006', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='Mammografia bilat', cwe_3='RADLEX')
        obr.observation_date_time = '20260509103000'
        obr.obr_14 = '20260509103000'
        obr.obr_15 = '^^MG'
        obr.obr_16 = 'DR611^Saarinen^Leena^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Bilateraalinen mammografia: Rintarauhaskudos ACR B. Ei epäilyttäviä massoja tai mikrokalkkeja. BI-RADS 1, normaali. Seuraava seulonta 2 vuod'
            'en kuluttua.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509143000'

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
    """ Based on live/fi/fi-sectra.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='KYS_RAD')
        msh.date_time_of_message = '20260509104000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600007', cx_4='KYS', cx_5='MR'), CX(cx_1='080288-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kemppainen', xpn_2='Timo', xpn_3='Sakari', xpn_5='Herra')
        pid.date_time_of_birth = '19880208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Minna Canthinkatu 9', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234575'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR612^Partanen^Esa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600006')

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
        orc.placer_order_number = EI(ei_1='ORD600007', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509104000^^S'
        orc.date_time_of_order_event = '20260509104000'
        orc.orc_10 = 'DR612^Partanen^Esa^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600007', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='36267-3', cwe_2='CT vatsa varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509104000'
        obr.obr_15 = 'DR612^Partanen^Esa^^^LKT^Lääkäri'
        obr.result_status = 'VATSAKIPU^Akuutti vatsakipu'

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
    """ Based on live/fi/fi-sectra.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='KYS_RAD')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000023'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600007', cx_4='KYS', cx_5='MR'), CX(cx_1='080288-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kemppainen', xpn_2='Timo', xpn_3='Sakari', xpn_5='Herra')
        pid.date_time_of_birth = '19880208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Minna Canthinkatu 9', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234575'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR612^Partanen^Esa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600006')

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
        orc.placer_order_number = EI(ei_1='ORD600007', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES600007', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509104000^^S'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600007', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES600007', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='36267-3', cwe_2='CT vatsa varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509113000'
        obr.obr_14 = '20260509113000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR613^Tamminen^Juha^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Vatsan varjoaine-TT: Umpilisäke turvonnut, halkaisija 12mm. Ympäröivä rasva ödemaattinen. Appendikoliitti havaittavissa. Löydös sopii akuutt'
            'iin appendisiittiin. Ei suolentukkeumaa.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-sectra.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='HUS_RAD')
        msh.date_time_of_message = '20260509114000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000024'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600008', cx_4='HUS', cx_5='MR'), CX(cx_1='031002-567H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuominen', xpn_2='Nelli', xpn_3='Kristiina', xpn_5='Neiti')
        pid.date_time_of_birth = '20021003'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 42', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876552'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='PPKL', pl_3='Triage 3', pl_5='HUS')
        pv1.pv1_7 = 'DR614^Salonen^Tero^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600007')

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
        orc.placer_order_number = EI(ei_1='ORD600008', ei_2='APOTTI')
        orc.orc_7 = '^^^20260509114000^^S'
        orc.date_time_of_order_event = '20260509114000'
        orc.orc_10 = 'DR614^Salonen^Tero^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600008', ei_2='APOTTI')
        obr.universal_service_identifier = CWE(cwe_1='37534-4', cwe_2='Rtg ranne', cwe_3='RADLEX')
        obr.observation_date_time = '20260509114000'
        obr.obr_15 = 'DR614^Salonen^Tero^^^LKT^Lääkäri'
        obr.result_status = 'RANNE^Rannevamma, kaatuminen'

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
    """ Based on live/fi/fi-sectra.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='HUS_RAD')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000025'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600008', cx_4='HUS', cx_5='MR'), CX(cx_1='031002-567H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuominen', xpn_2='Nelli', xpn_3='Kristiina', xpn_5='Neiti')
        pid.date_time_of_birth = '20021003'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 42', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876552'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='PPKL', pl_3='Triage 3', pl_5='HUS')
        pv1.pv1_7 = 'DR614^Salonen^Tero^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600007')

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
        orc.placer_order_number = EI(ei_1='ORD600008', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES600008', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509114000^^S'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600008', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES600008', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='37534-4', cwe_2='Rtg ranne', cwe_3='RADLEX')
        obr.observation_date_time = '20260509120000'
        obr.obr_14 = '20260509120000'
        obr.obr_15 = '^^Ranne'
        obr.obr_16 = 'DR615^Kallio^Minna^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Ranteen rtg: Distaalisen radiuksen murtuma (Colles), minimaalinen dislokaatio. Ulnan processus styloideus ehjä. Karpaalilinjat normaalit.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-sectra.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='TAYS_RAD')
        msh.date_time_of_message = '20260509101500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'SECTRA000026'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509101500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600009', cx_4='TAYS', cx_5='MR'), CX(cx_1='250890-901J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Katri', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19900825'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Verkatehtaankatu 10', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234587'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='RADPOLI', pl_3='Odotustila', pl_5='PSHP')
        pv1.pv1_7 = 'DR616^Rantala^Ville^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600008')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/fi/fi-sectra.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='TAYS_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'SECTRA000027'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260509113000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600009', cx_4='TAYS', cx_5='MR'), CX(cx_1='250890-901J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Katri', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19900825'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Verkatehtaankatu 10', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234587'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='RADPOLI', pl_3='Tutkimushuone 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR616^Rantala^Ville^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600008')
        pv1.pending_location = PL(pl_1='20260509101500')
        pv1.prior_temporary_location = PL(pl_1='20260509113000')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/fi/fi-sectra.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFECARE')
        msh.sending_facility = HD(hd_1='TAYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='TAYS_RAD')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SECTRA000028'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600010', cx_4='TAYS', cx_5='MR'), CX(cx_1='090175-234K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäntymäki', xpn_2='Riitta', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19750109'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Koulukatu 8', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654332'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='POLI5', pl_3='Vastaanottohuone 10', pl_5='PSHP')
        pv1.pv1_7 = 'DR617^Ahola^Sami^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600009')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CA'
        orc.placer_order_number = EI(ei_1='ORD600009', ei_2='LIFECARE')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509150000'
        orc.orc_10 = 'DR617^Ahola^Sami^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600009', ei_2='LIFECARE')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = 'DR617^Ahola^Sami^^^LKT^Lääkäri'

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
    """ Based on live/fi/fi-sectra.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='TAYS_RAD')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='TAYS')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000029'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600001', cx_4='TAYS', cx_5='MR'), CX(cx_1='120580-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hakkarainen', xpn_2='Jorma', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19800512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 55', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='TAYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSHP')
        pv1.pv1_7 = 'DR600^Niemi^Satu^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600001')

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
        orc.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        orc.filler_order_number = EI(ei_1='RES600001', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600001', ei_2='LIFECARE')
        obr.filler_order_number = EI(ei_1='RES600001', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^Thorax'
        obr.obr_16 = 'DR603^Ikäheimo^Reijo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'C'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Korjattu lausunto: Keuhkokentissä ei infiltraatteja. Sydämen koko normaali. Vasemmalla puolella pieni atelektaasi alakeuhkossa. Ei pleuranes'
            'tettä.'
        )
        obx.observation_result_status = 'C'
        obx.date_time_of_the_observation = '20260509170000'

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

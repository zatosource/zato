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

_md_path = md_path_for('fi', 'fi-hl7-imaging.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-hl7-imaging.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_A')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='100680-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laaksonen', xpn_2='Jari', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800610'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 75', xad_3='Helsinki', xad_5='00270', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234598'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='PPKL', pl_3='Triage 2', pl_5='SHP_A')
        pv1.pv1_7 = 'DR900^Virtanen^Elina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900001')

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
        orc.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_10 = 'DR900^Virtanen^Elina^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = 'DR900^Virtanen^Elina^^^LKT^Lääkäri'
        obr.result_status = 'KUUME^Kuume ja yskä, pneumoniaepäily'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_B')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_B')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900002', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='220570-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Eila', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19700522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hämeenkatu 60', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345681'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='KIR1', pl_3='Huone 304', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR901^Korhonen^Juha^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900001')

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
        orc.placer_order_number = EI(ei_1='ORD900002', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR901^Korhonen^Juha^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900002', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='36267-3', cwe_2='CT vatsa varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR901^Korhonen^Juha^^^LKT^Lääkäri'
        obr.result_status = 'KASVAIN^Vatsan alueen kasvainseuranta'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_C')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_C')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900003', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='051190-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Satu', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19901105'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 18', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876556'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_C', pl_2='NEUR1', pl_3='Vastaanottohuone 2', pl_5='SHP_C')
        pv1.pv1_7 = 'DR902^Mäkinen^Esa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900002')

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
        orc.placer_order_number = EI(ei_1='ORD900003', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR902^Mäkinen^Esa^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900003', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='MRI aivot', cwe_3='RADLEX')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR902^Mäkinen^Esa^^^LKT^Lääkäri'
        obr.result_status = 'MS^MS-taudin seuranta'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_D')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_D')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900004', cx_4='HOSP_D', cx_5='MR'), CX(cx_1='300865-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lehtinen', xpn_2='Pertti', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Isokatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234599'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_D', pl_2='POLI2', pl_3='Vastaanottohuone 4', pl_5='SHP_D')
        pv1.pv1_7 = 'DR903^Laine^Minna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900003')

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
        orc.placer_order_number = EI(ei_1='ORD900004', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509093000^^R'
        orc.date_time_of_order_event = '20260509093000'
        orc.orc_10 = 'DR903^Laine^Minna^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900004', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='76830-1', cwe_2='UÄ vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509093000'
        obr.obr_15 = 'DR903^Laine^Minna^^^LKT^Lääkäri'
        obr.result_status = 'MAKSA^Kohonneet maksa-arvot'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='100680-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laaksonen', xpn_2='Jari', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800610'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 75', xad_3='Helsinki', xad_5='00270', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234598'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='PPKL', pl_3='Triage 2', pl_5='SHP_A')
        pv1.pv1_7 = 'DR900^Virtanen^Elina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900001')

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
        orc.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900001', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509110000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900001', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^Thorax'
        obr.obr_16 = 'DR904^Ikonen^Reijo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Thorax PA+LAT: Oikealla alakeuhkossa infiltraatti, sopii pneumoniaan. Sydämen koko normaali. Ei pleuranestettä. Hilus normaalirakenteinen bi'
            'lateraalisesti.'
        )
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900002', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='220570-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Eila', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19700522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hämeenkatu 60', xad_3='Tampere', xad_5='33200', xad_6='FIN')
        pid.pid_13 = '^^PH^0332345681'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='KIR1', pl_3='Huone 304', pl_4='Vuode 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR901^Korhonen^Juha^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900001')

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
        orc.placer_order_number = EI(ei_1='ORD900002', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900002', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900002', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900002', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='36267-3', cwe_2='CT vatsa varjoaine', cwe_3='RADLEX')
        obr.observation_date_time = '20260509120000'
        obr.obr_14 = '20260509120000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR905^Koskinen^Leena^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Vatsan varjoaine-TT: Maksa-metastaasit pienentyneeet verrattuna aiempaan kuvaukseen. Suurin lesio 18mm (aiemmin 25mm). Ei uusia leesioita. H'
            'aima, perna ja munuaiset normaalit. Ei vapaa nestettä.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

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
        obx_2.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_C')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_C')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900003', cx_4='HOSP_C', cx_5='MR'), CX(cx_1='051190-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Satu', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19901105'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 18', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876556'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_C', pl_2='NEUR1', pl_3='Vastaanottohuone 2', pl_5='SHP_C')
        pv1.pv1_7 = 'DR902^Mäkinen^Esa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900002')

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
        orc.placer_order_number = EI(ei_1='ORD900003', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900003', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260512140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900003', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900003', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='MRI aivot', cwe_3='RADLEX')
        obr.observation_date_time = '20260511090000'
        obr.obr_14 = '20260511090000'
        obr.obr_15 = '^^MRI'
        obr.obr_16 = 'DR906^Paavola^Timo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260512140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Aivojen MRI: Periventrikulaarisesti ja subkortikaalisesti useita T2-hyperintensiivisiä leesioita, joista yksi uusi oikeassa frontaalilohkoss'
            'a. Löydös sopii MS-taudin aktiivisuuteen. Infratentoriaalisesti ei poikkeavaa.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512140000'

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
        obx_2.date_time_of_the_observation = '20260512140000'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_D')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_D')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900004', cx_4='HOSP_D', cx_5='MR'), CX(cx_1='300865-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lehtinen', xpn_2='Pertti', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Isokatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234599'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_D', pl_2='POLI2', pl_3='Vastaanottohuone 4', pl_5='SHP_D')
        pv1.pv1_7 = 'DR903^Laine^Minna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900003')

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
        orc.placer_order_number = EI(ei_1='ORD900004', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900004', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509093000^^R'
        orc.date_time_of_order_event = '20260509130000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900004', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900004', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='76830-1', cwe_2='UÄ vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509110000'
        obr.obr_14 = '20260509110000'
        obr.obr_15 = '^^UÄ'
        obr.obr_16 = 'DR907^Mattila^Sanna^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Vatsan UÄ: Maksa suurentunut, ekorakenteeltaan tasaisesti tiivistynyt, sopii steatoosiin. Sappirakko normaali, ei konkrementteja. Haima norm'
            'aali. Munuaiset symmetriset. Aortta normaali.'
        )
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_E')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_E_NM')
        msh.date_time_of_message = '20260509102000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900005', cx_4='HOSP_E', cx_5='MR'), CX(cx_1='140565-456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Raimo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19650514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 20', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654337'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_E', pl_2='ONK1', pl_3='Huone 205', pl_4='Vuode 1', pl_5='SHP_E')
        pv1.pv1_7 = 'DR908^Ahonen^Tuula^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900002')

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
        orc.placer_order_number = EI(ei_1='ORD900005', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509102000^^R'
        orc.date_time_of_order_event = '20260509102000'
        orc.orc_10 = 'DR908^Ahonen^Tuula^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900005', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='39811-5', cwe_2='Luuston isotooppikuvaus', cwe_3='RADLEX')
        obr.observation_date_time = '20260509102000'
        obr.obr_15 = 'DR908^Ahonen^Tuula^^^LKT^Lääkäri'
        obr.result_status = 'ETÄPESÄKE^Etäpesäke-epäily, eturauhassyöpä'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_E_NM')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_E')
        msh.date_time_of_message = '20260510150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900005', cx_4='HOSP_E', cx_5='MR'), CX(cx_1='140565-456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Raimo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19650514'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 20', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654337'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_E', pl_2='ONK1', pl_3='Huone 205', pl_4='Vuode 1', pl_5='SHP_E')
        pv1.pv1_7 = 'DR908^Ahonen^Tuula^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900002')

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
        orc.placer_order_number = EI(ei_1='ORD900005', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900005', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509102000^^R'
        orc.date_time_of_order_event = '20260510150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900005', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900005', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='39811-5', cwe_2='Luuston isotooppikuvaus', cwe_3='RADLEX')
        obr.observation_date_time = '20260510090000'
        obr.obr_14 = '20260510090000'
        obr.obr_15 = '^^NM'
        obr.obr_16 = 'DR909^Saarinen^Kari^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260510150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Luuston isotooppikuvaus: Oikealla puolella L3-nikamassa lisääntynyt kertymä, sopii metastaattiseen muutokseen. Vasemman lonkan alueella liev'
            'ä kertymän lisääntyminen, todennäköisesti degeneratiivinen muutos. Muilta osin normaali kertymäjakauma.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260510150000'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_A_PET')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900006', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='080375-789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Salminen', xpn_2='Matti', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19750308'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulevardi 30', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234580'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='KEUH1', pl_3='Huone 310', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR910^Nurmi^Harri^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900003')

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
        orc.placer_order_number = EI(ei_1='ORD900006', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509110000^^R'
        orc.date_time_of_order_event = '20260509110000'
        orc.orc_10 = 'DR910^Nurmi^Harri^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900006', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='44136-0', cwe_2='PET-TT koko keho', cwe_3='RADLEX')
        obr.observation_date_time = '20260509110000'
        obr.obr_15 = 'DR910^Nurmi^Harri^^^LKT^Lääkäri'
        obr.result_status = 'KEUHKOSYÖPÄ^Keuhkosyövän levinneisyysselvitys'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_A_PET')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260512160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900006', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='080375-789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Salminen', xpn_2='Matti', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19750308'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulevardi 30', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234580'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='KEUH1', pl_3='Huone 310', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR910^Nurmi^Harri^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900003')

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
        orc.placer_order_number = EI(ei_1='ORD900006', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900006', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509110000^^R'
        orc.date_time_of_order_event = '20260512160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900006', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900006', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='44136-0', cwe_2='PET-TT koko keho', cwe_3='RADLEX')
        obr.observation_date_time = '20260511080000'
        obr.obr_14 = '20260511080000'
        obr.obr_15 = '^^PET'
        obr.obr_16 = 'DR911^Kallio^Minna^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260512160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'PET-TT koko keho: Oikean yläkeuhkon tuumori metabolisesti aktiivinen, SUVmax 12.5. Oikean hilusn imusolmukkeissa metabolista aktiivisuutta, '
            'SUVmax 6.2. Ei kaukoetäpesäkkeitä. Maksa, luusto ja aivot normaalit.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260512160000'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_B')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_B')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900007', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Marja', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Puutarhakatu 30', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234600'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='RADPOLI', pl_3='Mammografiahuone 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR912^Rantala^Kristiina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900004')

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
        orc.placer_order_number = EI(ei_1='ORD900007', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR912^Rantala^Kristiina^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900007', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='Mammografia bilat', cwe_3='RADLEX')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR912^Rantala^Kristiina^^^LKT^Lääkäri'
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_B')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_B')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900007', cx_4='HOSP_B', cx_5='MR'), CX(cx_1='150275-234G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Marja', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Puutarhakatu 30', xad_3='Tampere', xad_5='33210', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234600'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_B', pl_2='RADPOLI', pl_3='Mammografiahuone 1', pl_5='SHP_B')
        pv1.pv1_7 = 'DR912^Rantala^Kristiina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900004')

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
        orc.placer_order_number = EI(ei_1='ORD900007', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900007', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509100000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900007', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900007', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='Mammografia bilat', cwe_3='RADLEX')
        obr.observation_date_time = '20260509103000'
        obr.obr_14 = '20260509103000'
        obr.obr_15 = '^^MG'
        obr.obr_16 = 'DR913^Saarinen^Leena^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Mammografia bilat: Rintarauhaskudos ACR C. Vasemmassa rinnassa yläulkokvadr. 12mm kokoinen epäsäännöllinen muutos. BI-RADS 4, suositellaan j'
            'atkotutkimuksia. Oikeassa rinnassa ei poikkeavaa.'
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_A')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900008', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='010555+678H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuominen', xpn_2='Veikko', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19550501'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Aleksanterinkatu 48', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0913456791'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='KAR1', pl_3='Huone 402', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR914^Salonen^Matti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900004')

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
        orc.placer_order_number = EI(ei_1='ORD900008', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509113000^^R'
        orc.date_time_of_order_event = '20260509113000'
        orc.orc_10 = 'DR914^Salonen^Matti^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900008', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='75635-2', cwe_2='Koronaariangiografia', cwe_3='RADLEX')
        obr.observation_date_time = '20260509113000'
        obr.obr_15 = 'DR914^Salonen^Matti^^^LKT^Lääkäri'
        obr.result_status = 'ANGINA^Stabiili angina pectoris'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900008', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='010555+678H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Tuominen', xpn_2='Veikko', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19550501'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Aleksanterinkatu 48', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0913456791'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='KAR1', pl_3='Huone 402', pl_4='Vuode 1', pl_5='SHP_A')
        pv1.pv1_7 = 'DR914^Salonen^Matti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900004')

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
        orc.placer_order_number = EI(ei_1='ORD900008', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900008', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509113000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900008', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900008', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='75635-2', cwe_2='Koronaariangiografia', cwe_3='RADLEX')
        obr.observation_date_time = '20260509130000'
        obr.obr_14 = '20260509130000'
        obr.obr_15 = '^^ANGIO'
        obr.obr_16 = 'DR915^Toivonen^Kari^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Koronaariangiografia: LAD:ssa proksimaaliosassa 70% ahtauma. RCA ja LCX normaalit. Vasemman kammion toiminta normaali, EF 60%.'
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_D')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_D')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'IMG000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900009', cx_4='HOSP_D', cx_5='MR'), CX(cx_1='200388-901J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kärkkäinen', xpn_2='Anu', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19880320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Albertinkatu 8', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654338'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_D', pl_2='POLI3', pl_3='Vastaanottohuone 6', pl_5='SHP_D')
        pv1.pv1_7 = 'DR916^Hakala^Vesa^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900005')

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
        orc.placer_order_number = EI(ei_1='ORD900009', ei_2='EHR_SYSTEM')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509140000'
        orc.orc_10 = 'DR916^Hakala^Vesa^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900009', ei_2='EHR_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = 'DR916^Hakala^Vesa^^^LKT^Lääkäri'

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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHR_SYSTEM')
        msh.sending_facility = HD(hd_1='HOSPITAL_A')
        msh.receiving_application = HD(hd_1='RIS_SYSTEM')
        msh.receiving_facility = HD(hd_1='RAD_A')
        msh.date_time_of_message = '20260509101000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'IMG000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509101000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900010', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='260895-234K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19950826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Meritullinkatu 5', xad_3='Helsinki', xad_5='00170', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234581'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='RADPOLI', pl_3='Odotustila', pl_5='SHP_A')
        pv1.pv1_7 = 'DR917^Mäkinen^Antti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900006')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509112000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'IMG000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260509112000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900010', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='260895-234K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19950826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Meritullinkatu 5', xad_3='Helsinki', xad_5='00170', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234581'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='RADPOLI', pl_3='Tutkimushuone 3', pl_5='SHP_A')
        pv1.pv1_7 = 'DR917^Mäkinen^Antti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900006')
        pv1.pending_location = PL(pl_1='20260509101000')
        pv1.prior_temporary_location = PL(pl_1='20260509112000')

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/fi/fi-hl7-imaging.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SYSTEM')
        msh.sending_facility = HD(hd_1='RAD_A')
        msh.receiving_application = HD(hd_1='EHR_SYSTEM')
        msh.receiving_facility = HD(hd_1='HOSPITAL_A')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'IMG000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900001', cx_4='HOSP_A', cx_5='MR'), CX(cx_1='100680-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laaksonen', xpn_2='Jari', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19800610'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 75', xad_3='Helsinki', xad_5='00270', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234598'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HOSP_A', pl_2='PPKL', pl_3='Triage 2', pl_5='SHP_A')
        pv1.pv1_7 = 'DR900^Virtanen^Elina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI900001')

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
        orc.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        orc.filler_order_number = EI(ei_1='RES900001', ei_2='RIS_SYSTEM')
        orc.orc_7 = '^^^20260509080000^^S'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900001', ei_2='EHR_SYSTEM')
        obr.filler_order_number = EI(ei_1='RES900001', ei_2='RIS_SYSTEM')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax PA+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^Thorax'
        obr.obr_16 = 'DR904^Ikonen^Reijo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'C'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = (
            'Lisälausunto: Tarkemmassa tarkastelussa infiltraatin yhteydessä nähtävissä pieni bronkogrammi, vahvistaa pneumoniadiagnoosia. Kontrollikuva '
            '2 viikon kuluttua suositeltava.'
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

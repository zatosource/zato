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
from zato.hl7v2.v2_9.datatypes import AUI, CQ, CWE, CX, EI, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RspK22QueryResponse
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ORM_O01, ORU_R01, QBP_Q21, RSP_K22
from zato.hl7v2.v2_9.segments import ERR, EVN, IN1, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, QAK, QPD, QRI, RCP

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-ib-salut.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-ib-salut.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='02')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250918085928'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '63817429'
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.assigned_patient_location = PL(pl_1='CODAUXCENTRO')

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
        orc.placer_order_number = EI(ei_1='95137682')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

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
    """ Based on live/es/es-ib-salut.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='13')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251207145211000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '42583716'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='UEPE', pl_2='0117M', pl_3='0117V', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='FERRANDO', xcn_3='MIQUEL', xcn_4='SERRA', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='PEDH')
        pv1.admit_source = CWE(cwe_1='PEDC')
        pv1.admitting_doctor = XCN(xcn_1='23456', xcn_2='FERRANDO', xcn_3='MIQUEL', xcn_4='SERRA', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025783156', cx_4='20')
        pv1.admit_date_time = '20251207112800000'

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
        orc.placer_order_number = EI(ei_1='18864723', ei_2='20')
        orc.placer_order_group_number = EI(ei_1='8532076', ei_2='20')
        orc.order_status = 'CA'
        orc.orc_7 = '^^^20251207134031000^^1'
        orc.date_time_of_order_event = '20251207134031000'
        orc.orc_12 = '23456^FERRANDO^MIQUEL^SERRA^^^^^018'
        orc.orc_17 = '13336^Hospital Mateu Orfila^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='18864723', ei_2='20')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma (Radelec)', cwe_3='L')
        obr.observation_date_time = '20251207134031000'
        obr.obr_16 = '23456^FERRANDO^MIQUEL^SERRA^^^^^018'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20251207134031000'

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
    """ Based on live/es/es-ib-salut.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='IBE')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='H.Mateu Orfila')
        msh.receiving_facility = HD(hd_1='00')
        msh.date_time_of_message = '20251208111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'cf9gc2641208202511170401'
        msh.processing_id = PT(pt_1='P', pt_2='T')
        msh.version_id = VID(vid_1='25')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')

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
        obr.filler_order_number = EI(ei_1='202512811173455804')
        obr.observation_date_time = '20251208111513'
        obr.filler_field_2 = 'cf8g85b1-d878-54bg-0477-65gdd3ec3c32'
        obr.results_rpt_status_chng_date_time = '20251208111513'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20251208111513'

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr

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
    """ Based on live/es/es-ib-salut.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251207190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '42576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251207190020000'
        evn.event_occurred = '20251207190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025785630', cx_4='20')
        pv1.admit_date_time = '20251207185900000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-ib-salut.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251207190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = '42576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251207190020000'
        evn.event_occurred = '20251207190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025785630', cx_4='20')
        pv1.admit_date_time = '20251207185900000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-ib-salut.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251207190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = '42576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251207190020000'
        evn.event_occurred = '20251207190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='ROCA', xcn_3='LLUC', xcn_4='SASTRE', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025785630', cx_4='20')
        pv1.admit_date_time = '20251207185900000'
        pv1.discharge_date_time = '20251207185900000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-ib-salut.md, message no. 7
    """

    maxDiff = None

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
    """ Based on live/es/es-ib-salut.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='81')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='11')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250903101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22')
        msh.message_control_id = 'ID2025090310193500'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'
        msh.msh_19 = ''

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = '12'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'
        qpd.qpd_4 = ''

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='20', cq_2='RD&Recods&HL70126')
        rcp.rcp_3 = ''

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/es/es-ib-salut.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='11')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250903101935'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22')
        msh.message_control_id = 'ID20250212134401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'ID2025090310193500'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='0', cwe_2='Message accepted', cwe_3='HL70357', cwe_4='0', cwe_5='Procesado correctamente', cwe_6='TES_ERROR')
        err.severity = 'I'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'ID2025090310193500'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'ID2025090310193500'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='numCIPAUT', cx_4='001'),
            CX(cx_1='numNHCHSLL', cx_4='004'),
            CX(cx_1='numCIP', cx_4='013'),
            CX(cx_1='numDNT', cx_4='014'),
        ]
        pid.patient_name = XPN(xpn_1='APE1', xpn_2='NOM', xpn_3='APE2')
        pid.date_time_of_birth = 'NAI'
        pid.administrative_sex = CWE(cwe_1='SEX')
        pid.patient_address = XAD(xad_5='CPOSTAL')
        pid.patient_death_indicator = 'N'

        # .. build QRI ..
        qri = QRI()
        qri.candidate_confidence = '1'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK22QueryResponse()
        query_response.pid = pid
        query_response.qri = qri

        # .. assemble the full message ..
        msg = RSP_K22()
        msg.msh = msh
        msg.msa = msa
        msg.err = err
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/es/es-ib-salut.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='04')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260315093000000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '78543219'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40006542384', cx_4='001')
        pid.pid_4 = '67495319T^^^014&000'
        pid.patient_name = XPN(xpn_1='VIVES', xpn_2='PERE', xpn_3='FRANCESC')
        pid.date_time_of_birth = '19780511'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M312', pl_3='M312A', pl_4='04')
        pv1.attending_doctor = XCN(xcn_1='6789', xcn_2='GARCIAS', xcn_3='NEUS', xcn_4='FLORIT', xcn_9='004')
        pv1.hospital_service = CWE(cwe_1='MMED')
        pv1.admit_source = CWE(cwe_1='MURG')
        pv1.admitting_doctor = XCN(xcn_1='6789', xcn_2='GARCIAS', xcn_3='NEUS', xcn_4='FLORIT', xcn_9='004')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2026057893', cx_4='04')
        pv1.admit_date_time = '20260314080000000'

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
        orc.placer_order_number = EI(ei_1='LAB20260315', ei_2='04')
        orc.placer_order_group_number = EI(ei_1='GRP20260315', ei_2='04')
        orc.date_time_of_order_event = '20260315093000000'
        orc.orc_12 = '6789^GARCIAS^NEUS^FLORIT^^^^^004'
        orc.orc_17 = '04^Hospital Universitari Son Llatzer^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20260315', ei_2='04')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260315093000000'
        obr.obr_16 = '6789^GARCIAS^NEUS^FLORIT^^^^^004'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20260315093000000'

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
    """ Based on live/es/es-ib-salut.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='04')
        msh.receiving_application = HD(hd_1='20')
        msh.receiving_facility = HD(hd_1='04')
        msh.date_time_of_message = '20260315150000000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '89654321'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40006542384', cx_4='001')
        pid.pid_4 = '67495319T^^^014&000'
        pid.patient_name = XPN(xpn_1='VIVES', xpn_2='PERE', xpn_3='FRANCESC')
        pid.date_time_of_birth = '19780511'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M312', pl_3='M312A', pl_4='04')

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
        orc.placer_order_number = EI(ei_1='LABR00123', ei_2='GESTLAB')
        orc.filler_order_number = EI(ei_1='LAB20260315', ei_2='04')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABR00123', ei_2='GESTLAB')
        obr.filler_order_number = EI(ei_1='LAB20260315', ei_2='04')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260315100000'
        obr.obr_14 = '6789^GARCIAS^NEUS^FLORIT^^^^^004'
        obr.filler_field_1 = '20260315145500'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_3.obx_5 = '141'
        obx_3.units = CWE(cwe_1='mEq/L')
        obx_3.reference_range = '136-145'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '3.5-5.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_5.obx_5 = '32'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '7-56'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_6.obx_5 = '28'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '10-40'
        obx_6.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/es/es-ib-salut.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260420183000000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '45678901'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260420182800000'
        evn.event_occurred = '20260420182800000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40005924563', cx_4='001')
        pid.pid_4 = '34228976H^^^014&000'
        pid.patient_name = XPN(xpn_1='OLIVER', xpn_2='BENET', xpn_3='GABRIEL')
        pid.date_time_of_birth = '19630728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&SA GERRERIA&12', xad_3='002', xad_4='07', xad_5='07001', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971345678~^WPN^CP^^+34^679234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KURG', pl_2='KBOX05', pl_3='KBOX05A', pl_4='12')
        pv1.attending_doctor = XCN(xcn_1='4567', xcn_2='CAMPANER', xcn_3='TOMEU', xcn_4='RAMIS', xcn_9='012')
        pv1.hospital_service = CWE(cwe_1='KURG')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4567', xcn_2='CAMPANER', xcn_3='TOMEU', xcn_4='RAMIS', xcn_9='012')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2026087654', cx_4='12')
        pv1.admit_date_time = '20260420182500000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-ib-salut.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260421090000000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '56789012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40005924563', cx_4='001')
        pid.pid_4 = '34228976H^^^014&000'
        pid.patient_name = XPN(xpn_1='OLIVER', xpn_2='BENET', xpn_3='GABRIEL')
        pid.date_time_of_birth = '19630728'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KURG', pl_2='KBOX05', pl_3='KBOX05A', pl_4='12')
        pv1.attending_doctor = XCN(xcn_1='4567', xcn_2='CAMPANER', xcn_3='TOMEU', xcn_4='RAMIS', xcn_9='012')
        pv1.hospital_service = CWE(cwe_1='KURG')
        pv1.visit_number = CX(cx_1='2026087654', cx_4='12')

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
        orc.placer_order_number = EI(ei_1='RAD20260421', ei_2='12')
        orc.placer_order_group_number = EI(ei_1='GRPRAD001', ei_2='12')
        orc.date_time_of_order_event = '20260421090000000'
        orc.orc_12 = '4567^CAMPANER^TOMEU^RAMIS^^^^^012'
        orc.orc_17 = '12^Hospital Universitari Son Espases^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260421', ei_2='12')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260421090000000'
        obr.obr_16 = '4567^CAMPANER^TOMEU^RAMIS^^^^^012'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20260421090000000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Dolor toracico agudo, descartar neumotorax'

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
    """ Based on live/es/es-ib-salut.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='20')
        msh.receiving_facility = HD(hd_1='12')
        msh.date_time_of_message = '20260421140000000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '67890123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40005924563', cx_4='001')
        pid.pid_4 = '34228976H^^^014&000'
        pid.patient_name = XPN(xpn_1='OLIVER', xpn_2='BENET', xpn_3='GABRIEL')
        pid.date_time_of_birth = '19630728'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KURG', pl_2='KBOX05', pl_3='KBOX05A', pl_4='12')

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
        orc.placer_order_number = EI(ei_1='RADR00456', ei_2='RIS')
        orc.filler_order_number = EI(ei_1='RAD20260421', ei_2='12')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADR00456', ei_2='RIS')
        obr.filler_order_number = EI(ei_1='RAD20260421', ei_2='12')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260421100000'
        obr.obr_14 = '4567^CAMPANER^TOMEU^RAMIS^^^^^012'
        obr.filler_field_1 = '20260421135500'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Hallazgos', cwe_3='LN')
        obx.obx_5 = (
            'Rx torax PA y lateral: Campos pulmonares sin condensaciones ni infiltrados. Senos costofrenicos libres. Silueta cardiaca dentro de limites n'
            'ormales. No se observa neumotorax.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='60591-5', cwe_2='SUMMARY', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA1OTUgODQyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMDUgPj4Kc3RyZWFtCkJUIC9GMSAxNiBUZiA3MiA3NjAgVGQgKEluZm9ybWUgUmFkaW9sb2dp'
            'YSAtIEhvc3BpdGFsIFVuaXZlcnNpdGFyaSBTb24gRXNwYXNlcykgVGogMCAtMjAgVGQgKFBhY2llbnRlOiBCQVJDRUxPIFRPTkkgTUlRVUVMKSBUaiBFVAplbmRzdHJlYW0KZW5kb2Jq'
            'CjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAw'
            'MDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMTQgMDAwMDAgbiAKMDAwMDAwMDQ2OSAwMDAwMCBuIAp0cmFpbGVyCjw8'
            'IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjU1NwolJUVPRgo='
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
    """ Based on live/es/es-ib-salut.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='04')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260501100000000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = '78901234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260501095800000'
        evn.event_occurred = '20260501095800000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40006542384', cx_4='001')
        pid.pid_4 = '67495319T^^^014&000'
        pid.patient_name = XPN(xpn_1='VIVES', xpn_2='PERE', xpn_3='FRANCESC')
        pid.date_time_of_birth = '19780511'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='CL&ARXIDUC LLUIS SALVADOR&55',
            xad_2='3r B',
            xad_3='002',
            xad_4='07',
            xad_5='07004',
            xad_6='724',
            xad_7='H',
            xad_8='000101',
        )
        pid.pid_13 = '^PRN^PH^^+34^971678901~^WPN^CP^^+34^613678901~^NET^Internet^pvives@hotmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M312', pl_3='M312A', pl_4='04')
        pv1.attending_doctor = XCN(xcn_1='6789', xcn_2='GARCIAS', xcn_3='NEUS', xcn_4='FLORIT', xcn_9='004')
        pv1.hospital_service = CWE(cwe_1='MMED')
        pv1.admit_source = CWE(cwe_1='MURG')
        pv1.admitting_doctor = XCN(xcn_1='6789', xcn_2='GARCIAS', xcn_3='NEUS', xcn_4='FLORIT', xcn_9='004')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2026057893', cx_4='04')
        pv1.admit_date_time = '20260314080000000'

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
    """ Based on live/es/es-ib-salut.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='IBE')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='H.Son Espases')
        msh.receiving_facility = HD(hd_1='00')
        msh.date_time_of_message = '20260422151200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ecg20260422151200'
        msh.processing_id = PT(pt_1='P', pt_2='T')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40007834956', cx_4='001')
        pid.pid_4 = 'PASSPORTWXYZ^^^1114&000'
        pid.patient_name = XPN(xpn_1='MASSANET', xpn_2='AINA', xpn_3='MAGDALENA')
        pid.date_time_of_birth = '19870214'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')

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
        obr.filler_order_number = EI(ei_1='20260422151055804')
        obr.observation_date_time = '20260422150900'
        obr.filler_field_2 = 'a3b4c5d6-e7f8-9012-3456-789abcdef012'
        obr.results_rpt_status_chng_date_time = '20260422150900'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20260422150900'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiograma interpretacion', cwe_3='CPT')
        obx.obx_5 = 'Ritmo sinusal a 78 lpm. Eje normal. No alteraciones de la repolarizacion. Sin signos de isquemia aguda.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Trazado ECG', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAeADIDASIAAhEBAxEB/8QAGQAAAgMBAAAAAAAAAAAAAAAABQYDBAcI/8QAKxAA'
            'AgEDAwMDBAIDAAAAAAAAAQIDBAURABIhBjFBE1FhByJxgRQjkaGx/8QAGAEAAwEBAAAAAAAAAAAAAAAAAgMEAQX/xAAeEQACAgICAwAAAAAAAAAAAAABAgARAyESMQRBUf/aAAwDAQAC'
            'EQMRAD8AyvpS3Vdzv8FPQ0zVEpOQoI4+STwBrWen/pGamvjWzqCopZohtPpRjexPjnwNVPpZVrQ9RiaopHqITGV2oxXBPHfGtaq+p7XR3AUtTeKCCdvCzoD+M6y3P8Alao//9k='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/es/es-ib-salut.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='NEFRORED')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260510080000000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '90123456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40004635817', cx_4='001')
        pid.pid_4 = '71963438P^^^014&000'
        pid.patient_name = XPN(xpn_1='PUJOL', xpn_2='MARC', xpn_3='TOMEU')
        pid.date_time_of_birth = '19610507'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='DIAL01', pl_3='DIAL01A', pl_4='12')
        pv1.attending_doctor = XCN(xcn_1='5678', xcn_2='SALVA', xcn_3='JOANA', xcn_4='GELABERT', xcn_9='012')
        pv1.hospital_service = CWE(cwe_1='NEFR')
        pv1.visit_number = CX(cx_1='2026098765', cx_4='12')

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
        orc.placer_order_number = EI(ei_1='DIAL20260510', ei_2='12')
        orc.placer_order_group_number = EI(ei_1='GRPDIAL001', ei_2='12')
        orc.date_time_of_order_event = '20260510080000000'
        orc.orc_12 = '5678^SALVA^JOANA^GELABERT^^^^^012'
        orc.orc_17 = '12^Hospital Universitari Son Espases^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DIAL20260510', ei_2='12')
        obr.universal_service_identifier = CWE(cwe_1='90935', cwe_2='Hemodialisis', cwe_3='CPT')
        obr.observation_date_time = '20260510080000000'
        obr.obr_16 = '5678^SALVA^JOANA^GELABERT^^^^^012'
        obr.obr_27 = '^^^^^1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Hemodialisis programada, 3 sesiones semanales, acceso vascular FAV humeral izquierda'

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
    """ Based on live/es/es-ib-salut.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLUCOSACON')
        msh.sending_facility = HD(hd_1='04')
        msh.receiving_application = HD(hd_1='20')
        msh.receiving_facility = HD(hd_1='04')
        msh.date_time_of_message = '20260515063000000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '01234567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40006542384', cx_4='001')
        pid.pid_4 = '67495319T^^^014&000'
        pid.patient_name = XPN(xpn_1='VIVES', xpn_2='PERE', xpn_3='FRANCESC')
        pid.date_time_of_birth = '19780511'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M312', pl_3='M312A', pl_4='04')

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
        orc.placer_order_number = EI(ei_1='GLUC00123', ei_2='GLUCOSACON')
        orc.placer_order_group_number = EI(ei_1='CM')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='GLUC00123', ei_2='GLUCOSACON')
        obr.universal_service_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa capilar', cwe_3='LN')
        obr.observation_date_time = '20260515063000'
        obr.obr_14 = '6789^GARCIAS^NEUS^FLORIT^^^^^004'
        obr.filler_field_1 = '20260515063500'
        obr.results_rpt_status_chng_date_time = 'POC'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '186'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-180'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='DEVICE', cwe_2='Dispositivo', cwe_3='LOCAL')
        obx_2.obx_5 = 'ACCU-CHEK INFORM II SN:23456789'
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
    """ Based on live/es/es-ib-salut.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='INFCONTROL')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20260520100000000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '12345678'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260520095800000'
        evn.event_occurred = '20260520095800000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='40003748628', cx_4='001')
        pid.pid_4 = '48769321V^^^014&000'
        pid.patient_name = XPN(xpn_1='COLL', xpn_2='CATALINA', xpn_3='MARGALIDA')
        pid.date_time_of_birth = '19480624'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&BLANQUERNA&8', xad_3='002', xad_4='07', xad_5='07003', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971901234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M201', pl_3='M201B', pl_4='12')
        pv1.attending_doctor = XCN(xcn_1='7890', xcn_2='SUREDA', xcn_3='PERE', xcn_4='FORTEZA', xcn_9='012')
        pv1.hospital_service = CWE(cwe_1='MMED')
        pv1.visit_number = CX(cx_1='2026109876', cx_4='12')
        pv1.admit_date_time = '20260520095500000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='IBSALUT', cwe_2='SERVEI DE SALUT DE LES ILLES BALEARS')
        in1.insurance_company_id = CX(cx_1='IBSALUT')
        in1.insurance_company_name = XON(xon_1='IB-SALUT - GOVERN DE LES ILLES BALEARS')
        in1.insurance_company_address = XAD(xad_1='C del Carme 18', xad_3='Palma', xad_5='07003', xad_6='ESP')
        in1.plan_expiration_date = '20250101'
        in1.authorization_information = AUI(aui_1='20261231')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/es/es-ib-salut.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='81')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='20')
        msh.receiving_facility = HD(hd_1='12')
        msh.date_time_of_message = '20260520100001000'
        msh.message_type = MSG(msg_1='ACK')
        msh.message_control_id = '12345679'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = '12345678'
        msa.msa_3 = 'Mensaje procesado correctamente'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
